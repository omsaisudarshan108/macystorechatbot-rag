#!/bin/bash

# Script to run only the Streamlit frontend

echo "🎨 Starting Streamlit Frontend..."

# Activate virtual environment
source .venv/bin/activate

# Set environment variable for API URL (when running locally)
export API_URL="http://127.0.0.1:8000"

echo "✅ Virtual environment activated"
echo "✅ API_URL set to: $API_URL"
echo ""
echo "🚀 Starting frontend on http://localhost:8501..."
echo ""

# Run streamlit
streamlit run ui/app.py
