#!/usr/bin/env python3
"""
Supabase Schema Setup Script

Runs the file management schema SQL against your Supabase project.
Can be run programmatically or you can use the Supabase web interface.

Usage:
    python3 scripts/setup_supabase_schema.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Load environment secrets
secrets_file = project_root / ".env.secrets"
if not secrets_file.exists():
    secrets_file = project_root / "env_secrets_for_cursor.md"

load_dotenv(secrets_file)

def get_supabase_credentials():
    """Get Supabase credentials from environment."""
    url = os.getenv("SUPABASE_URL")
    
    # Try new naming first, then legacy
    secret_key = (
        os.getenv("SUPABASE_SECRET_KEY") or
        os.getenv("SUPABASE_SERVICE_KEY") or
        os.getenv("SUPABASE_KEY")
    )
    
    if not url or not secret_key:
        raise ValueError(
            "Missing Supabase credentials. Set SUPABASE_URL and one of:\n"
            "  - SUPABASE_SECRET_KEY (new naming)\n"
            "  - SUPABASE_SERVICE_KEY (legacy)\n"
            "  - SUPABASE_KEY (fallback)"
        )
    
    return url, secret_key

def read_schema_file():
    """Read the schema SQL file."""
    schema_file = project_root / "foundations" / "public_works_foundation" / "sql" / "create_file_management_schema.sql"
    
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    
    with open(schema_file, "r") as f:
        return f.read()

def execute_schema_via_rest(url: str, secret_key: str, sql: str):
    """
    Execute SQL via Supabase REST API.
    
    Note: Supabase REST API doesn't directly support DDL statements.
    This method uses the PostgREST API which has limitations.
    For DDL (CREATE TABLE, etc.), we recommend using the web interface or psql.
    """
    import requests
    
    # Supabase REST API endpoint for SQL execution
    # Note: This requires the SQL extension or direct database access
    api_url = f"{url.rstrip('/')}/rest/v1/rpc/exec_sql"
    
    headers = {
        "apikey": secret_key,
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }
    
    # Split SQL into individual statements
    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
    
    print(f"📝 Attempting to execute {len(statements)} SQL statements...")
    print("⚠️  Note: Supabase REST API has limitations for DDL statements.")
    print("   If this fails, use the web interface method instead.\n")
    
    results = []
    for i, statement in enumerate(statements, 1):
        if not statement:
            continue
        
        try:
            # Try to execute via REST API
            # Note: This may not work for all DDL statements
            response = requests.post(
                api_url,
                headers=headers,
                json={"query": statement},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Statement {i}/{len(statements)} executed successfully")
                results.append({"statement": i, "success": True})
            else:
                print(f"⚠️  Statement {i}/{len(statements)} failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                results.append({"statement": i, "success": False, "error": response.text})
        except Exception as e:
            print(f"❌ Statement {i}/{len(statements)} error: {str(e)}")
            results.append({"statement": i, "success": False, "error": str(e)})
    
    return results

def main():
    """Main execution."""
    print("=" * 80)
    print("🚀 Supabase Schema Setup Script")
    print("=" * 80)
    print()
    
    try:
        # Get credentials
        print("📋 Step 1: Loading credentials...")
        url, secret_key = get_supabase_credentials()
        print(f"✅ Found Supabase URL: {url}")
        print(f"✅ Found Secret Key: {secret_key[:20]}...")
        print()
        
        # Read schema
        print("📋 Step 2: Reading schema file...")
        sql = read_schema_file()
        print(f"✅ Schema file loaded ({len(sql)} characters, ~{len(sql.split(';'))} statements)")
        print()
        
        # Check if we can use psql (preferred method)
        import shutil
        psql_available = shutil.which("psql") is not None
        
        if psql_available:
            print("📋 Step 3: Using psql (recommended method)...")
            print()
            print("To run via psql, extract connection info from your Supabase URL:")
            print(f"  URL: {url}")
            print()
            print("Or use the Supabase web interface (easiest):")
            print("  1. Go to https://supabase.com/dashboard")
            print("  2. Select your project")
            print("  3. Click 'SQL Editor' in left sidebar")
            print("  4. Click 'New query'")
            print("  5. Paste the schema SQL")
            print("  6. Click 'Run' (or press Ctrl+Enter)")
            print()
            print("The schema SQL is ready to copy from:")
            print(f"  {project_root / 'foundations' / 'public_works_foundation' / 'sql' / 'create_file_management_schema.sql'}")
            print()
            
            # Offer to show the SQL
            response = input("Would you like to see the SQL to copy? (y/n): ").strip().lower()
            if response == 'y':
                print("\n" + "=" * 80)
                print("SQL SCHEMA (copy this to Supabase SQL Editor):")
                print("=" * 80)
                print(sql)
                print("=" * 80)
        else:
            print("📋 Step 3: Attempting to execute via REST API...")
            print("⚠️  Note: DDL statements may not work via REST API.")
            print("   If this fails, use the web interface method.\n")
            
            results = execute_schema_via_rest(url, secret_key, sql)
            
            success_count = sum(1 for r in results if r.get("success"))
            print()
            print("=" * 80)
            print(f"📊 Results: {success_count}/{len(results)} statements succeeded")
            print("=" * 80)
            
            if success_count < len(results):
                print("\n⚠️  Some statements failed. Use the web interface method instead:")
                print("  1. Go to Supabase Dashboard → SQL Editor")
                print("  2. Paste the schema SQL")
                print("  3. Run it")
                print()
                print("Schema file location:")
                print(f"  {project_root / 'foundations' / 'public_works_foundation' / 'sql' / 'create_file_management_schema.sql'}")
        
        print()
        print("✅ Setup script completed!")
        print()
        print("Next steps:")
        print("  1. Verify tables were created (Supabase Dashboard → Table Editor)")
        print("  2. Create storage bucket 'project_files' (Supabase Dashboard → Storage)")
        print("  3. Test platform connection")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Recommendation: Use the Supabase web interface instead:")
        print("  1. Go to https://supabase.com/dashboard")
        print("  2. Select your project")
        print("  3. Click 'SQL Editor' → 'New query'")
        print("  4. Copy schema from:")
        print(f"     {project_root / 'foundations' / 'public_works_foundation' / 'sql' / 'create_file_management_schema.sql'}")
        print("  5. Paste and run")
        sys.exit(1)

if __name__ == "__main__":
    main()






