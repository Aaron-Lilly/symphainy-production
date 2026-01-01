#!/usr/bin/env python3
"""
Functional Test for DIL SDK (Phase 4.1)

Tests the DIL SDK initialization and basic operations.

Usage:
    python scripts/test_dil_sdk.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Set TEST_MODE to make Traefik optional
os.environ["TEST_MODE"] = "true"

# Add project root to path
project_root = Path(__file__).parent.parent / "symphainy-platform"
sys.path.insert(0, str(project_root))

from typing import Dict, Any


async def test_dil_sdk_initialization():
    """Test DIL SDK initialization."""
    print("\n" + "="*80)
    print("TEST: DIL SDK Initialization (Phase 4.1)")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
        from backend.smart_city.services.librarian.librarian_service import LibrarianService
        from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
        from backend.smart_city.services.nurse.nurse_service import NurseService
        from backend.smart_city.sdk.dil_sdk import DILSDK
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Public Works Foundation
        pwf = PublicWorksFoundationService(di_container=di_container)
        await pwf.initialize_foundation()
        di_container.public_works_foundation = pwf
        
        # Initialize Smart City Services
        print("\n1. Initializing Smart City Services...")
        content_steward = ContentStewardService(di_container=di_container)
        await content_steward.initialize()
        
        librarian = LibrarianService(di_container=di_container)
        await librarian.initialize()
        
        data_steward = DataStewardService(di_container=di_container)
        await data_steward.initialize()
        
        nurse = NurseService(di_container=di_container)
        await nurse.initialize()
        
        print("✅ All Smart City services initialized")
        
        # Initialize DIL SDK
        print("\n2. Initializing DIL SDK...")
        smart_city_services = {
            "content_steward": content_steward,
            "librarian": librarian,
            "data_steward": data_steward,
            "nurse": nurse
        }
        
        dil_sdk = DILSDK(smart_city_services)
        print("✅ DIL SDK initialized")
        
        # Verify service references
        print("\n3. Verifying service references...")
        if not dil_sdk.content_steward:
            print("❌ Content Steward not available")
            return False
        if not dil_sdk.librarian:
            print("❌ Librarian not available")
            return False
        if not dil_sdk.data_steward:
            print("❌ Data Steward not available")
            return False
        if not dil_sdk.nurse:
            print("❌ Nurse not available")
            return False
        
        print("✅ All service references verified")
        
        # Test a simple operation (upload_file)
        print("\n4. Testing upload_file() operation...")
        user_context = {
            "tenant_id": "test_tenant",
            "user_id": "test_user",
            "permissions": ["write", "read", "execute", "admin"]
        }
        
        test_file_data = b"Test file content for DIL SDK testing"
        upload_result = await dil_sdk.upload_file(
            file_data=test_file_data,
            file_name="test_dil_sdk.txt",
            file_type="txt",
            metadata={"description": "Test file for DIL SDK"},
            user_context=user_context
        )
        
        if not upload_result or "file_id" not in upload_result:
            print(f"❌ upload_file failed: {upload_result}")
            return False
        
        file_id = upload_result["file_id"]
        print(f"✅ File uploaded via DIL SDK: {file_id}")
        
        # Test get_file
        print("\n5. Testing get_file() operation...")
        file_record = await dil_sdk.get_file(file_id, user_context)
        if not file_record:
            print("❌ get_file returned None")
            return False
        print(f"✅ File retrieved via DIL SDK: {file_record.get('ui_name', 'N/A')}")
        
        print("\n" + "="*80)
        print("✅ DIL SDK tests passed!")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing DIL SDK: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all DIL SDK tests."""
    print("\n" + "="*80)
    print("DIL SDK FUNCTIONAL TEST (Phase 4.1)")
    print("="*80)
    
    results = {}
    results["dil_sdk"] = await test_dil_sdk_initialization()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All DIL SDK tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


