"""
Routes for inspecting stored chunks in Qdrant.
"""

import asyncio

from fastapi import APIRouter, HTTPException, Query
import os

from backend.utils.logger import setup_logger


router = APIRouter(prefix="/chunks", tags=["chunks"])
logger = setup_logger(os.getenv('LOG_LEVEL', 'INFO'))


def get_app_state():
    """Access global FastAPI application state."""
    from backend.main import app_state
    return app_state


@router.get("")
async def list_qdrant_chunks(limit: int = Query(200, ge=1, le=1000)):
    """
    List chunks stored in the Qdrant vector database.

    Args:
        limit: Maximum number of chunks to retrieve for this request.

    Returns:
        JSON payload containing chunk metadata and collection stats.
    """
    app_state = get_app_state()
    dense_retriever = app_state.get('dense_retriever')

    if not dense_retriever:
        raise HTTPException(status_code=503, detail="Dense retriever is not initialized")

    if not getattr(dense_retriever, "use_qdrant", False):
        raise HTTPException(status_code=503, detail="Qdrant storage is not enabled")

    qdrant_store = getattr(dense_retriever, "qdrant_store", None)
    if not qdrant_store:
        raise HTTPException(status_code=503, detail="Qdrant vector store is unavailable")

    loop = asyncio.get_running_loop()

    try:
        chunks, info = await loop.run_in_executor(
            None, lambda: qdrant_store.list_chunks_with_info(limit=limit)
        )
        total_chunks = info.get("vectors_count", len(chunks))

        return {
            "total_chunks": total_chunks,
            "returned": len(chunks),
            "limit": limit,
            "chunks": chunks,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to list Qdrant chunks: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chunks from Qdrant")
