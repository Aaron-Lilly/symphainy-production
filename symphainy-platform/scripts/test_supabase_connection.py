#!/usr/bin/env python3
"""
Test Supabase Connection

Quick script to verify Supabase is configured correctly and accessible.
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

def test_supabase_connection():
    """Test Supabase connection and configuration."""
    print("=" * 80)
    print("🧪 Testing Supabase Connection")
    print("=" * 80)
    print()
    
    # Check credentials
    print("📋 Step 1: Checking credentials...")
    url = os.getenv("SUPABASE_URL")
    secret_key = (
        os.getenv("SUPABASE_SECRET_KEY") or
        os.getenv("SUPABASE_SERVICE_KEY") or
        os.getenv("SUPABASE_KEY")
    )
    publishable_key = (
        os.getenv("SUPABASE_PUBLISHABLE_KEY") or
        os.getenv("SUPABASE_ANON_KEY") or
        os.getenv("SUPABASE_KEY")
    )
    
    if not url:
        print("❌ SUPABASE_URL not found")
        return False
    
    if not secret_key:
        print("❌ SUPABASE_SECRET_KEY (or SERVICE_KEY) not found")
        return False
    
    print(f"✅ URL: {url}")
    print(f"✅ Secret Key: {secret_key[:30]}...")
    if publishable_key:
        print(f"✅ Publishable Key: {publishable_key[:30]}...")
    print()
    
    # Test connection via Supabase client
    print("📋 Step 2: Testing Supabase connection...")
    try:
        from supabase import create_client, Client
        
        client: Client = create_client(url, secret_key)
        
        # Test connection by querying a system table
        # This will fail if credentials are wrong
        response = client.table("project_files").select("uuid").limit(1).execute()
        
        print("✅ Supabase connection successful!")
        print(f"   Response status: {response}")
        print()
        
        # Check if tables exist
        print("📋 Step 3: Verifying schema...")
        try:
            # Try to query project_files table structure
            test_query = client.table("project_files").select("uuid").limit(0).execute()
            print("✅ project_files table exists")
        except Exception as e:
            print(f"⚠️  project_files table check: {str(e)[:100]}")
        
        try:
            # Try to query file_links table
            test_query = client.table("file_links").select("id").limit(0).execute()
            print("✅ file_links table exists")
        except Exception as e:
            print(f"⚠️  file_links table check: {str(e)[:100]}")
        
        print()
        
        # Test storage bucket
        print("📋 Step 4: Testing storage bucket...")
        try:
            buckets = client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            
            if "project_files" in bucket_names:
                print("✅ project_files bucket exists")
            else:
                print("⚠️  project_files bucket not found")
                print(f"   Available buckets: {bucket_names}")
        except Exception as e:
            print(f"⚠️  Storage check: {str(e)[:100]}")
        
        print()
        print("=" * 80)
        print("✅ Supabase connection test completed!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  1. Verify SUPABASE_URL is correct (includes https://)")
        print("  2. Verify SUPABASE_SECRET_KEY is the full key (starts with eyJ or sb_)")
        print("  3. Check that your project is not paused in Supabase dashboard")
        print("  4. Verify network connectivity to Supabase")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)






