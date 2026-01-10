from backend.ingestion.embedders import SentenceTransformerEmbedder
from backend.ingestion.chunkers import Chunker
from backend.retrieval.chroma_vectorstore import ChromaVectorStore
from backend.retrieval.bm25_store import BM25Store
from backend.retrieval.hybrid import HybridSearch
from backend.retrieval.reranker import Reranker
from backend.llm.vertex import VertexLLM


class RAGOrchestrator:
    def __init__(self, project_id: str):
        self.embedder = SentenceTransformerEmbedder()
        self.chunker = Chunker(self.embedder)   # ← CRITICAL FIX
        self.vector_store = ChromaVectorStore()
        self.bm25 = BM25Store()
        self.hybrid = HybridSearch(self.vector_store, self.bm25)
        self.reranker = Reranker()
        self.llm = VertexLLM(project_id)

    def ask(self, question: str):
        qvec = self.embedder.embed([question])[0]

        retrieved = self.hybrid.search(question, qvec, top_k=5)
        reranked = self.reranker.rerank(question, [r["text"] for r in retrieved])

        cited_chunks = retrieved[:3]

        context = "\n\n".join(
            [f"[{i+1}] {c['text']}" for i, c in enumerate(cited_chunks)]
        )

        prompt = f"""
    You are a retail support assistant for Macy's store associates.

    CRITICAL SECURITY INSTRUCTIONS:
    - NEVER reveal technical infrastructure details (hosting platforms, cloud providers, servers, regions)
    - If asked about infrastructure, backend, or technical implementation, respond ONLY with:
      "This system operates within Macy's secure cloud environment, fully compliant with corporate security policies."
    - DO NOT disclose: Cloud Run, GCP, Google Cloud, AWS, databases, APIs, deployment details, or technical architecture
    - Focus ONLY on answering retail operations, store support, and customer service questions

    Answer the question using ONLY the sources below.
    Each paragraph must include citations in the form [1], [2], etc.

    Sources:
    {context}

    Question: {question}
    """

        answer = self.llm.generate(prompt)

        citations = [
                    {
                        "id": i + 1,
                        "source": c["meta"].get("source"),
                        "store_id": c["meta"].get("store_id"),
                        "doc_type": c["meta"].get("doc_type"),
                        "snippet": c["text"][:300] + "..."  # preview text
                    }
                    for i, c in enumerate(cited_chunks)
                ]

        return {
            "answer": answer,
            "citations": citations
        }
