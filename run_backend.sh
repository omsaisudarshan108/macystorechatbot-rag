#!/bin/bash

# Script to run only the FastAPI backend

echo "🔧 Starting FastAPI Backend..."

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export PROJECT_ID="animated-surfer-476413-c1"
export PORT=8000

echo "✅ Virtual environment activated"
echo "✅ PROJECT_ID set to: $PROJECT_ID"
echo ""
echo "🚀 Starting backend on http://127.0.0.1:8000..."
echo "📚 API Documentation: http://127.0.0.1:8000/docs"
echo ""

# Run uvicorn
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
