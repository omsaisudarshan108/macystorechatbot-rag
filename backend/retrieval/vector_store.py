from abc import ABC, abstractmethod
from typing import List, Dict


class BaseVectorStore(ABC):

    @abstractmethod
    def add(self, texts: List[str], embeddings: List[list], metadatas: List[Dict]):
        pass

    @abstractmethod
    def search(self, query_embedding: list, top_k: int = 5, filters: Dict | None = None):
        pass