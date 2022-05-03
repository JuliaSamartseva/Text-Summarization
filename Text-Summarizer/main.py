import nltk

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

from lsa_summarizer import LsaSummarizer
import json
from nltk.corpus import stopwords


def read_article(file_json):
    article = ''
    filedata = json.dumps(file_json)

    # Process only short websites
    if len(filedata) < 100000:
        article = filedata.replace('\\n', " ")

    return article


def generate_summary(request):
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    summarizer = LsaSummarizer()
    request_json = request.get_json(silent=True)
    sentences = read_article(request_json)
    summarizer.stop_words = stopwords.words('english')

    summary = summarizer(sentences, 3)

    return (json.dumps(summary), 200, headers)
