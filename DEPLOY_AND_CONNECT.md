# Deploy Backend and Connect Streamlit - Complete Guide

## Current Situation

1. ✅ Your **Streamlit frontend** is deployed: https://macystorechatbot-rag-hjiddencukj2xgk8ycjznh.streamlit.app/
2. ❌ Your **backend is NOT deployed yet** (or not accessible)
3. ❌ Streamlit can't connect because there's no backend URL configured

## Solution: Deploy Backend First, Then Connect

### Option 1: Deploy via GitHub Actions (Recommended)

#### Step 1: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets if not already present:

| Secret Name | Value | Example |
|------------|-------|---------|
| `GCP_SA_KEY` | Service account JSON | (Paste the full JSON from your gcp_sa_key.json file) |
| `GCP_PROJECT_ID` | Your project ID | `animated-surfer-476413-c1` |
| `GCP_REGION` | Deployment region | `us-central1` |
| `BACKEND_SERVICE` | Backend service name | `macy-rag-backend` |
| `UI_SERVICE` | Frontend service name | `macy-rag-ui` |
| `API_URL` | Backend URL (after first deploy) | `https://macy-rag-backend-574340049371.us-central1.run.app` |

#### Step 2: Push to GitHub to Trigger Deployment

```bash
# Make sure all changes are committed
git add .
git commit -m "Deploy backend with infrastructure security"
git push origin main
```

#### Step 3: Monitor Deployment

1. Go to your GitHub repository
2. Click "Actions" tab
3. Watch the "Deploy to Cloud Run" workflow
4. Wait for both backend and frontend deployments to complete

#### Step 4: Get Backend URL

After deployment completes, the GitHub Actions log will show:
```
Service URL: https://YOUR-BACKEND-SERVICE.run.app
```

Copy this URL.

#### Step 5: Add API_URL to GitHub Secrets

1. Go back to GitHub Secrets
2. Add or update `API_URL` secret with your backend URL
3. This will be used by the frontend deployment

#### Step 6: Configure Streamlit Cloud

1. Go to: https://macystorechatbot-rag-hjiddencukj2xgk8ycjznh.streamlit.app/
2. Click ☰ menu → Settings → Secrets
3. Add:
   ```toml
   API_URL = "https://YOUR-BACKEND-SERVICE.run.app"
   ```
4. Click Save

### Option 2: Deploy Manually with gcloud

#### Step 1: Authenticate

```bash
gcloud auth login
gcloud config set project animated-surfer-476413-c1
```

#### Step 2: Deploy Backend

```bash
gcloud run deploy macy-rag-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --command uvicorn \
  --args backend.api.main:app,--host,0.0.0.0,--port,8080 \
  --set-env-vars PROJECT_ID=animated-surfer-476413-c1 \
  --memory 2Gi \
  --port 8080
```

This will output:
```
Service URL: https://macy-rag-backend-XXXXXX.us-central1.run.app
```

#### Step 3: Test Backend

```bash
# Replace with your actual URL
curl https://macy-rag-backend-XXXXXX.us-central1.run.app/health
```

Should return:
```json
{"status": "healthy", "environment": "production"}
```

#### Step 4: Configure Streamlit Cloud

Use the backend URL from step 2 in your Streamlit secrets (see Option 1, Step 6).

### Option 3: Check if Backend Already Deployed

Maybe your backend is already deployed but under a different name or region.

#### Check All Regions

```bash
# Check all regions
for region in us-central1 us-east1 us-west1 europe-west1; do
  echo "Checking $region..."
  gcloud run services list --region=$region --project=animated-surfer-476413-c1
done
```

#### Check Specific Service

```bash
# If you know the service name
gcloud run services describe YOUR_SERVICE_NAME \
  --region=us-central1 \
  --project=animated-surfer-476413-c1 \
  --format='value(status.url)'
```

## Verification Checklist

### 1. Backend Deployed ✓
```bash
# Should show your backend service
gcloud run services list --region=us-central1
```

### 2. Backend Accessible ✓
```bash
# Should return healthy status
curl https://YOUR-BACKEND-URL/health
```

### 3. Backend API Works ✓
```bash
# Test infrastructure security
curl -X POST "https://YOUR-BACKEND-URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Where is this hosted?", "store_id": "1234"}'
```

Should return compliant response:
```json
{
  "answer": "This system operates within Macy's secure cloud environment...",
  "is_infrastructure_blocked": true
}
```

### 4. Streamlit Connected ✓
1. Go to your Streamlit app
2. Ask "Where is this hosted?"
3. Should get the compliant security response

## Common Issues

### Issue: "No such project"

**Solution**: Make sure you're authenticated and have access to the project:
```bash
gcloud auth login
gcloud projects list
gcloud config set project animated-surfer-476413-c1
```

### Issue: "Permission denied"

**Solution**: Your service account needs these roles:
- Cloud Run Admin
- Service Account User
- Artifact Registry Writer (if using Artifact Registry)

Grant permissions:
```bash
gcloud projects add-iam-policy-binding animated-surfer-476413-c1 \
  --member="serviceAccount:YOUR-SA@animated-surfer-476413-c1.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

### Issue: "Build failed"

**Solution**: Check your requirements.txt and ensure all dependencies are installable:
```bash
# Test locally
python -m venv test_venv
source test_venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Service timeout"

**Solution**: Backend takes time to cold start. Increase timeout or add warmup:
- Increase memory to 2Gi (already set)
- Set min instances to 1 (costs more but no cold starts)
- Optimize startup time

## Architecture After Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Cloud                        │
│  https://macystorechatbot-rag-*.streamlit.app/            │
│                                                             │
│  Reads API_URL from secrets                                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ HTTPS
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Run                         │
│  https://macy-rag-backend-*.us-central1.run.app            │
│                                                             │
│  • FastAPI Backend                                         │
│  • Infrastructure Security ✓                               │
│  • RAG Orchestrator                                        │
│  • Vertex AI Integration                                   │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start Commands

```bash
# 1. Deploy backend
gcloud run deploy macy-rag-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --command uvicorn \
  --args backend.api.main:app,--host,0.0.0.0,--port,8080 \
  --set-env-vars PROJECT_ID=animated-surfer-476413-c1 \
  --memory 2Gi

# 2. Get the URL from output, then test it
curl https://YOUR-BACKEND-URL/health

# 3. Add to Streamlit Cloud secrets:
#    Settings > Secrets > Add:
#    API_URL = "https://YOUR-BACKEND-URL"

# 4. Test in Streamlit app - ask any question
```

## What Happens Next

1. **Backend deploys** to Cloud Run (~2-3 minutes)
2. **You get backend URL** from deployment output
3. **You add URL to Streamlit secrets** (takes 10 seconds)
4. **Streamlit app restarts** automatically (~15 seconds)
5. **Everything works!** Frontend can now reach backend

## Support

If you continue having issues:

1. **Check deployment logs**:
   ```bash
   gcloud run services logs read macy-rag-backend --region=us-central1 --limit=50
   ```

2. **Verify service is running**:
   ```bash
   gcloud run services describe macy-rag-backend --region=us-central1
   ```

3. **Test locally first**:
   ```bash
   ./run_local.sh
   # Verify everything works locally
   ```

## Success Criteria

- [ ] Backend deployed to Cloud Run
- [ ] Backend URL obtained
- [ ] Backend /health endpoint returns 200
- [ ] Backend /ask endpoint works
- [ ] Infrastructure security working (test "Where is this hosted?")
- [ ] Streamlit secrets configured with API_URL
- [ ] Streamlit app can connect to backend
- [ ] Questions can be asked successfully
- [ ] Compliant responses working

## Next Steps

Choose your deployment method:
1. **GitHub Actions** (automated) - Recommended for production
2. **Manual gcloud** (quick test) - Good for testing
3. **Local testing** (development) - Use `./run_local.sh`

Then follow the steps above to deploy and connect.
