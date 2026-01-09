#!/bin/bash
set -e

echo "=========================================="
echo "Deploying RAG Platform to App Engine"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project selected${NC}"
    echo "Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}Using project: $PROJECT_ID${NC}"

# Step 1: Run startup script to download models
echo ""
echo "Step 1: Downloading required models..."
bash startup.sh

# Step 2: Deploy backend API service
echo ""
echo "Step 2: Deploying backend API service (default)..."
echo -e "${YELLOW}This may take 5-10 minutes...${NC}"
gcloud app deploy app.yaml --quiet

# Get the backend URL
BACKEND_URL="https://${PROJECT_ID}.uc.r.appspot.com"
echo -e "${GREEN}Backend deployed to: $BACKEND_URL${NC}"

# Step 3: Update UI config with backend URL
echo ""
echo "Step 3: Updating UI configuration..."
sed -i.bak "s|API_URL:.*|API_URL: \"$BACKEND_URL\"|" ui-app.yaml
rm -f ui-app.yaml.bak

# Step 4: Deploy UI service
echo ""
echo "Step 4: Deploying UI service..."
echo -e "${YELLOW}This may take 5-10 minutes...${NC}"
gcloud app deploy ui-app.yaml --quiet

# Get the UI URL
UI_URL="https://ui-dot-${PROJECT_ID}.uc.r.appspot.com"

echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Backend API: $BACKEND_URL"
echo "API Docs:    $BACKEND_URL/docs"
echo "Frontend UI: $UI_URL"
echo ""
echo "You can view logs with:"
echo "  gcloud app logs tail -s default  # Backend logs"
echo "  gcloud app logs tail -s ui       # Frontend logs"
echo ""
