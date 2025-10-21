"""
Document ingestion routes
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import StreamingResponse
import uuid
import time
import hashlib
import json
import asyncio

from backend.models.schemas import IngestResponse
from backend.utils.logger import setup_logger
from backend.storage.neo4j_client import Entity
import os

router = APIRouter(prefix="/ingest", tags=["ingestion"])
logger = setup_logger(os.getenv('LOG_LEVEL', 'INFO'))


def get_app_state():
    """Get app_state from main module"""
    from backend.main import app_state
    return app_state


@router.post("/stream")
async def ingest_document_stream(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Ingest document with real-time progress updates via Server-Sent Events (SSE)
    """
    app_state = get_app_state()
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
            doc_objects = [
                {
                    "id": f"{doc_id}_chunk_{i}",
                    "text": chunk_text,
                    "language": language,
                    "metadata": {
                        "document_id": doc_id,
                        "chunk_index": i,
                        "source": filename
                    }
                }
                for i, chunk_text in enumerate(chunks)
            ]
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
                            entity_id = f"{entity.name}_{entity.type}".replace(" ", "_")
                            
                            # Create Entity object
                            entity_obj = Entity(
                                id=entity_id,
                                name=entity.name,
                                type=entity.type,
                                language=entity.language,
                                confidence=entity.confidence,
                                metadata={}
                            )
                            app_state['neo4j_client'].add_entity(entity_obj)
                            
                            # Link chunk to entity
                            app_state['neo4j_client'].link_chunk_to_entity(
                                chunk_id=chunk_id,
                                entity_id=entity_id,
                                confidence=entity.confidence
                            )
                            relationships_count += 1
                
                await asyncio.sleep(0.05)  # Small delay for real-time feel
            
            # Merge new chunks with existing in-memory documents
            existing_docs = {
                doc['id']: doc
                for doc in app_state.get('documents', [])
                if isinstance(doc, dict) and doc.get('id')
            }
            for doc in doc_objects:
                existing_docs[doc['id']] = doc
            app_state['documents'] = list(existing_docs.values())

            # Persist to disk if configured
            if app_state.get('chunk_store'):
                app_state['documents'] = app_state['chunk_store'].upsert(app_state['documents'])
                logger.info(
                    f"[{request_id}] Persisted {len(doc_objects)} chunks "
                    f"(total stored: {len(app_state['documents'])})"
                )

            # Stage 5: Building BM25 index
            yield update_progress("indexing_bm25", 85, "Building BM25 search index...")
            if app_state.get('bm25_retriever') and app_state['documents']:
                app_state['bm25_retriever'].index_documents(app_state['documents'])
            await asyncio.sleep(0.2)
            
            # Stage 6: Building dense index (if available)
            if app_state.get('dense_retriever'):
                yield update_progress("indexing_dense", 92, "Building dense embeddings...")
                try:
                    dense_retriever = app_state['dense_retriever']
                    if getattr(dense_retriever, "use_qdrant", False) and dense_retriever.use_qdrant:
                        dense_retriever.index_documents(doc_objects)
                    elif app_state['documents']:
                        dense_retriever.index_documents(app_state['documents'])
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


@router.post("", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    language: str = Form("en"),
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
    app_state = get_app_state()
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"[{request_id}] Ingesting document: {file.filename}")
    
    try:
        from backend.main import reset_ingested_content
        
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

        doc_objects = [
            {
                "id": f"{doc_id}_chunk_{i}",
                "text": chunk_text,
                "language": language,
                "metadata": {
                    "document_id": doc_id,
                    "chunk_index": i,
                    "source": file.filename
                }
            }
            for i, chunk_text in enumerate(chunks)
        ]
        
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
                    entities_count += len(entities)
                    
                    # Add entities to graph
                    for entity in entities:
                        entity_id = f"{entity.name}_{entity.type}".replace(" ", "_")
                        
                        # Create Entity object
                        entity_obj = Entity(
                            id=entity_id,
                            name=entity.name,
                            type=entity.type,
                            language=entity.language,
                            confidence=entity.confidence,
                            metadata={}
                        )
                        app_state['neo4j_client'].add_entity(entity_obj)
                        
                        # Link chunk to entity
                        app_state['neo4j_client'].link_chunk_to_entity(
                            chunk_id=chunk_id,
                            entity_id=entity_id,
                            confidence=entity.confidence
                        )

        # Merge new chunks with existing in-memory documents
        existing_docs = {
            doc['id']: doc for doc in app_state.get('documents', []) if isinstance(doc, dict) and doc.get('id')
        }
        for doc in doc_objects:
            existing_docs[doc['id']] = doc
        app_state['documents'] = list(existing_docs.values())

        # Persist to disk if configured
        if app_state.get('chunk_store'):
            app_state['documents'] = app_state['chunk_store'].upsert(app_state['documents'])
            logger.info(
                f"[{request_id}] Persisted {len(doc_objects)} chunks "
                f"(total stored: {len(app_state['documents'])})"
            )
        
        # Add to BM25 index
        if app_state.get('bm25_retriever') and app_state['documents']:
            app_state['bm25_retriever'].index_documents(app_state['documents'])
        
        # Add to dense retriever (if available)
        if app_state.get('dense_retriever') and app_state['documents']:
            try:
                dense_retriever = app_state['dense_retriever']
                if getattr(dense_retriever, "use_qdrant", False) and dense_retriever.use_qdrant:
                    dense_retriever.index_documents(doc_objects)
                else:
                    dense_retriever.index_documents(app_state['documents'])
            except Exception as e:
                logger.warning(f"[{request_id}] Dense indexing failed: {e}")
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"[{request_id}] Ingestion completed in {processing_time:.2f}ms")
        
        return IngestResponse(
            document_id=doc_id,
            chunks_created=len(chunks),
            entities_extracted=entities_count,
            relationships_found=0,  # Legacy
            processing_time_ms=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
