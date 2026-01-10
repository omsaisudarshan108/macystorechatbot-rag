# QUICK FIX: Streamlit Cloud Connection Issue

## Problem
Your Streamlit app can't connect to the backend because it's using `localhost` instead of your Cloud Run URL.

## Solution (2 minutes)

### Step 1: Get Your Backend URL

Run this command to find your backend URL:
```bash
gcloud run services list --region=us-central1 --project=animated-surfer-476413-c1
```

Look for your backend service and copy its URL (something like `https://***-574340049371.us-central1.run.app`)

### Step 2: Configure Streamlit Cloud

1. Go to: https://macystorechatbot-rag-hjiddencukj2xgk8ycjznh.streamlit.app/

2. Click the **☰ menu** (top right) → **Settings** → **Secrets**

3. Paste this (replace with your actual backend URL):
   ```toml
   API_URL = "https://your-backend-service.run.app"
   ```

4. Click **Save**

5. Wait ~15 seconds for restart

### Step 3: Test

Ask any question in the Streamlit UI. It should now work!

## Find Your Backend URL

### Option 1: From gcloud
```bash
gcloud run services list --region=us-central1
```

### Option 2: From Cloud Console
1. Go to: https://console.cloud.google.com/run?project=animated-surfer-476413-c1
2. Find your backend service
3. Copy the URL

### Option 3: From GitHub Secrets
1. Go to your GitHub repo → Settings → Secrets → Actions
2. Check the `API_URL` secret value

## Example

If your backend URL is:
```
https://macy-backend-574340049371.us-central1.run.app
```

Your Streamlit secret should be:
```toml
API_URL = "https://macy-backend-574340049371.us-central1.run.app"
```

## That's It!

Your Streamlit app will now connect to your Cloud Run backend.

---

For detailed instructions, see [STREAMLIT_CLOUD_SETUP.md](STREAMLIT_CLOUD_SETUP.md)
