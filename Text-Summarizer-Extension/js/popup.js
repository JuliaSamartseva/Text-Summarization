function summarize() {
    
    // Capture the data from the form
    var query = document.getElementById('query').value;
    var number = document.getElementById('number').value;
    
    // Create JSON from the form data
    var json = {};
    json['query'] = query;
    json['number'] = number;
    
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
                    }, function () {
                        chrome.tabs.sendMessage(tab.id, {parameter: json});
                    });
                });
                
            });
        });
    });
}

// Call a script summarization function in the current tab when the button is clicked
document.getElementById('summarize_text').addEventListener('click', summarize);