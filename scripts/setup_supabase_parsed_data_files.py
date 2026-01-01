#!/usr/bin/env python3
"""
Setup Script for Supabase parsed_data_files Table

This script creates the parsed_data_files table in Supabase if it doesn't exist.

Usage:
    python scripts/setup_supabase_parsed_data_files.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent / "symphainy-platform"
sys.path.insert(0, str(project_root))


async def setup_parsed_data_files_table():
    """Create parsed_data_files table in Supabase."""
    print("\n" + "="*80)
    print("SETTING UP SUPABASE parsed_data_files TABLE")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Public Works Foundation
        pwf = PublicWorksFoundationService(di_container=di_container)
        await pwf.initialize_foundation()
        
        # Get Supabase adapter
        supabase_adapter = pwf.supabase_adapter
        
        if not supabase_adapter:
            print("❌ Supabase adapter not found")
            return False
        
        print("✅ Supabase adapter retrieved")
        
        # Read SQL schema
        sql_file = Path(__file__).parent.parent / "symphainy-platform" / "foundations" / "public_works_foundation" / "sql" / "create_parsed_data_files_schema.sql"
        
        if not sql_file.exists():
            print(f"❌ SQL file not found: {sql_file}")
            return False
        
        with open(sql_file, 'r') as f:
            sql_schema = f.read()
        
        print(f"✅ SQL schema loaded from: {sql_file}")
        
        # Note: Supabase REST API doesn't support DDL statements directly
        # We'll guide the user to use the web interface instead
        print("\n" + "="*80)
        print("SUPABASE SQL EXECUTION")
        print("="*80)
        print("\n⚠️  Note: Supabase REST API has limitations for DDL statements (CREATE TABLE, etc.)")
        print("   The recommended method is to use the Supabase web interface.\n")
        print("📋 To create the parsed_data_files table:")
        print("   1. Go to https://supabase.com/dashboard")
        print("   2. Select your project")
        print("   3. Click 'SQL Editor' in the left sidebar")
        print("   4. Click 'New query'")
        print("   5. Copy and paste the SQL schema below")
        print("   6. Click 'Run' (or press Ctrl+Enter)")
        print()
        print("="*80)
        print("SQL SCHEMA (copy this to Supabase SQL Editor):")
        print("="*80)
        print(sql_schema)
        print("="*80)
        print()
        
        # Offer to show the SQL
        try:
            response = input("Would you like to verify the table exists after running the SQL? (y/n): ").strip().lower()
            if response == 'y':
                print("\n   Verifying table exists...")
                # Try to query the table (this should work via REST API)
                try:
                    # Use service client to query (bypasses RLS)
                    result = supabase_adapter.service_client.table("parsed_data_files").select("uuid").limit(1).execute()
                    print("✅ Table verified: parsed_data_files exists and is accessible")
                except Exception as e:
                    if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                        print("❌ Table not found - please run the SQL in Supabase SQL Editor first")
                        return False
                    else:
                        print(f"⚠️  Could not verify table (but it may exist): {e}")
                        print("   Please verify manually in Supabase Dashboard → Table Editor")
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Skipping verification (interrupted)")
            print("   Please verify manually in Supabase Dashboard → Table Editor")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Supabase table: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function."""
    success = await setup_parsed_data_files_table()
    
    if success:
        print("\n🎉 Supabase setup completed successfully!")
        return 0
    else:
        print("\n❌ Supabase setup failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

