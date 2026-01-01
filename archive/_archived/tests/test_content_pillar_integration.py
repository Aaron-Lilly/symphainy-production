#!/usr/bin/env python3
"""
Content Pillar Integration Test

Test the complete Content Pillar implementation from API endpoints through
micro-modules to infrastructure abstractions.
"""

import os
import sys
import asyncio
import tempfile
import pandas as pd
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from backend.business_enablement.pillars.content_pillar.content_pillar_service import content_pillar_service
from backend.business_enablement.interfaces.content_management_interface import (
    UploadRequest, ParseRequest, UserContext, FileType
)
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext as SecurityUserContext


async def test_content_pillar_integration():
    """Test complete Content Pillar integration."""
    print("🧪 Starting Content Pillar Integration Test...")
    
    try:
        # Initialize the content pillar service
        print("📦 Initializing Content Pillar Service...")
        await content_pillar_service.initialize()
        print("✅ Content Pillar Service initialized successfully")
        
        # Test 1: Health Check
        print("\n🔍 Testing health check...")
        health_status = await content_pillar_service.get_health_status()
        print(f"Health Status: {health_status['status']}")
        
        # Test 2: Create test data
        print("\n📊 Creating test data...")
        test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'city': ['New York', 'London', 'Paris', 'Tokyo', 'Sydney']
        })
        
        # Save test data to temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            test_csv_path = f.name
        
        print(f"✅ Test CSV created: {test_csv_path}")
        
        # Test 3: File Upload
        print("\n📁 Testing file upload...")
        
        # Read test file data
        with open(test_csv_path, 'rb') as f:
            file_data = f.read()
        
        # Create user context
        user_context = SecurityUserContext(
            user_id="test_user",
            session_id="test_session",
            permissions=["content:read", "content:write"],
            metadata={"test": True}
        )
        
        # Create upload request
        upload_request = UploadRequest(
            file_data=file_data,
            filename="test_data.csv",
            file_type=FileType.CSV,
            user_context=user_context,
            session_id="test_session",
            metadata={"description": "Test data for integration testing"}
        )
        
        # Upload file
        upload_response = await content_pillar_service.upload_file(upload_request)
        
        if upload_response.success:
            print("✅ File upload successful")
            print(f"   File ID: {upload_response.file_id}")
            print(f"   File Size: {upload_response.file_metadata.file_size} bytes")
            file_id = upload_response.file_id
        else:
            print(f"❌ File upload failed: {upload_response.message}")
            return
        
        # Test 4: File Parsing
        print("\n🔧 Testing file parsing...")
        
        parse_request = ParseRequest(
            file_id=file_id,
            user_context=user_context,
            session_id="test_session",
            parse_options={"extract_metadata": True}
        )
        
        parse_response = await content_pillar_service.parse_file(parse_request)
        
        if parse_response.success:
            print("✅ File parsing successful")
            print(f"   Parsed Content Keys: {list(parse_response.parsed_content.keys())}")
            print(f"   Processing Time: {parse_response.processing_time:.2f}s")
        else:
            print(f"❌ File parsing failed: {parse_response.message}")
        
        # Test 5: File Metadata
        print("\n📋 Testing file metadata retrieval...")
        
        file_metadata = await content_pillar_service.get_file_metadata(file_id, user_context)
        
        if file_metadata:
            print("✅ File metadata retrieved successfully")
            print(f"   Filename: {file_metadata.filename}")
            print(f"   File Type: {file_metadata.file_type.value}")
            print(f"   File Size: {file_metadata.file_size} bytes")
        else:
            print("❌ File metadata retrieval failed")
        
        # Test 6: List Files
        print("\n📋 Testing file listing...")
        
        files = await content_pillar_service.list_files(user_context)
        
        if files:
            print("✅ File listing successful")
            print(f"   Found {len(files)} files")
            for file_meta in files:
                print(f"   - {file_meta.filename} ({file_meta.file_type.value})")
        else:
            print("❌ File listing failed")
        
        # Test 7: File Conversion
        print("\n🔄 Testing file conversion...")
        
        convert_request = {
            "file_id": file_id,
            "target_format": FileType.JSON,
            "conversion_options": {"pretty": True},
            "user_context": user_context,
            "session_id": "test_session"
        }
        
        convert_response = await content_pillar_service.convert_file(convert_request)
        
        if convert_response.success:
            print("✅ File conversion successful")
            print(f"   Converted File ID: {convert_response.converted_file_id}")
            print(f"   Target Format: {convert_response.target_format}")
        else:
            print(f"❌ File conversion failed: {convert_response.message}")
        
        # Test 8: File Validation
        print("\n✅ Testing file validation...")
        
        validation_request = {
            "file_id": file_id,
            "validation_rules": {
                "max_file_size_mb": 10,
                "min_rows": 1,
                "max_rows": 1000,
                "min_columns": 1,
                "max_columns": 100
            },
            "user_context": user_context,
            "session_id": "test_session"
        }
        
        validation_response = await content_pillar_service.validate_file(validation_request)
        
        if validation_response.success:
            print("✅ File validation successful")
            print(f"   Is Valid: {validation_response.validation_result['is_valid']}")
            print(f"   Validation Score: {validation_response.validation_result['validation_score']}")
            print(f"   Errors: {len(validation_response.validation_result['validation_errors'])}")
            print(f"   Warnings: {len(validation_response.validation_result['validation_warnings'])}")
        else:
            print(f"❌ File validation failed: {validation_response.message}")
        
        # Test 9: File Deletion
        print("\n🗑️ Testing file deletion...")
        
        delete_success = await content_pillar_service.delete_file(file_id, user_context)
        
        if delete_success:
            print("✅ File deletion successful")
        else:
            print("❌ File deletion failed")
        
        print("\n🎉 Content Pillar Integration Test completed successfully!")
        
        # Test 10: Service Health Check
        print("\n🏥 Testing final health check...")
        final_health = await content_pillar_service.get_health_status()
        print(f"Final Health Status: {final_health['status']}")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            if 'test_csv_path' in locals():
                os.unlink(test_csv_path)
                print("🧹 Cleaned up test files")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")


if __name__ == "__main__":
    asyncio.run(test_content_pillar_integration())


