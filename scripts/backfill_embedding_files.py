#!/usr/bin/env python3
"""
Migration Script: Backfill embedding_files table from existing embeddings

This script:
1. Queries ArangoDB for all existing embeddings
2. Groups them by parsed_file_id (preferred) or file_id (fallback)
3. Creates embedding_file records in Supabase for each group
4. Updates embedding documents in ArangoDB with embedding_file_id

Run this after deploying the embedding_files table schema.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from collections import defaultdict
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter


async def get_all_embeddings(arango_adapter: ArangoDBAdapter) -> List[Dict[str, Any]]:
    """Get all embeddings from ArangoDB."""
    try:
        result = await arango_adapter.find_documents(
            collection="structured_embeddings",
            filter_conditions={},
            limit=None  # Get all
        )
        return result if result else []
    except Exception as e:
        print(f"❌ Failed to get embeddings from ArangoDB: {e}")
        return []


async def get_file_metadata(supabase_adapter: SupabaseFileManagementAdapter, file_id: str) -> Optional[Dict[str, Any]]:
    """Get file metadata from Supabase."""
    try:
        return await supabase_adapter.get_file(file_id)
    except Exception as e:
        print(f"⚠️ Failed to get file {file_id}: {e}")
        return None


async def create_embedding_file_record(
    supabase_adapter: SupabaseFileManagementAdapter,
    file_id: str,
    parsed_file_id: str,
    user_id: str,
    tenant_id: Optional[str],
    ui_name: str,
    embeddings_count: int,
    content_id: Optional[str] = None
) -> Optional[str]:
    """Create an embedding_file record in Supabase."""
    try:
        data_classification = "client" if tenant_id else "platform"
        
        embedding_file_data = {
            "file_id": file_id,
            "parsed_file_id": parsed_file_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "ui_name": ui_name,
            "content_id": content_id,
            "embeddings_count": embeddings_count,
            "embedding_type": "structured",  # Default, can be enhanced later
            "data_classification": data_classification,
            "status": "active",
            "processing_status": "completed",
            "created_by": "migration_script",
            "metadata": {
                "migrated_at": datetime.utcnow().isoformat(),
                "migration_source": "backfill_embedding_files.py"
            }
        }
        
        result = await supabase_adapter.create_embedding_file(embedding_file_data)
        embedding_file_id = result.get("uuid")
        
        if embedding_file_id:
            print(f"✅ Created embedding_file: {embedding_file_id} ({ui_name}) - {embeddings_count} embeddings")
            return embedding_file_id
        else:
            print(f"❌ Failed to create embedding_file: no UUID returned")
            return None
            
    except Exception as e:
        print(f"❌ Failed to create embedding_file record: {e}")
        return None


async def update_embedding_with_file_id(
    arango_adapter: ArangoDBAdapter,
    embedding_key: str,
    embedding_file_id: str
) -> bool:
    """Update an embedding document with embedding_file_id."""
    try:
        # Update the document directly (ArangoDBAdapter.update_document takes key and document dict)
        await arango_adapter.update_document(
            collection="structured_embeddings",
            key=embedding_key,
            document={"embedding_file_id": embedding_file_id}
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update embedding {embedding_key}: {e}")
        return False


async def backfill_embedding_files():
    """Main migration function."""
    print("🚀 Starting embedding_files backfill migration...")
    
    # Initialize adapters
    # Note: These should be initialized from environment variables
    # For now, we'll assume they're available via DI container or direct initialization
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        return
    
    # Initialize Supabase adapter
    supabase_adapter = SupabaseFileManagementAdapter(supabase_url, supabase_key)
    await supabase_adapter.connect()
    print("✅ Connected to Supabase")
    
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
    print("📋 Querying all embeddings from ArangoDB...")
    embeddings = await get_all_embeddings(arango_adapter)
    print(f"📊 Found {len(embeddings)} embeddings to migrate")
    
    # Group embeddings by parsed_file_id (preferred) or file_id (fallback)
    groups = defaultdict(list)
    for emb in embeddings:
        parsed_file_id = emb.get("parsed_file_id")
        file_id = emb.get("file_id")
        
        if parsed_file_id:
            groups[("parsed_file_id", parsed_file_id)].append(emb)
        elif file_id:
            groups[("file_id", file_id)].append(emb)
        else:
            print(f"⚠️ Embedding {emb.get('_key')} has no parsed_file_id or file_id - skipping")
    
    print(f"📦 Grouped into {len(groups)} embedding file groups")
    
    # Process each group
    created_count = 0
    updated_count = 0
    
    for (group_type, group_id), emb_list in groups.items():
        # Get file metadata
        file_id = emb_list[0].get("file_id")
        # If grouped by parsed_file_id, use group_id; otherwise try to get from embeddings
        if group_type == "parsed_file_id":
            parsed_file_id = group_id
        else:
            # Grouped by file_id - try to get parsed_file_id from embeddings
            parsed_file_id = emb_list[0].get("parsed_file_id")
        
        if not file_id:
            print(f"⚠️ Group {group_id} has no file_id - skipping")
            continue
        
        file_metadata = await get_file_metadata(supabase_adapter, file_id)
        if not file_metadata:
            print(f"⚠️ File {file_id} not found - skipping group {group_id}")
            continue
        
        user_id = file_metadata.get("user_id")
        tenant_id = file_metadata.get("tenant_id")
        ui_name = file_metadata.get("ui_name", f"file_{file_id[:8]}")
        
        if not user_id:
            print(f"⚠️ File {file_id} has no user_id - skipping")
            continue
        
        # Create embedding_file record
        embedding_file_id = await create_embedding_file_record(
            supabase_adapter=supabase_adapter,
            file_id=file_id,
            parsed_file_id=parsed_file_id,
            user_id=user_id,
            tenant_id=tenant_id,
            ui_name=f"Embeddings: {ui_name}",
            embeddings_count=len(emb_list),
            content_id=emb_list[0].get("content_id")
        )
        
        if embedding_file_id:
            created_count += 1
            
            # Update all embeddings in group
            for emb in emb_list:
                embedding_key = emb.get("_key")
                if embedding_key:
                    if await update_embedding_with_file_id(arango_adapter, embedding_key, embedding_file_id):
                        updated_count += 1
    
    if not embeddings:
        print("✅ No embeddings to migrate - exiting")
        return
    
    # Group embeddings by parsed_file_id (preferred) or file_id (fallback)
    groups = defaultdict(list)
    for emb in embeddings:
        parsed_file_id = emb.get("parsed_file_id")
        file_id = emb.get("file_id")
        
        if parsed_file_id:
            groups[("parsed_file_id", parsed_file_id)].append(emb)
        elif file_id:
            groups[("file_id", file_id)].append(emb)
        else:
            print(f"⚠️ Embedding {emb.get('_key')} has no parsed_file_id or file_id - skipping")
    
    print(f"📦 Grouped into {len(groups)} embedding file groups")
    
    # Process each group
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for (group_type, group_id), emb_list in groups.items():
        # Get file metadata
        file_id = emb_list[0].get("file_id")
        parsed_file_id = emb_list[0].get("parsed_file_id") or (group_id if group_type == "file_id" else None)
        
        if not file_id:
            print(f"⚠️ Group {group_id} has no file_id - skipping")
            skipped_count += 1
            continue
        
        # If we matched by file_id but don't have parsed_file_id, try to find it
        if not parsed_file_id and group_type == "file_id":
            # Try to get parsed_file_id from any embedding in the group
            for emb in emb_list:
                if emb.get("parsed_file_id"):
                    parsed_file_id = emb.get("parsed_file_id")
                    break
        
        file_metadata = await get_file_metadata(supabase_adapter, file_id)
        if not file_metadata:
            print(f"⚠️ File {file_id} not found - skipping group {group_id}")
            skipped_count += 1
            continue
        
        user_id = file_metadata.get("user_id")
        tenant_id = file_metadata.get("tenant_id")
        ui_name = file_metadata.get("ui_name", f"file_{file_id[:8]}")
        
        if not user_id:
            print(f"⚠️ File {file_id} has no user_id - skipping")
            skipped_count += 1
            continue
        
        # If we still don't have parsed_file_id, we'll use a placeholder
        # This shouldn't happen often, but we need to handle it
        if not parsed_file_id:
            parsed_file_id = f"unknown_{file_id[:8]}"
            print(f"⚠️ No parsed_file_id for group {group_id}, using placeholder: {parsed_file_id}")
        
        # Create embedding_file record
        embedding_file_id = await create_embedding_file_record(
            supabase_adapter=supabase_adapter,
            file_id=file_id,
            parsed_file_id=parsed_file_id,
            user_id=user_id,
            tenant_id=tenant_id,
            ui_name=f"Embeddings: {ui_name}",
            embeddings_count=len(emb_list),
            content_id=emb_list[0].get("content_id")
        )
        
        if embedding_file_id:
            created_count += 1
            
            # Update all embeddings in group
            for emb in emb_list:
                embedding_key = emb.get("_key")
                if embedding_key:
                    if await update_embedding_with_file_id(arango_adapter, embedding_key, embedding_file_id):
                        updated_count += 1
                else:
                    print(f"⚠️ Embedding has no _key - skipping update")
        else:
            skipped_count += 1
    
    print(f"\n✅ Migration complete!")
    print(f"   Created {created_count} embedding_file records")
    print(f"   Updated {updated_count} embedding documents")
    print(f"   Skipped {skipped_count} groups")


if __name__ == "__main__":
    asyncio.run(backfill_embedding_files())

