"""End-to-End Tests for API Endpoints"""

import pytest
from io import BytesIO

@pytest.mark.e2e
class TestHealthEndpoint:
    def test_health_check(self, client):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "uptime_seconds" in data

@pytest.mark.e2e
class TestIngestEndpoint:
    def test_ingest_document(self, client):
        """Test /ingest endpoint with file upload"""
        file_content = b"Machine learning is a subset of AI."
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        data = {"language": "en"}
        
        response = client.post("/ingest", files=files, data=data)
        assert response.status_code == 200
        result = response.json()
        assert "doc_id" in result
        assert "chunks_created" in result
    
    def test_ingest_invalid_file(self, client):
        """Test /ingest with invalid file"""
        response = client.post("/ingest", files={}, data={"language": "en"})
        assert response.status_code == 422  # Validation error

@pytest.mark.e2e
class TestQueryEndpoint:
    def test_query_search(self, client):
        """Test /query endpoint"""
        # First ingest a document
        file_content = b"Machine learning is a subset of AI."
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        client.post("/ingest", files=files, data={"language": "en"})
        
        # Then query
        query_data = {
            "query": "What is machine learning?",
            "top_k": 10,
            "language": "en"
        }
        response = client.post("/query", json=query_data)
        assert response.status_code == 200
        result = response.json()
        assert "results" in result
        assert "retrieval_time_ms" in result
