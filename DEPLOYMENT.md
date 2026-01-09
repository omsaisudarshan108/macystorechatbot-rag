# GCP App Engine Deployment Guide

This guide will help you deploy the RAG Platform to Google Cloud Platform App Engine.

## Prerequisites

1. **GCP Account**: Active Google Cloud Platform account
2. **GCP Project**: A GCP project with billing enabled
3. **gcloud CLI**: Installed and authenticated
4. **APIs Enabled**:
   - App Engine Admin API
   - Cloud Build API
   - Vertex AI API
   - Cloud Storage API

## Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# 1. Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# 2. Run the deployment script
./deploy.sh
```

The script will:
- Download required ML models (spaCy, sentence transformers)
- Deploy the backend API service
- Deploy the frontend UI service
- Display the URLs for both services

**Deployment time**: 10-20 minutes total

### Option 2: Manual Deployment

#### Step 1: Initialize App Engine (First time only)

```bash
gcloud app create --region=us-central
```

#### Step 2: Download Required Models

```bash
./startup.sh
```

#### Step 3: Deploy Backend API

```bash
gcloud app deploy app.yaml
```

Wait for deployment to complete, then get the backend URL:
```bash
export BACKEND_URL="https://YOUR_PROJECT_ID.uc.r.appspot.com"
```

#### Step 4: Update UI Configuration

Edit `ui-app.yaml` and replace the `API_URL` with your backend URL:
```yaml
env_variables:
  API_URL: "https://YOUR_PROJECT_ID.uc.r.appspot.com"
```

#### Step 5: Deploy Frontend UI

```bash
gcloud app deploy ui-app.yaml
```

## Accessing Your Application

After deployment:

- **Frontend UI**: `https://ui-dot-YOUR_PROJECT_ID.uc.r.appspot.com`
- **Backend API**: `https://YOUR_PROJECT_ID.uc.r.appspot.com`
- **API Docs**: `https://YOUR_PROJECT_ID.uc.r.appspot.com/docs`

## Configuration

### Environment Variables

Backend (`app.yaml`):
- `PROJECT_ID`: Your GCP project ID (for Vertex AI)
- `PYTHONUNBUFFERED`: Set to "1" for proper logging

Frontend (`ui-app.yaml`):
- `API_URL`: Backend API URL

### Instance Configuration

**Backend** (`app.yaml`):
- Instance class: F4 (1GB RAM, 2.4GHz CPU)
- Scaling: 1-10 instances
- Timeout: 300 seconds

**Frontend** (`ui-app.yaml`):
- Instance class: F2 (512MB RAM, 1.2GHz CPU)
- Scaling: 1-5 instances

## Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       v
┌─────────────────────┐
│  Streamlit UI       │  (ui service)
│  Port: 8080         │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│  FastAPI Backend    │  (default service)
│  Port: 8080         │
│                     │
│  - /ingest         │  (Upload & index docs)
│  - /ask            │  (Query RAG system)
│  - /docs           │  (API documentation)
└──────┬──────────────┘
       │
       ├──> Vertex AI (LLM)
       ├──> ChromaDB (Vector store - in-memory)
       └──> BM25 (Lexical search - in-memory)
```

## Storage Considerations

**Current Setup** (Development):
- ChromaDB: In-memory (ephemeral)
- BM25 Store: In-memory (ephemeral)
- Uploaded files: Local filesystem (ephemeral)

**⚠️ Important**: Data is lost when instances restart!

**Production Recommendations**:
1. Use Cloud Storage for uploaded files
2. Use Qdrant Cloud or Vertex AI Vector Search for persistent vectors
3. Use Cloud SQL or Firestore for metadata
4. Implement data persistence layer

## Monitoring & Logs

### View Logs

```bash
# Backend logs
gcloud app logs tail -s default

# Frontend logs
gcloud app logs tail -s ui

# Combined logs
gcloud app logs tail
```

### View in Console

https://console.cloud.google.com/logs

### Monitoring Dashboard

https://console.cloud.google.com/appengine

## Cost Estimates

Approximate monthly costs (light usage):

- App Engine F4 instances: ~$50-100/month
- App Engine F2 instances: ~$25-50/month
- Vertex AI API calls: ~$0.001-0.002 per request
- Cloud Storage: ~$0.02 per GB
- Network egress: ~$0.12 per GB

**Total estimated**: $100-200/month for development/testing

## Troubleshooting

### Issue: Deployment fails with "out of memory"

**Solution**: Increase instance class in `app.yaml`:
```yaml
instance_class: F4_1G  # or higher
```

### Issue: "Model not found" errors

**Solution**: Ensure `startup.sh` ran successfully and models were downloaded.

### Issue: ChromaDB data lost after restart

**Expected behavior**: In-memory storage is ephemeral. Implement persistent storage for production.

### Issue: Timeout errors

**Solution**: Increase timeout in `app.yaml`:
```yaml
entrypoint: gunicorn -w 4 -k uvicorn.workers.UvicornWorker --timeout 600 --bind :$PORT main:app
```

### Issue: API connection refused from UI

**Solution**: Verify backend URL in `ui-app.yaml` matches your actual backend URL.

## Updating the Application

```bash
# Update backend
gcloud app deploy app.yaml

# Update frontend
gcloud app deploy ui-app.yaml

# Update both
gcloud app deploy app.yaml ui-app.yaml
```

## Rollback

```bash
# List versions
gcloud app versions list

# Route traffic to previous version
gcloud app versions set-traffic [VERSION_ID] --service=default
gcloud app versions set-traffic [VERSION_ID] --service=ui
```

## Cleaning Up

```bash
# Delete specific service version
gcloud app versions delete [VERSION_ID] --service=ui

# Stop all services (billing continues for default service)
gcloud app versions stop [VERSION_ID]

# To completely remove App Engine (not reversible):
# Must be done via Cloud Console
```

## Security Best Practices

1. **Enable IAP** (Identity-Aware Proxy) for authentication
2. **Use Secret Manager** for sensitive configuration
3. **Enable Cloud Armor** for DDoS protection
4. **Set up VPC Service Controls** for data exfiltration prevention
5. **Regular security updates** of dependencies

## Production Readiness Checklist

- [ ] Replace in-memory storage with persistent storage
- [ ] Implement proper authentication/authorization
- [ ] Set up monitoring and alerting
- [ ] Configure custom domain
- [ ] Enable HTTPS only (already enforced by default)
- [ ] Implement rate limiting
- [ ] Set up CI/CD pipeline
- [ ] Configure backup strategy
- [ ] Load testing
- [ ] Security audit

## Support

For issues or questions:
1. Check [GCP App Engine documentation](https://cloud.google.com/appengine/docs)
2. Review application logs
3. Check [GCP Status Dashboard](https://status.cloud.google.com/)

## Additional Resources

- [App Engine Python 3 Runtime](https://cloud.google.com/appengine/docs/standard/python3)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Streamlit Deployment](https://docs.streamlit.io/knowledge-base/tutorials/deploy)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
