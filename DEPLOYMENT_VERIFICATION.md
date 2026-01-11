# Deployment Verification Checklist

Use this checklist to verify successful deployment of the RAG application.

---

## Local Docker Deployment

### Pre-Deployment
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] `.env` file created from `.env.template`
- [ ] `PROJECT_ID` set in `.env` file

### Deployment
```bash
docker-compose up -d
```

### Verification
- [ ] Backend container running (`docker-compose ps backend`)
- [ ] Frontend container running (`docker-compose ps frontend`)
- [ ] Backend health check passes (`curl http://localhost:8000/health`)
- [ ] Frontend accessible (`curl http://localhost:8501`)
- [ ] Backend logs show no errors (`docker-compose logs backend | tail -20`)
- [ ] Frontend logs show no errors (`docker-compose logs frontend | tail -20`)

### Functional Testing
- [ ] Can access frontend UI at http://localhost:8501
- [ ] Can upload document successfully
- [ ] Can ask question and get answer with citations
- [ ] Safety indicators display correctly
- [ ] Language detection works (English/Spanish)

---

## Google Cloud Run Deployment

### Pre-Deployment
- [ ] gcloud CLI installed (`gcloud --version`)
- [ ] Authenticated (`gcloud auth list`)
- [ ] Project selected (`gcloud config get-value project`)
- [ ] Billing enabled on GCP project

### Setup (One-Time)
```bash
./setup-gcp-project.sh YOUR_PROJECT_ID
```

- [ ] APIs enabled successfully
- [ ] IAM permissions configured
- [ ] Service account created
- [ ] No errors in script output

### Deployment
```bash
./deploy-gcp.sh YOUR_PROJECT_ID us-central1
```

- [ ] Backend image built successfully
- [ ] Backend deployed to Cloud Run
- [ ] Frontend image built successfully
- [ ] Frontend deployed to Cloud Run
- [ ] Backend URL displayed
- [ ] Frontend URL displayed
- [ ] No deployment errors

### Verification

#### Backend Service
```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe rag-backend --region us-central1 --format 'value(status.url)')

# Test health endpoint
curl $BACKEND_URL/health
```

- [ ] Backend service status: READY
- [ ] Health endpoint returns 200 OK
- [ ] Health check response valid JSON
- [ ] All safety features listed

#### Frontend Service
```bash
# Get frontend URL
FRONTEND_URL=$(gcloud run services describe rag-frontend --region us-central1 --format 'value(status.url)')

# Visit in browser
open $FRONTEND_URL
```

- [ ] Frontend service status: READY
- [ ] Frontend loads without errors
- [ ] Can connect to backend API
- [ ] UI displays correctly

### Functional Testing
- [ ] Can upload document via UI
- [ ] Can ask question and get answer
- [ ] Citations display correctly
- [ ] Safety checks functioning
- [ ] No 403 Vertex AI errors (or fallback working)

### IAM Verification
```bash
# Check Vertex AI permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/aiplatform.user"
```

- [ ] Service account has Vertex AI user role
- [ ] Secret Manager permissions granted
- [ ] Storage permissions granted

---

## Performance Verification

### Response Time Testing
```bash
# Test backend response time
time curl -X POST $BACKEND_URL/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"test","store_id":"test"}'
```

- [ ] Cold start < 5 seconds
- [ ] Warm request < 2 seconds
- [ ] RAG query < 5 seconds

### Load Testing (Optional)
```bash
# Install hey (HTTP load generator)
# macOS: brew install hey
# Linux: go install github.com/rakyll/hey@latest

# Run load test (100 requests, 10 concurrent)
hey -n 100 -c 10 -m GET $BACKEND_URL/health
```

- [ ] All requests return 200 OK
- [ ] No timeout errors
- [ ] Average latency < 500ms

---

## Security Verification

### Network Security
- [ ] Services not exposed publicly (if intended)
- [ ] HTTPS enabled (Cloud Run)
- [ ] Backend URL uses HTTPS
- [ ] Frontend URL uses HTTPS

### IAM Security
- [ ] Service accounts using least privilege
- [ ] No overly permissive roles
- [ ] Secrets not in environment variables
- [ ] API keys not exposed

### Application Security
- [ ] Document verification enabled
- [ ] Safety classification active
- [ ] Infrastructure guard working
- [ ] Response filtering disabled (per refactor)

---

## Monitoring Verification

### Cloud Logging (Cloud Run)
```bash
# View backend logs
gcloud logging read "resource.type=cloud_run_revision AND \
  resource.labels.service_name=rag-backend" \
  --limit 20 \
  --format json
```

- [ ] Logs visible in Cloud Logging
- [ ] No error messages
- [ ] Request logs captured
- [ ] Health checks logged

### Cloud Monitoring (Cloud Run)
- [ ] CPU metrics available
- [ ] Memory metrics available
- [ ] Request count visible
- [ ] Latency metrics tracked

---

## Cost Verification

### Check Billing
```bash
# View Cloud Run costs
gcloud alpha billing accounts list
```

- [ ] Billing account linked
- [ ] Budget alerts configured (optional)
- [ ] Cost tracking enabled

### Resource Optimization
- [ ] Min instances set to 0 (scale to zero)
- [ ] Max instances set appropriately
- [ ] CPU allocation appropriate
- [ ] Memory allocation appropriate

---

## Rollback Plan

### Local Docker
```bash
# Stop services
docker-compose down

# Revert changes
git checkout HEAD~1

# Restart
docker-compose up -d
```

### Cloud Run
```bash
# List revisions
gcloud run revisions list --service rag-backend --region us-central1

# Rollback to previous revision
gcloud run services update-traffic rag-backend \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

---

## Common Issues

### Local Docker: Port Already in Use
```bash
# Find and kill process
lsof -ti :8000 | xargs kill -9
lsof -ti :8501 | xargs kill -9
```

### Cloud Run: Build Fails
```bash
# Check build logs
gcloud builds list --limit 5
gcloud builds log BUILD_ID
```

### Cloud Run: 403 Vertex AI Error
```bash
# Grant permissions
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

---

## Sign-Off

### Deployment Team
- [ ] Deployment completed by: _________________
- [ ] Date: _________________
- [ ] Environment: [ ] Local [ ] Staging [ ] Production
- [ ] All checks passed: [ ] Yes [ ] No

### Issues Found
```
Document any issues encountered during verification:

1. 
2. 
3. 
```

### Notes
```
Additional deployment notes:



```

---

**Document Version:** 1.0
**Last Updated:** 2026-01-11
**Next Review:** After each deployment
