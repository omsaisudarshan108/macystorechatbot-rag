#!/bin/bash

# GCP Project Setup Script - Initialize IAM and Permissions
# Usage: ./setup-gcp-project.sh <PROJECT_ID>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ID="${1:-}"

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if PROJECT_ID is provided
if [ -z "$PROJECT_ID" ]; then
    print_message "$RED" "Error: PROJECT_ID is required"
    echo "Usage: ./setup-gcp-project.sh <PROJECT_ID>"
    echo "Example: ./setup-gcp-project.sh my-rag-project-123"
    exit 1
fi

print_message "$BLUE" "=========================================="
print_message "$BLUE" "  GCP Project Setup"
print_message "$BLUE" "=========================================="
echo ""
print_message "$GREEN" "Project ID: $PROJECT_ID"
echo ""

# Step 1: Set project
print_message "$BLUE" "Step 1: Setting GCP project..."
gcloud config set project "$PROJECT_ID"

# Get project number
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
print_message "$GREEN" "Project Number: $PROJECT_NUMBER"

# Step 2: Enable APIs
print_message "$BLUE" "Step 2: Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    secretmanager.googleapis.com \
    compute.googleapis.com \
    storage.googleapis.com \
    --project="$PROJECT_ID"

print_message "$GREEN" "APIs enabled successfully"

# Step 3: Set up IAM permissions for Cloud Run service account
print_message "$BLUE" "Step 3: Configuring IAM permissions..."

# Default compute service account
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant Vertex AI permissions
print_message "$YELLOW" "Granting Vertex AI User role..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/aiplatform.user" \
    --condition=None

# Grant Secret Manager access
print_message "$YELLOW" "Granting Secret Manager Accessor role..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

# Grant Storage permissions (for document storage)
print_message "$YELLOW" "Granting Storage Object Admin role..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/storage.objectAdmin" \
    --condition=None

print_message "$GREEN" "IAM permissions configured"

# Step 4: Create encryption key secret (optional)
print_message "$BLUE" "Step 4: Setting up encryption key..."
read -p "Create a new encryption key secret? (yes/no): " create_secret

if [ "$create_secret" = "yes" ]; then
    # Generate random encryption key
    ENCRYPTION_KEY=$(openssl rand -hex 32)

    # Create secret
    echo -n "$ENCRYPTION_KEY" | gcloud secrets create safety-encryption-key \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$PROJECT_ID" 2>/dev/null || print_message "$YELLOW" "Secret already exists, skipping..."

    print_message "$GREEN" "Encryption key created: safety-encryption-key"
else
    print_message "$YELLOW" "Skipping encryption key creation"
fi

# Step 5: Create storage bucket for documents (optional)
print_message "$BLUE" "Step 5: Setting up Cloud Storage..."
BUCKET_NAME="${PROJECT_ID}-rag-documents"

gsutil mb -p "$PROJECT_ID" -l us-central1 "gs://$BUCKET_NAME/" 2>/dev/null || print_message "$YELLOW" "Bucket already exists"
gsutil versioning set on "gs://$BUCKET_NAME/" 2>/dev/null || true

print_message "$GREEN" "Storage bucket ready: gs://$BUCKET_NAME/"

# Step 6: Summary
echo ""
print_message "$BLUE" "=========================================="
print_message "$BLUE" "  Setup Complete!"
print_message "$BLUE" "=========================================="
echo ""
print_message "$GREEN" "Project Configuration:"
echo "  Project ID:     $PROJECT_ID"
echo "  Project Number: $PROJECT_NUMBER"
echo "  Service Account: $COMPUTE_SA"
echo "  Storage Bucket: gs://$BUCKET_NAME/"
echo ""
print_message "$GREEN" "Enabled APIs:"
echo "  ✓ Cloud Build"
echo "  ✓ Cloud Run"
echo "  ✓ Artifact Registry"
echo "  ✓ Vertex AI"
echo "  ✓ Secret Manager"
echo "  ✓ Cloud Storage"
echo ""
print_message "$GREEN" "IAM Roles Granted:"
echo "  ✓ roles/aiplatform.user"
echo "  ✓ roles/secretmanager.secretAccessor"
echo "  ✓ roles/storage.objectAdmin"
echo ""
print_message "$YELLOW" "Next Steps:"
echo "1. Deploy the application:"
echo "   ./deploy-gcp.sh $PROJECT_ID us-central1"
echo ""
echo "2. (Optional) Configure custom domain in Cloud Run console"
echo ""
echo "3. (Optional) Set up monitoring and alerting"
echo ""
print_message "$BLUE" "=========================================="
