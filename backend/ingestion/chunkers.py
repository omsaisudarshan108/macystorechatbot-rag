from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from backend.ingestion.embedders import BaseEmbedder
import nltk

nltk.download('punkt_tab')


class Chunker:
    def __init__(self, embedder: BaseEmbedder, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedder = embedder

    # -----------------------------------------
    # Sentence Sliding Window Chunking
    # -----------------------------------------
    def sentence_chunker(self, text: str) -> List[str]:
        sentences = sent_tokenize(text)
        chunks, current_chunk = [], []

        for sent in sentences:
            current_chunk.append(sent)

            if len(" ".join(current_chunk)) >= self.chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = current_chunk[-self.overlap:]

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    # -----------------------------------------
    # Semantic Chunking using SAME embedder
    # -----------------------------------------
    def semantic_chunker(self, text: str, threshold: float = 0.75) -> List[str]:
        sentences = sent_tokenize(text)
        if len(sentences) <= 1:
            return sentences

        embeddings = self.embedder.embed(sentences)

        chunks, current_chunk = [], [sentences[0]]

        for i in range(1, len(sentences)):
            sim = cosine_similarity(
                [embeddings[i-1]], [embeddings[i]]
            )[0][0]

            if sim < threshold:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

            current_chunk.append(sentences[i])

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
