from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import math
import numpy

from warnings import warn
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from numpy.linalg import svd as singular_value_decomposition
from base_summarizer import BaseSummarizer
from sentence_similarity import SentenceSimilarity

import os
import pickle
from google.cloud import storage

from google.cloud import logging as cloudlogging
import logging

lg_client = cloudlogging.Client()

lg_handler = lg_client.get_default_handler()
cloud_logger = logging.getLogger("cloudLogger")
cloud_logger.setLevel(logging.INFO)
cloud_logger.addHandler(lg_handler)

# Download model from cloud storage bucket.
model = None


class LsaSummarizer(BaseSummarizer):
    MIN_DIMENSIONS = 3
    REDUCTION_RATIO = 1 / 1

    _stop_words = list(stopwords.words('english'))

    @property
    def stop_words(self):
        return self._stop_words

    @stop_words.setter
    def stop_words(self, words):
        self._stop_words = words

    # Download model file from cloud storage bucket
    @staticmethod
    def download_model_file():

        from google.cloud import storage
        # Model Bucket details
        BUCKET_NAME = "sentence-transformer"
        PROJECT_ID = "query-summarization"
        GCS_MODEL_FILE = "model_pkl.pkl"

        # Initialise a client
        client = storage.Client(PROJECT_ID)

        # Create a bucket object for our bucket
        bucket = client.get_bucket(BUCKET_NAME)

        # Create a blob object from the filepath
        blob = bucket.blob(GCS_MODEL_FILE)

        folder = '/tmp/'
        if not os.path.exists(folder):
            os.makedirs(folder)
        # Download the file to a destination
        blob.download_to_filename(folder + "local_model.pkl")

    def __call__(self, document, query, sentences_count):
        # Use the global model variable
        global model

        if not model:
            cloud_logger.info("Loading model file from the cloud storage.")
            self.download_model_file()
            model = pickle.load(open("/tmp/local_model.pkl", 'rb'))
            cloud_logger.info("Cloud model was initialised and finished download.")

        dictionary = self._create_dictionary(document)

        if not dictionary:
            return ()

        sentences = sent_tokenize(document)

        if query:
            sentence_similarity = SentenceSimilarity(sentences, model)
            sentences = sentence_similarity.get_most_similar(query)

        matrix = self._create_matrix(document, dictionary)
        matrix = self._compute_term_frequency(matrix)
        u, sigma, v = singular_value_decomposition(matrix, full_matrices=False)

        ranks = iter(self._compute_ranks(sigma, v))
        return self._get_best_sentences(sentences, sentences_count,
                                        lambda s: next(ranks))

    def _create_dictionary(self, document):
        words = word_tokenize(document)
        words = tuple(words)

        words = map(self.normalize_word, words)

        unique_words = frozenset(w for w in words if w not in self._stop_words)

        return dict((w, i) for i, w in enumerate(unique_words))

    @staticmethod
    def _create_matrix(sentences, dictionary):
        words_count = len(dictionary)
        sentences_count = len(sentences)
        if words_count < sentences_count:
            message = (
                "Number of words (%d) is lower than number of sentences (%d). "
                "LSA algorithm may not work properly."
            )
            warn(message % (words_count, sentences_count))

        matrix = numpy.zeros((words_count, sentences_count))
        for col, sentence in enumerate(sentences):
            words = word_tokenize(sentence)
            for word in words:
                if word in dictionary:
                    row = dictionary[word]
                    matrix[row, col] += 1

        return matrix

    @staticmethod
    def _compute_term_frequency(matrix, smooth=0.4):
        max_word_frequencies = numpy.max(matrix, axis=0)
        rows, cols = matrix.shape
        for row in range(rows):
            for col in range(cols):
                max_word_frequency = max_word_frequencies[col]
                if max_word_frequency != 0:
                    frequency = matrix[row, col] / max_word_frequency
                    matrix[row, col] = smooth + (1.0 - smooth) * frequency

        return matrix

    @staticmethod
    def _compute_ranks(sigma, v_matrix):
        assert len(sigma) == v_matrix.shape[0]

        dimensions = max(LsaSummarizer.MIN_DIMENSIONS,
                         int(len(sigma) * LsaSummarizer.REDUCTION_RATIO))
        powered_sigma = tuple(s ** 2 if i < dimensions else 0.0
                              for i, s in enumerate(sigma))

        ranks = []

        for column_vector in v_matrix.T:
            rank = sum(s * v ** 2 for s, v in zip(powered_sigma, column_vector))
            ranks.append(math.sqrt(rank))

        return ranks
