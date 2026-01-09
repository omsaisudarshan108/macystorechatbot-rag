#!/bin/bash
# Quick Reference: All Deployment Commands
# Copy and paste commands as needed

# =============================================================================
# INITIAL SETUP (One-time)
# =============================================================================

# Check prerequisites
gcloud --version
gcloud auth list

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Verify project
gcloud config get-value project

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com

# Initialize App Engine (first time only)
gcloud app create --region=us-central

# =============================================================================
# DEPLOYMENT
# =============================================================================

# Option 1: Automated deployment (recommended)
./deploy.sh

# Option 2: Manual deployment
./startup.sh
gcloud app deploy app.yaml --quiet
export BACKEND_URL="https://$(gcloud config get-value project).uc.r.appspot.com"
sed -i.bak "s|API_URL:.*|API_URL: \"$BACKEND_URL\"|" ui-app.yaml
gcloud app deploy ui-app.yaml --quiet

# =============================================================================
# VERIFICATION
# =============================================================================

# Check deployment status
gcloud app versions list
gcloud app services list

# Get URLs
export PROJECT_ID=$(gcloud config get-value project)
echo "Backend: https://$PROJECT_ID.uc.r.appspot.com"
echo "Frontend: https://ui-dot-$PROJECT_ID.uc.r.appspot.com"

# Test backend health
curl https://$PROJECT_ID.uc.r.appspot.com/health

# Open frontend in browser
gcloud app browse -s ui

# =============================================================================
# MONITORING
# =============================================================================

# View real-time logs
gcloud app logs tail

# View backend logs
gcloud app logs tail -s default

# View frontend logs
gcloud app logs tail -s ui

# View specific version logs
gcloud app logs read --version=VERSION_ID

# View logs in browser
echo "https://console.cloud.google.com/logs/query;query=resource.type%3D%22gae_app%22"

# =============================================================================
# UPDATING
# =============================================================================

# Update backend only
gcloud app deploy app.yaml

# Update frontend only
gcloud app deploy ui-app.yaml

# Update both services
gcloud app deploy app.yaml ui-app.yaml

# =============================================================================
# ROLLBACK
# =============================================================================

# List all versions
gcloud app versions list

# Route traffic to specific version
gcloud app services set-traffic default --splits VERSION_ID=1
gcloud app services set-traffic ui --splits VERSION_ID=1

# Stop a specific version
gcloud app versions stop VERSION_ID

# Delete old versions
gcloud app versions delete VERSION_ID

# =============================================================================
# DEBUGGING
# =============================================================================

# Describe the app
gcloud app describe

# Get instance details
gcloud app instances list

# SSH into instance
gcloud app instances ssh INSTANCE_ID --service=default

# View build logs
gcloud builds list
gcloud builds log BUILD_ID

# =============================================================================
# COST MANAGEMENT
# =============================================================================

# View current quota usage
gcloud app instances list --format="table(service,version,id,vmStatus)"

# Set up billing budget alert (via console)
echo "https://console.cloud.google.com/billing/budgets"

# View current costs
echo "https://console.cloud.google.com/billing"

# =============================================================================
# CLEANUP
# =============================================================================

# Stop serving traffic (billing continues for default service)
gcloud app versions stop VERSION_ID

# Delete non-default services
gcloud app services delete ui

# Delete old versions
gcloud app versions delete VERSION_ID --service=default
gcloud app versions delete VERSION_ID --service=ui

# Note: Cannot delete App Engine completely once created
# Must disable in console: https://console.cloud.google.com/appengine/settings

# =============================================================================
# USEFUL QUERIES
# =============================================================================

# Count requests in last hour
gcloud logging read "resource.type=gae_app AND timestamp>=\"$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%SZ')\"" --limit 1000 --format="value(timestamp)" | wc -l

# Check for errors in last hour
gcloud logging read "resource.type=gae_app AND severity>=ERROR AND timestamp>=\"$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%SZ')\"" --limit 50

# Get average response time
gcloud logging read "resource.type=gae_app AND httpRequest.latency!=\"\"" --limit 1000 --format="value(httpRequest.latency)"

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

# These are set in app.yaml and ui-app.yaml
# Backend (app.yaml):
#   PROJECT_ID: "your-project-id"
#   PYTHONUNBUFFERED: "1"
#
# Frontend (ui-app.yaml):
#   API_URL: "https://your-project-id.uc.r.appspot.com"
#   PYTHONUNBUFFERED: "1"

# =============================================================================
# TESTING ENDPOINTS
# =============================================================================

export PROJECT_ID=$(gcloud config get-value project)
export BACKEND_URL="https://$PROJECT_ID.uc.r.appspot.com"
export UI_URL="https://ui-dot-$PROJECT_ID.uc.r.appspot.com"

# Test health endpoint
curl $BACKEND_URL/health

# Test root endpoint
curl $BACKEND_URL/

# Test API docs (should return HTML)
curl $BACKEND_URL/docs

# Test frontend (should return HTML)
curl $UI_URL

# Test file upload (example)
curl -X POST "$BACKEND_URL/ingest" \
  -F "file=@test.pdf" \
  -F "store_id=NY_001"

# Test query (example)
curl -X POST "$BACKEND_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the store hours?", "store_id": "NY_001"}'

# =============================================================================
# SECURITY
# =============================================================================

# Enable Identity-Aware Proxy (IAP)
gcloud iap web enable --resource-type=app-engine

# Add IAP user
gcloud iap web add-iam-policy-binding \
  --member='user:email@example.com' \
  --role='roles/iap.httpsResourceAccessor'

# View IAP settings
echo "https://console.cloud.google.com/security/iap"

# =============================================================================
# CUSTOM DOMAIN
# =============================================================================

# Add custom domain
gcloud app domain-mappings create DOMAIN

# List custom domains
gcloud app domain-mappings list

# =============================================================================
# PERFORMANCE
# =============================================================================

# View performance metrics
echo "https://console.cloud.google.com/appengine/metrics"

# Set up uptime check
echo "https://console.cloud.google.com/monitoring/uptime"

# =============================================================================
# MORE INFO
# =============================================================================

# See documentation
cat DEPLOYMENT.md
cat QUICKSTART.md
cat DEPLOYMENT_CHECKLIST.md

# Get help
gcloud app --help
gcloud app deploy --help
