import nltk

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

from lsa_summarizer import LsaSummarizer
import json
from nltk.corpus import stopwords

from google.cloud import logging as cloudlogging
import logging

lg_client = cloudlogging.Client()

lg_handler = lg_client.get_default_handler()
cloud_logger = logging.getLogger("cloudLogger")
cloud_logger.setLevel(logging.INFO)
cloud_logger.addHandler(lg_handler)


def read_article(text):
    article = ''

    # Process only short websites
    if len(text) < 100000:
        article = text.replace('\\n', " ")

    return article


def summarize_article(sentences, query, number):
    summarizer = LsaSummarizer()
    summarizer.stop_words = stopwords.words('english')
    summary = summarizer(sentences, query, number)
    cloud_logger.info("Finished summarization")
    return summary


def generate_summary(request):
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        cloud_logger.info("Received preflight request")
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return '', 204, headers

    # Set CORS headers for the main request
    cloud_logger.info("Received main request")

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    request_json = request.get_json(force=True)
    text = request_json["text"]
    query = request_json["query"]
    number = request_json["number"]

    cloud_logger.info(query) #REMOVE

    sentences = read_article(text)

    summary = summarize_article(sentences, query, number)
    cloud_logger.info("Finished summarization")

    return json.dumps(summary), 200, headers
