"""Unit Tests for Hybrid Fusion (RRF)"""

import pytest
from backend.retrieval.hybrid_fusion import reciprocal_rank_fusion, FusedResult
from backend.retrieval.bm25_retriever import BM25Result

@pytest.mark.unit
class TestReciprocalRankFusion:
    def test_fusion_empty_results(self):
        results_dict = {}
        fused = reciprocal_rank_fusion(results_dict, k=60)
        assert fused == []
    
    def test_fusion_single_method(self):
        bm25_results = [
            BM25Result(doc_id='doc1', score=10.0, rank=1, text='text1', language='en'),
            BM25Result(doc_id='doc2', score=5.0, rank=2, text='text2', language='en'),
        ]
        results_dict = {'bm25': bm25_results}
        fused = reciprocal_rank_fusion(results_dict, k=60)
        assert len(fused) == 2
        assert all(isinstance(r, FusedResult) for r in fused)
    
    def test_rrf_score_calculation(self):
        bm25_results = [BM25Result(doc_id='doc1', score=10.0, rank=1, text='text1', language='en')]
        fused = reciprocal_rank_fusion({'bm25': bm25_results}, k=60)
        expected_score = 1 / (60 + 1)
        assert abs(fused[0].rrf_score - expected_score) < 0.0001
