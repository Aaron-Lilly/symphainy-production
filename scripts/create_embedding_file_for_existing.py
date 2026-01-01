#!/usr/bin/env python3
"""
Quick script to create embedding_file record for existing embeddings.

This script:
1. Queries ArangoDB for existing embeddings
2. Groups them to understand the structure
3. Creates a single embedding_file record
4. Updates all embeddings with embedding_file_id

Run this to test the approach with your actual data.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Add platform root to path for imports
platform_root = os.path.abspath(os.path.join(project_root, 'symphainy-platform'))
sys.path.insert(0, platform_root)

# Load environment variables from .env.secrets
try:
    from dotenv import load_dotenv
    # Try loading from symphainy-platform/.env.secrets first
    secrets_file = Path(platform_root) / ".env.secrets"
    if secrets_file.exists():
        load_dotenv(secrets_file, override=False)
        print(f"✅ Loaded .env.secrets from: {secrets_file}")
    else:
        # Fallback to project root
        secrets_file = Path(project_root) / ".env.secrets"
        if secrets_file.exists():
            load_dotenv(secrets_file, override=False)
            print(f"✅ Loaded .env.secrets from: {secrets_file}")
except ImportError:
    print("⚠️ python-dotenv not available - using environment variables only")

from foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter


async def main():
    """Create embedding_file for existing embeddings."""
    print("🚀 Creating embedding_file record for existing embeddings...")
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY (or SUPABASE_SECRET_KEY) must be set")
        print(f"   SUPABASE_URL: {'✅' if supabase_url else '❌'}")
        print(f"   SUPABASE_SERVICE_KEY: {'✅' if supabase_key else '❌'}")
        return
    
    # Initialize Supabase adapter
    print(f"🔍 Initializing Supabase adapter...")
    print(f"   URL: {supabase_url[:50]}...")
    print(f"   Key: {supabase_key[:20]}...")
    supabase_adapter = SupabaseFileManagementAdapter(supabase_url, supabase_key)
    connected = await supabase_adapter.connect()
    if connected:
        print("✅ Connected to Supabase")
    else:
        print("⚠️ Supabase connection check failed, but continuing...")
    
    # Initialize ArangoDB adapter
    arango_url = os.getenv("ARANGO_URL") or os.getenv("ARANGODB_HOSTS", "http://localhost:8529")
    arango_db = os.getenv("ARANGO_DB") or os.getenv("ARANGODB_DATABASE", "symphainy_metadata")
    arango_user = os.getenv("ARANGO_USER") or os.getenv("ARANGODB_USERNAME", "root")
    arango_pass = os.getenv("ARANGO_PASS") or os.getenv("ARANGODB_PASSWORD", "")
    
    if not arango_url or not arango_db:
        print("❌ ARANGO_URL (or ARANGODB_HOSTS) and ARANGO_DB (or ARANGODB_DATABASE) must be set")
        return
    
    arango_adapter = ArangoDBAdapter(
        hosts=arango_url,
        database=arango_db,
        username=arango_user,
        password=arango_pass
    )
    
    # Connect to ArangoDB
    connected = await arango_adapter.connect(timeout=10.0)
    if not connected:
        print("❌ Failed to connect to ArangoDB")
        return
    print("✅ Connected to ArangoDB")
    
    # Get all embeddings from ArangoDB
    print("\n📋 Querying existing embeddings from ArangoDB...")
    try:
        embeddings = await arango_adapter.find_documents(
            collection="structured_embeddings",
            filter_conditions={},
            limit=None
        )
        print(f"📊 Found {len(embeddings)} embeddings")
    except Exception as e:
        print(f"❌ Failed to query embeddings: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if not embeddings:
        print("✅ No embeddings found - nothing to migrate")
        return
    
    # Analyze embeddings structure
    print("\n🔍 Analyzing embedding structure...")
    print(f"   First embedding keys: {list(embeddings[0].keys())}")
    
    # Group by file_id and parsed_file_id to understand structure
    file_id_groups = defaultdict(list)
    parsed_file_id_groups = defaultdict(list)
    
    for emb in embeddings:
        file_id = emb.get("file_id")
        parsed_file_id = emb.get("parsed_file_id")
        
        if file_id:
            file_id_groups[file_id].append(emb)
        if parsed_file_id:
            parsed_file_id_groups[parsed_file_id].append(emb)
    
    print(f"\n📦 Grouping results:")
    print(f"   Unique file_ids: {len(file_id_groups)}")
    print(f"   Unique parsed_file_ids: {len(parsed_file_id_groups)}")
    
    # Show all unique file_ids sorted by count (to find the one with 145)
    print(f"\n📋 All unique file_ids found (sorted by count):")
    sorted_file_ids = sorted(file_id_groups.items(), key=lambda x: len(x[1]), reverse=True)
    for file_id, emb_list in sorted_file_ids[:30]:  # Show top 30
        print(f"   {file_id}: {len(emb_list)} embeddings")
    if len(file_id_groups) > 30:
        print(f"   ... and {len(file_id_groups) - 30} more file_ids")
    
    # Find file_id with most embeddings (likely the one with 145)
    if sorted_file_ids:
        largest_file_id, largest_emb_list = sorted_file_ids[0]
        print(f"\n🎯 Largest group: {largest_file_id} with {len(largest_emb_list)} embeddings")
    
    # Show sample embedding structure
    sample = embeddings[0]
    print(f"\n📄 Sample embedding structure:")
    print(f"   _key: {sample.get('_key')}")
    print(f"   file_id: {sample.get('file_id')}")
    print(f"   parsed_file_id: {sample.get('parsed_file_id')}")
    print(f"   content_id: {sample.get('content_id')}")
    print(f"   column_name: {sample.get('column_name')}")
    print(f"   embedding_file_id: {sample.get('embedding_file_id')} (should be None if not yet set)")
    
    # Filter out test embeddings (file_ids starting with "test_")
    real_file_id_groups = {fid: emb_list for fid, emb_list in file_id_groups.items() if not fid.startswith("test_")}
    real_parsed_file_id_groups = {pid: emb_list for pid, emb_list in parsed_file_id_groups.items() if pid and not pid.startswith("test_")}
    
    print(f"\n🔍 Filtering out test data:")
    print(f"   Real file_ids: {len(real_file_id_groups)}")
    print(f"   Real parsed_file_ids: {len(real_parsed_file_id_groups)}")
    
    if not real_file_id_groups and not real_parsed_file_id_groups:
        print("\n⚠️ No real embeddings found (all appear to be test data)")
        print("   Showing all file_ids for review:")
        for file_id, emb_list in list(file_id_groups.items())[:10]:
            print(f"   - {file_id}: {len(emb_list)} embeddings")
        return
    
    # Determine which file_id/parsed_file_id to use
    # Use the file_id with the most embeddings (likely the one the user mentioned)
    if real_file_id_groups:
        # Sort by count and use the largest
        sorted_real = sorted(real_file_id_groups.items(), key=lambda x: len(x[1]), reverse=True)
        file_id, emb_list = sorted_real[0]
        print(f"\n✅ Using file_id with most embeddings: {file_id} ({len(emb_list)} embeddings)")
        parsed_file_id = emb_list[0].get("parsed_file_id")
        
        # Show sample from this file
        sample = emb_list[0]
        print(f"\n📄 Sample embedding from this file:")
        print(f"   _key: {sample.get('_key')}")
        print(f"   file_id: {sample.get('file_id')}")
        print(f"   parsed_file_id: {sample.get('parsed_file_id')}")
        print(f"   content_id: {sample.get('content_id')}")
        print(f"   column_name: {sample.get('column_name')}")
        print(f"   tenant_id: {sample.get('tenant_id')}")
        print(f"   created_at: {sample.get('created_at')}")
        
        # User mentioned it was created from "parsed_rates_by_age"
        # Let's search for parsed files that match this name
        print(f"\n🔍 Searching for parsed file 'parsed_rates_by_age'...")
        try:
            # Query parsed_data_files table to find parsed file with matching name pattern
            # We'll search by file_id first, then check metadata
            parsed_files_result = supabase_adapter.client.table("parsed_data_files").select("*").eq("file_id", file_id).execute()
            if parsed_files_result.data:
                for pf in parsed_files_result.data:
                    # Check if metadata or other fields contain "rates_by_age"
                    metadata = pf.get("metadata", {})
                    gcs_path = metadata.get("gcs_path", "")
                    if "rates_by_age" in str(pf).lower() or "rates_by_age" in gcs_path.lower():
                        parsed_file_id = pf.get("parsed_file_id")
                        user_id = pf.get("user_id")
                        print(f"   ✅ Found parsed file: {parsed_file_id}")
                        print(f"      user_id: {user_id}")
                        if parsed_file_id:
                            break
        except Exception as e:
            print(f"   ⚠️ Could not search parsed_data_files: {e}")
    elif real_parsed_file_id_groups:
        print(f"\n✅ Using real parsed_file_id grouping (more accurate)")
        parsed_file_id = list(real_parsed_file_id_groups.keys())[0]
        emb_list = real_parsed_file_id_groups[parsed_file_id]
        file_id = emb_list[0].get("file_id")
    elif parsed_file_id_groups:
        print(f"\n⚠️ Using parsed_file_id grouping (may be test data)")
        parsed_file_id = list(parsed_file_id_groups.keys())[0]
        emb_list = parsed_file_id_groups[parsed_file_id]
        file_id = emb_list[0].get("file_id")
    elif file_id_groups:
        print(f"\n⚠️ Using file_id grouping (may be test data)")
        file_id = list(file_id_groups.keys())[0]
        emb_list = file_id_groups[file_id]
        parsed_file_id = emb_list[0].get("parsed_file_id")
    else:
        print("❌ No file_id or parsed_file_id found in embeddings")
        return
    
    print(f"\n📋 Creating embedding_file record:")
    print(f"   file_id: {file_id}")
    print(f"   parsed_file_id: {parsed_file_id}")
    print(f"   embeddings_count: {len(emb_list)}")
    
    # Get file metadata to get ui_name and user_id
    print(f"\n🔍 Getting file metadata for file_id: {file_id}...")
    # First, try to find parsed_file_id from parsed_data_files table
    # User mentioned "parsed_rates_by_age" - let's search for it
    print(f"\n🔍 Searching parsed_data_files for 'rates_by_age' pattern...")
    parsed_file_metadata = None
    try:
        # Search by file_id first
        parsed_files_result = supabase_adapter.client.table("parsed_data_files").select("*").eq("file_id", file_id).execute()
        if parsed_files_result.data:
            for pf in parsed_files_result.data:
                # Check metadata for "rates_by_age" pattern
                metadata_str = str(pf).lower()
                if "rates_by_age" in metadata_str or "rates" in metadata_str:
                    parsed_file_metadata = pf
                    parsed_file_id = pf.get("parsed_file_id")
                    user_id = pf.get("user_id")
                    tenant_id = pf.get("tenant_id")
                    print(f"   ✅ Found parsed file matching 'rates_by_age':")
                    print(f"      parsed_file_id: {parsed_file_id}")
                    print(f"      user_id: {user_id}")
                    print(f"      tenant_id: {tenant_id}")
                    break
        
        # If not found, try searching all parsed files for the pattern
        if not parsed_file_metadata:
            print(f"   Searching all parsed files for 'rates_by_age'...")
            all_parsed = supabase_adapter.client.table("parsed_data_files").select("*").limit(100).execute()
            if all_parsed.data:
                for pf in all_parsed.data:
                    metadata_str = str(pf).lower()
                    if "rates_by_age" in metadata_str:
                        # Check if this parsed file's file_id matches our embeddings
                        pf_file_id = pf.get("file_id")
                        if pf_file_id == file_id:
                            parsed_file_metadata = pf
                            parsed_file_id = pf.get("parsed_file_id")
                            user_id = pf.get("user_id")
                            tenant_id = pf.get("tenant_id")
                            print(f"   ✅ Found matching parsed file:")
                            print(f"      parsed_file_id: {parsed_file_id}")
                            print(f"      user_id: {user_id}")
                            print(f"      file_id: {pf_file_id}")
                            break
    except Exception as e:
        print(f"   ⚠️ Could not search parsed_data_files: {e}")
    
    # Now try to get file metadata
    file_metadata = await supabase_adapter.get_file(file_id)
    
    # Use parsed_file_metadata if we found it, otherwise try file_metadata
    if parsed_file_metadata:
        # We already have user_id, tenant_id, parsed_file_id from above
        # Just need ui_name
        if not file_metadata:
            # Try to get original file name from parsed file's metadata or use fallback
            ui_name = f"rates_by_age"  # Based on user's info
        else:
            ui_name = file_metadata.get("ui_name", "rates_by_age")
    elif not file_metadata:
        print(f"⚠️ File {file_id} not found in project_files table")
        print(f"   Trying to find parsed_file_id from parsed_data_files table...")
        
        # Query parsed_data_files table to find parsed_file_id for this file_id
        try:
            parsed_files_result = supabase_adapter.client.table("parsed_data_files").select("*").eq("file_id", file_id).limit(1).execute()
            if parsed_files_result.data and len(parsed_files_result.data) > 0:
                parsed_file_metadata = parsed_files_result.data[0]
                parsed_file_id = parsed_file_metadata.get("parsed_file_id")
                user_id = parsed_file_metadata.get("user_id")
                tenant_id = parsed_file_metadata.get("tenant_id")
                print(f"   ✅ Found in parsed_data_files:")
                print(f"      parsed_file_id: {parsed_file_id}")
                print(f"      user_id: {user_id}")
                print(f"      tenant_id: {tenant_id}")
                
                # Try to get original file name from project_files using the file_id
                # If that fails, use a fallback name
                try:
                    original_file = await supabase_adapter.get_file(file_id)
                    if original_file:
                        ui_name = original_file.get("ui_name", f"file_{file_id[:8]}")
                    else:
                        ui_name = f"file_{file_id[:8]}"
                except:
                    ui_name = f"file_{file_id[:8]}"
            else:
                print(f"   ❌ File {file_id} not found in parsed_data_files either")
                print(f"   Using fallback: will create with minimal metadata")
                user_id = None
                tenant_id = None
                ui_name = f"file_{file_id[:8]}"
                parsed_file_id = parsed_file_id or f"unknown_{file_id[:8]}"
        except Exception as e:
            print(f"   ❌ Failed to query parsed_data_files: {e}")
            print(f"   Using fallback: will create with minimal metadata")
            user_id = None
            tenant_id = None
            ui_name = f"file_{file_id[:8]}"
            parsed_file_id = parsed_file_id or f"unknown_{file_id[:8]}"
    else:
        user_id = file_metadata.get("user_id")
        tenant_id = file_metadata.get("tenant_id")
        ui_name = file_metadata.get("ui_name", f"file_{file_id[:8]}")
        
        if not user_id:
            print(f"⚠️ File {file_id} has no user_id - will try to get from parsed_data_files")
            # Try parsed_data_files as fallback
            try:
                parsed_files_result = supabase_adapter.client.table("parsed_data_files").select("*").eq("file_id", file_id).limit(1).execute()
                if parsed_files_result.data and len(parsed_files_result.data) > 0:
                    parsed_file_metadata = parsed_files_result.data[0]
                    user_id = parsed_file_metadata.get("user_id") or user_id
                    tenant_id = parsed_file_metadata.get("tenant_id") or tenant_id
                    if not parsed_file_id:
                        parsed_file_id = parsed_file_metadata.get("parsed_file_id")
            except:
                pass
    
    # If we still don't have user_id, we need to get it from the backend or user
    # For now, let's try to query via ContentStewardService or check if we can infer it
        if not user_id:
            print(f"\n⚠️ Cannot determine user_id from Supabase (auth issue)")
            print(f"   File: {file_id}")
            print(f"   Embeddings: {len(emb_list)}")
            print(f"   Known: Created from 'parsed_rates_by_age'")
            print(f"\n   💡 Trying alternative methods...")
            
            # Try to query backend API
            import requests
            backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
            try:
                # Try to get file via backend API
                api_url = f"{backend_url}/api/v1/content-pillar/list-uploaded-files"
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    files_data = response.json()
                    if files_data.get("success") and files_data.get("files"):
                        # Find our file
                        for f in files_data.get("files", []):
                            if f.get("uuid") == file_id or f.get("file_id") == file_id:
                                user_id = f.get("user_id")
                                ui_name = f.get("ui_name", ui_name)
                                print(f"   ✅ Found file via backend API!")
                                print(f"      user_id: {user_id}")
                                print(f"      ui_name: {ui_name}")
                                break
            except Exception as api_error:
                print(f"   ⚠️ Backend API not available: {api_error}")
            
            # If still no user_id, try to get from environment variable or use a workaround
            if not user_id:
                # Check if user_id is in environment
                user_id = os.getenv("EMBEDDING_USER_ID")
                if user_id:
                    print(f"   ✅ Using user_id from EMBEDDING_USER_ID env var: {user_id}")
                else:
                    # Since we know it's from "parsed_rates_by_age", let's try to query parsed files
                    # using a different approach - maybe we can use the tenant_id from embeddings
                    print(f"   ⚠️ No user_id found. Since we know it's from 'parsed_rates_by_age',")
                    print(f"      we can try to find the parsed_file_id and user_id manually.")
                    print(f"\n   Please provide user_id via:")
                    print(f"   1. Set EMBEDDING_USER_ID environment variable")
                    print(f"   2. Or check Supabase for file_id: {file_id}")
                    print(f"   3. Or check parsed_data_files for 'rates_by_age'")
                    
                    # For now, let's proceed with what we have and see if we can create without user_id
                    # Actually, user_id is required by the schema, so we can't proceed
                    print(f"\n   ❌ Cannot proceed without user_id (required by schema)")
                    return
    
    print(f"\n📋 Final metadata:")
    print(f"   file_id: {file_id}")
    print(f"   parsed_file_id: {parsed_file_id or 'None (will use placeholder)'}")
    print(f"   user_id: {user_id}")
    print(f"   tenant_id: {tenant_id}")
    print(f"   ui_name: {ui_name}")
    print(f"   embeddings_count: {len(emb_list)}")
    
    # Check if embedding_file already exists
    print(f"\n🔍 Checking if embedding_file already exists...")
    existing_embedding_files = await supabase_adapter.list_embedding_files(
        user_id=user_id,
        parsed_file_id=parsed_file_id
    )
    
    if existing_embedding_files:
        print(f"⚠️ Embedding file already exists: {existing_embedding_files[0].get('uuid')}")
        embedding_file_id = existing_embedding_files[0].get("uuid")
        print(f"   Using existing embedding_file_id: {embedding_file_id}")
    else:
        # Create embedding_file record
        data_classification = "client" if tenant_id else "platform"
        
        embedding_file_data = {
            "file_id": file_id,
            "parsed_file_id": parsed_file_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "ui_name": f"Embeddings: {ui_name}",
            "content_id": emb_list[0].get("content_id"),
            "embeddings_count": len(emb_list),
            "embedding_type": "structured",
            "data_classification": data_classification,
            "status": "active",
            "processing_status": "completed",
            "created_by": "manual_script",
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "source": "create_embedding_file_for_existing.py"
            }
        }
        
        print(f"\n📝 Creating embedding_file record...")
        try:
            result = await supabase_adapter.create_embedding_file(embedding_file_data)
            embedding_file_id = result.get("uuid")
            
            if embedding_file_id:
                print(f"✅ Created embedding_file: {embedding_file_id}")
                print(f"   ui_name: {embedding_file_data['ui_name']}")
                print(f"   embeddings_count: {len(emb_list)}")
            else:
                print(f"❌ Failed to create embedding_file: no UUID returned")
                print(f"   Result: {result}")
                return
        except Exception as e:
            print(f"❌ Failed to create embedding_file: {e}")
            import traceback
            traceback.print_exc()
            return
    
    # Update all embeddings with embedding_file_id
    print(f"\n🔄 Updating {len(emb_list)} embeddings with embedding_file_id...")
    updated_count = 0
    failed_count = 0
    
    for emb in emb_list:
        embedding_key = emb.get("_key")
        if not embedding_key:
            print(f"⚠️ Embedding has no _key - skipping")
            failed_count += 1
            continue
        
        # Check if already has embedding_file_id
        if emb.get("embedding_file_id"):
            print(f"   ⚠️ Embedding {embedding_key} already has embedding_file_id: {emb.get('embedding_file_id')}")
            # Update anyway to ensure consistency
            # updated_count += 1
            # continue
        
        try:
            await arango_adapter.update_document(
                collection="structured_embeddings",
                key=embedding_key,
                document={"embedding_file_id": embedding_file_id}
            )
            updated_count += 1
            if updated_count % 10 == 0:
                print(f"   ✅ Updated {updated_count}/{len(emb_list)} embeddings...")
        except Exception as e:
            print(f"   ❌ Failed to update embedding {embedding_key}: {e}")
            failed_count += 1
    
    print(f"\n✅ Complete!")
    print(f"   Embedding file ID: {embedding_file_id}")
    print(f"   Updated {updated_count} embeddings")
    if failed_count > 0:
        print(f"   Failed {failed_count} updates")
    
    # Verify by querying back
    print(f"\n🔍 Verifying update...")
    try:
        updated_embeddings = await arango_adapter.find_documents(
            collection="structured_embeddings",
            filter_conditions={"embedding_file_id": embedding_file_id},
            limit=5
        )
        print(f"   ✅ Found {len(updated_embeddings)} embeddings with embedding_file_id={embedding_file_id}")
        if updated_embeddings:
            print(f"   Sample: {updated_embeddings[0].get('_key')} - column: {updated_embeddings[0].get('column_name')}")
    except Exception as e:
        print(f"   ⚠️ Verification query failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())

