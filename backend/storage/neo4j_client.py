"""
Neo4j Graph Database Client
Handles entity storage, relationship management, and graph traversal
"""

from neo4j import GraphDatabase
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Entity:
    """Entity node in knowledge graph"""
    id: str
    name: str
    type: str  # PERSON, ORGANIZATION, LOCATION, CONCEPT, etc.
    language: str
    confidence: float
    metadata: Dict

@dataclass
class Relationship:
    """Relationship edge in knowledge graph"""
    source_id: str
    target_id: str
    type: str  # RELATED_TO, PART_OF, LOCATED_IN, etc.
    confidence: float
    metadata: Dict

class Neo4jClient:
    """
    Neo4j client for knowledge graph operations
    
    Graph Schema:
        (:Document {id, title, language, content_hash})
        (:Chunk {id, text, language, embedding_id, doc_id})
        (:Entity {id, name, type, language, confidence})
        
        (Document)-[:CONTAINS]->(Chunk)
        (Chunk)-[:MENTIONS {confidence}]->(Entity)
        (Entity)-[:RELATES_TO {type, confidence}]->(Entity)
        (Entity)-[:SAME_AS {confidence}]->(Entity)  # Cross-language linking
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize Neo4j client
        
        Args:
            uri: Neo4j connection URI (e.g., neo4j+s://abc.databases.neo4j.io)
            username: Neo4j username (typically 'neo4j')
            password: Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info(f"Connected to Neo4j at {uri}")
        
        # Create constraints and indexes
        self._setup_schema()
    
    def _setup_schema(self):
        """Create constraints and indexes for optimal performance"""
        constraints = [
            # Unique constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            
            # Indexes for fast lookups
            "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.language)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Chunk) ON (c.doc_id)",
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created: {constraint[:50]}...")
                except Exception as e:
                    logger.warning(f"Constraint/index already exists or error: {e}")
    
    def add_document(
        self,
        doc_id: str,
        title: str,
        language: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add document node to graph
        
        Args:
            doc_id: Unique document identifier
            title: Document title
            language: Document language code
            metadata: Additional metadata
        """
        # Build query dynamically based on whether metadata exists
        if metadata:
            query = """
            MERGE (d:Document {id: $doc_id})
            SET d.title = $title,
                d.language = $language,
                d.metadata = $metadata,
                d.created_at = datetime()
            RETURN d
            """
            params = {
                "doc_id": doc_id,
                "title": title,
                "language": language,
                "metadata": metadata
            }
        else:
            query = """
            MERGE (d:Document {id: $doc_id})
            SET d.title = $title,
                d.language = $language,
                d.created_at = datetime()
            RETURN d
            """
            params = {
                "doc_id": doc_id,
                "title": title,
                "language": language
            }
        
        with self.driver.session() as session:
            session.run(query, **params)
        
        logger.info(f"Added document: {doc_id}")
    
    def add_chunk(
        self,
        chunk_id: str,
        doc_id: str,
        text: str,
        language: str,
        embedding_id: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add chunk node and link to document
        
        Args:
            chunk_id: Unique chunk identifier
            doc_id: Parent document ID
            text: Chunk text content
            language: Chunk language
            embedding_id: Vector embedding identifier
            metadata: Additional metadata (e.g., page number, section)
        """
        # Build query dynamically based on whether metadata exists
        if metadata:
            query = """
            MATCH (d:Document {id: $doc_id})
            MERGE (c:Chunk {id: $chunk_id})
            SET c.text = $text,
                c.language = $language,
                c.embedding_id = $embedding_id,
                c.doc_id = $doc_id,
                c.metadata = $metadata
            MERGE (d)-[:CONTAINS]->(c)
            RETURN c
            """
            params = {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "text": text,
                "language": language,
                "embedding_id": embedding_id,
                "metadata": metadata
            }
        else:
            query = """
            MATCH (d:Document {id: $doc_id})
            MERGE (c:Chunk {id: $chunk_id})
            SET c.text = $text,
                c.language = $language,
                c.embedding_id = $embedding_id,
                c.doc_id = $doc_id
            MERGE (d)-[:CONTAINS]->(c)
            RETURN c
            """
            params = {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "text": text,
                "language": language,
                "embedding_id": embedding_id
            }
        
        with self.driver.session() as session:
            session.run(query, **params)
        
        logger.debug(f"Added chunk: {chunk_id} to document: {doc_id}")
    
    def add_entity(self, entity: Entity) -> None:
        """
        Add or update entity node
        
        Args:
            entity: Entity object
        """
        # Build query dynamically based on whether metadata exists
        if entity.metadata:
            query = """
            MERGE (e:Entity {id: $id})
            SET e.name = $name,
                e.type = $type,
                e.language = $language,
                e.confidence = $confidence,
                e.metadata = $metadata,
                e.updated_at = datetime()
            RETURN e
            """
            params = {
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "language": entity.language,
                "confidence": entity.confidence,
                "metadata": entity.metadata
            }
        else:
            query = """
            MERGE (e:Entity {id: $id})
            SET e.name = $name,
                e.type = $type,
                e.language = $language,
                e.confidence = $confidence,
                e.updated_at = datetime()
            RETURN e
            """
            params = {
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "language": entity.language,
                "confidence": entity.confidence
            }
        
        with self.driver.session() as session:
            session.run(query, **params)
    
    def link_chunk_to_entity(
        self,
        chunk_id: str,
        entity_id: str,
        confidence: float
    ) -> None:
        """
        Create MENTIONS relationship between chunk and entity
        
        Args:
            chunk_id: Chunk identifier
            entity_id: Entity identifier
            confidence: Mention confidence score
        """
        query = """
        MATCH (c:Chunk {id: $chunk_id})
        MATCH (e:Entity {id: $entity_id})
        MERGE (c)-[m:MENTIONS]->(e)
        SET m.confidence = $confidence
        RETURN c, m, e
        """
        
        with self.driver.session() as session:
            session.run(
                query,
                chunk_id=chunk_id,
                entity_id=entity_id,
                confidence=confidence
            )
    
    def add_relationship(self, relationship: Relationship) -> None:
        """
        Create relationship between two entities
        
        Args:
            relationship: Relationship object
        """
        # Build query dynamically based on whether metadata exists
        if relationship.metadata:
            query = """
            MATCH (e1:Entity {id: $source_id})
            MATCH (e2:Entity {id: $target_id})
            MERGE (e1)-[r:RELATES_TO {type: $rel_type}]->(e2)
            SET r.confidence = $confidence,
                r.metadata = $metadata
            RETURN r
            """
            params = {
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "rel_type": relationship.type,
                "confidence": relationship.confidence,
                "metadata": relationship.metadata
            }
        else:
            query = """
            MATCH (e1:Entity {id: $source_id})
            MATCH (e2:Entity {id: $target_id})
            MERGE (e1)-[r:RELATES_TO {type: $rel_type}]->(e2)
            SET r.confidence = $confidence
            RETURN r
            """
            params = {
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "rel_type": relationship.type,
                "confidence": relationship.confidence
            }
        
        with self.driver.session() as session:
            session.run(query, **params)
    
    def find_entities_by_name(
        self,
        name: str,
        language: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find entities by name (fuzzy match)
        
        Args:
            name: Entity name to search
            language: Optional language filter
            limit: Maximum number of results
        
        Returns:
            List of entity dictionaries
        """
        if language:
            query = """
            MATCH (e:Entity)
            WHERE e.name CONTAINS $name AND e.language = $language
            RETURN e
            ORDER BY e.confidence DESC
            LIMIT $limit
            """
            params = {"name": name, "language": language, "limit": limit}
        else:
            query = """
            MATCH (e:Entity)
            WHERE e.name CONTAINS $name
            RETURN e
            ORDER BY e.confidence DESC
            LIMIT $limit
            """
            params = {"name": name, "limit": limit}
        
        with self.driver.session() as session:
            result = session.run(query, **params)
            return [dict(record["e"]) for record in result]
    
    def find_chunks_by_entities(
        self,
        entity_ids: List[str],
        top_k: int = 10
    ) -> List[Dict]:
        """
        Find chunks that mention given entities
        
        Args:
            entity_ids: List of entity IDs
            top_k: Maximum number of chunks to return
        
        Returns:
            List of chunk dictionaries with scores
        """
        query = """
        MATCH (c:Chunk)-[m:MENTIONS]->(e:Entity)
        WHERE e.id IN $entity_ids
        WITH c, sum(m.confidence * e.confidence) as score
        ORDER BY score DESC
        LIMIT $top_k
        RETURN c, score
        """
        
        with self.driver.session() as session:
            result = session.run(query, entity_ids=entity_ids, top_k=top_k)
            return [
                {**dict(record["c"]), "score": record["score"]}
                for record in result
            ]
    
    def get_graph_stats(self) -> Dict:
        """
        Get statistics about the knowledge graph
        
        Returns:
            Dictionary with node and relationship counts
        """
        with self.driver.session() as session:
            # Count each type separately to avoid cross-product issues
            doc_count = session.run("MATCH (d:Document) RETURN count(d) as count").single()['count']
            chunk_count = session.run("MATCH (c:Chunk) RETURN count(c) as count").single()['count']
            entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()['count']
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()['count']
            
            return {
                'documents': doc_count,
                'chunks': chunk_count,
                'entities': entity_count,
                'relationships': rel_count
            }
    
    def get_graph_visualization_data(self, limit: int = 100) -> Dict:
        """
        Get graph data for visualization
        
        Args:
            limit: Maximum number of nodes to return
        
        Returns:
            Dictionary with nodes and edges for visualization
        """
        with self.driver.session() as session:
            # Get entities
            entities_query = """
            MATCH (e:Entity)
            RETURN e.id as id, e.name as name, e.type as type, 
                   e.language as language, e.confidence as confidence
            ORDER BY e.confidence DESC
            LIMIT $limit
            """
            
            entities_result = session.run(entities_query, limit=limit)
            entities = []
            entity_ids = []
            
            for record in entities_result:
                entity = {
                    'id': record['id'],
                    'name': record['name'],
                    'type': record['type'],
                    'language': record['language'],
                    'confidence': record['confidence']
                }
                entities.append(entity)
                entity_ids.append(record['id'])
            
            # Get relationships between these entities
            relationships = []
            if entity_ids:
                rels_query = """
                MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
                WHERE e1.id IN $entity_ids AND e2.id IN $entity_ids
                RETURN e1.id as source, e2.id as target, 
                       r.type as type, r.confidence as confidence
                LIMIT 200
                """
                
                rels_result = session.run(rels_query, entity_ids=entity_ids)
                for record in rels_result:
                    relationships.append({
                        'source': record['source'],
                        'target': record['target'],
                        'type': record['type'],
                        'confidence': record['confidence']
                    })
            
            # Get chunk connections
            chunk_connections = []
            if entity_ids:
                chunks_query = """
                MATCH (c:Chunk)-[m:MENTIONS]->(e:Entity)
                WHERE e.id IN $entity_ids
                RETURN c.id as chunk_id, c.text as chunk_text,
                       e.id as entity_id, m.confidence as confidence
                LIMIT 200
                """
                
                chunks_result = session.run(chunks_query, entity_ids=entity_ids)
                for record in chunks_result:
                    chunk_connections.append({
                        'chunk_id': record['chunk_id'],
                        'chunk_text': record['chunk_text'][:100] if record['chunk_text'] else '',
                        'entity_id': record['entity_id'],
                        'confidence': record['confidence']
                    })
            
            return {
                'nodes': entities,
                'edges': relationships,
                'chunk_connections': chunk_connections,
                'stats': self.get_graph_stats()
            }
    
    def clear_database(self) -> None:
        """Remove all nodes and relationships from the Neo4j database."""
        query = "MATCH (n) DETACH DELETE n"

        with self.driver.session() as session:
            session.run(query)

        logger.info("Cleared all nodes and relationships from Neo4j")

    def close(self):
        """Close Neo4j driver connection"""
        self.driver.close()
        logger.info("Neo4j connection closed")
