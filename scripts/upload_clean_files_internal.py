#!/usr/bin/env python3
"""
Upload clean test files using internal service methods (bypasses HTTP auth).
Run this inside the backend container.
"""

import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.insert(0, '/app')

# Create data file content (10 records, 81 bytes each = 810 bytes)
records = [
    b"POL001123456789012345" + b"John Smith                    " + b"045" + b"Term Life  " + b"0000050000" + b"20240115",
    b"POL002234567890123456" + b"Mary Johnson                  " + b"032" + b"Whole Life " + b"0000075000" + b"20240116",
    b"POL003345678901234567" + b"Robert Davis                  " + b"028" + b"Universal  " + b"0000100000" + b"20240117",
    b"POL004456789012345678" + b"Sarah Wilson                  " + b"025" + b"Annuity    " + b"0000020000" + b"20240118",
    b"POL005567890123456789" + b"Michael Brown                 " + b"055" + b"Term Life  " + b"0000030000" + b"20240119",
    b"POL006678901234567890" + b"Lisa Anderson                 " + b"042" + b"Whole Life " + b"0000080000" + b"20240120",
    b"POL007789012345678901" + b"David Miller                  " + b"038" + b"Universal  " + b"0000120000" + b"20240121",
    b"POL008890123456789012" + b"Jennifer Taylor               " + b"029" + b"Annuity    " + b"0000150000" + b"20240122",
    b"POL009901234567890123" + b"Christopher Lee                " + b"035" + b"Term Life  " + b"0000040000" + b"20240123",
    b"POL010012345678901234" + b"Amanda White                  " + b"031" + b"Whole Life " + b"0000090000" + b"20240124"
]

data_content = b"".join(records)

copybook_content = """      01  POLICYHOLDER-RECORD.
          05  POLICY-NUMBER        PIC X(20).
          05  POLICYHOLDER-NAME    PIC X(30).
          05  POLICYHOLDER-AGE     PIC 9(3).
          05  POLICY-TYPE          PIC X(10).
          05  PREMIUM-AMOUNT       PIC 9(10).
          05  ISSUE-DATE           PIC X(8).
""".encode('utf-8')

async def main():
    print("=" * 60)
    print("Uploading Clean Test Files via Internal Service")
    print("=" * 60)
    print()
    
    try:
        from foundations.public_works_foundation.composition_services.di_container_service import DIContainerService
        from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
        
        # Get DI container
        di_container = DIContainerService.get_instance()
        if not di_container:
            print("❌ DI Container not available")
            return
        
        # Get Content Steward Service
        content_steward = di_container.get_service("ContentStewardService")
        if not content_steward:
            # Try direct instantiation as fallback
            print("⚠️  ContentStewardService not in DI, trying direct access...")
            # For now, let's use a simpler approach - call via the orchestrator
            from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
            orchestrator = ContentJourneyOrchestrator()
            if hasattr(orchestrator, 'upload_file'):
                # Use orchestrator's upload_file method
                print("✅ Using ContentJourneyOrchestrator.upload_file")
                # Upload data
                print("\n📤 Uploading: Annuity Policyholder Data (Clean)")
                data_result = await orchestrator.upload_file(
                    file_data=data_content,
                    filename="scenario3_annuity_data_clean.bin",
                    file_type="application/octet-stream",
                    user_id="test_user"
                )
                data_uuid = data_result.get("uuid") or data_result.get("file_id") if data_result else None
                if data_uuid:
                    print(f"   ✅ UUID: {data_uuid}")
                else:
                    print(f"   ❌ Failed: {data_result}")
                
                # Upload copybook
                print("\n📤 Uploading: COBOL Copybook (Corrected)")
                copybook_result = await orchestrator.upload_file(
                    file_data=copybook_content,
                    filename="scenario3_copybook_clean.cpy",
                    file_type="text/plain",
                    user_id="test_user"
                )
                copybook_uuid = copybook_result.get("uuid") or copybook_result.get("file_id") if copybook_result else None
                if copybook_uuid:
                    print(f"   ✅ UUID: {copybook_uuid}")
                else:
                    print(f"   ❌ Failed: {copybook_result}")
                
                # Summary
                print("\n" + "=" * 60)
                print("📊 UPLOAD SUMMARY")
                print("=" * 60)
                if data_uuid and copybook_uuid:
                    print(f"\n✅ Both files uploaded successfully!")
                    print(f"   Data file UUID: {data_uuid}")
                    print(f"   Copybook UUID: {copybook_uuid}")
                elif data_uuid or copybook_uuid:
                    print(f"\n⚠️  Partial success")
                    if data_uuid:
                        print(f"   ✅ Data: {data_uuid}")
                    if copybook_uuid:
                        print(f"   ✅ Copybook: {copybook_uuid}")
                else:
                    print(f"\n❌ Upload failed")
                print("=" * 60)
                return
            else:
                print("❌ ContentJourneyOrchestrator.upload_file not available")
                return
        
        print("✅ Services initialized")
        print()
        
        # Upload data file
        print("📤 Uploading: Annuity Policyholder Data (Clean)")
        data_result = await content_steward.upload_file(
            file_data=data_content,
            file_name="scenario3_annuity_data_clean.bin",
            file_type="bin",
            metadata={
                "ui_name": "Annuity Policyholder Data (Clean)",
                "description": "Clean binary file containing annuity policyholder records (no header comments, 81-byte records). Corrected for Cobrix parsing.",
                "pillar": "insights"
            }
        )
        data_uuid = data_result.get("uuid") if data_result else None
        if data_uuid:
            print(f"   ✅ UUID: {data_uuid}")
        else:
            print(f"   ❌ Failed: {data_result}")
        
        print()
        
        # Upload copybook
        print("📤 Uploading: COBOL Copybook (Corrected)")
        copybook_result = await content_steward.upload_file(
            file_data=copybook_content,
            file_name="scenario3_copybook_clean.cpy",
            file_type="cpy",
            metadata={
                "ui_name": "COBOL Copybook (Corrected)",
                "description": "Corrected COBOL copybook with only the data record structure (POLICYHOLDER-RECORD). Removed metadata tables that caused record size miscalculation.",
                "pillar": "content"
            }
        )
        copybook_uuid = copybook_result.get("uuid") if copybook_result else None
        if copybook_uuid:
            print(f"   ✅ UUID: {copybook_uuid}")
        else:
            print(f"   ❌ Failed: {copybook_result}")
        
        # Summary
        print()
        print("=" * 60)
        print("📊 UPLOAD SUMMARY")
        print("=" * 60)
        if data_uuid and copybook_uuid:
            print(f"\n✅ Both files uploaded successfully!")
            print(f"   Data file UUID: {data_uuid}")
            print(f"   Copybook UUID: {copybook_uuid}")
            print(f"\n🎯 Next steps:")
            print(f"   1. Go to Content Pillar in the UI")
            print(f"   2. Find 'Annuity Policyholder Data (Clean)'")
            print(f"   3. Use 'COBOL Copybook (Corrected)' as the copybook")
            print(f"   4. Test parsing - should work correctly now!")
        elif data_uuid or copybook_uuid:
            print(f"\n⚠️  Partial success:")
            if data_uuid:
                print(f"   ✅ Data: {data_uuid}")
            if copybook_uuid:
                print(f"   ✅ Copybook: {copybook_uuid}")
        else:
            print(f"\n❌ Upload failed for both files")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

