#!/usr/bin/env python3
"""
Delete embeddings from ArangoDB for a specific file_id.

This allows you to recreate embeddings with the new flow that automatically
creates embedding_file records.

Usage:
    python3 scripts/delete_embeddings_for_file.py --file_id <file_id> [--confirm]
"""

import os
import sys
import asyncio
import argparse
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

from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter


async def main():
    parser = argparse.ArgumentParser(description='Delete embeddings from ArangoDB for a file_id')
    parser.add_argument('--file_id', type=str, default='0eda1bad-c2c0-4177-bea1-67682a3759ca',
                       help='File ID to delete embeddings for (default: the one with 725 embeddings)')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompt (use with caution)')
    
    args = parser.parse_args()
    
    file_id = args.file_id
    
    print("🗑️  Deleting embeddings from ArangoDB...")
    print(f"   file_id: {file_id}")
    
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
    
    # Query embeddings for this file_id
    print(f"\n📋 Querying embeddings for file_id: {file_id}...")
    try:
        embeddings = await arango_adapter.find_documents(
            collection="structured_embeddings",
            filter_conditions={"file_id": file_id},
            limit=None
        )
        print(f"📊 Found {len(embeddings)} embeddings to delete")
    except Exception as e:
        print(f"❌ Failed to query embeddings: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if not embeddings:
        print("✅ No embeddings found for this file_id - nothing to delete")
        return
    
    # Show sample embedding info
    sample = embeddings[0]
    print(f"\n📄 Sample embedding:")
    print(f"   _key: {sample.get('_key')}")
    print(f"   file_id: {sample.get('file_id')}")
    print(f"   column_name: {sample.get('column_name')}")
    print(f"   content_id: {sample.get('content_id')}")
    
    # Confirm deletion
    if not args.confirm:
        print(f"\n⚠️  WARNING: This will delete {len(embeddings)} embeddings!")
        print(f"   This action cannot be undone.")
        response = input(f"\n   Are you sure you want to delete these embeddings? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Deletion cancelled")
            return
    
    # Delete embeddings
    print(f"\n🗑️  Deleting {len(embeddings)} embeddings...")
    deleted_count = 0
    failed_count = 0
    
    for i, emb in enumerate(embeddings):
        embedding_key = emb.get("_key")
        if not embedding_key:
            print(f"   ⚠️ Embedding {i+1} has no _key - skipping")
            failed_count += 1
            continue
        
        try:
            await arango_adapter.delete_document(
                collection="structured_embeddings",
                key=embedding_key
            )
            deleted_count += 1
            if deleted_count % 50 == 0:
                print(f"   ✅ Deleted {deleted_count}/{len(embeddings)} embeddings...")
        except Exception as e:
            print(f"   ❌ Failed to delete embedding {embedding_key}: {e}")
            failed_count += 1
    
    print(f"\n✅ Deletion complete!")
    print(f"   Deleted: {deleted_count} embeddings")
    if failed_count > 0:
        print(f"   Failed: {failed_count} embeddings")
    
    # Verify deletion
    print(f"\n🔍 Verifying deletion...")
    try:
        remaining = await arango_adapter.find_documents(
            collection="structured_embeddings",
            filter_conditions={"file_id": file_id},
            limit=10
        )
        if remaining:
            print(f"   ⚠️  Warning: {len(remaining)} embeddings still found (may need to check more)")
        else:
            print(f"   ✅ All embeddings deleted successfully")
    except Exception as e:
        print(f"   ⚠️  Could not verify deletion: {e}")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Recreate embeddings through the normal UI flow")
    print(f"   2. The new embeddings will automatically create embedding_file records")
    print(f"   3. The embedding_file will have the correct UI name and metadata")


if __name__ == "__main__":
    asyncio.run(main())




