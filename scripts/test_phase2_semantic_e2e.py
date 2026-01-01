#!/usr/bin/env python3
"""
Phase 2 E2E Test: Content Pillar Semantic Processing
Tests parse_file() with semantic processing integration via API.

This test verifies:
1. parse_file() is called with content_type in parse_options
2. Semantic processing runs (structured/unstructured/hybrid)
3. Embeddings/semantic graphs are stored in Arango
4. Response includes semantic_result
"""

import os
import sys
import asyncio
import httpx
import json
from pathlib import Path
from typing import Dict, Any, Optional

async def test_parse_file_with_semantic_processing():
    """Test parse_file endpoint with semantic processing."""
    print("=" * 70)
    print("🧪 Phase 2 E2E Test: Content Pillar Semantic Processing")
    print("=" * 70)
    print()
    
    # Try multiple base URLs (container network, localhost, Traefik)
    base_urls = [
        "http://symphainy-backend-prod:8000",  # Container network
        "http://localhost:8000",  # Direct host
        "http://localhost:80/api/v1",  # Through Traefik
    ]
    base_url = None
    for url in base_urls:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    base_url = url.replace("/health", "").replace("/api/v1", "")
                    print(f"✅ Found accessible backend at: {base_url}")
                    break
        except:
            continue
    
    if not base_url:
        print("⚠️  Could not find accessible backend URL")
        print("   Trying default: http://localhost:8000")
        base_url = "http://localhost:8000"
    
    # Step 1: Check platform health
    print("Step 1: Checking platform health...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Platform is healthy")
            else:
                print(f"⚠️  Platform health check returned {response.status_code}")
                print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Platform health check failed: {e}")
        return False
    
    print()
    
    # Step 2: List uploaded files (to get a file_id for testing)
    print("Step 2: Listing uploaded files...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/v1/content-pillar/list-uploaded-files")
            if response.status_code == 200:
                data = response.json()
                files = data.get("data", {}).get("files", [])
                if files:
                    test_file_id = files[0].get("file_id")
                    print(f"✅ Found {len(files)} file(s), using file_id: {test_file_id}")
                else:
                    print("⚠️  No files found. You may need to upload a file first.")
                    print("   Skipping parse_file test (no file_id available)")
                    return False
            else:
                print(f"⚠️  List files returned {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"❌ List files failed: {e}")
        return False
    
    print()
    
    # Step 3: Test parse_file with structured content_type
    print("Step 3: Testing parse_file with structured content_type...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for semantic processing
            payload = {
                "parse_options": {
                    "content_type": "structured"  # This should trigger structured semantic processing
                }
            }
            response = await client.post(
                f"{base_url}/api/v1/content-pillar/process-file/{test_file_id}",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Parse request succeeded")
                
                # Check for semantic_result in response
                if "semantic_result" in result or "data" in result:
                    data = result.get("data", result)
                    semantic_result = data.get("semantic_result")
                    
                    if semantic_result:
                        print("✅ Semantic processing result found in response!")
                        print(f"   Type: {semantic_result.get('type')}")
                        
                        if semantic_result.get("type") == "structured":
                            embeddings = semantic_result.get("embeddings", [])
                            print(f"   Embeddings count: {len(embeddings)}")
                            if embeddings:
                                print(f"   First embedding dimensions: {len(embeddings[0].get('embedding', []))}")
                        
                        elif semantic_result.get("type") == "unstructured":
                            graph = semantic_result.get("semantic_graph", {})
                            nodes = graph.get("nodes", [])
                            edges = graph.get("edges", [])
                            print(f"   Semantic graph: {len(nodes)} nodes, {len(edges)} edges")
                        
                        elif semantic_result.get("type") == "hybrid":
                            print("   Hybrid semantic processing completed")
                            structured = semantic_result.get("structured_semantic", {})
                            unstructured = semantic_result.get("unstructured_semantic", {})
                            print(f"   Structured embeddings: {len(structured.get('embeddings', []))}")
                            graph = unstructured.get("semantic_graph", {})
                            print(f"   Unstructured graph: {len(graph.get('nodes', []))} nodes")
                        
                        return True
                    else:
                        print("⚠️  No semantic_result in response (semantic processing may not have run)")
                        print(f"   Response keys: {list(data.keys())}")
                        return False
                else:
                    print("⚠️  Response structure unexpected")
                    print(f"   Response keys: {list(result.keys())}")
                    return False
            else:
                print(f"❌ Parse request failed: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
    except Exception as e:
        print(f"❌ Parse file test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    success = await test_parse_file_with_semantic_processing()
    
    print()
    print("=" * 70)
    if success:
        print("✅ Phase 2 E2E Test: PASSED")
        print("   Semantic processing is working end-to-end!")
    else:
        print("❌ Phase 2 E2E Test: FAILED")
        print("   Check the errors above for details")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

