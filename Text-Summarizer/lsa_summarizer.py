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

    def __call__(self, document, query, sentences_count):
        dictionary = self._create_dictionary(document)

        if not dictionary:
            return ()

        sentences = sent_tokenize(document)

        # If the query is not empty, module with the search for the most relevant sentences is started.
        if query:
            sentence_similarity = SentenceSimilarity(sentences)
            sentences = sentence_similarity.get_most_similar(query, 1)

        matrix = LsaSummarizer._create_matrix(sentences, dictionary)
        matrix = LsaSummarizer._compute_term_frequency(matrix)

        # Singular Value Decomposition
        u, sigma, v = singular_value_decomposition(matrix, full_matrices=False)

        ranks = iter(self._compute_ranks(sigma, v))
        return LsaSummarizer._get_best_sentences(sentences, sentences_count,
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
