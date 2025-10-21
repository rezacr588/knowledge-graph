"""
Knowledge graph routes
"""

from fastapi import APIRouter, HTTPException
import os

from backend.utils.logger import setup_logger

router = APIRouter(prefix="/graph", tags=["knowledge-graph"])
logger = setup_logger(os.getenv('LOG_LEVEL', 'INFO'))


def get_app_state():
    """Get app_state from main module"""
    from backend.main import app_state
    return app_state


@router.get("/stats")
async def get_graph_stats():
    """
    Get knowledge graph statistics
    """
    app_state = get_app_state()
    
    try:
        neo4j_client = app_state.get('neo4j_client')
        if not neo4j_client:
            raise HTTPException(status_code=503, detail="Neo4j not available")
        
        stats = neo4j_client.get_stats()
        return stats
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Graph stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualization")
async def get_graph_visualization(limit: int = 100):
    """
    Get graph data for visualization
    """
    app_state = get_app_state()
    
    try:
        neo4j_client = app_state.get('neo4j_client')
        if not neo4j_client:
            raise HTTPException(status_code=503, detail="Neo4j not available")
        
        graph_data = neo4j_client.get_visualization_data(limit=limit)
        return graph_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Graph visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
