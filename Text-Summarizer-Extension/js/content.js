function unicodeToChar(text) {
    return text.replace(/\\u[\dA-F]{4}/gi, function (match) {
        return String.fromCharCode(parseInt(match.replace(/\\u/g, ""), 16));
    });
}

chrome.runtime.onMessage.addListener(function (message) {
    // Capture all text
    var textToSend = document.body.innerText;
    var jsonFormData = message.parameter;
    var query = jsonFormData["query"];
    var number = jsonFormData["number"];

    // Notify user about the successful capture of the parameters and summary generation
    alert(
        "Generating summary. The text will be highlighted on the page. It may take several seconds. " +
            "\nQuery: " +
            query +
            "\nNumber of sentences in the result: " +
            number
    );

    // Create JSON from the form data and text from the chrome tab to send
    var json = {};
    json["text"] = textToSend;
    json["query"] = query;
    json["number"] = number;

    fetch(
        "https://us-central1-query-summarization.cloudfunctions.net/function-3",
        {
            method: "POST",
            body: json,
            headers: {
                "Content-Type": "application/json",
            },
        }
    )
        .then((data) => {
            return data.json();
        })
        .then((res) => {
            $.each(res, function (index, value) {
                // Highlight summary sentences that the algorithm has identified.
                var source_document = document.body.innerHTML;
                value = value.replace(/(\s+)/, "(<[^>]+>)*$1(<[^>]+>)*");
                var pattern = new RegExp("(" + value + ")", "i");
                source_document = source_document.replace(
                    pattern,
                    "<mark>$1</mark>"
                );
                source_document = source_document.replace(
                    /(<mark>[^<>]*)((<[^>]+>)+)([^<>]*<\/mark>)/,
                    "$1</mark>$2<mark>$4"
                );

                // Replace the updated text with highlights into the source document.
                document.body.innerHTML = source_document;
            });
        })
        .catch((error) => console.error("Error:", error));
});
