#!/bin/bash

# Development startup script - starts all services with cleanup

set -e

echo "🚀 Starting Hybrid RAG System in Development Mode"
echo ""

# Clean up any existing processes first
echo "🧹 Cleaning up any existing processes..."
pkill -9 -f "uvicorn backend.main:app" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true

# Clear ports
for port in 3000 5173 8000; do
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "   Clearing port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done
sleep 2

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Running setup..."
    bash setup_venv.sh
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not found. Installing..."
    cd frontend && npm install && cd ..
fi

# Start Redis in Docker
echo "🐳 Starting Redis container..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
for i in {1..10}; do
    if docker ps | grep -q "hybrid-rag-redis"; then
        sleep 2
        if redis-cli -h localhost -p 6379 ping 2>/dev/null | grep -q "PONG"; then
            echo "✅ Redis is running"
            break
        fi
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Failed to start Redis"
        exit 1
    fi
    sleep 1
done

# Start Backend in background
echo ""
echo "🐍 Starting Backend (in venv)..."
source venv/bin/activate
nohup python -m uvicorn backend.main:app --reload --port 8000 --host 127.0.0.1 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in {1..20}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "❌ Backend failed to start. Check logs/backend.log"
        exit 1
    fi
    sleep 1
done

# Start Frontend
echo ""
echo "⚛️  Starting Frontend..."
cd frontend
nohup npm run dev -- --port 3000 --host 0.0.0.0 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
sleep 5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All services started successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Service URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://127.0.0.1:8000"
echo "   API Docs:  http://127.0.0.1:8000/docs"
echo "   Redis:     localhost:6379"
echo ""
echo "📊 Process IDs:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "🛑 To stop all services, run:"
echo "   ./stop_dev.sh"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
