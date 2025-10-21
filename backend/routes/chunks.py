"""
Routes for inspecting stored chunks across Qdrant and the persisted chunk store.
"""

import asyncio
from typing import Dict, List, Optional, Set, Tuple

from fastapi import APIRouter, HTTPException, Query
import os

from backend.utils.logger import setup_logger


router = APIRouter(prefix="/chunks", tags=["chunks"])
logger = setup_logger(os.getenv('LOG_LEVEL', 'INFO'))


def get_app_state():
    """Access global FastAPI application state."""
    from backend.main import app_state
    return app_state


def _filter_by_language(items: List[Dict], language: Optional[str]) -> List[Dict]:
    if not language:
        return items

    lang = language.lower()
    filtered = [
        item for item in items
        if str(item.get("language", "")).lower() == lang
    ]
    return filtered


def _normalise_store_chunk(chunk: Dict) -> Dict:
    """Convert persisted chunk record to API payload shape."""
    return {
        "point_id": chunk.get("id"),
        "doc_id": chunk.get("id"),
        "text": chunk.get("text", ""),
        "language": chunk.get("language", "unknown"),
        "payload": chunk.get("metadata", {}),
        "source": "chunk_store",
    }


def _normalise_qdrant_chunk(chunk: Dict) -> Dict:
    """Ensure chunks returned from Qdrant have consistent metadata."""
    normalised = dict(chunk)
    normalised.setdefault("source", "qdrant")
    return normalised


async def _fetch_qdrant_chunks(
    limit: int,
    language: Optional[str]
) -> Tuple[List[Dict], Dict, bool]:
    """Fetch chunks from Qdrant if configured."""
    app_state = get_app_state()
    dense_retriever = app_state.get("dense_retriever")

    if not dense_retriever:
        return [], {}, False

    if not getattr(dense_retriever, "use_qdrant", False):
        return [], {}, False

    qdrant_store = getattr(dense_retriever, "qdrant_store", None)
    if not qdrant_store:
        logger.warning("Requested Qdrant chunks but vector store is unavailable.")
        return [], {}, False

    loop = asyncio.get_running_loop()

    def _load():
        return qdrant_store.list_chunks_with_info(limit=limit)

    chunks: List[Dict]
    info: Dict
    try:
        chunks, info = await loop.run_in_executor(None, _load)
        chunks = [_normalise_qdrant_chunk(chunk) for chunk in chunks]
        chunks = _filter_by_language(chunks, language)
        return chunks, info, True
    except Exception as exc:
        logger.error(f"Failed to list Qdrant chunks: {exc}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chunks from Qdrant")


def _fetch_persisted_chunks(language: Optional[str]) -> Tuple[List[Dict], Optional[int], bool]:
    """Retrieve chunks from the persisted chunk store on disk."""
    app_state = get_app_state()
    chunk_store = app_state.get("chunk_store")
    if not chunk_store:
        return [], None, False

    persisted = chunk_store.load_all()
    persisted = _filter_by_language(persisted, language)
    normalised = [_normalise_store_chunk(chunk) for chunk in persisted]
    return normalised, len(persisted), True


@router.get("")
async def list_chunks(
    limit: int = Query(200, ge=1, le=1000),
    language: Optional[str] = Query(default=None, description="Filter by language code"),
    source: str = Query(
        default="auto",
        pattern="^(auto|qdrant|store)$",
        description="Choose chunk source: 'auto' (default), 'qdrant', or 'store'"
    )
):
    """
    List stored chunks across Qdrant and/or the persisted chunk store.

    Args:
        limit: Maximum number of chunks to return.
        language: Optional language filter.
        source: Data source selector ('auto', 'qdrant', 'store').

    Returns:
        JSON payload containing chunk metadata, counts, and provenance details.
    """
    source = source.lower()
    results: List[Dict] = []
    source_counts: Dict[str, int] = {"qdrant": 0, "chunk_store": 0}
    total_available: Dict[str, Optional[int]] = {"qdrant": None, "chunk_store": None}
    seen_ids: Set[str] = set()

    include_qdrant = source in {"auto", "qdrant"}
    include_store = source in {"auto", "store"}

    if include_qdrant:
        qdrant_chunks, info, qdrant_active = await _fetch_qdrant_chunks(limit, language)
        if qdrant_active:
            total_available["qdrant"] = info.get("vectors_count", len(qdrant_chunks))
            for chunk in qdrant_chunks:
                if len(results) >= limit:
                    break
                results.append(chunk)
                seen_ids.add(str(chunk.get("doc_id")))
            source_counts["qdrant"] = len(qdrant_chunks[:limit])
        elif source == "qdrant":
            raise HTTPException(status_code=503, detail="Qdrant storage is not enabled")

    remaining_slots = limit - len(results)

    if include_store and remaining_slots > 0:
        store_chunks, total_store, store_active = _fetch_persisted_chunks(language)
        total_available["chunk_store"] = total_store

        if source == "store" and not store_active:
            raise HTTPException(status_code=503, detail="Chunk store is not available")

        appended = 0
        for chunk in store_chunks:
            if remaining_slots <= 0:
                break
            chunk_id = str(chunk.get("doc_id"))
            if chunk_id in seen_ids and source == "auto":
                continue
            results.append(chunk)
            seen_ids.add(chunk_id)
            appended += 1
            remaining_slots -= 1
        source_counts["chunk_store"] = appended if source != "store" else min(total_store or 0, limit)

    if source == "store" and total_available["chunk_store"] is None:
        raise HTTPException(status_code=503, detail="Chunk store is not available")

    return {
        "limit": limit,
        "returned": len(results),
        "language": language,
        "source": source,
        "source_counts": source_counts,
        "total_available": total_available,
        "chunks": results,
    }
