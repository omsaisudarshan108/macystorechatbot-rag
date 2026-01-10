#!/bin/bash

# Script to run the RAG platform locally

echo "🚀 Starting Retail Knowledge RAG Platform locally..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo "⬇️  Downloading required models..."
    bash startup.sh
else
    source .venv/bin/activate
fi

# Set environment variables for local development
export PROJECT_ID="animated-surfer-476413-c1"
export PORT=8000

echo "✅ Virtual environment activated"
echo "✅ PROJECT_ID set to: $PROJECT_ID"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend
echo "🔧 Starting FastAPI backend on http://127.0.0.1:8000..."
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "❌ Backend failed to start. Check backend.log for errors."
    exit 1
fi

echo "✅ Backend running (PID: $BACKEND_PID)"
echo "   API Docs: http://127.0.0.1:8000/docs"
echo ""

# Start frontend
echo "🎨 Starting Streamlit frontend on http://localhost:8501..."
streamlit run ui/app.py > streamlit.log 2>&1 &
FRONTEND_PID=$!

sleep 2

echo "✅ Frontend running (PID: $FRONTEND_PID)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Services are running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Frontend UI:     http://localhost:8501"
echo "🔌 Backend API:     http://127.0.0.1:8000"
echo "📚 API Docs:        http://127.0.0.1:8000/docs"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f streamlit.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Keep script running and wait for user interrupt
wait
