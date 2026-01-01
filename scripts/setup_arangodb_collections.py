#!/usr/bin/env python3
"""
Setup Script for ArangoDB Collections

This script creates the necessary ArangoDB collections for:
- semantic_data (embeddings, semantic graphs, correlation maps)
- platform_observability (logs, metrics, traces, agent executions)

Usage:
    python scripts/setup_arangodb_collections.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent / "symphainy-platform"
sys.path.insert(0, str(project_root))


async def setup_arangodb_collections():
    """Create ArangoDB collections."""
    print("\n" + "="*80)
    print("SETTING UP ARANGODB COLLECTIONS")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Public Works Foundation
        pwf = PublicWorksFoundationService(di_container=di_container)
        await pwf.initialize_foundation()
        
        # Get ArangoDB adapter
        arango_adapter = pwf.arango_adapter
        
        if not arango_adapter:
            print("❌ ArangoDB adapter not found")
            return False
        
        print("✅ ArangoDB adapter retrieved")
        
        # Collections to create
        collections = {
            # Semantic Data Collections
            "structured_embeddings": {
                "type": "document",
                "description": "Stores semantic embeddings for structured data"
            },
            "semantic_graph_nodes": {
                "type": "document",
                "description": "Stores semantic graph nodes for unstructured data"
            },
            "semantic_graph_edges": {
                "type": "edge",
                "description": "Stores semantic graph edges for unstructured data"
            },
            "correlation_maps": {
                "type": "document",
                "description": "Stores correlation maps for hybrid data"
            },
            # Observability Collections
            "platform_logs": {
                "type": "document",
                "description": "Stores platform logs"
            },
            "platform_metrics": {
                "type": "document",
                "description": "Stores platform metrics"
            },
            "platform_traces": {
                "type": "document",
                "description": "Stores platform traces"
            },
            "agent_executions": {
                "type": "document",
                "description": "Stores agent execution records"
            }
        }
        
        created_count = 0
        existing_count = 0
        
        for collection_name, collection_info in collections.items():
            print(f"\n   Processing collection: {collection_name}")
            print(f"      Type: {collection_info['type']}")
            print(f"      Description: {collection_info['description']}")
            
            try:
                # Check if collection exists
                await arango_adapter._ensure_connected()
                db = arango_adapter._db
                
                if db.has_collection(collection_name):
                    print(f"      ⚠️  Collection already exists (skipping)")
                    existing_count += 1
                else:
                    # Create collection
                    if collection_info["type"] == "edge":
                        db.create_collection(collection_name, edge=True)
                    else:
                        db.create_collection(collection_name)
                    
                    print(f"      ✅ Collection created")
                    created_count += 1
                    
            except Exception as e:
                # Check if error is "already exists" (which is OK)
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print(f"      ⚠️  Collection already exists (skipping)")
                    existing_count += 1
                else:
                    print(f"      ❌ Error creating collection: {e}")
                    return False
        
        print("\n" + "="*80)
        print("SETUP SUMMARY")
        print("="*80)
        print(f"   Created: {created_count} collections")
        print(f"   Already existed: {existing_count} collections")
        print(f"   Total: {len(collections)} collections")
        
        # Verify collections
        print("\n   Verifying collections...")
        await arango_adapter._ensure_connected()
        db = arango_adapter._db
        
        verified_count = 0
        for collection_name in collections.keys():
            if db.has_collection(collection_name):
                verified_count += 1
                print(f"      ✅ {collection_name}")
            else:
                print(f"      ❌ {collection_name} (not found)")
        
        if verified_count == len(collections):
            print(f"\n✅ All {verified_count} collections verified")
            return True
        else:
            print(f"\n⚠️  Only {verified_count}/{len(collections)} collections verified")
            return False
        
    except Exception as e:
        print(f"❌ Error setting up ArangoDB collections: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function."""
    success = await setup_arangodb_collections()
    
    if success:
        print("\n🎉 ArangoDB setup completed successfully!")
        return 0
    else:
        print("\n❌ ArangoDB setup failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)



