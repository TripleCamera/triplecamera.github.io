// ==UserScript==
// @name         OS discussion
// @namespace    http://tampermonkey.net/
// @version      2024-06-23
// @description  try to take over the world!
// @author       You
// @match        https://os.buaa.edu.cn/discussion/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=buaa.edu.cn
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Your code here...
    let href = window.location.href;
    let hrefArray = href.split('/');
    let id = Number(hrefArray[hrefArray.length - 1]);
    console.log('id = ' + id);
    if (id >= 360) {
        console.log('===== SCRIPT END =====');
        return;
    }
    hrefArray[hrefArray.length - 1] = String(id + 1);
    let newHref = hrefArray.join('/');
    setTimeout(function () {
        window.location.href = newHref;
    }, 3000);
})();