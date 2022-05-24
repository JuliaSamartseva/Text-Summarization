import scipy
from sentence_transformers import SentenceTransformer


class SentenceSimilarity:
    def __init__(self, sentences):
        # Initialize SBERT model.
        self.model = SentenceTransformer("bert-base-nli-mean-tokens")

        self.sentences = sentences

        for s in sentences:
            self.sentences.append(s)

        # Encode the sentences using SBERT module.
        self.embedded_sentences = self.model.encode(self.sentences)

    def get_most_similar(self, query, threshold):
        # Encode the query using SBERT module.
        query_embeddings = self.model.encode(query)

        # Find cosine similarity between query and document sentences
        cosine_dist = scipy.spatial.distance.cdist(query_embeddings, self.embedded_sentences, "cosine")

        # Choose sentences that have cosine similarity distance more than the threshold.
        result = []
        for i, s in enumerate(self.sentences):
            if cosine_dist[0][i] > threshold:
                result.append(s)

        return result
