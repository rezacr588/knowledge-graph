# 🐳 FULL-STACK DOCKER COMPOSE GUIDE

**Status:** ✅ UPDATED - Backend + Frontend + Redis

---

## 🎯 WHAT'S INCLUDED

The `docker-compose.yml` now includes:

1. ✅ **Backend** - FastAPI application (port 8000)
2. ✅ **Frontend** - React UI (port 3000) ⭐ NEW
3. ✅ **Redis** - Cache and message broker (port 6379)

**All services run together with a single command!**

---

## 🚀 QUICK START

### Step 1: Configure Environment

```bash
cd /Users/rezazeraat/Desktop/KnowledgeGraph

# Create .env if you haven't already
cp .env.example .env

# Edit with your credentials
nano .env
```

Add your credentials:
```env
NEO4J_URI=neo4j+s://YOUR_INSTANCE.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=YOUR_PASSWORD
QDRANT_URL=https://YOUR_CLUSTER.qdrant.io:6333
QDRANT_API_KEY=YOUR_API_KEY
GEMINI_API_KEY=YOUR_GEMINI_KEY
```

### Step 2: Start Everything

```bash
# Start all services (backend + frontend + redis)
docker-compose up -d
```

**That's it!** All services are now running.

### Step 3: Access the Application

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📦 SERVICES OVERVIEW

### Backend Service
```yaml
Service: backend
Port: 8000
Container: hybrid-rag-backend
Health Check: /health endpoint
```

**What it does:**
- BM25, ColBERT, Graph retrieval
- RRF fusion
- REST API endpoints

### Frontend Service ⭐ NEW
```yaml
Service: frontend
Port: 3000
Container: hybrid-rag-frontend
Health Check: HTTP 200 on port 3000
```

**What it does:**
- React UI with TailwindCSS
- Document upload interface
- Query search interface
- Results display

### Redis Service
```yaml
Service: redis
Port: 6379
Container: hybrid-rag-redis
Health Check: redis-cli ping
```

**What it does:**
- Caching layer
- Message broker for Celery

---

## 🔧 DOCKER COMPOSE COMMANDS

### Start Services
```bash
# Start in background (detached)
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d frontend
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop but keep volumes
docker-compose stop

# Stop specific service
docker-compose stop frontend
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 frontend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart frontend
```

### Rebuild Services
```bash
# Rebuild all
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build frontend
```

### Check Status
```bash
# View running services
docker-compose ps

# View detailed status
docker-compose ps -a
```

### Execute Commands Inside Containers
```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# Redis CLI
docker-compose exec redis redis-cli
```

---

## 📊 ARCHITECTURE

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
│         (hybrid-rag-network)            │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    Frontend (React)              │  │
│  │    Port: 3000                    │  │
│  │    http://localhost:3000         │  │
│  └──────────────┬───────────────────┘  │
│                 │ /api/* → backend:8000 │
│                 ▼                        │
│  ┌──────────────────────────────────┐  │
│  │    Backend (FastAPI)             │  │
│  │    Port: 8000                    │  │
│  │    http://localhost:8000         │  │
│  └──────────────┬───────────────────┘  │
│                 │                        │
│                 ▼                        │
│  ┌──────────────────────────────────┐  │
│  │    Redis                         │  │
│  │    Port: 6379                    │  │
│  └──────────────────────────────────┘  │
│                                         │
│  External Services (Cloud):             │
│  - Neo4j AuraDB                         │
│  - Qdrant Cloud                         │
│  - Google Gemini API                    │
└─────────────────────────────────────────┘
```

---

## 🔍 HOW IT WORKS

### 1. Frontend Proxy Setup

The frontend in Docker uses Vite's proxy to forward API calls to the backend:

**Frontend makes request:**
```javascript
axios.post('/api/query', {...})
```

**Vite proxy forwards to:**
```
http://backend:8000/query
```

**Docker internal networking** resolves `backend` to the backend container.

### 2. Service Communication

Services communicate using **Docker network names**:
- Frontend → Backend: `http://backend:8000`
- Backend → Redis: `redis://redis:6379`

### 3. Port Mapping

Docker maps container ports to host:
- `3000:3000` - Frontend accessible at localhost:3000
- `8000:8000` - Backend accessible at localhost:8000
- `6379:6379` - Redis accessible at localhost:6379

---

## ✅ VERIFICATION

### Check All Services Running

```bash
docker-compose ps
```

**Expected output:**
```
NAME                    STATUS    PORTS
hybrid-rag-backend      running   0.0.0.0:8000->8000/tcp
hybrid-rag-frontend     running   0.0.0.0:3000->3000/tcp
hybrid-rag-redis        running   0.0.0.0:6379->6379/tcp
```

### Check Health Status

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health (should return HTML)
curl http://localhost:3000

# Redis health
docker-compose exec redis redis-cli ping
```

### Test End-to-End

1. **Open browser:** http://localhost:3000
2. **Check health status:** Should show "Healthy" (green)
3. **Upload document:** Click Upload tab, select file
4. **Search:** Click Query tab, enter query
5. **Verify results:** Should display with scores

---

## 🐛 TROUBLESHOOTING

### Frontend Can't Connect to Backend

**Symptom:** Health shows "Unhealthy", API calls fail

**Check:**
```bash
# Check backend is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Test backend directly
curl http://localhost:8000/health
```

**Solution:**
```bash
# Restart backend
docker-compose restart backend

# Or rebuild
docker-compose up -d --build backend
```

---

### Frontend Shows Blank Page

**Check browser console:**
```
Open DevTools (F12) → Console tab
```

**Common issues:**
- Build errors in frontend
- Port 3000 conflict

**Solution:**
```bash
# View frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

---

### Port Already in Use

**Error:**
```
Error: port 3000 already allocated
```

**Solution:**
```bash
# Find process using port
lsof -ti:3000

# Kill it
lsof -ti:3000 | xargs kill

# Or change port in docker-compose.yml
ports:
  - "3001:3000"  # Use 3001 instead
```

---

### Services Keep Restarting

**Check logs:**
```bash
docker-compose logs -f SERVICE_NAME
```

**Common causes:**
- Missing environment variables
- Can't connect to external services (Neo4j, Qdrant)
- Health check failing

**Solution:**
```bash
# Check .env file exists and has values
cat .env

# Test external services
curl https://YOUR_QDRANT_URL/collections

# Restart with fresh build
docker-compose down
docker-compose up -d --build
```

---

## 🔧 DEVELOPMENT WORKFLOW

### Making Code Changes

**Backend changes:**
```bash
# Backend auto-reloads with volume mount
# Just edit files in backend/ directory
# Changes take effect immediately
```

**Frontend changes:**
```bash
# Frontend auto-reloads with HMR
# Edit files in frontend/src/
# Browser refreshes automatically
```

### Installing New Dependencies

**Backend:**
```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Rebuild backend
docker-compose up -d --build backend
```

**Frontend:**
```bash
# Add via npm (on host)
cd frontend
npm install new-package

# Rebuild frontend
cd ..
docker-compose up -d --build frontend
```

---

## 📈 PERFORMANCE TIPS

### Reduce Build Time

**Use build cache:**
```bash
# Docker will use cached layers
docker-compose build
```

**Multi-stage builds:**
Already optimized in Dockerfiles

### Reduce Image Size

**Frontend already uses:**
- `node:18-alpine` (smaller base image)
- `.dockerignore` to exclude unnecessary files

**Backend already uses:**
- `python:3.11-slim` (smaller base image)
- `--no-cache-dir` pip flag

---

## 🚀 PRODUCTION DEPLOYMENT

### Build for Production

**Create production docker-compose:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: .
    environment:
      - DEBUG=False
      - LOG_LEVEL=WARNING
    # ... rest of config

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    # ... rest of config
```

**Frontend production Dockerfile:**
```dockerfile
# frontend/Dockerfile.prod
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Deploy:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ FULL-STACK CHECKLIST

### Initial Setup
- [x] Frontend Dockerfile created
- [x] docker-compose.yml updated
- [x] Frontend proxy configured
- [x] .dockerignore added
- [x] Health checks configured

### Running
- [ ] `.env` file configured with credentials
- [ ] `docker-compose up -d` executed
- [ ] All 3 services running
- [ ] Frontend accessible at :3000
- [ ] Backend accessible at :8000
- [ ] End-to-end test successful

---

## 🎯 QUICK COMMANDS REFERENCE

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart frontend

# Rebuild service
docker-compose up -d --build frontend

# Check status
docker-compose ps

# View specific logs
docker-compose logs -f frontend

# Execute command in container
docker-compose exec frontend sh

# Remove everything (including volumes)
docker-compose down -v
```

---

## 🎉 SUCCESS!

**You now have a complete full-stack Docker setup!**

**Single command to run everything:**
```bash
docker-compose up -d
```

**Access points:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

**All services work together seamlessly!** ✅

---

## 📚 WHAT'S INCLUDED

| Service | Port | Container Name | Status |
|---------|------|----------------|--------|
| Frontend | 3000 | hybrid-rag-frontend | ✅ NEW |
| Backend | 8000 | hybrid-rag-backend | ✅ |
| Redis | 6379 | hybrid-rag-redis | ✅ |

**Total: 3 services running with Docker Compose** 🎉

---

**Updated:** October 2025  
**Status:** ✅ COMPLETE - Full-Stack Docker Setup  
**Ready:** Start with `docker-compose up -d`
