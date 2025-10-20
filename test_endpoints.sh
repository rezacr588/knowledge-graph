#!/bin/bash
# Comprehensive API Endpoint Testing Script

echo "🧪 Testing Hybrid RAG System API Endpoints"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC} - $2"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} - $2"
        ((FAILED++))
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Testing Health Endpoint (GET /health)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Health endpoint returns 200"
    echo "Response: $BODY" | python3 -m json.tool
    echo ""
else
    print_result 1 "Health endpoint (got $HTTP_CODE)"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Testing Document Ingestion (POST /ingest)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create test document
TEST_DOC="test_api_document.txt"
cat > "$TEST_DOC" << 'EOF'
Artificial Intelligence and Machine Learning

Artificial intelligence (AI) is revolutionizing technology. Machine learning, a subset of AI, enables systems to learn from data without explicit programming.

Deep learning uses neural networks with multiple layers to process complex patterns. Natural language processing (NLP) allows computers to understand human language.

Key applications include:
- Computer Vision: Image and video analysis
- Speech Recognition: Voice assistants and transcription
- Recommendation Systems: Personalized content
- Autonomous Vehicles: Self-driving technology

The future of AI promises even more innovations in healthcare, education, and industry.
EOF

echo "Uploading test document: $TEST_DOC"
INGEST_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ingest" \
  -F "file=@$TEST_DOC" \
  -F "language=en")

HTTP_CODE=$(echo "$INGEST_RESPONSE" | tail -n1)
BODY=$(echo "$INGEST_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Document ingestion returns 200"
    echo "Response: $BODY" | python3 -m json.tool
    DOC_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['document_id'])" 2>/dev/null)
    echo ""
    echo "Document ID: $DOC_ID"
    echo ""
else
    print_result 1 "Document ingestion (got $HTTP_CODE)"
fi

# Wait for indexing
echo "Waiting 2 seconds for indexing..."
sleep 2

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Testing Query Endpoint (POST /query)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test Query 1: Simple query
echo "Test Query 1: 'What is machine learning?'"
QUERY_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 5,
    "language": "en",
    "retrieval_methods": ["bm25", "graph"]
  }')

HTTP_CODE=$(echo "$QUERY_RESPONSE" | tail -n1)
BODY=$(echo "$QUERY_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Query endpoint returns 200"
    echo "Response:"
    echo "$BODY" | python3 -m json.tool | head -30
    
    RESULT_COUNT=$(echo "$BODY" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['results']))" 2>/dev/null)
    echo ""
    echo "Results returned: $RESULT_COUNT"
    echo ""
else
    print_result 1 "Query endpoint (got $HTTP_CODE)"
fi

# Test Query 2: Different query
echo "Test Query 2: 'How does deep learning work?'"
QUERY_RESPONSE2=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does deep learning work?",
    "top_k": 3,
    "language": "en",
    "retrieval_methods": ["bm25", "graph"]
  }')

HTTP_CODE=$(echo "$QUERY_RESPONSE2" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Query with different parameters"
else
    print_result 1 "Query with different parameters (got $HTTP_CODE)"
fi

# Test Query 3: Entity-focused query
echo ""
echo "Test Query 3: 'What are AI applications?'"
QUERY_RESPONSE3=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are AI applications?",
    "top_k": 5,
    "language": "en",
    "retrieval_methods": ["bm25", "graph"]
  }')

HTTP_CODE=$(echo "$QUERY_RESPONSE3" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Entity-focused query"
else
    print_result 1 "Entity-focused query (got $HTTP_CODE)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Testing Error Handling"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test invalid endpoint
echo "Test: Invalid endpoint (GET /invalid)"
INVALID_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/invalid")
HTTP_CODE=$(echo "$INVALID_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "404" ]; then
    print_result 0 "Invalid endpoint returns 404"
else
    print_result 1 "Invalid endpoint (expected 404, got $HTTP_CODE)"
fi

# Test invalid query (missing required fields)
echo "Test: Invalid query (missing required fields)"
INVALID_QUERY=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{}')

HTTP_CODE=$(echo "$INVALID_QUERY" | tail -n1)

if [ "$HTTP_CODE" = "422" ]; then
    print_result 0 "Invalid query returns 422 (validation error)"
else
    print_result 1 "Invalid query (expected 422, got $HTTP_CODE)"
fi

# Test query without indexed documents (if this is first run)
echo "Test: Query with no documents (edge case)"
EMPTY_QUERY=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "nonexistent query for empty database test",
    "top_k": 5,
    "language": "en",
    "retrieval_methods": ["bm25", "graph"]
  }')

HTTP_CODE=$(echo "$EMPTY_QUERY" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Query handles edge cases gracefully"
else
    print_result 1 "Query edge case (got $HTTP_CODE)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Performance Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Running 5 consecutive queries to test performance..."
TOTAL_TIME=0
for i in {1..5}; do
    START=$(date +%s%N)
    curl -s -X POST "$BASE_URL/query" \
      -H "Content-Type: application/json" \
      -d '{
        "query": "machine learning",
        "top_k": 5,
        "language": "en",
        "retrieval_methods": ["bm25", "graph"]
      }' > /dev/null
    END=$(date +%s%N)
    DURATION=$((($END - $START) / 1000000))
    TOTAL_TIME=$(($TOTAL_TIME + $DURATION))
    echo "  Query $i: ${DURATION}ms"
done

AVG_TIME=$(($TOTAL_TIME / 5))
echo ""
echo "Average query time: ${AVG_TIME}ms"

if [ $AVG_TIME -lt 200 ]; then
    print_result 0 "Query performance (avg ${AVG_TIME}ms < 200ms)"
else
    print_result 1 "Query performance (avg ${AVG_TIME}ms >= 200ms)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
TOTAL=$(($PASSED + $FAILED))
echo "Total: $TOTAL"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}"
    exit 1
fi

# Cleanup
rm -f "$TEST_DOC"
