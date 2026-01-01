#!/usr/bin/env python3
"""
Simple script to create embedding_file record for existing embeddings.
Accepts user_id and parsed_file_id as command-line arguments.

Usage:
    python3 scripts/create_embedding_file_simple.py --user_id <user_id> [--parsed_file_id <parsed_file_id>]
"""

import os
import sys
import asyncio
import argparse
from typing import Dict, Any, Optional
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
    secrets_file = Path(platform_root) / ".env.secrets"
    if secrets_file.exists():
        load_dotenv(secrets_file, override=False)
except ImportError:
    pass

from foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter


async def main():
    parser = argparse.ArgumentParser(description='Create embedding_file record for existing embeddings')
    parser.add_argument('--file_id', type=str, default='0eda1bad-c2c0-4177-bea1-67682a3759ca',
                       help='File ID for the embeddings (default: the one with 725 embeddings)')
    parser.add_argument('--user_id', type=str, required=True,
                       help='User ID (required)')
    parser.add_argument('--parsed_file_id', type=str, default=None,
                       help='Parsed file ID (optional, will use placeholder if not provided)')
    parser.add_argument('--ui_name', type=str, default='Embeddings: rates_by_age',
                       help='UI-friendly name (default: Embeddings: rates_by_age)')
    
    args = parser.parse_args()
    
    file_id = args.file_id
    user_id = args.user_id
    parsed_file_id = args.parsed_file_id
    ui_name = args.ui_name
    
    print("🚀 Creating embedding_file record for existing embeddings...")
    print(f"   file_id: {file_id}")
    print(f"   user_id: {user_id}")
    print(f"   parsed_file_id: {parsed_file_id or 'None (will use placeholder)'}")
    print(f"   ui_name: {ui_name}")
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        return
    
    # Initialize Supabase adapter
    supabase_adapter = SupabaseFileManagementAdapter(supabase_url, supabase_key)
    connected = await supabase_adapter.connect()
    if not connected:
        print("⚠️ Supabase connection check failed, but continuing...")
    else:
        print("✅ Connected to Supabase")
    
    # Initialize ArangoDB adapter
    arango_url = os.getenv("ARANGO_URL") or os.getenv("ARANGODB_HOSTS", "http://localhost:8529")
    arango_db = os.getenv("ARANGO_DB") or os.getenv("ARANGODB_DATABASE", "symphainy_metadata")
    arango_user = os.getenv("ARANGO_USER") or os.getenv("ARANGODB_USERNAME", "root")
    arango_pass = os.getenv("ARANGO_PASS") or os.getenv("ARANGODB_PASSWORD", "")
    
    if not arango_url or not arango_db:
        print("❌ ARANGO_URL and ARANGO_DB must be set")
        return
    
    arango_adapter = ArangoDBAdapter(
        hosts=arango_url,
        database=arango_db,
        username=arango_user,
        password=arango_pass
    )
    
    connected = await arango_adapter.connect(timeout=10.0)
    if not connected:
        print("❌ Failed to connect to ArangoDB")
        return
    print("✅ Connected to ArangoDB")
    
    # Get embeddings for this file_id
    print(f"\n📋 Querying embeddings for file_id: {file_id}...")
    try:
        embeddings = await arango_adapter.find_documents(
            collection="structured_embeddings",
            filter_conditions={"file_id": file_id},
            limit=None
        )
        print(f"📊 Found {len(embeddings)} embeddings")
    except Exception as e:
        print(f"❌ Failed to query embeddings: {e}")
        return
    
    if not embeddings:
        print("❌ No embeddings found for this file_id")
        return
    
    # Get tenant_id from first embedding
    tenant_id = embeddings[0].get("tenant_id")
    content_id = embeddings[0].get("content_id")
    
    # Use placeholder for parsed_file_id if not provided
    if not parsed_file_id:
        parsed_file_id = f"unknown_{file_id[:8]}"
        print(f"⚠️ Using placeholder parsed_file_id: {parsed_file_id}")
    
    # Check if embedding_file already exists
    print(f"\n🔍 Checking if embedding_file already exists...")
    try:
        existing_embedding_files = await supabase_adapter.list_embedding_files(
            user_id=user_id,
            file_id=file_id
        )
        
        if existing_embedding_files:
            existing = existing_embedding_files[0]
            embedding_file_id = existing.get("uuid")
            print(f"⚠️ Embedding file already exists: {embedding_file_id}")
            print(f"   ui_name: {existing.get('ui_name')}")
            print(f"   embeddings_count: {existing.get('embedding_count', 0)}")
            
            # Check if embeddings need updating
            print(f"\n🔄 Checking if embeddings need embedding_file_id update...")
            needs_update = 0
            for emb in embeddings[:10]:  # Check first 10
                if not emb.get("embedding_file_id"):
                    needs_update += 1
            
            if needs_update > 0:
                print(f"   Found {needs_update} embeddings (out of {len(embeddings)}) that need updating")
                update_all = input("   Update all embeddings with embedding_file_id? (y/n): ").lower() == 'y'
                if update_all:
                    updated_count = 0
                    for emb in embeddings:
                        embedding_key = emb.get("_key")
                        if embedding_key and not emb.get("embedding_file_id"):
                            try:
                                await arango_adapter.update_document(
                                    collection="structured_embeddings",
                                    key=embedding_key,
                                    document={"embedding_file_id": embedding_file_id}
                                )
                                updated_count += 1
                                if updated_count % 50 == 0:
                                    print(f"   ✅ Updated {updated_count}/{len(embeddings)} embeddings...")
                            except Exception as e:
                                print(f"   ❌ Failed to update embedding {embedding_key}: {e}")
                    print(f"   ✅ Updated {updated_count} embeddings")
        else:
            # Create new embedding_file record
            print(f"\n📝 Creating embedding_file record...")
            data_classification = "client" if tenant_id else "platform"
            
            embedding_file_data = {
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "ui_name": ui_name,
                "embedding_count": len(embeddings),
                "content_type": "structured",
                "status": "embedded",
                "metadata": {
                    "embedding_model": "unknown",
                    "embedding_dimensions": len(embeddings[0].get("metadata_embedding", [])) if embeddings else 0,
                    "content_id": content_id,
                    "created_by": "manual_script"
                }
            }
            
            try:
                result = await supabase_adapter.create_embedding_file(embedding_file_data)
                embedding_file_id = result.get("uuid")
                
                if embedding_file_id:
                    print(f"✅ Created embedding_file: {embedding_file_id}")
                    print(f"   ui_name: {ui_name}")
                    print(f"   embeddings_count: {len(embeddings)}")
                    
                    # Update all embeddings with embedding_file_id
                    print(f"\n🔄 Updating {len(embeddings)} embeddings with embedding_file_id...")
                    updated_count = 0
                    for emb in embeddings:
                        embedding_key = emb.get("_key")
                        if embedding_key:
                            try:
                                await arango_adapter.update_document(
                                    collection="structured_embeddings",
                                    key=embedding_key,
                                    document={"embedding_file_id": embedding_file_id}
                                )
                                updated_count += 1
                                if updated_count % 50 == 0:
                                    print(f"   ✅ Updated {updated_count}/{len(embeddings)} embeddings...")
                            except Exception as e:
                                print(f"   ❌ Failed to update embedding {embedding_key}: {e}")
                    
                    print(f"\n✅ Complete!")
                    print(f"   Embedding file ID: {embedding_file_id}")
                    print(f"   Updated {updated_count} embeddings")
                else:
                    print(f"❌ Failed to create embedding_file: no UUID returned")
                    print(f"   Result: {result}")
            except Exception as e:
                print(f"❌ Failed to create embedding_file: {e}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())




