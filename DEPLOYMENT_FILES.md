# Deployment Files Overview

This document describes all the files created for GCP App Engine deployment.

## Core Deployment Files

### 1. `app.yaml`
**Purpose**: App Engine configuration for the backend API service

**Key settings**:
- Runtime: Python 3.12
- Instance class: F4 (1GB RAM)
- Entry point: Gunicorn with Uvicorn workers
- Scaling: 1-10 instances
- Environment variables: PROJECT_ID

**Service**: `default` (backend API)

### 2. `ui-app.yaml`
**Purpose**: App Engine configuration for the Streamlit frontend

**Key settings**:
- Runtime: Python 3.12
- Instance class: F2 (512MB RAM)
- Entry point: Streamlit server
- Scaling: 1-5 instances
- Environment variables: API_URL (points to backend)

**Service**: `ui` (frontend)

### 3. `main.py`
**Purpose**: Entry point that App Engine uses to start the backend

**Content**: Imports the FastAPI app from `backend.api.main`

**Why needed**: App Engine looks for `main.py` in the root directory

### 4. `requirements.txt`
**Purpose**: Python dependencies for both backend and frontend

**Updated with**:
- `gunicorn` - WSGI server for App Engine
- `python-multipart` - For file upload handling
- `google-cloud-storage` - For GCS integration (future use)
- `requests` - For HTTP requests in UI

### 5. `.gcloudignore`
**Purpose**: Specifies files to exclude from deployment (like .gitignore)

**Excludes**:
- Virtual environments (.venv/)
- Python cache files (__pycache__/, *.pyc)
- Local data (data/chroma/, data/raw/)
- Tests and documentation
- IDE configurations
- Log files

**Why important**: Reduces deployment size and speeds up uploads

## Helper Scripts

### 6. `startup.sh`
**Purpose**: Downloads required ML models before deployment

**Downloads**:
- spaCy English model (en_core_web_sm)
- NLTK data (punkt_tab tokenizer)
- Sentence transformer embeddings (all-MiniLM-L6-v2)
- Cross-encoder reranker (ms-marco-MiniLM-L-6-v2)

**Usage**: Run before deploying or let `deploy.sh` run it

### 7. `deploy.sh`
**Purpose**: Automated deployment script

**Steps**:
1. Validates gcloud CLI and project setup
2. Runs `startup.sh` to download models
3. Deploys backend service
4. Updates UI config with backend URL
5. Deploys frontend service
6. Displays access URLs

**Usage**: `./deploy.sh`

## Documentation

### 8. `DEPLOYMENT.md`
**Purpose**: Comprehensive deployment guide

**Covers**:
- Prerequisites and setup
- Step-by-step deployment instructions
- Architecture overview
- Configuration options
- Monitoring and logging
- Troubleshooting
- Cost estimates
- Production checklist
- Security best practices

### 9. `QUICKSTART.md`
**Purpose**: Quick reference for common deployment commands

**Includes**:
- Prerequisites check commands
- API enablement
- Deployment commands
- Troubleshooting snippets
- Log viewing commands

### 10. `DEPLOYMENT_FILES.md` (this file)
**Purpose**: Overview of all deployment-related files

## Modified Application Files

### 11. `backend/api/main.py` (modified)
**Changes**:
- Added `os.getenv()` to read PROJECT_ID from environment
- Added root endpoint (`/`)
- Added health check endpoint (`/health`)
- Enhanced FastAPI metadata (title, description, version)

**Why**: Makes the app cloud-ready and adds monitoring endpoints

### 12. `ui/app.py` (modified)
**Changes**:
- Added `os.getenv()` to read API_URL from environment
- Falls back to localhost if not set

**Why**: Allows UI to work in both local and cloud environments

## Deployment Architecture

```
Project Root
├── app.yaml              → Backend config
├── ui-app.yaml           → Frontend config
├── main.py               → Backend entry point
├── requirements.txt      → Dependencies
├── .gcloudignore        → Exclude files
├── startup.sh           → Model download script
├── deploy.sh            → Deployment automation
│
├── backend/
│   └── api/
│       └── main.py      → FastAPI app (modified)
│
└── ui/
    └── app.py           → Streamlit app (modified)
```

## Deployment Flow

```
1. Developer runs: ./deploy.sh
         ↓
2. Script downloads ML models
         ↓
3. gcloud deploys backend (app.yaml)
         ↓
4. Backend URL generated
         ↓
5. Script updates ui-app.yaml with backend URL
         ↓
6. gcloud deploys frontend (ui-app.yaml)
         ↓
7. Both services running on App Engine
```

## URL Structure

After deployment:

- **Backend API**: `https://PROJECT_ID.uc.r.appspot.com`
  - Root: `/`
  - Health: `/health`
  - Docs: `/docs`
  - Ingest: `/ingest`
  - Ask: `/ask`

- **Frontend UI**: `https://ui-dot-PROJECT_ID.uc.r.appspot.com`

## Environment Variables

### Backend (app.yaml)
```yaml
PROJECT_ID: "your-project-id"  # For Vertex AI
PYTHONUNBUFFERED: "1"          # For proper logging
```

### Frontend (ui-app.yaml)
```yaml
API_URL: "https://your-project.uc.r.appspot.com"  # Backend URL
PYTHONUNBUFFERED: "1"                              # For proper logging
```

## File Sizes (Approximate)

- `app.yaml`: ~400 bytes
- `ui-app.yaml`: ~300 bytes
- `main.py`: ~200 bytes
- `requirements.txt`: ~300 bytes
- `.gcloudignore`: ~500 bytes
- `startup.sh`: ~500 bytes
- `deploy.sh`: ~2 KB
- `DEPLOYMENT.md`: ~12 KB
- `QUICKSTART.md`: ~3 KB

**Total deployment config**: ~20 KB

## Next Steps

1. **Review** all files to ensure they match your project requirements
2. **Update** PROJECT_ID in `app.yaml` if different
3. **Test locally** to ensure changes work
4. **Run** `./deploy.sh` to deploy to App Engine
5. **Monitor** logs after deployment
6. **Test** both frontend and backend URLs

## Support

For issues or questions about these files:
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed documentation
- See [QUICKSTART.md](QUICKSTART.md) for quick commands
- Check [GCP App Engine docs](https://cloud.google.com/appengine/docs)
