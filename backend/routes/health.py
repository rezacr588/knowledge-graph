"""
Health check and system status routes
"""

from fastapi import APIRouter
import os
import time

from backend.models.schemas import HealthResponse, HealthStatus, DependencyStatus

router = APIRouter(tags=["health"])


def get_app_state():
    """Get app_state from main module"""
    from backend.main import app_state
    return app_state


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Hybrid RAG System",
        "version": os.getenv('APP_VERSION', '1.0.0'),
        "status": "running",
        "docs": "/docs"
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Checks all dependencies and returns system status
    """
    app_state = get_app_state()
    dependencies = {}
    overall_healthy = True
    
    # Check Neo4j
    if app_state.get('neo4j_client'):
        try:
            # Simple connectivity check
            app_state['neo4j_client'].driver.verify_connectivity()
            dependencies['neo4j'] = DependencyStatus(available=True)
        except Exception as e:
            dependencies['neo4j'] = DependencyStatus(available=False, message=str(e))
            overall_healthy = False
    else:
        dependencies['neo4j'] = DependencyStatus(available=False, message="Not configured")
        overall_healthy = False
    
    # Check BM25
    dependencies['bm25'] = DependencyStatus(
        available=app_state.get('bm25_retriever') is not None
    )
    
    # Check Dense Retriever (replaces ColBERT)
    dependencies['dense'] = DependencyStatus(
        available=app_state.get('dense_retriever') is not None
    )
    
    # Check Entity Extractor
    dependencies['entity_extractor'] = DependencyStatus(
        available=app_state.get('entity_extractor') is not None
    )
    
    status = HealthStatus.HEALTHY if overall_healthy else HealthStatus.DEGRADED
    
    return HealthResponse(
        status=status,
        dependencies=dependencies,
        uptime_seconds=time.time() - app_state['start_time'],
        version=os.getenv('APP_VERSION', '1.0.0')
    )
