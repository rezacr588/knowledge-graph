"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

class LanguageEnum(str, Enum):
    """Supported languages"""
    EN = "en"
    AR = "ar"
    ES = "es"

class RetrievalMethodEnum(str, Enum):
    """Available retrieval methods"""
    BM25 = "bm25"
    DENSE = "dense"  # Dense neural retrieval (sentence transformers)
    COLBERT = "colbert"  # Alias for dense (backward compatibility)
    GRAPH = "graph"

class IngestRequest(BaseModel):
    """Request model for document ingestion"""
    language: Optional[LanguageEnum] = Field(
        default=LanguageEnum.EN,
        description="Document language"
    )
    metadata: Optional[Dict] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

class IngestResponse(BaseModel):
    """Response model for document ingestion"""
    document_id: str = Field(description="Unique document identifier")
    chunks_created: int = Field(description="Number of chunks created")
    entities_extracted: int = Field(description="Number of entities extracted")
    relationships_found: int = Field(description="Number of relationships found")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    status: str = Field(default="success", description="Processing status")

class QueryRequest(BaseModel):
    """Request model for hybrid search query"""
    query: str = Field(..., description="Search query", min_length=1)
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results")
    language: Optional[LanguageEnum] = Field(
        default=LanguageEnum.EN,
        description="Query language"
    )
    include_answer: bool = Field(
        default=False,
        description="Generate LLM answer"
    )
    retrieval_methods: List[RetrievalMethodEnum] = Field(
        default=[RetrievalMethodEnum.BM25, RetrievalMethodEnum.DENSE, RetrievalMethodEnum.GRAPH],
        description="Retrieval methods to use"
    )
    rrf_k: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="RRF k parameter"
    )

class RetrievalResult(BaseModel):
    """Individual retrieval result"""
    doc_id: str = Field(description="Document identifier")
    chunk_id: str = Field(description="Chunk identifier")
    text: str = Field(description="Retrieved text")
    rrf_score: float = Field(description="RRF fusion score")
    rank: int = Field(description="Result rank")
    language: str = Field(description="Content language")
    method_scores: Dict[str, float] = Field(
        description="Scores from each retrieval method"
    )
    method_ranks: Dict[str, int] = Field(
        description="Ranks from each retrieval method"
    )

class QueryResponse(BaseModel):
    """Response model for hybrid search query"""
    results: List[RetrievalResult] = Field(description="Retrieval results")
    answer: Optional[str] = Field(default=None, description="Generated answer")
    retrieval_time_ms: float = Field(description="Retrieval time in milliseconds")
    fusion_time_ms: float = Field(description="Fusion time in milliseconds")
    total_time_ms: float = Field(description="Total processing time")
    methods_used: List[str] = Field(description="Retrieval methods used")

class HealthStatus(str, Enum):
    """Health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class DependencyStatus(BaseModel):
    """Status of a single dependency"""
    available: bool
    message: Optional[str] = None

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: HealthStatus = Field(description="Overall system health")
    dependencies: Dict[str, DependencyStatus] = Field(
        description="Status of each dependency"
    )
    uptime_seconds: float = Field(description="System uptime")
    version: str = Field(description="Application version")

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    timestamp: Optional[str] = Field(default=None, description="Message timestamp")

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message", min_length=1)
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous messages in the conversation"
    )
    top_k: int = Field(default=5, ge=1, le=20, description="Number of context chunks to retrieve")
    language: Optional[LanguageEnum] = Field(
        default=LanguageEnum.EN,
        description="Message language"
    )
    retrieval_methods: List[RetrievalMethodEnum] = Field(
        default=[RetrievalMethodEnum.BM25, RetrievalMethodEnum.COLBERT, RetrievalMethodEnum.GRAPH],
        description="Retrieval methods to use"
    )

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(description="Assistant's response")
    retrieved_chunks: List[RetrievalResult] = Field(
        description="Context chunks used for response"
    )
    retrieval_time_ms: float = Field(description="Time to retrieve context")
    generation_time_ms: float = Field(description="Time to generate response")
    total_time_ms: float = Field(description="Total processing time")
