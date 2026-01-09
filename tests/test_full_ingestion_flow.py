from pathlib import Path
from backend.ingestion.loaders import DocumentProcessor
from backend.ingestion.embedders import SentenceTransformerEmbedder
from backend.ingestion.chunkers import Chunker
from backend.retrieval.chroma_vectorstore import ChromaVectorStore

# ----------------------------------------------------
# 1️⃣ Load Document
# ----------------------------------------------------
doc_path = Path(r"D:\WORKSPACE\Macy_Chatbot\Macy's KB articles\all_docs\ELSKiosk_Issue.docx")

processor = DocumentProcessor(doc_path)
document_text = list(processor.document_dict.values())[0]

print(f"\nLoaded document characters: {len(document_text)}")


# ----------------------------------------------------
# 2️⃣ Initialize Embedder + Chunker
# ----------------------------------------------------
embedder = SentenceTransformerEmbedder()
chunker = Chunker(embedder)

chunks = chunker.semantic_chunker(document_text)
print(f"Generated {len(chunks)} semantic chunks")


# ----------------------------------------------------
# 3️⃣ Prepare Metadata
# ----------------------------------------------------
metadatas = []
for i, chunk in enumerate(chunks):
    metadatas.append({
        "source": doc_path.name,
        "chunk_id": i,
        "store_id": "NY_001",
        "doc_type": "kb_article"
    })


# ----------------------------------------------------
# 4️⃣ Embed Chunks
# ----------------------------------------------------
embeddings = embedder.embed(chunks)
print(f"Generated {len(embeddings)} embeddings")


# ----------------------------------------------------
# 5️⃣ Store in Vector DB (Chroma)
# ----------------------------------------------------
vector_store = ChromaVectorStore()
vector_store.add(chunks, embeddings, metadatas)

print("\n✅ Ingestion Pipeline Completed Successfully!")
