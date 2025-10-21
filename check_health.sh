#!/bin/bash

# Check health of all services

echo "🏥 Checking Hybrid RAG System Health..."
echo ""

# Check Backend
echo "🐍 Backend (http://127.0.0.1:8000):"
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    STATUS=$(curl -s http://127.0.0.1:8000/health | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
    if [ "$STATUS" == "healthy" ]; then
        echo "   ✅ Status: HEALTHY"
    else
        echo "   ⚠️  Status: $STATUS"
    fi
else
    echo "   ❌ NOT RESPONDING"
fi

# Check Frontend
echo ""
echo "⚛️  Frontend (http://localhost:3000):"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Status: RUNNING"
else
    echo "   ❌ NOT RESPONDING"
fi

# Check Redis
echo ""
echo "🐳 Redis (localhost:6379):"
if redis-cli -h localhost -p 6379 ping 2>/dev/null | grep -q "PONG"; then
    echo "   ✅ Status: RUNNING"
else
    echo "   ❌ NOT RUNNING"
fi

# Check for running processes
echo ""
echo "📊 Process Status:"
BACKEND_PROCS=$(ps aux | grep -c "[u]vicorn backend.main:app")
FRONTEND_PROCS=$(ps aux | grep -c "[v]ite")
echo "   Backend processes:  $BACKEND_PROCS"
echo "   Frontend processes: $FRONTEND_PROCS"

if [ $FRONTEND_PROCS -gt 1 ]; then
    echo "   ⚠️  WARNING: Multiple frontend processes detected!"
    echo "   Run './stop_dev.sh' to clean up"
fi

# Check ports
echo ""
echo "🔌 Port Status:"
for port in 8000 3000 6379; do
    if lsof -ti:$port > /dev/null 2>&1; then
        PID=$(lsof -ti:$port | head -1)
        echo "   Port $port: ✅ In use (PID: $PID)"
    else
        echo "   Port $port: ⚪ Free"
    fi
done

echo ""
