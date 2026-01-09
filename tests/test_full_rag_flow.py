from pathlib import Path
from backend.ingestion.loaders import DocumentProcessor
from backend.ingestion.embedders import SentenceTransformerEmbedder
from backend.ingestion.chunkers import Chunker
from backend.retrieval.chroma_vectorstore import ChromaVectorStore
from backend.retrieval.bm25_store import BM25Store
from backend.retrieval.hybrid import HybridSearch
from backend.retrieval.reranker import Reranker
from backend.llm.vertex import VertexLLM



# -------------------------------------------------
# 1️⃣ Load Document
# -------------------------------------------------
doc_path = Path(r"D:\WORKSPACE\Macy_Chatbot\Macy's KB articles\all_docs\ELSKiosk_Issue.docx")

processor = DocumentProcessor(doc_path)
document_text = list(processor.document_dict.values())[0]

print(f"Loaded document characters: {len(document_text)}")


# -------------------------------------------------
# 2️⃣ Chunk + Embed
# -------------------------------------------------
embedder = SentenceTransformerEmbedder()
chunker = Chunker(embedder)

chunks = chunker.semantic_chunker(document_text)
print(f"Generated {len(chunks)} chunks")


# -------------------------------------------------
# 3️⃣ Metadata
# -------------------------------------------------
metadatas = []
for i, chunk in enumerate(chunks):
    metadatas.append({
        "source": doc_path.name,
        "chunk_id": i,
        "store_id": "NY_001",
        "doc_type": "kb_article"
    })


# -------------------------------------------------
# 4️⃣ Vector Store + BM25
# -------------------------------------------------
vector_store = ChromaVectorStore()
bm25_store = BM25Store()

embeddings = embedder.embed(chunks)
vector_store.add(chunks, embeddings, metadatas)
bm25_store.add(chunks, metadatas)

print("Chunks indexed in vector DB and BM25")


# -------------------------------------------------
# 5️⃣ Hybrid Retrieval + Rerank
# -------------------------------------------------
query = "Kiosk Pulling wrong store information?"

query_embedding = embedder.embed([query])[0]

hybrid = HybridSearch(vector_store, bm25_store)
reranker = Reranker()

hybrid_results = hybrid.search(query, query_embedding, top_k=5)
reranked = reranker.rerank(query, [r[0] for r in hybrid_results])


# print("\nTop Reranked Results:")
# for text, score in reranked:
#     print(f"\nScore: {score:.3f}\n{text}\n{'-'*80}")

# -------------------------------------------------
# 5️⃣ LLM Generation
# -------------------------------------------------

PROJECT_ID = "mtech-stores-sre-monit-dev"

llm = VertexLLM(project_id=PROJECT_ID)

context = "\n\n".join([text for text, _ in reranked[:3]])

prompt = f"""
You are a retail support assistant.

Answer the question using ONLY the context below.
If the answer is not present, say "Insufficient information".

Context:
{context}

Question: {query}
"""

print(f"\nFINAL PROMPT:\n{prompt}\n\n")

answer = llm.generate(prompt)
print("\nFINAL ANSWER:\n", answer)
