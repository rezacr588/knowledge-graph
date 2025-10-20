"""
Hybrid Fusion Strategy - Reciprocal Rank Fusion (RRF)
Reference: Cormack et al., "Reciprocal Rank Fusion outperforms Condorcet 
and individual Rank Learning Methods", SIGIR 2009
"""

from typing import List, Dict, Any
from collections import defaultdict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class FusedResult:
    """Fused retrieval result"""
    doc_id: str
    chunk_id: str
    rrf_score: float
    rank: int
    text: str
    language: str
    method_scores: Dict[str, float]
    method_ranks: Dict[str, int]

def reciprocal_rank_fusion(
    results_dict: Dict[str, List[Any]], 
    k: int = 60,
    top_k: int = 10
) -> List[FusedResult]:
    """
    Combine multiple ranked lists using Reciprocal Rank Fusion
    
    Args:
        results_dict: Dictionary mapping method names to result lists
                     Each result must have 'doc_id' or 'chunk_id' attribute
        k: RRF parameter (typically 60)
        top_k: Number of final results to return
    
    Returns:
        Combined ranked list with RRF scores
        
    Formula:
        RRFscore(d) = Σ_{r∈R} 1/(k + rank_r(d))
        
    Example:
        results_dict = {
            'bm25': [result1, result2, ...],
            'colbert': [result1, result2, ...],
            'graph': [result1, result2, ...]
        }
    """
    logger.info(f"Fusing results from {len(results_dict)} methods with RRF (k={k})")
    
    # Calculate RRF scores
    rrf_scores = defaultdict(float)
    method_ranks = defaultdict(dict)
    method_scores = defaultdict(dict)
    doc_info = {}  # Store document information
    
    for method_name, results in results_dict.items():
        logger.info(f"  {method_name}: {len(results)} results")
        
        for rank, result in enumerate(results, start=1):
            # Get document/chunk identifier
            doc_id = getattr(result, 'chunk_id', None) or getattr(result, 'doc_id', None)
            
            if doc_id:
                # Add RRF contribution
                rrf_scores[doc_id] += 1.0 / (k + rank)
                
                # Store method-specific rank and score
                method_ranks[doc_id][method_name] = rank
                method_scores[doc_id][method_name] = getattr(result, 'score', 0.0)
                
                # Store document info (text, language, etc.)
                if doc_id not in doc_info:
                    doc_info[doc_id] = {
                        'text': getattr(result, 'text', ''),
                        'language': getattr(result, 'language', 'unknown'),
                        'doc_id': getattr(result, 'doc_id', doc_id),
                        'chunk_id': doc_id
                    }
    
    # Sort by RRF score
    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    # Create FusedResult objects
    fused_results = []
    for final_rank, (doc_id, rrf_score) in enumerate(sorted_results, start=1):
        info = doc_info[doc_id]
        
        fused_results.append(FusedResult(
            doc_id=info['doc_id'],
            chunk_id=info['chunk_id'],
            rrf_score=float(rrf_score),
            rank=final_rank,
            text=info['text'],
            language=info['language'],
            method_scores=dict(method_scores[doc_id]),
            method_ranks=dict(method_ranks[doc_id])
        ))
    
    logger.info(f"✅ Fused to {len(fused_results)} final results")
    
    return fused_results


def weighted_fusion(
    results_dict: Dict[str, List[Any]],
    weights: Dict[str, float],
    top_k: int = 10
) -> List[FusedResult]:
    """
    Combine results using weighted scoring
    
    Args:
        results_dict: Dictionary mapping method names to result lists
        weights: Dictionary mapping method names to weights
        top_k: Number of final results to return
    
    Returns:
        Combined ranked list with weighted scores
    """
    logger.info(f"Fusing results using weighted scoring")
    
    combined_scores = defaultdict(float)
    method_scores = defaultdict(dict)
    doc_info = {}
    
    for method_name, results in results_dict.items():
        weight = weights.get(method_name, 1.0)
        
        for result in results:
            doc_id = getattr(result, 'chunk_id', None) or getattr(result, 'doc_id', None)
            score = getattr(result, 'score', 0.0)
            
            if doc_id:
                combined_scores[doc_id] += weight * score
                method_scores[doc_id][method_name] = score
                
                if doc_id not in doc_info:
                    doc_info[doc_id] = {
                        'text': getattr(result, 'text', ''),
                        'language': getattr(result, 'language', 'unknown'),
                        'doc_id': getattr(result, 'doc_id', doc_id),
                        'chunk_id': doc_id
                    }
    
    # Sort by weighted score
    sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    # Create FusedResult objects
    fused_results = []
    for final_rank, (doc_id, weighted_score) in enumerate(sorted_results, start=1):
        info = doc_info[doc_id]
        
        fused_results.append(FusedResult(
            doc_id=info['doc_id'],
            chunk_id=info['chunk_id'],
            rrf_score=float(weighted_score),
            rank=final_rank,
            text=info['text'],
            language=info['language'],
            method_scores=dict(method_scores[doc_id]),
            method_ranks={}
        ))
    
    return fused_results
