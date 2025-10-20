"""
ColBERT Dense Retrieval Implementation
Reference: Santhanam et al., "ColBERTv2: Effective and Efficient Retrieval 
via Lightweight Late Interaction", NAACL 2022

ColBERT scoring formula:
MaxSim(Q, D) = Σ_{q∈Q} max_{d∈D} (E_q · E_d^T)

Where:
- Q: Query token embeddings
- D: Document token embeddings  
- E_q, E_d: Embedding vectors
- · : Dot product
"""

from ragatouille import RAGPretrainedModel
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ColBERTResult:
    """ColBERT search result with metadata"""
    doc_id: str
    score: float
    rank: int
    text: str
    language: str
    embedding_id: str

class ColBERTRetriever:
    """
    ColBERT retrieval using late-interaction mechanism
    
    Model: colbert-ir/colbertv2.0 (110M parameters)
    Paper: https://arxiv.org/abs/2112.01488
    
    Late-interaction allows fine-grained token-level matching between
    query and document, improving accuracy especially for:
    - Technical documents
    - Multi-lingual content
    - Long documents with diverse topics
    """
    
    def __init__(
        self,
        index_name: str = "colbert_index",
        model_name: str = "colbert-ir/colbertv2.0"
    ):
        """
        Initialize ColBERT retriever
        
        Args:
            index_name: Name for the index
            model_name: Hugging Face model name
        """
        logger.info(f"Initializing ColBERT with model: {model_name}")
        
        # Initialize RAGatouille model (handles ColBERT)
        self.model = RAGPretrainedModel.from_pretrained(model_name)
        self.index_name = index_name
        self.documents: Dict[str, Dict] = {}
        self.indexed = False
        
        logger.info("✅ ColBERT retriever initialized")
    
    def _generate_doc_id_hash(self, doc_id: str) -> str:
        """Generate unique hash for document ID"""
        return hashlib.md5(doc_id.encode()).hexdigest()
    
    def index_documents(
        self, 
        documents: List[Dict],
        max_document_length: int = 256
    ) -> None:
        """
        Index documents using ColBERT embeddings
        
        Args:
            documents: List of dicts with keys: id, text, language, metadata
            max_document_length: Max tokens per document chunk
        
        Note: ColBERT generates multiple embeddings per document (one per token).
        For storage efficiency, we use RAGatouille's built-in indexing.
        """
        logger.info(f"Indexing {len(documents)} documents with ColBERT...")
        
        # Store documents in memory for retrieval
        for doc in documents:
            self.documents[doc['id']] = doc
        
        # Use RAGatouille's index method for efficient storage
        try:
            self.model.index(
                collection=[doc['text'] for doc in documents],
                document_ids=[doc['id'] for doc in documents],
                document_metadatas=[{
                    'language': doc.get('language', 'en'),
                    'metadata': doc.get('metadata', {})
                } for doc in documents],
                index_name=self.index_name,
                max_document_length=max_document_length,
                split_documents=True
            )
            
            self.indexed = True
            logger.info(f"✅ Successfully indexed {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error during indexing: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        language: Optional[str] = None
    ) -> List[ColBERTResult]:
        """
        Search documents using ColBERT late-interaction
        
        Args:
            query: Search query string
            top_k: Number of results to return
            language: Optional language filter ('en', 'ar', 'es')
        
        Returns:
            List of ColBERTResult objects sorted by MaxSim score
        
        MaxSim Scoring:
            For each query token, find maximum similarity with any document token.
            Sum these maximum similarities across all query tokens.
            Higher scores indicate better matches.
        """
        if not self.indexed:
            logger.warning("No documents indexed yet")
            return []
            
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        
        try:
            # RAGatouille handles the late-interaction scoring internally
            results = self.model.search(
                query=query,
                k=top_k,
                index_name=self.index_name
            )
            
            # Convert to ColBERTResult format
            colbert_results = []
            for rank, result in enumerate(results, start=1):
                doc_id = result['document_id']
                doc = self.documents.get(doc_id, {})
                
                # Filter by language if specified
                if language and doc.get('language') != language:
                    continue
                
                colbert_results.append(ColBERTResult(
                    doc_id=doc_id,
                    score=float(result['score']),
                    rank=rank,
                    text=result['content'],
                    language=doc.get('language', 'unknown'),
                    embedding_id=self._generate_doc_id_hash(doc_id)
                ))
            
            logger.info(f"Found {len(colbert_results)} results")
            return colbert_results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

    def clear_index(self) -> None:
        """Remove indexed documents and drop the ColBERT index if available."""
        self.documents = {}
        self.indexed = False

        try:
            if hasattr(self.model, "delete_index"):
                self.model.delete_index(self.index_name)
            elif hasattr(self.model, "reset_index"):
                self.model.reset_index(self.index_name)
        except Exception as exc:
            logger.warning("Failed to clear ColBERT index '%s': %s", self.index_name, exc)
        else:
            logger.info("Cleared ColBERT index '%s'", self.index_name)
