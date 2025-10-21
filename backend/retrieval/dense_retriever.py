"""
Dense Neural Retrieval Implementation using Sentence Transformers
Alternative to ColBERT providing semantic search via dense embeddings

This implementation uses bi-encoder architecture similar to ColBERT's approach
but with more stable dependencies and faster inference.

Reference: Reimers & Gurevych, "Sentence-BERT: Sentence Embeddings using 
Siamese BERT-Networks", EMNLP 2019
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
import os

logger = logging.getLogger(__name__)

# Try to import Qdrant (optional)
QDRANT_AVAILABLE = False
try:
    from backend.storage.qdrant_client import QdrantVectorStore
    QDRANT_AVAILABLE = True
except ImportError:
    logger.warning("Qdrant not available, using in-memory storage")

@dataclass
class DenseResult:
    """Dense retrieval result with metadata"""
    doc_id: str
    score: float
    rank: int
    text: str
    language: str
    chunk_id: str

class DenseRetriever:
    """
    Dense neural retrieval using Sentence Transformers
    
    This provides semantic search capabilities similar to ColBERT but uses
    sentence-level embeddings instead of token-level embeddings.
    
    Model: all-MiniLM-L6-v2 (22M parameters)
    - Faster than ColBERT (110M params)
    - More stable dependencies
    - Better multilingual support
    - 384-dimensional embeddings
    
    Architecture:
    - Bi-encoder: Separate encoding for queries and documents
    - Cosine similarity for ranking
    - Efficient batch processing
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "auto",
        use_qdrant: bool = True
    ):
        """
        Initialize dense retriever with optional Qdrant storage
        
        Args:
            model_name: Sentence Transformer model name
                - all-MiniLM-L6-v2: Fast, good quality (default)
                - all-mpnet-base-v2: Better quality, slower
                - paraphrase-multilingual-MiniLM-L12-v2: Multilingual
            device: 'cpu', 'cuda', 'mps', or 'auto'
            use_qdrant: Use Qdrant for persistent storage (default: True)
        """
        logger.info(f"Initializing DenseRetriever with model: {model_name}")
        
        try:
            if device == "auto":
                from backend.utils.device import resolve_device
                resolved_device = resolve_device()
            else:
                resolved_device = device

            self.model = SentenceTransformer(model_name, device=resolved_device)
            self.model_name = model_name
            self.documents: Dict[str, Dict] = {}
            self.doc_ids: List[str] = []
            
            # Initialize Qdrant (required, no in-memory fallback)
            self.qdrant_store = None
            self.use_qdrant = use_qdrant and QDRANT_AVAILABLE
            
            if not QDRANT_AVAILABLE:
                raise ImportError(
                    "Qdrant is required but not available. "
                    "Please install: pip install qdrant-client"
                )
            
            if self.use_qdrant:
                qdrant_url = os.getenv('QDRANT_URL')
                qdrant_key = os.getenv('QDRANT_API_KEY')
                collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'documents')
                
                if not qdrant_url or not qdrant_key:
                    raise ValueError(
                        "Qdrant credentials not found. "
                        "Please set QDRANT_URL and QDRANT_API_KEY environment variables."
                    )
                
                embedding_dim = self.model.get_sentence_embedding_dimension()
                self.qdrant_store = QdrantVectorStore(
                    url=qdrant_url,
                    api_key=qdrant_key,
                    collection_name=collection_name,
                    vector_size=embedding_dim
                )
                logger.info("✅ Using Qdrant for persistent vector storage")
            else:
                raise ValueError(
                    "use_qdrant must be True. In-memory storage is not supported."
                )
            
            # Check if Qdrant already has vectors (from previous session)
            self.indexed = False
            if self.qdrant_store:
                try:
                    info = self.qdrant_store.get_collection_info()
                    vector_count = info.get('vectors_count', 0)
                    if vector_count > 0:
                        self.indexed = True
                        logger.info(f"✅ Found {vector_count} existing vectors in Qdrant")
                except Exception as e:
                    logger.warning(f"Could not check Qdrant vectors: {e}")
            
            logger.info(
                "✅ DenseRetriever initialized (device=%s, embedding dim=%d, storage=Qdrant, indexed=%s)",
                resolved_device,
                self.model.get_sentence_embedding_dimension(),
                self.indexed
            )
        except Exception as e:
            logger.error(f"Failed to initialize DenseRetriever: {e}")
            raise
    
    def index_documents(
        self, 
        documents: List[Dict],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> None:
        """
        Index documents by generating dense embeddings and storing in Qdrant or memory
        
        Args:
            documents: List of dicts with keys: id, text, language, metadata
            batch_size: Number of documents to encode at once
            show_progress: Show progress bar during encoding
        """
        logger.info(f"Indexing {len(documents)} documents with dense embeddings...")
        
        if not documents:
            logger.warning("No documents to index")
            return
        
        # Store document metadata
        self.documents = {doc['id']: doc for doc in documents}
        self.doc_ids = [doc['id'] for doc in documents]
        
        # Extract text for encoding
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        try:
            logger.info("Generating embeddings...")
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 normalization for cosine similarity
            )
            
            # Store in Qdrant with full metadata (aligned with Neo4j chunks)
            payloads = [
                {
                    'text': doc['text'],
                    'language': doc.get('language', 'unknown'),
                    'metadata': doc.get('metadata', {})
                }
                for doc in documents
            ]
            self.qdrant_store.add_vectors(
                ids=self.doc_ids,  # Uses chunk_id (e.g., "doc123_chunk_0") - aligned with Neo4j
                vectors=embeddings,
                payloads=payloads
            )
            logger.info(
                f"✅ Stored {len(documents)} vectors in Qdrant "
                f"(chunk IDs aligned with Neo4j: {self.doc_ids[0] if self.doc_ids else 'N/A'}...)"
            )
            
            self.indexed = True
            logger.info(f"✅ Successfully indexed {len(documents)} documents")
            logger.info(f"   Embedding shape: {embeddings.shape}")
            
        except Exception as e:
            logger.error(f"Error during indexing: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        language: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[DenseResult]:
        """
        Search documents using dense embeddings and cosine similarity
        
        Args:
            query: Search query string
            top_k: Number of results to return
            language: Optional language filter ('en', 'ar', 'es')
            min_score: Minimum similarity score threshold (0.0 to 1.0)
        
        Returns:
            List of DenseResult objects sorted by similarity score
        """
        # Check if we have data to search in Qdrant
        try:
            info = self.qdrant_store.get_collection_info()
            if info.get('vectors_count', 0) == 0:
                logger.warning("No vectors in Qdrant collection")
                return []
        except Exception as e:
            logger.error(f"Error checking Qdrant: {e}")
            return []
        
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        
        try:
            # Encode query
            query_embedding = self.model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            
            # Search in Qdrant
            logger.info(f"🔍 Searching Qdrant vector database (top_k={top_k})")
            search_results = self.qdrant_store.search(
                query_vector=query_embedding,
                top_k=top_k * 2  # Get extra to allow for filtering
            )
            logger.info(f"✅ Qdrant returned {len(search_results)} candidate results")
            
            # Build results from Qdrant response
            results = []
            for hit in search_results:
                score = float(hit['score'])
                
                # Apply minimum score filter
                if score < min_score:
                    continue
                
                doc_id = hit['id']  # This is the chunk_id aligned with Neo4j
                payload = hit['payload']
                
                # Apply language filter if specified
                if language and payload.get('language') != language:
                    continue
                
                # Get document metadata (prefer from memory, fallback to payload)
                doc = self.documents.get(doc_id, {'text': payload.get('text', '')})
                
                results.append(DenseResult(
                    doc_id=doc_id,
                    chunk_id=doc_id,  # Aligned with Neo4j Chunk.id
                    score=score,
                    rank=len(results) + 1,
                    text=payload.get('text', doc.get('text', '')),
                    language=payload.get('language', 'unknown')
                ))
                
                if len(results) >= top_k:
                    break
            
            logger.info(f"Found {len(results)} results (min_score={min_score})")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

    def clear_index(self) -> None:
        """Reset cached documents and embeddings in Qdrant."""
        self.documents = {}
        self.doc_ids = []
        
        try:
            self.qdrant_store.clear_collection()
            logger.info("Cleared Qdrant collection")
        except Exception as e:
            logger.error(f"Error clearing Qdrant: {e}")
            raise
        
        self.indexed = False
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Normalized embedding vector
        """
        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
    
    def get_document_score(self, query: str, doc_id: str) -> float:
        """
        Get similarity score for a specific document from Qdrant
        
        Args:
            query: Search query
            doc_id: Document/chunk identifier (aligned with Neo4j)
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self.indexed:
            return 0.0
        
        try:
            # Encode query
            query_embedding = self.get_embedding(query)
            
            # Search for this specific document in Qdrant
            results = self.qdrant_store.search(
                query_vector=query_embedding,
                top_k=100  # Get enough to find our target
            )
            
            # Find the score for the requested doc_id
            for hit in results:
                if hit['id'] == doc_id:
                    return float(hit['score'])
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error computing document score: {e}")
            return 0.0
    
    
    def get_stats(self) -> Dict:
        """Get retriever statistics"""
        stats = {
            'model_name': self.model_name,
            'indexed': self.indexed,
            'num_documents': len(self.documents),
            'embedding_dim': self.model.get_sentence_embedding_dimension(),
            'storage': 'Qdrant'
        }
        
        try:
            qdrant_info = self.qdrant_store.get_collection_info()
            stats['qdrant_vectors'] = qdrant_info.get('vectors_count', 0)
        except Exception as e:
            logger.warning(f"Could not get Qdrant stats: {e}")
        
        return stats
