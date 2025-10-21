# Quick Development Start 🚀

## One-Time Setup

```bash
# 1. Make scripts executable
chmod +x *.sh

# 2. Setup Python venv and install dependencies
./setup_venv.sh

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials (Neo4j, Gemini API, etc.)
```

## Daily Development

### Start Everything
```bash
./start_dev.sh
```

This starts:
- ✅ Redis in Docker
- ✅ Backend in venv (http://localhost:8000)
- ✅ Frontend with Vite (http://localhost:5173)

### Stop Everything
```bash
./stop_dev.sh
```

## Manual Control

### Redis Only
```bash
# Start
docker-compose -f docker-compose.dev.yml up -d

# Stop
docker-compose -f docker-compose.dev.yml down
```

### Backend Only
```bash
# Terminal 1
./start_backend.sh

# Or manually:
source venv/bin/activate
python -m uvicorn backend.main:app --reload --port 8000
```

### Frontend Only
```bash
# Terminal 2
cd frontend
npm run dev
```

## Quick Checks

```bash
# Check Redis
docker ps | grep redis
redis-cli -h localhost -p 6379 ping

# Check Backend
curl http://localhost:8000/health

# Check Frontend
curl http://localhost:5173
```

## URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

## Troubleshooting

### Port conflicts
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Kill process on port 6379
docker-compose -f docker-compose.dev.yml down
```

### Dependencies issues
```bash
# Backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Reset everything
```bash
./stop_dev.sh
rm -rf venv
./setup_venv.sh
cd frontend && rm -rf node_modules && npm install && cd ..
```

## File Structure

```
KnowledgeGraph/
├── backend/              # Python backend
├── frontend/             # React frontend
├── venv/                 # Python virtual environment
├── .env                  # Your config (gitignored)
├── docker-compose.dev.yml # Redis only
├── setup_venv.sh         # Setup script
├── start_dev.sh          # Start all
├── start_backend.sh      # Start backend only
└── stop_dev.sh           # Stop all
```

## Development Workflow

1. **Start services**: `./start_dev.sh`
2. **Make changes**: Edit code in `backend/` or `frontend/src/`
3. **Auto-reload**: Both backend and frontend reload automatically
4. **Test**: Visit http://localhost:5173
5. **Check logs**: Watch the terminals
6. **Stop**: `./stop_dev.sh` or Ctrl+C

## Next Steps

- 📖 Read **[DEV_SETUP_GUIDE.md](DEV_SETUP_GUIDE.md)** for detailed info
- 🌐 Visit **[Documentation](http://localhost:5173)** > Docs tab
- 🔧 Check **[API Docs](http://localhost:8000/docs)** for endpoint testing
