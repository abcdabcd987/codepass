'use strict';

function config_testcases(files, time_limit, mem_limit) {
    function isdigit(ch) {
        return '0' <= ch && ch <= '9';
    }

    function natural_sort_split(str) {
        if (!str)
            return [];
        let res = [];
        let token = '';
        for (let i = 0; i < str.length; ++i) {
            token += str[i];
            if (i + 1 === str.length || (isdigit(str[i]) !== isdigit(str[i + 1]))) {
                if (isdigit(str[i]))
                    token = parseInt(token, 10);
                res.push(token);
                token = '';
            }
        }
        return res;
    }

    function natural_sort_compare(a, b) {
        a = natural_sort_split(a.filename);
        b = natural_sort_split(b.filename);
        let i = 0;
        while (i < a.length && i < b.length) {
            if (a[i] < b[i]) return -1;
            if (a[i] > b[i]) return 1;
            ++i;
        }
        if (a.length < b.length) return -1;
        if (a.length > b.length) return 1;
        return 0;
    }

    let natural_sorted_files = Object.keys(files).map(x => {
        return Object.assign({filename: x}, files[x]);
    });
    natural_sorted_files.sort(natural_sort_compare);


    natural_sorted_files.forEach(file => {
        let updated_at = new Date(file.updated_at * 1000); // TODO: timezone
        const tr = `<tr>
          <td><input type="checkbox" name="delete-${file.filename}"></td>
          <td><input type="text" name="rename-${file.filename}" value="${file.filename}" class="monospace"></td>
          <td>${updated_at}</td>
        </tr>`;
        $('#all-files').append(tr);
    });


    function update_testcases() {
        function do_line(cols) {
            let tr = '<tr>';

            if (cols.length <= 0) return {err: 'Standard Input is missing.'};
            const stdin = cols[0].trim();
            if (!files.hasOwnProperty(stdin)) return {err: `There is no file named <code>${stdin}</code>.`};
            tr += `<td class="monospace">${stdin}</td>`;

            if (cols.length <= 1) return {err: 'Standard Output is missing.'};
            const stdout = cols[1].trim();
            if (!files.hasOwnProperty(stdout)) return {err: `There is no file named <code>${stdout}</code>.`};
            tr += `<td class="monospace">${stdout}</td>`;

            if (cols.length <= 2) return {err: 'Time Limit (ms) is missing.'};
            const time = cols[2].trim();
            if (!/\d+/.test(time)) return {err: `<code>${time}</code> is not an integer.`};
            tr += `<td class="monospace">${time}</td>`;

            if (cols.length <= 3) return {err: 'Memory Limit (ms) is missing.'};
            const mem = cols[3].trim();
            if (!/\d+/.test(time)) return {err: `<code>${mem}</code> is not an integer.`};
            tr += `<td class="monospace">${mem}</td>`;

            if (cols.length <= 4) return {err: 'Score is missing.'};
            const score = cols[4].trim();
            if (!/\d+/.test(score)) return {err: `<code>${score}</code> is not an integer.`};
            tr += `<td class="monospace">${score}</td>`;

            if (cols.length > 5) return {err: 'There should be only 5 columns.'};
            tr += '</tr>';

            return {err: null, tr: tr};
        }

        const lines = $('#testcase-config').val().split('\n');
        let html = '';
        let error = '';
        for (let i = 0; i < lines.length; ++i) {
            if (!lines[i].trim())
                continue;
            const ret = do_line(lines[i].split('|'));
            if (ret.err) {
                error = `Line ${i + 1}: ${ret.err}`;
                break;
            }
            html += ret.tr;
        }
        if (error) {
            $('#testcases').html(`<tr><td colspan="5" class="table-danger">${error}</td></tr>`);
        } else {
            $('#testcases').html(html);
        }
    }

    $('#testcase-config').on('input', update_testcases);
    update_testcases();


    function auto_fill_impl() {
        let groups = [];
        let files = {};
        natural_sorted_files.forEach(x => files[x.filename] = null);
        natural_sorted_files.forEach(x => {
            if (files[x.filename] !== null)
                return;
            const split = natural_sort_split(x.filename);
            for (let i = 0; i < split.length; ++i) {
                if (typeof split[0] !== 'number')
                    continue;
                let group = [x.filename];
                for (let j = 1; ; ++j) {
                    let new_split = split.slice();
                    new_split[i] = split[i] + j;
                    const new_filename = new_split.join('');
                    if (!files.hasOwnProperty(new_filename))
                        break;
                    group.push(new_filename);
                }
                if (group.length > 1) {
                    groups.push(group);
                    group.forEach(x => files[x] = group);
                }
            }
        });
        if (groups.length !== 2)
            return null;
        let g0 = groups[0], g1 = groups[1];
        if (g0.length !== g1.length)
            return null;
        let g0split = natural_sort_split(g0[0]);
        let g1split = natural_sort_split(g1[0]);
        if (g0split.length !== g1split.length)
            return null;
        let diff_split = [];
        for (let i = 0; i < g0split.length; ++i)
            if (g0split[i] !== g1split[i])
                diff_split.push([g0split[i], g1split[i]]);
        if (diff_split.length !== 1)
            return null;
        const part0 = diff_split[0][0].replace('.', '').replace('/', '');
        const part1 = diff_split[0][1].replace('.', '').replace('/', '');

        function is_input(part) {
            return ['in', 'inp', 'input'].indexOf(part) > -1;
        }

        function is_output(part) {
            return ['ou', 'out', 'output', 'an', 'ans', 'answer'].indexOf(part) > -1;
        }

        if (is_input(part0) && is_output(part1))
            return [g0, g1];
        if (is_input(part1) && is_output(part0))
            return [g1, g0];
        return null;
    }

    function auto_fill() {
        const res = auto_fill_impl();
        if (res === null) {
            alert('Failed to Auto Fill');
            return;
        }
        const inputs = res[0], outputs = res[1];
        const n = inputs.length;
        const score = Math.floor(100 / n);
        let config = '';
        for (let i = 0; i < n; ++i) {
            let s = i + 1 === n ? 100 - score * (n - 1) : score;
            config += `${inputs[i]}|${outputs[i]}|${time_limit}|${mem_limit}|${s}\n`;
        }
        $('#testcase-config').val(config);
        update_testcases();
    }

    $('#auto-fill').on('click', auto_fill);
}
