#!/usr/bin/env python3
"""
Verify User-Tenant Setup in Supabase

Checks if test user exists in user_tenants table and has proper permissions.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

def load_env():
    """Load environment variables from .env files."""
    # Try environment variables first
    if os.getenv("SUPABASE_URL") and (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SECRET_KEY")):
        return
    
    # Try .env.secrets in symphainy-platform
    env_file = project_root / "symphainy-platform" / ".env.secrets"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip('"').strip("'")
                        os.environ[key] = value
    
    # Also try root .env files
    for env_file_name in [".env", ".env.secrets"]:
        env_path = project_root / env_file_name
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip().strip('"').strip("'")
                            if not os.getenv(key):  # Don't override existing
                                os.environ[key] = value

async def verify_user_tenant_setup():
    """Verify user-tenant setup for test user."""
    try:
        from supabase import create_client
        
        # Get Supabase credentials
        url = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_PROJECT_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
        
        if not url or not service_key:
            print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
            return False
        
        print(f"🔍 Connecting to Supabase: {url}")
        client = create_client(url, service_key)
        
        # Test user ID from the logs
        test_user_id = "3a0d577e-dd18-41df-bfa7-ac5a404b6a83"
        print(f"\n📋 Checking user: {test_user_id}")
        
        # Check if user exists in auth.users
        try:
            user_response = client.auth.admin.get_user_by_id(test_user_id)
            user = user_response.user
            print(f"✅ User exists in auth.users")
            print(f"   Email: {user.email}")
            print(f"   Created: {user.created_at}")
        except Exception as e:
            print(f"❌ User not found in auth.users: {e}")
            return False
        
        # Check user_tenants table
        print(f"\n📋 Checking user_tenants table...")
        try:
            response = client.table("user_tenants").select(
                "tenant_id, role, is_primary, tenants(type, name, status)"
            ).eq("user_id", test_user_id).eq("is_primary", True).execute()
            
            if response.data:
                tenant_data = response.data[0]
                tenant_info = tenant_data.get("tenants", {})
                role = tenant_data.get("role", "member")
                
                print(f"✅ User has tenant record:")
                print(f"   Tenant ID: {tenant_data.get('tenant_id')}")
                print(f"   Tenant Name: {tenant_info.get('name', 'N/A')}")
                print(f"   Tenant Type: {tenant_info.get('type', 'N/A')}")
                print(f"   Role: {role}")
                print(f"   Is Primary: {tenant_data.get('is_primary', False)}")
                
                # Check permissions mapping
                role_permissions = {
                    "owner": ["read", "write", "admin", "delete"],
                    "admin": ["read", "write", "admin"],
                    "member": ["read", "write"],
                    "viewer": ["read"]
                }
                expected_permissions = role_permissions.get(role, ["read"])
                print(f"   Expected Permissions: {expected_permissions}")
                
                return True
            else:
                print(f"❌ No tenant record found in user_tenants table")
                print(f"   This is why permissions are empty!")
                
                # Check user_metadata as fallback
                print(f"\n📋 Checking user_metadata fallback...")
                user_metadata = user.user_metadata or {}
                if user_metadata.get("tenant_id"):
                    print(f"⚠️  Found tenant_id in user_metadata: {user_metadata.get('tenant_id')}")
                    print(f"   But user_tenants record is missing - permissions won't work")
                else:
                    print(f"❌ No tenant_id in user_metadata either")
                
                return False
                
        except Exception as e:
            print(f"❌ Error querying user_tenants: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except ImportError:
        print("❌ supabase-py not installed")
        print("   Install with: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    
    load_env()
    result = asyncio.run(verify_user_tenant_setup())
    
    if not result:
        print("\n" + "="*80)
        print("❌ USER-TENANT SETUP VERIFICATION FAILED")
        print("="*80)
        print("\nTo fix this:")
        print("1. Ensure user exists in auth.users")
        print("2. Create a record in user_tenants table with:")
        print("   - user_id: <user_id>")
        print("   - tenant_id: <tenant_id>")
        print("   - role: 'member' (or 'admin' for full permissions)")
        print("   - is_primary: true")
        print("3. Or run: python3 scripts/setup_test_users.py")
        sys.exit(1)
    else:
        print("\n" + "="*80)
        print("✅ USER-TENANT SETUP VERIFIED")
        print("="*80)
        sys.exit(0)

