"""
Pytest Configuration and Fixtures
Shared test fixtures for unit, integration, and E2E tests
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from typing import List, Dict

# Set test environment variables
os.environ['NEO4J_URI'] = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
os.environ['NEO4J_USERNAME'] = os.getenv('NEO4J_USERNAME', 'neo4j')
os.environ['NEO4J_PASSWORD'] = os.getenv('NEO4J_PASSWORD', 'password')
os.environ['QDRANT_URL'] = os.getenv('QDRANT_URL', 'http://localhost:6333')
os.environ['QDRANT_API_KEY'] = os.getenv('QDRANT_API_KEY', 'test-key')
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', 'test-key')
os.environ['LOG_LEVEL'] = 'ERROR'  # Reduce log noise in tests


@pytest.fixture(scope="session")
def test_documents() -> List[Dict]:
    """Sample documents for testing"""
    return [
        {
            'id': 'doc1',
            'text': 'Machine learning is a subset of artificial intelligence that focuses on algorithms.',
            'language': 'en',
            'metadata': {'source': 'test'}
        },
        {
            'id': 'doc2',
            'text': 'Deep learning uses neural networks with multiple layers to learn representations.',
            'language': 'en',
            'metadata': {'source': 'test'}
        },
        {
            'id': 'doc3',
            'text': 'Natural language processing enables computers to understand human language.',
            'language': 'en',
            'metadata': {'source': 'test'}
        },
        {
            'id': 'doc4',
            'text': 'El aprendizaje automático es un subcampo de la inteligencia artificial.',
            'language': 'es',
            'metadata': {'source': 'test'}
        },
        {
            'id': 'doc5',
            'text': 'التعلم الآلي هو فرع من فروع الذكاء الاصطناعي.',
            'language': 'ar',
            'metadata': {'source': 'test'}
        }
    ]


@pytest.fixture(scope="session")
def test_queries() -> List[Dict]:
    """Sample queries for testing"""
    return [
        {'query': 'What is machine learning?', 'language': 'en'},
        {'query': 'How does deep learning work?', 'language': 'en'},
        {'query': '¿Qué es el aprendizaje automático?', 'language': 'es'},
        {'query': 'ما هو التعلم الآلي؟', 'language': 'ar'}
    ]


@pytest.fixture
def mock_neo4j_client():
    """Mock Neo4j client for unit tests"""
    mock = MagicMock()
    mock.add_document.return_value = True
    mock.add_chunk.return_value = True
    mock.add_entity.return_value = True
    mock.add_relationship.return_value = True
    mock.search.return_value = []
    mock.close.return_value = None
    return mock


@pytest.fixture
def mock_entity_extractor():
    """Mock entity extractor for unit tests"""
    mock = MagicMock()
    mock.extract_entities.return_value = []
    mock.generate_entity_id.return_value = 'test_entity_id'
    return mock


@pytest.fixture
def sample_entities():
    """Sample extracted entities"""
    from backend.services.entity_extraction import ExtractedEntity
    return [
        ExtractedEntity(
            name='Machine Learning',
            type='CONCEPT',
            language='en',
            confidence=0.9,
            context='Machine learning is a subset of AI'
        ),
        ExtractedEntity(
            name='Neural Networks',
            type='CONCEPT',
            language='en',
            confidence=0.85,
            context='Neural networks are used in deep learning'
        )
    ]


@pytest.fixture(scope="function")
def client():
    """FastAPI test client"""
    from backend.main import app
    return TestClient(app)


@pytest.fixture(scope="function")
def authenticated_client(client):
    """Authenticated test client (if auth is added later)"""
    return client


# Markers for different test types
def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_external: mark test as requiring external services"
    )
