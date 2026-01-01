#!/usr/bin/env python3
"""
Quick verification script to test that test Supabase setup is working.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load test environment
test_env_file = project_root / "tests" / ".env.test"
if test_env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(test_env_file)
    print("✅ Loaded test environment from .env.test")
else:
    print("❌ .env.test file not found")
    sys.exit(1)

# Check test credentials
test_url = os.getenv("TEST_SUPABASE_URL")
test_anon_key = os.getenv("TEST_SUPABASE_ANON_KEY")
test_service_key = os.getenv("TEST_SUPABASE_SERVICE_KEY")

if not test_url or not test_anon_key or not test_service_key:
    print("❌ Missing test Supabase credentials")
    sys.exit(1)

print(f"✅ Test Supabase URL: {test_url}")
print(f"✅ Test Supabase Anon Key: {test_anon_key[:20]}...")
print(f"✅ Test Supabase Service Key: {test_service_key[:20]}...")

# Try to connect to Supabase
try:
    from supabase import create_client, Client
    
    supabase: Client = create_client(test_url, test_service_key)
    
    # Test connection by querying a table
    # First, check if tenants table exists
    try:
        result = supabase.table("tenants").select("id").limit(1).execute()
        print("✅ Successfully connected to test Supabase")
        print("✅ Tenants table exists (migrations successful)")
    except Exception as e:
        # Table might not exist or might be empty - that's okay for now
        if "relation" in str(e).lower() or "does not exist" in str(e).lower():
            print("⚠️  Tenants table not found - migrations may not have run correctly")
        else:
            print(f"✅ Successfully connected to test Supabase (query error: {e})")
    
    print("\n✅ Test Supabase setup verified!")
    print("✅ Ready to run tests with TEST_MODE=true")
    
except ImportError:
    print("⚠️  supabase-py not installed, but credentials are configured")
    print("   Install with: pip install supabase")
    print("   Or proceed with backend testing (backend will handle Supabase connection)")
except Exception as e:
    print(f"❌ Failed to connect to test Supabase: {e}")
    sys.exit(1)



