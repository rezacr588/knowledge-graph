"""
Hybrid RAG System - FastAPI Backend
Combines BM25, Dense, and Graph retrieval with RRF fusion
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from dotenv import load_dotenv

from backend.retrieval.bm25_retriever import BM25Retriever
from backend.retrieval.graph_retriever import GraphRetriever
from backend.storage.neo4j_client import Neo4jClient
from backend.storage.chunk_store import ChunkStore
from backend.services.entity_extraction import EntityExtractor
from backend.services.chat_service import ChatService
from backend.utils.logger import setup_logger
from backend.utils.document_parser import DocumentParser

# Import routers
from backend.routes import (
    health_router,
    ingest_router,
    query_router,
    chat_router,
    graph_router,
    chunks_router,
    admin_router
)

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(os.getenv('LOG_LEVEL', 'INFO'))

# Persistence configuration
PERSIST_INGESTED_CONTENT = os.getenv('PERSIST_INGESTED_CONTENT', 'true').lower() in {
    '1', 'true', 'yes', 'on'
}
INGESTED_CHUNKS_PATH = os.getenv(
    'INGESTED_CHUNKS_PATH',
    os.path.join(os.getcwd(), 'data', 'ingested_chunks.json')
)

# Dense retriever import (configurable via environment)
ENABLE_DENSE_RETRIEVER = os.getenv('ENABLE_DENSE_RETRIEVER', 'true').lower() in {
    '1', 'true', 'yes', 'on'
}
DENSE_AVAILABLE = False
DenseRetriever = None
if ENABLE_DENSE_RETRIEVER:
    try:
        from backend.retrieval.dense_retriever import DenseRetriever
        DENSE_AVAILABLE = True
        logger.info("✅ Dense retriever module loaded successfully")
    except ImportError as e:
        logger.warning(f"⚠️  Dense retriever not available: {e}")
        logger.warning("⚠️  System will use BM25 and Graph retrieval only")
else:
    logger.info("ℹ️ Dense retriever disabled via ENABLE_DENSE_RETRIEVER flag")

# Initialize FastAPI app
app = FastAPI(
    title="Hybrid RAG System",
    version=os.getenv('APP_VERSION', '1.0.0'),
    description="Production-grade Hybrid Retrieval-Augmented Generation system"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
app_state = {
    'start_time': time.time(),
    'bm25_retriever': None,
    'dense_retriever': None,
    'graph_retriever': None,
    'neo4j_client': None,
    'entity_extractor': None,
    'chat_service': None,
    'document_parser': None,
    'documents': [],
    'ingestion_reset_done': False,
    'progress_trackers': {},
    'chunk_store': None,
    'persist_ingested_content': PERSIST_INGESTED_CONTENT
}

if PERSIST_INGESTED_CONTENT:
    app_state['ingestion_reset_done'] = True


def reset_ingested_content(force: bool = False) -> None:
    """Remove any previously indexed documents across storage layers."""
    if PERSIST_INGESTED_CONTENT and not force:
        logger.info("🛑 Persistence enabled; skipping automatic reset of ingested content.")
        app_state['ingestion_reset_done'] = True
        return

    logger.info("🧹 Clearing previously ingested documents and indexes")

    if app_state.get('bm25_retriever'):
        app_state['bm25_retriever'].clear_index()

    if app_state.get('dense_retriever'):
        try:
            app_state['dense_retriever'].clear_index()
        except Exception as exc:
            logger.warning(f"Failed to clear dense index: {exc}")

    if app_state.get('neo4j_client'):
        app_state['neo4j_client'].clear_database()

    if app_state.get('chunk_store'):
        app_state['chunk_store'].clear()

    app_state['documents'] = []
    app_state['ingestion_reset_done'] = True


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    logger.info("🚀 Starting Hybrid RAG System...")
    
    try:
        # Initialize Neo4j client
        neo4j_uri = os.getenv('NEO4J_URI')
        neo4j_user = os.getenv('NEO4J_USERNAME')
        neo4j_password = os.getenv('NEO4J_PASSWORD')
        
        if neo4j_uri and neo4j_user and neo4j_password:
            app_state['neo4j_client'] = Neo4jClient(
                uri=neo4j_uri,
                username=neo4j_user,
                password=neo4j_password
            )
            logger.info("✅ Neo4j client initialized")
        else:
            logger.warning("⚠️  Neo4j credentials not configured")
        
        # Initialize BM25 retriever
        app_state['bm25_retriever'] = BM25Retriever()
        logger.info("✅ BM25 retriever initialized")
        
        # Initialize Entity Extractor (needed by GraphRetriever)
        app_state['entity_extractor'] = EntityExtractor()
        logger.info("✅ Entity extractor initialized")
        
        # Initialize Dense retriever if available
        if DENSE_AVAILABLE and DenseRetriever:
            try:
                app_state['dense_retriever'] = DenseRetriever()
                qdrant_store = getattr(app_state['dense_retriever'], 'qdrant_store', None)
                if qdrant_store:
                    app_state['qdrant_store'] = qdrant_store
                logger.info("✅ Dense retriever initialized")
            except Exception as e:
                logger.warning(f"⚠️  Dense retriever initialization failed: {e}")
        
        # Initialize Graph retriever (requires neo4j_client and entity_extractor)
        if app_state.get('neo4j_client') and app_state.get('entity_extractor'):
            app_state['graph_retriever'] = GraphRetriever(
                neo4j_client=app_state['neo4j_client'],
                entity_extractor=app_state['entity_extractor']
            )
            logger.info("✅ Graph retriever initialized")
        
        # Initialize Chat Service
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            app_state['chat_service'] = ChatService(gemini_api_key=gemini_api_key)
            logger.info("✅ Chat service initialized")
        else:
            logger.warning("⚠️  Gemini API key not configured")
        
        # Initialize Document Parser
        app_state['document_parser'] = DocumentParser()
        logger.info("✅ Document parser initialized")

        if PERSIST_INGESTED_CONTENT:
            chunk_store = ChunkStore(INGESTED_CHUNKS_PATH)
            app_state['chunk_store'] = chunk_store
            persisted_chunks = chunk_store.load_all()

            if persisted_chunks:
                try:
                    app_state['bm25_retriever'].index_documents(persisted_chunks)
                    app_state['documents'] = persisted_chunks
                    logger.info(
                        "✅ Loaded %d persisted chunks into BM25 index", len(persisted_chunks)
                    )
                except Exception as exc:
                    logger.warning("Failed to hydrate BM25 index from disk: %s", exc)

                dense_retriever = app_state.get('dense_retriever')
                if dense_retriever and not getattr(dense_retriever, 'indexed', False):
                    try:
                        dense_retriever.index_documents(persisted_chunks)
                        logger.info("✅ Rebuilt dense index from persisted chunks")
                    except Exception as exc:
                        logger.warning("Failed to rebuild dense index from disk: %s", exc)
            else:
                logger.info("ℹ️ No persisted chunks found at %s", INGESTED_CHUNKS_PATH)
        
        logger.info("✅ Hybrid RAG System started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Hybrid RAG System...")
    if app_state.get('neo4j_client'):
        app_state['neo4j_client'].close()


# Register routers
app.include_router(health_router)  # Root level (/, /health)
app.include_router(health_router, prefix="/api")  # Also under /api for frontend
app.include_router(ingest_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(graph_router, prefix="/api")
app.include_router(chunks_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

logger.info("✅ All routes registered")
