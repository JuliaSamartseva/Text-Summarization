from sentence_transformers import SentenceTransformer, util
import torch


class SentenceSimilarity:
    def __init__(self, sentences, model):
        self.model = model

        self.sentences = sentences

        # Encode the sentences using SBERT module.
        self.embedded_sentences = self.model.encode(self.sentences)

    def get_most_similar(self, query):
        # Encode the query using SBERT module.
        query_embeddings = self.model.encode(query)

        # Find dot distance between query and document sentences
        dot_distance = util.dot_score(query_embeddings, self.embedded_sentences)[0]

        # Choose top sentences with the highest scores
        sentences_number = len(self.sentences) 
        top_k = int(sentences_number * 0.3)
        top_results = torch.topk(dot_distance, k=top_k)

        result = []
        for score, idx in zip(top_results[0], top_results[1]):
            result.append(self.sentences[idx])

        return result
