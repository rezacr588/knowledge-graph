"""Integration Tests for Retrieval Pipeline"""

import pytest
from backend.retrieval.bm25_retriever import BM25Retriever
from backend.retrieval.hybrid_fusion import reciprocal_rank_fusion

@pytest.mark.integration
class TestRetrievalPipeline:
    def test_full_retrieval_pipeline(self, test_documents):
        """Test complete retrieval pipeline with BM25"""
        bm25 = BM25Retriever()
        bm25.index(test_documents[:3])
        
        bm25_results = bm25.search(query="machine learning", top_k=5)
        results_dict = {'bm25': bm25_results}
        fused = reciprocal_rank_fusion(results_dict, k=60)
        
        assert len(fused) > 0
        assert all(hasattr(r, 'rrf_score') for r in fused)
    
    def test_multilingual_retrieval(self, test_documents):
        """Test retrieval across multiple languages"""
        bm25 = BM25Retriever()
        bm25.index(test_documents)
        
        en_results = bm25.search(query="machine learning", top_k=5, language='en')
        es_results = bm25.search(query="aprendizaje", top_k=5, language='es')
        
        assert all(r.language == 'en' for r in en_results)
        assert all(r.language == 'es' for r in es_results)
