# Docker Deployment Guide

**Date:** 2026-01-11
**Version:** 1.0
**Status:** Production Ready

---

## OVERVIEW

This guide covers deploying the RAG application using Docker containers. The application is fully portable and can run on:
- **Local development** (Docker Compose)
- **Google Cloud Run** (any GCP project)
- **Any Kubernetes cluster**
- **Any container orchestration platform**

---

## TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Local Development with Docker](#local-development-with-docker)
3. [Deploy to Google Cloud Run](#deploy-to-google-cloud-run)
4. [Deploy to Kubernetes](#deploy-to-kubernetes)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## PREREQUISITES

### Required Tools

- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ (included with Docker Desktop)
- **Google Cloud SDK** (for GCP deployment) ([Install gcloud](https://cloud.google.com/sdk/docs/install))

### GCP Setup (for Cloud Run deployment)

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** authenticated: `gcloud auth login`
3. **Required APIs** (enabled via setup script)

---

## LOCAL DEVELOPMENT WITH DOCKER

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd temp_rag-main

# 2. Copy environment template
cp .env.template .env

# 3. Edit .env with your PROJECT_ID
nano .env  # or use your preferred editor

# 4. Start the application
docker-compose up -d

# 5. Access the application
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose restart

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec backend bash
```

### Volume Management

Data is persisted in Docker volumes:

```bash
# View volumes
docker volume ls

# Inspect volume
docker volume inspect temp_rag-main_data

# Backup data volume
docker run --rm -v temp_rag-main_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/data-backup.tar.gz -C /data .

# Restore data volume
docker run --rm -v temp_rag-main_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/data-backup.tar.gz -C /data
```

---

## DEPLOY TO GOOGLE CLOUD RUN

### Option 1: Automated Deployment (Recommended)

Use the provided deployment script for any GCP project:

```bash
# Step 1: Setup GCP project (one-time)
./setup-gcp-project.sh YOUR_PROJECT_ID

# Step 2: Deploy application
./deploy-gcp.sh YOUR_PROJECT_ID us-central1
```

**What the scripts do:**

**setup-gcp-project.sh:**
- Enables required GCP APIs
- Configures IAM permissions
- Creates service accounts
- Sets up Secret Manager
- Creates Cloud Storage bucket

**deploy-gcp.sh:**
- Builds Docker images
- Pushes to Artifact Registry
- Deploys backend to Cloud Run
- Deploys frontend to Cloud Run
- Configures networking

### Option 2: Manual Deployment

#### Step 1: Enable APIs

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  --project=YOUR_PROJECT_ID
```

#### Step 2: Create Artifact Registry

```bash
gcloud artifacts repositories create rag-app \
  --repository-format=docker \
  --location=us-central1 \
  --project=YOUR_PROJECT_ID
```

#### Step 3: Build and Deploy Backend

```bash
# Build image
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/rag-app/rag-backend:latest \
  --file Dockerfile.backend \
  --project=YOUR_PROJECT_ID

# Deploy to Cloud Run
gcloud run deploy rag-backend \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/rag-app/rag-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=YOUR_PROJECT_ID \
  --memory 2Gi \
  --cpu 2 \
  --project=YOUR_PROJECT_ID
```

#### Step 4: Build and Deploy Frontend

```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe rag-backend \
  --region us-central1 \
  --format 'value(status.url)' \
  --project=YOUR_PROJECT_ID)

# Build image
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/rag-app/rag-frontend:latest \
  --file Dockerfile.frontend \
  --project=YOUR_PROJECT_ID

# Deploy to Cloud Run
gcloud run deploy rag-frontend \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/rag-app/rag-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_URL=$BACKEND_URL \
  --memory 1Gi \
  --cpu 1 \
  --project=YOUR_PROJECT_ID
```

### Configure Vertex AI Permissions

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID \
  --format="value(projectNumber)")

# Grant Vertex AI access
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### View Deployed Services

```bash
# List Cloud Run services
gcloud run services list --project=YOUR_PROJECT_ID

# Get frontend URL
gcloud run services describe rag-frontend \
  --region us-central1 \
  --format 'value(status.url)' \
  --project=YOUR_PROJECT_ID
```

---

## DEPLOY TO KUBERNETES

### Kubernetes Manifests

Create `k8s/backend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rag-backend
  template:
    metadata:
      labels:
        app: rag-backend
    spec:
      containers:
      - name: backend
        image: YOUR_REGISTRY/rag-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: PROJECT_ID
          value: "YOUR_PROJECT_ID"
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: rag-backend
spec:
  selector:
    app: rag-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

Create `k8s/frontend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rag-frontend
  template:
    metadata:
      labels:
        app: rag-frontend
    spec:
      containers:
      - name: frontend
        image: YOUR_REGISTRY/rag-frontend:latest
        ports:
        - containerPort: 8501
        env:
        - name: API_URL
          value: "http://rag-backend:8000"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: rag-frontend
spec:
  selector:
    app: rag-frontend
  ports:
  - port: 8501
    targetPort: 8501
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# Get frontend URL
kubectl get service rag-frontend
```

---

## CONFIGURATION

### Environment Variables

#### Backend (Dockerfile.backend)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROJECT_ID` | GCP Project ID | - | Yes |
| `ENVIRONMENT` | Environment name | `local` | No |
| `PORT` | Backend port | `8000` | No |
| `VERTEX_AI_LOCATION` | Vertex AI region | `us-central1` | No |
| `VERTEX_AI_MODEL` | Gemini model name | `gemini-2.0-flash` | No |

#### Frontend (Dockerfile.frontend)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_URL` | Backend API URL | `http://backend:8000` | Yes |
| `STREAMLIT_SERVER_PORT` | Frontend port | `8501` | No |

### Docker Compose Override

Create `docker-compose.override.yml` for local customization:

```yaml
version: '3.8'

services:
  backend:
    environment:
      - LOG_LEVEL=DEBUG
    volumes:
      - ./backend:/app/backend:ro  # Hot reload for development

  frontend:
    environment:
      - STREAMLIT_THEME_BASE=dark
```

### Cloud Run Configuration

Set environment variables via gcloud:

```bash
gcloud run services update rag-backend \
  --set-env-vars KEY1=value1,KEY2=value2 \
  --region us-central1 \
  --project YOUR_PROJECT_ID
```

---

## TROUBLESHOOTING

### Local Docker Issues

#### Container won't start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check if ports are in use
lsof -i :8000
lsof -i :8501

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

#### Network connectivity issues

```bash
# Inspect network
docker network inspect temp_rag-main_rag-network

# Test backend from frontend
docker-compose exec frontend curl http://backend:8000/health
```

### Cloud Run Issues

#### Build fails

```bash
# Check Cloud Build logs
gcloud builds list --limit 5 --project YOUR_PROJECT_ID

# View detailed build log
gcloud builds log BUILD_ID --project YOUR_PROJECT_ID
```

#### Service won't deploy

```bash
# Check service status
gcloud run services describe rag-backend \
  --region us-central1 \
  --project YOUR_PROJECT_ID

# View service logs
gcloud logging read "resource.type=cloud_run_revision AND \
  resource.labels.service_name=rag-backend" \
  --limit 50 \
  --format json \
  --project YOUR_PROJECT_ID
```

#### Vertex AI 403 errors

```bash
# Verify IAM permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/aiplatform.user"

# Add permission if missing
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID \
  --format="value(projectNumber)")

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Performance Issues

#### Backend slow to respond

```bash
# Increase memory and CPU
gcloud run services update rag-backend \
  --memory 4Gi \
  --cpu 2 \
  --region us-central1 \
  --project YOUR_PROJECT_ID
```

#### Frontend slow to load

```bash
# Enable HTTP/2
gcloud run services update rag-frontend \
  --use-http2 \
  --region us-central1 \
  --project YOUR_PROJECT_ID
```

---

## ARCHITECTURE

### Container Architecture

```
┌─────────────────────────────────────────────┐
│          Frontend Container                  │
│  (Streamlit on port 8501)                   │
│                                              │
│  - Serves web UI                            │
│  - Connects to backend API                  │
│  - Handles user interactions                │
└──────────────────┬──────────────────────────┘
                   │ HTTP
                   │
┌──────────────────▼──────────────────────────┐
│          Backend Container                   │
│  (FastAPI on port 8000)                     │
│                                              │
│  - RAG orchestration                        │
│  - Document processing                      │
│  - Safety checks                            │
│  - Vertex AI integration                    │
│  - Vector store (ChromaDB)                  │
│  - BM25 search                              │
└─────────────────────────────────────────────┘
```

### Cloud Run Architecture

```
┌────────────┐      HTTPS       ┌──────────────┐
│   Users    │ ──────────────► │   Frontend   │
└────────────┘                  │  Cloud Run   │
                                └──────┬───────┘
                                       │ HTTPS
                                       │
                                ┌──────▼───────┐
                                │   Backend    │
                                │  Cloud Run   │
                                └──────┬───────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
              ┌─────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
              │  Vertex AI  │   │Secret Manager│   │Cloud Storage│
              └─────────────┘   └──────────────┘   └─────────────┘
```

---

## BEST PRACTICES

### Security

1. **Never commit secrets** - Use Secret Manager or environment variables
2. **Enable authentication** - Remove `--allow-unauthenticated` for production
3. **Use service accounts** - Assign minimal required permissions
4. **Enable VPC** - Use VPC Service Controls for sensitive data

### Performance

1. **Use multi-stage builds** - Reduce image size
2. **Enable caching** - Use BuildKit and layer caching
3. **Set appropriate resources** - Memory and CPU based on load
4. **Use CDN** - Cache static assets

### Monitoring

1. **Enable Cloud Logging** - Centralized log management
2. **Set up alerts** - Monitor error rates and latency
3. **Use Cloud Trace** - Distributed tracing for requests
4. **Enable health checks** - Automatic recovery

---

## COST OPTIMIZATION

### Cloud Run Pricing

- **CPU/Memory:** Billed per 100ms of usage
- **Requests:** $0.40 per million requests
- **Networking:** Egress charged separately

### Optimization Tips

1. **Set min-instances=0** - Scale to zero when idle
2. **Right-size resources** - Don't over-provision
3. **Use request timeout** - Prevent runaway requests
4. **Enable concurrency** - Handle multiple requests per instance

---

## NEXT STEPS

1. **Deploy to staging** - Test in non-production environment
2. **Set up CI/CD** - Automate deployments with GitHub Actions
3. **Configure monitoring** - Set up Cloud Monitoring dashboards
4. **Enable autoscaling** - Configure based on traffic patterns
5. **Add custom domain** - Map your domain to Cloud Run services

---

**Documentation Version:** 1.0
**Last Updated:** 2026-01-11
**Maintained By:** Development Team
