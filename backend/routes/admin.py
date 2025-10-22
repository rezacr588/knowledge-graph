from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
import logging

from backend.storage.neo4j_client import Neo4jClient
from backend.storage.qdrant_client import QdrantVectorStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


def _get_app_state() -> dict:
    from backend.main import app_state  # type: ignore
    return app_state


def get_neo4j_client() -> Neo4jClient:
    app_state = _get_app_state()
    client = app_state.get("neo4j_client")
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Neo4j client not available. Check connection settings."
        )
    return client


def get_qdrant_store() -> QdrantVectorStore:
    app_state = _get_app_state()

    dense_retriever = app_state.get("dense_retriever")
    if dense_retriever:
        qdrant_store = getattr(dense_retriever, "qdrant_store", None)
        if qdrant_store:
            return qdrant_store

    qdrant_store = app_state.get("qdrant_store")
    if qdrant_store:
        return qdrant_store

    raise HTTPException(
        status_code=503,
        detail="Qdrant store not available. Ensure dense retriever is configured."
    )

@router.post("/reset-all", response_model=Dict[str, str])
async def reset_all_data(
    neo4j_client: Neo4jClient = Depends(get_neo4j_client),
    qdrant_store: QdrantVectorStore = Depends(get_qdrant_store)
) -> Dict[str, str]:
    """
    Reset all data from databases and in-memory indexes.
    
    This will:
    - Clear all nodes and relationships from Neo4j
    - Delete all vectors and metadata from Qdrant
    - Clear BM25 in-memory index
    - Clear persisted chunk store
    - Clear in-memory documents
    
    ⚠️ WARNING: This action is irreversible!
    """
    try:
        logger.warning("🗑️  Starting database reset - clearing all data...")
        app_state = _get_app_state()
        
        # Clear Neo4j database
        logger.info("Clearing Neo4j database...")
        neo4j_client.clear_database()
        logger.info("✅ Neo4j database cleared")
        
        # Clear Qdrant collection (vectors and chunks)
        logger.info("Clearing Qdrant collection...")
        qdrant_store.clear_collection()
        logger.info("✅ Qdrant collection cleared")
        
        # Clear BM25 index
        bm25_retriever = app_state.get('bm25_retriever')
        if bm25_retriever:
            logger.info("Clearing BM25 index...")
            bm25_retriever.clear_index()
            logger.info("✅ BM25 index cleared")
        
        # Clear persisted chunk store
        chunk_store = app_state.get('chunk_store')
        if chunk_store:
            logger.info("Clearing chunk store...")
            chunk_store.clear()
            logger.info("✅ Chunk store cleared")
        
        # Clear in-memory documents
        if 'documents' in app_state:
            logger.info("Clearing in-memory documents...")
            app_state['documents'] = []
            logger.info("✅ In-memory documents cleared")
        
        logger.warning("🎉 Database reset completed successfully!")
        
        return {
            "status": "success",
            "message": "All data has been cleared from Neo4j, Qdrant, BM25 index, and chunk store",
            "neo4j": "cleared",
            "qdrant": "cleared",
            "bm25": "cleared",
            "chunks": "cleared",
            "documents": "cleared"
        }
        
    except Exception as e:
        logger.error(f"❌ Error during database reset: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset databases: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, int])
async def get_admin_stats(
    neo4j_client: Neo4jClient = Depends(get_neo4j_client),
    qdrant_store: QdrantVectorStore = Depends(get_qdrant_store)
) -> Dict[str, int]:
    """
    Get current database statistics.
    """
    try:
        # Get Neo4j stats
        neo4j_stats = neo4j_client.get_graph_stats()
        
        # Get Qdrant stats
        collection_info = qdrant_store.client.get_collection(qdrant_store.collection_name)
        qdrant_count = collection_info.points_count if collection_info else 0
        
        return {
            "neo4j_entities": neo4j_stats.get("entities", 0),
            "neo4j_relationships": neo4j_stats.get("relationships", 0),
            "neo4j_documents": neo4j_stats.get("documents", 0),
            "neo4j_chunks": neo4j_stats.get("chunks", 0),
            "qdrant_vectors": qdrant_count
        }
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )
