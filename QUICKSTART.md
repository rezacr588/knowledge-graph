# Quick Start Guide - Hybrid RAG System

Get up and running in **15 minutes**!

## Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- Free accounts for:
  - [Neo4j AuraDB](https://neo4j.com/cloud/aura-free/) (free tier)
  - [Qdrant Cloud](https://cloud.qdrant.io/) (free tier)
  - [Google Gemini API](https://aistudio.google.com/) (free tier)

## Step 1: Setup (5 minutes)

```bash
# Clone repository
cd /Users/rezazeraat/Desktop/KnowledgeGraph

# Run setup script
chmod +x setup.sh
./setup.sh

# The script will:
# ✅ Check Python version
# ✅ Create virtual environment
# ✅ Install dependencies
# ✅ Download spaCy models
# ✅ Download NLTK data
# ✅ Create .env file
```

## Step 2: Configure Credentials (5 minutes)

Edit the `.env` file with your credentials:

```bash
nano .env
```

**Get your credentials:**

### Neo4j AuraDB (Graph Database)
1. Go to https://neo4j.com/cloud/aura-free/
2. Sign up (free, no credit card)
3. Create a new instance
4. Copy the connection URI, username, and password

### Qdrant (Vector Database)
1. Go to https://cloud.qdrant.io/
2. Sign up (free, no credit card)
3. Create a new cluster
4. Copy the cluster URL and API key

### Gemini API (LLM)
1. Go to https://aistudio.google.com/
2. Sign in with Google account
3. Click "Get API Key"
4. Copy the API key

**Your .env should look like:**
```env
NEO4J_URI=neo4j+s://abc123.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-here

QDRANT_URL=https://xyz.qdrant.io:6333
QDRANT_API_KEY=your-api-key-here

GEMINI_API_KEY=your-gemini-key-here
```

## Step 3: Start the System (2 minutes)

### Option A: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Wait for "Hybrid RAG System started successfully!"
```

### Option B: Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn backend.main:app --reload

# Server will start on http://localhost:8000
```

## Step 4: Test the System (3 minutes)

### Check Health

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "dependencies": {
    "neo4j": {"available": true},
    "bm25": {"available": true},
    "colbert": {"available": true}
  }
}
```

### Ingest a Test Document

```bash
# Create test document
echo "Hybrid retrieval systems combine BM25 sparse retrieval with ColBERT dense retrieval and knowledge graph traversal. This approach achieves better accuracy than single-method systems." > test_doc.txt

# Ingest document
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@test_doc.txt" \
  -F "language=en"
```

**Expected response:**
```json
{
  "document_id": "abc123",
  "chunks_created": 1,
  "entities_extracted": 5,
  "relationships_found": 0,
  "processing_time_ms": 1234.5,
  "status": "success"
}
```

### Query the System

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is hybrid retrieval?",
    "top_k": 5,
    "language": "en"
  }'
```

**Expected response:**
```json
{
  "results": [
    {
      "doc_id": "abc123",
      "chunk_id": "abc123_chunk_0",
      "text": "Hybrid retrieval systems combine...",
      "rrf_score": 0.0486,
      "rank": 1,
      "method_scores": {
        "bm25": 15.3,
        "colbert": 0.89,
        "graph": 0.75
      }
    }
  ],
  "total_time_ms": 258.1
}
```

## Step 5: Explore the API

Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Try the interactive API documentation!

## Common Issues & Solutions

### Issue: "Neo4j connection failed"

**Solution:**
- Check your Neo4j URI format: `neo4j+s://` (with `+s` for SSL)
- Verify credentials are correct
- Check firewall allows port 7687

### Issue: "ColBERT initialization failed"

**Solution:**
```bash
# ColBERT requires more dependencies, install manually:
pip install torch
pip install ragatouille
```

### Issue: "spaCy model not found"

**Solution:**
```bash
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download xx_ent_wiki_sm
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or run on different port
uvicorn backend.main:app --port 8001
```

## What's Next?

### Test Multilingual Support

```bash
# Ingest Arabic document
echo "أنظمة الاسترجاع الهجينة تجمع بين BM25 و ColBERT" > arabic_doc.txt
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@arabic_doc.txt" \
  -F "language=ar"

# Query in Arabic
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "ما هو BM25؟", "language": "ar"}'
```

### Run Evaluation

```bash
# Run evaluation framework
python evaluation/benchmark.py

# Results show comparison of BM25, ColBERT, Graph, and Hybrid methods
```

### Deploy to Production

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment
kubectl get pods
kubectl get svc
```

## Need Help?

- **Documentation**: See `README.md` for full documentation
- **Architecture**: See `DESIGN_DOCUMENT.md` for technical details
- **API Reference**: http://localhost:8000/docs

---

**🎉 Congratulations! Your Hybrid RAG System is running!**
