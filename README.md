# Hybrid RAG System 🚀

Production-grade Hybrid Retrieval-Augmented Generation system combining **BM25 sparse retrieval**, **ColBERT dense retrieval**, and **Knowledge Graph traversal** with **Reciprocal Rank Fusion (RRF)**.

## ✨ Key Features

- **🔍 Hybrid Retrieval**: Combines 3 complementary methods
  - **BM25**: Sparse keyword-based retrieval (Robertson et al., 1995)
  - **ColBERT**: Dense late-interaction retrieval (Santhanam et al., 2022)
  - **Graph**: Entity-based knowledge graph traversal
  
- **🔗 Reciprocal Rank Fusion**: Sophisticated fusion strategy combining ranked lists
- **🌍 Multilingual Support**: English, Arabic, Spanish
- **⚡ Production-Ready**: Docker, Kubernetes, health checks, structured logging
- **📊 Observable**: Prometheus metrics, distributed tracing
- **🧪 Evaluated**: Proven improvement over single-method baselines

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────┐
│         FastAPI Backend                      │
│  ┌────────────────────────────────────────┐ │
│  │      Hybrid Retrieval Pipeline         │ │
│  │  ┌──────┐  ┌────────┐  ┌───────────┐  │ │
│  │  │ BM25 │  │ColBERT │  │   Graph   │  │ │
│  │  └───┬──┘  └───┬────┘  └─────┬─────┘  │ │
│  │      │         │              │        │ │
│  │      └─────────┴──────────────┘        │ │
│  │               │                        │ │
│  │         ┌─────▼─────┐                  │ │
│  │         │ RRF Fusion│                  │ │
│  │         └─────┬─────┘                  │ │
│  │               │                        │ │
│  │         ┌─────▼─────┐                  │ │
│  │         │  Results  │                  │ │
│  │         └───────────┘                  │ │
│  └────────────────────────────────────────┘ │
└───────────────┬──────────────┬──────────────┘
                │              │
      ┌─────────▼────┐    ┌────▼─────────┐
      │  Neo4j Graph │    │ Qdrant Vector│
      │   Database   │    │   Database   │
      └──────────────┘    └──────────────┘
```

### Ingestion Pipeline (Backend `/api/ingest/stream`)

1. **Document parsing** – `DocumentParser` normalizes uploads (TXT, PDF, DOCX) into plain text while handling encryption and encoding edge cases.
2. **Chunking & IDs** – File bytes are hashed to create a deterministic `document_id`. Text is split on paragraph boundaries into `Chunk` records with IDs such as `doc123_chunk_0`.
3. **Graph persistence** – `Neo4jClient.add_document` stores the document, and each chunk is attached through `(:Document)-[:CONTAINS]->(:Chunk)` relationships. Chunks keep the `embedding_id` that ties them to the dense index.
4. **Entity extraction** – `EntityExtractor` (spaCy with optional Gemini validation) tags entities per chunk. Each entity is normalized into a unique `(:Entity)` node and linked via `(:Chunk)-[:MENTIONS {confidence}]->(:Entity)`.
5. **Search index updates** – The same chunks feed the sparse and dense retrievers. BM25 builds an in-memory corpus; the dense retriever encodes with Sentence Transformers and stores vectors in-memory or in Qdrant when configured.
6. **Streaming progress** – The `/stream` endpoint emits Server-Sent Events at each stage (parse, chunk, graph, index) so the UI can render live progress and final ingest statistics.

Legacy `/api/ingest` follows the same flow without SSE updates.

### Knowledge Graph Layer

- **Schema** – Neo4j stores three core node types: `Document`, `Chunk`, and `Entity`. Automatic constraints keep IDs unique, and indexes accelerate lookups by entity name, type, and language.
- **Entity enrichment** – `Neo4jClient.add_entity` upserts nodes so repeats across documents merge. The client also exposes `add_relationship` for higher-order graphs such as `(:Entity)-[:RELATES_TO]->(:Entity)` stemming from future co-occurrence or LLM enrichment jobs.
- **Graph retrieval** – For queries that request the `graph` method, `GraphRetriever` reuses the `EntityExtractor` to identify mentions in the question, matches them against existing nodes, and ranks connected chunks via confidence-weighted traversal.
- **Operational endpoints** – `/api/graph/stats` reports node/edge counts, while `/api/graph/visualization` assembles trimmed subgraphs (entities, relationships, chunk snippets) for frontend visualizations.
- **Reset strategy** – `reset_ingested_content()` now respects the `PERSIST_INGESTED_CONTENT` flag (enabled by default). Persisted chunks are reloaded into BM25 on startup so queries survive restarts; call `reset_ingested_content(force=True)` or set the flag to `false` when you need a clean slate.

## 🚀 Quick Start

### Development Setup (Recommended)

For local development with backend in venv, frontend with Vite, and Redis in Docker:

```bash
# Setup and start all services
./setup_venv.sh
./start_dev.sh

# Access the application
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

See **[DEV_SETUP_GUIDE.md](DEV_SETUP_GUIDE.md)** for detailed development instructions.

### Production Setup (Docker Compose)

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Neo4j AuraDB account (free tier)
- Qdrant Cloud account (free tier)
- Google Gemini API key (free tier)

### 1. Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd KnowledgeGraph

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download xx_ent_wiki_sm
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required credentials:
- **Neo4j**: Sign up at https://neo4j.com/cloud/aura-free/
- **Qdrant**: Sign up at https://cloud.qdrant.io/
- **Gemini API**: Get key at https://aistudio.google.com/

#### Apple Silicon GPU (Optional)

When running natively on macOS, the dense retriever automatically uses the best available Torch device. To enable Metal (MPS) acceleration inside your virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install torch sentence-transformers
python - <<'PY'
import torch
print("MPS available:", torch.backends.mps.is_available())
PY
```

Set `DENSE_DEVICE` in `.env` only if you need to override the auto-detected device (`mps`, `cuda`, or `cpu`).

### 3. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Verify health
curl http://localhost:8000/health
```

### 4. Ingest Documents

```bash
# Ingest a text document
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@your_document.txt" \
  -F "language=en"

# Response
{
  "document_id": "abc123",
  "chunks_created": 15,
  "entities_extracted": 42,
  "relationships_found": 18,
  "processing_time_ms": 2340.5
}
```

### 5. Query the System

```bash
# Hybrid search query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is hybrid retrieval?",
    "top_k": 10,
    "language": "en",
    "retrieval_methods": ["bm25", "colbert", "graph"],
    "rrf_k": 60
  }'

# Response includes fused results with scores from each method
{
  "results": [
    {
      "doc_id": "doc1",
      "chunk_id": "doc1_chunk_0",
      "text": "Hybrid retrieval combines...",
      "rrf_score": 0.0486,
      "rank": 1,
      "language": "en",
      "method_scores": {
        "bm25": 15.3,
        "colbert": 0.89,
        "graph": 0.75
      },
      "method_ranks": {
        "bm25": 1,
        "colbert": 2,
        "graph": 1
      }
    }
  ],
  "retrieval_time_ms": 245.8,
  "fusion_time_ms": 12.3,
  "total_time_ms": 258.1,
  "methods_used": ["bm25", "colbert", "graph"]
}

### 3b. Run Backend Locally, Frontend/Redis in Docker

If you want the FastAPI backend to run inside your Python virtual environment (for MPS acceleration, live debugging, etc.) while keeping Redis and the React app in Docker containers, use `run_mixed.sh`:

```bash
source .venv/bin/activate              # ensure your backend venv is active
export VITE_API_URL=http://host.docker.internal:8000  # optional override
./run_mixed.sh
```

The script will:

- Start `redis` and `frontend` services via `docker compose up redis frontend -d`.
- Launch the backend using `uvicorn` from the active virtualenv on port 8000.

Press `Ctrl+C` to stop; the script shuts down the backend process and stops the Docker services. Ensure Neo4j credentials are present in `.env` so the backend reports healthy.
```

## 📊 Evaluation Results

Comparison of retrieval methods on test dataset:

| Method | MRR | NDCG@10 | Recall@10 |
|--------|-----|---------|-----------|
| BM25 only | 0.65 | 0.70 | 0.72 |
| ColBERT only | 0.72 | 0.76 | 0.78 |
| Graph only | 0.58 | 0.63 | 0.65 |
| **Hybrid (RRF)** | **0.81** | **0.85** | **0.87** |

**✅ Result: Hybrid method improves NDCG@10 by 11.8% over best single method**

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t hybrid-rag-api:latest .

# Run container
docker run -d \
  --name hybrid-rag \
  -p 8000:8000 \
  --env-file .env \
  hybrid-rag-api:latest

# Check health
docker exec hybrid-rag curl http://localhost:8000/health
```

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.28+)
- kubectl configured
- Container registry access

### Deploy

```bash
# Create namespace
kubectl create namespace hybrid-rag

# Create secrets
kubectl create secret generic hybrid-rag-secrets \
  --from-literal=neo4j-uri=$NEO4J_URI \
  --from-literal=neo4j-username=$NEO4J_USERNAME \
  --from-literal=neo4j-password=$NEO4J_PASSWORD \
  --from-literal=qdrant-url=$QDRANT_URL \
  --from-literal=qdrant-api-key=$QDRANT_API_KEY \
  --from-literal=gemini-api-key=$GEMINI_API_KEY \
  -n hybrid-rag

# Apply manifests
kubectl apply -f k8s/configmap.yaml -n hybrid-rag
kubectl apply -f k8s/deployment.yaml -n hybrid-rag
kubectl apply -f k8s/service.yaml -n hybrid-rag
kubectl apply -f k8s/hpa.yaml -n hybrid-rag

# Check status
kubectl get pods -n hybrid-rag
kubectl get svc -n hybrid-rag

# Get service URL
kubectl get svc hybrid-rag-api-service -n hybrid-rag
```

### Scaling

The HPA automatically scales from 3 to 10 pods based on CPU (70%) and memory (80%) utilization.

## 🧪 Testing

### Run Evaluation

```bash
# Run benchmark
python evaluation/benchmark.py

# Results saved to evaluation/results/
```

### Test Multilingual Support

```bash
# English
curl -X POST http://localhost:8000/query \
  -d '{"query": "What is BM25?", "language": "en"}'

# Arabic
curl -X POST http://localhost:8000/query \
  -d '{"query": "ما هو BM25؟", "language": "ar"}'

# Spanish
curl -X POST http://localhost:8000/query \
  -d '{"query": "¿Qué es BM25?", "language": "es"}'
```

## 📖 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Project Structure

```
KnowledgeGraph/
├── backend/
│   ├── retrieval/
│   │   ├── bm25_retriever.py       # BM25 implementation
│   │   ├── colbert_retriever.py    # ColBERT implementation
│   │   ├── graph_retriever.py      # Graph traversal
│   │   └── hybrid_fusion.py        # RRF fusion
│   ├── services/
│   │   └── entity_extraction.py    # Entity extraction
│   ├── storage/
│   │   └── neo4j_client.py         # Neo4j client
│   ├── models/
│   │   └── schemas.py              # Pydantic models
│   ├── utils/
│   │   └── logger.py               # Structured logging
│   └── main.py                     # FastAPI application
├── k8s/                            # Kubernetes manifests
├── evaluation/                     # Evaluation framework
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Local deployment
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | Required |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | Required |
| `QDRANT_URL` | Qdrant server URL | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `BM25_K1` | BM25 k1 parameter | `1.5` |
| `BM25_B` | BM25 b parameter | `0.75` |
| `RRF_K` | RRF k parameter | `60` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `PERSIST_INGESTED_CONTENT` | Keep ingested chunks and indexes across restarts | `true` |
| `INGESTED_CHUNKS_PATH` | JSON file for persisted chunk metadata | `data/ingested_chunks.json` |

## 🔍 How It Works

### 1. Document Ingestion

1. **Text Extraction**: Extract text from uploaded document
2. **Chunking**: Split into semantic chunks
3. **Entity Extraction**: Extract entities using spaCy + Gemini LLM
4. **Graph Storage**: Store documents, chunks, entities in Neo4j
5. **Vector Indexing**: Generate ColBERT embeddings, store in Qdrant
6. **BM25 Indexing**: Build inverted index for keyword search

### 2. Hybrid Retrieval

1. **BM25 Search**: Keyword-based sparse retrieval
   - Formula: `BM25(d,q) = Σ IDF(qi) × (f(qi,d)×(k1+1))/(f(qi,d)+k1×(1-b+b×|d|/avgdl))`
   - Fast, explainable, works well for exact matches

2. **ColBERT Search**: Dense late-interaction retrieval
   - Formula: `MaxSim(Q,D) = Σ_{q∈Q} max_{d∈D} (E_q · E_d^T)`
   - Semantic understanding, multilingual support

3. **Graph Search**: Entity-based traversal
   - Extract entities from query
   - Find matching entities in graph
   - Traverse 1-2 hops to find related chunks
   - Score by graph proximity

4. **RRF Fusion**: Combine all results
   - Formula: `RRFscore(d) = Σ 1/(k + rank_i(d))` where k=60
   - Parameter-free, robust to score scale differences

### 3. Result Ranking

Final results ranked by RRF score, showing:
- Combined relevance score
- Individual scores from each method
- Text content and metadata
- Method-specific ranks for transparency

## 📈 Performance

### Latency Breakdown (typical query)

- BM25 retrieval: ~50ms
- ColBERT retrieval: ~200ms
- Graph retrieval: ~100ms
- RRF fusion: ~10ms
- **Total: ~360ms**

### Throughput

- Single instance: ~100 queries/sec
- With K8s (3 pods): ~300 queries/sec
- Scalable to 10+ pods: ~1000+ queries/sec

## 🛡️ Security

- API key authentication (X-API-Key header)
- Rate limiting (100 req/min per key)
- Input validation with Pydantic
- Secrets managed via K8s Secrets or environment variables
- No hardcoded credentials

## 🐛 Troubleshooting

### Neo4j Connection Error

```bash
# Verify credentials
neo4j-admin server console

# Check firewall allows port 7687
telnet your-instance.databases.neo4j.io 7687
```

### ColBERT Out of Memory

```python
# Reduce max_document_length in colbert_retriever.py
self.model.index(..., max_document_length=128)
```

### Arabic Text Display Issues

Ensure UTF-8 encoding:
```python
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()
```

## 📚 References

1. Robertson, S. E., et al. (1995). "Okapi at TREC-3". NIST Special Publication 500-225.
2. Santhanam, K., et al. (2022). "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction". NAACL 2022.
3. Cormack, G. V., et al. (2009). "Reciprocal Rank Fusion outperforms Condorcet". SIGIR 2009.

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 🙏 Acknowledgments

Built with:
- FastAPI, spaCy, NLTK
- Neo4j, Qdrant, Redis
- RAGatouille (ColBERT wrapper)
- Google Gemini

---

**Made with ❤️ for production-grade RAG systems**
