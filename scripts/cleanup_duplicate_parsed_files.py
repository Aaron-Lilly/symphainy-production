#!/usr/bin/env python3
"""
Cleanup Script for Duplicate Parsed Files

This script identifies and removes duplicate/orphaned entries in:
- project_files (parsed files without corresponding parsed_data_files entries)
- parsed_data_files (entries without corresponding project_files entries)

Run from project root: python3 scripts/cleanup_duplicate_parsed_files.py
"""

import sys
import os
import json
from typing import List, Dict, Any
from pathlib import Path
from supabase import create_client, Client

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
symphainy_platform = project_root / "symphainy-platform"
sys.path.insert(0, str(symphainy_platform))
os.chdir(str(symphainy_platform))

# Import config system
try:
    from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
    from config.environment_loader import EnvironmentLoader
    
    # Initialize config system
    config_manager = UnifiedConfigurationManager()
    env_loader = EnvironmentLoader()
    
    # Get Supabase credentials from config
    # Use config_manager.get() which handles secrets from .env.secrets
    SUPABASE_URL = config_manager.get("SUPABASE_URL")
    # Try multiple key names for service key
    SUPABASE_SERVICE_KEY = (
        config_manager.get("SUPABASE_SERVICE_KEY") or 
        config_manager.get("SUPABASE_SECRET_KEY") or
        config_manager.get("SUPABASE_KEY")  # Fallback to anon key if service key not found
    )
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("Could not load Supabase credentials from config")
        
except Exception as e:
    print(f"⚠️  Could not load from config system: {e}")
    print("   Falling back to environment variables")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be available via config or environment")
        sys.exit(1)


async def cleanup_duplicate_parsed_files():
    """Clean up duplicate and orphaned parsed file entries."""
    print("🔍 Starting cleanup of duplicate parsed files...\n")
    
    # Initialize Supabase client directly
    client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Step 1: Get all parsed files from project_files
    print("📊 Step 1: Analyzing project_files table...")
    project_files_result = client.table("project_files").select("*").eq("status", "parsed").eq("deleted", False).execute()
    parsed_project_files = project_files_result.data if project_files_result.data else []
    print(f"   Found {len(parsed_project_files)} parsed files in project_files\n")
    
    # Step 2: Get all entries from parsed_data_files
    print("📊 Step 2: Analyzing parsed_data_files table...")
    parsed_data_files_result = client.table("parsed_data_files").select("*").execute()
    parsed_data_files = parsed_data_files_result.data if parsed_data_files_result.data else []
    print(f"   Found {len(parsed_data_files)} entries in parsed_data_files\n")
    
    # Step 3: Build lookup maps
    print("📊 Step 3: Building lookup maps...")
    
    # Map: project_file_uuid -> parsed_data_files entry
    parsed_data_by_project_uuid = {}
    for pdf in parsed_data_files:
        metadata = pdf.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        project_file_uuid = metadata.get("project_file_uuid")
        if project_file_uuid:
            parsed_data_by_project_uuid[project_file_uuid] = pdf
    
    # Map: parsed_file_id -> parsed_data_files entry
    parsed_data_by_parsed_file_id = {}
    for pdf in parsed_data_files:
        parsed_file_id = pdf.get("parsed_file_id")
        if parsed_file_id:
            parsed_data_by_parsed_file_id[parsed_file_id] = pdf
    
    print(f"   Mapped {len(parsed_data_by_project_uuid)} parsed_data_files by project_file_uuid")
    print(f"   Mapped {len(parsed_data_by_parsed_file_id)} parsed_data_files by parsed_file_id\n")
    
    # Step 4: Identify orphaned entries in project_files
    print("🔍 Step 4: Identifying orphaned parsed files in project_files...")
    orphaned_project_files = []
    for pf in parsed_project_files:
        pf_uuid = pf.get("uuid")
        if pf_uuid not in parsed_data_by_project_uuid:
            orphaned_project_files.append(pf)
            print(f"   ⚠️  Orphaned: {pf.get('ui_name')} (uuid: {pf_uuid})")
    
    print(f"\n   Found {len(orphaned_project_files)} orphaned parsed files in project_files\n")
    
    # Step 5: Identify orphaned entries in parsed_data_files
    print("🔍 Step 5: Identifying orphaned entries in parsed_data_files...")
    orphaned_parsed_data = []
    for pdf in parsed_data_files:
        metadata = pdf.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        project_file_uuid = metadata.get("project_file_uuid")
        
        if project_file_uuid:
            # Check if corresponding project_files entry exists
            pf_result = client.table("project_files").select("uuid").eq("uuid", project_file_uuid).eq("deleted", False).execute()
            if not pf_result.data or len(pf_result.data) == 0:
                orphaned_parsed_data.append(pdf)
                print(f"   ⚠️  Orphaned: parsed_file_id={pdf.get('parsed_file_id')} (no project_files entry for uuid: {project_file_uuid})")
        else:
            # No project_file_uuid in metadata - this is an old entry
            orphaned_parsed_data.append(pdf)
            print(f"   ⚠️  Orphaned: parsed_file_id={pdf.get('parsed_file_id')} (no project_file_uuid in metadata)")
    
    print(f"\n   Found {len(orphaned_parsed_data)} orphaned entries in parsed_data_files\n")
    
    # Step 6: Ask for confirmation
    total_to_delete = len(orphaned_project_files) + len(orphaned_parsed_data)
    if total_to_delete == 0:
        print("✅ No orphaned entries found! Database is clean.\n")
        return
    
    print(f"⚠️  WARNING: About to delete {total_to_delete} orphaned entries:")
    print(f"   - {len(orphaned_project_files)} from project_files")
    print(f"   - {len(orphaned_parsed_data)} from parsed_data_files")
    print("\n   This action cannot be undone!")
    
    response = input("\n   Continue? (yes/no): ").strip().lower()
    if response != "yes":
        print("❌ Cleanup cancelled.\n")
        return
    
    # Step 7: Delete orphaned entries
    print("\n🗑️  Step 7: Deleting orphaned entries...")
    
    deleted_count = 0
    
    # Delete orphaned project_files
    for pf in orphaned_project_files:
        pf_uuid = pf.get("uuid")
        try:
            # Soft delete
            client.table("project_files").update({"deleted": True}).eq("uuid", pf_uuid).execute()
            print(f"   ✅ Deleted from project_files: {pf.get('ui_name')} (uuid: {pf_uuid})")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Failed to delete {pf_uuid}: {e}")
    
    # Delete orphaned parsed_data_files
    for pdf in orphaned_parsed_data:
        pdf_uuid = pdf.get("uuid")
        try:
            client.table("parsed_data_files").delete().eq("uuid", pdf_uuid).execute()
            print(f"   ✅ Deleted from parsed_data_files: parsed_file_id={pdf.get('parsed_file_id')} (uuid: {pdf_uuid})")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Failed to delete {pdf_uuid}: {e}")
    
    print(f"\n✅ Cleanup complete! Deleted {deleted_count} orphaned entries.\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(cleanup_duplicate_parsed_files())

