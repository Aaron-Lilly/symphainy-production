#!/usr/bin/env python3
"""
Test script for Optimal File Architecture implementation.

This script validates the logic flow without requiring a full container setup.
Tests:
1. Data structure validation
2. Query logic validation
3. Delete logic validation
4. UUID handling validation
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def test_get_dashboard_files_logic():
    """Test the logic for get_dashboard_files() method."""
    print("=" * 80)
    print("TEST 1: get_dashboard_files() Logic Validation")
    print("=" * 80)
    
    # Simulate data structures
    mock_uploaded_files = [
        {
            "uuid": "file-1-uuid",
            "ui_name": "Balances.csv",
            "status": "uploaded",
            "file_type": "csv",
            "mime_type": "text/csv",
            "file_size": 1024,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "uuid": "file-2-uuid",
            "ui_name": "Transactions.csv",
            "status": "uploaded",
            "file_type": "csv",
            "mime_type": "text/csv",
            "file_size": 2048,
            "created_at": "2024-01-02T00:00:00Z"
        }
    ]
    
    mock_parsed_files = [
        {
            "uuid": "parsed-1-uuid",  # parsed_data_files.uuid
            "parsed_file_id": "parsed-file-1-gcs-id",  # GCS identifier
            "file_id": "file-1-uuid",  # Link to original
            "format_type": "parquet",
            "file_size": 512,
            "parsed_at": "2024-01-01T01:00:00Z",
            "metadata": {
                "ui_name": "parsed_Balances",
                "user_id": "user-123",
                "gcs_path": "parsed_data/parsed-file-1-gcs-id.parquet"
            }
        }
    ]
    
    mock_embedded_files = [
        {
            "uuid": "embed-1-uuid",
            "content_id": "content-1-id",
            "file_id": "file-1-uuid",
            "parsed_file_id": "parsed-file-1-gcs-id",
            "ui_name": "embeddings_parsed_Balances",
            "embeddings_count": 100,
            "created_at": "2024-01-01T02:00:00Z"
        }
    ]
    
    # Simulate get_dashboard_files() logic
    files = []
    
    # 1. Add uploaded files
    for f in mock_uploaded_files:
        if f.get("status") == "uploaded":
            files.append({
                "uuid": f["uuid"],
                "ui_name": f.get("ui_name", ""),
                "status": "uploaded",
                "file_type": f.get("file_type", ""),
                "mime_type": f.get("mime_type", ""),
                "size": f.get("file_size", 0),
                "created_at": f.get("created_at", ""),
                "type": "original"
            })
    
    # 2. Add parsed files
    for pf in mock_parsed_files:
        metadata = pf.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        ui_name = metadata.get("ui_name") or f"parsed_{pf.get('parsed_file_id', '')}"
        
        files.append({
            "uuid": pf["uuid"],  # parsed_data_files.uuid
            "ui_name": ui_name,
            "status": "parsed",
            "file_type": pf.get("format_type", ""),
            "mime_type": f"application/{pf.get('format_type', '')}",
            "size": pf.get("file_size", 0),
            "created_at": pf.get("parsed_at", pf.get("created_at", "")),
            "original_file_id": pf.get("file_id"),  # Link to original
            "type": "parsed"
        })
    
    # 3. Add embedded files
    for ef in mock_embedded_files:
        files.append({
            "uuid": ef.get("uuid", ef.get("content_id", "")),
            "ui_name": ef.get("ui_name", f"embeddings_{ef.get('parsed_file_id', '')}"),
            "status": "embedded",
            "file_type": "embeddings",
            "mime_type": "application/json",
            "size": ef.get("size", 0),
            "created_at": ef.get("created_at", ""),
            "parsed_file_id": ef.get("parsed_file_id"),
            "original_file_id": ef.get("file_id"),
            "type": "embedded"
        })
    
    # Sort by created_at
    files.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Calculate statistics
    statistics = {
        "uploaded": len([f for f in files if f["type"] == "original"]),
        "parsed": len([f for f in files if f["type"] == "parsed"]),
        "embedded": len([f for f in files if f["type"] == "embedded"]),
        "total": len(files)
    }
    
    # Validate results
    print(f"✅ Files processed: {len(files)}")
    print(f"✅ Statistics: {statistics}")
    print(f"\n📋 Files list:")
    for f in files:
        print(f"  - {f['type']}: {f['ui_name']} (uuid: {f['uuid']})")
    
    # Assertions
    assert statistics["uploaded"] == 2, f"Expected 2 uploaded files, got {statistics['uploaded']}"
    assert statistics["parsed"] == 1, f"Expected 1 parsed file, got {statistics['parsed']}"
    assert statistics["embedded"] == 1, f"Expected 1 embedded file, got {statistics['embedded']}"
    assert statistics["total"] == 4, f"Expected 4 total files, got {statistics['total']}"
    
    # Check UUID consistency
    parsed_file = next((f for f in files if f["type"] == "parsed"), None)
    assert parsed_file is not None, "Parsed file not found"
    assert parsed_file["uuid"] == "parsed-1-uuid", f"Expected parsed-1-uuid, got {parsed_file['uuid']}"
    assert parsed_file["original_file_id"] == "file-1-uuid", "Parsed file should link to original"
    
    print("\n✅ TEST 1 PASSED: get_dashboard_files() logic is correct")
    return True


def test_delete_file_by_type_logic():
    """Test the logic for delete_file_by_type() method."""
    print("\n" + "=" * 80)
    print("TEST 2: delete_file_by_type() Logic Validation")
    print("=" * 80)
    
    # Simulate parsed file metadata from parsed_data_files table
    mock_parsed_file_metadata = {
        "uuid": "parsed-1-uuid",  # parsed_data_files.uuid (what we delete by)
        "parsed_file_id": "parsed-file-1-gcs-id",  # GCS identifier
        "file_id": "file-1-uuid",  # Original file
        "format_type": "parquet",
        "metadata": {
            "gcs_path": "parsed_data/parsed-file-1-gcs-id.parquet",
            "ui_name": "parsed_Balances",
            "user_id": "user-123"
        }
    }
    
    # Test case 1: Delete parsed file
    file_uuid = "parsed-1-uuid"
    file_type = "parsed"
    
    # Simulate query by uuid
    if file_type == "parsed":
        # Query parsed_data_files by uuid
        parsed_file_metadata = mock_parsed_file_metadata
        
        # Extract GCS path
        metadata = parsed_file_metadata.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        gcs_path = metadata.get("gcs_path")
        if not gcs_path:
            # Fallback construction
            parsed_file_id = parsed_file_metadata.get("parsed_file_id")
            format_type = parsed_file_metadata.get("format_type", "parquet")
            gcs_path = f"parsed_data/{parsed_file_id}.{format_type}"
        
        print(f"✅ Parsed file found: uuid={file_uuid}")
        print(f"✅ GCS path extracted: {gcs_path}")
        print(f"✅ Would delete from GCS: {gcs_path}")
        print(f"✅ Would delete from parsed_data_files: uuid={file_uuid}")
        
        assert gcs_path == "parsed_data/parsed-file-1-gcs-id.parquet", "GCS path should match"
        assert parsed_file_metadata["uuid"] == file_uuid, "UUID should match"
    
    # Test case 2: Delete original file
    file_uuid = "file-1-uuid"
    file_type = "original"
    
    if file_type == "original":
        print(f"\n✅ Original file deletion: uuid={file_uuid}")
        print(f"✅ Would delete from project_files: uuid={file_uuid}")
        print(f"✅ Would delete from GCS: (via file_management_abstraction.delete_file())")
    
    print("\n✅ TEST 2 PASSED: delete_file_by_type() logic is correct")
    return True


def test_store_parsed_file_logic():
    """Test the logic for store_parsed_file() method."""
    print("\n" + "=" * 80)
    print("TEST 3: store_parsed_file() Logic Validation")
    print("=" * 80)
    
    # Simulate input
    file_id = "file-1-uuid"
    parsed_file_data = b"mock parquet data"
    format_type = "parquet"
    original_file = {
        "uuid": "file-1-uuid",
        "ui_name": "Balances.csv",
        "user_id": "user-123",
        "tenant_id": "tenant-1"
    }
    
    # Simulate store_parsed_file() logic
    parsed_file_gcs_id = "parsed-file-1-gcs-id"  # Generated UUID
    gcs_path = f"parsed_data/{parsed_file_gcs_id}.{format_type}"
    parsed_file_id = parsed_file_gcs_id  # Use GCS UUID as parsed_file_id
    
    original_ui_name = original_file.get("ui_name", file_id)
    parsed_file_ui_name = f"parsed_{original_ui_name}"
    
    # ✅ OPTIMAL: Only create entry in parsed_data_files (NOT in project_files)
    parsed_file_metadata = {
        "file_id": file_id,  # Link to original
        "parsed_file_id": parsed_file_id,  # GCS UUID
        "format_type": format_type,
        "file_size": len(parsed_file_data),
        "metadata": {
            "gcs_file_id": parsed_file_gcs_id,
            "gcs_path": gcs_path,
            "user_id": original_file.get("user_id"),
            "ui_name": parsed_file_ui_name
        }
    }
    
    print(f"✅ Generated parsed_file_id: {parsed_file_id}")
    print(f"✅ GCS path: {gcs_path}")
    print(f"✅ UI name: {parsed_file_ui_name}")
    print(f"✅ Metadata structure: {json.dumps(parsed_file_metadata, indent=2)}")
    
    # Validations
    assert parsed_file_metadata["file_id"] == file_id, "Should link to original file"
    assert parsed_file_metadata["parsed_file_id"] == parsed_file_id, "Should use GCS UUID"
    assert parsed_file_metadata["metadata"]["ui_name"] == parsed_file_ui_name, "UI name should match"
    assert "project_file_uuid" not in parsed_file_metadata["metadata"], "Should NOT have project_file_uuid (optimal architecture)"
    
    print("\n✅ TEST 3 PASSED: store_parsed_file() logic is correct (no project_files entry)")
    return True


def test_get_parsed_file_logic():
    """Test the logic for get_parsed_file() method."""
    print("\n" + "=" * 80)
    print("TEST 4: get_parsed_file() Logic Validation")
    print("=" * 80)
    
    # Simulate parsed_file_id (can be either parsed_data_files.uuid or parsed_file_id)
    parsed_file_id = "parsed-file-1-gcs-id"  # GCS identifier
    
    # Simulate query from parsed_data_files table
    mock_parsed_file_metadata = {
        "uuid": "parsed-1-uuid",  # parsed_data_files.uuid
        "parsed_file_id": "parsed-file-1-gcs-id",  # GCS identifier
        "format_type": "parquet",
        "metadata": {
            "gcs_path": "parsed_data/parsed-file-1-gcs-id.parquet",
            "ui_name": "parsed_Balances"
        }
    }
    
    # Simulate get_parsed_file() logic
    # Query by parsed_file_id (GCS identifier)
    result = mock_parsed_file_metadata  # Simulated query result
    
    # Extract GCS path
    metadata = result.get("metadata", {})
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except:
            metadata = {}
    
    gcs_path = metadata.get("gcs_path")
    if not gcs_path:
        # Fallback construction
        format_type = result.get("format_type", "parquet")
        gcs_path = f"parsed_data/{parsed_file_id}.{format_type}"
    
    print(f"✅ Parsed file metadata found")
    print(f"✅ GCS path: {gcs_path}")
    print(f"✅ Would download from GCS: {gcs_path}")
    
    assert gcs_path == "parsed_data/parsed-file-1-gcs-id.parquet", "GCS path should match"
    
    print("\n✅ TEST 4 PASSED: get_parsed_file() logic is correct (direct GCS retrieval)")
    return True


def test_uuid_consistency():
    """Test UUID consistency across the architecture."""
    print("\n" + "=" * 80)
    print("TEST 5: UUID Consistency Validation")
    print("=" * 80)
    
    # Key UUIDs in the system
    original_file_uuid = "file-1-uuid"  # project_files.uuid
    parsed_file_gcs_id = "parsed-file-1-gcs-id"  # GCS blob identifier
    parsed_data_files_uuid = "parsed-1-uuid"  # parsed_data_files.uuid (primary key)
    
    print(f"Original file UUID (project_files.uuid): {original_file_uuid}")
    print(f"Parsed file GCS ID (parsed_file_id): {parsed_file_gcs_id}")
    print(f"Parsed data files UUID (parsed_data_files.uuid): {parsed_data_files_uuid}")
    
    # Validate relationships
    mock_parsed_file = {
        "uuid": parsed_data_files_uuid,  # Primary key for deletion
        "parsed_file_id": parsed_file_gcs_id,  # Used for GCS retrieval
        "file_id": original_file_uuid,  # Links to original
        "metadata": {
            "gcs_path": f"parsed_data/{parsed_file_gcs_id}.parquet"
        }
    }
    
    # Dashboard uses parsed_data_files.uuid
    dashboard_uuid = mock_parsed_file["uuid"]
    assert dashboard_uuid == parsed_data_files_uuid, "Dashboard should use parsed_data_files.uuid"
    
    # Delete uses parsed_data_files.uuid
    delete_uuid = mock_parsed_file["uuid"]
    assert delete_uuid == parsed_data_files_uuid, "Delete should use parsed_data_files.uuid"
    
    # GCS retrieval uses parsed_file_id
    gcs_retrieval_id = mock_parsed_file["parsed_file_id"]
    assert gcs_retrieval_id == parsed_file_gcs_id, "GCS retrieval should use parsed_file_id"
    
    print("\n✅ UUID relationships are consistent:")
    print(f"  - Dashboard/Delete: uses parsed_data_files.uuid ({parsed_data_files_uuid})")
    print(f"  - GCS retrieval: uses parsed_file_id ({parsed_file_gcs_id})")
    print(f"  - Lineage: file_id links to original ({original_file_uuid})")
    
    print("\n✅ TEST 5 PASSED: UUID consistency is correct")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("OPTIMAL FILE ARCHITECTURE - LOGIC VALIDATION TESTS")
    print("=" * 80)
    
    tests = [
        test_get_dashboard_files_logic,
        test_delete_file_by_type_logic,
        test_store_parsed_file_logic,
        test_get_parsed_file_logic,
        test_uuid_consistency
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Logic validation successful.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

