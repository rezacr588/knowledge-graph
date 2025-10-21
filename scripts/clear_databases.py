#!/usr/bin/env python3
"""
Clear all data from Neo4j and Qdrant databases
Use this to start fresh for testing
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from backend.storage.neo4j_client import Neo4jClient
from backend.storage.qdrant_client import QdrantVectorStore

def clear_neo4j():
    """Clear all data from Neo4j database"""
    print("\n🗑️  Clearing Neo4j database...")
    
    try:
        neo4j_uri = os.getenv('NEO4J_URI')
        neo4j_user = os.getenv('NEO4J_USERNAME')
        neo4j_password = os.getenv('NEO4J_PASSWORD')
        
        if not all([neo4j_uri, neo4j_user, neo4j_password]):
            print("❌ Neo4j credentials not found in environment")
            return False
        
        client = Neo4jClient(neo4j_uri, neo4j_user, neo4j_password)
        
        # Get stats before clearing
        stats_before = client.get_graph_stats()
        print(f"   Before: {stats_before}")
        
        # Clear database
        client.clear_database()
        
        # Get stats after clearing
        stats_after = client.get_graph_stats()
        print(f"   After:  {stats_after}")
        
        client.close()
        print("✅ Neo4j cleared successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing Neo4j: {e}")
        return False

def clear_qdrant():
    """Clear all vectors from Qdrant collection"""
    print("\n🗑️  Clearing Qdrant database...")
    
    try:
        qdrant_url = os.getenv('QDRANT_URL')
        qdrant_key = os.getenv('QDRANT_API_KEY')
        collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'documents')
        
        if not all([qdrant_url, qdrant_key]):
            print("❌ Qdrant credentials not found in environment")
            return False
        
        store = QdrantVectorStore(
            url=qdrant_url,
            api_key=qdrant_key,
            collection_name=collection_name,
            vector_size=384
        )
        
        # Get stats before clearing
        info_before = store.get_collection_info()
        print(f"   Before: {info_before['vectors_count']} vectors")
        
        # Clear collection
        store.clear_collection()
        
        # Get stats after clearing
        info_after = store.get_collection_info()
        print(f"   After:  {info_after['vectors_count']} vectors")
        
        print("✅ Qdrant cleared successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing Qdrant: {e}")
        return False

def main():
    print("=" * 60)
    print("DATABASE CLEANUP UTILITY")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete ALL data from:")
    print("   - Neo4j (documents, chunks, entities, relationships)")
    print("   - Qdrant (all vectors)")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Cleanup cancelled")
        return
    
    print("\n🚀 Starting cleanup...")
    
    # Clear databases
    neo4j_success = clear_neo4j()
    qdrant_success = clear_qdrant()
    
    # Summary
    print("\n" + "=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"Neo4j:  {'✅ Cleared' if neo4j_success else '❌ Failed'}")
    print(f"Qdrant: {'✅ Cleared' if qdrant_success else '❌ Failed'}")
    
    if neo4j_success and qdrant_success:
        print("\n✅ All databases cleared successfully!")
        print("   You can now test with fresh data.")
    else:
        print("\n⚠️  Some databases failed to clear. Check errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
