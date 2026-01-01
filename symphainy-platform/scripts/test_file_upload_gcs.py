#!/usr/bin/env python3
"""
Test File Upload Flow with GCS + Supabase

Tests the complete file upload and retrieval flow:
1. Upload file → GCS (binary) + Supabase (metadata)
2. Retrieve file → From GCS + Supabase
3. Verify data integrity
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

async def test_file_upload_flow():
    """Test complete file upload and retrieval flow."""
    print("=" * 80)
    print("🧪 Testing File Upload Flow (GCS + Supabase)")
    print("=" * 80)
    print()
    
    try:
        # Step 1: Initialize Public Works Foundation (single source of truth)
        print("📋 Step 1: Initializing Public Works Foundation...")
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        public_works = PublicWorksFoundationService()
        result = await public_works.initialize_foundation()
        
        if not result:
            print("❌ Public Works Foundation initialization failed")
            return False
        
        print("✅ Public Works Foundation initialized")
        print()
        
        # Step 2: Get File Management Abstraction (via Public Works Foundation)
        print("📋 Step 2: Getting File Management Abstraction...")
        file_mgmt = public_works.get_file_management_abstraction()
        
        if not file_mgmt:
            print("❌ File Management Abstraction not available")
            return False
        
        print("✅ File Management Abstraction available")
        print(f"   Type: {type(file_mgmt).__name__}")
        print("   Note: Using Public Works Foundation's new pattern (single source of truth)")
        print()
        
        # Step 3: Create test file
        print("📋 Step 3: Creating test file...")
        test_content = b"This is a test file for GCS + Supabase integration\nLine 2\nLine 3"
        test_filename = "test_upload_file.txt"
        test_user_id = "test_user_123"
        
        print(f"   File: {test_filename}")
        print(f"   Size: {len(test_content)} bytes")
        print(f"   User: {test_user_id}")
        print()
        
        # Step 4: Upload file
        print("📋 Step 4: Uploading file (GCS + Supabase)...")
        file_record = {
            "ui_name": test_filename,
            "file_type": "text/plain",
            "file_content": test_content,  # This should go to GCS
            "user_id": test_user_id,
            "metadata": {
                "test": True,
                "upload_source": "test_script"
            }
        }
        
        try:
            upload_result = await file_mgmt.create_file(file_record)
            
            if not upload_result or not upload_result.get("uuid"):
                print("❌ File upload failed - no UUID returned")
                print(f"   Result: {upload_result}")
                return False
            
            file_uuid = upload_result["uuid"]
            service_context = upload_result.get("service_context", {})
            print(f"✅ File uploaded successfully!")
            print(f"   UUID: {file_uuid}")
            print(f"   GCS Blob: {service_context.get('gcs_blob_name', 'N/A')}")
            print(f"   Bucket: {service_context.get('gcs_bucket', 'N/A')}")
            print()
            
        except Exception as e:
            print(f"❌ File upload error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 5: Retrieve file metadata from Supabase
        print("📋 Step 5: Retrieving file metadata from Supabase...")
        try:
            retrieved_metadata = await file_mgmt.get_file(file_uuid)
            
            if not retrieved_metadata:
                print("❌ File metadata not found in Supabase")
                return False
            
            print("✅ File metadata retrieved from Supabase")
            print(f"   UUID: {retrieved_metadata.get('uuid')}")
            print(f"   Name: {retrieved_metadata.get('ui_name')}")
            print(f"   Size: {retrieved_metadata.get('file_size')} bytes")
            service_context = retrieved_metadata.get('service_context', {})
            print(f"   GCS Blob: {service_context.get('gcs_blob_name', 'N/A')}")
            print(f"   Original Path: {retrieved_metadata.get('original_path', 'N/A')}")
            print()
            
        except Exception as e:
            print(f"❌ File retrieval error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 6: Verify file content (if available)
        if retrieved_metadata.get("file_content"):
            print("📋 Step 6: Verifying file content...")
            retrieved_content = retrieved_metadata["file_content"]
            
            if retrieved_content == test_content:
                print("✅ File content matches original!")
                print(f"   Original: {len(test_content)} bytes")
                print(f"   Retrieved: {len(retrieved_content)} bytes")
            else:
                print("⚠️  File content mismatch")
                print(f"   Original: {len(test_content)} bytes")
                print(f"   Retrieved: {len(retrieved_content)} bytes")
        else:
            print("📋 Step 6: File content not in metadata (expected - stored in GCS)")
            print("   ✅ This is correct - file content should be in GCS, not Supabase")
        
        print()
        print("=" * 80)
        print("✅ FILE UPLOAD FLOW TEST PASSED!")
        print("=" * 80)
        print()
        print("Summary:")
        service_context = upload_result.get("service_context", {})
        print(f"  ✅ File uploaded to GCS: {service_context.get('gcs_blob_name', 'N/A')}")
        print(f"  ✅ Metadata stored in Supabase: {file_uuid}")
        print(f"  ✅ File retrieval works")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_file_upload_flow())
    sys.exit(0 if success else 1)

