from sentence_transformers import SentenceTransformer, util
import pickle


if __name__ == '__main__':
    model = SentenceTransformer('msmarco-distilbert-base-v2')

    with open('model_pkl.pkl', 'wb') as files:
        pickle.dump(model, files)
