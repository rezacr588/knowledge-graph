"""End-to-End Tests for API Endpoints"""

import json
from io import BytesIO

import pytest

from backend.main import app_state, reset_ingested_content
from backend.storage.chunk_store import ChunkStore


@pytest.mark.e2e
class TestHealthEndpoint:
    def test_health_check(self, client):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "uptime_seconds" in data

        api_response = client.get("/api/health")
        assert api_response.status_code == 200
        assert api_response.json()["status"] == data["status"]


@pytest.mark.e2e
class TestIngestEndpoint:
    def test_ingest_document(self, client):
        """Test /ingest endpoint with file upload"""
        file_content = b"Machine learning is a subset of AI."
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        data = {"language": "en"}

        response = client.post("/api/ingest", files=files, data=data)
        assert response.status_code == 200
        result = response.json()
        assert "document_id" in result
        assert "chunks_created" in result

    def test_ingest_invalid_file(self, client):
        """Test /ingest with invalid file"""
        response = client.post("/api/ingest", files={}, data={"language": "en"})
        assert response.status_code == 422  # Validation error

    def test_ingest_persists_chunks_to_disk(self, client, tmp_path):
        """Ingest should write chunk metadata to the configured chunk store."""
        chunk_path = tmp_path / "chunks.json"
        replacement_store = ChunkStore(str(chunk_path))

        previous_store = app_state.get("chunk_store")
        previous_docs = list(app_state.get("documents", []))
        app_state["chunk_store"] = replacement_store
        app_state["persist_ingested_content"] = True

        try:
            reset_ingested_content(force=True)

            file_content = b"Persist this chunk please."
            files = {"file": ("persist.txt", BytesIO(file_content), "text/plain")}
            response = client.post("/api/ingest", files=files, data={"language": "en"})
            assert response.status_code == 200

            assert chunk_path.exists()
            with open(chunk_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)

            assert len(payload) == 1
            chunk_entry = payload[0]
            assert chunk_entry["id"].endswith("_chunk_0")
            assert chunk_entry["text"].startswith("Persist this chunk")
            assert chunk_entry["language"] == "en"
        finally:
            if chunk_path.exists():
                replacement_store.clear()
            app_state["chunk_store"] = previous_store
            app_state["documents"] = previous_docs
            reset_ingested_content(force=True)


@pytest.mark.e2e
class TestQueryEndpoint:
    def test_query_search(self, client):
        """Test /query endpoint"""
        # First ingest a document
        file_content = b"Machine learning is a subset of AI."
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        client.post("/api/ingest", files=files, data={"language": "en"})

        # Then query
        query_data = {
            "query": "What is machine learning?",
            "top_k": 10,
            "language": "en",
        }
        response = client.post("/api/query", json=query_data)
        assert response.status_code == 200
        result = response.json()
        assert "results" in result
        assert "retrieval_time_ms" in result

    def test_query_without_ingestion_returns_error(self, client):
        """Query should fail gracefully when nothing has been indexed."""
        response = client.post(
            "/api/query",
            json={"query": "hello world", "top_k": 5, "language": "en"},
        )
        assert response.status_code == 500
        assert "No documents indexed" in response.json()["detail"]


@pytest.mark.e2e
class TestChunksEndpoint:
    def test_chunks_endpoint_requires_qdrant(self, client):
        """Ensure chunks endpoint returns 503 when Qdrant is not configured."""
        response = client.get("/api/chunks")
        assert response.status_code == 503

    def test_chunks_endpoint_rejects_invalid_limit(self, client):
        """Ensure validation catches invalid pagination arguments."""
        response = client.get("/api/chunks?limit=-5")
        assert response.status_code == 422

    def test_chunks_endpoint_returns_data(self, client):
        """Ensure chunks endpoint surfaces stored chunk metadata."""
        original_dense = app_state.get("dense_retriever")

        class DummyQdrantStore:
            def __init__(self):
                self._chunks = [
                    {
                        "point_id": "1",
                        "doc_id": "doc-1",
                        "text": "Chunk text A",
                        "language": "en",
                        "payload": {"doc_id": "doc-1", "text": "Chunk text A"},
                    },
                    {
                        "point_id": "2",
                        "doc_id": "doc-2",
                        "text": "Chunk text B",
                        "language": "en",
                        "payload": {"doc_id": "doc-2", "text": "Chunk text B"},
                    },
                ]

            def list_chunks_with_info(self, limit=None):
                limit = limit or len(self._chunks)
                return self._chunks[:limit], {"vectors_count": len(self._chunks)}

        class DummyDenseRetriever:
            def __init__(self, store):
                self.use_qdrant = True
                self.qdrant_store = store

        try:
            app_state["dense_retriever"] = DummyDenseRetriever(DummyQdrantStore())

            response = client.get("/api/chunks?limit=2")
            assert response.status_code == 200
            payload = response.json()

            assert payload["total_chunks"] == 2
            assert payload["returned"] == 2
            assert len(payload["chunks"]) == 2
            assert payload["chunks"][0]["doc_id"] == "doc-1"
            assert payload["chunks"][1]["doc_id"] == "doc-2"
        finally:
            app_state["dense_retriever"] = original_dense
