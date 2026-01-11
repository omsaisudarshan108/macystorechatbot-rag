# Quick Start Guide

Get the RAG application running in under 5 minutes!

---

## Option 1: Local Docker (Fastest)

```bash
# 1. Copy environment template
cp .env.template .env

# 2. Edit PROJECT_ID in .env
nano .env  # Set PROJECT_ID=your-gcp-project-id

# 3. Start application
docker-compose up -d

# 4. Access application
# Frontend: http://localhost:8501
# Backend:  http://localhost:8000/docs
```

**Done!** The application is running locally with Docker.

---

## Option 2: Deploy to Google Cloud

```bash
# 1. Setup GCP project (one-time)
./setup-gcp-project.sh YOUR_PROJECT_ID

# 2. Deploy application
./deploy-gcp.sh YOUR_PROJECT_ID us-central1

# 3. Access the URLs printed at the end
```

**Done!** The application is deployed to Cloud Run.

---

## Verify It's Working

### Test Backend API

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "local",
  "safety_features": {...}
}
```

### Test Question Answering

```bash
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is the return policy?","store_id":"test"}'
```

Expected: Answer with citations from knowledge base.

---

## Next Steps

- Read [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for detailed guide
- Read [REFACTOR_SAFETY_REVERSION.md](REFACTOR_SAFETY_REVERSION.md) for safety info
- Read [TEST_RESULTS.md](TEST_RESULTS.md) for test validation
