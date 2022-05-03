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
    summarizer = LsaSummarizer()
    request_json = request.get_json(silent=True)
    sentences = read_article(request_json)
    summarizer.stop_words = stopwords.words('english')

    summary = summarizer(sentences, 3)

    return json.dumps(summary)
