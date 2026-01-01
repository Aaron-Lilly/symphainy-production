#!/usr/bin/env python3
"""
Test Arango storage/retrieval of semantic graph in production container.

Run this in production container to verify Arango semantic graph storage works.

Usage:
    # Set ArangoDB connection details (or use existing config)
    export ARANGO_URL="http://localhost:8529"
    export ARANGO_DB="symphainy_metadata"
    export ARANGO_USER="root"
    export ARANGO_PASS=""
    
    python3 scripts/test_arango_semantic_graph.py
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

async def test_arango_semantic_graph():
    """Test Arango semantic graph storage/retrieval."""
    print("🧪 Testing Arango Semantic Graph Storage/Retrieval...")
    
    # Initialize adapter (use config from development.env or environment variables)
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
            print("   Check your ARANGO_URL, ARANGO_DB, ARANGO_USER, ARANGO_PASS")
            return False
        
        print("✅ Connected to ArangoDB")
        
        # Test node storage
        test_timestamp = datetime.utcnow().timestamp()
        test_node = {
            "_key": f"test_node_{test_timestamp}",
            "file_id": "test_file_456",
            "entity_id": "entity_1",
            "entity_text": "Test Entity",
            "entity_type": "person",
            "semantic_id": "test_semantic_id",
            "embedding": [0.1] * 768,  # Mock embedding (768 dims like mpnet-base-v2)
            "confidence": 0.85,
            "confidence_breakdown": {
                "extraction": 0.9,
                "matching": 0.8,
                "normalization": 0.85
            },
            "explanation": "Test entity extracted from document",
            "tenant_id": "test_tenant",
            "created_at": datetime.utcnow().isoformat()
        }
        
        print(f"   Storing test node: {test_node['_key']}")
        
        result = await adapter.create_document("semantic_graph_nodes", test_node)
        if result and result.get("_key"):
            print(f"✅ Stored node: {result.get('_key')}")
        else:
            print(f"❌ Failed to store node: {result}")
            return False
        
        # Test edge storage
        test_edge = {
            "_key": f"test_edge_{test_timestamp}",
            "file_id": "test_file_456",
            "source_entity_id": "entity_1",
            "target_entity_id": "entity_2",
            "relationship_type": "related_to",
            "confidence": 0.75,
            "explanation": "Test relationship between entities",
            "tenant_id": "test_tenant",
            "created_at": datetime.utcnow().isoformat()
        }
        
        print(f"   Storing test edge: {test_edge['_key']}")
        
        result = await adapter.create_document("semantic_graph_edges", test_edge)
        if result and result.get("_key"):
            print(f"✅ Stored edge: {result.get('_key')}")
        else:
            print(f"❌ Failed to store edge: {result}")
            return False
        
        # Retrieve node
        print(f"   Retrieving node: {test_node['_key']}")
        retrieved_node = await adapter.get_document("semantic_graph_nodes", test_node["_key"])
        if retrieved_node:
            print(f"✅ Retrieved node: {retrieved_node.get('entity_text')}")
            print(f"   Entity type: {retrieved_node.get('entity_type')}")
            print(f"   Confidence: {retrieved_node.get('confidence')}")
            print(f"   Embedding dimensions: {len(retrieved_node.get('embedding', []))}")
            
            # Verify data integrity
            if retrieved_node.get("file_id") != "test_file_456":
                print("❌ Data integrity check failed: file_id mismatch")
                return False
            if len(retrieved_node.get("embedding", [])) != 768:
                print("❌ Data integrity check failed: embedding dimension mismatch")
                return False
        else:
            print("❌ Failed to retrieve node")
            return False
        
        # Retrieve edge
        print(f"   Retrieving edge: {test_edge['_key']}")
        retrieved_edge = await adapter.get_document("semantic_graph_edges", test_edge["_key"])
        if retrieved_edge:
            print(f"✅ Retrieved edge: {retrieved_edge.get('relationship_type')}")
            print(f"   Source: {retrieved_edge.get('source_entity_id')}")
            print(f"   Target: {retrieved_edge.get('target_entity_id')}")
            print(f"   Confidence: {retrieved_edge.get('confidence')}")
        else:
            print("❌ Failed to retrieve edge")
            return False
        
        # Query nodes by file_id using AQL
        print(f"   Querying nodes by file_id: test_file_456")
        nodes_query = """
            FOR doc IN semantic_graph_nodes
            FILTER doc.file_id == @file_id
            RETURN doc
        """
        nodes_result = await adapter.execute_aql(
            nodes_query,
            bind_vars={"file_id": "test_file_456"}
        )
        if nodes_result and len(nodes_result) > 0:
            print(f"✅ Query nodes by file_id returned {len(nodes_result)} nodes")
        else:
            print("❌ Query nodes by file_id returned no results")
            return False
        
        # Query edges by file_id using AQL
        print(f"   Querying edges by file_id: test_file_456")
        edges_query = """
            FOR doc IN semantic_graph_edges
            FILTER doc.file_id == @file_id
            RETURN doc
        """
        edges_result = await adapter.execute_aql(
            edges_query,
            bind_vars={"file_id": "test_file_456"}
        )
        if edges_result and len(edges_result) > 0:
            print(f"✅ Query edges by file_id returned {len(edges_result)} edges")
        else:
            print("❌ Query edges by file_id returned no results")
            return False
        
        # Query edges by source entity (graph traversal)
        print(f"   Querying edges by source entity: entity_1")
        source_query = """
            FOR doc IN semantic_graph_edges
            FILTER doc.source_entity_id == @entity_id
            RETURN doc
        """
        source_result = await adapter.execute_aql(
            source_query,
            bind_vars={"entity_id": "entity_1"}
        )
        if source_result and len(source_result) > 0:
            print(f"✅ Query edges by source entity returned {len(source_result)} edges")
        else:
            print("❌ Query edges by source entity returned no results")
            return False
        
        # Cleanup
        print(f"   Cleaning up test graph data...")
        deleted_node = await adapter.delete_document("semantic_graph_nodes", test_node["_key"])
        deleted_edge = await adapter.delete_document("semantic_graph_edges", test_edge["_key"])
        if deleted_node and deleted_edge:
            print("✅ Cleaned up test graph data")
        else:
            print("⚠️  Failed to cleanup (non-critical)")
        
        print("✅ Arango semantic graph storage/retrieval test PASSED!")
        return True
    
    except Exception as e:
        print(f"❌ Arango semantic graph test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_arango_semantic_graph())
    sys.exit(0 if success else 1)






