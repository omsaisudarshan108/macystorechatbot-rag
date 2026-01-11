# RAG Knowledge Assistant for Retail Operations

Enterprise-grade RAG (Retrieval-Augmented Generation) system for retail store associates with comprehensive safety features, bilingual support, and premium UI.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Deployed-green?logo=google-cloud)](https://cloud.google.com/run)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

- **🤖 RAG Question Answering** - Knowledge-based Q&A with source citations
- **🔒 Multi-Layer Safety** - Document verification, query classification, infrastructure protection
- **🌍 Bilingual Support** - Auto-detect English/Spanish with WCAG 2.1 AA compliance
- **🎨 Premium Dark Theme** - Retail-grade UI inspired by department store aesthetics
- **📦 Fully Dockerized** - Deploy anywhere: local, Cloud Run, or Kubernetes
- **🚀 One-Command Deployment** - Automated GCP setup and deployment scripts

---

## Quick Start

### Option 1: Local Docker (Fastest)

```bash
# 1. Clone repository
git clone https://github.com/omsaisudarshan108/macystorechatbot-rag.git
cd macystorechatbot-rag

# 2. Configure environment
cp .env.template .env
nano .env  # Set PROJECT_ID

# 3. Start application
docker-compose up -d

# 4. Access application
open http://localhost:8501
```

### Option 2: Deploy to Google Cloud

```bash
# 1. Setup GCP project (one-time)
./setup-gcp-project.sh YOUR_PROJECT_ID

# 2. Deploy application
./deploy-gcp.sh YOUR_PROJECT_ID us-central1

# 3. Access URLs printed at the end
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│          Frontend (Streamlit)            │
│  - Premium dark theme UI                │
│  - Bilingual EN/ES support              │
│  - Document upload interface            │
│  - Safety status indicators             │
└──────────────────┬──────────────────────┘
                   │ HTTP/HTTPS
┌──────────────────▼──────────────────────┐
│          Backend (FastAPI)               │
│  - RAG orchestration                    │
│  - Document verification                │
│  - Safety classification                │
│  - Vertex AI integration                │
│  - Vector store (ChromaDB)              │
│  - BM25 search + reranking              │
└─────────────────────────────────────────┘
```

---

## Technology Stack

**Backend:**
- FastAPI - High-performance API framework
- LangChain - RAG orchestration
- ChromaDB - Vector database
- Sentence Transformers - Embeddings (all-MiniLM-L6-v2)
- Vertex AI - LLM generation (Gemini 2.0 Flash)
- BM25 - Keyword search
- Cross-encoder - Reranking

**Frontend:**
- Streamlit - Interactive web UI
- Custom CSS - Premium dark theme
- i18n - Bilingual support (EN/ES)

**Infrastructure:**
- Docker - Containerization
- Docker Compose - Local orchestration
- Google Cloud Run - Serverless deployment
- Artifact Registry - Container images
- Secret Manager - Credentials
- Cloud Storage - Document storage

---

## Project Structure

```
.
├── backend/
│   ├── api/              # FastAPI endpoints
│   ├── ingestion/        # Document processing
│   ├── retrieval/        # Vector & BM25 search
│   ├── rag/              # RAG orchestration
│   ├── llm/              # Vertex AI integration
│   ├── safety/           # Safety framework
│   ├── security/         # Infrastructure protection
│   ├── document_security/# Document verification
│   └── i18n/             # Internationalization
├── ui/
│   ├── app.py            # Streamlit application
│   ├── styles_dark.css   # Premium dark theme
│   └── i18n_utils.py     # Frontend translations
├── Dockerfile.backend    # Backend container
├── Dockerfile.frontend   # Frontend container
├── docker-compose.yml    # Local orchestration
├── deploy-gcp.sh         # GCP deployment script
├── setup-gcp-project.sh  # GCP initialization script
└── docs/                 # Documentation
```

---

## Safety Features

### Multi-Layer Protection

1. **Document Verification (Pre-Ingestion)**
   - Malware detection
   - Prompt injection prevention
   - Social engineering detection
   - Policy compliance validation

2. **Query Classification (Pre-Processing)**
   - Violence content blocking
   - Self-harm support escalation
   - Hate speech prevention
   - Explicit content filtering

3. **Infrastructure Guard (Runtime)**
   - Backend disclosure prevention
   - OWASP LLM guardrails
   - Technical probing protection

4. **Confidential Escalation**
   - Safety incident reporting
   - Employee assistance routing
   - Security team notification

**Note:** Aggressive response safety filter removed (see [REFACTOR_SAFETY_REVERSION.md](REFACTOR_SAFETY_REVERSION.md))

---

## Bilingual Support

Auto-detect language from user input (English or Spanish):

- **Pattern-based detection** - 60+ Spanish indicators, 40+ English patterns
- **Confidence scoring** - Threshold-based language selection
- **WCAG 2.1 AA compliant** - Proper lang attributes for screen readers
- **ARIA support** - Live regions and labels in both languages
- **No language mixing** - Consistent language throughout response

See [I18N_IMPLEMENTATION.md](I18N_IMPLEMENTATION.md) for technical details.

---

## Premium UI

Macy's-inspired dark theme design:

- **Near-black background** - #0E0F12 (not pure black)
- **Muted red accent** - #A8434B (used sparingly)
- **Typography** - Inter font with optimized line-heights
- **Contrast ratios** - AAA compliant (13.2:1 primary, 8.9:1 secondary)
- **8px grid system** - Consistent spacing
- **Subtle interactions** - 200ms transitions, soft glows

See [DARK_THEME_DESIGN.md](DARK_THEME_DESIGN.md) for design system.

---

## Deployment

### Local Docker

```bash
docker-compose up -d
```

**Ports:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Google Cloud Run

```bash
./setup-gcp-project.sh YOUR_PROJECT_ID    # One-time setup
./deploy-gcp.sh YOUR_PROJECT_ID us-central1
```

**Features:**
- Auto-scaling (0-10 instances)
- HTTPS by default
- Pay-per-use pricing
- Zero maintenance

### Kubernetes

```bash
kubectl apply -f k8s/
```

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for complete deployment guide.

---

## Configuration

### Environment Variables

```bash
# GCP Configuration
PROJECT_ID=your-gcp-project-id
REGION=us-central1
ENVIRONMENT=local

# Vertex AI
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-2.0-flash

# Application Settings
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,docx,txt
LOG_LEVEL=INFO
```

See [.env.template](.env.template) for all options.

---

## API Endpoints

### Backend API (FastAPI)

**Base URL:** `http://localhost:8000` (local) or `https://rag-backend-xxx.run.app` (Cloud Run)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with safety feature status |
| `/ask` | POST | Ask a question (RAG pipeline) |
| `/ingest` | POST | Upload and ingest document |
| `/feedback` | POST | Submit user feedback |
| `/feedback/stats` | GET | Get feedback statistics |
| `/docs` | GET | Interactive API documentation |

**Example:**
```bash
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is the return policy?","store_id":"test"}'
```

---

## Testing

### Run Tests

```bash
# Backend tests
pytest backend/

# i18n tests
python backend/i18n/test_detector.py

# Integration test
./test_i18n.sh
```

### Manual Testing

1. **Upload Document:**
   - Open UI at http://localhost:8501
   - Click "📁 Upload Knowledge Base Documents"
   - Upload PDF/DOCX file
   - Verify "✅ Indexed successfully"

2. **Ask Question:**
   - Type question in text input
   - Press Enter
   - Verify answer with citations
   - Check safety indicators

3. **Test Bilingual:**
   - English: "What is the return policy?"
   - Spanish: "¿Cuál es la política de devolución?"
   - Verify correct language detection

---

## Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute quick start guide |
| [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | Complete deployment guide (580 lines) |
| [DOCKERIZATION_SUMMARY.md](DOCKERIZATION_SUMMARY.md) | Implementation details (550 lines) |
| [DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md) | Quality checklist (300 lines) |
| [REFACTOR_SAFETY_REVERSION.md](REFACTOR_SAFETY_REVERSION.md) | Safety architecture (360 lines) |
| [TEST_RESULTS.md](TEST_RESULTS.md) | Test validation (305 lines) |
| [DARK_THEME_DESIGN.md](DARK_THEME_DESIGN.md) | UI design system (578 lines) |
| [I18N_IMPLEMENTATION.md](I18N_IMPLEMENTATION.md) | Bilingual implementation (700+ lines) |

---

## Performance

**Response Times:**
- Health check: < 100ms
- RAG query: 1-3 seconds (includes retrieval + reranking + generation)
- Document upload: 1-2 seconds

**Scaling (Cloud Run):**
- Cold start: 1-3 seconds
- Warm request: 100-500ms
- Auto-scale: 0-10 instances
- Concurrency: 80 requests per instance

---

## Cost Estimate (Cloud Run)

**Monthly Costs:**
- 10,000 requests: $2-5
- 100,000 requests: $15-25
- 1,000,000 requests: $100-150

**Optimization:**
- Scale to zero when idle: $0 idle cost
- Right-sized resources: 2 GB backend, 1 GB frontend
- Request timeout: 300 seconds

---

## Troubleshooting

### Port Already in Use

```bash
lsof -ti :8000 | xargs kill -9  # Backend
lsof -ti :8501 | xargs kill -9  # Frontend
```

### Docker Build Fails

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Vertex AI 403 Error

```bash
# Authenticate
gcloud auth application-default login

# Or grant IAM permissions
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md#troubleshooting) for complete troubleshooting guide.

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **LangChain** - RAG framework
- **ChromaDB** - Vector database
- **Sentence Transformers** - Embedding models
- **Streamlit** - Web UI framework
- **Google Vertex AI** - LLM generation
- **FastAPI** - API framework

---

## Support

**Issues:** https://github.com/omsaisudarshan108/macystorechatbot-rag/issues

**Documentation:** See `/docs` folder or individual markdown files in root

**Contact:** Open an issue for questions or bug reports

---

## Status

✅ **Production Ready**
- Docker containerization complete
- Multi-environment deployment tested
- Security features validated
- Performance optimized
- Documentation comprehensive

**Last Updated:** 2026-01-11
**Version:** 1.0
**Maintained By:** Development Team
