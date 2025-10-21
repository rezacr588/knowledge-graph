"""
Unit Tests for BM25 Retriever
Tests BM25 indexing and search functionality
"""

import pytest
from backend.retrieval.bm25_retriever import BM25Retriever, BM25Result


@pytest.mark.unit
class TestBM25Retriever:
    """Test BM25 retrieval functionality"""
    
    def test_initialization(self):
        """Test BM25 retriever initialization"""
        retriever = BM25Retriever(k1=1.5, b=0.75)
        assert retriever.k1 == 1.5
        assert retriever.b == 0.75
        assert retriever.bm25 is None
        assert retriever.documents == []
    
    def test_index_documents(self, test_documents):
        """Test indexing documents"""
        retriever = BM25Retriever()
        retriever.index(test_documents[:3])  # English docs only
        
        assert len(retriever.documents) == 3
        assert retriever.bm25 is not None
        assert len(retriever.doc_ids) == 3
    
    def test_index_empty_documents(self):
        """Test indexing with empty document list"""
        retriever = BM25Retriever()
        retriever.index([])
        
        assert len(retriever.documents) == 0
        assert retriever.bm25 is None
    
    def test_search_basic(self, test_documents):
        """Test basic search functionality"""
        retriever = BM25Retriever()
        retriever.index(test_documents[:3])
        
        results = retriever.search(query="machine learning", top_k=2)
        
        assert isinstance(results, list)
        assert len(results) <= 2
        assert all(isinstance(r, BM25Result) for r in results)
    
    def test_search_returns_scores(self, test_documents):
        """Test that search returns proper scores"""
        retriever = BM25Retriever()
        retriever.index(test_documents[:3])
        
        results = retriever.search(query="machine learning", top_k=3)
        
        # Results should be sorted by score descending
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)
        
        # Scores may be negative for tiny corpora, but the top result should be the highest.
        assert scores  # ensure at least one result is returned
    
    def test_search_with_language_filter(self, test_documents):
        """Test search with language filtering"""
        retriever = BM25Retriever()
        retriever.index(test_documents)
        
        results = retriever.search(query="machine learning", top_k=10, language='en')
        
        # Should only return English documents
        assert all(r.language == 'en' for r in results)
    
    def test_search_before_indexing(self):
        """Test search before indexing raises appropriate error"""
        retriever = BM25Retriever()
        
        results = retriever.search(query="test", top_k=5)
        
        # Should return empty list, not raise error
        assert results == []
    
    def test_search_empty_query(self, test_documents):
        """Test search with empty query"""
        retriever = BM25Retriever()
        retriever.index(test_documents[:3])
        
        results = retriever.search(query="", top_k=5)
        
        # Empty query should return no results
        assert len(results) == 0
    
    def test_search_top_k_limit(self, test_documents):
        """Test that top_k limits results"""
        retriever = BM25Retriever()
        retriever.index(test_documents[:3])
        
        results = retriever.search(query="learning", top_k=2)
        
        assert len(results) <= 2
    
    def test_result_structure(self, test_documents):
        """Test BM25Result structure"""
        retriever = BM25Retriever()
        retriever.index(test_documents[:3])
        
        results = retriever.search(query="machine learning", top_k=1)
        
        if results:
            result = results[0]
            assert hasattr(result, 'doc_id')
            assert hasattr(result, 'score')
            assert hasattr(result, 'rank')
            assert hasattr(result, 'text')
            assert hasattr(result, 'language')
            assert result.rank == 1
    
    def test_multilingual_indexing(self, test_documents):
        """Test indexing multilingual documents"""
        retriever = BM25Retriever()
        retriever.index(test_documents)
        
        assert len(retriever.documents) == 5
        
        # Test English query
        en_results = retriever.search(query="machine learning", top_k=5, language='en')
        assert len(en_results) > 0
        
        # Test Spanish query
        es_results = retriever.search(query="aprendizaje", top_k=5, language='es')
        assert len(es_results) > 0
    
    def test_reindexing(self, test_documents):
        """Test reindexing with new documents"""
        retriever = BM25Retriever()
        
        # Initial index
        retriever.index(test_documents[:2])
        assert len(retriever.documents) == 2
        
        # Reindex with more documents
        retriever.index(test_documents)
        assert len(retriever.documents) == 5
    
    def test_special_characters(self):
        """Test handling of special characters"""
        docs = [
            {'id': 'doc1', 'text': 'Test @#$% special chars!', 'language': 'en'}
        ]
        
        retriever = BM25Retriever()
        retriever.index(docs)
        results = retriever.search(query="special chars", top_k=1)
        
        assert len(results) >= 0  # Should not crash
    
    def test_unicode_text(self):
        """Test handling of Unicode text"""
        docs = [
            {'id': 'doc1', 'text': 'Testing 中文 Arabic العربية', 'language': 'en'}
        ]
        
        retriever = BM25Retriever()
        retriever.index(docs)
        results = retriever.search(query="中文", top_k=1)
        
        assert len(results) >= 0  # Should not crash


@pytest.mark.unit
class TestBM25Parameters:
    """Test BM25 parameter effects"""
    
    def test_k1_parameter_effect(self, test_documents):
        """Test that k1 parameter affects scoring"""
        retriever1 = BM25Retriever(k1=1.2, b=0.75)
        retriever2 = BM25Retriever(k1=2.0, b=0.75)
        
        retriever1.index(test_documents[:3])
        retriever2.index(test_documents[:3])
        
        results1 = retriever1.search(query="machine learning", top_k=3)
        results2 = retriever2.search(query="machine learning", top_k=3)
        
        # Scores should be different due to different k1
        if results1 and results2:
            assert results1[0].score != results2[0].score
    
    def test_b_parameter_effect(self, test_documents):
        """Test that b parameter affects scoring"""
        retriever1 = BM25Retriever(k1=1.5, b=0.5)
        retriever2 = BM25Retriever(k1=1.5, b=1.0)
        
        retriever1.index(test_documents[:3])
        retriever2.index(test_documents[:3])
        
        results1 = retriever1.search(query="machine learning", top_k=3)
        results2 = retriever2.search(query="machine learning", top_k=3)
        
        # Scores should be different due to different b
        if results1 and results2:
            assert results1[0].score != results2[0].score
