#!/usr/bin/env python3
"""
Simple Direct Binary Parsing Test

Run this inside the backend container:
  docker-compose exec backend python3 /app/scripts/test_binary_direct_simple.py

Or copy to container first, then run.
"""

import asyncio
import sys
import os

# Set working directory
os.chdir('/app')
sys.path.insert(0, '/app')

async def test():
    """Test binary parsing directly."""
    print("="*80)
    print("DIRECT BINARY PARSING TEST")
    print("="*80)
    
    try:
        # Import main app to get initialized services
        from main import app
        
        # Get DI container from app state (if available)
        # Or use the lifespan context
        print("\n📋 Getting services from running app...")
        
        # Access services via the app's dependency injection
        # The simplest way: use the app's startup context
        from main import app_state
        
        # Try to get di_container
        di_container = None
        if 'di_container' in app_state:
            di_container = app_state['di_container']
        else:
            # Try to get from managers
            if 'managers' in app_state:
                managers = app_state['managers']
                if 'DeliveryManager' in managers:
                    delivery_manager = managers['DeliveryManager']
                    di_container = delivery_manager.di_container if hasattr(delivery_manager, 'di_container') else None
        
        if not di_container:
            print("❌ Could not get DI container from app state")
            print("   Trying alternative: access via DeliveryManager directly...")
            # Alternative: try to import and get directly
            try:
                from backend.business_enablement.delivery_manager.delivery_manager import DeliveryManager
                # This won't work without proper initialization
                print("   ⚠️  Direct import requires full initialization")
                return False
            except Exception as e:
                print(f"   ❌ Direct import failed: {e}")
                return False
        
        # Get DeliveryManager
        delivery_manager = di_container.get("DeliveryManager")
        if not delivery_manager:
            print("❌ DeliveryManager not available")
            return False
        
        content_orchestrator = delivery_manager.content_orchestrator
        if not content_orchestrator:
            print("❌ ContentOrchestrator not available")
            return False
        
        print("✅ Services obtained")
        
        # Test data
        binary_data = b"CUST001   John Doe                              030New York                    " \
                     b"CUST002   Jane Smith                            025San Francisco               "
        copybook = """01  CUSTOMER-RECORD.
    05  CUSTOMER-ID        PIC X(10).
    05  CUSTOMER-NAME      PIC X(50).
    05  CUSTOMER-AGE       PIC 9(3).
    05  CUSTOMER-CITY      PIC X(30).
"""
        
        print("\n📤 Uploading binary file...")
        upload_result = await content_orchestrator.handle_content_upload(
            file_data=binary_data,
            filename="test_binary.bin",
            file_type="application/octet-stream",
            user_id="test_user_direct",
            session_id="test_session_direct"
        )
        
        if not upload_result.get("success"):
            print(f"❌ Upload failed: {upload_result.get('error')}")
            return False
        
        file_id = upload_result.get("file_id")
        print(f"✅ Upload successful: file_id={file_id}")
        
        print("\n⚙️  Parsing binary file with copybook...")
        parse_result = await content_orchestrator.process_file(
            file_id=file_id,
            user_id="test_user_direct",
            copybook_file_id=None,
            processing_options={"copybook": copybook, "file_type": "binary"}
        )
        
        if not parse_result.get("success"):
            print(f"❌ Parsing failed: {parse_result.get('error')}")
            return False
        
        parsed_file_id = parse_result.get("parsed_file_id")
        print(f"✅ Parsing successful: parsed_file_id={parsed_file_id}")
        
        parse_summary = parse_result.get("parse_result", {})
        print(f"\n📊 Parse Summary:")
        print(f"   Parsing type: {parse_summary.get('parsing_type', 'unknown')}")
        print(f"   Table count: {parse_summary.get('table_count', 0)}")
        print(f"   Record count: {parse_summary.get('record_count', 0)}")
        
        print("\n✅ DIRECT BINARY PARSING TEST PASSED")
        print("   Core functionality works: Upload → Parse → Save as Parquet")
        print("   (API serialization is a separate issue)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test())
    sys.exit(0 if result else 1)


