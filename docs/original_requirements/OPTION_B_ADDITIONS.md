# Option B Implementation - Additional Sections

## Day 3: Knowledge Graph & Entity Extraction

### Task 3.1: Entity Extraction Pipeline (4 hours)
- [ ] **Install dependencies**:
  ```bash
  pip install spacy langchain-google-genai
  python -m spacy download en_core_web_sm
  python -m spacy download es_core_news_sm
  python -m spacy download xx_ent_wiki_sm  # multilingual
  ```
- [ ] **Create `services/entity_extraction.py`**:
  - [ ] LLM-based extraction using Gemini Pro
  - [ ] spaCy NER for fallback/validation
  - [ ] Entity type classification (Person, Org, Location, Concept)
  - [ ] Relationship extraction between entities
  - [ ] Multilingual entity handling
- [ ] **Entity linking**:
  - [ ] Cross-language entity matching
  - [ ] Deduplication logic
  - [ ] Confidence scoring
- [ ] **Testing**:
  - [ ] Test with English documents
  - [ ] Test with Arabic documents
  - [ ] Test with Spanish documents
  - [ ] Verify entity quality

### Task 3.2: Graph Database Integration (3 hours)
- [ ] **Create `storage/neo4j_client.py`**:
  - [ ] Connection management
  - [ ] Graph schema enforcement
  - [ ] Node creation (entities with metadata)
  - [ ] Relationship creation
  - [ ] Query templates for traversal
- [ ] **Graph schema design**:
  ```cypher
  // Node types
  (:Document {id, title, language, content_hash})
  (:Entity {id, name, type, language, canonical_name})
  (:Chunk {id, text, language, embedding_id})
  
  // Relationships
  (Document)-[:CONTAINS]->(Chunk)
  (Chunk)-[:MENTIONS]->(Entity)
  (Entity)-[:RELATES_TO {type, confidence}]->(Entity)
  (Entity)-[:SAME_AS]->(Entity)  // cross-language linking
  ```
- [ ] **Implement Cypher queries**:
  - Subgraph retrieval around entities
  - Multi-hop traversal with depth limits
  - Relationship-based ranking
  - Language-aware querying

### Task 3.3: Graph-based Retriever (2 hours)
- [ ] **Create `retrieval/graph_retriever.py`**:
  - [ ] Extract entities from query using NER/LLM
  - [ ] Find matching nodes in graph
  - [ ] Traverse relationships (1-2 hops)
  - [ ] Retrieve connected chunks
  - [ ] Score by graph proximity
  - [ ] Return ranked results with context
- [ ] **Testing**:
  - [ ] Test entity-based queries
  - [ ] Test relationship traversal
  - [ ] Compare with vector-only retrieval

---

## Day 4: Fusion Strategy & API Development

### Task 4.1: Reciprocal Rank Fusion (3 hours)
- [ ] **Create `retrieval/hybrid_fusion.py`**:
  - [ ] Implement RRF algorithm:
    ```python
    def reciprocal_rank_fusion(results_lists, k=60):
        """
        Combine multiple ranked lists using RRF
        score(d) = sum(1 / (k + rank_i(d)))
        """
        scores = defaultdict(float)
        for results in results_lists:
            for rank, doc in enumerate(results, start=1):
                scores[doc.id] += 1.0 / (k + rank)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ```
  - [ ] Weighted scoring alternative
  - [ ] Configurable fusion parameters
  - [ ] Normalization strategies
- [ ] **BGE Re-ranker integration (optional)**:
  ```bash
  pip install sentence-transformers
  ```
  - [ ] Load BGE reranker model
  - [ ] Re-rank top-K results
  - [ ] Cross-encoder scoring
- [ ] **Testing**:
  - [ ] Compare RRF vs weighted fusion
  - [ ] Test different k parameters
  - [ ] Measure improvement over single methods

### Task 4.2: FastAPI Backend (4 hours)
- [ ] **Create `api/routes.py`**:
  ```python
  @app.post("/ingest")
  async def ingest_document(file: UploadFile, language: str = None):
      # Extract text, chunk, embed, extract entities, store
      
  @app.post("/query")
  async def hybrid_search(query: str, top_k: int = 10):
      # Run BM25, ColBERT, Graph retrieval in parallel
      # Fuse results with RRF
      # Generate answer with LLM
      
  @app.get("/health")
  async def health_check():
      # Check all dependencies
      
  @app.get("/metrics")
  async def metrics():
      # Prometheus metrics
  ```
- [ ] **Request/Response models** (`models/schemas.py`):
  - [ ] IngestRequest, IngestResponse
  - [ ] QueryRequest, QueryResponse
  - [ ] RetrievalResult with metadata
- [ ] **Error handling**:
  - [ ] Custom exception classes
  - [ ] HTTP error responses
  - [ ] Logging integration
- [ ] **CORS configuration**
- [ ] **OpenAPI documentation**

### Task 4.3: Async Task Queue (2 hours)
- [ ] **Setup Celery**:
  ```bash
  pip install celery redis
  ```
- [ ] **Create `tasks/ingestion.py`**:
  - [ ] Async document processing
  - [ ] Batch embedding generation
  - [ ] Entity extraction tasks
  - [ ] Progress tracking
- [ ] **Redis broker configuration**
- [ ] **Task monitoring**

---

## Day 5: Production Features & Observability

### Task 5.1: Containerization (3 hours)
- [ ] **Create `docker/Dockerfile`**:
  ```dockerfile
  FROM python:3.11-slim
  
  WORKDIR /app
  
  # Install system dependencies
  RUN apt-get update && apt-get install -y \
      build-essential \
      && rm -rf /var/lib/apt/lists/*
  
  # Install Python dependencies
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  
  # Copy application code
  COPY backend/ ./backend/
  
  # Health check
  HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
      CMD curl -f http://localhost:8000/health || exit 1
  
  CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- [ ] **Create `docker-compose.yml`**:
  ```yaml
  version: '3.8'
  services:
    backend:
      build: ./docker
      ports:
        - "8000:8000"
      environment:
        - NEO4J_URI=${NEO4J_URI}
        - QDRANT_URL=${QDRANT_URL}
        - REDIS_URL=redis://redis:6379
      depends_on:
        - redis
    
    redis:
      image: redis:7-alpine
      ports:
        - "6379:6379"
    
    celery-worker:
      build: ./docker
      command: celery -A backend.tasks worker --loglevel=info
      depends_on:
        - redis
  ```
- [ ] **Multi-stage build optimization**
- [ ] **Environment variable configuration**

### Task 5.2: Kubernetes Deployment (3 hours)
- [ ] **Create `k8s/deployment.yaml`**:
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: hybrid-rag-api
  spec:
    replicas: 3
    selector:
      matchLabels:
        app: hybrid-rag-api
    template:
      metadata:
        labels:
          app: hybrid-rag-api
      spec:
        containers:
        - name: api
          image: hybrid-rag-api:latest
          ports:
          - containerPort: 8000
          env:
          - name: NEO4J_URI
            valueFrom:
              secretKeyRef:
                name: hybrid-rag-secrets
                key: neo4j-uri
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              memory: "2Gi"
              cpu: "1"
            limits:
              memory: "4Gi"
              cpu: "2"
  ```
- [ ] **Create `k8s/service.yaml`**
- [ ] **Create `k8s/configmap.yaml`**
- [ ] **Create `k8s/secrets.yaml`** (template)
- [ ] **Create `k8s/hpa.yaml`** (HorizontalPodAutoscaler)
- [ ] **Optional: Helm chart**

### Task 5.3: Observability (3 hours)
- [ ] **Structured logging**:
  ```bash
  pip install loguru structlog
  ```
  - [ ] JSON log formatting
  - [ ] Request ID tracking
  - [ ] Performance logging
- [ ] **OpenTelemetry tracing**:
  ```bash
  pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
  ```
  - [ ] Trace ingestion pipeline
  - [ ] Trace retrieval pipeline
  - [ ] Export to Jaeger/Grafana
- [ ] **Prometheus metrics**:
  ```bash
  pip install prometheus-client
  ```
  - [ ] Request count/latency
  - [ ] Retrieval method performance
  - [ ] Fusion strategy metrics
  - [ ] Error rates
- [ ] **Create Grafana dashboard JSON**

### Task 5.4: Security (1 hour)
- [ ] **API key authentication**:
  ```python
  from fastapi.security import APIKeyHeader
  
  api_key_header = APIKeyHeader(name="X-API-Key")
  ```
- [ ] **Rate limiting**:
  ```bash
  pip install slowapi
  ```
- [ ] **Input validation with Pydantic**
- [ ] **PII redaction (optional)**

---

## Day 6: Frontend & Evaluation

### Task 6.1: React UI (4 hours)
- [ ] **Setup**:
  ```bash
  npm create vite@latest frontend -- --template react
  cd frontend
  npm install axios @tanstack/react-query
  npm install -D tailwindcss postcss autoprefixer
  npm install lucide-react react-force-graph-2d
  npx shadcn-ui@latest init
  ```
- [ ] **Create components**:
  - [ ] `DocumentUpload.tsx` - Upload docs for ingestion
  - [ ] `ChatInterface.tsx` - Query interface with RTL support
  - [ ] `RetrievalComparison.tsx` - Show results from each method
  - [ ] `GraphVisualization.tsx` - Display knowledge graph
  - [ ] `MetricsPanel.tsx` - Show performance stats
- [ ] **API integration with React Query**
- [ ] **Loading states and error handling**
- [ ] **shadcn/ui components for polish**

### Task 6.2: Evaluation Framework (4 hours)
- [ ] **Create evaluation dataset**:
  - [ ] Collect 20-30 documents per language (EN, AR, ES)
  - [ ] Create 10-15 test queries per language
  - [ ] Manual relevance judgments (gold standard)
- [ ] **Create `evaluation/benchmark.py`**:
  ```python
  def evaluate_retrieval(retriever, queries, ground_truth):
      results = {
          'mrr': mean_reciprocal_rank(),
          'ndcg@5': ndcg_at_k(k=5),
          'ndcg@10': ndcg_at_k(k=10),
          'recall@5': recall_at_k(k=5),
          'recall@10': recall_at_k(k=10),
      }
      return results
  ```
- [ ] **Run baseline comparisons**:
  - [ ] BM25 only
  - [ ] ColBERT only
  - [ ] Graph only
  - [ ] Hybrid (BM25 + ColBERT + Graph)
- [ ] **Generate comparison report**:
  - [ ] Tables with metrics
  - [ ] Improvement percentages
  - [ ] Per-language breakdown
  - [ ] Example queries with results
- [ ] **Document findings in design doc**

---

## Day 7: Testing, Documentation & Presentation

### Task 7.1: End-to-End Testing (3 hours)
- [ ] **Integration tests**:
  ```bash
  pip install pytest pytest-asyncio
  ```
  - [ ] Test full ingestion pipeline
  - [ ] Test full retrieval pipeline
  - [ ] Test fusion logic
  - [ ] Test multilingual handling
- [ ] **Load testing**:
  ```bash
  pip install locust
  # OR: npm install -g k6
  ```
  - [ ] Simulate concurrent requests
  - [ ] Measure throughput
  - [ ] Identify bottlenecks
- [ ] **Test multilingual scenarios**:
  - [ ] English doc + English query
  - [ ] Arabic doc + Arabic query
  - [ ] Spanish doc + Spanish query
  - [ ] Cross-language queries

### Task 7.2: Documentation (3 hours)
- [ ] **Update `README.md`**:
  ```markdown
  # Hybrid Knowledge Graph + RAG System
  
  ## Features
  - Sparse (BM25) + Dense (ColBERT) + Graph retrieval
  - Reciprocal Rank Fusion
  - Multilingual support (EN, AR, ES)
  
  ## Quick Start
  ```bash
  docker-compose up
  curl -X POST http://localhost:8000/ingest -F file=@document.pdf
  curl http://localhost:8000/query -d '{"q": "What is X?"}'
  ```
  
  ## Architecture
  [Include diagram]
  
  ## Evaluation Results
  [Include comparison table]
  ```
- [ ] **API documentation** (auto-generated via FastAPI)
- [ ] **Architecture Decision Records (ADRs)**:
  - Why ColBERT over standard embeddings
  - Why RRF over weighted fusion
  - Trade-offs in entity extraction
- [ ] **Deployment guide**:
  - Local setup
  - Docker Compose
  - Kubernetes deployment
- [ ] **Troubleshooting guide**

### Task 7.3: Presentation Preparation (2 hours)
- [ ] **Create demo script**:
  1. Show architecture diagram (2 min)
  2. Live demo: Ingest multilingual docs (2 min)
  3. Live demo: Query and show fusion (3 min)
  4. Show evaluation results (2 min)
  5. Q&A prep (3 min)
- [ ] **Prepare for key questions**:
  - "How would you scale to 10x traffic?"
    → Horizontal scaling with K8s, caching layer, async processing
  - "What are the failure modes?"
    → Graph DB down: fallback to vector only
    → LLM timeout: use cached entities
    → Vector DB down: fallback to BM25 + graph
  - "How do you handle drift in entity extraction?"
    → Regular evaluation on test set
    → A/B testing new prompts
    → Monitoring entity quality metrics
- [ ] **Test demo environment**
- [ ] **Prepare backup slides**

---

## 📊 Success Criteria Checklist

### Must Have (Critical):
- [ ] **Hybrid retrieval working**: BM25 + ColBERT + Graph
- [ ] **Fusion strategy implemented**: RRF or weighted scoring
- [ ] **Multilingual support**: EN, AR, ES all working
- [ ] **Production features**: Docker + K8s + health checks
- [ ] **Design document complete**: ≤10 pages, execution-ready
- [ ] **Evaluation demonstrates improvement**: Hybrid > single-method
- [ ] **Live demo working**: End-to-end ingestion and query
- [ ] **Clean API**: Well-documented, type-safe
- [ ] **Observability**: Logs, metrics, traces

### Should Have:
- [ ] Re-ranking with BGE-reranker
- [ ] Helm chart for K8s
- [ ] Grafana dashboard
- [ ] Load testing results
- [ ] PII redaction
- [ ] Beautiful frontend UI
- [ ] Comprehensive test coverage

### Nice to Have:
- [ ] Multiple fusion strategies comparison
- [ ] Query expansion
- [ ] Cross-language entity linking
- [ ] Advanced graph algorithms (PageRank, community detection)
- [ ] Streaming responses

---

## 🎯 Key Deliverables Summary

1. **Design Document** (≤10 pages)
   - Architecture diagrams
   - Component specifications
   - Technology justifications
   - Scalability strategy
   - Deployment architecture

2. **Working POC Repository**
   - Clean, modular code
   - Dockerfile + docker-compose.yml
   - K8s manifests
   - README with setup instructions
   - Evaluation results

3. **Live Presentation** (Day 8)
   - 15-minute walkthrough
   - Live demo
   - Q&A preparation
