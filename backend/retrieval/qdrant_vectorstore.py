from qdrant_client import QdrantClient
from typing import List, Dict
from backend.retrieval.vector_store import BaseVectorStore
import uuid


class QdrantVectorStore(BaseVectorStore):
    def __init__(self, collection_name="retail_docs", path="./qdrant_data"):
        self.client = QdrantClient(path=path)
        self.collection = collection_name

        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config={"size": 384, "distance": "Cosine"}
        )

    def add(self, texts: List[str], embeddings: List[list], metadatas: List[Dict]):
        points = [
            {
                "id": str(uuid.uuid4()),
                "vector": emb,
                "payload": meta | {"text": txt}
            }
            for txt, emb, meta in zip(texts, embeddings, metadatas)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_embedding: list, top_k: int = 5, filters: Dict | None = None):
        return self.client.search(
            collection_name=self.collection,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=filters
        )
