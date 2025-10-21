# Development Setup Guide

This guide explains how to run the Hybrid RAG System in development mode with:
- **Backend** running in Python virtual environment (venv)
- **Frontend** running locally with npm/Vite
- **Redis** running in Docker Compose

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd /Users/rezazeraat/Desktop/KnowledgeGraph

# Make scripts executable
chmod +x *.sh

# Setup Python virtual environment
./setup_venv.sh
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required Configuration:**
- `NEO4J_URI` - Your Neo4j connection URI
- `NEO4J_USERNAME` - Neo4j username (usually "neo4j")
- `NEO4J_PASSWORD` - Your Neo4j password
- `GEMINI_API_KEY` - Google Gemini API key
- `REDIS_URL` - Redis connection URL (default: redis://localhost:6379/0)

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Start All Services

**Option A: Start Everything at Once**
```bash
./start_dev.sh
```

**Option B: Start Services Individually**

Terminal 1 - Redis:
```bash
docker-compose -f docker-compose.dev.yml up
```

Terminal 2 - Backend:
```bash
./start_backend.sh
```

Terminal 3 - Frontend:
```bash
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis**: localhost:6379

## Detailed Setup Instructions

### Python Virtual Environment Setup

The `setup_venv.sh` script will:
1. Create a Python virtual environment in `./venv`
2. Install all Python dependencies from `requirements.txt`
3. Download required spaCy language models:
   - `en_core_web_sm` (English)
   - `es_core_news_sm` (Spanish)
   - `xx_ent_wiki_sm` (Multilingual)

**Manual Setup:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download xx_ent_wiki_sm
```

### Redis in Docker

The `docker-compose.dev.yml` file runs only Redis:
- Uses Redis 7 Alpine image
- Exposes port 6379
- Persists data in a Docker volume
- Includes health checks

**Commands:**
```bash
# Start Redis
docker-compose -f docker-compose.dev.yml up -d

# Check Redis status
docker ps | grep redis

# View Redis logs
docker logs hybrid-rag-redis

# Stop Redis
docker-compose -f docker-compose.dev.yml down
```

### Backend Development

The backend runs in the virtual environment with hot-reload enabled:

```bash
# Activate venv
source venv/bin/activate

# Start backend with auto-reload
python -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0
```

**Features:**
- Auto-reload on code changes
- Interactive API docs at `/docs`
- OpenAPI schema at `/openapi.json`
- Health check at `/health`

### Frontend Development

The frontend uses Vite for fast development:

```bash
cd frontend
npm run dev
```

**Features:**
- Hot Module Replacement (HMR)
- Fast refresh on code changes
- Runs on http://localhost:5173
- Proxies API requests to backend

## Development Workflow

### Making Backend Changes

1. Edit Python files in `backend/`
2. Backend automatically reloads (if using `--reload`)
3. Check terminal for errors
4. Test changes via API docs or frontend

### Making Frontend Changes

1. Edit React files in `frontend/src/`
2. Vite hot-reloads the browser
3. Check browser console for errors
4. Changes appear immediately

### Testing

```bash
# Backend tests
source venv/bin/activate
pytest tests/

# Check backend health
curl http://localhost:8000/health

# Check Redis connection
redis-cli -h localhost -p 6379 ping
```

## Stopping Services

### Stop All Services
```bash
./stop_dev.sh
```

This will:
- Stop the backend (uvicorn)
- Stop the frontend (vite)
- Stop Redis container

### Stop Individual Services

**Backend:**
```bash
# Find and kill uvicorn process
pkill -f "uvicorn backend.main:app"
```

**Frontend:**
```bash
# Stop in the terminal with Ctrl+C
# Or kill the vite process
pkill -f "vite"
```

**Redis:**
```bash
docker-compose -f docker-compose.dev.yml down
```

## Troubleshooting

### Virtual Environment Issues

**Problem:** `venv` not activating
```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** Missing dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Redis Connection Issues

**Problem:** Backend can't connect to Redis

**Check Redis is running:**
```bash
docker ps | grep redis
```

**Check Redis connectivity:**
```bash
redis-cli -h localhost -p 6379 ping
# Should return: PONG
```

**Restart Redis:**
```bash
docker-compose -f docker-compose.dev.yml restart
```

### Frontend Build Issues

**Problem:** Dependencies not installing
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem:** Port 5173 already in use
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
cd frontend
npm run dev -- --port 5174
```

### Backend API Issues

**Problem:** Backend won't start

**Check Python version:**
```bash
python3 --version
# Should be 3.8 or higher
```

**Check environment variables:**
```bash
source venv/bin/activate
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Neo4j URI:', os.getenv('NEO4J_URI'))"
```

**View backend logs:**
```bash
tail -f logs/app.log
```

### Neo4j Connection Issues

**Problem:** "Neo4j not available"

**Solutions:**
1. Verify credentials in `.env`
2. Check Neo4j database is running
3. Test connection:
```bash
source venv/bin/activate
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('YOUR_URI', auth=('neo4j', 'YOUR_PASSWORD')); driver.verify_connectivity(); print('Connected!')"
```

## Environment Variables

### Backend (.env)
```bash
# Neo4j
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# Redis (for local dev)
REDIS_URL=redis://localhost:6379/0

# Gemini AI
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

# Optional: Dense Retrieval
DENSE_MODEL=all-MiniLM-L6-v2
DENSE_DEVICE=auto
```

### Frontend
The frontend uses the backend URL from Vite proxy configuration (automatically set to http://localhost:8000).

## File Structure

```
KnowledgeGraph/
├── backend/              # Python backend code
│   ├── main.py          # FastAPI application
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   ├── storage/         # Neo4j client
│   └── retrieval/       # Search methods
├── frontend/            # React frontend code
│   ├── src/            # React components
│   ├── public/         # Static assets
│   └── package.json    # NPM dependencies
├── venv/               # Python virtual environment
├── logs/               # Application logs
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (gitignored)
├── .env.example       # Example environment file
├── docker-compose.dev.yml  # Redis only
├── setup_venv.sh      # Setup script
├── start_dev.sh       # Start all services
├── start_backend.sh   # Start backend only
└── stop_dev.sh        # Stop all services
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `setup_venv.sh` | Create venv and install dependencies |
| `start_dev.sh` | Start all services (Redis, backend, frontend) |
| `start_backend.sh` | Start backend only in venv |
| `stop_dev.sh` | Stop all running services |

## Best Practices

1. **Always activate venv** before running backend commands
2. **Keep .env private** - never commit to git
3. **Use separate terminals** for backend and frontend logs
4. **Check logs** when debugging issues
5. **Restart services** after changing environment variables
6. **Update dependencies** regularly:
   ```bash
   # Backend
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   
   # Frontend
   cd frontend
   npm update
   ```

## Production Deployment

For production deployment, use the full `docker-compose.yml` which containerizes all services:

```bash
docker-compose up -d
```

This guide is for development only. See `DEPLOYMENT.md` for production instructions.

## Getting Help

- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Logs**: Check `./logs/` directory
- **Issues**: Check GitHub issues or create a new one

---

Happy Developing! 🚀
