'use strict';

function config_testcases(files) {
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
          <td><input type="checkbox" name="delete-${file.filename}" class="form-check-input"></td>
          <td><input type="text" name="rename-${file.filename}" value="${file.filename}" class="monospace form-control form-control-sm"></td>
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


    $('#auto-fill').on('click', function () {
        alert('TODO: Auto Fill');
    });
}
