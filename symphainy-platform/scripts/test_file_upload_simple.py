#!/usr/bin/env python3
"""
Simple File Upload Test

Tests file upload via the API endpoint (simulating frontend request).
This tests the complete flow: API → ContentAnalysisOrchestrator → Content Steward → GCS + Supabase
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Load environment secrets
load_dotenv('.env.secrets')
load_dotenv('env_secrets_for_cursor.md')

async def test_via_api():
    """Test file upload via the actual API endpoint."""
    print("=" * 80)
    print("🧪 Testing File Upload via API Endpoint")
    print("=" * 80)
    print()
    
    # Create a test file
    test_file_path = project_root / "test_upload.txt"
    test_content = b"This is a test file for GCS + Supabase integration\nLine 2\nLine 3"
    
    with open(test_file_path, "wb") as f:
        f.write(test_content)
    
    print(f"📝 Created test file: {test_file_path}")
    print(f"   Size: {len(test_content)} bytes")
    print()
    
    # Test via curl (simulating frontend)
    print("📋 Testing via API endpoint...")
    import subprocess
    
    try:
        # First, check if server is running
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend server is running")
            else:
                print("⚠️  Backend server responded but may not be ready")
        except:
            print("⚠️  Backend server not running on port 8000")
            print("   Start it with: python3 main.py")
            print()
            print("   For now, testing configuration only...")
            return test_configuration_only()
        
        # Upload file
        print("📤 Uploading file via API...")
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path.name, f, "text/plain")}
            data = {"user_id": "test_user"}
            
            response = requests.post(
                "http://localhost:8000/api/mvp/content/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File upload successful!")
            print(f"   Response: {result}")
            
            file_id = result.get("file_id")
            if file_id:
                print()
                print("📋 Testing file retrieval...")
                
                # Try to parse the file
                parse_response = requests.post(
                    f"http://localhost:8000/api/mvp/content/parse/{file_id}",
                    json={"user_id": "test_user"},
                    timeout=30
                )
                
                if parse_response.status_code == 200:
                    parse_result = parse_response.json()
                    print("✅ File parsing successful!")
                    print(f"   Result: {parse_result.get('success', False)}")
                else:
                    print(f"⚠️  File parsing failed: {parse_response.status_code}")
                    print(f"   Response: {parse_response.text[:200]}")
            
            return True
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except ImportError:
        print("⚠️  requests library not available, using curl...")
        # Fall back to curl
        result = subprocess.run([
            "curl", "-X", "POST",
            "http://localhost:8000/api/mvp/content/upload",
            "-F", f"file=@{test_file_path}",
            "-F", "user_id=test_user"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ File upload successful!")
            print(f"   Response: {result.stdout}")
            return True
        else:
            print(f"❌ File upload failed")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if test_file_path.exists():
            test_file_path.unlink()

def test_configuration_only():
    """Test configuration without requiring server."""
    print("📋 Testing Configuration...")
    print()
    
    from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter
    
    config = ConfigAdapter()
    
    # Check Supabase
    supabase_url = config.get_supabase_url()
    supabase_secret = config.get_supabase_service_key()
    
    print("Supabase Configuration:")
    print(f"  URL: {supabase_url}")
    print(f"  Secret Key: {'✅ SET' if supabase_secret else '❌ NOT SET'}")
    print()
    
    # Check GCS
    gcs_project = config.get_gcs_project_id()
    gcs_bucket = config.get_gcs_bucket_name()
    gcs_creds = config.get_gcs_credentials_path()
    
    print("GCS Configuration:")
    print(f"  Project ID: {gcs_project}")
    print(f"  Bucket: {gcs_bucket}")
    print(f"  Credentials: {gcs_creds}")
    print()
    
    if supabase_url and supabase_secret and gcs_project and gcs_bucket:
        print("✅ Configuration looks good!")
        print("   Start the server and test the full flow.")
        return True
    else:
        print("❌ Configuration incomplete")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--config-only":
        success = test_configuration_only()
    else:
        success = asyncio.run(test_via_api())
    sys.exit(0 if success else 1)






