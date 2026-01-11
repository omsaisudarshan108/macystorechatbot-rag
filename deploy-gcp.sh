#!/bin/bash

# Deploy to Google Cloud Run - Portable for Any GCP Project
# Usage: ./deploy-gcp.sh <PROJECT_ID> <REGION>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
BACKEND_SERVICE="rag-backend"
FRONTEND_SERVICE="rag-frontend"

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if PROJECT_ID is provided
if [ -z "$PROJECT_ID" ]; then
    print_message "$RED" "Error: PROJECT_ID is required"
    echo "Usage: ./deploy-gcp.sh <PROJECT_ID> [REGION]"
    echo "Example: ./deploy-gcp.sh my-project-123 us-central1"
    exit 1
fi

print_message "$BLUE" "=========================================="
print_message "$BLUE" "  GCP Cloud Run Deployment"
print_message "$BLUE" "=========================================="
echo ""
print_message "$GREEN" "Project ID: $PROJECT_ID"
print_message "$GREEN" "Region: $REGION"
echo ""

# Confirm deployment
read -p "Deploy to GCP? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    print_message "$YELLOW" "Deployment cancelled"
    exit 0
fi

# Step 1: Set GCP project
print_message "$BLUE" "Step 1: Setting GCP project..."
gcloud config set project "$PROJECT_ID"

# Step 2: Enable required APIs
print_message "$BLUE" "Step 2: Enabling required GCP APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    secretmanager.googleapis.com \
    --project="$PROJECT_ID"

# Step 3: Create Artifact Registry repository (if doesn't exist)
print_message "$BLUE" "Step 3: Setting up Artifact Registry..."
gcloud artifacts repositories create rag-app \
    --repository-format=docker \
    --location="$REGION" \
    --description="RAG application container images" \
    --project="$PROJECT_ID" 2>/dev/null || print_message "$YELLOW" "Repository already exists, skipping..."

# Step 4: Build and push backend image
print_message "$BLUE" "Step 4: Building backend image..."
gcloud builds submit \
    --tag "$REGION-docker.pkg.dev/$PROJECT_ID/rag-app/$BACKEND_SERVICE:latest" \
    --file Dockerfile.backend \
    --project="$PROJECT_ID" \
    .

# Step 5: Deploy backend to Cloud Run
print_message "$BLUE" "Step 5: Deploying backend to Cloud Run..."
gcloud run deploy "$BACKEND_SERVICE" \
    --image "$REGION-docker.pkg.dev/$PROJECT_ID/rag-app/$BACKEND_SERVICE:latest" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --project="$PROJECT_ID"

# Get backend URL
BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" \
    --platform managed \
    --region "$REGION" \
    --format 'value(status.url)' \
    --project="$PROJECT_ID")

print_message "$GREEN" "Backend deployed at: $BACKEND_URL"

# Step 6: Build and push frontend image
print_message "$BLUE" "Step 6: Building frontend image..."
gcloud builds submit \
    --tag "$REGION-docker.pkg.dev/$PROJECT_ID/rag-app/$FRONTEND_SERVICE:latest" \
    --file Dockerfile.frontend \
    --project="$PROJECT_ID" \
    .

# Step 7: Deploy frontend to Cloud Run
print_message "$BLUE" "Step 7: Deploying frontend to Cloud Run..."
gcloud run deploy "$FRONTEND_SERVICE" \
    --image "$REGION-docker.pkg.dev/$PROJECT_ID/rag-app/$FRONTEND_SERVICE:latest" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "API_URL=$BACKEND_URL" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --project="$PROJECT_ID"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" \
    --platform managed \
    --region "$REGION" \
    --format 'value(status.url)' \
    --project="$PROJECT_ID")

print_message "$GREEN" "Frontend deployed at: $FRONTEND_URL"

# Step 8: Display summary
echo ""
print_message "$BLUE" "=========================================="
print_message "$BLUE" "  Deployment Complete!"
print_message "$BLUE" "=========================================="
echo ""
print_message "$GREEN" "Backend API:  $BACKEND_URL"
print_message "$GREEN" "Frontend UI:  $FRONTEND_URL"
echo ""
print_message "$YELLOW" "Next steps:"
echo "1. Visit the frontend URL to access the application"
echo "2. Configure Vertex AI permissions if needed:"
echo "   gcloud projects add-iam-policy-binding $PROJECT_ID \\"
echo "     --member='serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com' \\"
echo "     --role='roles/aiplatform.user'"
echo ""
print_message "$BLUE" "=========================================="
