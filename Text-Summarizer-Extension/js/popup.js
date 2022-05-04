function summarize() {
    chrome.windows.getCurrent(function (currentWindow) {
        chrome.tabs.query({ active: true, windowId: currentWindow.id }, function (activeTabs) {
            activeTabs.map(function (tab) {
                chrome.scripting.executeScript({
                    target: {tabId: tab.id, allFrames: false},
                    files: ['js/jquery.js'],
                },
                () => {
                    chrome.scripting.executeScript({
                        target: {tabId: tab.id, allFrames: false},
                        files: ['js/content.js'],
                    });
                });
            });
        });
    });
}

document.getElementById('summarize_text').addEventListener('click', summarize);