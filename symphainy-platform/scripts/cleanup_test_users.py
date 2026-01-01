#!/usr/bin/env python3
"""
Cleanup Test Users Created During Multi-Tenant Testing

Removes test users that were created with fake email addresses
to prevent email bounces and Supabase email suspension.
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

# Import after path setup
try:
    from supabase import create_client
except ImportError:
    print("❌ supabase-py not installed. Install with: pip install supabase")
    sys.exit(1)


def cleanup_test_users():
    """Remove test users created during multi-tenant testing."""
    print("=" * 70)
    print("Cleanup Test Users - Multi-Tenant Testing")
    print("=" * 70)
    print()
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    if "localhost" in supabase_url:
        supabase_url = "https://rmymvrifwvqpeffmxkwi.supabase.co"
    
    supabase_service_key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ Missing Supabase credentials")
        return False
    
    # Create admin client
    admin_client = create_client(supabase_url, supabase_service_key)
    
    print("🔍 Finding test users...")
    print("   Looking for users with email patterns:")
    print("   - test_tenant_*@gmail.com")
    print("   - test_token_*@gmail.com")
    print("   - test_isolate*@gmail.com")
    print()
    
    # Get all users
    try:
        # List all users (admin API)
        users_response = admin_client.auth.admin.list_users()
        users = users_response.users if hasattr(users_response, 'users') else []
        
        test_users = []
        for user in users:
            email = user.email if hasattr(user, 'email') else getattr(user, 'email', None)
            if email:
                # Check if it matches test patterns
                if any(pattern in email for pattern in [
                    'test_tenant_',
                    'test_token_',
                    'test_isolate'
                ]) and '@gmail.com' in email:
                    test_users.append({
                        'id': user.id if hasattr(user, 'id') else getattr(user, 'id', None),
                        'email': email
                    })
        
        if not test_users:
            print("✅ No test users found to clean up")
            return True
        
        print(f"📋 Found {len(test_users)} test user(s) to remove:")
        for user in test_users:
            print(f"   - {user['email']} (ID: {user['id'][:8]}...)")
        print()
        
        # Confirm deletion
        response = input("Delete these test users? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Cleanup cancelled")
            return False
        
        print()
        print("🗑️  Deleting test users...")
        
        deleted_count = 0
        for user in test_users:
            try:
                admin_client.auth.admin.delete_user(user['id'])
                print(f"   ✅ Deleted: {user['email']}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ Failed to delete {user['email']}: {e}")
        
        print()
        print(f"✅ Cleanup complete: {deleted_count}/{len(test_users)} users deleted")
        
        # Also clean up associated tenant data
        print()
        print("🧹 Cleaning up associated tenant data...")
        try:
            # Delete user_tenants relationships
            for user in test_users:
                try:
                    # Delete from user_tenants table
                    admin_client.table("user_tenants").delete().eq("user_id", user['id']).execute()
                    print(f"   ✅ Cleaned user_tenants for: {user['email']}")
                except Exception as e:
                    print(f"   ⚠️  Could not clean user_tenants for {user['email']}: {e}")
            
            # Note: We're not deleting tenants themselves as they might be referenced elsewhere
            # The tenant cleanup can be done separately if needed
            print("   ℹ️  Tenant records left intact (can be cleaned separately if needed)")
            
        except Exception as e:
            print(f"   ⚠️  Could not clean tenant data: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = cleanup_test_users()
    sys.exit(0 if success else 1)






