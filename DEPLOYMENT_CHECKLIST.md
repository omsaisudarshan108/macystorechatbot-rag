# Pre-Deployment Checklist

Use this checklist before deploying to ensure everything is configured correctly.

## Prerequisites ✓

- [ ] GCP account with billing enabled
- [ ] gcloud CLI installed (`gcloud --version`)
- [ ] Authenticated with GCP (`gcloud auth list`)
- [ ] Project created in GCP Console
- [ ] Project ID configured (`gcloud config get-value project`)

## APIs Enabled ✓

Run these commands to enable required APIs:

```bash
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
```

Check with:
```bash
gcloud services list --enabled | grep -E "appengine|cloudbuild|aiplatform|storage"
```

- [ ] App Engine Admin API enabled
- [ ] Cloud Build API enabled
- [ ] Vertex AI API enabled
- [ ] Cloud Storage API enabled

## App Engine Initialization ✓

**First time only:**
```bash
gcloud app create --region=us-central
```

Check if already initialized:
```bash
gcloud app describe
```

- [ ] App Engine initialized in your project
- [ ] Region selected (recommend: us-central)

## Configuration Review ✓

### 1. Backend Configuration (`app.yaml`)

- [ ] `PROJECT_ID` matches your GCP project
- [ ] `instance_class` appropriate for your needs (F4 = 1GB)
- [ ] Scaling settings match your requirements
- [ ] Region is correct

### 2. Frontend Configuration (`ui-app.yaml`)

- [ ] `API_URL` will be set to your backend URL
  - Auto-updated by deploy.sh
  - Or manually set to: `https://YOUR_PROJECT_ID.uc.r.appspot.com`
- [ ] `instance_class` appropriate (F2 = 512MB)
- [ ] Scaling settings reasonable

### 3. Dependencies (`requirements.txt`)

- [ ] All required packages listed
- [ ] No version conflicts
- [ ] `gunicorn` included
- [ ] `python-multipart` included
- [ ] `google-cloud-storage` included

### 4. Application Code

- [ ] Backend health endpoint exists (`/health`)
- [ ] Frontend uses environment variable for API_URL
- [ ] No hardcoded credentials
- [ ] No debug mode enabled

## Local Testing ✓

Before deploying, verify locally:

```bash
# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:8501
```

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Health endpoint returns 200 OK
- [ ] Can upload and ingest a document
- [ ] Can query the system

## File Verification ✓

Check all deployment files exist:

```bash
ls -l app.yaml ui-app.yaml main.py .gcloudignore requirements.txt deploy.sh startup.sh
```

- [ ] `app.yaml` exists and is valid YAML
- [ ] `ui-app.yaml` exists and is valid YAML
- [ ] `main.py` exists in project root
- [ ] `.gcloudignore` exists
- [ ] `requirements.txt` is complete
- [ ] `deploy.sh` is executable (`chmod +x deploy.sh`)
- [ ] `startup.sh` is executable (`chmod +x startup.sh`)

## Security Review ✓

- [ ] No API keys in code
- [ ] No passwords in configuration files
- [ ] Sensitive data in Secret Manager (if applicable)
- [ ] `.gcloudignore` excludes sensitive files
- [ ] Environment variables properly set
- [ ] Consider enabling IAP for production

## Cost Awareness ✓

- [ ] Understand App Engine pricing model
- [ ] Set up billing alerts
- [ ] Configure max instances to control costs
- [ ] Understand Vertex AI API costs
- [ ] Know how to stop/delete services

Set a billing alert:
```bash
# In Cloud Console: Billing > Budgets & alerts
# Or use: gcloud billing budgets create
```

## Deployment Strategy ✓

Choose your deployment method:

### Option A: Automated (Recommended)
- [ ] Run `./deploy.sh`
- [ ] Monitor output for errors
- [ ] Verify both services deploy successfully

### Option B: Manual
- [ ] Run `./startup.sh` to download models
- [ ] Deploy backend: `gcloud app deploy app.yaml`
- [ ] Update `ui-app.yaml` with backend URL
- [ ] Deploy frontend: `gcloud app deploy ui-app.yaml`

## Post-Deployment Verification ✓

After deployment completes:

### 1. Check Deployment Status
```bash
gcloud app versions list
gcloud app services list
```

- [ ] Both services (default and ui) show as SERVING
- [ ] Latest version is receiving traffic

### 2. Test Backend Endpoints

```bash
export BACKEND_URL="https://$(gcloud config get-value project).uc.r.appspot.com"

# Test health
curl $BACKEND_URL/health

# Test root
curl $BACKEND_URL/

# Test docs
curl $BACKEND_URL/docs
```

- [ ] `/health` returns 200 OK
- [ ] `/` returns API info
- [ ] `/docs` shows Swagger UI

### 3. Test Frontend

```bash
export UI_URL="https://ui-dot-$(gcloud config get-value project).uc.r.appspot.com"

# Open in browser
open $UI_URL
# or
gcloud app browse -s ui
```

- [ ] UI loads without errors
- [ ] Can see upload interface
- [ ] Can enter questions
- [ ] No console errors

### 4. End-to-End Test

- [ ] Upload a test document through UI
- [ ] Wait for ingestion to complete
- [ ] Ask a question about the document
- [ ] Verify answer and citations appear
- [ ] Check backend logs for errors

### 5. Monitor Logs

```bash
# Backend logs
gcloud app logs tail -s default

# Frontend logs
gcloud app logs tail -s ui

# All logs
gcloud app logs tail
```

- [ ] No error messages in logs
- [ ] Requests logging properly
- [ ] Response times acceptable

## Monitoring Setup ✓

After successful deployment:

- [ ] Set up uptime checks
- [ ] Configure error alerting
- [ ] Create performance dashboard
- [ ] Set up cost tracking
- [ ] Document access URLs

## Documentation ✓

- [ ] Update team documentation with URLs
- [ ] Document any custom configurations
- [ ] Share monitoring dashboard
- [ ] Document rollback procedures
- [ ] Create runbook for common issues

## Rollback Plan ✓

Know how to rollback if needed:

```bash
# List versions
gcloud app versions list

# Traffic to previous version
gcloud app services set-traffic default --splits [VERSION]=1
gcloud app services set-traffic ui --splits [VERSION]=1
```

- [ ] Know how to list versions
- [ ] Know how to redirect traffic
- [ ] Tested rollback procedure

## Success Criteria ✓

Deployment is successful when:

- [ ] ✅ Backend service accessible via HTTPS
- [ ] ✅ Frontend service accessible via HTTPS
- [ ] ✅ Health checks passing
- [ ] ✅ Can ingest documents
- [ ] ✅ Can query system
- [ ] ✅ No errors in logs
- [ ] ✅ Response times acceptable
- [ ] ✅ Auto-scaling working
- [ ] ✅ Team notified of URLs

## Final Steps ✓

- [ ] Save URLs in secure location
- [ ] Update project documentation
- [ ] Notify stakeholders
- [ ] Schedule post-deployment review
- [ ] Plan for monitoring and maintenance

---

## Quick Deploy Command

If all checklist items are complete:

```bash
./deploy.sh
```

## Emergency Contacts

- **GCP Support**: https://cloud.google.com/support
- **Status Page**: https://status.cloud.google.com/
- **Billing**: https://console.cloud.google.com/billing

---

**Last Updated**: 2026-01-09
**Deployment Type**: GCP App Engine Standard (Python 3.12)
