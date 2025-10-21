# E2E Testing Instructions 🧪

## Quick Test Guide

### Prerequisites

1. **Backend must be running** on `http://localhost:8000`
2. **Environment variables** configured (`.env` file)
3. **Qdrant credentials** set up
4. **Neo4j credentials** set up

---

## Option 1: Start Backend First

### Using Docker Compose (Recommended)

```bash
# Start all services
cd /Users/rezazeraat/Desktop/KnowledgeGraph
docker-compose up -d

# Check if backend is ready
curl http://localhost:8000/health

# Wait for services to be healthy (may take 30-60 seconds)
```

### Using Local Development

```bash
# Activate virtual environment
cd /Users/rezazeraat/Desktop/KnowledgeGraph
source venv/bin/activate  # or source .venv/bin/activate

# Install dependencies if needed
pip install -r requirements.txt

# Start backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## Option 2: Run E2E Test

Once the backend is running:

```bash
# Make test executable
chmod +x test_e2e_qdrant_ingestion.py

# Run the test
python test_e2e_qdrant_ingestion.py
```

### Expected Output

```
================================================================================
E2E Test: Qdrant Ingestion & Retrieval
API URL: http://localhost:8000
================================================================================

================================================================================
                          TEST 1: System Health Check                           
================================================================================

ℹ Health Status:
{
  "status": "healthy",
  "dependencies": {
    "neo4j": {"available": true},
    "bm25": {"available": true},
    "dense": {"available": true},
    "entity_extractor": {"available": true}
  }
}
✓ Dense retriever is available
✓ Neo4j is available
✓ System is healthy

================================================================================
                          TEST 2: Document Ingestion                            
================================================================================

ℹ Created temporary test file: /tmp/tmpXXXXX.txt
ℹ Document length: 428 characters
ℹ Uploading document...
✓ Document uploaded successfully!
ℹ Document ID: abc123def456
ℹ Chunks created: 3
ℹ Entities extracted: 8
ℹ Processing time: 2340.50ms

================================================================================
                          TEST 3: Verify Chunks in Neo4j                        
================================================================================

ℹ Neo4j Graph Stats:
{
  "documents": 1,
  "chunks": 3,
  "entities": 8,
  "relationships": 15
}
✓ Found 3 chunks in Neo4j
ℹ Expected chunk IDs: ['abc123def456_chunk_0', 'abc123def456_chunk_1', 'abc123def456_chunk_2']...

================================================================================
                          TEST 4: Verify Chunks in Qdrant                       
================================================================================

ℹ Qdrant Collection Info:
{
  "name": "documents",
  "vectors_count": 3,
  "vector_size": 384,
  "status": "green"
}
✓ Found 3 vectors in Qdrant

ℹ Verifying Chunk ID Alignment:
Expected chunks from Neo4j: 3
Vectors in Qdrant: 3

ℹ First 3 chunks from Qdrant:
  1. ID: abc123def456_chunk_0
     Text: Machine Learning Fundamentals

Machine learning is...
     ✓ Chunk ID matches Neo4j format
  2. ID: abc123def456_chunk_1
     Text: Deep Learning Techniques

Deep learning uses neur...
     ✓ Chunk ID matches Neo4j format
  3. ID: abc123def456_chunk_2
     Text: Applications and Future

Machine learning applic...
     ✓ Chunk ID matches Neo4j format

================================================================================
                          TEST 5: Hybrid Query Test                             
================================================================================

ℹ Query: What is deep learning?
ℹ Methods: ['bm25', 'dense', 'graph']
✓ Query completed in 245.32ms
ℹ Retrieval time: 230.15ms
ℹ Methods used: ['bm25', 'dense', 'graph']
ℹ Results returned: 3

Top 3 results:

  1. Chunk ID: abc123def456_chunk_1
     RRF Score: 0.0486
     Rank: 1
     Text: Deep Learning Techniques

Deep learning uses neural networks with multiple...
     Method Scores: bm25=18.50 dense=0.92 graph=0.85 

  2. Chunk ID: abc123def456_chunk_0
     RRF Score: 0.0420
     Rank: 2
     Text: Machine Learning Fundamentals

Machine learning is a subset of artificial...
     Method Scores: bm25=12.30 dense=0.88 graph=0.70 

  3. Chunk ID: abc123def456_chunk_2
     RRF Score: 0.0325
     Rank: 3
     Text: Applications and Future

Machine learning applications span across...
     Method Scores: bm25=8.20 dense=0.75 graph=0.60 

✓ Dense retrieval (Qdrant) was used successfully!

================================================================================
                                TEST SUMMARY                                    
================================================================================

✓ PASS - Health Check
✓ PASS - Ingestion
✓ PASS - Neo4j Verification
✓ PASS - Qdrant Verification
✓ PASS - Query Test

Results: 5/5 tests passed

🎉 ALL TESTS PASSED!
Chunks are successfully stored in Qdrant with aligned IDs.
```

---

## Manual Testing Alternative

If you prefer to test manually:

### 1. Check Health

```bash
curl http://localhost:8000/health | jq
```

### 2. Upload Document

```bash
cat > test_doc.txt << 'EOF'
Machine learning is a powerful technology that enables computers to learn from data.
Deep learning uses neural networks to process complex patterns.
EOF

curl -X POST http://localhost:8000/api/ingest \
  -F "file=@test_doc.txt" \
  -F "language=en" | jq
```

### 3. Check Qdrant Storage

```bash
# If chunks endpoint is available
curl http://localhost:8000/api/chunks | jq

# Check collection info
curl http://localhost:8000/api/chunks | jq '.collection_info'

# Check chunk IDs
curl http://localhost:8000/api/chunks | jq '.chunks[].doc_id'
```

### 4. Query with Dense Retrieval

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "top_k": 5,
    "retrieval_methods": ["dense"]
  }' | jq
```

### 5. Verify Results

Check that:
- ✅ `methods_used` includes `"dense"`
- ✅ Results are returned with chunk IDs
- ✅ Chunk IDs match format: `{doc_id}_chunk_{index}`

---

## Troubleshooting

### Backend Not Running

```bash
# Check if port 8000 is in use
lsof -i :8000

# Check Docker containers
docker ps

# View backend logs
docker-compose logs backend -f
```

### Qdrant Not Available

```bash
# Check health endpoint
curl http://localhost:8000/health | jq '.dependencies.dense'

# Should show:
# {
#   "available": true
# }

# If false, check environment variables
cat .env | grep QDRANT
```

### No Results from Dense Retrieval

1. Check Qdrant credentials in `.env`
2. Verify ingestion completed successfully
3. Check backend logs for errors
4. Try re-ingesting a document

---

## What the Test Validates

### ✅ End-to-End Flow

1. **Document Ingestion**
   - Document is parsed and chunked
   - Chunks stored in Neo4j with IDs like `doc123_chunk_0`
   - Same chunks sent to Dense Retriever

2. **Qdrant Storage**
   - Dense Retriever generates 384-dim embeddings
   - Vectors stored in Qdrant with chunk IDs in payload
   - Point IDs are deterministic hashes of chunk IDs

3. **ID Alignment**
   - Neo4j chunk IDs: `abc123_chunk_0`
   - Qdrant payload doc_id: `abc123_chunk_0`
   - **Perfect 1:1 mapping** ✅

4. **Query Retrieval**
   - Dense retriever searches Qdrant by vector similarity
   - Returns results with aligned chunk IDs
   - Hybrid fusion combines with BM25 and Graph results

5. **Data Consistency**
   - Same chunk ID can be used to query Neo4j or Qdrant
   - Results from dense retrieval reference valid Neo4j chunks
   - No orphaned vectors or missing chunks

---

## Success Criteria

The test passes when:

- [x] Health check shows dense retriever available
- [x] Document ingestion completes without errors
- [x] Neo4j contains chunks with expected IDs
- [x] Qdrant contains vectors with matching doc_ids
- [x] Hybrid query uses dense retrieval successfully
- [x] All chunk IDs are aligned across systems

---

## Next Steps After Test Passes

1. ✅ **Verified**: Chunks are stored in Qdrant
2. ✅ **Verified**: Chunk IDs are aligned with Neo4j
3. ✅ **Verified**: Dense retrieval works end-to-end
4. ✅ **Ready**: System is production-ready

You can now:
- Upload real documents
- Run production queries
- Deploy to production
- Monitor with confidence

---

**Test Script**: `test_e2e_qdrant_ingestion.py`  
**Status**: Ready to run when backend is available
