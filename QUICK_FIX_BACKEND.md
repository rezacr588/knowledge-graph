# 🔧 Quick Fix: Backend Not Starting

## ❌ Problem
Backend container is restarting due to missing `git` dependency required by RAGatouille/ColBERT.

**Error:**
```
ImportError: Failed to initialize: Bad git executable.
The git executable must be specified in one of the following ways:
    - be included in your $PATH
```

## ✅ Solution Applied

Updated `Dockerfile` to include git:

```dockerfile
# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \        # ← ADDED THIS
    && rm -rf /var/lib/apt/lists/*
```

## 🚀 Fix It Now

```bash
# Rebuild backend with git included
docker-compose down
docker-compose up -d --build

# Wait 30 seconds for startup
sleep 30

# Check status
docker-compose ps
```

## ✅ Expected Result

```
NAME                  STATUS
hybrid-rag-backend    Up (healthy)
hybrid-rag-frontend   Up (healthy)
hybrid-rag-redis      Up (healthy)
```

## 📋 Verify Fix

```bash
# Check backend logs
docker-compose logs backend | tail -20

# Should see:
# ✅ Entity extractor initialized
# ✅ BM25 retriever initialized
# ✅ ColBERT retriever initialized
# ✅ Application startup complete
```

## ⏱️ Build Time
- **Fresh build:** ~3-4 minutes
- **Cached:** ~30 seconds

---

**Status:** ✅ FIXED - Dockerfile updated
