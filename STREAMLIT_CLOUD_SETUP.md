# Streamlit Cloud Configuration Guide

## Issue
Your Streamlit app is deployed at https://macystorechatbot-rag-hjiddencukj2xgk8ycjznh.streamlit.app/ but cannot connect to the backend because it's trying to reach `http://127.0.0.1:8000` (localhost).

## Solution
You need to configure your Streamlit Cloud app to use your deployed Cloud Run backend URL.

## Step-by-Step Instructions

### 1. Get Your Backend URL

First, find your backend Cloud Run service URL. You can get this from:

**Option A: From the error message you shared earlier**
```
Service URL: https://***-574340049371.***.run.app
```

**Option B: Using gcloud CLI**
```bash
gcloud run services describe YOUR_BACKEND_SERVICE_NAME \
  --region YOUR_REGION \
  --format='value(status.url)'
```

**Option C: From Google Cloud Console**
1. Go to https://console.cloud.google.com/run
2. Find your backend service
3. Copy the URL shown

### 2. Configure Streamlit Cloud Secrets

1. **Go to your Streamlit Cloud app**: https://macystorechatbot-rag-hjiddencukj2xgk8ycjznh.streamlit.app/

2. **Click the menu icon (☰)** in the top right corner

3. **Select "Settings"** from the dropdown

4. **Click "Secrets"** in the left sidebar

5. **Add this configuration** (replace with your actual backend URL):
   ```toml
   API_URL = "https://your-backend-service-574340049371.us-central1.run.app"
   ```

6. **Click "Save"**

7. **Your app will automatically restart** and connect to the backend

### 3. Verify the Configuration

After saving the secrets:

1. Wait for the app to restart (usually 10-20 seconds)
2. Try asking a question in the UI
3. The app should now successfully connect to your backend

### Example Configuration

If your backend URL is:
```
https://macy-rag-backend-574340049371.us-central1.run.app
```

Your Streamlit secrets should be:
```toml
API_URL = "https://macy-rag-backend-574340049371.us-central1.run.app"
```

**Important Notes**:
- Do NOT include a trailing slash
- Use `https://` not `http://`
- Make sure the URL is the Cloud Run service URL, not localhost

## Finding Your Exact Backend URL

Since you mentioned the service URL in the error was partially redacted (`https://***-574340049371.***.run.app`), here are ways to find your complete backend URL:

### Method 1: Check GitHub Secrets

Your GitHub Actions workflow uses `${{ secrets.API_URL }}`. Check your GitHub repository secrets:

1. Go to your GitHub repository
2. Click "Settings" > "Secrets and variables" > "Actions"
3. Look for `API_URL` secret
4. Use that URL for Streamlit

### Method 2: Deploy and Get URL

Run your GitHub Actions workflow or deploy manually:

```bash
# This will show the service URL after deployment
gcloud run services list --region=YOUR_REGION
```

### Method 3: Check Cloud Run Console

1. Go to https://console.cloud.google.com/run
2. Select your project: `animated-surfer-476413-c1`
3. Find your backend service (likely named something like `macy-rag-backend`)
4. Copy the URL shown

## Testing Locally

To test locally before deploying:

```bash
# Start backend
./run_backend.sh

# In another terminal, start frontend with API_URL
export API_URL="http://127.0.0.1:8000"
./run_frontend.sh
```

## Common Issues

### Issue: "Cannot connect to backend API"

**Cause**: Streamlit secrets not configured or incorrect URL

**Solution**:
1. Check that you added the secrets correctly
2. Verify the backend URL is correct and accessible
3. Make sure backend service is deployed and running

### Issue: "404 Not Found"

**Cause**: Backend URL is wrong or service doesn't exist

**Solution**:
1. Verify the backend service is deployed
2. Check the URL is exactly correct (no typos)
3. Test the backend URL directly in a browser

### Issue: "Timeout"

**Cause**: Backend is slow or not responding

**Solution**:
1. Check backend Cloud Run logs
2. Verify backend has enough memory/CPU
3. Check if cold start is causing delays

### Issue: "CORS Error"

**Cause**: Backend not allowing requests from Streamlit domain

**Solution**: Add CORS middleware to backend (already implemented in main.py)

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Cloud                        │
│                                                             │
│  https://macystorechatbot-rag-*.streamlit.app/            │
│                                                             │
│  • Reads API_URL from secrets                              │
│  • Makes HTTP requests to backend                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTPS
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Run                         │
│                                                             │
│  https://your-backend-***.run.app                          │
│                                                             │
│  • FastAPI backend                                         │
│  • RAG orchestrator                                        │
│  • Vertex AI integration                                   │
│  • Infrastructure security                                 │
└─────────────────────────────────────────────────────────────┘
```

## Updated Files

The following files have been updated to support Streamlit secrets:

1. **ui/app.py** - Added Streamlit secrets support and better error messages
2. **.streamlit/secrets.toml.example** - Example configuration file

## Verification Checklist

After configuring Streamlit secrets:

- [ ] Backend service is deployed on Cloud Run
- [ ] Backend URL is accessible (test in browser)
- [ ] Streamlit secrets configured with correct URL
- [ ] Streamlit app restarted
- [ ] App can connect to backend
- [ ] Questions can be asked successfully
- [ ] Infrastructure security still working

## Next Steps

1. **Get your backend URL** (use one of the methods above)
2. **Add to Streamlit secrets** (Settings > Secrets)
3. **Test the connection** (ask a question)
4. **Verify infrastructure security** (ask "Where is this hosted?")

## Support

If you continue to have issues:

1. Check the backend is deployed:
   ```bash
   gcloud run services list --region=YOUR_REGION
   ```

2. Test the backend directly:
   ```bash
   curl https://your-backend-url.run.app/health
   ```

3. Check Streamlit Cloud logs for detailed error messages

4. Verify the secrets are correctly formatted (no extra spaces, quotes, etc.)

## Example Complete Configuration

**Streamlit Secrets** (Settings > Secrets):
```toml
API_URL = "https://macy-rag-backend-574340049371.us-central1.run.app"
```

**GitHub Actions Secrets**:
- `GCP_SA_KEY` - Your service account JSON
- `GCP_PROJECT_ID` - `animated-surfer-476413-c1`
- `GCP_REGION` - e.g., `us-central1`
- `BACKEND_SERVICE` - e.g., `macy-rag-backend`
- `UI_SERVICE` - e.g., `macy-rag-frontend`
- `API_URL` - Your backend Cloud Run URL

## Security Note

The backend URL in Streamlit secrets is safe to expose as:
- The backend is protected by infrastructure security
- No sensitive data is in the URL
- The backend has authentication/authorization if needed
- Infrastructure details are blocked by security guard

However, avoid sharing:
- Service account keys
- Database credentials
- API keys
- Internal implementation details
