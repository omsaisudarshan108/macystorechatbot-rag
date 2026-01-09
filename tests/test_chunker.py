from backend.ingestion.loaders import DocumentProcessor
from backend.ingestion.embedders import SentenceTransformerEmbedder
from backend.ingestion.chunkers import Chunker
from pathlib import Path


# Parsing Document
processor = DocumentProcessor(
    Path(r"D:\WORKSPACE\Macy_Chatbot\Macy's KB articles\all_docs\ELSKiosk_Issue.docx")
)

document_text = list(processor.document_dict.values())[0]

print(f"Loaded document characters: {len(document_text)}")

# Intializing Embedding Model
embedder = SentenceTransformerEmbedder()

# Intializing Semantic Chunker
chunker = Chunker(embedder)

chunks = chunker.semantic_chunker(document_text)

for i, chunk in enumerate(chunks):
    print(f"\nChunk {i}:\n{chunk}\n{'-'*80}")