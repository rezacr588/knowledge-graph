# Option B: Hybrid Knowledge Graph + RAG System - Production Implementation

> **⏰ URGENT: 24-Hour Delivery Deadline**  
> This implementation plan is optimized for delivery by tomorrow with all Option B requirements.  
> Focus: Working POC + Design Document + Live Demo Preparation

---

## 🎯 Project Overview
**Goal**: Build a **production-grade** Hybrid RAG system combining sparse retrieval (BM25), dense retrieval (ColBERT v2), and graph-based retrieval with fusion strategies for **multilingual documents** (English, Arabic, Spanish).

**Priorities:**
1. ✅ **Hybrid retrieval architecture** - Sparse (BM25) + Dense (ColBERT) + Graph traversal
2. ✅ **Fusion strategy** - Reciprocal Rank Fusion (RRF) or weighted scoring
3. ✅ **Multilingual support** - English, Arabic, Spanish with proper entity linking
4. ✅ **Production-ready** - Docker, K8s, observability, health probes, structured logging
5. ✅ **Clean architecture** - Modular, documented, testable code
6. ✅ **Detailed design document** - Architecture diagrams, component specs, deployment strategy
7. ✅ **Evaluation framework** - Demonstrate hybrid > single-method baselines

**Focus**: Production-grade system with execution-ready design documentation.

---

## ⚡ Production Tech Stack (With Versions & Citations)

```yaml
# Retrieval Components (Research-Backed)
Sparse Retrieval: 
  - Library: rank-bm25 v0.2.2 (pip install rank-bm25)
  - Alternative: Elasticsearch 8.x with BM25 similarity
  - Paper: "Okapi at TREC-3" (Robertson et al., 1995)
  - Formula: BM25(d,q) = Σ IDF(qi) × (f(qi,d)×(k1+1))/(f(qi,d)+k1×(1-b+b×|d|/avgdl))
  - Parameters: k1=1.5, b=0.75 (standard)

Dense Retrieval:
  - Model: ColBERTv2 via ragatouille v0.0.8
  - Paper: "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction" (Santhanam et al., 2022)
  - Hugging Face: colbert-ir/colbertv2.0
  - Mechanism: Late-interaction with MaxSim scoring
  - Formula: MaxSim(Q,D) = Σ_{q∈Q} max_{d∈D} E_q · E_d^T
  - Alternative: sentence-transformers/paraphrase-multilingual-mpnet-base-v2

Vector Store:
  - Primary: Qdrant Cloud v1.7+ (https://qdrant.tech/)
  - API: qdrant-client v1.7.0
  - Index: HNSW (Hierarchical Navigable Small World)
  - Distance: Cosine similarity
  - Alternative: Weaviate v1.22+

Graph Database:
  - Primary: Neo4j AuraDB Free (v5.x)
  - Driver: neo4j-python-driver v5.14
  - Query Language: Cypher
  - Alternative: Memgraph v2.11+

# AI/ML Services (With Model Cards)
LLM:
  - Model: Google Gemini 2.0 Flash (gemini-2.0-flash-exp)
  - API: google-generativeai v0.3.2
  - Context: 1M tokens
  - Rate Limits: 10 RPM, 250K TPM (free tier)
  - Endpoint: https://generativelanguage.googleapis.com/v1beta/models/
  
Embeddings:
  - Primary: intfloat/e5-mistral-7b-instruct (Hugging Face)
  - Dimensions: 4096
  - Languages: 100+ (multilingual)
  - Alternative: BAAI/bge-m3 (8192 dims)
  - Library: sentence-transformers v2.2.2

Entity Recognition:
  - spaCy v3.7.2
  - Models: en_core_web_sm, es_core_news_sm, xx_ent_wiki_sm
  - Download: python -m spacy download en_core_web_sm
  - Custom NER: Train on domain-specific data if needed

# Backend Architecture (Exact Versions)
API Framework:
  - FastAPI v0.104.1
  - Uvicorn v0.24.0 (ASGI server)
  - Pydantic v2.5.0 (data validation)
  - Python: 3.11+

Task Queue:
  - Celery v5.3.4
  - Redis v5.0.1 (Python client)
  - Broker: Redis 7.2 (Docker image)

Caching:
  - redis-py v5.0.1
  - TTL: 3600s for embeddings, 1800s for queries
  
Fusion Algorithm:
  - Implementation: Custom RRF (Reciprocal Rank Fusion)
  - Paper: "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods" (Cormack et al., 2009)
  - Formula: RRFscore(d) = Σ_{r∈R} 1/(k + r(d)) where k=60
  - Alternative: Weighted linear combination with learned weights

# Frontend & Deployment
UI Framework:
  - React 18.2.0
  - Vite 5.0.0 (build tool)
  - TailwindCSS 3.3.0
  - shadcn/ui (Radix UI primitives)
  - Lucide React (icons)

Containerization:
  - Docker Engine 24.0+
  - Base Image: python:3.11-slim
  - docker-compose v2.23+

Orchestration:
  - Kubernetes 1.28+
  - Helm v3.13+ (optional)
  - kubectl v1.28+

Observability:
  - Prometheus: prometheus-client v0.19.0
  - OpenTelemetry: opentelemetry-api v1.21.0
  - Logging: loguru v0.7.2
  - Grafana: v10.2+

# Documentation & Standards
Design Doc:
  - Format: Markdown
  - Diagrams: Mermaid v10.6+ or Draw.io
  - Equations: LaTeX notation
  - Citations: IEEE style

API Documentation:
  - OpenAPI 3.1.0 spec
  - Auto-generated via FastAPI
  - Endpoint: /docs (Swagger UI)
  - Alternative: /redoc (ReDoc UI)

Deployment:
  - K8s API: apps/v1
  - Service: v1
  - ConfigMap: v1
  - Health checks: HTTPGetAction
```

---

## 📅 24-Hour Implementation Timeline (Optimized for Tomorrow's Delivery)

> **Critical Path**: Design Doc (4h) → Core Retrieval (8h) → Graph+Fusion (4h) → Docker+Demo (4h) → Testing+Polish (4h)

### **Block 1: Design Document & Setup (0-4 hours)** 📐
- [ ] **Design document creation** (≤10 pages)
  - System architecture diagram (Mermaid/Draw.io)
  - Component specifications (BM25, ColBERT, Graph, Fusion)
  - Data flow diagrams
  - Technology stack justification
  - Scalability & fault tolerance design
  - Observability strategy
  - Security considerations
  - Deployment architecture
  - Assumptions & trade-offs
- [ ] **Infrastructure planning**
  - Neo4j/Memgraph setup
  - Qdrant/Weaviate setup
  - Redis configuration
  - Elasticsearch (optional for BM25)

### **Block 2: Core Retrieval Systems (4-12 hours)** 🔍

#### **Task 2.1: Project Setup (30 min)**

```bash
# Step 1: Create project directory
mkdir hybrid-rag-system && cd hybrid-rag-system

# Step 2: Initialize Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR: venv\Scripts\activate  # Windows

# Step 3: Install ALL required dependencies with exact versions
pip install --upgrade pip
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0
pip install rank-bm25==0.2.2 ragatouille==0.0.8
pip install qdrant-client==1.7.0 neo4j==5.14.0 redis==5.0.1
pip install google-generativeai==0.3.2 langchain==0.1.0
pip install sentence-transformers==2.2.2 spacy==3.7.2
pip install nltk==3.8.1 pydantic==2.5.0 python-dotenv==1.0.0
pip install loguru==0.7.2 celery==5.3.4

# Step 4: Download spaCy models for multilingual support
python -m spacy download en_core_web_sm  # English
python -m spacy download es_core_news_sm # Spanish
python -m spacy download xx_ent_wiki_sm  # Multilingual

# Step 5: Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Step 6: Create project structure
mkdir -p backend/{retrieval,services,storage,models,utils,api}
mkdir -p frontend/src k8s evaluation docs tests

# Step 7: Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
rank-bm25==0.2.2
ragatouille==0.0.8
qdrant-client==1.7.0
neo4j==5.14.0
redis==5.0.1
google-generativeai==0.3.2
langchain==0.1.0
sentence-transformers==2.2.2
spacy==3.7.2
nltk==3.8.1
pydantic==2.5.0
python-dotenv==1.0.0
loguru==0.7.2
celery==5.3.4
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
EOF

# Step 8: Create .env.example template
cat > .env.example << 'EOF'
# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-here

# Qdrant Configuration
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION_NAME=documents

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp

# Application Settings
APP_NAME=hybrid-rag-system
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# Retrieval Parameters
BM25_K1=1.5
BM25_B=0.75
RRF_K=60
TOP_K=10
EOF

# Step 9: Copy to actual .env and fill in credentials
cp .env.example .env
echo "⚠️  IMPORTANT: Edit .env file and add your actual credentials!"
```

#### **Task 2.2: BM25 Sparse Retrieval Implementation (2h)**

**File: `backend/retrieval/bm25_retriever.py`**

```python
"""
BM25 Sparse Retrieval Implementation
Reference: Robertson et al., "Okapi at TREC-3", NIST Special Publication 500-225, 1995
Formula: BM25(d,q) = Σ IDF(qi) × (f(qi,d)×(k1+1))/(f(qi,d)+k1×(1-b+b×|d|/avgdl))
"""

from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from typing import List, Tuple, Dict, Optional
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BM25Result:
    """BM25 search result with metadata"""
    doc_id: str
    score: float
    rank: int
    text: str
    language: str

class MultilingualTokenizer:
    """
    Multilingual tokenizer supporting English, Arabic, Spanish
    """
    def __init__(self):
        # Download required NLTK data if not present
        try:
            stopwords.words('english')
        except LookupError:
            nltk.download('stopwords')
            nltk.download('punkt')
        
        # Initialize stopwords for each language
        self.stopwords = {
            'en': set(stopwords.words('english')),
            'es': set(stopwords.words('spanish')),
            'ar': set(stopwords.words('arabic'))
        }
    
    def tokenize(self, text: str, language: str = 'en') -> List[str]:
        """
        Tokenize text for given language
        
        Args:
            text: Input text to tokenize
            language: Language code ('en', 'ar', 'es')
        
        Returns:
            List of tokens (lowercased, no stopwords)
        """
        # Lowercase and basic cleaning
        text = text.lower()
        
        # Handle Arabic-specific preprocessing
        if language == 'ar':
            # Remove Arabic diacritics (tashkeel)
            text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
            # Normalize Arabic characters
            text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
            text = text.replace('ة', 'ه')
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and non-alphanumeric tokens
        tokens = [
            token for token in tokens 
            if token.isalnum() and token not in self.stopwords.get(language, set())
        ]
        
        return tokens

class BM25Retriever:
    """
    BM25 retrieval implementation with multilingual support
    
    Parameters:
        k1 (float): Term frequency saturation parameter (default: 1.5)
        b (float): Length normalization parameter (default: 0.75)
    
    Reference:
        Robertson, S. E., & Walker, S. (1994). Some simple effective 
        approximations to the 2-poisson model for probabilistic weighted 
        retrieval. In SIGIR'94.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.tokenizer = MultilingualTokenizer()
        self.bm25: Optional[BM25Okapi] = None
        self.documents: List[Dict] = []
        self.tokenized_corpus: List[List[str]] = []
        
        logger.info(f"Initialized BM25Retriever with k1={k1}, b={b}")
    
    def index_documents(self, documents: List[Dict]) -> None:
        """
        Index documents for BM25 retrieval
        
        Args:
            documents: List of dicts with keys: id, text, language, metadata
                Example: [
                    {
                        "id": "doc1",
                        "text": "Document content...",
                        "language": "en",
                        "metadata": {"source": "file.pdf", "page": 1}
                    }
                ]
        """
        logger.info(f"Indexing {len(documents)} documents...")
        
        self.documents = documents
        
        # Tokenize all documents
        self.tokenized_corpus = [
            self.tokenizer.tokenize(doc['text'], doc.get('language', 'en'))
            for doc in documents
        ]
        
        # Initialize BM25 with tokenized corpus
        # Note: BM25Okapi uses k1 and b parameters internally
        self.bm25 = BM25Okapi(
            self.tokenized_corpus,
            k1=self.k1,
            b=self.b
        )
        
        logger.info(f"✅ Successfully indexed {len(documents)} documents")
        logger.info(f"   Average document length: {self.bm25.avgdl:.2f} tokens")
    
    def search(
        self, 
        query: str, 
        top_k: int = 10,
        language: str = 'en',
        min_score: float = 0.0
    ) -> List[BM25Result]:
        """
        Search documents using BM25 scoring
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            language: Query language ('en', 'ar', 'es')
            min_score: Minimum BM25 score threshold
        
        Returns:
            List of BM25Result objects sorted by score (descending)
        
        Example:
            >>> retriever.search("hybrid retrieval", top_k=5, language='en')
            [BM25Result(doc_id='doc1', score=15.3, rank=1, ...)]
        """
        if self.bm25 is None:
            raise ValueError("No documents indexed. Call index_documents() first.")
        
        # Tokenize query
        tokenized_query = self.tokenizer.tokenize(query, language)
        logger.info(f"Query tokens: {tokenized_query}")
        
        # Get BM25 scores for all documents
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k document indices
        top_indices = sorted(
            range(len(scores)), 
            key=lambda i: scores[i], 
            reverse=True
        )[:top_k]
        
        # Build results
        results = []
        for rank, idx in enumerate(top_indices, start=1):
            score = scores[idx]
            if score >= min_score:
                doc = self.documents[idx]
                results.append(BM25Result(
                    doc_id=doc['id'],
                    score=float(score),
                    rank=rank,
                    text=doc['text'],
                    language=doc.get('language', 'en')
                ))
        
        logger.info(f"Found {len(results)} results with score >= {min_score}")
        return results
    
    def get_document_score(self, query: str, doc_id: str, language: str = 'en') -> float:
        """Get BM25 score for a specific document"""
        tokenized_query = self.tokenizer.tokenize(query, language)
        
        # Find document index
        doc_idx = next(
            (i for i, doc in enumerate(self.documents) if doc['id'] == doc_id),
            None
        )
        
        if doc_idx is None:
            return 0.0
        
        scores = self.bm25.get_scores(tokenized_query)
        return float(scores[doc_idx])


# Example usage and testing
if __name__ == "__main__":
    # Test documents in multiple languages
    test_docs = [
        {
            "id": "doc1",
            "text": "Hybrid retrieval systems combine sparse and dense methods for better accuracy.",
            "language": "en"
        },
        {
            "id": "doc2",
            "text": "أنظمة الاسترجاع الهجينة تجمع بين الطرق المتفرقة والكثيفة لدقة أفضل",
            "language": "ar"
        },
        {
            "id": "doc3",
            "text": "Los sistemas de recuperación híbridos combinan métodos dispersos y densos.",
            "language": "es"
        }
    ]
    
    # Initialize and index
    retriever = BM25Retriever(k1=1.5, b=0.75)
    retriever.index_documents(test_docs)
    
    # Test queries
    test_queries = [
        ("hybrid retrieval systems", "en"),
        ("أنظمة الاسترجاع", "ar"),
        ("sistemas de recuperación", "es")
    ]
    
    for query, lang in test_queries:
        print(f"\nQuery: {query} ({lang})")
        results = retriever.search(query, top_k=3, language=lang)
        for result in results:
            print(f"  Rank {result.rank}: {result.doc_id} (score: {result.score:.2f})")
```

#### **Task 2.3: ColBERT Dense Retrieval Implementation (3h)**

**File: `backend/retrieval/colbert_retriever.py`**

```python
"""
ColBERT Dense Retrieval Implementation
Reference: Santhanam et al., "ColBERTv2: Effective and Efficient Retrieval 
via Lightweight Late Interaction", NAACL 2022

ColBERT scoring formula:
MaxSim(Q, D) = Σ_{q∈Q} max_{d∈D} (E_q · E_d^T)

Where:
- Q: Query token embeddings
- D: Document token embeddings  
- E_q, E_d: Embedding vectors
- · : Dot product
"""

from ragatouille import RAGPretrainedModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging
import hashlib
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ColBERTResult:
    """ColBERT search result with metadata"""
    doc_id: str
    score: float
    rank: int
    text: str
    language: str
    embedding_id: str

class ColBERTRetriever:
    """
    ColBERT retrieval using late-interaction mechanism
    
    Model: colbert-ir/colbertv2.0 (110M parameters)
    Paper: https://arxiv.org/abs/2112.01488
    
    Late-interaction allows fine-grained token-level matching between
    query and document, improving accuracy especially for:
    - Technical documents
    - Multi-lingual content
    - Long documents with diverse topics
    """
    
    def __init__(
        self,
        qdrant_url: str,
        qdrant_api_key: str,
        collection_name: str = "colbert_embeddings",
        model_name: str = "colbert-ir/colbertv2.0"
    ):
        """
        Initialize ColBERT retriever
        
        Args:
            qdrant_url: Qdrant server URL (e.g., https://xyz.qdrant.io:6333)
            qdrant_api_key: Qdrant API key
            collection_name: Name for Qdrant collection
            model_name: Hugging Face model name
        """
        logger.info(f"Initializing ColBERT with model: {model_name}")
        
        # Initialize RAGatouille model (handles ColBERT)
        self.model = RAGPretrainedModel.from_pretrained(model_name)
        
        # Initialize Qdrant client
        self.qdrant = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=30.0
        )
        
        self.collection_name = collection_name
        self.documents: Dict[str, Dict] = {}
        
        # Create collection if it doesn't exist
        self._initialize_collection()
        
        logger.info("✅ ColBERT retriever initialized")
    
    def _initialize_collection(self):
        """Create Qdrant collection for ColBERT embeddings"""
        try:
            # Check if collection exists
            collections = self.qdrant.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                # ColBERT embeddings are 128-dimensional per token
                # We'll store document-level aggregated embeddings
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=128,  # ColBERT dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
        
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    def _generate_doc_id_hash(self, doc_id: str) -> str:
        """Generate unique hash for document ID"""
        return hashlib.md5(doc_id.encode()).hexdigest()
    
    def index_documents(
        self, 
        documents: List[Dict],
        batch_size: int = 10
    ) -> None:
        """
        Index documents using ColBERT embeddings
        
        Args:
            documents: List of dicts with keys: id, text, language, metadata
            batch_size: Number of documents to process in each batch
        
        Note: ColBERT generates multiple embeddings per document (one per token).
        For storage efficiency, we use RAGatouille's built-in indexing.
        """
        logger.info(f"Indexing {len(documents)} documents with ColBERT...")
        
        # Store documents in memory for retrieval
        for doc in documents:
            self.documents[doc['id']] = doc
        
        # Use RAGatouille's index method for efficient storage
        # This handles token-level embeddings internally
        try:
            self.model.index(
                collection=[doc['text'] for doc in documents],
                document_ids=[doc['id'] for doc in documents],
                document_metadatas=[{
                    'language': doc.get('language', 'en'),
                    'metadata': doc.get('metadata', {})
                } for doc in documents],
                index_name=self.collection_name,
                max_document_length=256,  # Max tokens per document
                split_documents=True  # Split long documents
            )
            
            logger.info(f"✅ Successfully indexed {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error during indexing: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        language: Optional[str] = None
    ) -> List[ColBERTResult]:
        """
        Search documents using ColBERT late-interaction
        
        Args:
            query: Search query string
            top_k: Number of results to return
            language: Optional language filter ('en', 'ar', 'es')
        
        Returns:
            List of ColBERTResult objects sorted by MaxSim score
        
        MaxSim Scoring:
            For each query token, find maximum similarity with any document token.
            Sum these maximum similarities across all query tokens.
            Higher scores indicate better matches.
        """
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        
        try:
            # RAGatouille handles the late-interaction scoring internally
            results = self.model.search(
                query=query,
                k=top_k,
                index_name=self.collection_name
            )
            
            # Convert to ColBERTResult format
            colbert_results = []
            for rank, result in enumerate(results, start=1):
                doc_id = result['document_id']
                doc = self.documents.get(doc_id, {})
                
                # Filter by language if specified
                if language and doc.get('language') != language:
                    continue
                
                colbert_results.append(ColBERTResult(
                    doc_id=doc_id,
                    score=float(result['score']),
                    rank=rank,
                    text=result['content'],
                    language=doc.get('language', 'unknown'),
                    embedding_id=self._generate_doc_id_hash(doc_id)
                ))
            
            logger.info(f"Found {len(colbert_results)} results")
            return colbert_results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize retriever
    retriever = ColBERTRetriever(
        qdrant_url=os.getenv('QDRANT_URL'),
        qdrant_api_key=os.getenv('QDRANT_API_KEY'),
        collection_name="test_colbert"
    )
    
    # Test documents
    docs = [
        {
            "id": "doc1",
            "text": "ColBERT uses late-interaction for efficient neural retrieval.",
            "language": "en"
        },
        {
            "id": "doc2",
            "text": "BM25 is a probabilistic ranking function based on TF-IDF.",
            "language": "en"
        }
    ]
    
    # Index and search
    retriever.index_documents(docs)
    results = retriever.search("neural retrieval methods", top_k=2)
    
    for result in results:
        print(f"Rank {result.rank}: {result.doc_id} (score: {result.score:.4f})")
```

**Continue with remaining tasks...**

### **Block 3: Graph & Fusion (12-16 hours)** 🕸️🔗
- [ ] **Graph database integration (2h)**:
  - Create `storage/neo4j_client.py`
  - Design graph schema (Document → Chunk → Entity → Relationships)
  - Implement Cypher query templates
  - Test entity storage and retrieval
- [ ] **Graph-based retriever (1.5h)**:
  - Create `retrieval/graph_retriever.py`
  - Extract entities from query
  - Traverse graph (1-2 hops)
  - Score results by proximity
- [ ] **Reciprocal Rank Fusion (1h)**:
  - Create `retrieval/hybrid_fusion.py`
  - Implement RRF algorithm: `score(d) = sum(1/(k+rank))`
  - Configurable k parameter
  - Test fusion with all 3 methods
- [ ] **FastAPI Backend (1.5h)**:
  - Create `main.py` with endpoints:
    - POST `/ingest` - document upload
    - POST `/query` - hybrid search
    - GET `/health` - health check
  - Request/response Pydantic models
  - CORS configuration
  - Error handling

### **Block 4: Production & Docker (16-20 hours)** 🔧
- [ ] **Dockerfile & docker-compose (1.5h)**:
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY backend/ ./backend/
  HEALTHCHECK CMD curl -f http://localhost:8000/health
  CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]
  ```
  - Create docker-compose with backend + redis
  - Test local Docker build
- [ ] **Kubernetes manifests (1h)**:
  - Create `k8s/deployment.yaml` with health probes
  - Create `k8s/service.yaml`
  - Create `k8s/configmap.yaml`
  - Document K8s deployment steps
- [ ] **Structured logging (30 min)**:
  - Add loguru for JSON logs
  - Log request IDs and performance metrics
- [ ] **Simple React UI (1h)** - FUNCTIONAL NOT PRETTY:
  - Create Vite React app
  - Document upload form
  - Query input with results display
  - Show retrieval method scores (optional)

### **Block 5: Testing, Evaluation & Final Polish (20-24 hours)** ✅
- [ ] **Evaluation framework (2h)**:
  - Create test dataset (5-10 docs per language)
  - Create 5 test queries per language
  - Run baseline tests:
    - BM25 only
    - ColBERT only
    - Graph only
    - Hybrid (all 3)
  - Generate comparison table showing hybrid improvement
- [ ] **End-to-end testing (1h)**:
  - Test full ingestion pipeline (EN/AR/ES docs)
  - Test hybrid query flow
  - Test Docker deployment
  - Fix critical bugs
- [ ] **Documentation (1h)**:
  - **README.md**:
    - Quick start commands
    - API usage examples
    - Docker deployment
  - **DESIGN_DOC.md** final review
  - Add evaluation results to design doc
- [ ] **Presentation prep (30 min)**:
  - Prepare demo script (ingest → query → show results)
  - Test live demo environment
  - Prepare architecture diagram walkthrough
  - Document Q&A responses (scalability, failures, 10x)

---

## 💰 Free Resources & Services

### Recommended Free/Testing Stack for Development

**For testing this pipeline without costs, use these services with generous free tiers:**

#### **1. Graph Database - Neo4j AuraDB Free** ✅ RECOMMENDED
- **Free Tier**: Permanent free tier (no time limit, no credit card required)
- **Limits**: 200K nodes + 400K relationships, 50 MB storage
- **Perfect for**: Testing and prototyping GraphRAG pipelines
- **Sign up**: https://neo4j.com/cloud/aura-free/

#### **2. Vector Database Options**

**Qdrant Cloud Free Tier** ✅ RECOMMENDED
- **Free Tier**: 1GB cluster, no credit card required
- **Perfect for**: 1M+ vectors with 384-dimensional embeddings
- **Sign up**: https://cloud.qdrant.io/

**Weaviate Cloud (WCD) Free Tier**
- **Free Tier**: Sandbox environment with 14-day duration
- **Good for**: Quick prototyping and testing

**Pinecone**
- **Free Tier**: Starter plan (1 pod, 100K vectors)
- **Limitations**: More restrictive than Qdrant for testing

#### **3. LLM APIs with Free Credits**

**Google Gemini API** ✅ RECOMMENDED FOR TESTING
- **Free Tier**: Unlimited free requests (rate limited)
- **Models**: 
  - Gemini 2.5 Flash: 10 RPM, 250K TPM, 250 RPD
  - Gemini 2.5 Flash-Lite: 15 RPM, 250K TPM, 1000 RPD (fastest)
  - Gemini 2.5 Pro: 5 RPM, 250K TPM, 100 RPD (best quality)
- **No credit card required**
- **Sign up**: https://aistudio.google.com/

**OpenAI API**
- **Free Credits**: $5 on new accounts (if available)
- **Data Sharing Program**: 11M free tokens/month if you opt-in to share data (until April 2025)
- **Best for**: Production quality, but requires payment setup

**Anthropic Claude API**
- **Free Credits**: Check for promotional credits ($10-20 for eligible developers)
- **Sign up**: https://console.anthropic.com/

**Ollama (Local LLMs)** ✅ 100% FREE
- **Cost**: Completely free, runs locally
- **Models**: Llama 3, Mistral, Phi-3, Gemma (all free)
- **Requirements**: Good GPU/CPU (8GB+ RAM recommended)
- **Perfect for**: Cost-free development and unlimited testing
- **Install**: https://ollama.com/

#### **4. Translation Services**

**Google Cloud Translation API**
- **Free Tier**: $300 credit for new accounts (90 days)
- **Usage**: 500K characters/month free

**LibreTranslate** ✅ FREE
- **Cost**: 100% free and open source
- **Self-hosted**: Run locally for unlimited translations
- **API**: https://libretranslate.com/

#### **5. Hosting & Deployment**

**Vercel** ✅ RECOMMENDED
- **Free Tier**: Generous free tier for frontend hosting
- **Features**: Serverless functions, edge functions, CDN
- **Perfect for**: React/Next.js UI

**Netlify**
- **Free Tier**: 100GB bandwidth/month, 300 build minutes/month
- **Good for**: Static sites and serverless functions

**Railway.app**
- **Free Trial**: $5 credits for 30 days, then $1/month minimum
- **After trial**: $1/month includes $5 usage credits
- **Good for**: Backend services, databases, APIs

**Render**
- **Free Tier**: Free web services (750 hours/month)
- **Good for**: Python FastAPI backend

#### **6. Embedding Models (100% Free)**

**Hugging Face Inference API** ✅ FREE
- **Free Models**: All open-source embedding models
- **Recommended**: `sentence-transformers/all-MiniLM-L6-v2`
- **Multi-lingual**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- **Sign up**: https://huggingface.co/

**Local Sentence Transformers**
- **Cost**: 100% free (runs locally)
- **No API limits**: Unlimited embeddings

#### **7. Redis (Caching)**

**Redis Cloud Free Tier**
- **Free**: 30MB storage
- **Perfect for**: Development caching

**Upstash Redis**
- **Free Tier**: 10K commands/day
- **Serverless**: Pay-per-request model

#### **8. Monitoring & Logging**

**Grafana Cloud Free Tier**
- **Free**: 10K metrics, 50GB logs, 50GB traces

**Sentry Free Tier**
- **Free**: 5K errors/month
- **Perfect for**: Error tracking

### 💡 Cost-Free Testing Stack Recommendation

```yaml
Graph Database: Neo4j AuraDB Free (permanent free)
Vector Store: Qdrant Cloud Free (1GB free)
LLM: Google Gemini 2.5 Flash (unlimited free with rate limits)
Local LLM: Ollama + Llama 3 (100% free, offline)
Embeddings: Hugging Face sentence-transformers (free)
Translation: LibreTranslate (self-hosted, free)
Backend: Railway.app ($5/month credit)
Frontend: Vercel (free tier)
Caching: Upstash Redis (free tier)
Monitoring: Grafana Cloud (free tier)
```

**Estimated Total Cost for Testing**: **$0/month** (completely free!)

---

## 📋 Detailed Implementation Tasks

## Day 1: Design Document & Architecture

### Task 1.1: System Architecture Design (3 hours)
- [ ] **Create architecture diagram** with:
  - Ingestion pipeline (document → chunks → embeddings → storage)
  - Retrieval pipeline (query → BM25 + ColBERT + Graph → RRF fusion → response)
  - Component boundaries (API, retrieval, storage, LLM services)
  - Data flow between components
  - External dependencies (Neo4j, Qdrant, Redis)
- [ ] **Design document sections**:
  - Executive summary (1 page)
  - System architecture (2 pages with diagrams)
  - Component specifications (3 pages)
  - Technology stack justification (1 page)
  - Scalability & fault tolerance (1 page)
  - Observability & monitoring (1 page)
  - Deployment strategy (1 page)
  - Assumptions & trade-offs (½ page)

### Task 1.2: Component Specifications (2 hours)
- [ ] **BM25 sparse retrieval spec**:
  - Tokenization strategy (multilingual)
  - Index structure and updates
  - Scoring mechanism
  - Performance expectations
- [ ] **ColBERT dense retrieval spec**:
  - Model selection (multilingual ColBERT or BGE)
  - Late-interaction scoring approach
  - Vector storage requirements
  - Inference optimization
- [ ] **Graph retrieval spec**:
  - Entity extraction approach (LLM-based vs NER)
  - Relationship types and schema
  - Graph traversal strategies
  - Subgraph ranking
- [ ] **Fusion strategy spec**:
  - RRF algorithm details (k parameter)
  - Weighted scoring alternative
  - Configurable parameters
  - Re-ranking options

### Task 1.3: Technology Stack Justification (1 hour)
- [ ] Document choices:
  - Why ColBERT over standard dense retrieval
  - Why Neo4j/Memgraph for graph storage
  - Why Qdrant/Weaviate for vectors
  - Why FastAPI for API layer
  - Why Redis for caching
- [ ] Document trade-offs:
  - Latency vs accuracy
  - Cost vs performance
  - Complexity vs maintainability

### Task 1.4: Infrastructure Setup (2 hours)
- [ ] **Neo4j AuraDB setup**:
  - Create free/production instance
  - Configure constraints and indexes
  - Test connection
- [ ] **Qdrant Cloud setup**:
  - Create cluster
  - Design collection schema
  - Test vector operations
- [ ] **Redis setup**:
  - Local Redis or Upstash
  - Configure persistence
  - Test caching
- [ ] **Environment configuration**:
  - Create `.env.example` template
  - Document all required credentials
  - Setup local `.env` file

---

## Day 2: Core Retrieval Components Implementation

### Task 2.1: BM25 Sparse Retrieval (3 hours)
- [ ] **Install and setup**:
  ```bash
  pip install rank-bm25 nltk
  # OR for production: setup Elasticsearch
  ```
- [ ] **Create `retrieval/bm25_retriever.py`**:
  - [ ] BM25Retriever class with multilingual tokenization
  - [ ] Support for Arabic, English, Spanish tokenizers
  - [ ] Index building and incremental updates
  - [ ] Query processing with BM25 scoring
  - [ ] Return ranked results with scores
- [ ] **Multilingual tokenization**:
  - [ ] NLTK tokenizers for English/Spanish
  - [ ] Arabic-specific tokenization (pyarabic or custom)
  - [ ] Language detection integration
- [ ] **Testing**:
  - [ ] Test with English queries
  - [ ] Test with Arabic queries (RTL handling)
  - [ ] Test with Spanish queries
  - [ ] Verify scoring correctness

### Task 2.2: ColBERT Dense Retrieval (4 hours)
- [ ] **Install ColBERT dependencies**:
  ```bash
  pip install ragatouille
  # OR: pip install colbert-ai
  ```
- [ ] **Create `retrieval/colbert_retriever.py`**:
  - [ ] ColBERTRetriever class
  - [ ] Model initialization (multilingual ColBERT preferred)
  - [ ] Late-interaction scoring implementation
  - [ ] Batch encoding for efficiency
  - [ ] Integration with Qdrant/Weaviate
- [ ] **Vector store integration**:
  - [ ] Connect to Qdrant Cloud
  - [ ] Create collection with appropriate dimensions
  - [ ] Implement batch indexing (chunks of 100)
  - [ ] Query interface with similarity search
- [ ] **Optimization**:
  - [ ] Model caching
  - [ ] GPU acceleration if available
  - [ ] Batch processing for multiple queries
- [ ] **Testing**:
  - [ ] Test multilingual document indexing
  - [ ] Test query-document matching
  - [ ] Verify late-interaction scores
  - [ ] Compare with standard dense retrieval

### Task 2.3: Project Structure Setup (1 hour)
- [ ] **Create project directories**:
  ```
  hybrid-rag-system/
  ├── backend/
  │   ├── api/
  │   ├── retrieval/
  │   │   ├── bm25_retriever.py
  │   │   ├── colbert_retriever.py
  │   │   ├── graph_retriever.py
  │   │   └── hybrid_fusion.py
  │   ├── services/
  │   │   ├── llm_service.py
  │   │   ├── entity_extraction.py
  │   │   └── embedding_service.py
  │   ├── storage/
  │   │   ├── neo4j_client.py
  │   │   ├── qdrant_client.py
  │   │   └── redis_cache.py
  │   ├── models/
  │   ├── utils/
  │   └── main.py
  ├── frontend/
  ├── docs/
  ├── tests/
  ├── docker/
  ├── k8s/
  └── README.md
  ```
- [ ] **Setup Python environment**:
  ```bash
  python -m venv venv
  source venv/bin/activate
  pip install fastapi uvicorn pydantic python-dotenv
  ```
- [ ] **Initialize dependencies**:
  - Create `requirements.txt`
  - Create `pyproject.toml` (optional)

---

## Hour 5-6: Frontend UI Development (+ UI Documentation)

### Task 3.1: Setup React + Tailwind (15 min)
- [ ] Configure Tailwind CSS
- [ ] Update `index.css` with Tailwind directives
- [ ] Setup React Query for data fetching

### Task 3.2: Build Simple Chat UI (60 min) - FUNCTIONAL NOT PRETTY
- [ ] **ChatBox.jsx**: Simple chat interface
  - [ ] Text input (supports Arabic RTL automatically)
  - [ ] Send button
  - [ ] Display answers
- [ ] **IngestBox.jsx**: Paste document area
  - [ ] Textarea for Arabic or English documents
  - [ ] "Process" button
  - [ ] Shows "Done" message
- [ ] Skip fancy styling - use basic HTML/CSS
- [ ] Skip language selector - auto-detect is enough

### Task 3.3: Optional Simple Graph View (30 min)
- [ ] Simple list of entities from graph (optional)
- [ ] Or use react-force-graph-2d if time permits
- [ ] Skip if running out of time - chat is more important

---

## Hour 7-8: Integration, Testing & API Documentation

### Task 4.1: Arabic + English Testing (60 min) - CRITICAL
- [ ] Start backend: `python backend/main.py`
- [ ] Start frontend: `npm run dev`
- [ ] **Test Arabic document ingestion**:
  - [ ] Paste Arabic news article
  - [ ] Verify entities extracted correctly
  - [ ] Check Neo4j has Arabic text
- [ ] **Test English document**:
  - [ ] Paste English text
  - [ ] Verify entities extracted
- [ ] **Test Arabic questions**:
  - [ ] Ask in Arabic about the document
  - [ ] Verify answer makes sense
- [ ] **Test English questions**:
  - [ ] Ask in English
  - [ ] Verify answer works

### Task 4.2: Fix Arabic Issues (60 min)
- [ ] Fix UTF-8 encoding if broken
- [ ] Fix RTL display if not working
- [ ] Fix any Arabic-specific bugs
- [ ] Make sure Arabic entities show in graph
- [ ] Make sure answers in Arabic are readable

---

## Hour 9-10: Complete Documentation & Deployment

### Task 5.1: Make Everything Work (60 min)
- [ ] Test full flow: Arabic doc → entities → Arabic question → answer
- [ ] Test full flow: English doc → entities → English question → answer
- [ ] Fix whatever is broken
- [ ] Make UI usable (doesn't need to be pretty)
- [ ] Ensure graph has good quality

### Task 5.2: Basic README (10 min)
- [ ] Write simple README with:
  - [ ] How to run backend
  - [ ] How to run frontend
  - [ ] How to use (paste doc, ask questions)
- [ ] Skip everything else

### Task 5.3: Done When It Works (50 min)
- [ ] Keep testing and fixing
- [ ] Focus on Arabic + English working properly
- [ ] Stop when it's functional
- [ ] Don't waste time on polish

---

## 🎉 Final Checklist

### Implementation Complete When:

**CRITICAL - MUST WORK:**
- [ ] 🇦🇪 **Arabic document ingestion works** - paste Arabic text, entities extracted
- [ ] 🇬🇧 **English document ingestion works** - paste English text, entities extracted
- [ ] 🇦🇪 **Chat with Arabic documents works** - ask in Arabic, get Arabic answers
- [ ] 🇬🇧 **Chat with English documents works** - ask in English, get English answers
- [ ] 📊 **Knowledge graph has good quality** - entities and relationships make sense
- [ ] 💬 **Chat UI is functional** - can type, send, see answers (ugly is OK)

**NICE TO HAVE:**
- [ ] Backend API running on port 8000
- [ ] Frontend UI running on port 5173
- [ ] Neo4j shows entities properly
- [ ] Simple graph visualization (optional)
- [ ] Basic README with run instructions

**NOT NEEDED:**
- ❌ Clean code
- ❌ Beautiful UI
- ❌ Complete documentation
- ❌ Docstrings
- ❌ Tests

---

## ⏱️ Realistic Timeline

**Total Time**: 8-10 hours (1 working day)

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Setup & Docs | 2 hours | Environment ready, initial documentation |
| Backend | 2 hours | API endpoints, services, Neo4j integration |
| Frontend | 2 hours | UI components, graph visualization |
| Integration & Testing | 2 hours | End-to-end testing, API docs |
| Documentation & Polish | 2 hours | Complete all docs, optional deployment |

---

## 🚀 Quick Start Commands

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn langchain langchain-google-genai sentence-transformers neo4j googletrans==4.0.0rc1 langdetect
python main.py  # Runs on http://localhost:8000

# Frontend
cd frontend && npm install
npm install axios @tanstack/react-query lucide-react tailwindcss react-force-graph-2d
npm run dev  # Runs on http://localhost:5173
```

---

## 📅 2025 GraphRAG Best Practices Included

**⭐ Latest Research (Jan 2025): Hybrid RAG performs 35% better**
- Combine vector similarity search + knowledge graph traversal
- Use both for better accuracy (proven in recent studies)

### ✅ What's Included (FOCUS)
- **Arabic document processing** - MUST WORK
- **English document processing** - MUST WORK
- **Arabic chat/questions** - MUST WORK
- **English chat/questions** - MUST WORK
- **Good knowledge graph** - entities + relationships
- **Hybrid retrieval** - vector + graph (2025 best practice)
- **Simple functional UI** - chat box that works
- Neo4j storage
- Gemini for entity extraction
- Auto language detection
- Free services ($0 cost)

### ❌ What's NOT Needed
- Clean code / docstrings / comments
- Beautiful UI / fancy design / animations
- Complete documentation
- Other languages (Spanish, French, etc) - only Arabic + English matter
- Authentication
- Testing suite
- Monitoring
- Production deployment
- Graph algorithms
- Caching

---

## 💡 Tips for Success

1. **Test Arabic EARLY** - Don't wait until the end to test Arabic text
2. **Use real Arabic documents** - News articles, Wikipedia pages in Arabic
3. **Test UTF-8 immediately** - Make sure Python/Node handle Arabic encoding
4. **RTL is usually automatic** - HTML `dir="auto"` handles right-to-left
5. **Gemini supports Arabic** - It works well with Arabic entity extraction
6. **Don't polish** - Stop when it works, don't waste time making it pretty
7. **Skip other languages** - Only Arabic and English matter

---

## 🐛 Common Issues & Quick Fixes

**"Neo4j connection failed"**
- Verify credentials in `.env`
- Check if instance is running (refresh AuraDB console)

**"Gemini API error"**
- Check API key is correct
- Verify you're not hitting rate limits (15 RPM)

**"Translation not working"**
- googletrans can be unstable
- Fallback: Skip translation, use English only for testing

**"Graph not rendering"**
- Check browser console for errors
- Verify backend is returning nodes/links data
- Try with smaller dataset first

**"Arabic text not displaying"**
- Check UTF-8 encoding in all files
- Add `<meta charset="UTF-8">` to HTML
- Ensure database stores UTF-8
- Test with `console.log()` to see if backend sends Arabic correctly

---

## 🎯 Success Criteria (Simple)

**You're done when:**
1. ✅ Arabic document → entities extracted → can chat about it in Arabic
2. ✅ English document → entities extracted → can chat about it in English
3. ✅ Knowledge graph makes sense (good entities/relationships)
4. ✅ UI works (doesn't need to look good)

**Time target:** 8-10 hours

**Don't waste time on:** Clean code, beautiful UI, documentation, other languages

---

## 🎓 Resources

- [Neo4j AuraDB Free](https://neo4j.com/cloud/aura-free/)
- [Google Gemini API](https://aistudio.google.com/)
- [LangChain Docs](https://python.langchain.com/)
- [React Force Graph](https://github.com/vasturiano/react-force-graph)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

---

## 🎯 Critical Summary for Tomorrow's Delivery

### Three Core Deliverables (ALL REQUIRED):

1. **Design Document** (≤10 pages) - See `FINAL_DELIVERABLES_CHECKLIST.md` for template
2. **Working POC Repository** - All Option B components functional
3. **Live Demo + Presentation** - 15-minute walkthrough prepared

### Must-Have Components:
✅ BM25 sparse retrieval  
✅ ColBERT v2 dense retrieval  
✅ Knowledge graph with entity extraction  
✅ RRF fusion algorithm  
✅ Multilingual support (EN, AR, ES)  
✅ Docker + docker-compose  
✅ K8s manifests (deployment, service, health probes)  
✅ Evaluation showing hybrid > single-method  
✅ FastAPI backend with /ingest and /query endpoints  
✅ Structured logging

### Implementation Priority:
1. **Hours 0-4**: Design doc + infrastructure setup (**DO NOT SKIP**)
2. **Hours 4-12**: BM25 + ColBERT + entity extraction (core system)
3. **Hours 12-16**: Graph + RRF + FastAPI (hybrid fusion)
4. **Hours 16-20**: Docker + K8s + basic UI
5. **Hours 20-24**: Evaluation + testing + demo prep

### Quick Start (Right Now):
```bash
# 1. Create design doc from template
# 2. Setup infrastructure
# 3. Follow 24-hour timeline blocks
# 4. Reference FINAL_DELIVERABLES_CHECKLIST.md throughout
```

**⚠️ If behind schedule**: Simplify UI (use Swagger), skip Grafana, focus on working hybrid retrieval + evaluation proof.

---

**Document Version**: 3.0 (Option B - 24-Hour Production Implementation)  
**Last Updated**: 2025-10-20  
**Deadline**: Tomorrow  
**Total Cost**: $0 (free tier services)  
**Focus**: Working POC with all Option B requirements + execution-ready design doc
