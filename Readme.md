🛒 Retail Knowledge RAG Platform

An enterprise-grade Retail Intelligence System built using Retrieval-Augmented Generation (RAG) with:

Hybrid Search – Chroma (vector) + BM25 (lexical)

Reranking – Cross-Encoder

LLM – Google Vertex AI Gemini

Backend – FastAPI

Frontend – Streamlit

Persistent Storage – Chroma PersistentClient + BM25 pickle

Evidence-Backed Answers – Citations + Snippets

Evaluation Ready – RAGAS compatible

📐 Architecture
Streamlit UI  ────────────▶  FastAPI Backend  ────────────▶  Vertex AI Gemini
     │                           │
     │                           │
     ▼                           ▼
File Uploads                Hybrid Retrieval
                           ├── Chroma Vector DB (Persistent)
                           ├── BM25 Lexical Index (Pickled)
                           ├── Cross-Encoder Reranker
                           └── Citation Generator

📁 Folder Structure
Rag_Retail_App/
│
├── backend/
│   ├── api/
│   │   └── main.py
│   ├── rag/
│   │   └── orchestrator.py
│   ├── ingestion/
│   │   ├── loaders.py
│   │   ├── chunker.py
│   │   └── embedders.py
│   ├── retrieval/
│   │   ├── chroma_vectorstore.py
│   │   ├── bm25_store.py
│   │   ├── hybrid.py
│   │   └── reranker.py
│   ├── llm/
│   │   └── vertex.py
│   └── eval/
│       ├── logger.py
│       └── run_ragas.py
│
├── ui/
│   └── app.py
│
├── data/
│   ├── chroma/        # Vector DB persistence
│   ├── raw/           # Uploaded files
│   └── bm25.pkl       # BM25 index
│
└── README.md

🔐 Prerequisites

Python 3.10+

Google Cloud SDK installed

Vertex AI enabled in your GCP project

Authenticate once:

gcloud auth application-default login

📦 Installation
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

▶ Running the Platform
1️⃣ Start FastAPI Backend
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000


Verify:

http://127.0.0.1:8000/docs

2️⃣ Start Streamlit UI (new terminal)
streamlit run ui/app.py


Open:

http://localhost:8501

📤 Upload Knowledge Base Files

Select Store ID.

Upload one or more files (PDF, DOCX, TXT).

Click Ingest Files.

During ingestion:

Files are chunked semantically.

Chunks are embedded.

Stored in Chroma.

Indexed in BM25.

Persisted to disk.

❓ Ask Questions

Enter retail support or operational questions.

Example:

Why is kiosk showing incorrect store information?


Answers are returned with citations and supporting snippets.

💾 Persistence Model
Component	Location
Chroma Vector DB	data/chroma/
BM25 Index	data/bm25.pkl
Uploaded Files	data/raw/

Indexes survive FastAPI restarts.

📊 RAG Evaluation (RAGAS)

After collecting real usage:

python backend/eval/run_ragas.py


Metrics generated:

Faithfulness

Answer Relevancy

Context Precision

Context Recall

🛡 Production Capabilities
Feature	Status
Hybrid Retrieval	✅
Semantic Chunking	✅
Cross-Encoder Reranking	✅
Vertex AI Gemini	✅
Persistent Indexes	✅
Evidence Citations	✅
Multi-file Upload	✅
RAG Evaluation	✅
🏁 Result

This platform is a production-grade retail knowledge system designed for store operations, incident resolution, SOP discovery, and analytics — not a demo chatbot.