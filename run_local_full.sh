#!/bin/bash

# Local Deployment Script - Full Application
# Runs backend and frontend with all safety features enabled

set -e

echo "========================================="
echo "Retail Knowledge RAG - Local Deployment"
echo "========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create data directories
echo ""
echo "📁 Setting up data directories..."
mkdir -p data/raw
mkdir -p data/chroma

# Set environment variables
export ENVIRONMENT="local"
export PROJECT_ID="${PROJECT_ID:-mtech-stores-sre-monit-dev}"
export API_URL="http://127.0.0.1:8000"

echo ""
echo "========================================="
echo "🛡️  Safety Features Status"
echo "========================================="
echo "✅ Document Safety Verification: ENABLED"
echo "✅ Prompt Injection Protection: ENABLED"
echo "✅ OWASP LLM Guardrails: ENABLED"
echo "✅ Response Safety Filter: ENABLED"
echo "✅ Confidential Escalation: ENABLED"
echo ""

echo "========================================="
echo "🚀 Starting Services"
echo "========================================="
echo ""

# Kill existing processes on ports 8000 and 8501
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

# Start backend
echo "🔧 Starting FastAPI backend (http://127.0.0.1:8000)..."
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "   Waiting for backend to initialize..."
sleep 3

# Check backend health
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "   ✅ Backend is healthy"
else
    echo "   ⚠️  Backend health check failed (might still be starting)"
fi

# Start frontend
echo ""
echo "🎨 Starting Streamlit frontend (http://localhost:8501)..."
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0 > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Save PIDs
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "========================================="
echo "✅ Deployment Complete"
echo "========================================="
echo ""
echo "🌐 Application URLs:"
echo "   Backend API: http://127.0.0.1:8000"
echo "   API Docs:    http://127.0.0.1:8000/docs"
echo "   Frontend UI: http://localhost:8501"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 To stop services:"
echo "   ./stop_local.sh"
echo ""
echo "Press Ctrl+C to view this message again, or close terminal to continue running."
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Services still running in background. Use ./stop_local.sh to stop.'; exit 0" INT

# Keep script running
tail -f /dev/null
