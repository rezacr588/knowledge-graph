"""
Unit Tests for Dense Retriever
Tests dense retrieval using sentence transformers
"""

import pytest
import numpy as np
from backend.retrieval.dense_retriever import DenseRetriever, DenseResult


@pytest.mark.unit
class TestDenseRetriever:
    """Test dense retrieval functionality"""
    
    def test_initialization(self):
        """Test dense retriever initialization"""
        retriever = DenseRetriever(model_name='all-MiniLM-L6-v2')
        assert retriever.model_name == 'all-MiniLM-L6-v2'
        assert retriever.indexed is False
        assert retriever.embeddings is None
        assert len(retriever.documents) == 0
    
    def test_index_documents(self, test_documents):
        """Test indexing documents"""
        retriever = DenseRetriever(model_name='all-MiniLM-L6-v2')
        retriever.index_documents(test_documents[:3])
        
        assert retriever.indexed is True
        assert retriever.embeddings is not None
        assert len(retriever.documents) == 3
        assert retriever.embeddings.shape[0] == 3
        assert retriever.embeddings.shape[1] == 384  # all-MiniLM-L6-v2 dimension
    
    def test_index_empty_documents(self):
        """Test indexing with empty document list"""
        retriever = DenseRetriever()
        retriever.index_documents([])
        
        assert retriever.indexed is False
        assert retriever.embeddings is None
    
    def test_search_basic(self, test_documents):
        """Test basic search functionality"""
        retriever = DenseRetriever()
        retriever.index_documents(test_documents[:3])
        
        results = retriever.search(query="machine learning", top_k=2)
        
        assert isinstance(results, list)
        assert len(results) <= 2
        assert all(isinstance(r, DenseResult) for r in results)
    
    def test_search_returns_scores(self, test_documents):
        """Test that search returns proper cosine similarity scores"""
        retriever = DenseRetriever()
        retriever.index_documents(test_documents[:3])
        
        results = retriever.search(query="machine learning", top_k=3)
        
        # Results should be sorted by score descending
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)
        
        # Scores should be between 0 and 1 (cosine similarity)
        assert all(0.0 <= r.score <= 1.0 for r in results)
    
    def test_search_with_language_filter(self, test_documents):
        """Test search with language filtering"""
        retriever = DenseRetriever()
        retriever.index_documents(test_documents)
        
        results = retriever.search(query="machine learning", top_k=10, language='en')
        
        # Should only return English documents
        assert all(r.language == 'en' for r in results)
    
    def test_search_before_indexing(self):
        """Test search before indexing returns empty list"""
        retriever = DenseRetriever()
        
        results = retriever.search(query="test", top_k=5)
        
        assert results == []
    
    def test_search_with_min_score(self, test_documents):
        """Test search with minimum score threshold"""
        retriever = DenseRetriever()
        retriever.index_documents(test_documents[:3])
        
        results = retriever.search(query="machine learning", top_k=10, min_score=0.5)
        
        # All results should have score >= 0.5
        assert all(r.score >= 0.5 for r in results)
    
    def test_search_top_k_limit(self, test_documents):
        """Test that top_k limits results"""
        retriever = DenseRetriever()
        retriever.index_documents(test_documents)
        
        results = retriever.search(query="learning", top_k=2)
        
        assert len(results) <= 2
    
    def test_get_embedding(self, test_documents):
        """Test getting embedding for single text"""
        retriever = DenseRetriever()
        
        embedding = retriever.get_embedding("test text")
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)  # all-MiniLM-L6-v2 dimension
        # Should be normalized
        assert np.abs(np.linalg.norm(embedding) - 1.0) < 1e-5
    
    def test_get_document_score(self, test_documents):
        """Test getting score for specific document"""
        retriever = DenseRetriever()
        retriever.index_documents(test_documents[:3])
        
        score = retriever.get_document_score(
            query="machine learning",
            doc_id=test_documents[0]['id']
        )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_clear_index(self, test_documents):
        """Test clearing the index"""
        retriever = DenseRetriever()
        retriever.index_documents(test_documents[:3])
        
        assert retriever.indexed is True
        
        retriever.clear_index()
        
        assert retriever.indexed is False
        assert retriever.embeddings is None
        assert len(retriever.documents) == 0
        assert len(retriever.doc_ids) == 0
    
    def test_get_stats(self, test_documents):
        """Test getting retriever statistics"""
        retriever = DenseRetriever()
        
        # Before indexing
        stats = retriever.get_stats()
        assert stats['indexed'] is False
        assert stats['num_documents'] == 0
        
        # After indexing
        retriever.index_documents(test_documents[:3])
        stats = retriever.get_stats()
        assert stats['indexed'] is True
        assert stats['num_documents'] == 3
        assert stats['embedding_dim'] == 384
        assert stats['memory_mb'] > 0
    
    def test_semantic_search_quality(self, test_documents):
        """Test that semantic search works better than exact matching"""
        retriever = DenseRetriever()
        
        # Add documents with semantic relationships
        docs = [
            {'id': '1', 'text': 'Python is a programming language', 'language': 'en'},
            {'id': '2', 'text': 'Dogs are domestic animals', 'language': 'en'},
            {'id': '3', 'text': 'Coding in Python is fun', 'language': 'en'},
        ]
        retriever.index_documents(docs)
        
        # Query semantically similar to doc 1 and 3
        results = retriever.search(query="software development", top_k=3)
        
        # Programming-related docs should rank higher than dogs
        assert results[0].doc_id in ['1', '3']
        assert results[-1].doc_id == '2'


@pytest.mark.unit 
class TestDenseRetrieverMultilingual:
    """Test multilingual capabilities"""
    
    def test_multilingual_search(self):
        """Test that retriever works with multiple languages"""
        retriever = DenseRetriever(model_name='paraphrase-multilingual-MiniLM-L12-v2')
        
        docs = [
            {'id': '1', 'text': 'Machine learning is artificial intelligence', 'language': 'en'},
            {'id': '2', 'text': 'El aprendizaje automático es inteligencia artificial', 'language': 'es'},
            {'id': '3', 'text': 'Something completely unrelated', 'language': 'en'},
        ]
        retriever.index_documents(docs)
        
        # Should find both English and Spanish docs about ML
        results = retriever.search(query="artificial intelligence", top_k=3)
        
        # ML-related docs should rank higher
        top_ids = [r.doc_id for r in results[:2]]
        assert '1' in top_ids
        assert '2' in top_ids
