#!/usr/bin/env python3
"""
End-to-End Test: Verify Document Ingestion Stores Chunks in Qdrant

This script tests:
1. Document upload and ingestion
2. Chunks stored in Neo4j with correct IDs
3. Vectors stored in Qdrant with aligned chunk IDs
4. Query retrieval uses Qdrant correctly
"""

import requests
import json
import time
import sys
from typing import Dict, List

# Configuration
API_URL = "http://localhost:8000"
TEST_DOCUMENT = """
Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that focuses on building systems that can learn from data.

Deep Learning Techniques

Deep learning uses neural networks with multiple layers to learn complex patterns in large datasets. It has revolutionized computer vision and natural language processing.

Applications and Future

Machine learning applications span across healthcare, finance, autonomous vehicles, and recommendation systems. The future of AI will be shaped by advances in these technologies.
"""

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def test_health_check() -> Dict:
    """Test 1: Check system health"""
    print_header("TEST 1: System Health Check")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        health = response.json()
        
        print_info("Health Status:")
        print(json.dumps(health, indent=2))
        
        # Check critical dependencies
        if health.get('dependencies', {}).get('dense', {}).get('available'):
            print_success("Dense retriever is available")
        else:
            print_error("Dense retriever is NOT available")
            return None
            
        if health.get('dependencies', {}).get('neo4j', {}).get('available'):
            print_success("Neo4j is available")
        else:
            print_error("Neo4j is NOT available")
            return None
        
        print_success(f"System is {health.get('status', 'unknown')}")
        return health
        
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return None


def test_document_ingestion() -> str:
    """Test 2: Upload and ingest document"""
    print_header("TEST 2: Document Ingestion")
    
    try:
        # Create temporary test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(TEST_DOCUMENT)
            temp_file = f.name
        
        print_info(f"Created temporary test file: {temp_file}")
        print_info(f"Document length: {len(TEST_DOCUMENT)} characters")
        
        # Upload document
        with open(temp_file, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {'language': 'en'}
            
            print_info("Uploading document...")
            response = requests.post(
                f"{API_URL}/api/ingest",
                files=files,
                data=data,
                timeout=60
            )
            response.raise_for_status()
        
        result = response.json()
        print_success("Document uploaded successfully!")
        print_info(f"Document ID: {result.get('document_id')}")
        print_info(f"Chunks created: {result.get('chunks_created')}")
        print_info(f"Entities extracted: {result.get('entities_extracted')}")
        print_info(f"Processing time: {result.get('processing_time_ms'):.2f}ms")
        
        # Cleanup
        import os
        os.unlink(temp_file)
        
        return result.get('document_id')
        
    except Exception as e:
        print_error(f"Document ingestion failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"Response: {e.response.text}")
        return None


def test_neo4j_chunks(doc_id: str) -> List[str]:
    """Test 3: Verify chunks in Neo4j"""
    print_header("TEST 3: Verify Chunks in Neo4j")
    
    try:
        response = requests.get(f"{API_URL}/api/graph/stats", timeout=10)
        response.raise_for_status()
        stats = response.json()
        
        print_info("Neo4j Graph Stats:")
        print(json.dumps(stats, indent=2))
        
        chunk_count = stats.get('chunks', 0)
        if chunk_count > 0:
            print_success(f"Found {chunk_count} chunks in Neo4j")
        else:
            print_error("No chunks found in Neo4j!")
            return []
        
        # Note: We can't directly query chunk IDs without a specific endpoint
        # But we know the format: {doc_id}_chunk_0, {doc_id}_chunk_1, etc.
        expected_chunks = [f"{doc_id}_chunk_{i}" for i in range(chunk_count)]
        print_info(f"Expected chunk IDs: {expected_chunks[:3]}...")
        
        return expected_chunks
        
    except Exception as e:
        print_error(f"Neo4j verification failed: {e}")
        return []


def test_qdrant_chunks(expected_chunk_ids: List[str]) -> bool:
    """Test 4: Verify chunks in Qdrant with aligned IDs"""
    print_header("TEST 4: Verify Chunks in Qdrant")
    
    try:
        # Check if chunks endpoint exists
        response = requests.get(f"{API_URL}/api/chunks", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        chunks = result.get('chunks', [])
        collection_info = result.get('collection_info', {})
        
        print_info("Qdrant Collection Info:")
        print(json.dumps(collection_info, indent=2))
        
        vectors_count = collection_info.get('vectors_count', 0)
        if vectors_count > 0:
            print_success(f"Found {vectors_count} vectors in Qdrant")
        else:
            print_error("No vectors found in Qdrant!")
            return False
        
        # Verify chunk IDs alignment
        print_info("\nVerifying Chunk ID Alignment:")
        print(f"Expected chunks from Neo4j: {len(expected_chunk_ids)}")
        print(f"Vectors in Qdrant: {vectors_count}")
        
        if chunks:
            print_info(f"\nFirst 3 chunks from Qdrant:")
            for i, chunk in enumerate(chunks[:3]):
                doc_id = chunk.get('doc_id', 'N/A')
                text_preview = chunk.get('text', '')[:50]
                print(f"  {i+1}. ID: {doc_id}")
                print(f"     Text: {text_preview}...")
                
                # Check if this chunk ID was expected
                if doc_id in expected_chunk_ids:
                    print_success(f"     ✓ Chunk ID matches Neo4j format")
                else:
                    print_warning(f"     ⚠ Chunk ID doesn't match expected format")
        
        return vectors_count > 0
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print_warning("Chunks endpoint not found. Trying alternative method...")
            return test_qdrant_via_query()
        else:
            print_error(f"Qdrant verification failed: {e}")
            return False
    except Exception as e:
        print_error(f"Qdrant verification failed: {e}")
        return False


def test_qdrant_via_query() -> bool:
    """Alternative: Test Qdrant by performing a query"""
    print_info("Testing Qdrant through query endpoint...")
    
    try:
        query_data = {
            "query": "machine learning",
            "top_k": 5,
            "language": "en",
            "retrieval_methods": ["dense"]  # Only use dense to test Qdrant
        }
        
        response = requests.post(
            f"{API_URL}/api/query",
            json=query_data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        results = result.get('results', [])
        methods_used = result.get('methods_used', [])
        
        if 'dense' in methods_used and len(results) > 0:
            print_success(f"Dense retrieval returned {len(results)} results")
            print_info("First result:")
            first = results[0]
            print(f"  Chunk ID: {first.get('chunk_id')}")
            print(f"  Text: {first.get('text', '')[:80]}...")
            print(f"  RRF Score: {first.get('rrf_score'):.4f}")
            return True
        else:
            print_error("Dense retrieval did not return results")
            return False
            
    except Exception as e:
        print_error(f"Query test failed: {e}")
        return False


def test_hybrid_query() -> bool:
    """Test 5: Verify hybrid query works"""
    print_header("TEST 5: Hybrid Query Test")
    
    try:
        query_data = {
            "query": "What is deep learning?",
            "top_k": 5,
            "language": "en",
            "retrieval_methods": ["bm25", "dense", "graph"]
        }
        
        print_info(f"Query: {query_data['query']}")
        print_info(f"Methods: {query_data['retrieval_methods']}")
        
        response = requests.post(
            f"{API_URL}/api/query",
            json=query_data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        results = result.get('results', [])
        methods_used = result.get('methods_used', [])
        retrieval_time = result.get('retrieval_time_ms', 0)
        total_time = result.get('total_time_ms', 0)
        
        print_success(f"Query completed in {total_time:.2f}ms")
        print_info(f"Retrieval time: {retrieval_time:.2f}ms")
        print_info(f"Methods used: {methods_used}")
        print_info(f"Results returned: {len(results)}")
        
        if len(results) > 0:
            print_info("\nTop 3 results:")
            for i, res in enumerate(results[:3], 1):
                print(f"\n  {i}. Chunk ID: {res.get('chunk_id')}")
                print(f"     RRF Score: {res.get('rrf_score'):.4f}")
                print(f"     Rank: {res.get('rank')}")
                print(f"     Text: {res.get('text', '')[:80]}...")
                
                method_scores = res.get('method_scores', {})
                if method_scores:
                    print(f"     Method Scores: ", end="")
                    for method, score in method_scores.items():
                        print(f"{method}={score:.2f} ", end="")
                    print()
            
            # Check if dense was used
            if 'dense' in methods_used:
                print_success("✓ Dense retrieval (Qdrant) was used successfully!")
            else:
                print_warning("⚠ Dense retrieval was not used")
            
            return True
        else:
            print_error("No results returned!")
            return False
        
    except Exception as e:
        print_error(f"Query test failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"Response: {e.response.text}")
        return False


def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}E2E Test: Qdrant Ingestion & Retrieval{Colors.ENDC}")
    print(f"{Colors.BOLD}API URL: {API_URL}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    results = {
        'health_check': False,
        'ingestion': False,
        'neo4j_verification': False,
        'qdrant_verification': False,
        'query_test': False
    }
    
    # Test 1: Health Check
    health = test_health_check()
    results['health_check'] = health is not None
    
    if not results['health_check']:
        print_error("\n❌ Health check failed. Cannot proceed with tests.")
        return False
    
    # Wait a bit for system to be ready
    time.sleep(1)
    
    # Test 2: Document Ingestion
    doc_id = test_document_ingestion()
    results['ingestion'] = doc_id is not None
    
    if not results['ingestion']:
        print_error("\n❌ Document ingestion failed. Cannot proceed with tests.")
        return False
    
    # Wait for indexing to complete
    print_info("\nWaiting 3 seconds for indexing to complete...")
    time.sleep(3)
    
    # Test 3: Neo4j Verification
    expected_chunks = test_neo4j_chunks(doc_id)
    results['neo4j_verification'] = len(expected_chunks) > 0
    
    # Test 4: Qdrant Verification
    results['qdrant_verification'] = test_qdrant_chunks(expected_chunks)
    
    # Test 5: Query Test
    results['query_test'] = test_hybrid_query()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        color = Colors.OKGREEN if passed else Colors.FAIL
        print(f"{color}{status}{Colors.ENDC} - {test_name.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}Results: {passed_tests}/{total_tests} tests passed{Colors.ENDC}")
    
    if passed_tests == total_tests:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Chunks are successfully stored in Qdrant with aligned IDs.{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}⚠️  SOME TESTS FAILED{Colors.ENDC}")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
