#!/usr/bin/env python3
"""
Inline Phase 2 Test - Run inside backend container
Tests semantic processing via direct API calls
"""

import subprocess
import json
import sys

def run_in_container(cmd):
    """Run command inside backend container."""
    full_cmd = f"docker exec symphainy-backend-prod {cmd}"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def test_health():
    """Test 1: Platform health check."""
    print("=" * 70)
    print("Test 1: Platform Health Check")
    print("=" * 70)
    
    stdout, stderr, code = run_in_container("curl -s http://localhost:8000/health")
    if code == 0:
        try:
            health = json.loads(stdout)
            print(f"✅ Platform is healthy")
            print(f"   Status: {health.get('status')}")
            print(f"   Realms: {health.get('total_realms')}")
            return True
        except:
            print(f"⚠️  Health check returned non-JSON: {stdout[:200]}")
            return False
    else:
        print(f"❌ Health check failed: {stderr}")
        return False

def test_list_files():
    """Test 2: List uploaded files."""
    print("\n" + "=" * 70)
    print("Test 2: List Uploaded Files")
    print("=" * 70)
    
    stdout, stderr, code = run_in_container("curl -s http://localhost:8000/api/v1/content-pillar/list-uploaded-files")
    if code == 0:
        try:
            result = json.loads(stdout)
            files = result.get("data", {}).get("files", [])
            if files:
                print(f"✅ Found {len(files)} file(s)")
                for i, file in enumerate(files[:3], 1):
                    print(f"   {i}. {file.get('filename')} (ID: {file.get('file_id')})")
                return files[0].get("file_id")
            else:
                print("⚠️  No files found. Need to upload a file first.")
                return None
        except Exception as e:
            print(f"⚠️  Failed to parse response: {e}")
            print(f"   Response: {stdout[:300]}")
            return None
    else:
        print(f"❌ List files failed: {stderr}")
        return None

def test_parse_with_semantic(file_id, content_type="structured"):
    """Test 3: Parse file with semantic processing."""
    print("\n" + "=" * 70)
    print(f"Test 3: Parse File with Semantic Processing (content_type: {content_type})")
    print("=" * 70)
    
    payload = json.dumps({
        "parse_options": {
            "content_type": content_type
        }
    })
    
    # Escape JSON for shell
    payload_escaped = payload.replace('"', '\\"')
    
    cmd = f'curl -s -X POST http://localhost:8000/api/v1/content-pillar/process-file/{file_id} -H "Content-Type: application/json" -d "{payload_escaped}"'
    
    stdout, stderr, code = run_in_container(cmd)
    
    if code == 0:
        try:
            result = json.loads(stdout)
            print(f"✅ Parse request succeeded (status code: {code})")
            
            # Check response structure
            data = result.get("data", result)
            print(f"\n📊 Response Structure:")
            print(f"   Top-level keys: {list(result.keys())}")
            if "data" in result:
                print(f"   Data keys: {list(data.keys())}")
            
            # Check for semantic_result
            semantic_result = data.get("semantic_result")
            if semantic_result:
                print(f"\n✅ Semantic processing result found!")
                print(f"   Type: {semantic_result.get('type')}")
                print(f"   Success: {semantic_result.get('success')}")
                
                if semantic_result.get("type") == "structured":
                    embeddings = semantic_result.get("embeddings", [])
                    print(f"   Embeddings count: {len(embeddings)}")
                    if embeddings:
                        first_embed = embeddings[0]
                        embed_dims = len(first_embed.get("embedding", []))
                        print(f"   First embedding: {first_embed.get('column_name')} ({embed_dims} dimensions)")
                        print(f"   Model: {first_embed.get('model')}")
                
                elif semantic_result.get("type") == "unstructured":
                    graph = semantic_result.get("semantic_graph", {})
                    nodes = graph.get("nodes", [])
                    edges = graph.get("edges", [])
                    print(f"   Semantic graph: {len(nodes)} nodes, {len(edges)} edges")
                    if nodes:
                        print(f"   First node: {nodes[0].get('entity_name')} ({nodes[0].get('entity_type')})")
                
                elif semantic_result.get("type") == "hybrid":
                    print(f"   Hybrid processing completed")
                    structured = semantic_result.get("structured_semantic", {})
                    unstructured = semantic_result.get("unstructured_semantic", {})
                    print(f"   Structured embeddings: {len(structured.get('embeddings', []))}")
                    graph = unstructured.get("semantic_graph", {})
                    print(f"   Unstructured graph: {len(graph.get('nodes', []))} nodes")
                
                return True
            else:
                print(f"\n⚠️  No semantic_result in response")
                print(f"   Available keys in data: {list(data.keys())}")
                print(f"\n   Full response (first 500 chars):")
                print(f"   {json.dumps(result, indent=2)[:500]}...")
                return False
        except Exception as e:
            print(f"❌ Failed to parse response: {e}")
            print(f"   Raw response: {stdout[:500]}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"❌ Parse request failed (exit code: {code})")
        print(f"   Error: {stderr}")
        print(f"   Output: {stdout[:500]}")
        return False

def main():
    """Run all tests."""
    print("\n🧪 Phase 2 Semantic Processing - Inline Test")
    print("=" * 70)
    
    # Test 1: Health
    if not test_health():
        print("\n❌ Platform health check failed. Cannot proceed.")
        return False
    
    # Test 2: List files
    file_id = test_list_files()
    if not file_id:
        print("\n⚠️  No files available for testing.")
        print("   Please upload a file first, then re-run this test.")
        return False
    
    # Test 3: Parse with semantic processing
    print(f"\n📝 Using file_id: {file_id}")
    
    # Try structured first
    success = test_parse_with_semantic(file_id, "structured")
    
    if success:
        print("\n" + "=" * 70)
        print("✅ Phase 2 Test: PASSED")
        print("   Semantic processing is working!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ Phase 2 Test: FAILED")
        print("   Check the output above for details")
        print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)






