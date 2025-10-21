"""
Qdrant Vector Database Client
Handles vector storage and similarity search for dense retrieval
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional, Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """
    Qdrant client for persistent vector storage
    
    Replaces in-memory numpy storage with cloud-based vector DB
    """
    
    def __init__(
        self,
        url: str,
        api_key: str,
        collection_name: str = "documents",
        vector_size: int = 384
    ):
        """
        Initialize Qdrant client
        
        Args:
            url: Qdrant instance URL
            api_key: Qdrant API key
            collection_name: Collection name for storing vectors
            vector_size: Dimension of embedding vectors
        """
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
            timeout=30
        )
        
        # Create collection if it doesn't exist
        self._ensure_collection()
        
        logger.info(f"✅ Qdrant client initialized: {url}, collection: {collection_name}")
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Collection created: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
            raise
    
    def add_vectors(
        self,
        ids: List[str],
        vectors: np.ndarray,
        payloads: Optional[List[Dict]] = None
    ) -> None:
        """
        Add vectors to Qdrant
        
        Args:
            ids: List of document IDs (must be unique)
            vectors: Numpy array of vectors (n_docs x vector_size)
            payloads: Optional metadata for each vector
        """
        if payloads is None:
            payloads = [{} for _ in ids]
        
        # Use doc_id as point ID (convert to hash for consistency)
        points = [
            PointStruct(
                id=hash(doc_id) & 0x7FFFFFFFFFFFFFFF,  # Use hash of doc_id as point ID (positive int64)
                vector=vector.tolist(),
                payload={**payload, 'doc_id': doc_id}  # Include doc_id in payload
            )
            for doc_id, vector, payload in zip(ids, vectors, payloads)
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"Added {len(points)} vectors to Qdrant")
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional filter conditions
        
        Returns:
            List of dicts with id, score, and payload
        """
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=top_k,
            query_filter=filter_dict
        )
        
        return [
            {
                'id': hit.payload.get('doc_id', str(hit.id)),
                'score': hit.score,
                'payload': hit.payload
            }
            for hit in search_result
        ]
    
    def get_vector(self, point_id: int) -> Optional[np.ndarray]:
        """Get vector by ID"""
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
                with_vectors=True
            )
            if points:
                return np.array(points[0].vector)
            return None
        except Exception as e:
            logger.error(f"Error retrieving vector: {e}")
            return None
    
    def clear_collection(self) -> None:
        """Delete all vectors from collection"""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            self._ensure_collection()
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                'name': self.collection_name,
                'vectors_count': info.points_count,
                'vector_size': self.vector_size,
                'status': info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}
    
    def list_chunks_with_info(
        self,
        limit: Optional[int] = None,
        batch_size: int = 128
    ) -> Tuple[List[Dict], Dict]:
        """
        Retrieve stored chunks and accompanying collection info from Qdrant.

        Args:
            limit: Maximum number of chunks to return (None for all).
            batch_size: Number of records to fetch per scroll call.

        Returns:
            Tuple of (chunk list, collection info dict).
        """
        collected_chunks: List[Dict] = []
        next_offset = None

        while True:
            # Determine batch size respecting requested limit
            current_batch = batch_size
            if limit is not None:
                remaining = limit - len(collected_chunks)
                if remaining <= 0:
                    break
                current_batch = min(batch_size, remaining)

            try:
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=current_batch,
                    offset=next_offset,
                    with_payload=True,
                    with_vectors=False
                )
            except Exception as e:
                logger.error(f"Error scrolling Qdrant collection: {e}")
                raise

            # Handle both tuple and ScrollResult return signatures
            if isinstance(scroll_result, tuple):
                points, next_offset = scroll_result  # Older client versions
            else:
                points = getattr(scroll_result, "points", [])
                next_offset = getattr(
                    scroll_result,
                    "next_page_offset",
                    getattr(scroll_result, "next_offset", None)
                )

            if not points:
                break

            for point in points:
                payload = getattr(point, "payload", {}) or {}
                point_id = getattr(point, "id", None)
                chunk_data = {
                    'point_id': str(point_id) if point_id is not None else None,
                    'doc_id': payload.get('doc_id', str(point_id) if point_id is not None else ""),
                    'text': payload.get('text', ''),
                    'language': payload.get('language', 'unknown'),
                    'payload': payload
                }
                collected_chunks.append(chunk_data)

            if next_offset is None:
                break

        info = self.get_collection_info()
        return collected_chunks, info
    
    def close(self):
        """Close Qdrant connection"""
        # Qdrant client doesn't require explicit close
        logger.info("Qdrant connection closed")
