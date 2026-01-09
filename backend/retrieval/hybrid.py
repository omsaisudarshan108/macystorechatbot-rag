from typing import List, Dict
from backend.retrieval.vector_store import BaseVectorStore
from backend.retrieval.bm25_store import BM25Store


class HybridSearch:
    def __init__(self, vector_store, bm25_store):
        self.vector_store = vector_store
        self.bm25_store = bm25_store

    def rrf_fusion(self, dense_texts, sparse_results, k: int = 60):
        scores = {}

        # Dense results are plain strings
        for rank, text in enumerate(dense_texts):
            scores[text] = scores.get(text, 0) + 1 / (k + rank)

        # Sparse results are (text, metadata, score)
        for rank, (text, _, _) in enumerate(sparse_results):
            scores[text] = scores.get(text, 0) + 1 / (k + rank)

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def search(self, query: str, query_embedding: list, top_k: int = 5):
        dense = self.vector_store.search(query_embedding, top_k=top_k)
        sparse = self.bm25_store.search(query, top_k=top_k)

        dense_texts = dense["documents"][0] if dense["documents"] else []
        dense_metas = dense["metadatas"][0] if dense["metadatas"] else []

        results = [{"text": t, "meta": m} for t, m in zip(dense_texts, dense_metas)]
        results += [{"text": t, "meta": m} for t, m, _ in sparse]

        return results[:top_k]

