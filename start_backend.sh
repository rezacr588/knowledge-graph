#!/bin/bash

# Start backend only in virtual environment

set -e

echo "🐍 Starting Backend Server..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup_venv.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Start backend
echo "🚀 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
python -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0
