"""
Graph-based Retrieval using Neo4j Knowledge Graph
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
from backend.storage.neo4j_client import Neo4jClient
from backend.services.entity_extraction import EntityExtractor

logger = logging.getLogger(__name__)

@dataclass
class GraphResult:
    """Graph-based retrieval result"""
    doc_id: str
    chunk_id: str
    score: float
    rank: int
    text: str
    language: str
    entities: List[str]

class GraphRetriever:
    """
    Graph-based retrieval using entity extraction and graph traversal
    """
    
    def __init__(
        self,
        neo4j_client: Neo4jClient,
        entity_extractor: EntityExtractor
    ):
        """
        Initialize graph retriever
        
        Args:
            neo4j_client: Neo4j client instance
            entity_extractor: Entity extraction service
        """
        self.neo4j_client = neo4j_client
        self.entity_extractor = entity_extractor
        logger.info("✅ Graph retriever initialized")
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        language: str = 'en'
    ) -> List[GraphResult]:
        """
        Search using graph traversal
        
        Args:
            query: Search query
            top_k: Number of results to return
            language: Query language
        
        Returns:
            List of graph-based results
        """
        logger.info(f"Graph search for: '{query}'")
        
        # Extract entities from query
        query_entities = self.entity_extractor.extract_entities(query, language)
        
        if not query_entities:
            logger.warning("No entities extracted from query")
            return []
        
        logger.info(f"Extracted {len(query_entities)} entities from query")
        
        # Find matching entities in graph
        entity_ids = []
        for entity in query_entities:
            matches = self.neo4j_client.find_entities_by_name(
                entity.name,
                language=language,
                limit=3
            )
            entity_ids.extend([m['id'] for m in matches])
        
        if not entity_ids:
            logger.warning("No matching entities found in graph")
            return []
        
        logger.info(f"Found {len(entity_ids)} matching entities in graph")
        
        # Find chunks mentioning these entities
        chunks = self.neo4j_client.find_chunks_by_entities(
            entity_ids=entity_ids,
            top_k=top_k
        )
        
        # Convert to GraphResult format
        results = []
        for rank, chunk in enumerate(chunks, start=1):
            results.append(GraphResult(
                doc_id=chunk.get('doc_id', 'unknown'),
                chunk_id=chunk['id'],
                score=float(chunk['score']),
                rank=rank,
                text=chunk['text'],
                language=chunk.get('language', language),
                entities=[e.name for e in query_entities]
            ))
        
        logger.info(f"Found {len(results)} graph-based results")
        return results
