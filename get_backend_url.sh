#!/bin/bash

# Script to find your Cloud Run backend URL

echo "🔍 Finding your Cloud Run backend URL..."
echo ""

PROJECT_ID="animated-surfer-476413-c1"
REGION="us-central1"  # Change if your region is different

echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" > /dev/null 2>&1; then
    echo "❌ Not authenticated with gcloud"
    echo "Run: gcloud auth login"
    exit 1
fi

echo "📋 Listing Cloud Run services:"
echo ""

# List all services in the region
gcloud run services list \
    --project=$PROJECT_ID \
    --region=$REGION \
    --format="table(metadata.name,status.url,metadata.labels)" \
    2>/dev/null

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Try to find backend service specifically
BACKEND_URL=$(gcloud run services list \
    --project=$PROJECT_ID \
    --region=$REGION \
    --format="value(status.url)" \
    --filter="metadata.name~backend" \
    2>/dev/null | head -1)

if [ ! -z "$BACKEND_URL" ]; then
    echo "✅ Found backend service URL:"
    echo ""
    echo "   $BACKEND_URL"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 Add this to Streamlit Cloud Secrets:"
    echo ""
    echo "   API_URL = \"$BACKEND_URL\""
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🧪 Test the backend:"
    echo ""
    echo "   curl $BACKEND_URL/health"
    echo ""

    # Test if backend is accessible
    if curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
        echo "✅ Backend is accessible!"
    else
        echo "⚠️  Backend might not be accessible or not deployed yet"
    fi
else
    echo "⚠️  No backend service found with 'backend' in the name"
    echo ""
    echo "All services listed above. Look for your backend service."
    echo "Then use that URL in your Streamlit secrets."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 For detailed setup instructions, see: STREAMLIT_CLOUD_SETUP.md"
