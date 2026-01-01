#!/usr/bin/env python3
"""
Test Agent → HF Model → Arango flow in production container.

Run this in production container to verify end-to-end semantic flow works.

This test combines:
1. HF embedding generation (Test 1.1)
2. Arango storage (Test 1.2)
3. End-to-end flow verification

Usage:
    # Set HF endpoint and API key
    export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"
    export HUGGINGFACE_EMBEDDINGS_API_KEY="hf_xxx"
    
    # Set ArangoDB connection details (or use existing config)
    export ARANGO_URL="http://localhost:8529"
    export ARANGO_DB="symphainy_metadata"
    export ARANGO_USER="root"
    export ARANGO_PASS=""
    
    python3 scripts/test_agent_hf_arango_flow.py
"""

import asyncio
import sys
import os
import httpx
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Add symphainy-platform to path
platform_root = os.path.join(project_root, 'symphainy-platform')
sys.path.insert(0, platform_root)

from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter

async def test_agent_hf_arango_flow():
    """Test Agent → HF → Arango flow."""
    print("🧪 Testing Agent → HF Model → Arango Flow...")
    print("   This tests the complete semantic processing pipeline")
    print("")
    
    # Step 1: Initialize HF endpoint
    hf_endpoint_url = os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
    hf_api_key = os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY")
    
    if not hf_endpoint_url or not hf_api_key:
        print("❌ HF endpoint configuration missing!")
        print("   Set HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
        print("   Set HUGGINGFACE_EMBEDDINGS_API_KEY")
        return False
    
    print(f"   HF Endpoint: {hf_endpoint_url}")
    print(f"   HF API Key: {hf_api_key[:10]}...{hf_api_key[-4:] if len(hf_api_key) > 14 else '***'}")
    
    # Step 2: Initialize ArangoDB adapter
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
        # Step 3: Connect to ArangoDB
        print("Step 1: Connecting to ArangoDB...")
        connected = await adapter.connect(timeout=10.0)
        if not connected:
            print("❌ Failed to connect to ArangoDB")
            return False
        print("✅ Connected to ArangoDB")
        print("")
        
        # Step 4: Generate embedding via HF
        print("Step 2: Generating embedding via HuggingFace endpoint...")
        test_text = "policy_number"
        print(f"   Text: '{test_text}'")
        
        headers = {
            "Authorization": f"Bearer {hf_api_key}",
            "X-Scale-Up-Timeout": "600"  # Wait for cold start if needed
        }
        
        payload = {
            "inputs": test_text
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            print("   Sending request to HF endpoint (may take 30-60 seconds if cold start)...")
            response = await client.post(hf_endpoint_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                embedding = result[0] if isinstance(result[0], list) else result
            elif isinstance(result, dict) and "embedding" in result:
                embedding = result["embedding"]
            else:
                embedding = result
            
            if not isinstance(embedding, list) or len(embedding) == 0:
                print(f"❌ Invalid embedding response: {result}")
                return False
            
            print(f"✅ Generated embedding: {len(embedding)} dimensions")
            print(f"   First 5 values: {embedding[:5]}")
            print("")
        
        # Step 5: Store in Arango
        print("Step 3: Storing embedding in Arango...")
        test_timestamp = datetime.utcnow().timestamp()
        test_embedding_doc = {
            "_key": f"test_flow_{test_timestamp}",
            "file_id": "test_file_flow",
            "column_name": test_text,
            "semantic_id": None,  # Would be set by semantic matching agent
            "metadata_embedding": embedding,
            "meaning_embedding": embedding,  # Same for test (would be different in real flow)
            "samples_embedding": None,  # Would be set if sample values available
            "tenant_id": "test_tenant",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = await adapter.create_document("structured_embeddings", test_embedding_doc)
        if result and result.get("_key"):
            print(f"✅ Stored embedding in Arango: {result.get('_key')}")
        else:
            print(f"❌ Failed to store embedding: {result}")
            return False
        print("")
        
        # Step 6: Retrieve from Arango
        print("Step 4: Retrieving embedding from Arango...")
        retrieved = await adapter.get_document("structured_embeddings", test_embedding_doc["_key"])
        if retrieved:
            print(f"✅ Retrieved embedding from Arango: {retrieved.get('column_name')}")
            print(f"   Embedding dimensions: {len(retrieved.get('metadata_embedding', []))}")
            
            # Verify data integrity
            if retrieved.get("file_id") != "test_file_flow":
                print("❌ Data integrity check failed: file_id mismatch")
                return False
            if len(retrieved.get("metadata_embedding", [])) != len(embedding):
                print("❌ Data integrity check failed: embedding dimension mismatch")
                return False
            
            # Verify embedding values match (first few values)
            stored_embedding = retrieved.get("metadata_embedding", [])
            if stored_embedding[:5] != embedding[:5]:
                print("❌ Data integrity check failed: embedding values don't match")
                return False
            
            print("   ✅ Data integrity verified")
        else:
            print("❌ Failed to retrieve embedding")
            return False
        print("")
        
        # Step 7: Query by file_id (simulate real use case)
        print("Step 5: Querying embeddings by file_id (simulating real use case)...")
        query = """
            FOR doc IN structured_embeddings
            FILTER doc.file_id == @file_id
            RETURN doc
        """
        query_result = await adapter.execute_aql(
            query,
            bind_vars={"file_id": "test_file_flow"}
        )
        if query_result and len(query_result) > 0:
            print(f"✅ Query by file_id returned {len(query_result)} embeddings")
            print(f"   Found column: {query_result[0].get('column_name')}")
        else:
            print("❌ Query by file_id returned no results")
            return False
        print("")
        
        # Step 8: Cleanup
        print("Step 6: Cleaning up test data...")
        deleted = await adapter.delete_document("structured_embeddings", test_embedding_doc["_key"])
        if deleted:
            print("✅ Cleaned up test data")
        else:
            print("⚠️  Failed to cleanup (non-critical)")
        print("")
        
        print("✅ Agent → HF → Arango flow test PASSED!")
        print("")
        print("Summary:")
        print("  ✅ HF embedding generation works")
        print("  ✅ Arango storage works")
        print("  ✅ Arango retrieval works")
        print("  ✅ End-to-end flow works")
        print("  ✅ Data integrity verified")
        return True
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            print("⚠️  503 Service Unavailable - endpoint may be scaling up (cold start)")
            print("   Wait 30-60 seconds and try again")
        elif e.response.status_code == 401:
            print("❌ 401 Unauthorized - check your HF API key")
        else:
            print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
        return False
    
    except httpx.TimeoutException:
        print("❌ Timeout - endpoint may be taking too long to scale up")
        print("   Try again in a minute")
        return False
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent_hf_arango_flow())
    sys.exit(0 if success else 1)






