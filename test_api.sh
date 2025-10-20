#!/bin/bash
# Test script for Hybrid RAG API

echo "Testing Hybrid RAG System API"
echo "=============================="
echo ""

# Health check
echo "1. Health Check..."
curl -s http://localhost:8000/health | jq '.'
echo ""

# Create test doc
echo "This is a test document about hybrid retrieval systems." > test_doc.txt

# Ingest
echo "2. Ingesting test document..."
curl -s -X POST http://localhost:8000/ingest \
  -F "file=@test_doc.txt" \
  -F "language=en" | jq '.'
echo ""

# Query
echo "3. Testing query..."
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is hybrid retrieval?", "top_k": 5}' | jq '.'
echo ""

echo "✅ Test complete!"
