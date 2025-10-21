"""
Routes package for Hybrid RAG System
"""

from .health import router as health_router
from .ingest import router as ingest_router
from .query import router as query_router
from .chat import router as chat_router
from .graph import router as graph_router
from .chunks import router as chunks_router

__all__ = [
    'health_router',
    'ingest_router',
    'query_router',
    'chat_router',
    'graph_router',
    'chunks_router'
]
