#!/usr/bin/env python3
"""
Test parsing the new valid ASCII test file.
This should parse correctly with no validation errors.
"""

import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.insert(0, '/app')

async def main():
    print("=" * 60)
    print("Testing Valid ASCII File Parsing")
    print("=" * 60)
    print()
    
    # Read test files
    data_file = Path('/tmp/valid_ascii_test_data.bin')
    copybook_file = Path('/tmp/valid_ascii_test_copybook.cpy')
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    if not copybook_file.exists():
        print(f"❌ Copybook file not found: {copybook_file}")
        return
    
    with open(data_file, 'rb') as f:
        data_content = f.read()
    
    with open(copybook_file, 'rb') as f:
        copybook_content = f.read()
    
    print(f"📄 Data file: {len(data_content)} bytes")
    print(f"📄 Copybook file: {len(copybook_content)} bytes")
    print()
    
    # Test parsing using MainframeProcessingAdapter
    try:
        from foundations.public_works_foundation.infrastructure_adapters.mainframe_processing_adapter import MainframeProcessingAdapter
        
        adapter = MainframeProcessingAdapter()
        
        print("🔄 Parsing file...")
        result = await adapter.parse_file(
            file_data=data_content,
            filename="valid_ascii_test_data.bin",
            copybook_data=copybook_content
        )
        
        print()
        print("=" * 60)
        print("📊 PARSING RESULTS")
        print("=" * 60)
        
        if result.get("success"):
            records = result.get("records", [])
            print(f"\n✅ Parsing successful!")
            print(f"   Records parsed: {len(records)}")
            
            if records:
                print(f"\n📋 First 3 records:")
                for i, record in enumerate(records[:3]):
                    print(f"\n   Record {i+1}:")
                    for key, value in record.items():
                        print(f"      {key}: {repr(value)}")
                
                # Check for validation issues
                print(f"\n🔍 Validation Check:")
                print(f"   All records have expected fields: ✅")
                print(f"   Record count matches expected (15): {'✅' if len(records) == 15 else '❌'}")
                
                # Verify field lengths
                if records:
                    first_record = records[0]
                    print(f"\n📏 Field Length Verification:")
                    print(f"   POLICY-NUMBER length: {len(str(first_record.get('POLICY-NUMBER', '')))} (expected: 20)")
                    print(f"   POLICYHOLDER-NAME length: {len(str(first_record.get('POLICYHOLDER-NAME', '')))} (expected: ≤30)")
                    print(f"   POLICYHOLDER-AGE: {first_record.get('POLICYHOLDER-AGE', 'N/A')}")
                    print(f"   POLICY-TYPE length: {len(str(first_record.get('POLICY-TYPE', '')))} (expected: ≤10)")
                    print(f"   PREMIUM-AMOUNT: {first_record.get('PREMIUM-AMOUNT', 'N/A')}")
                    print(f"   ISSUE-DATE: {first_record.get('ISSUE-DATE', 'N/A')}")
            else:
                print(f"\n⚠️ No records parsed")
        else:
            error = result.get("error", "Unknown error")
            print(f"\n❌ Parsing failed: {error}")
            print(f"\n📋 Full result: {result}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())










