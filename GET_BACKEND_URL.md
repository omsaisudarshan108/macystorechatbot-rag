# How to Get Your Backend URL

## Quick Method: GitHub Actions Log

Your backend is deployed! The URL is in your GitHub Actions log.

### Steps:

1. **Go to GitHub Actions**:
   - https://github.com/omsaisudarshan108/macystorechatbot-rag/actions

2. **Click on the latest workflow run**:
   - Look for "Add infrastructure security and fix deployment issues"
   - Click on it

3. **Click "Deploy backend" step**:
   - In the left sidebar, click "Deploy backend"
   - Or expand the step in the main view

4. **Scroll to the bottom of the logs**:
   - Look for this line:
   ```
   Service URL: https://YOUR-BACKEND-SERVICE.run.app
   ```

5. **Copy the complete URL**:
   - Example: `https://macy-rag-backend-574340049371.us-central1.run.app`
   - The format is: `https://SERVICE-NAME-PROJECT-NUMBER.REGION.run.app`

6. **Write it here for reference**:
   ```
   Backend URL: ________________________________
   ```

## Alternative: Use gcloud CLI

If you have gcloud installed and authenticated:

```bash
# List all Cloud Run services
gcloud run services list --project=animated-surfer-476413-c1

# Get specific service URL
gcloud run services describe YOUR-SERVICE-NAME \
  --project=animated-surfer-476413-c1 \
  --region=us-central1 \
  --format='value(status.url)'
```

## Alternative: Google Cloud Console

1. Go to: https://console.cloud.google.com/run?project=animated-surfer-476413-c1
2. Find your backend service in the list
3. Click on it
4. The URL is shown at the top

## Once You Have the URL

### Test the Backend:

```bash
# Replace with your actual URL
BACKEND_URL="https://YOUR-BACKEND-URL.run.app"

# Test 1: Health check
curl $BACKEND_URL/health

# Expected response:
# {"status": "healthy", "environment": "production"}

# Test 2: Infrastructure security
curl -X POST "$BACKEND_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Where is this hosted?", "store_id": "1234"}'

# Expected response:
# {
#   "answer": "This system operates within Macy's secure cloud environment...",
#   "is_infrastructure_blocked": true
# }
```

### Configure Streamlit Cloud:

1. Go to: https://macystorechatbot-rag-hjiddencukj2xgk8ycjznh.streamlit.app/

2. Click the ☰ menu (top right) → Settings → Secrets

3. Add this configuration (replace with your actual URL):
   ```toml
   API_URL = "https://YOUR-BACKEND-URL.run.app"
   ```

4. Click Save

5. Wait ~15 seconds for the app to restart

6. Test by asking: "Where is this hosted?"

## Troubleshooting

### Can't find the workflow run?

- Make sure you're looking at: https://github.com/omsaisudarshan108/macystorechatbot-rag/actions
- The most recent run should be at the top
- Look for runs with your commit message

### URL is partially redacted in logs?

GitHub Actions sometimes redacts secrets. The pattern is:
```
Service URL: https://***-574340049371.***.run.app
```

From your error message, we know:
- Project number: `574340049371`
- Pattern: `https://[service-name]-574340049371.[region].run.app`

The service name is whatever you set in `BACKEND_SERVICE` secret.
The region is whatever you set in `GCP_REGION` secret (likely `us-central1`).

### Still can't find it?

Check your GitHub Secrets to see what service names you're using:
1. Go to your repo → Settings → Secrets and variables → Actions
2. Look at `BACKEND_SERVICE` secret name
3. The URL will be: `https://[that-name]-574340049371.[region].run.app`

## Next Steps

Once you have the backend URL:

1. ✅ Test backend health endpoint
2. ✅ Test infrastructure security
3. ✅ Configure Streamlit Cloud secrets
4. ✅ Test Streamlit app
5. ✅ Verify everything works end-to-end

See [POST_DEPLOYMENT_CHECKLIST.md](POST_DEPLOYMENT_CHECKLIST.md) for complete verification steps.
