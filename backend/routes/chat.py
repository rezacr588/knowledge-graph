"""
Chat routes
"""

from fastapi import APIRouter, HTTPException
import uuid
import time
import os
from typing import Dict, Any, List

from backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    RetrievalResult,
    RetrievalMethodEnum,
    LanguageEnum
)
from backend.retrieval.hybrid_fusion import reciprocal_rank_fusion
from backend.utils.logger import setup_logger

router = APIRouter(prefix="/chat", tags=["chat"])
logger = setup_logger(os.getenv('LOG_LEVEL', 'INFO'))


def get_app_state():
    """Get app_state from main module"""
    from backend.main import app_state
    return app_state


def _normalise_methods(methods: List[Any]) -> List[str]:
    """Convert retrieval method enums/strings to lowercase strings."""
    normalised = []
    for method in methods:
        if isinstance(method, RetrievalMethodEnum):
            normalised.append(method.value)
        elif isinstance(method, str):
            normalised.append(method.lower())
    return normalised


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with documents using Gemini.

    Steps:
        1. Retrieve hybrid context (BM25, dense/ColBERT, graph).
        2. Generate answer using Gemini conditioned on retrieved chunks.
    """
    app_state = get_app_state()
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(f"[{request_id}] Chat: {request.message[:100]}")

    if not app_state.get('chat_service'):
        raise HTTPException(
            status_code=503,
            detail="Chat service not available. Please configure GEMINI_API_KEY."
        )

    try:
        requested_methods = set(_normalise_methods(request.retrieval_methods))
        language = (
            request.language.value
            if isinstance(request.language, LanguageEnum)
            else request.language
        )
        if not language:
            language = "en"

        retrieval_start = time.time()
        results_dict: Dict[str, List[Any]] = {}

        # BM25 retrieval
        if 'bm25' in requested_methods and app_state.get('bm25_retriever'):
            bm25_results = app_state['bm25_retriever'].search(
                query=request.message,
                top_k=request.top_k,
                language=language
            )
            results_dict['bm25'] = bm25_results

        # Dense retrieval (alias: colbert)
        if {'dense', 'colbert'} & requested_methods and app_state.get('dense_retriever'):
            try:
                dense_results = app_state['dense_retriever'].search(
                    query=request.message,
                    top_k=request.top_k,
                    language=language
                )
                results_dict['dense'] = dense_results
            except Exception as err:
                logger.warning(f"Dense retrieval failed: {err}")

        # Graph retrieval
        if 'graph' in requested_methods and app_state.get('graph_retriever'):
            try:
                graph_results = app_state['graph_retriever'].search(
                    query=request.message,
                    top_k=request.top_k,
                    language=language
                )
                results_dict['graph'] = graph_results
            except Exception as err:
                logger.warning(f"Graph retrieval failed: {err}")

        if not results_dict:
            logger.warning(f"[{request_id}] No retrieval methods available or configured.")

        fused_results = reciprocal_rank_fusion(
            results_dict=results_dict,
            k=60,
            top_k=request.top_k
        )

        retrieval_time_ms = (time.time() - retrieval_start) * 1000

        generation_start = time.time()

        retrieved_chunks_for_llm = [
            {
                "text": result.text,
                "rrf_score": result.rrf_score,
                "doc_id": result.doc_id,
                "chunk_id": result.chunk_id
            }
            for result in fused_results
        ]

        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        answer = app_state['chat_service'].generate_response(
            query=request.message,
            retrieved_chunks=retrieved_chunks_for_llm,
            conversation_history=conversation_history,
            language=language
        )

        generation_time_ms = (time.time() - generation_start) * 1000

        response_results = [
            RetrievalResult(
                doc_id=result.doc_id,
                chunk_id=result.chunk_id,
                text=result.text,
                rrf_score=result.rrf_score,
                rank=result.rank,
                language=result.language,
                method_scores=result.method_scores,
                method_ranks=result.method_ranks
            )
            for result in fused_results
        ]

        total_time_ms = (time.time() - start_time) * 1000

        logger.info(f"[{request_id}] Chat completed in {total_time_ms:.2f}ms")

        return ChatResponse(
            message=answer,
            retrieved_chunks=response_results,
            retrieval_time_ms=retrieval_time_ms,
            generation_time_ms=generation_time_ms,
            total_time_ms=total_time_ms
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[{request_id}] Chat error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
