# 🛠️ Local Development Guide

## Overview

This setup runs the **backend in your local Python venv** while **supporting services run in Docker**.

### Architecture:

- ✅ **Backend (FastAPI)**: Local venv with hot reload
- ✅ **Redis**: Docker container (port 6379)
- ✅ **Neo4j**: AuraDB Cloud (or local Docker - commented out)
- ✅ **Qdrant**: Qdrant Cloud
- ✅ **Gemini API**: Google Cloud

---

## 🚀 Quick Start

### 1. Initial Setup (First Time Only)

```bash
./setup-local.sh
```

This will:

- Create/copy `.env` file
- Start Docker services (Redis)
- Create Python virtual environment
- Install all dependencies
- Download spaCy models

### 2. Start Backend

```bash
./run-local.sh
```

This will:

- Start Docker services if not running
- Activate virtual environment
- Start FastAPI with hot reload on `http://localhost:8000`

### 3. Stop Everything

```bash
./stop-local.sh
```

Or just `Ctrl+C` the backend and run:

```bash
docker compose -f docker-compose.services.yml down
```

---

## 📝 Manual Commands

### Start Docker Services Only

```bash
docker compose -f docker-compose.services.yml up -d
```

### Check Docker Services Status

```bash
docker compose -f docker-compose.services.yml ps
```

### View Docker Logs

```bash
docker compose -f docker-compose.services.yml logs -f redis
```

### Start Backend Manually

```bash
# Activate venv
source venv/bin/activate

# Run uvicorn
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🔧 Environment Configuration

Edit `.env` file with your credentials:

```bash
# Neo4j (AuraDB or local)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# Qdrant Cloud
QDRANT_URL=https://xxxxx.cloud.qdrant.io:6333
QDRANT_API_KEY=your-api-key

# Google Gemini
GEMINI_API_KEY=your-gemini-key

# Redis (automatically set for Docker)
REDIS_URL=redis://localhost:6379/0
```

---

## 🐛 Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
docker ps | grep redis

# Test Redis connection
docker exec hybrid-rag-redis redis-cli ping
# Should return: PONG

# View Redis logs
docker logs hybrid-rag-redis
```

### Neo4j Connection Issues

```bash
# Test Neo4j connection with Python
source venv/bin/activate
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('YOUR_URI', auth=('neo4j', 'YOUR_PASSWORD')); driver.verify_connectivity(); print('✅ Neo4j connected')"
```

### Qdrant Connection Issues

```bash
# Test Qdrant connection
source venv/bin/activate
python -c "from qdrant_client import QdrantClient; client = QdrantClient(url='YOUR_URL', api_key='YOUR_KEY'); print('✅ Qdrant connected')"
```

### Port Already in Use

If port 8000 is already in use:

```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use a different port
python -m uvicorn backend.main:app --reload --port 8001
```

### Virtual Environment Issues

```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🧪 Testing

### Run All Tests

```bash
source venv/bin/activate
pytest
```

### Run Specific Test Suite

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health | jq

# Ingest a document
curl -X POST http://localhost:8000/ingest \
  -F "file=@test_document.pdf" \
  -F "language=en"

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 5,
    "retrieval_methods": ["bm25", "dense", "graph"]
  }' | jq
```

---

## 📊 Monitoring

### View Backend Logs

The backend logs to both console and `logs/` directory:

```bash
# Watch logs in real-time
tail -f logs/app.log
```

### Check Resource Usage

```bash
# Docker containers
docker stats hybrid-rag-redis

# Python process
ps aux | grep uvicorn
```

---

## 🔄 Development Workflow

### 1. Make Code Changes

Edit files in `backend/` directory. Uvicorn will auto-reload on file changes.

### 2. Test Changes

```bash
# Quick test
curl http://localhost:8000/health

# Run unit tests
pytest tests/unit/test_bm25_retriever.py -v
```

### 3. Commit Changes

```bash
git add backend/
git commit -m "feat: add new retrieval feature"
```

---

## 🚀 Production Deployment

When ready for production, use the full Docker setup:

```bash
# Build and run everything in Docker
docker compose up -d

# Or deploy to Kubernetes
kubectl apply -f k8s/
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Design Document**: `DESIGN_DOCUMENT.md`
- **Requirements Compliance**: `REQUIREMENTS_COMPLIANCE_REPORT.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **README**: `README.md`

---

## 🆘 Need Help?

1. Check the logs: `logs/app.log`
2. Verify services: `docker compose -f docker-compose.services.yml ps`
3. Test connections: Health check endpoint
4. Review documentation: `docs/` directory
