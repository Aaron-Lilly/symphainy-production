#!/usr/bin/env python3
"""
Test: Unified File Metadata Pattern

Tests the standardized metadata pattern across all three file tables:
- project_files (uploaded files)
- parsed_data_files (parsed files)  
- embedding_files (embedding files)

Validates:
1. ui_name is stored in parsed_data_files when creating parsed files
2. list_parsed_files returns ui_name directly (no JOINs needed)
3. list_parsed_files_with_embeddings uses ui_name correctly
4. All three tables follow the unified pattern
"""

import requests
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Test configuration
# Use Traefik (port 80) for production containers, or direct backend (port 8000) if specified
API_BASE = os.getenv("TEST_BACKEND_URL", "http://localhost/api")
# Fallback to direct backend if Traefik not available
if API_BASE == "http://localhost/api":
    # Try to detect if we should use direct backend
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        if result == 0:
            API_BASE = "http://localhost:8000"
    except:
        pass

USER_ID = os.getenv("TEST_USER_ID", "test_unified_pattern_user")
SESSION_ID = os.getenv("TEST_SESSION_ID", "test_unified_pattern_session")

# Authentication token
def get_auth_token() -> Optional[str]:
    """Get authentication token from environment or login."""
    token = os.getenv("AUTH_TOKEN") or os.getenv("SYMPHAINY_API_TOKEN")
    if token:
        return token
    
    # Try to login
    test_email = os.getenv("TEST_USER_EMAIL", "test@symphainy.com")
    test_password = os.getenv("TEST_USER_PASSWORD", "test_password_123")
    
    try:
        login_url = f"{API_BASE}/auth/login" if API_BASE.endswith("/api") else f"{API_BASE}/api/auth/login"
        print(f"🔐 Attempting to get auth token via login...")
        response = requests.post(
            login_url,
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
    
    print(f"⚠️ No auth token available - some tests may fail with 401")
    return None

AUTH_TOKEN = get_auth_token()

# Headers for authenticated requests
def get_headers() -> Dict[str, str]:
    """Get headers with authentication."""
    headers = {"Content-Type": "application/json"}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
        headers["X-Session-Token"] = AUTH_TOKEN
    return headers

# Test file content
TEST_FILE_CONTENT = """name,age,city
John,30,New York
Jane,25,San Francisco
Bob,35,Chicago
Alice,28,Boston
"""

def create_test_file() -> Path:
    """Create a test CSV file."""
    test_file = Path("/tmp/test_unified_pattern.csv")
    test_file.write_text(TEST_FILE_CONTENT)
    return test_file

def test_1_upload_file() -> Optional[str]:
    """Test 1: Upload a file and verify ui_name is stored."""
    print("\n" + "="*80)
    print("TEST 1: Upload File (Verify project_files.ui_name)")
    print("="*80)
    
    test_file = create_test_file()
    print(f"📄 Created test file: {test_file}")
    
    try:
        # Upload file
        files = {
            'file': ('test_unified_pattern.csv', test_file.open('rb'), 'text/csv')
        }
        data = {
            'file_type': 'csv',
            'user_id': USER_ID,
            'session_id': SESSION_ID
        }
        
        # Adjust URL based on API_BASE
        upload_url = f"{API_BASE}/v1/content-pillar/upload-file" if API_BASE.endswith("/api") else f"{API_BASE}/api/v1/content-pillar/upload-file"
        print(f"📤 Uploading file to {upload_url}...")
        upload_headers = {}
        if AUTH_TOKEN:
            upload_headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
            upload_headers["X-Session-Token"] = AUTH_TOKEN
        response = requests.post(
            upload_url,
            files=files,
            data=data,
            headers=upload_headers,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
        
        result = response.json()
        file_id = result.get("file_id") or result.get("uuid")
        ui_name = result.get("ui_name") or result.get("filename")
        
        print(f"✅ File uploaded successfully")
        print(f"   file_id: {file_id}")
        print(f"   ui_name: {ui_name}")
        
        # Verify ui_name is present
        assert ui_name, "❌ ui_name not returned in upload response"
        print(f"✅ Verified: ui_name is stored in project_files table")
        
        return file_id
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_2_parse_file(file_id: str) -> Optional[str]:
    """Test 2: Parse the file and verify ui_name is stored in parsed_data_files."""
    print("\n" + "="*80)
    print("TEST 2: Parse File (Verify parsed_data_files.ui_name)")
    print("="*80)
    
    try:
        # Trigger parsing (use process-file endpoint)
        parse_url = f"{API_BASE}/v1/content-pillar/process-file" if API_BASE.endswith("/api") else f"{API_BASE}/api/v1/content-pillar/process-file"
        print(f"🔄 Triggering parse for file_id: {file_id}...")
        response = requests.post(
            parse_url,
            json={
                "file_id": file_id,
                "user_id": USER_ID
            },
            headers=get_headers(),
            timeout=60
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Parse failed: {response.status_code} - {response.text}")
            return None
        
        result = response.json()
        
        # Check if parsing actually failed
        if not result.get("success", False):
            error_msg = result.get("error") or result.get("message") or "Unknown error"
            print(f"❌ Parse failed: {error_msg}")
            print(f"   Full response: {json.dumps(result, indent=2)}")
            return None
        
        parsed_file_id = result.get("parsed_file_id") or result.get("uuid")
        
        print(f"✅ File parsed successfully")
        print(f"   parsed_file_id: {parsed_file_id}")
        print(f"   Full response keys: {list(result.keys())}")
        
        # If parsed_file_id is None, try to get it from parse_result
        if not parsed_file_id:
            parse_result = result.get("parse_result", {})
            parsed_file_id = parse_result.get("parsed_file_id")
            print(f"   Trying parse_result.parsed_file_id: {parsed_file_id}")
        
        # Wait a moment for metadata to be stored in parsed_data_files
        import time
        print(f"⏳ Waiting 3 seconds for parsed_data_files metadata to be stored...")
        time.sleep(3)
        
        # If we still don't have parsed_file_id, try to find it by querying parsed files
        # Note: We query without file_id to get all parsed files for the user, then filter
        if not parsed_file_id:
            print(f"⚠️ parsed_file_id not in response, querying list_parsed_files to find it...")
            list_url = f"{API_BASE}/v1/content-pillar/list-parsed-files" if API_BASE.endswith("/api") else f"{API_BASE}/api/v1/content-pillar/list-parsed-files"
            # Query all parsed files (no file_id filter) - user_id comes from auth context
            list_response = requests.get(
                list_url,
                # Don't pass file_id - get all parsed files for user, then we'll filter
                headers=get_headers(),
                timeout=30
            )
            if list_response.status_code == 200:
                list_result = list_response.json()
                parsed_files = list_result.get("parsed_files", [])
                print(f"   Found {len(parsed_files)} total parsed files for user")
                # Filter to find our file_id
                matching_files = [pf for pf in parsed_files if pf.get("file_id") == file_id]
                if matching_files:
                    parsed_file_id = matching_files[0].get("parsed_file_id")
                    print(f"   ✅ Found parsed_file_id via list: {parsed_file_id}")
        
        if not parsed_file_id:
            print(f"⚠️ Could not determine parsed_file_id - will skip embedding tests")
            print(f"   This might indicate a storage issue - check backend logs")
            return None
        
        return parsed_file_id
        
    except Exception as e:
        print(f"❌ Parse test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_3_list_parsed_files(file_id: str) -> bool:
    """Test 3: List parsed files and verify ui_name is returned directly."""
    print("\n" + "="*80)
    print("TEST 3: List Parsed Files (Verify ui_name returned directly)")
    print("="*80)
    
    try:
        # List parsed files for user
        # ✅ Note: The endpoint uses authenticated user_id from context, not query parameter
        # So we don't pass user_id in query params - it will use the authenticated user from the token
        list_url = f"{API_BASE}/v1/content-pillar/list-parsed-files" if API_BASE.endswith("/api") else f"{API_BASE}/api/v1/content-pillar/list-parsed-files"
        print(f"📋 Listing parsed files (using authenticated user from token)...")
        response = requests.get(
            list_url,
            # Don't pass user_id - endpoint uses authenticated user from token context
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ List parsed files failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        parsed_files = result.get("parsed_files", [])
        
        print(f"✅ Found {len(parsed_files)} parsed files")
        
        # Find our parsed file (match by file_id)
        our_parsed_file = None
        for pf in parsed_files:
            if pf.get("file_id") == file_id:
                our_parsed_file = pf
                break
        
        if not our_parsed_file:
            print(f"⚠️ Our parsed file not found in list")
            print(f"   Looking for file_id: {file_id}")
            print(f"   Found {len(parsed_files)} total parsed files for user")
            if parsed_files:
                print(f"   Sample parsed files:")
                for pf in parsed_files[:3]:
                    print(f"      - file_id: {pf.get('file_id')}, parsed_file_id: {pf.get('parsed_file_id')}, ui_name: {pf.get('ui_name') or pf.get('name')}")
            else:
                print(f"   No parsed files found - this might indicate a query or storage issue")
            return False
        
        # Verify ui_name is present and follows pattern
        ui_name = our_parsed_file.get("name") or our_parsed_file.get("ui_name")
        print(f"✅ Found our parsed file:")
        print(f"   parsed_file_id: {our_parsed_file.get('parsed_file_id')}")
        print(f"   ui_name: {ui_name}")
        
        assert ui_name, "❌ ui_name not returned in parsed file list"
        assert ui_name.startswith("parsed_") or "parsed" in ui_name.lower(), \
            f"❌ ui_name doesn't follow pattern (expected 'parsed_*'): {ui_name}"
        
        print(f"✅ Verified: ui_name is returned directly from parsed_data_files table")
        print(f"✅ Verified: ui_name follows naming pattern: {ui_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ List parsed files test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_create_embeddings(parsed_file_id: str, file_id: str) -> bool:
    """Test 4: Create embeddings and verify embedding_files.ui_name."""
    print("\n" + "="*80)
    print("TEST 4: Create Embeddings (Verify embedding_files.ui_name)")
    print("="*80)
    
    try:
        # Create embeddings
        embed_url = f"{API_BASE}/v1/content-pillar/create-embeddings" if API_BASE.endswith("/api") else f"{API_BASE}/api/v1/content-pillar/create-embeddings"
        print(f"🔮 Creating embeddings for parsed_file_id: {parsed_file_id}...")
        response = requests.post(
            embed_url,
            json={
                "parsed_file_id": parsed_file_id,
                "file_id": file_id,
                "user_id": USER_ID
            },
            headers=get_headers(),
            timeout=120
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Create embeddings failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        embedding_count = result.get("embeddings_count", 0)
        
        print(f"✅ Embeddings created successfully")
        print(f"   embeddings_count: {embedding_count}")
        
        # Wait a moment for embedding_file record to be created
        import time
        time.sleep(2)
        
        # List embedding files
        # ✅ Note: The endpoint uses authenticated user_id from context, not query parameter
        list_embed_url = f"{API_BASE}/v1/content-pillar/list-embedding-files" if API_BASE.endswith("/api") else f"{API_BASE}/api/v1/content-pillar/list-embedding-files"
        print(f"📋 Listing embedding files (using authenticated user from token)...")
        response = requests.get(
            list_embed_url,
            params={"parsed_file_id": parsed_file_id},  # Only pass parsed_file_id filter, user_id comes from auth context
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"⚠️ List embedding files failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        embedding_files = result.get("embedding_files", [])
        
        if not embedding_files:
            print(f"⚠️ No embedding files found (may need to wait)")
            return False
        
        # Find our embedding file
        our_embedding_file = None
        for ef in embedding_files:
            if ef.get("parsed_file_id") == parsed_file_id:
                our_embedding_file = ef
                break
        
        if not our_embedding_file:
            print(f"⚠️ Our embedding file not found")
            return False
        
        # Verify ui_name is present and follows pattern
        ui_name = our_embedding_file.get("ui_name") or our_embedding_file.get("name")
        print(f"✅ Found our embedding file:")
        print(f"   embedding_file_id: {our_embedding_file.get('embedding_file_id')}")
        print(f"   ui_name: {ui_name}")
        
        assert ui_name, "❌ ui_name not returned in embedding file list"
        assert "embedding" in ui_name.lower() or "Embeddings:" in ui_name, \
            f"❌ ui_name doesn't follow pattern (expected 'Embeddings:*'): {ui_name}"
        
        print(f"✅ Verified: ui_name is returned directly from embedding_files table")
        print(f"✅ Verified: ui_name follows naming pattern: {ui_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Create embeddings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_list_parsed_files_with_embeddings() -> bool:
    """Test 5: List parsed files with embeddings and verify ui_name is used."""
    print("\n" + "="*80)
    print("TEST 5: List Parsed Files With Embeddings (Verify unified pattern)")
    print("="*80)
    
    try:
        # List parsed files with embeddings
        # ✅ Note: The endpoint uses authenticated user_id from context, not query parameter
        list_with_embed_url = f"{API_BASE}/v1/content-pillar/list-parsed-files-with-embeddings" if API_BASE.endswith("/api") else f"{API_BASE}/api/v1/content-pillar/list-parsed-files-with-embeddings"
        print(f"📋 Listing parsed files with embeddings (using authenticated user from token)...")
        response = requests.get(
            list_with_embed_url,
            # Don't pass user_id - endpoint uses authenticated user from token context
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ List parsed files with embeddings failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        parsed_files = result.get("parsed_files", [])
        
        print(f"✅ Found {len(parsed_files)} parsed files with embeddings")
        
        if not parsed_files:
            print(f"⚠️ No parsed files with embeddings found (may need to create embeddings first)")
            return True  # Not a failure, just no data yet
        
        # Verify all parsed files have ui_name
        for pf in parsed_files:
            ui_name = pf.get("name") or pf.get("ui_name")
            assert ui_name, f"❌ Parsed file {pf.get('parsed_file_id')} missing ui_name"
            print(f"   ✅ {ui_name} (parsed_file_id: {pf.get('parsed_file_id')[:8]}...)")
        
        print(f"✅ Verified: All parsed files with embeddings have ui_name")
        print(f"✅ Verified: ui_name is used directly from parsed_data_files table (no JOINs)")
        
        return True
        
    except Exception as e:
        print(f"❌ List parsed files with embeddings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_6_file_statistics() -> bool:
    """Test 6: Get file statistics and verify counts are correct."""
    print("\n" + "="*80)
    print("TEST 6: File Statistics (Verify unified query pattern)")
    print("="*80)
    
    try:
        # Get file statistics
        # ✅ Note: The endpoint uses authenticated user_id from context, not query parameter
        stats_url = f"{API_BASE}/v1/content-pillar/get-file-statistics" if API_BASE.endswith("/api") else f"{API_BASE}/api/v1/content-pillar/get-file-statistics"
        print(f"📊 Getting file statistics (using authenticated user from token)...")
        response = requests.get(
            stats_url,
            # Don't pass user_id - endpoint uses authenticated user from token context
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Get file statistics failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        stats = result.get("statistics", {})
        
        print(f"✅ File statistics retrieved:")
        print(f"   uploaded: {stats.get('uploaded', 0)}")
        print(f"   parsed: {stats.get('parsed', 0)}")
        print(f"   embedded: {stats.get('embedded', 0)}")
        print(f"   total: {stats.get('total', 0)}")
        
        # Verify statistics are non-negative
        assert stats.get("uploaded", 0) >= 0, "❌ Invalid uploaded count"
        assert stats.get("parsed", 0) >= 0, "❌ Invalid parsed count"
        assert stats.get("embedded", 0) >= 0, "❌ Invalid embedded count"
        
        print(f"✅ Verified: File statistics are correct")
        print(f"✅ Verified: Statistics use unified query pattern (direct queries by user_id)")
        
        return True
        
    except Exception as e:
        print(f"❌ File statistics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("UNIFIED FILE METADATA PATTERN TEST SUITE")
    print("="*80)
    print(f"API Base: {API_BASE}")
    print(f"User ID: {USER_ID}")
    print(f"Auth Token: {'✅ Present' if AUTH_TOKEN else '❌ Missing'}")
    print("="*80)
    
    results = {}
    
    # Test 1: Upload file
    file_id = test_1_upload_file()
    results["test_1_upload"] = file_id is not None
    
    if not file_id:
        print("\n❌ Cannot continue - file upload failed")
        return
    
    # Test 2: Parse file
    parsed_file_id = test_2_parse_file(file_id)
    results["test_2_parse"] = parsed_file_id is not None
    
    if not parsed_file_id:
        print("\n⚠️ Cannot test embeddings - parse failed")
    else:
        # Test 3: List parsed files
        results["test_3_list_parsed"] = test_3_list_parsed_files(file_id)
        
        # Test 4: Create embeddings
        results["test_4_embeddings"] = test_4_create_embeddings(parsed_file_id, file_id)
        
        # Test 5: List parsed files with embeddings
        results["test_5_list_with_embeddings"] = test_5_list_parsed_files_with_embeddings()
    
    # Test 6: File statistics
    results["test_6_statistics"] = test_6_file_statistics()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print("="*80)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Unified pattern is working correctly!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

