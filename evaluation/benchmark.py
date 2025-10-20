"""
Evaluation Framework for Hybrid RAG System
Compares BM25-only, ColBERT-only, Graph-only, and Hybrid approaches
"""

import json
import time
from typing import List, Dict
import numpy as np

def mean_reciprocal_rank(results: List[List[str]], ground_truth: List[str]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR)
    
    Args:
        results: List of ranked result lists
        ground_truth: List of relevant document IDs
    
    Returns:
        MRR score
    """
    reciprocal_ranks = []
    
    for result_list in results:
        for rank, doc_id in enumerate(result_list, start=1):
            if doc_id in ground_truth:
                reciprocal_ranks.append(1.0 / rank)
                break
        else:
            reciprocal_ranks.append(0.0)
    
    return np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0

def ndcg_at_k(results: List[List[str]], ground_truth: Dict[str, float], k: int = 10) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain at K
    
    Args:
        results: List of ranked result lists
        ground_truth: Dict mapping doc_id to relevance score
        k: Cutoff position
    
    Returns:
        NDCG@K score
    """
    def dcg(relevances):
        return sum(rel / np.log2(idx + 2) for idx, rel in enumerate(relevances))
    
    ndcg_scores = []
    
    for result_list in results:
        # Get relevances for retrieved documents
        relevances = [ground_truth.get(doc_id, 0.0) for doc_id in result_list[:k]]
        
        # Calculate DCG
        dcg_score = dcg(relevances)
        
        # Calculate IDCG (ideal DCG)
        ideal_relevances = sorted(ground_truth.values(), reverse=True)[:k]
        idcg_score = dcg(ideal_relevances)
        
        # Calculate NDCG
        if idcg_score > 0:
            ndcg_scores.append(dcg_score / idcg_score)
        else:
            ndcg_scores.append(0.0)
    
    return np.mean(ndcg_scores) if ndcg_scores else 0.0

def recall_at_k(results: List[List[str]], ground_truth: List[str], k: int = 10) -> float:
    """
    Calculate Recall at K
    
    Args:
        results: List of ranked result lists
        ground_truth: List of relevant document IDs
        k: Cutoff position
    
    Returns:
        Recall@K score
    """
    recall_scores = []
    
    for result_list in results:
        retrieved = set(result_list[:k])
        relevant = set(ground_truth)
        
        if len(relevant) > 0:
            recall = len(retrieved & relevant) / len(relevant)
            recall_scores.append(recall)
    
    return np.mean(recall_scores) if recall_scores else 0.0

def evaluate_retrieval_method(method_name: str, results: List[List[str]], 
                              ground_truth_list: List[str], 
                              ground_truth_dict: Dict[str, float]) -> Dict:
    """
    Evaluate a single retrieval method
    
    Args:
        method_name: Name of the method
        results: Retrieval results
        ground_truth_list: List of relevant docs
        ground_truth_dict: Dict of relevance scores
    
    Returns:
        Dictionary of evaluation metrics
    """
    metrics = {
        'method': method_name,
        'mrr': mean_reciprocal_rank(results, ground_truth_list),
        'ndcg@5': ndcg_at_k(results, ground_truth_dict, k=5),
        'ndcg@10': ndcg_at_k(results, ground_truth_dict, k=10),
        'recall@5': recall_at_k(results, ground_truth_list, k=5),
        'recall@10': recall_at_k(results, ground_truth_list, k=10),
    }
    
    return metrics

def print_comparison_table(all_metrics: List[Dict]):
    """Print comparison table of all methods"""
    print("\n" + "="*80)
    print("EVALUATION RESULTS - Hybrid RAG System")
    print("="*80)
    print(f"{'Method':<20} {'MRR':<10} {'NDCG@5':<10} {'NDCG@10':<10} {'Recall@5':<10} {'Recall@10':<10}")
    print("-"*80)
    
    for metrics in all_metrics:
        print(f"{metrics['method']:<20} "
              f"{metrics['mrr']:<10.4f} "
              f"{metrics['ndcg@5']:<10.4f} "
              f"{metrics['ndcg@10']:<10.4f} "
              f"{metrics['recall@5']:<10.4f} "
              f"{metrics['recall@10']:<10.4f}")
    
    print("="*80)
    
    # Calculate improvement
    if len(all_metrics) > 1:
        hybrid = next((m for m in all_metrics if 'hybrid' in m['method'].lower()), None)
        if hybrid:
            best_single = max([m for m in all_metrics if 'hybrid' not in m['method'].lower()],
                            key=lambda x: x['ndcg@10'])
            
            improvement = ((hybrid['ndcg@10'] - best_single['ndcg@10']) / 
                          best_single['ndcg@10'] * 100)
            
            print(f"\n✅ Hybrid method improves NDCG@10 by {improvement:.1f}% "
                  f"over best single method ({best_single['method']})")
            print("="*80 + "\n")

if __name__ == "__main__":
    # Example usage
    print("Evaluation Framework Ready")
    print("Add your test queries and ground truth data to run evaluation")
