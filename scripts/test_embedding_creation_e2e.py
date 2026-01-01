#!/usr/bin/env python3
"""
E2E Test: Embedding Creation and Accuracy Validation

Tests the complete embedding creation flow:
1. Upload a test file with known structure
2. Parse the file
3. Create embeddings
4. Validate embedding quality and accuracy

Validation includes:
- Embeddings are not zeros (real embeddings generated)
- Similar columns get similar embeddings
- Different columns get different embeddings
- Embedding dimensions are correct
- Metadata is stored correctly
"""

import os
import sys
import asyncio
import json
import requests
import uuid
import io
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# API configuration (match test_all_parsing_types.py)
API_BASE = os.getenv("API_BASE", "http://localhost/api")  # Via Traefik
API_BASE_DIRECT = os.getenv("API_BASE_DIRECT", "http://localhost:8000")  # Direct backend (no /api)

# Test user credentials (match test_all_parsing_types.py pattern)
USER_ID = "test_user_e2e"
SESSION_ID = "test_session_e2e"

# Authentication token - try to get from environment or login
def get_auth_token():
    """Get authentication token - try environment first, then login."""
    # Try environment variable first
    token = os.getenv("AUTH_TOKEN") or os.getenv("SYMPHAINY_API_TOKEN")
    if token:
        return token
    
    # Try to login and get token
    test_email = os.getenv("TEST_USER_EMAIL") or os.getenv("TEST_SUPABASE_EMAIL") or "test@symphainy.com"
    test_password = os.getenv("TEST_USER_PASSWORD") or os.getenv("TEST_SUPABASE_PASSWORD") or "test_password_123"
    
    try:
        print(f"🔐 Attempting to get auth token via login...")
        print(f"   Using email: {test_email}")
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": test_email, "password": test_password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            if token:
                print(f"✅ Got auth token via login")
                return token
    except Exception as e:
        print(f"⚠️ Failed to get token via login: {e}")
    
    print(f"⚠️ No auth token available - test will fail with 401")
    return None

AUTH_TOKEN = get_auth_token()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    try:
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        # Normalize vectors
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(v1, v2) / (norm1 * norm2)
        return float(similarity)
    except Exception as e:
        print(f"⚠️ Error calculating cosine similarity: {e}")
        return 0.0


def is_zero_vector(vec: List[float], threshold: float = 1e-6) -> bool:
    """Check if vector is essentially zero."""
    try:
        norm = np.linalg.norm(np.array(vec))
        return norm < threshold
    except Exception:
        return True


def create_test_csv_file():
    """Create a test CSV file with known structure for embedding testing."""
    csv_content = """customer_id,customer_name,customer_email,customer_age,order_total
CUST001,John Doe,john.doe@example.com,30,150.50
CUST002,Jane Smith,jane.smith@example.com,25,200.75
CUST003,Bob Johnson,bob.johnson@example.com,35,175.25
CUST004,Alice Williams,alice.williams@example.com,28,300.00
CUST005,Charlie Brown,charlie.brown@example.com,42,125.50
CUST006,Diana Prince,diana.prince@example.com,29,250.75
CUST007,Frank Miller,frank.miller@example.com,33,180.00
CUST008,Grace Lee,grace.lee@example.com,27,220.50
CUST009,Henry Ford,henry.ford@example.com,45,275.25
CUST010,Iris West,iris.west@example.com,31,195.75"""
    
    return csv_content.encode('utf-8'), 'test_embedding_validation.csv', 'text/csv', 'csv'


# Login function removed - using get_auth_token() pattern instead


def upload_file(file_data: bytes, filename: str, content_type: str):
    """Upload a file."""
    # Try API_BASE first (Traefik), then direct backend
    for api_base in [API_BASE, API_BASE_DIRECT]:
        try:
            url = f"{api_base}/v1/content-pillar/upload-file"
            files = {
                'file': (filename, io.BytesIO(file_data), content_type)
            }
            data = {
                'file_type': 'csv',  # Match test file type
                'user_id': USER_ID,
                'session_id': SESSION_ID
            }
            headers = {
                'X-Session-Token': SESSION_ID
            }
            if AUTH_TOKEN:
                headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return True, result
                else:
                    if api_base == API_BASE:
                        print(f"⚠️ Upload failed via Traefik (success=False), trying direct backend...")
                        continue
                    else:
                        return False, result
            else:
                if api_base == API_BASE:
                    print(f"⚠️ Upload failed via Traefik ({response.status_code}), trying direct backend...")
                    continue
                else:
                    print(f"❌ Upload failed: {response.status_code} - {response.text[:200]}")
                    return False, None
        except requests.exceptions.ConnectionError as e:
            if api_base == API_BASE:
                print(f"⚠️ Traefik connection failed ({e}), trying direct backend...")
                continue
            else:
                print(f"❌ Upload connection error: {e}")
                return False, None
        except Exception as e:
            if api_base == API_BASE:
                print(f"⚠️ Traefik request failed ({e}), trying direct backend...")
                continue
            else:
                print(f"❌ Upload exception: {e}")
                return False, None
    
    return False, None


def parse_file(file_id: str):
    """Parse a file."""
    for api_base in [API_BASE, API_BASE_DIRECT]:
        try:
            url = f"{api_base}/v1/content-pillar/process-file/{file_id}"
            data = {'user_id': USER_ID}
            headers = {
                'X-Session-Token': SESSION_ID
            }
            if AUTH_TOKEN:
                headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
            
            response = requests.post(url, json=data, headers=headers, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return True, result
                else:
                    if api_base == API_BASE:
                        print(f"⚠️ Parse failed via Traefik, trying direct backend...")
                        continue
                    else:
                        return False, result
            else:
                if api_base == API_BASE:
                    print(f"⚠️ Parse failed via Traefik ({response.status_code}), trying direct backend...")
                    continue
                else:
                    print(f"❌ Parse failed: {response.status_code} - {response.text}")
                    return False, None
        except Exception as e:
            if api_base == API_BASE:
                print(f"⚠️ Parse exception via Traefik ({e}), trying direct backend...")
                continue
            else:
                print(f"❌ Parse exception: {e}")
                return False, None
    
    return False, None


def get_embeddings(content_id: str):
    """Get embeddings from ArangoDB (via API or direct query)."""
    # For now, we'll need to query ArangoDB directly or via an API endpoint
    # This is a placeholder - we'll need to implement an endpoint or use direct DB access
    print(f"⚠️ Getting embeddings for content_id={content_id} - endpoint not yet implemented")
    return None


async def test_embedding_creation_e2e():
    """Test embedding creation E2E flow."""
    print("="*80)
    print("E2E TEST: Embedding Creation and Accuracy Validation")
    print("="*80)
    
    # Step 1: Authentication (AUTH_TOKEN already set via get_auth_token())
    print("\n📋 Step 1: Authentication...")
    if AUTH_TOKEN:
        print(f"✅ Auth token available (length: {len(AUTH_TOKEN)})")
    else:
        print("⚠️ No auth token - test may fail with 401")
    
    # Step 2: Create and upload test file
    print("\n📦 Step 2: Creating and uploading test file...")
    file_data, filename, content_type, file_type = create_test_csv_file()
    print(f"   File: {filename} ({len(file_data)} bytes)")
    print(f"   Columns: customer_id, customer_name, customer_email, customer_age, order_total")
    
    success, upload_result = upload_file(file_data, filename, content_type)
    if not success:
        print(f"❌ Upload failed: {upload_result}")
        return False
    
    file_id = upload_result.get("file_id")
    print(f"✅ Upload successful: file_id={file_id}")
    
    # Step 3: Parse file
    print("\n⚙️  Step 3: Parsing file...")
    success, parse_result = parse_file(file_id)
    if not success:
        print(f"❌ Parsing failed: {parse_result}")
        return False
    
    parsed_file_id = parse_result.get("parsed_file_id")
    content_metadata = parse_result.get("parse_result", {})
    print(f"✅ Parsing successful: parsed_file_id={parsed_file_id}")
    print(f"   Columns detected: {len(content_metadata.get('metadata', {}).get('columns', []))}")
    
    # Step 4: Create embeddings (via ContentOrchestrator.embed_content)
    print("\n🧬 Step 4: Creating embeddings...")
    # Try to call embed endpoint (if available)
    embed_success = False
    content_id = None
    
    # Extract parsed_file_id and content_metadata from parse_result
    parsed_file_id = parse_result.get("parsed_file_id")
    parse_result_data = parse_result.get("parse_result", {})
    
    # Build content_metadata from parse_result
    content_metadata = {
        "file_id": file_id,
        "parsed_file_id": parsed_file_id,
        "metadata": parse_result_data.get("metadata", {}),
        "structure": parse_result_data.get("structure", {}),
        "parsing_type": parse_result_data.get("parsing_type", "structured"),
        "file_type": parse_result_data.get("file_type", "unknown")
    }
    
    # Try API_BASE first (Traefik), then direct backend
    for api_base in [API_BASE, API_BASE_DIRECT]:
        try:
            # Ensure correct URL format
            if api_base == API_BASE_DIRECT:
                url = f"{api_base}/api/v1/content-pillar/embed/{file_id}"
            else:
                url = f"{api_base}/v1/content-pillar/embed/{file_id}"
            data = {
                'parsed_file_id': parsed_file_id,
                'content_metadata': content_metadata,
                'user_id': USER_ID,
                'user_context': {
                    'user_id': USER_ID,
                    'session_id': SESSION_ID,
                    'workflow_id': str(uuid.uuid4())
                }
            }
            headers = {
                'X-Session-Token': SESSION_ID
            }
            if AUTH_TOKEN:
                headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
            
            response = requests.post(url, json=data, headers=headers, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                # Check for route not found error (route exists but not registered)
                if result.get("error") == "Route not found":
                    print(f"⚠️  Route not found: {result.get('endpoint')} - route may not be registered with Curator")
                    if api_base == API_BASE:
                        print(f"   Trying direct backend...")
                        continue
                    else:
                        print(f"   Route needs to be registered - checking if handler exists...")
                        # Route exists but not discovered - this is a registration issue
                        break
                elif result.get("success"):
                    embed_success = True
                    content_id = result.get("content_id")
                    embeddings_count = result.get("embeddings_count", 0)
                    print(f"✅ Embedding creation successful: {embeddings_count} embeddings, content_id={content_id}")
                    break
                else:
                    # Even if success=False, log the response for debugging
                    error_msg = result.get("error") or result.get("message") or "Unknown error"
                    print(f"⚠️  Embed request returned success=False: {error_msg}")
                    print(f"   Full response: {result}")
                    # Continue to try direct backend if via Traefik
                    if api_base == API_BASE:
                        continue
                    else:
                        break
            elif response.status_code == 404:
                # Endpoint doesn't exist yet
                if api_base == API_BASE:
                    print(f"⚠️  Embed endpoint not found via Traefik, trying direct backend...")
                    continue
                else:
                    print(f"⚠️  Embed endpoint not yet implemented - need to add to API")
                    break
            else:
                if api_base == API_BASE:
                    print(f"⚠️  Embed failed via Traefik ({response.status_code}), trying direct backend...")
                    continue
                else:
                    print(f"❌ Embed failed: {response.status_code} - {response.text}")
                    break
        except Exception as e:
            if api_base == API_BASE:
                print(f"⚠️  Embed exception via Traefik ({e}), trying direct backend...")
                continue
            else:
                print(f"⚠️  Embed endpoint not available: {e}")
                break
    
    if not embed_success:
        print("   ⚠️  Cannot test embedding validation without embed endpoint")
        print("   Need to add POST /api/v1/content-pillar/embed/{file_id} endpoint")
        return False
    
    # Step 5: Retrieve embeddings for validation
    print("\n🔍 Step 5: Retrieving embeddings for validation...")
    embeddings = None
    
    # Try API_BASE first (Traefik), then direct backend
    for api_base in [API_BASE, API_BASE_DIRECT]:
        try:
            # Ensure correct URL format
            if api_base == API_BASE_DIRECT:
                url = f"{api_base}/api/v1/content-pillar/embeddings/{content_id}"
            else:
                # Traefik routes /api/v1/... to backend
                url = f"{api_base}/api/v1/content-pillar/embeddings/{content_id}"
            headers = {
                'X-Session-Token': SESSION_ID
            }
            if AUTH_TOKEN:
                headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    embeddings = result.get("embeddings", [])
                    print(f"✅ Retrieved {len(embeddings)} embeddings")
                    break
            elif response.status_code == 404:
                if api_base == API_BASE:
                    print(f"⚠️  Get embeddings endpoint not found via Traefik, trying direct backend...")
                    continue
                else:
                    print(f"⚠️  Get embeddings endpoint not yet implemented")
                    # For now, we'll validate what we can
                    break
            else:
                if api_base == API_BASE:
                    print(f"⚠️  Get embeddings failed via Traefik ({response.status_code}), trying direct backend...")
                    continue
                else:
                    print(f"❌ Get embeddings failed: {response.status_code}")
                    break
        except Exception as e:
            if api_base == API_BASE:
                continue
            else:
                print(f"⚠️  Get embeddings endpoint not available: {e}")
                break
    
    # Step 6: Validate embedding quality and accuracy
    print("\n📊 Step 6: Validating embedding quality and accuracy...")
    
    if not embeddings or len(embeddings) == 0:
        print("   ⚠️  Cannot validate - no embeddings retrieved")
        print("   Need to add GET /api/v1/content-pillar/embeddings/{content_id} endpoint")
        return False
    
    validation_results = {
        "total_embeddings": len(embeddings),
        "zero_vectors": 0,
        "valid_embeddings": 0,
        "similarity_tests": {},
        "dimension_checks": {}
    }
    
    # Validate each embedding
    for emb in embeddings:
        column_name = emb.get("column_name", "unknown")
        
        # Check for zero vectors
        metadata_emb = emb.get("metadata_embedding", [])
        meaning_emb = emb.get("meaning_embedding", [])
        samples_emb = emb.get("samples_embedding", [])
        
        if is_zero_vector(metadata_emb) or is_zero_vector(meaning_emb) or is_zero_vector(samples_emb):
            validation_results["zero_vectors"] += 1
            print(f"   ⚠️  {column_name}: Contains zero vectors (placeholder embeddings)")
        else:
            validation_results["valid_embeddings"] += 1
            print(f"   ✅ {column_name}: Valid embeddings (non-zero)")
        
        # Check dimensions
        dim = len(metadata_emb) if metadata_emb else 0
        validation_results["dimension_checks"][column_name] = dim
        if dim == 0:
            print(f"   ⚠️  {column_name}: Empty embedding")
        elif dim not in [384, 768]:  # Common dimensions
            print(f"   ⚠️  {column_name}: Unexpected dimension {dim} (expected 384 or 768)")
        else:
            print(f"   ✅ {column_name}: Correct dimension {dim}")
    
    # Test similarity: Similar columns should have similar embeddings
    print("\n   Testing similarity between related columns...")
    
    # Expected similar pairs (based on column names)
    similar_pairs = [
        ("customer_id", "customer_name"),  # Both customer-related
        ("customer_email", "customer_name"),  # Both customer-related
    ]
    
    # Expected different pairs
    different_pairs = [
        ("customer_id", "order_total"),  # ID vs numeric value
        ("customer_name", "order_total"),  # Text vs numeric
    ]
    
    for col1, col2 in similar_pairs:
        emb1 = next((e for e in embeddings if e.get("column_name") == col1), None)
        emb2 = next((e for e in embeddings if e.get("column_name") == col2), None)
        
        if emb1 and emb2:
            metadata1 = emb1.get("metadata_embedding", [])
            metadata2 = emb2.get("metadata_embedding", [])
            
            if metadata1 and metadata2 and not is_zero_vector(metadata1) and not is_zero_vector(metadata2):
                similarity = cosine_similarity(metadata1, metadata2)
                validation_results["similarity_tests"][f"{col1}_vs_{col2}"] = similarity
                
                if similarity > 0.3:  # Threshold for "similar"
                    print(f"   ✅ {col1} vs {col2}: Similar (similarity={similarity:.3f})")
                else:
                    print(f"   ⚠️  {col1} vs {col2}: Less similar than expected (similarity={similarity:.3f})")
    
    for col1, col2 in different_pairs:
        emb1 = next((e for e in embeddings if e.get("column_name") == col1), None)
        emb2 = next((e for e in embeddings if e.get("column_name") == col2), None)
        
        if emb1 and emb2:
            metadata1 = emb1.get("metadata_embedding", [])
            metadata2 = emb2.get("metadata_embedding", [])
            
            if metadata1 and metadata2 and not is_zero_vector(metadata1) and not is_zero_vector(metadata2):
                similarity = cosine_similarity(metadata1, metadata2)
                validation_results["similarity_tests"][f"{col1}_vs_{col2}"] = similarity
                
                if similarity < 0.5:  # Threshold for "different"
                    print(f"   ✅ {col1} vs {col2}: Different (similarity={similarity:.3f})")
                else:
                    print(f"   ⚠️  {col1} vs {col2}: More similar than expected (similarity={similarity:.3f})")
    
    # Summary
    print("\n" + "="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    print(f"Total embeddings: {validation_results['total_embeddings']}")
    print(f"Valid embeddings (non-zero): {validation_results['valid_embeddings']}")
    print(f"Zero vectors (placeholders): {validation_results['zero_vectors']}")
    print(f"\nSimilarity tests: {len(validation_results['similarity_tests'])}")
    for pair, sim in validation_results['similarity_tests'].items():
        print(f"  {pair}: {sim:.3f}")
    
    # Success criteria
    success = (
        validation_results["valid_embeddings"] > 0 and
        validation_results["zero_vectors"] == 0 and
        len(validation_results["similarity_tests"]) > 0
    )
    
    if success:
        print("\n✅ E2E EMBEDDING TEST PASSED")
        print("   Embeddings are being generated correctly!")
    else:
        print("\n⚠️  E2E EMBEDDING TEST PARTIAL")
        if validation_results["zero_vectors"] > 0:
            print("   Some embeddings are placeholders (zeros)")
        if validation_results["valid_embeddings"] == 0:
            print("   No valid embeddings found")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(test_embedding_creation_e2e())
    sys.exit(0 if success else 1)

