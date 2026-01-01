#!/usr/bin/env python3
"""
Upload the new valid ASCII test file and copybook to the platform.
This file matches the copybook exactly and should parse without validation errors.
"""

import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.insert(0, '/app')

# Read the test files
script_dir = Path(__file__).parent
test_files_dir = script_dir / "clean_test_files"

data_file = test_files_dir / "valid_ascii_test_data.bin"
copybook_file = test_files_dir / "valid_ascii_test_copybook.cpy"

if not data_file.exists():
    print(f"❌ Data file not found: {data_file}")
    print("   Run scripts/create_valid_ascii_test_file.py first to create the test files.")
    sys.exit(1)

if not copybook_file.exists():
    print(f"❌ Copybook file not found: {copybook_file}")
    print("   Run scripts/create_valid_ascii_test_file.py first to create the test files.")
    sys.exit(1)

# Read file contents
with open(data_file, 'rb') as f:
    data_content = f.read()

with open(copybook_file, 'rb') as f:
    copybook_content = f.read()

print(f"📄 Data file: {data_file}")
print(f"   Size: {len(data_content)} bytes")
print(f"📄 Copybook file: {copybook_file}")
print(f"   Size: {len(copybook_content)} bytes")
print()

async def main():
    print("=" * 60)
    print("Uploading Valid ASCII Test Files")
    print("=" * 60)
    print()
    
    try:
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator()
        
        # Upload data file
        print("📤 Uploading: Valid ASCII Test Data")
        data_result = await orchestrator.upload_file(
            file_data=data_content,
            filename="valid_ascii_test_data.bin",
            file_type="application/octet-stream",
            user_id="test_user"
        )
        data_uuid = data_result.get("uuid") or data_result.get("file_id") if data_result else None
        if data_uuid:
            print(f"   ✅ UUID: {data_uuid}")
        else:
            print(f"   ❌ Failed: {data_result}")
            return
        
        # Upload copybook
        print("\n📤 Uploading: Valid ASCII Test Copybook")
        copybook_result = await orchestrator.upload_file(
            file_data=copybook_content,
            filename="valid_ascii_test_copybook.cpy",
            file_type="text/plain",
            user_id="test_user"
        )
        copybook_uuid = copybook_result.get("uuid") or copybook_result.get("file_id") if copybook_result else None
        if copybook_uuid:
            print(f"   ✅ UUID: {copybook_uuid}")
        else:
            print(f"   ❌ Failed: {copybook_result}")
            return
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 UPLOAD SUMMARY")
        print("=" * 60)
        if data_uuid and copybook_uuid:
            print(f"\n✅ Both files uploaded successfully!")
            print(f"   Data file UUID: {data_uuid}")
            print(f"   Copybook UUID: {copybook_uuid}")
            print(f"\n🎯 Next steps:")
            print(f"   1. Go to Content Pillar in the UI")
            print(f"   2. Find 'valid_ascii_test_data.bin'")
            print(f"   3. Use 'valid_ascii_test_copybook.cpy' as the copybook")
            print(f"   4. Test parsing - should work correctly with no validation errors!")
        else:
            print(f"\n❌ Upload failed")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())









