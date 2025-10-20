# Complete Implementation Reference for Another LLM

> **Purpose**: This document contains ALL technical details, citations, formulas, and complete code examples needed to implement Option B from scratch with zero ambiguity.

---

## 📚 Complete Citations & References

### Core Papers

1. **BM25 Algorithm**
   - Robertson, S. E., Walker, S., Jones, S., Hancock-Beaulieu, M. M., & Gatford, M. (1995). "Okapi at TREC-3". NIST Special Publication 500-225, pp. 109-126.
   - Robertson, S. E., & Zaragoza, H. (2009). "The Probabilistic Relevance Framework: BM25 and Beyond". Foundations and Trends in Information Retrieval, 3(4), 333-389.

2. **ColBERT**
   - Khattab, O., & Zaharia, M. (2020). "ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT". SIGIR'20.
   - Santhanam, K., Khattab, O., Saad-Falcon, J., Potts, C., & Zaharia, M. (2022). "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction". NAACL 2022.
   - ArXiv: https://arxiv.org/abs/2112.01488

3. **Reciprocal Rank Fusion**
   - Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009). "Reciprocal rank fusion outperforms condorcet and individual rank learning methods". SIGIR '09, pp. 758-759.
   - Formula: RRFscore(d) = Σ_{r∈R} 1/(k + r(d)) where k is typically 60

4. **Knowledge Graphs for RAG**
   - Edge, D., et al. (2024). "From Local to Global: A Graph RAG Approach to Query-Focused Summarization". Microsoft Research.
   - ArXiv: https://arxiv.org/abs/2404.16130

### Model Cards & Documentation

1. **ColBERTv2 Model**
   - Model: `colbert-ir/colbertv2.0`
   - Hugging Face: https://huggingface.co/colbert-ir/colbertv2.0
   - Parameters: 110M
   - Embedding Dimension: 128 per token
   - Max Sequence Length: 512 tokens

2. **Multilingual Embeddings**
   - Primary: `intfloat/e5-mistral-7b-instruct`
   - HF: https://huggingface.co/intfloat/e5-mistral-7b-instruct
   - Dimensions: 4096
   - Languages: 100+
   - Alternative: `BAAI/bge-m3` (8192 dims)

3. **spaCy Models**
   - English: `en_core_web_sm` (12MB)
   - Spanish: `es_core_news_sm` (12MB)
   - Multilingual: `xx_ent_wiki_sm` (12MB)
   - Documentation: https://spacy.io/models

---

## 🔢 Complete Mathematical Formulas

### 1. BM25 Scoring (Full Derivation)

```
Given:
- D: Document
- Q: Query = {q1, q2, ..., qn}
- C: Collection of all documents

BM25(D, Q) = Σ_{i=1}^{n} IDF(qi) × TF(qi, D)

where:

IDF(qi) = log((N - df(qi) + 0.5) / (df(qi) + 0.5) + 1)
    N = total number of documents in collection
    df(qi) = document frequency of term qi

TF(qi, D) = (f(qi, D) × (k1 + 1)) / (f(qi, D) + k1 × (1 - b + b × (|D| / avgdl)))
    f(qi, D) = raw frequency of term qi in document D
    |D| = length of document D (in terms)
    avgdl = average document length in collection
    k1 = term frequency saturation parameter (default: 1.5)
    b = length normalization parameter (default: 0.75)

Parameters Rationale:
- k1 = 1.5: Allows TF to saturate (diminishing returns for repeated terms)
- b = 0.75: Balances between no length normalization (b=0) and full (b=1)
```

### 2. ColBERT MaxSim Scoring (Full Derivation)

```
Given:
- Q = {q1, q2, ..., qm}: Query tokens
- D = {d1, d2, ..., dn}: Document tokens
- E_q: BERT embedding of query token q
- E_d: BERT embedding of document token d

MaxSim(Q, D) = Σ_{i=1}^{m} max_{j=1}^{n} sim(E_qi, E_dj)

where:
sim(E_qi, E_dj) = E_qi · E_dj / (||E_qi|| × ||E_dj||)  # Cosine similarity
                = E_qi · E_dj  # If vectors are L2-normalized

Late-Interaction Mechanism:
1. Encode query: Each query token → 128-dim embedding
2. Encode document: Each document token → 128-dim embedding
3. For each query token:
   - Compute similarity with ALL document tokens
   - Take maximum similarity
4. Sum all maximum similarities

Time Complexity: O(|Q| × |D| × d) where d=128
Space Complexity: O(|Q| × d + |D| × d)

Advantages over bi-encoder:
- Fine-grained token matching
- Better for multi-lingual and technical documents
- ~15-20% improvement in NDCG@10
```

### 3. Reciprocal Rank Fusion (Full Algorithm)

```
Given:
- R = {R1, R2, ..., Rm}: m ranked lists of documents
- Ri = [doc_id1, doc_id2, ...]: Ranked list from retrieval method i
- k: Constant (typically 60)

For each document d in any ranked list:
    RRFscore(d) = Σ_{i=1}^{m} 1 / (k + rank_i(d))
    
where:
    rank_i(d) = position of document d in list Ri (1-indexed)
              = ∞ if d not in Ri (contributes 0 to sum)

Final ranking: Sort all documents by RRFscore (descending)

Example:
    R1 (BM25):    [doc_a(rank=1), doc_b(rank=2), doc_c(rank=3)]
    R2 (ColBERT): [doc_b(rank=1), doc_c(rank=2), doc_d(rank=3)]
    R3 (Graph):   [doc_c(rank=1), doc_a(rank=2), doc_d(rank=4)]
    
    RRFscore(doc_a) = 1/(60+1) + 0        + 1/(60+2) = 0.0328
    RRFscore(doc_b) = 1/(60+2) + 1/(60+1) + 0        = 0.0325
    RRFscore(doc_c) = 1/(60+3) + 1/(60+2) + 1/(60+1) = 0.0486  ← Winner
    RRFscore(doc_d) = 0        + 1/(60+3) + 1/(60+4) = 0.0314

Why k=60?
- Empirically optimal across many datasets (Cormack et al., 2009)
- Balances between top-ranked and lower-ranked documents
- Too small k → only top results matter
- Too large k → all ranks weighted equally
```

### 4. Graph Scoring (Distance-based)

```
Given:
- Q: Query
- E_Q = {e1, e2, ..., en}: Entities extracted from query
- G: Knowledge graph
- d: Document node
- path(ei, d): Shortest path from entity ei to document d

GraphScore(d, Q) = Σ_{i=1}^{n} confidence(ei) / (1 + distance(ei, d))

where:
    confidence(ei) = NER confidence × LLM confidence
    distance(ei, d) = length of shortest path from ei to d
                    = ∞ if no path exists

Normalization:
    GraphScore_norm(d, Q) = GraphScore(d, Q) / max_{d'} GraphScore(d', Q)

Time Complexity: O(|E_Q| × |V| × log|V|) using Dijkstra
Space Complexity: O(|V| + |E|) for graph storage
```

---

## 💻 Complete Code Implementations

### Neo4j Graph Client (Complete Implementation)

**File: `backend/storage/neo4j_client.py`**

```python
"""
Neo4j Graph Database Client
Handles entity storage, relationship management, and graph traversal
"""

from neo4j import GraphDatabase, Query
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Entity:
    """Entity node in knowledge graph"""
    id: str
    name: str
    type: str  # PERSON, ORGANIZATION, LOCATION, CONCEPT, etc.
    language: str
    confidence: float
    metadata: Dict

@dataclass
class Relationship:
    """Relationship edge in knowledge graph"""
    source_id: str
    target_id: str
    type: str  # RELATED_TO, PART_OF, LOCATED_IN, etc.
    confidence: float
    metadata: Dict

class Neo4jClient:
    """
    Neo4j client for knowledge graph operations
    
    Graph Schema:
        (:Document {id, title, language, content_hash})
        (:Chunk {id, text, language, embedding_id, doc_id})
        (:Entity {id, name, type, language, confidence})
        
        (Document)-[:CONTAINS]->(Chunk)
        (Chunk)-[:MENTIONS {confidence}]->(Entity)
        (Entity)-[:RELATES_TO {type, confidence}]->(Entity)
        (Entity)-[:SAME_AS {confidence}]->(Entity)  # Cross-language linking
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize Neo4j client
        
        Args:
            uri: Neo4j connection URI (e.g., neo4j+s://abc.databases.neo4j.io)
            username: Neo4j username (typically 'neo4j')
            password: Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info(f"Connected to Neo4j at {uri}")
        
        # Create constraints and indexes
        self._setup_schema()
    
    def _setup_schema(self):
        """Create constraints and indexes for optimal performance"""
        constraints = [
            # Unique constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            
            # Indexes for fast lookups
            "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.language)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Chunk) ON (c.doc_id)",
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created: {constraint[:50]}...")
                except Exception as e:
                    logger.warning(f"Constraint/index already exists or error: {e}")
    
    def add_document(
        self,
        doc_id: str,
        title: str,
        language: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add document node to graph
        
        Args:
            doc_id: Unique document identifier
            title: Document title
            language: Document language code
            metadata: Additional metadata
        """
        query = """
        MERGE (d:Document {id: $doc_id})
        SET d.title = $title,
            d.language = $language,
            d.metadata = $metadata,
            d.created_at = datetime()
        RETURN d
        """
        
        with self.driver.session() as session:
            session.run(
                query,
                doc_id=doc_id,
                title=title,
                language=language,
                metadata=metadata or {}
            )
        
        logger.info(f"Added document: {doc_id}")
    
    def add_chunk(
        self,
        chunk_id: str,
        doc_id: str,
        text: str,
        language: str,
        embedding_id: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add chunk node and link to document
        
        Args:
            chunk_id: Unique chunk identifier
            doc_id: Parent document ID
            text: Chunk text content
            language: Chunk language
            embedding_id: Vector embedding identifier
            metadata: Additional metadata (e.g., page number, section)
        """
        query = """
        MATCH (d:Document {id: $doc_id})
        MERGE (c:Chunk {id: $chunk_id})
        SET c.text = $text,
            c.language = $language,
            c.embedding_id = $embedding_id,
            c.doc_id = $doc_id,
            c.metadata = $metadata
        MERGE (d)-[:CONTAINS]->(c)
        RETURN c
        """
        
        with self.driver.session() as session:
            session.run(
                query,
                chunk_id=chunk_id,
                doc_id=doc_id,
                text=text,
                language=language,
                embedding_id=embedding_id,
                metadata=metadata or {}
            )
        
        logger.debug(f"Added chunk: {chunk_id} to document: {doc_id}")
    
    def add_entity(self, entity: Entity) -> None:
        """
        Add or update entity node
        
        Args:
            entity: Entity object
        """
        query = """
        MERGE (e:Entity {id: $id})
        SET e.name = $name,
            e.type = $type,
            e.language = $language,
            e.confidence = $confidence,
            e.metadata = $metadata,
            e.updated_at = datetime()
        RETURN e
        """
        
        with self.driver.session() as session:
            session.run(
                query,
                id=entity.id,
                name=entity.name,
                type=entity.type,
                language=entity.language,
                confidence=entity.confidence,
                metadata=entity.metadata
            )
    
    def link_chunk_to_entity(
        self,
        chunk_id: str,
        entity_id: str,
        confidence: float
    ) -> None:
        """
        Create MENTIONS relationship between chunk and entity
        
        Args:
            chunk_id: Chunk identifier
            entity_id: Entity identifier
            confidence: Mention confidence score
        """
        query = """
        MATCH (c:Chunk {id: $chunk_id})
        MATCH (e:Entity {id: $entity_id})
        MERGE (c)-[m:MENTIONS]->(e)
        SET m.confidence = $confidence
        RETURN c, m, e
        """
        
        with self.driver.session() as session:
            session.run(
                query,
                chunk_id=chunk_id,
                entity_id=entity_id,
                confidence=confidence
            )
    
    def add_relationship(self, relationship: Relationship) -> None:
        """
        Create relationship between two entities
        
        Args:
            relationship: Relationship object
        """
        query = """
        MATCH (e1:Entity {id: $source_id})
        MATCH (e2:Entity {id: $target_id})
        MERGE (e1)-[r:RELATES_TO {type: $rel_type}]->(e2)
        SET r.confidence = $confidence,
            r.metadata = $metadata
        RETURN r
        """
        
        with self.driver.session() as session:
            session.run(
                query,
                source_id=relationship.source_id,
                target_id=relationship.target_id,
                rel_type=relationship.type,
                confidence=relationship.confidence,
                metadata=relationship.metadata
            )
    
    def find_entities_by_name(
        self,
        name: str,
        language: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find entities by name (fuzzy match)
        
        Args:
            name: Entity name to search
            language: Optional language filter
            limit: Maximum number of results
        
        Returns:
            List of entity dictionaries
        """
        if language:
            query = """
            MATCH (e:Entity)
            WHERE e.name CONTAINS $name AND e.language = $language
            RETURN e
            ORDER BY e.confidence DESC
            LIMIT $limit
            """
            params = {"name": name, "language": language, "limit": limit}
        else:
            query = """
            MATCH (e:Entity)
            WHERE e.name CONTAINS $name
            RETURN e
            ORDER BY e.confidence DESC
            LIMIT $limit
            """
            params = {"name": name, "limit": limit}
        
        with self.driver.session() as session:
            result = session.run(query, **params)
            return [dict(record["e"]) for record in result]
    
    def get_entity_subgraph(
        self,
        entity_ids: List[str],
        max_depth: int = 2
    ) -> Dict:
        """
        Retrieve subgraph around given entities
        
        Args:
            entity_ids: List of entity IDs to start from
            max_depth: Maximum traversal depth (1 or 2 hops)
        
        Returns:
            Dictionary with nodes and relationships
        """
        query = f"""
        MATCH path = (start:Entity)-[*1..{max_depth}]-(connected)
        WHERE start.id IN $entity_ids
        WITH path, nodes(path) as nodes, relationships(path) as rels
        UNWIND nodes as node
        WITH collect(DISTINCT node) as all_nodes, collect(DISTINCT rels) as all_rels
        RETURN all_nodes, all_rels
        """
        
        with self.driver.session() as session:
            result = session.run(query, entity_ids=entity_ids)
            record = result.single()
            
            if not record:
                return {"nodes": [], "relationships": []}
            
            nodes = [dict(node) for node in record["all_nodes"]]
            rels = [dict(rel) for rel_list in record["all_rels"] for rel in rel_list]
            
            return {"nodes": nodes, "relationships": rels}
    
    def find_chunks_by_entities(
        self,
        entity_ids: List[str],
        top_k: int = 10
    ) -> List[Dict]:
        """
        Find chunks that mention given entities
        
        Args:
            entity_ids: List of entity IDs
            top_k: Maximum number of chunks to return
        
        Returns:
            List of chunk dictionaries with scores
        """
        query = """
        MATCH (c:Chunk)-[m:MENTIONS]->(e:Entity)
        WHERE e.id IN $entity_ids
        WITH c, sum(m.confidence * e.confidence) as score
        ORDER BY score DESC
        LIMIT $top_k
        RETURN c, score
        """
        
        with self.driver.session() as session:
            result = session.run(query, entity_ids=entity_ids, top_k=top_k)
            return [
                {**dict(record["c"]), "score": record["score"]}
                for record in result
            ]
    
    def close(self):
        """Close Neo4j driver connection"""
        self.driver.close()
        logger.info("Neo4j connection closed")


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize client
    client = Neo4jClient(
        uri=os.getenv('NEO4J_URI'),
        username=os.getenv('NEO4J_USERNAME'),
        password=os.getenv('NEO4J_PASSWORD')
    )
    
    # Add document
    client.add_document(
        doc_id="doc1",
        title="ColBERT Research Paper",
        language="en"
    )
    
    # Add entity
    entity = Entity(
        id="e1",
        name="ColBERT",
        type="CONCEPT",
        language="en",
        confidence=0.95,
        metadata={"domain": "information_retrieval"}
    )
    client.add_entity(entity)
    
    # Search entities
    results = client.find_entities_by_name("ColBERT", language="en")
    print(f"Found {len(results)} entities")
    
    client.close()
```

---

## 🔧 Environment Setup (Complete Commands)

```bash
#!/bin/bash
# Complete setup script - run this first

set -e  # Exit on error

echo "🚀 Setting up Hybrid RAG System..."

# 1. Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
if [ "$(printf '%s\n' "3.11" "$python_version" | sort -V | head -n1)" != "3.11" ]; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install dependencies (in correct order to avoid conflicts)
echo "📦 Installing core dependencies..."
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.5.0

echo "📦 Installing retrieval libraries..."
pip install rank-bm25==0.2.2 ragatouille==0.0.8

echo "📦 Installing database clients..."
pip install qdrant-client==1.7.0 neo4j==5.14.0 redis==5.0.1

echo "📦 Installing AI/ML libraries..."
pip install google-generativeai==0.3.2 langchain==0.1.0
pip install sentence-transformers==2.2.2 spacy==3.7.2 nltk==3.8.1

echo "📦 Installing utilities..."
pip install python-dotenv==1.0.0 loguru==0.7.2 celery==5.3.4
pip install prometheus-client==0.19.0 opentelemetry-api==1.21.0

# 5. Download NLP models
echo "📥 Downloading spaCy models..."
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download xx_ent_wiki_sm

echo "📥 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# 6. Create project structure
echo "📁 Creating project structure..."
mkdir -p backend/{retrieval,services,storage,models,utils,api}
mkdir -p frontend/src/{components,hooks,utils}
mkdir -p k8s/{base,overlays/{dev,prod}}
mkdir -p evaluation/{data,scripts,results}
mkdir -p docs tests

# 7. Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file - PLEASE FILL IN YOUR CREDENTIALS!"
fi

# 8. Verify installation
echo "🔍 Verifying installation..."
python -c "import fastapi, uvicorn, rank_bm25, ragatouille; print('✅ All imports successful')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Follow GRAPHRAG_MULTILINGUAL_PIPELINE_TASKS.md"
echo "3. Start with Day 1: Design Document"
```

---

## 📖 Complete API Specification (OpenAPI 3.1.0)

```yaml
openapi: 3.1.0
info:
  title: Hybrid RAG System API
  version: 1.0.0
  description: |
    Production-grade Hybrid Retrieval-Augmented Generation system combining:
    - BM25 sparse retrieval
    - ColBERT dense retrieval
    - Knowledge graph traversal
    - Reciprocal Rank Fusion

servers:
  - url: http://localhost:8000
    description: Local development
  - url: https://api.hybrid-rag.example.com
    description: Production

paths:
  /ingest:
    post:
      summary: Ingest document into system
      description: |
        Processes document through full pipeline:
        1. Extract text and chunk semantically
        2. Extract entities and relationships (LLM + spaCy)
        3. Generate ColBERT embeddings
        4. Build BM25 index
        5. Populate knowledge graph
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required:
                - file
              properties:
                file:
                  type: string
                  format: binary
                  description: Document file (PDF, DOCX, TXT)
                language:
                  type: string
                  enum: [en, ar, es]
                  description: Document language (auto-detected if not provided)
                metadata:
                  type: object
                  additionalProperties: true
      responses:
        '200':
          description: Document successfully ingested
          content:
            application/json:
              schema:
                type: object
                properties:
                  document_id:
                    type: string
                  chunks_created:
                    type: integer
                  entities_extracted:
                    type: integer
                  relationships_found:
                    type: integer
                  processing_time_ms:
                    type: number
  
  /query:
    post:
      summary: Hybrid search query
      description: |
        Executes hybrid retrieval:
        1. BM25 sparse search → top-K
        2. ColBERT dense search → top-K
        3. Graph entity-based search → top-K
        4. Fuse with RRF → final ranking
        5. Optional: Generate answer with LLM
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - query
              properties:
                query:
                  type: string
                  description: User query
                top_k:
                  type: integer
                  default: 10
                  minimum: 1
                  maximum: 100
                language:
                  type: string
                  enum: [en, ar, es]
                include_answer:
                  type: boolean
                  default: false
                  description: Generate LLM answer
                retrieval_methods:
                  type: array
                  items:
                    type: string
                    enum: [bm25, colbert, graph]
                  default: [bm25, colbert, graph]
                rrf_k:
                  type: number
                  default: 60
                  description: RRF k parameter
      responses:
        '200':
          description: Query results
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        doc_id:
                          type: string
                        chunk_id:
                          type: string
                        text:
                          type: string
                        rrf_score:
                          type: number
                        rank:
                          type: integer
                        method_scores:
                          type: object
                          properties:
                            bm25:
                              type: number
                            colbert:
                              type: number
                            graph:
                              type: number
                  answer:
                    type: string
                    nullable: true
                  retrieval_time_ms:
                    type: number
                  fusion_time_ms:
                    type: number
  
  /health:
    get:
      summary: Health check
      responses:
        '200':
          description: System healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [healthy, degraded, unhealthy]
                  dependencies:
                    type: object
                    properties:
                      neo4j:
                        type: boolean
                      qdrant:
                        type: boolean
                      redis:
                        type: boolean
                  uptime_seconds:
                    type: number
```

---

## 🎓 Troubleshooting Guide (Complete)

### Issue: "ragatouille installation fails"
**Solution**:
```bash
# Install from source if pip fails
git clone https://github.com/bclavie/RAGatouille.git
cd RAGatouille
pip install -e .
```

### Issue: "Neo4j connection timeout"
**Solution**:
1. Check URI format: `neo4j+s://` for AuraDB
2. Verify firewall allows port 7687
3. Test with:
```python
from neo4j import GraphDatabase
driver = GraphDatabase.driver(uri, auth=(user, password))
driver.verify_connectivity()
```

### Issue: "Arabic text displays as boxes"
**Solution**:
1. Ensure UTF-8 encoding:
```python
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()
```
2. Check terminal/IDE supports Arabic fonts
3. Database collation: Use `utf8mb4` for MySQL, UTF-8 for PostgreSQL

### Issue: "ColBERT runs out of memory"
**Solution**:
1. Reduce `max_document_length`:
```python
model.index(..., max_document_length=128)
```
2. Use smaller batch sizes
3. Enable gradient checkpointing

### Issue: "BM25 scores all zero"
**Solution**:
1. Check documents are indexed:
```python
assert retriever.bm25 is not None
assert len(retriever.documents) > 0
```
2. Verify query tokenization produces tokens
3. Check stopword removal isn't too aggressive

---

This document provides COMPLETE implementation details. Refer to it alongside the main task files for zero-ambiguity implementation.
