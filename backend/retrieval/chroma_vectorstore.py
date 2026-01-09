import chromadb
from chromadb.config import Settings
from typing import List, Dict
from backend.retrieval.vector_store import BaseVectorStore
import uuid
from pathlib import Path


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, collection_name: str = "retail_docs", persist_dir: str = "./data/chroma"):
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_dir,settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(collection_name)

    def add(self, texts, embeddings, metadatas):
        import uuid

        ids = [str(uuid.uuid4()) for _ in texts]

        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        # New chromadb versions auto-persist.
        if hasattr(self.client, "persist"):
            self.client.persist()


    def search(self, query_embedding: list, top_k: int = 5, filters=None):
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas"]
        }

        if filters:
            kwargs["where"] = filters

        return self.collection.query(**kwargs)
