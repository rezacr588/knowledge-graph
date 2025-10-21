"""
Query and search routes
"""

from fastapi import APIRouter, HTTPException
import uuid
import time
import os

from backend.models.schemas import QueryRequest, QueryResponse, RetrievalResult
from backend.retrieval.hybrid_fusion import reciprocal_rank_fusion
from backend.utils.logger import setup_logger

router = APIRouter(prefix="/query", tags=["search"])
logger = setup_logger(os.getenv('LOG_LEVEL', 'INFO'))


def get_app_state():
    """Get app_state from main module"""
    from backend.main import app_state
    return app_state


@router.post("", response_model=QueryResponse)
async def hybrid_search(request: QueryRequest):
    """
    Execute hybrid search query
    
    Process:
    1. Run BM25 retrieval
    2. Run Dense retrieval
    3. Run Graph retrieval
    4. Fuse results with RRF
    5. Optional: Generate answer with LLM
    """
    app_state = get_app_state()
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"[{request_id}] Query: {request.query}")
    
    try:
        results_dict = {}
        retrieval_start = time.time()
        
        # BM25 retrieval
        if 'bm25' in request.retrieval_methods and app_state.get('bm25_retriever'):
            bm25_results = app_state['bm25_retriever'].search(
                query=request.query,
                top_k=request.top_k,
                language=request.language,
                min_score=-999.0  # Allow negative scores for small corpuses
            )
            results_dict['bm25'] = bm25_results
            logger.info(f"[{request_id}] BM25: {len(bm25_results)} results")
        
        # Dense retrieval
        if 'dense' in request.retrieval_methods and app_state.get('dense_retriever'):
            try:
                dense_results = app_state['dense_retriever'].search(
                    query=request.query,
                    top_k=request.top_k,
                    language=request.language
                )
                results_dict['dense'] = dense_results
                logger.info(f"[{request_id}] Dense: {len(dense_results)} results")
            except Exception as e:
                logger.warning(f"Dense retrieval search failed: {e}")
        
        # Also accept 'colbert' as alias for 'dense' for backward compatibility
        if 'colbert' in request.retrieval_methods and app_state.get('dense_retriever'):
            if 'dense' not in results_dict:
                try:
                    dense_results = app_state['dense_retriever'].search(
                        query=request.query,
                        top_k=request.top_k,
                        language=request.language
                    )
                    results_dict['dense'] = dense_results
                    logger.info(f"[{request_id}] Dense (as colbert): {len(dense_results)} results")
                except Exception as e:
                    logger.warning(f"Dense retrieval search failed: {e}")
        
        # Graph retrieval
        if 'graph' in request.retrieval_methods and app_state.get('graph_retriever'):
            try:
                graph_results = app_state['graph_retriever'].search(
                    query=request.query,
                    top_k=request.top_k,
                    language=request.language
                )
                results_dict['graph'] = graph_results
                logger.info(f"[{request_id}] Graph: {len(graph_results)} results")
            except Exception as e:
                logger.warning(f"Graph search failed: {e}")
        
        retrieval_time = (time.time() - retrieval_start) * 1000

        available_results = [
            results for results in results_dict.values() if results
        ]

        if not available_results:
            logger.warning(f"[{request_id}] No retriever returned any results.")
            raise HTTPException(
                status_code=500,
                detail="No documents indexed. Please ingest data before querying."
            )
        
        # Fusion
        fusion_start = time.time()
        fused_results = reciprocal_rank_fusion(
            results_dict=results_dict,
            k=request.rrf_k,
            top_k=request.top_k
        )
        fusion_time = (time.time() - fusion_start) * 1000
        
        logger.info(f"[{request_id}] Fused to {len(fused_results)} results")
        
        # Convert to response format (fused_results are FusedResult dataclass objects)
        results = [
            RetrievalResult(
                doc_id=r.doc_id,
                chunk_id=r.chunk_id,
                text=r.text,
                rrf_score=r.rrf_score,
                rank=r.rank,
                language=r.language,
                method_scores=r.method_scores,
                method_ranks=r.method_ranks
            )
            for r in fused_results
        ]
        
        total_time = (time.time() - start_time) * 1000
        
        logger.info(f"[{request_id}] Total query time: {total_time:.2f}ms")
        
        return QueryResponse(
            results=results,
            retrieval_time_ms=retrieval_time,
            fusion_time_ms=fusion_time,
            total_time_ms=total_time,
            methods_used=list(results_dict.keys())
        )
    
    except Exception as e:
        logger.error(f"[{request_id}] Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
