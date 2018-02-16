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
        return {filename: x, sha1: files[x]}
    });
    natural_sorted_files.sort(natural_sort_compare);

    const ul_all_files = $('#all-files');
    natural_sorted_files.forEach(file => {
        const li = '<li data-sha1="' + file.sha1 + '"><code>' + file.filename + '</code></li>';
        ul_all_files.append(li);
    });
}
