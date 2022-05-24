alert("Generating summary. The text will be highlighted on the page. It may take several seconds.");

function unicodeToChar(text) {
	return text.replace(/\\u[\dA-F]{4}/gi, 
	      function (match) {
	           return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
	      });
}

chrome.runtime.onMessage.addListener(function(message) {
    // Capture all text
    var textToSend = document.body.innerText;
    var jsonFormData = message.parameter;
    
    // Create JSON from the form data and text from the chrome tab to send
    var json = {};
    json['text'] = textToSend;
    json['query'] = jsonFormData['query'];
    json['number'] = jsonFormData['number'];

    fetch('https://us-central1-query-summarization.cloudfunctions.net/function-3', {
      method: 'POST',
      body: json,
      headers:{
        'Content-Type': 'application/json'
      } })
    .then(data => { return data.json() })
    .then(res => { 
        $.each(res, function( index, value ) {
            // Highlight summary sentences that the algorithm has identified.
            var source_document = document.body.innerHTML;
            value = value.replace(/(\s+)/,"(<[^>]+>)*$1(<[^>]+>)*");
            var pattern = new RegExp("("+value+")", "i");
            source_document = source_document.replace(pattern, "<mark>$1</mark>");
            source_document = source_document.replace(/(<mark>[^<>]*)((<[^>]+>)+)([^<>]*<\/mark>)/,"$1</mark>$2<mark>$4");
            
            // Replace the updated text with highlights into the source document.
            document.body.innerHTML = source_document;
        });
     })
    .catch(error => console.error('Error:', error));
}


