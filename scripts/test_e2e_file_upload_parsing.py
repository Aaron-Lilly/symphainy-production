#!/usr/bin/env python3
"""
E2E File Upload & Parsing Test

Tests the complete flow:
1. Upload file
2. Verify upload success
3. Trigger parsing
4. Verify parsing success
"""

import requests
import json
import sys
import os
from pathlib import Path

# Test configuration
API_BASE = "http://localhost/api"  # Via Traefik
API_BASE_DIRECT = "http://localhost:8000"  # Direct backend
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
    # Use test@symphainy.com (known working user) or override via env
    test_email = os.getenv("TEST_USER_EMAIL") or os.getenv("TEST_SUPABASE_EMAIL") or "test@symphainy.com"
    test_password = os.getenv("TEST_USER_PASSWORD") or os.getenv("TEST_SUPABASE_PASSWORD") or "test_password_123"
    
    try:
        print(f"🔐 Attempting to get auth token via login...")
        print(f"   Using email: {test_email}")
        # Auth router is mounted at /api/auth
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
    
    # Fallback - return None (will fail auth, but we'll see the error)
    print(f"⚠️ No auth token available - test will fail with 401")
    return None

AUTH_TOKEN = get_auth_token()

# Test file (create a simple CSV for testing)
TEST_FILE_CONTENT = """name,age,city
John,30,New York
Jane,25,San Francisco
Bob,35,Chicago
"""

def create_test_file():
    """Create a test CSV file."""
    test_file = Path("/tmp/test_e2e_file.csv")
    test_file.write_text(TEST_FILE_CONTENT)
    return test_file

def test_upload_file():
    """Test file upload."""
    print("\n" + "="*80)
    print("TEST 1: File Upload")
    print("="*80)
    
    # Create test file
    test_file = create_test_file()
    print(f"📄 Created test file: {test_file}")
    
    # Try via Traefik first, then direct
    for api_base in [API_BASE, API_BASE_DIRECT]:
        try:
            print(f"\n🔍 Trying API: {api_base}")
            
            # Prepare multipart form data
            files = {
                'file': ('test_e2e_file.csv', test_file.open('rb'), 'text/csv')
            }
            data = {
                'file_type': 'csv',
                'user_id': USER_ID,
                'session_id': SESSION_ID
            }
            
            # Upload file
            url = f"{api_base}/v1/content-pillar/upload-file"
            print(f"📤 Uploading to: {url}")
            
            # Add Authorization header (if token available)
            headers = {
                'X-Session-Token': SESSION_ID
            }
            if AUTH_TOKEN:
                headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
            else:
                print(f"⚠️ No auth token - request will likely fail with 401")
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"📄 Response: {json.dumps(result, indent=2)}")
                
                file_id = result.get("file_id") or result.get("uuid")
                workflow_id = result.get("workflow_id")
                
                if file_id:
                    print(f"✅ File ID: {file_id}")
                    if workflow_id:
                        print(f"✅ Workflow ID: {workflow_id}")
                    return True, file_id, workflow_id, result
                else:
                    print(f"⚠️ No file_id in response")
                    return False, None, None, result
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"📄 Response: {response.text}")
                if api_base == API_BASE_DIRECT:
                    return False, None, None, None
                continue
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            if api_base == API_BASE_DIRECT:
                return False, None, None, None
            continue
    
    return False, None, None, None

def test_parse_file(file_id):
    """Test file parsing."""
    print("\n" + "="*80)
    print("TEST 2: File Parsing")
    print("="*80)
    
    if not file_id:
        print("❌ No file_id provided, skipping parsing test")
        return False, None
    
    # Try via Traefik first, then direct
    for api_base in [API_BASE, API_BASE_DIRECT]:
        try:
            print(f"\n🔍 Trying API: {api_base}")
            
            # Trigger parsing
            url = f"{api_base}/v1/content-pillar/process-file/{file_id}"
            print(f"⚙️ Processing file: {url}")
            
            data = {
                'user_id': USER_ID
            }
            
            # Add Authorization header (if token available)
            headers = {
                'X-Session-Token': SESSION_ID
            }
            if AUTH_TOKEN:
                headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
            else:
                print(f"⚠️ No auth token - request will likely fail with 401")
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Parsing successful!")
                print(f"📄 Response: {json.dumps(result, indent=2)}")
                
                success = result.get("success", False)
                parse_result = result.get("parse_result", {})
                
                if success:
                    print(f"✅ Parsing completed successfully")
                    return True, result
                else:
                    print(f"⚠️ Parsing returned success=False")
                    print(f"📄 Error: {result.get('error', 'Unknown error')}")
                    return False, result
            else:
                print(f"❌ Parsing failed: {response.status_code}")
                print(f"📄 Response: {response.text}")
                if api_base == API_BASE_DIRECT:
                    return False, None
                continue
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            if api_base == API_BASE_DIRECT:
                return False, None
            continue
    
    return False, None

def main():
    """Run E2E tests."""
    print("\n" + "="*80)
    print("E2E FILE UPLOAD & PARSING TEST")
    print("="*80)
    print("\nTesting complete flow: Upload → Parse")
    print("="*80)
    
    # Test 1: Upload
    upload_success, file_id, workflow_id, upload_result = test_upload_file()
    
    if not upload_success:
        print("\n" + "="*80)
        print("❌ E2E TEST FAILED: File upload failed")
        print("="*80)
        return 1
    
    # Test 2: Parse
    parse_success, parse_result = test_parse_file(file_id)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Upload: {'PASS' if upload_success else 'FAIL'}")
    print(f"   File ID: {file_id}")
    print(f"   Workflow ID: {workflow_id}")
    print(f"✅ Parsing: {'PASS' if parse_success else 'FAIL'}")
    
    if upload_success and parse_success:
        print("\n🎉 E2E TEST PASSED: Upload and parsing both successful!")
        return 0
    elif upload_success:
        print("\n⚠️ E2E TEST PARTIAL: Upload succeeded but parsing failed")
        return 1
    else:
        print("\n❌ E2E TEST FAILED: Upload failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

