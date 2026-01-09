from rank_bm25 import BM25Okapi
import nltk
import pickle
from pathlib import Path


class BM25Store:
    def __init__(self):
        self.persist_path = Path("data/bm25.pkl")
        self.corpus = []
        self.tokenized_corpus = []
        self.metadatas = []
        self.bm25 = None

        if self.persist_path.exists():
            with open(self.persist_path, "rb") as f:
                self.corpus, self.tokenized_corpus, self.metadatas = pickle.load(f)
                if self.tokenized_corpus:
                    self.bm25 = BM25Okapi(self.tokenized_corpus)

    def add(self, texts, metadatas):
        for text, meta in zip(texts, metadatas):
            tokens = nltk.word_tokenize(text.lower())
            self.corpus.append(text)
            self.tokenized_corpus.append(tokens)
            self.metadatas.append(meta)

        self.bm25 = BM25Okapi(self.tokenized_corpus)

        with open(self.persist_path, "wb") as f:
            pickle.dump((self.corpus, self.tokenized_corpus, self.metadatas), f)

    def search(self, query: str, top_k: int = 5):
        if self.bm25 is None or not self.corpus:
            return []   # ← graceful empty state

        tokens = nltk.word_tokenize(query.lower())
        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            zip(self.corpus, self.metadatas, scores),
            key=lambda x: x[2],
            reverse=True
        )
        return ranked[:top_k]
