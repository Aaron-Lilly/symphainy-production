#!/usr/bin/env python3
"""
Test Content Metadata Abstraction integration with semantic data.

Run this in production container to verify integration works.

This test verifies:
1. Can create content metadata
2. Can link semantic embeddings to content_id
3. Can query semantic data by content_id
4. Integration between Content Metadata and semantic data works

Usage:
    # Set ArangoDB connection details (or use existing config)
    export ARANGO_URL="http://localhost:8529"
    export ARANGO_DB="symphainy_metadata"
    export ARANGO_USER="root"
    export ARANGO_PASS=""
    
    python3 scripts/test_content_metadata_semantic_integration.py
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

async def test_content_metadata_semantic_integration():
    """Test Content Metadata Abstraction with semantic data."""
    print("🧪 Testing Content Metadata Abstraction + Semantic Integration...")
    print("   This tests linking semantic data to content metadata")
    print("")
    
    # Initialize ArangoDB adapter
    arango_url = os.getenv("ARANGO_URL", "http://localhost:8529")
    arango_db = os.getenv("ARANGO_DB", "symphainy_metadata")
    arango_user = os.getenv("ARANGO_USER", "root")
    arango_pass = os.getenv("ARANGO_PASS", "")
    
    print(f"   ArangoDB: {arango_url}/{arango_db}")
    print("")
    
    adapter = ArangoDBAdapter(
        hosts=arango_url,
        database=arango_db,
        username=arango_user,
        password=arango_pass
    )
    
    try:
        # Step 1: Connect to ArangoDB
        print("Step 1: Connecting to ArangoDB...")
        connected = await adapter.connect(timeout=10.0)
        if not connected:
            print("❌ Failed to connect to ArangoDB")
            return False
        print("✅ Connected to ArangoDB")
        print("")
        
        # Step 2: Create content metadata
        print("Step 2: Creating content metadata...")
        test_timestamp = datetime.utcnow().timestamp()
        content_id = f"test_content_{test_timestamp}"
        file_uuid = f"test_file_{test_timestamp}"
        
        content_metadata = {
            "_key": content_id,
            "file_uuid": file_uuid,
            "content_type": "structured",
            "semantic_processing_status": "completed",
            "semantic_processing_timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "active",
            "version": 1
        }
        
        result = await adapter.create_document("content_metadata", content_metadata)
        if result and result.get("_key"):
            print(f"✅ Created content metadata: {result.get('_key')}")
            print(f"   File UUID: {file_uuid}")
            print(f"   Content Type: {content_metadata.get('content_type')}")
        else:
            print(f"❌ Failed to create content metadata: {result}")
            return False
        print("")
        
        # Step 3: Store semantic embedding linked to content_id
        print("Step 3: Storing semantic embedding linked to content_id...")
        embedding_doc = {
            "_key": f"test_embedding_{test_timestamp}",
            "content_id": content_id,  # Link to content metadata
            "file_id": file_uuid,  # Also link to file_uuid for backward compatibility
            "column_name": "test_column",
            "semantic_id": "test_semantic_id",
            "metadata_embedding": [0.1] * 768,  # Mock embedding
            "meaning_embedding": [0.2] * 768,
            "samples_embedding": [0.3] * 768,
            "tenant_id": "test_tenant",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = await adapter.create_document("structured_embeddings", embedding_doc)
        if result and result.get("_key"):
            print(f"✅ Stored embedding linked to content_id: {result.get('_key')}")
            print(f"   Content ID: {content_id}")
            print(f"   Column: {embedding_doc.get('column_name')}")
        else:
            print(f"❌ Failed to store embedding: {result}")
            return False
        print("")
        
        # Step 4: Query embeddings by content_id
        print("Step 4: Querying embeddings by content_id...")
        query = """
            FOR doc IN structured_embeddings
            FILTER doc.content_id == @content_id
            RETURN doc
        """
        embeddings = await adapter.execute_aql(
            query,
            bind_vars={"content_id": content_id}
        )
        if embeddings and len(embeddings) > 0:
            print(f"✅ Query embeddings by content_id returned {len(embeddings)} embeddings")
            print(f"   Found column: {embeddings[0].get('column_name')}")
        else:
            print("❌ Query embeddings by content_id returned no results")
            return False
        print("")
        
        # Step 5: Query content metadata and verify link
        print("Step 5: Verifying content metadata and semantic data link...")
        retrieved_metadata = await adapter.get_document("content_metadata", content_id)
        if retrieved_metadata:
            print(f"✅ Retrieved content metadata: {retrieved_metadata.get('file_uuid')}")
            print(f"   Semantic processing status: {retrieved_metadata.get('semantic_processing_status')}")
            
            # Verify we can get semantic data from content metadata
            if retrieved_metadata.get("semantic_processing_status") == "completed":
                print("   ✅ Content metadata indicates semantic processing completed")
        else:
            print("❌ Failed to retrieve content metadata")
            return False
        print("")
        
        # Step 6: Test query pattern (get content metadata + semantic data together)
        print("Step 6: Testing combined query (content metadata + semantic data)...")
        combined_query = """
            LET content = DOCUMENT('content_metadata', @content_id)
            LET embeddings = (
                FOR emb IN structured_embeddings
                FILTER emb.content_id == @content_id
                RETURN emb
            )
            RETURN {
                content: content,
                embeddings: embeddings,
                embedding_count: LENGTH(embeddings)
            }
        """
        combined_result = await adapter.execute_aql(
            combined_query,
            bind_vars={"content_id": content_id}
        )
        if combined_result and len(combined_result) > 0:
            result_data = combined_result[0]
            print(f"✅ Combined query successful")
            print(f"   Content file_uuid: {result_data.get('content', {}).get('file_uuid')}")
            print(f"   Embedding count: {result_data.get('embedding_count', 0)}")
            if result_data.get("embedding_count", 0) > 0:
                print(f"   First embedding column: {result_data.get('embeddings', [{}])[0].get('column_name')}")
        else:
            print("❌ Combined query returned no results")
            return False
        print("")
        
        # Step 7: Cleanup
        print("Step 7: Cleaning up test data...")
        deleted_embedding = await adapter.delete_document("structured_embeddings", embedding_doc["_key"])
        deleted_metadata = await adapter.delete_document("content_metadata", content_id)
        if deleted_embedding and deleted_metadata:
            print("✅ Cleaned up test data")
        else:
            print("⚠️  Failed to cleanup (non-critical)")
        print("")
        
        print("✅ Content Metadata + Semantic integration test PASSED!")
        print("")
        print("Summary:")
        print("  ✅ Can create content metadata")
        print("  ✅ Can link semantic embeddings to content_id")
        print("  ✅ Can query embeddings by content_id")
        print("  ✅ Can query content metadata and semantic data together")
        print("  ✅ Integration between Content Metadata and semantic data works")
        return True
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_content_metadata_semantic_integration())
    sys.exit(0 if success else 1)






