"""Integration Tests for Neo4j Client"""

import pytest
from backend.storage.neo4j_client import Neo4jClient, Entity
import os

@pytest.mark.integration
@pytest.mark.requires_external
class TestNeo4jClient:
    @pytest.fixture
    def neo4j_client(self):
        """Create Neo4j client for testing"""
        uri = os.getenv('NEO4J_URI')
        username = os.getenv('NEO4J_USERNAME')
        password = os.getenv('NEO4J_PASSWORD')

        if not uri or not username or not password:
            pytest.skip("Neo4j credentials not configured.")

        try:
            client = Neo4jClient(uri=uri, username=username, password=password)
        except Exception as exc:  # pragma: no cover - environment specific
            pytest.skip(f"Neo4j not available: {exc}")

        yield client
        client.close()
    
    def test_add_document(self, neo4j_client):
        """Test adding document to graph"""
        doc_id = "test_doc_1"
        success = neo4j_client.add_document(
            doc_id=doc_id,
            title="Test Document",
            language="en"
        )
        assert success is True
    
    def test_add_entity(self, neo4j_client):
        """Test adding entity to graph"""
        entity = Entity(
            id="test_entity_1",
            name="Test Entity",
            type="CONCEPT",
            language="en",
            confidence=0.9,
            metadata={}
        )
        success = neo4j_client.add_entity(entity)
        assert success is True
    
    def test_search(self, neo4j_client):
        """Test graph search"""
        results = neo4j_client.search(
            query="test",
            top_k=10,
            language="en"
        )
        assert isinstance(results, list)
