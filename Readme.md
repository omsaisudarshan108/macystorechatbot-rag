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
│   ├── safety/
│   │   ├── classifier.py
│   │   └── policy_engine.py
│   ├── security/
│   │   └── infrastructure_guard.py
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

**Local Development (Quick Start)**
```bash
./run_local.sh
```
This starts both backend and frontend locally.

**Manual Start (Local)**

1️⃣ Start FastAPI Backend
```bash
./run_backend.sh
# or
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Verify: http://127.0.0.1:8000/docs

2️⃣ Start Streamlit UI (new terminal)
```bash
./run_frontend.sh
# or
streamlit run ui/app.py
```

Open: http://localhost:8501

**Cloud Deployment**

See [DEPLOY_AND_CONNECT.md](DEPLOY_AND_CONNECT.md) for deploying to Google Cloud Run and connecting Streamlit Cloud.

**Streamlit Cloud Configuration**

If using Streamlit Cloud, configure the backend URL in secrets:
1. Go to your app settings → Secrets
2. Add: `API_URL = "https://your-backend-url.run.app"`
3. See [QUICK_FIX.md](QUICK_FIX.md) for details

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

🔒 Security & Safety Features

**Infrastructure Security**
- Prevents disclosure of backend hosting details (Cloud Run, GCP, regions, etc.)
- Provides compliant standard response: "Operates within Macy's secure cloud environment"
- Pattern-based detection with confidence scoring
- See [INFRASTRUCTURE_SECURITY.md](INFRASTRUCTURE_SECURITY.md) for details

**Safety Framework**
- Content moderation for harmful language
- Mental health distress detection
- Confidential escalation for crisis situations
- See [SAFETY_FRAMEWORK.md](SAFETY_FRAMEWORK.md) for details

**Test Infrastructure Security**
```bash
./test_infrastructure_security.sh
```

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
Safety Framework	✅
Infrastructure Security	✅
🏁 Result

This platform is a production-grade retail knowledge system designed for store operations, incident resolution, SOP discovery, and analytics — not a demo chatbot.