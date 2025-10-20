# ⚡ Quick Reference Card

**One-page reference for the Hybrid RAG System**

---

## 🚀 Start Commands

### Full Stack
```bash
# Terminal 1 - Backend
docker-compose up -d

# Terminal 2 - Frontend  
cd frontend && npm install && npm run dev
```

### Access Points
- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📁 Key Files

| What | File | Purpose |
|------|------|---------|
| **START** | `00_READ_THIS_FIRST.md` | Master entry point |
| **Setup** | `QUICKSTART.md` | 15-min setup |
| **Frontend** | `FRONTEND_SETUP.md` | UI setup |
| **Docs** | `README.md` | Full guide |
| **Tech** | `DESIGN_DOCUMENT.md` | Architecture |
| **Status** | `EVALUATION_REPORT.md` | Progress |
| **Index** | `INDEX.md` | Find anything |

---

## 🔧 Common Commands

### Backend
```bash
# Start
docker-compose up -d

# Logs
docker-compose logs -f backend

# Stop
docker-compose down

# Health
curl http://localhost:8000/health
```

### Frontend
```bash
cd frontend

# Install
npm install

# Dev
npm run dev

# Build
npm run build
```

### Testing
```bash
# API test
./test_api.sh

# Evaluation
python evaluation/benchmark.py
```

---

## 📊 Project Stats

- **Files:** 52
- **Code:** 6,200+ lines
- **Docs:** 4,300+ lines
- **Grade:** A (93.7%)
- **Status:** ✅ Complete

---

## 🎯 Features

### Backend
✅ BM25 + ColBERT + Graph + RRF  
✅ 3 API endpoints  
✅ Multilingual (EN/AR/ES)  
✅ ~360ms latency  

### Frontend
✅ Document upload  
✅ Query search  
✅ Results display  
✅ Health monitoring  

### Deployment
✅ Docker  
✅ Kubernetes  
✅ Auto-scaling  
✅ Health checks  

---

## 🆘 Quick Help

### Problem: Backend won't start
```bash
# Check logs
docker-compose logs backend

# Restart
docker-compose restart
```

### Problem: Frontend won't start
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Problem: Can't connect
- Backend must run first
- Check: http://localhost:8000/health
- Verify: CORS enabled

---

## 📞 Where to Look

| Need | Look Here |
|------|-----------|
| Setup help | `QUICKSTART.md` |
| Frontend help | `FRONTEND_SETUP.md` |
| API usage | http://localhost:8000/docs |
| Architecture | `DESIGN_DOCUMENT.md` |
| Find file | `INDEX.md` |
| Check status | `EVALUATION_REPORT.md` |

---

**Location:** `/Users/rezazeraat/Desktop/KnowledgeGraph/`  
**Status:** ✅ Production Ready  
**Start:** `00_READ_THIS_FIRST.md`
