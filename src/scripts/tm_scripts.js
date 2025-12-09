// ==UserScript==
// @name         Leetcode Copy Problem Title with Difficulty
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Add a copy button to Leetcode problem titles like "[H] 2071. Maximum Number of Tasks You Can Assign"
// @author       Honiess1927 & ChatGPT
// @match        https://leetcode.com/problems/*
// @grant        GM_setClipboard
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    function getDifficultyAbbreviation(text) {
        if (text.includes('Hard')) return 'H';
        if (text.includes('Medium')) return 'M';
        if (text.includes('Easy')) return 'E';
        return '?';
    }

    function addCopyButton() {
        const titleAnchor = document.querySelector('div.text-title-large a[href^="/problems/"]');
        const difficultyDiv = document.querySelector('div.rounded-full'); // difficulty badge (e.g. Easy/Medium/Hard)

        if (!titleAnchor || !difficultyDiv) return;
        if (document.getElementById('copy-problem-title-btn')) return;

        const titleText = titleAnchor.textContent.trim(); // e.g. "2071. Maximum Number of Tasks You Can Assign"
        const difficultyText = difficultyDiv.textContent.trim(); // e.g. "Hard"
        const difficultyAbbr = getDifficultyAbbreviation(difficultyText);

        const fullText = `(${difficultyAbbr}) ${titleText}`;

        const button = document.createElement('button');
        button.id = 'copy-problem-title-btn';
        button.innerText = '📋';
        button.style.marginLeft = '10px';
        button.style.cursor = 'pointer';
        button.style.border = 'none';
        button.style.background = 'none';
        button.style.fontSize = '1rem';

        button.addEventListener('click', () => {
            if (typeof GM_setClipboard !== 'undefined') {
                GM_setClipboard(fullText);
            } else {
                navigator.clipboard.writeText(fullText);
            }
            button.innerText = '✅';
            setTimeout(() => {
                button.innerText = '📋';
            }, 1000);
        });

        titleAnchor.parentElement.insertBefore(button, titleAnchor.nextSibling);
    }

    const observer = new MutationObserver(() => {
        addCopyButton();
    });

    observer.observe(document.body, { childList: true, subtree: true });
    addCopyButton();
})();