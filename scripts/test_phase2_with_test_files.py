#!/usr/bin/env python3
"""
Phase 2 E2E Test with Test Files
Tests semantic processing using actual test files from the test environment
"""

import asyncio
import httpx
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Try to use ProductionTestClient for auth, fallback to direct client
try:
    sys.path.insert(0, '/app/tests')
    from tests.e2e.production.test_production_client import ProductionTestClient
    USE_AUTH_CLIENT = True
except:
    USE_AUTH_CLIENT = False

BASE_URL = "http://symphainy-backend-prod:8000"  # Container network
TIMEOUT = 120.0  # Longer timeout for semantic processing

def create_test_csv_file() -> Path:
    """Create a structured CSV file for testing."""
    test_file = Path("/tmp/test_structured.csv")
    csv_content = """policy_number,policyholder_name,policy_type,premium,coverage_amount,start_date
POL-001,John Doe,Home Insurance,1200.00,500000,2020-01-15
POL-002,Jane Smith,Auto Insurance,800.50,100000,2019-06-20
POL-003,Bob Johnson,Life Insurance,2500.00,1000000,2021-03-10
POL-004,Alice Williams,Home Insurance,1350.75,750000,2020-11-05
POL-005,Charlie Brown,Auto Insurance,950.25,150000,2021-08-12"""
    test_file.write_text(csv_content)
    return test_file

def create_test_txt_file() -> Path:
    """Create an unstructured text file for testing."""
    test_file = Path("/tmp/test_unstructured.txt")
    test_file.write_text("""
Insurance Policy Document

This document outlines the terms and conditions for policy number POL-12345.

Policyholder Information:
- Name: John Doe
- Policy Number: POL-12345
- Effective Date: January 15, 2020
- Premium: $1,200.00 annually

Coverage Details:
The policy provides comprehensive home insurance coverage including:
- Dwelling coverage up to $500,000
- Personal property protection
- Liability coverage
- Additional living expenses

Claims History:
The policyholder has filed 3 claims since policy inception:
1. Water damage claim in March 2021 - $5,000
2. Theft claim in August 2022 - $2,500
3. Storm damage claim in November 2023 - $8,000

Contact Information:
- Email: john.doe@example.com
- Phone: 555-1234
- Address: 123 Main Street, Anytown, USA 12345

This policy is subject to the terms and conditions outlined in the master policy document.
    """.strip())
    return test_file

async def get_auth_token() -> Optional[str]:
    """Get authentication token."""
    import httpx
    test_email = os.getenv("TEST_USER_EMAIL") or os.getenv("TEST_SUPABASE_EMAIL") or "test@symphainy.com"
    test_password = os.getenv("TEST_USER_PASSWORD") or os.getenv("TEST_SUPABASE_PASSWORD") or "test_password_123"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": test_password}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("token") or data.get("access_token")
    except:
        pass
    return None

async def upload_file(client: httpx.AsyncClient, file_path: Path, token: Optional[str] = None) -> Optional[str]:
    """Upload a file and return file_id."""
    print(f"📤 Uploading file: {file_path.name}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f.read(), "application/octet-stream")}
            response = await client.post(
                f"{BASE_URL}/api/v1/content-pillar/upload-file",
                files=files,
                headers=headers,
                timeout=TIMEOUT
            )
        
        if response.status_code in [200, 201]:
            data = response.json()
            file_id = data.get("file_id") or data.get("uuid") or data.get("id")
            if file_id:
                print(f"   ✅ Uploaded: file_id={file_id}")
                return file_id
            else:
                print(f"   ❌ Upload response missing file_id: {data}")
                return None
        else:
            print(f"   ❌ Upload failed: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return None

async def test_parse_with_semantic(
    client: httpx.AsyncClient,
    file_id: str,
    content_type: str,
    test_name: str,
    token: Optional[str] = None
) -> bool:
    """Test parse_file with semantic processing."""
    print(f"\n{'='*70}")
    print(f"Test: {test_name} (content_type: {content_type})")
    print(f"{'='*70}")
    
    # Gateway expects "options" not "parse_options"
    payload = {
        "options": {
            "content_type": content_type,
            "parse_options": {
                "content_type": content_type
            }
        }
    }
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"📝 Calling parse_file with content_type: {content_type}")
    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/content-pillar/process-file/{file_id}",
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201, 202]:
            print(f"❌ Parse request failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
        
        result = response.json()
        
        print(f"✅ Parse request succeeded")
        print(f"\n📊 Response Structure:")
        print(f"   Top-level keys: {list(result.keys())}")
        
        # Navigate to the nested data structure
        # Response structure: parse_result -> data -> {parse_result, semantic_result}
        parse_result_wrapper = result.get("parse_result", {})
        data = parse_result_wrapper.get("data", {})
        
        if data:
            print(f"   Data keys: {list(data.keys())}")
        
        # Check for semantic_result in the nested data structure
        semantic_result = data.get("semantic_result")
        data_type = data.get("data_type")  # Also check top-level data_type
        semantic_processing_enabled = data.get("semantic_processing_enabled", False)
        
        if semantic_result:
            print(f"\n✅ Semantic processing result found!")
            print(f"   Semantic processing enabled: {semantic_processing_enabled}")
            print(f"   Data type (top-level): {data_type}")
            print(f"   Semantic result keys: {list(semantic_result.keys())}")
            print(f"   Type (from semantic_result): {semantic_result.get('type')}")
            print(f"   Success: {semantic_result.get('success')}")
            
            # Use data_type from top-level if available, otherwise from semantic_result
            actual_type = data_type or semantic_result.get('type')
            
            if actual_type == "structured":
                embeddings = semantic_result.get("embeddings", [])
                print(f"   Embeddings count: {len(embeddings)}")
                if embeddings:
                    first_embed = embeddings[0]
                    embed_dims = len(first_embed.get("embedding", []))
                    print(f"   First embedding: {first_embed.get('column_name')} ({embed_dims} dimensions)")
                    print(f"   Model: {first_embed.get('model')}")
                    return True
                else:
                    print(f"   ⚠️  No embeddings in result")
                    return False
            
            elif actual_type == "unstructured":
                graph = semantic_result.get("semantic_graph", {})
                nodes = graph.get("nodes", [])
                edges = graph.get("edges", [])
                print(f"   Semantic graph: {len(nodes)} nodes, {len(edges)} edges")
                if nodes:
                    print(f"   First node: {nodes[0].get('entity_name')} ({nodes[0].get('entity_type')})")
                    return True
                else:
                    print(f"   ⚠️  No nodes in semantic graph")
                    return False
            
            elif actual_type == "hybrid":
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
            print(f"\n   Full response (first 1000 chars):")
            print(f"   {json.dumps(result, indent=2)[:1000]}...")
            return False
            
    except Exception as e:
        print(f"❌ Parse test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("\n🧪 Phase 2 Semantic Processing - E2E Test with Test Files")
    print("=" * 70)
    print()
    
    # Create test files
    print("📝 Creating test files...")
    csv_file = create_test_csv_file()
    txt_file = create_test_txt_file()
    print(f"✅ Created structured CSV: {csv_file}")
    print(f"✅ Created unstructured TXT: {txt_file}")
    
    # Get authentication token
    print("🔐 Getting authentication token...")
    token = await get_auth_token()
    if token:
        print(f"✅ Authentication successful")
    else:
        print(f"⚠️  Could not get auth token, requests may fail")
    
    # Create HTTP client
    client = httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT)
    
    try:
        # Test 1: Structured data (CSV)
        print(f"\n{'='*70}")
        print("Test 1: Structured Data (CSV)")
        print(f"{'='*70}")
        
        file_id = await upload_file(client, csv_file, token)
        if not file_id:
            print("❌ Failed to upload CSV file")
            return False
        
        success1 = await test_parse_with_semantic(
            client, file_id, "structured", "Structured CSV Semantic Processing", token
        )
        
        # Test 2: Unstructured data (TXT)
        print(f"\n{'='*70}")
        print("Test 2: Unstructured Data (TXT)")
        print(f"{'='*70}")
        
        file_id2 = await upload_file(client, txt_file, token)
        if not file_id2:
            print("❌ Failed to upload TXT file")
            return False
        
        success2 = await test_parse_with_semantic(
            client, file_id2, "unstructured", "Unstructured TXT Semantic Processing", token
        )
        
        # Summary
        print(f"\n{'='*70}")
        print("Test Summary")
        print(f"{'='*70}")
        print(f"✅ Structured (CSV): {'PASSED' if success1 else 'FAILED'}")
        print(f"✅ Unstructured (TXT): {'PASSED' if success2 else 'FAILED'}")
        
        if success1 and success2:
            print(f"\n🎉 All tests PASSED!")
            return True
        else:
            print(f"\n⚠️  Some tests failed - check output above")
            return False
    finally:
        await client.aclose()

if __name__ == "__main__":
    # Run inside container
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

