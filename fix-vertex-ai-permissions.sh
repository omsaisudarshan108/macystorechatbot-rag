#!/bin/bash
# Script to fix Vertex AI permissions

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
ACCOUNT=$(gcloud config get-value account 2>/dev/null)

echo "=========================================="
echo "Vertex AI Permission Fix Script"
echo "=========================================="
echo ""
echo "Project: $PROJECT_ID"
echo "Account: $ACCOUNT"
echo ""

# Check if user has necessary permissions
echo "Checking current permissions..."
echo ""

# Option 1: Grant Vertex AI User role (recommended for users)
echo "To use Vertex AI, you need one of these roles:"
echo "  1. Vertex AI User (roles/aiplatform.user)"
echo "  2. Vertex AI Admin (roles/aiplatform.admin)"
echo "  3. Project Owner (roles/owner)"
echo ""

# Try to grant the role (requires admin access)
echo "Attempting to grant Vertex AI User role..."
echo ""

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$ACCOUNT" \
  --role="roles/aiplatform.user" \
  --condition=None 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Successfully granted Vertex AI User role!"
    echo ""
    echo "Please wait a few seconds for permissions to propagate, then try again."
else
    echo ""
    echo "✗ Could not grant role automatically."
    echo ""
    echo "You need to either:"
    echo "  1. Have a project admin grant you the 'Vertex AI User' role"
    echo "  2. Use a service account with proper permissions"
    echo "  3. Use a different project where you have permissions"
    echo ""
    echo "To grant the role manually (requires project admin):"
    echo "  gcloud projects add-iam-policy-binding $PROJECT_ID \\"
    echo "    --member=\"user:$ACCOUNT\" \\"
    echo "    --role=\"roles/aiplatform.user\""
    echo ""
    echo "Or via Cloud Console:"
    echo "  1. Go to: https://console.cloud.google.com/iam-admin/iam?project=$PROJECT_ID"
    echo "  2. Find your account: $ACCOUNT"
    echo "  3. Click Edit (pencil icon)"
    echo "  4. Add role: 'Vertex AI User'"
    echo "  5. Click Save"
fi

echo ""
echo "=========================================="
