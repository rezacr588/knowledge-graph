#!/bin/bash

# Stop all development services

set -e

echo "🛑 Stopping Hybrid RAG System..."
echo ""

# Stop Backend (force kill if necessary)
echo "🐍 Stopping Backend..."
pkill -9 -f "uvicorn backend.main:app" 2>/dev/null && echo "   ✅ Backend stopped" || echo "   ℹ️  Backend not running"
sleep 1

# Stop Frontend (force kill if necessary)
echo "⚛️  Stopping Frontend..."
pkill -9 -f "vite" 2>/dev/null && echo "   ✅ Frontend stopped" || echo "   ℹ️  Frontend not running"
sleep 1

# Clear any processes on ports 3000, 5173, 8000
echo "🧹 Clearing ports..."
for port in 3000 5173 8000; do
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "   Killing process on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

# Stop Redis container
echo "🐳 Stopping Redis container..."
docker-compose -f docker-compose.dev.yml down

echo ""
echo "✅ All services stopped and ports cleared"
