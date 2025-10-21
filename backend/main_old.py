"""
Hybrid RAG System - FastAPI Backend
Combines BM25, ColBERT, and Graph retrieval with RRF fusion
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import time
import os
from dotenv import load_dotenv
from typing import Dict, List
import uuid
import hashlib

from backend.models.schemas import (
    IngestRequest, IngestResponse,
    QueryRequest, QueryResponse, RetrievalResult,
    HealthResponse, HealthStatus, DependencyStatus,
    ChatRequest, ChatResponse, ChatMessage
)
from backend.retrieval.bm25_retriever import BM25Retriever
from backend.retrieval.graph_retriever import GraphRetriever
from backend.retrieval.hybrid_fusion import reciprocal_rank_fusion
from backend.storage.neo4j_client import Neo4jClient, Entity
from backend.services.entity_extraction import EntityExtractor
from backend.services.chat_service import ChatService
from backend.utils.logger import setup_logger, log_request, log_response
from backend.utils.document_parser import DocumentParser

# Load environment variables
load_dotenv()

# Setup logging (must be before imports that use it)
logger = setup_logger(os.getenv('LOG_LEVEL', 'INFO'))

# Dense retriever import (replaces problematic ColBERT/ragatouille)
DENSE_AVAILABLE = False
DenseRetriever = None
try:
    from backend.retrieval.dense_retriever import DenseRetriever
    DENSE_AVAILABLE = True
    logger.info("✅ Dense retriever module loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️  Dense retriever not available: {e}")
    logger.warning("⚠️  System will use BM25 and Graph retrieval only")

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
    'document_parser': None,
    'documents': [],  # In-memory document store for BM25
    'ingestion_reset_done': False,
    'progress_trackers': {}  # Track progress for active ingestion jobs
}

class ProgressUpdate(BaseModel):
    stage: str
    percent: int
    message: str


def reset_ingested_content() -> None:
    """
    Remove any previously indexed documents across storage layers.
    """
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

    app_state['documents'] = []
    app_state['ingestion_reset_done'] = True

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    logger.info("🚀 Starting Hybrid RAG System...")
    
    try:
        # Initialize Neo4j client
        if all([os.getenv('NEO4J_URI'), os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD')]):
            app_state['neo4j_client'] = Neo4jClient(
                uri=os.getenv('NEO4J_URI'),
                username=os.getenv('NEO4J_USERNAME'),
                password=os.getenv('NEO4J_PASSWORD')
            )
            logger.info("✅ Neo4j client initialized")
        else:
            logger.warning("⚠️  Neo4j credentials not configured")
        
        # Initialize Entity Extractor
        app_state['entity_extractor'] = EntityExtractor(
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        logger.info("✅ Entity extractor initialized")
        
        # Initialize Document Parser
        app_state['document_parser'] = DocumentParser()
        logger.info("✅ Document parser initialized")
        
        # Initialize BM25 Retriever
        app_state['bm25_retriever'] = BM25Retriever(
            k1=float(os.getenv('BM25_K1', 1.5)),
            b=float(os.getenv('BM25_B', 0.75))
        )
        logger.info("✅ BM25 retriever initialized")
        
        # Initialize Dense Retriever (replaces ColBERT)
        if DENSE_AVAILABLE:
            try:
                dense_device_override = os.getenv('DENSE_DEVICE')
                app_state['dense_retriever'] = DenseRetriever(
                    model_name=os.getenv('DENSE_MODEL', 'all-MiniLM-L6-v2'),
                    device=dense_device_override if dense_device_override else 'auto'
                )
                logger.info("✅ Dense retriever initialized")
            except Exception as e:
                logger.warning(f"⚠️  Dense retriever initialization failed: {e}")
        else:
            logger.warning("⚠️  Dense retriever not available - using BM25 and Graph only")
        
        # Initialize Graph Retriever
        if app_state['neo4j_client'] and app_state['entity_extractor']:
            app_state['graph_retriever'] = GraphRetriever(
                neo4j_client=app_state['neo4j_client'],
                entity_extractor=app_state['entity_extractor']
            )
            logger.info("✅ Graph retriever initialized")
        
        # Initialize Chat Service
        if os.getenv('GEMINI_API_KEY'):
            try:
                app_state['chat_service'] = ChatService(
                    gemini_api_key=os.getenv('GEMINI_API_KEY'),
                    model_name=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
                )
                logger.info("✅ Chat service initialized")
            except Exception as e:
                logger.warning(f"⚠️  Chat service initialization failed: {e}")
        else:
            logger.warning("⚠️  Gemini API key not configured - chat disabled")
        
        logger.info("✅ Hybrid RAG System started successfully!")
        reset_ingested_content()
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Hybrid RAG System...")
    if app_state.get('neo4j_client'):
        app_state['neo4j_client'].close()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Hybrid RAG System",
        "version": os.getenv('APP_VERSION', '1.0.0'),
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Checks all dependencies and returns system status
    """
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

@app.post("/ingest-stream")
async def ingest_document_stream(
    file: UploadFile = File(...),
    language: str = "en"
):
    """
    Ingest document with real-time progress updates via Server-Sent Events (SSE)
    """
    request_id = str(uuid.uuid4())
    
    # Read file content BEFORE creating the generator (to avoid "closed file" error)
    filename = file.filename
    content = await file.read()
    
    async def progress_generator():
        start_time = time.time()
        
        try:
            # Initialize progress tracker
            def update_progress(stage: str, percent: int, message: str):
                data = json.dumps({
                    "stage": stage,
                    "percent": percent,
                    "message": message
                })
                return f"data: {data}\n\n"
            
            # Stage 1: Reading file (already done)
            yield update_progress("reading", 5, "Reading uploaded file...")
            await asyncio.sleep(0.1)
            
            # Stage 2: Parsing document
            yield update_progress("parsing", 15, f"Parsing {filename}...")
            document_parser = app_state.get('document_parser')
            if not document_parser:
                raise ValueError("Document parser not available")
            
            text = document_parser.parse(filename, content)
            doc_id = hashlib.md5(content).hexdigest()[:16]
            await asyncio.sleep(0.1)
            
            # Stage 3: Chunking
            yield update_progress("chunking", 25, "Creating document chunks...")
            chunks = [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]
            total_chunks = len(chunks)
            await asyncio.sleep(0.1)
            
            # Stage 4: Storing in Neo4j
            yield update_progress("storing", 35, f"Storing {total_chunks} chunks in knowledge graph...")
            if app_state.get('neo4j_client'):
                app_state['neo4j_client'].add_document(
                    doc_id=doc_id,
                    title=filename,
                    language=language
                )
            
            entities_count = 0
            relationships_count = 0
            
            # Process each chunk with progress updates
            for i, chunk_text in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                progress_percent = 35 + int((i / total_chunks) * 45)
                
                yield update_progress(
                    "processing",
                    progress_percent,
                    f"Processing chunk {i+1}/{total_chunks}..."
                )
                
                # Add chunk to graph
                if app_state.get('neo4j_client'):
                    app_state['neo4j_client'].add_chunk(
                        chunk_id=chunk_id,
                        doc_id=doc_id,
                        text=chunk_text,
                        language=language,
                        embedding_id=chunk_id
                    )
                
                # Extract entities
                if app_state.get('entity_extractor'):
                    entities = app_state['entity_extractor'].extract_entities(
                        chunk_text,
                        language=language
                    )
                    entities_count += len(entities)
                    
                    # Add entities to graph
                    if app_state.get('neo4j_client'):
                        for entity in entities:
                            app_state['neo4j_client'].add_entity(
                                entity_id=f"{entity.text}_{entity.type}".replace(" ", "_"),
                                text=entity.text,
                                entity_type=entity.type
                            )
                            
                            app_state['neo4j_client'].add_relationship(
                                chunk_id=chunk_id,
                                entity_id=f"{entity.text}_{entity.type}".replace(" ", "_"),
                                relationship_type="CONTAINS"
                            )
                            relationships_count += 1
                
                await asyncio.sleep(0.05)  # Small delay for real-time feel
            
            # Stage 5: Building BM25 index
            yield update_progress("indexing_bm25", 85, "Building BM25 search index...")
            if app_state.get('bm25_retriever'):
                app_state['bm25_retriever'].add_documents([
                    {"id": f"{doc_id}_chunk_{i}", "text": chunk}
                    for i, chunk in enumerate(chunks)
                ])
            await asyncio.sleep(0.2)
            
            # Stage 6: Building dense index (if available)
            if app_state.get('dense_retriever'):
                yield update_progress("indexing_dense", 92, "Building dense embeddings...")
                try:
                    app_state['dense_retriever'].add_documents([
                        {"id": f"{doc_id}_chunk_{i}", "text": chunk}
                        for i, chunk in enumerate(chunks)
                    ])
                except Exception as e:
                    logger.warning(f"Dense indexing failed: {e}")
                await asyncio.sleep(0.2)
            
            # Complete
            processing_time = (time.time() - start_time) * 1000
            yield update_progress(
                "complete",
                100,
                f"Processing complete in {processing_time:.0f}ms"
            )
            
            # Send final result
            result = {
                "document_id": doc_id,
                "chunks_created": total_chunks,
                "entities_extracted": entities_count,
                "relationships_found": relationships_count,
                "processing_time_ms": processing_time
            }
            yield f"data: {json.dumps({'result': result})}\n\n"
            
        except Exception as e:
            logger.error(f"[{request_id}] Error during ingestion: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        progress_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    language: str = "en",
    background_tasks: BackgroundTasks = None
):
    """
    Ingest document into the hybrid RAG system (legacy endpoint, use /ingest-stream for progress)
    
    Process:
    1. Extract text from document
    2. Chunk into semantic sections
    3. Extract entities and relationships
    4. Store in Neo4j graph
    5. Generate embeddings and index with ColBERT
    6. Build BM25 index
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"[{request_id}] Ingesting document: {file.filename}")
    
    try:
        if not app_state.get('ingestion_reset_done'):
            try:
                reset_ingested_content()
            except Exception as exc:
                logger.error(f"[{request_id}] Failed to reset ingested documents: {exc}")
                raise HTTPException(status_code=500, detail="Failed to reset ingested documents") from exc
        
        # Ensure document parser is available
        document_parser = app_state.get('document_parser')
        if not document_parser:
            logger.error(f"[{request_id}] Document parser not initialized")
            raise HTTPException(status_code=500, detail="Document parser unavailable")
        
        # Read and parse file content
        content = await file.read()
        try:
            text = document_parser.parse(file.filename, content)
        except ValueError as exc:
            logger.error(f"[{request_id}] Unsupported document type: {exc}")
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            logger.error(f"[{request_id}] Document parsing error: {exc}")
            raise HTTPException(status_code=500, detail="Failed to parse uploaded document") from exc
        
        # Generate document ID
        doc_id = hashlib.md5(content).hexdigest()[:16]
        
        # Simple chunking (split by paragraphs)
        chunks = [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]
        logger.info(f"[{request_id}] Created {len(chunks)} chunks")
        
        # Store document and chunks in Neo4j
        entities_count = 0
        if app_state.get('neo4j_client'):
            app_state['neo4j_client'].add_document(
                doc_id=doc_id,
                title=file.filename,
                language=language
            )
            
            for i, chunk_text in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                
                # Add chunk to graph
                app_state['neo4j_client'].add_chunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    text=chunk_text,
                    language=language,
                    embedding_id=chunk_id
                )
                
                # Extract entities
                if app_state.get('entity_extractor'):
                    entities = app_state['entity_extractor'].extract_entities(
                        chunk_text,
                        language=language
                    )
                    
                    for entity in entities:
                        entity_id = app_state['entity_extractor'].generate_entity_id(
                            entity.name,
                            language
                        )
                        
                        # Add entity to graph
                        app_state['neo4j_client'].add_entity(Entity(
                            id=entity_id,
                            name=entity.name,
                            type=entity.type,
                            language=language,
                            confidence=entity.confidence,
                            metadata={}
                        ))
                        
                        # Link chunk to entity
                        app_state['neo4j_client'].link_chunk_to_entity(
                            chunk_id=chunk_id,
                            entity_id=entity_id,
                            confidence=entity.confidence
                        )
                        entities_count += 1
        
        # Prepare documents for indexing
        doc_objects = [
            {
                'id': f"{doc_id}_chunk_{i}",
                'text': chunk_text,
                'language': language,
                'metadata': {'doc_id': doc_id, 'chunk_idx': i}
            }
            for i, chunk_text in enumerate(chunks)
        ]
        
        # Index with BM25
        app_state['documents'].extend(doc_objects)
        app_state['bm25_retriever'].index_documents(app_state['documents'])
        
        # Index with Dense Retriever (replaces ColBERT)
        if app_state.get('dense_retriever'):
            try:
                app_state['dense_retriever'].index_documents(doc_objects)
            except Exception as e:
                logger.warning(f"Dense retriever indexing failed: {e}")
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"[{request_id}] Ingestion completed in {processing_time:.2f}ms")
        
        return IngestResponse(
            document_id=doc_id,
            chunks_created=len(chunks),
            entities_extracted=entities_count,
            relationships_found=0,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def hybrid_search(request: QueryRequest):
    """
    Execute hybrid search query
    
    Process:
    1. Run BM25 retrieval
    2. Run ColBERT retrieval
    3. Run Graph retrieval
    4. Fuse results with RRF
    5. Optional: Generate answer with LLM
    """
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
                language=request.language
            )
            results_dict['bm25'] = bm25_results
            logger.info(f"[{request_id}] BM25: {len(bm25_results)} results")
        
        # Dense retrieval (replaces ColBERT)
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
            if 'dense' not in results_dict:  # Only if not already searched
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
        
        # Fusion
        fusion_start = time.time()
        fused_results = reciprocal_rank_fusion(
            results_dict=results_dict,
            k=request.rrf_k,
            top_k=request.top_k
        )
        fusion_time = (time.time() - fusion_start) * 1000
        
        # Convert to response format
        response_results = [
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
        
        logger.info(f"[{request_id}] Query completed in {total_time:.2f}ms")
        
        return QueryResponse(
            results=response_results,
            answer=None,
            retrieval_time_ms=retrieval_time,
            fusion_time_ms=fusion_time,
            total_time_ms=total_time,
            methods_used=list(results_dict.keys())
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/stats")
async def get_graph_stats():
    """
    Get knowledge graph statistics
    
    Returns:
        Statistics about nodes and relationships in the graph
    """
    try:
        if not app_state.get('neo4j_client'):
            raise HTTPException(
                status_code=503,
                detail="Neo4j not available"
            )
        
        stats = app_state['neo4j_client'].get_graph_stats()
        return stats
    except Exception as e:
        logger.error(f"Graph stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/visualization")
async def get_graph_visualization(limit: int = 100):
    """
    Get graph data for visualization
    
    Args:
        limit: Maximum number of nodes to return
    
    Returns:
        Graph data with nodes and edges
    """
    try:
        if not app_state.get('neo4j_client'):
            raise HTTPException(
                status_code=503,
                detail="Neo4j not available"
            )
        
        graph_data = app_state['neo4j_client'].get_graph_visualization_data(limit=limit)
        return graph_data
    except Exception as e:
        logger.error(f"Graph visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with documents using Gemini
    
    Process:
    1. Retrieve relevant context using hybrid search
    2. Generate response with Gemini using retrieved context
    3. Return response with context chunks
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"[{request_id}] Chat: {request.message[:100]}")
    
    try:
        # Check if chat service is available
        if not app_state.get('chat_service'):
            raise HTTPException(
                status_code=503,
                detail="Chat service not available. Please configure GEMINI_API_KEY."
            )
        
        # Step 1: Retrieve relevant context
        retrieval_start = time.time()
        results_dict = {}
        
        # BM25 retrieval
        if 'bm25' in request.retrieval_methods and app_state.get('bm25_retriever'):
            bm25_results = app_state['bm25_retriever'].search(
                query=request.message,
                top_k=request.top_k,
                language=request.language
            )
            results_dict['bm25'] = bm25_results
        
        # ColBERT retrieval
        if 'colbert' in request.retrieval_methods and app_state.get('colbert_retriever'):
            try:
                colbert_results = app_state['colbert_retriever'].search(
                    query=request.message,
                    top_k=request.top_k,
                    language=request.language
                )
                results_dict['colbert'] = colbert_results
            except Exception as e:
                logger.warning(f"ColBERT search failed: {e}")
        
        # Graph retrieval
        if 'graph' in request.retrieval_methods and app_state.get('graph_retriever'):
            try:
                graph_results = app_state['graph_retriever'].search(
                    query=request.message,
                    top_k=request.top_k,
                    language=request.language
                )
                results_dict['graph'] = graph_results
            except Exception as e:
                logger.warning(f"Graph search failed: {e}")
        
        # Fusion
        fused_results = reciprocal_rank_fusion(
            results_dict=results_dict,
            k=60,
            top_k=request.top_k
        )
        
        retrieval_time = (time.time() - retrieval_start) * 1000
        
        # Step 2: Generate response with Gemini
        generation_start = time.time()
        
        # Convert fused results to dict format for chat service
        retrieved_chunks = [
            {
                'text': r.text,
                'rrf_score': r.rrf_score,
                'doc_id': r.doc_id,
                'chunk_id': r.chunk_id
            }
            for r in fused_results
        ]
        
        # Convert conversation history to dict format
        conversation_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in request.conversation_history
        ]
        
        # Generate response
        response_text = app_state['chat_service'].generate_response(
            query=request.message,
            retrieved_chunks=retrieved_chunks,
            conversation_history=conversation_history,
            language=request.language
        )
        
        generation_time = (time.time() - generation_start) * 1000
        
        # Convert results to response format
        response_results = [
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
        
        logger.info(f"[{request_id}] Chat completed in {total_time:.2f}ms")
        
        return ChatResponse(
            message=response_text,
            retrieved_chunks=response_results,
            retrieval_time_ms=retrieval_time,
            generation_time_ms=generation_time,
            total_time_ms=total_time
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
