from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(self, model="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model)

    def rerank(self, query: str, documents: list[str]):
        pairs = [(query, doc) for doc in documents]
        scores = self.model.predict(pairs)

        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return ranked

if __name__== '__main__':
    reranker_model = Reranker()

# (Removed hardcoded Hugging Face token.)
