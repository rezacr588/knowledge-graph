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

logger = logging.getLogger(__name__)

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
        device: str = "auto"
    ):
        """
        Initialize dense retriever
        
        Args:
            model_name: Sentence Transformer model name
                - all-MiniLM-L6-v2: Fast, good quality (default)
                - all-mpnet-base-v2: Better quality, slower
                - paraphrase-multilingual-MiniLM-L12-v2: Multilingual
            device: 'cpu', 'cuda', 'mps', or 'auto'
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
            self.embeddings: Optional[np.ndarray] = None
            self.doc_ids: List[str] = []
            self.indexed = False
            
            logger.info(
                "✅ DenseRetriever initialized (device=%s, embedding dim=%d)",
                resolved_device,
                self.model.get_sentence_embedding_dimension(),
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
        Index documents by generating dense embeddings
        
        Args:
            documents: List of dicts with keys: id, text, language, metadata
            batch_size: Number of documents to encode at once
            show_progress: Show progress bar during encoding
        """
        logger.info(f"Indexing {len(documents)} documents with dense embeddings...")
        
        if not documents:
            logger.warning("No documents to index")
            return
        
        # Store documents
        self.documents = {doc['id']: doc for doc in documents}
        self.doc_ids = [doc['id'] for doc in documents]
        
        # Extract text for encoding
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        try:
            logger.info("Generating embeddings...")
            self.embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 normalization for cosine similarity
            )
            
            self.indexed = True
            logger.info(f"✅ Successfully indexed {len(documents)} documents")
            logger.info(f"   Embedding shape: {self.embeddings.shape}")
            
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
        if not self.indexed or self.embeddings is None:
            logger.warning("No documents indexed yet")
            return []
        
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        
        try:
            # Encode query
            query_embedding = self.model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            
            # Compute cosine similarity with all documents
            # Since embeddings are normalized, dot product = cosine similarity
            similarities = np.dot(self.embeddings, query_embedding)
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1]
            
            # Build results
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                
                # Apply minimum score filter
                if score < min_score:
                    continue
                
                doc_id = self.doc_ids[idx]
                doc = self.documents[doc_id]
                
                # Apply language filter if specified
                if language and doc.get('language') != language:
                    continue
                
                results.append(DenseResult(
                    doc_id=doc_id,
                    chunk_id=doc_id,  # Use doc_id as chunk_id for consistency
                    score=score,
                    rank=len(results) + 1,
                    text=doc['text'],
                    language=doc.get('language', 'unknown')
                ))
                
                # Stop when we have enough results
                if len(results) >= top_k:
                    break
            
            logger.info(f"Found {len(results)} results (min_score={min_score})")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

    def clear_index(self) -> None:
        """Reset cached documents and embeddings."""
        self.documents = {}
        self.doc_ids = []
        self.embeddings = None
        self.indexed = False
        logger.info("Cleared dense retriever index")
    
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
        Get similarity score for a specific document
        
        Args:
            query: Search query
            doc_id: Document identifier
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self.indexed or doc_id not in self.documents:
            return 0.0
        
        try:
            # Find document index
            doc_idx = self.doc_ids.index(doc_id)
            
            # Encode query
            query_embedding = self.get_embedding(query)
            
            # Compute similarity
            doc_embedding = self.embeddings[doc_idx]
            similarity = np.dot(doc_embedding, query_embedding)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing document score: {e}")
            return 0.0
    
    def clear_index(self) -> None:
        """Remove all indexed documents and embeddings"""
        self.documents = {}
        self.embeddings = None
        self.doc_ids = []
        self.indexed = False
        logger.info("Cleared dense retriever index")
    
    def get_stats(self) -> Dict:
        """Get retriever statistics"""
        return {
            'model_name': self.model_name,
            'indexed': self.indexed,
            'num_documents': len(self.documents),
            'embedding_dim': self.model.get_sentence_embedding_dimension() if self.indexed else None,
            'memory_mb': self.embeddings.nbytes / (1024 * 1024) if self.embeddings is not None else 0
        }
