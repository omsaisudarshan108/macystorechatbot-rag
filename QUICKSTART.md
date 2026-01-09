# Quick Deployment Guide

## Prerequisites Check

```bash
# Check gcloud is installed
gcloud --version

# Check you're authenticated
gcloud auth list

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Verify project is set
gcloud config get-value project
```

## Enable Required APIs

```bash
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
```

## Initialize App Engine (First Time Only)

```bash
gcloud app create --region=us-central
```

## Deploy

### Automated (Recommended)

```bash
./deploy.sh
```

### Manual Steps

```bash
# 1. Download models
./startup.sh

# 2. Deploy backend
gcloud app deploy app.yaml --quiet

# 3. Get backend URL and update ui-app.yaml
export BACKEND_URL="https://$(gcloud config get-value project).uc.r.appspot.com"
sed -i.bak "s|API_URL:.*|API_URL: \"$BACKEND_URL\"|" ui-app.yaml

# 4. Deploy frontend
gcloud app deploy ui-app.yaml --quiet
```

## Access Your App

```bash
# Get URLs
export PROJECT_ID=$(gcloud config get-value project)
echo "Backend: https://$PROJECT_ID.uc.r.appspot.com"
echo "Frontend: https://ui-dot-$PROJECT_ID.uc.r.appspot.com"

# Open in browser
gcloud app browse -s ui
```

## View Logs

```bash
# Real-time logs
gcloud app logs tail

# Service-specific logs
gcloud app logs tail -s default  # Backend
gcloud app logs tail -s ui       # Frontend
```

## Update Deployment

```bash
# Update backend
gcloud app deploy app.yaml

# Update frontend
gcloud app deploy ui-app.yaml

# Update both
gcloud app deploy app.yaml ui-app.yaml
```

## Troubleshooting

```bash
# Check service status
gcloud app describe

# List versions
gcloud app versions list

# View specific version logs
gcloud app logs read --version=VERSION_ID

# SSH into instance (for debugging)
gcloud app instances ssh INSTANCE_ID --service=default
```

## Common Issues

### "API not enabled"
```bash
gcloud services enable appengine.googleapis.com
```

### "Billing not enabled"
Enable billing in Cloud Console: https://console.cloud.google.com/billing

### "Region already set"
If App Engine is already initialized, skip the `gcloud app create` step.

### Deployment hangs
Check Cloud Build logs: https://console.cloud.google.com/cloud-build/builds

## Cost Management

```bash
# Stop a version (but doesn't stop billing completely)
gcloud app versions stop VERSION_ID

# Check current serving version
gcloud app versions list --filter="SERVING_STATUS=SERVING"
```

## Complete Cleanup

To completely remove App Engine (not reversible):
1. Go to https://console.cloud.google.com/appengine/settings
2. Disable application
3. Note: Default service cannot be deleted

For full documentation, see [DEPLOYMENT.md](DEPLOYMENT.md)
