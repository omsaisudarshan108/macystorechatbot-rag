from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
from typing import List


# ------------------------------
# Base Interface
# ------------------------------
class BaseEmbedder(ABC):

    @abstractmethod
    def embed(self, texts: List[str]) -> List[list]:
        pass


# ------------------------------
# Local SBERT Embedder
# ------------------------------
class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[list]:
        return self.model.encode(texts, show_progress_bar=True).tolist()
