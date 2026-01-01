#!/usr/bin/env python3
"""
Test Arango storage/retrieval of embeddings in production container.

Run this in production container to verify Arango embedding storage works.

Usage:
    # Set ArangoDB connection details (or use existing config)
    export ARANGODB_HOSTS="http://localhost:8529"
    export ARANGODB_DATABASE="symphainy_metadata"
    export ARANGODB_USERNAME="root"
    export ARANGODB_PASSWORD="your_password"
    
    python3 scripts/test_arango_embeddings.py
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Add symphainy-platform to path
platform_root = os.path.join(project_root, 'symphainy-platform')
sys.path.insert(0, platform_root)

from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter

async def test_arango_embeddings():
    """Test Arango embedding storage/retrieval."""
    print("🧪 Testing Arango Embedding Storage/Retrieval...")
    
    # Initialize adapter (use config from development.env or environment variables)
    # Config uses: ARANGO_URL, ARANGO_DB, ARANGO_USER, ARANGO_PASS
    arango_url = os.getenv("ARANGO_URL", "http://localhost:8529")
    arango_db = os.getenv("ARANGO_DB", "symphainy_metadata")
    arango_user = os.getenv("ARANGO_USER", "root")
    arango_pass = os.getenv("ARANGO_PASS", "")  # Default is empty
    
    arango_config = {
        "hosts": arango_url,
        "database": arango_db,
        "username": arango_user,
        "password": arango_pass
    }
    
    print(f"   Connecting to: {arango_config['hosts']}/{arango_config['database']}")
    print(f"   Using config from: ARANGO_URL, ARANGO_DB, ARANGO_USER, ARANGO_PASS")
    print(f"   (These should be in config/development.env)")
    
    adapter = ArangoDBAdapter(
        hosts=arango_config["hosts"],
        database=arango_config["database"],
        username=arango_config["username"],
        password=arango_config["password"]
    )
    
    try:
        # Connect
        print("   Connecting to ArangoDB...")
        connected = await adapter.connect(timeout=10.0)
        if not connected:
            print("❌ Failed to connect to ArangoDB")
            print("   Check your ARANGODB_HOSTS, ARANGODB_DATABASE, ARANGODB_USERNAME, ARANGODB_PASSWORD")
            return False
        
        print("✅ Connected to ArangoDB")
        
        # Test embedding storage
        test_timestamp = datetime.utcnow().timestamp()
        test_embedding = {
            "_key": f"test_embedding_{test_timestamp}",
            "file_id": "test_file_123",
            "column_name": "test_column",
            "semantic_id": "test_semantic_id",
            "metadata_embedding": [0.1] * 768,  # Mock embedding (768 dims like mpnet-base-v2)
            "meaning_embedding": [0.2] * 768,
            "samples_embedding": [0.3] * 768,
            "tenant_id": "test_tenant",
            "created_at": datetime.utcnow().isoformat()
        }
        
        print(f"   Storing test embedding: {test_embedding['_key']}")
        
        # Store
        result = await adapter.create_document("structured_embeddings", test_embedding)
        if result and result.get("_key"):
            print(f"✅ Stored embedding: {result.get('_key')}")
        else:
            print(f"❌ Failed to store embedding: {result}")
            return False
        
        # Retrieve
        print(f"   Retrieving embedding: {test_embedding['_key']}")
        retrieved = await adapter.get_document("structured_embeddings", test_embedding["_key"])
        if retrieved:
            print(f"✅ Retrieved embedding: {retrieved.get('column_name')}")
            print(f"   Metadata embedding dimensions: {len(retrieved.get('metadata_embedding', []))}")
            print(f"   Meaning embedding dimensions: {len(retrieved.get('meaning_embedding', []))}")
            
            # Verify data integrity
            if retrieved.get("file_id") != "test_file_123":
                print("❌ Data integrity check failed: file_id mismatch")
                return False
            if len(retrieved.get("metadata_embedding", [])) != 768:
                print("❌ Data integrity check failed: embedding dimension mismatch")
                return False
        else:
            print("❌ Failed to retrieve embedding")
            return False
        
        # Query by file_id using AQL (more reliable than find with offset)
        print(f"   Querying embeddings by file_id: test_file_123")
        aql_query = """
            FOR doc IN structured_embeddings
            FILTER doc.file_id == @file_id
            RETURN doc
        """
        query_result = await adapter.execute_aql(
            aql_query,
            bind_vars={"file_id": "test_file_123"}
        )
        if query_result and len(query_result) > 0:
            print(f"✅ Query by file_id returned {len(query_result)} embeddings")
        else:
            print("❌ Query by file_id returned no results")
            return False
        
        # Cleanup
        print(f"   Cleaning up test embedding: {test_embedding['_key']}")
        deleted = await adapter.delete_document("structured_embeddings", test_embedding["_key"])
        if deleted:
            print("✅ Cleaned up test embedding")
        else:
            print("⚠️  Failed to cleanup (non-critical)")
        
        print("✅ Arango embedding storage/retrieval test PASSED!")
        return True
    
    except Exception as e:
        print(f"❌ Arango embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_arango_embeddings())
    sys.exit(0 if success else 1)

