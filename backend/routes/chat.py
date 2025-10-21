"""
Chat routes
"""

from fastapi import APIRouter, HTTPException
import uuid
import time
import os

from backend.models.schemas import ChatRequest, ChatResponse
from backend.utils.logger import setup_logger

router = APIRouter(prefix="/chat", tags=["chat"])
logger = setup_logger(os.getenv('LOG_LEVEL', 'INFO'))


def get_app_state():
    """Get app_state from main module"""
    from backend.main import app_state
    return app_state


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with documents using Gemini
    
    Process:
    1. Retrieve relevant context
    2. Generate response with LLM
    """
    app_state = get_app_state()
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"[{request_id}] Chat query: {request.messages[-1].content}")
    
    try:
        # Get the latest user message
        user_message = request.messages[-1].content
        
        # Retrieve relevant context using hybrid search
        from backend.models.schemas import QueryRequest
        query_request = QueryRequest(
            query=user_message,
            retrieval_methods=['bm25', 'graph'],
            top_k=request.context_chunks,
            language='en'
        )
        
        # Import here to avoid circular dependency
        from backend.routes.query import hybrid_search
        
        search_results = await hybrid_search(query_request)
        
        # Extract context from results
        context = "\n\n".join([
            f"[Chunk {i+1}] {result.text}"
            for i, result in enumerate(search_results.results)
        ])
        
        # Generate response using chat service
        chat_service = app_state.get('chat_service')
        if not chat_service:
            raise HTTPException(status_code=503, detail="Chat service not available")
        
        response = chat_service.generate_response(
            messages=request.messages,
            context=context
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"[{request_id}] Chat response generated in {processing_time:.2f}ms")
        
        return ChatResponse(
            response=response,
            context_used=len(search_results.results),
            processing_time_ms=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
