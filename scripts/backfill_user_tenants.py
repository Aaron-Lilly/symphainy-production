#!/usr/bin/env python3
"""
Backfill User-Tenant Relationships

One-time script to create tenant relationships for all existing users
who don't have one. This fixes users created before the tenant system
was implemented or users created via direct Supabase admin API.

Usage:
    python3 scripts/backfill_user_tenants.py
"""

import os
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
                        if not os.getenv(key):  # Don't override existing
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
                            if not os.getenv(key):
                                os.environ[key] = value

async def backfill_user_tenants():
    """Backfill tenant relationships for all users without tenants."""
    try:
        from supabase import create_client
        
        # Get Supabase credentials
        url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
        
        if not url or not service_key:
            print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
            return False
        
        print(f"🔍 Connecting to Supabase: {url}")
        client = create_client(url, service_key)
        
        # Step 1: Get all users
        print("\n📋 Step 1: Fetching all users...")
        try:
            users_response = client.auth.admin.list_users()
            users = users_response.users if hasattr(users_response, 'users') else []
            print(f"   ✅ Found {len(users)} users")
        except Exception as e:
            print(f"   ❌ Failed to fetch users: {e}")
            return False
        
        # Step 2: Check which users have tenants
        print("\n📋 Step 2: Checking tenant relationships...")
        users_without_tenants = []
        
        for user in users:
            user_id = user.id
            email = getattr(user, 'email', 'N/A')
            
            try:
                # Check if user has tenant
                tenant_check = client.table("user_tenants").select("tenant_id").eq("user_id", user_id).eq("is_primary", True).limit(1).execute()
                
                if not tenant_check.data:
                    users_without_tenants.append({
                        "user_id": user_id,
                        "email": email
                    })
            except Exception as e:
                print(f"   ⚠️  Error checking tenant for user {user_id}: {e}")
                # Assume no tenant if check fails
                users_without_tenants.append({
                    "user_id": user_id,
                    "email": email
                })
        
        print(f"   ✅ Found {len(users_without_tenants)} users without tenants")
        
        if not users_without_tenants:
            print("\n✅ All users already have tenant relationships!")
            return True
        
        # Step 3: Create tenants for users without them
        print(f"\n📋 Step 3: Creating tenants for {len(users_without_tenants)} users...")
        created = 0
        failed = 0
        
        for user_info in users_without_tenants:
            user_id = user_info["user_id"]
            email = user_info["email"]
            
            try:
                print(f"\n   👤 Processing user: {email} ({user_id[:8]}...)")
                
                # Create tenant
                tenant_data = {
                    "name": f"Tenant for {email or user_id[:8]}",
                    "slug": f"tenant-{user_id[:8]}-{uuid.uuid4().hex[:8]}",
                    "type": "individual",
                    "owner_id": user_id,
                    "status": "active",
                    "metadata": {
                        "created_by": "backfill_script",
                        "created_for": email,
                        "backfilled": True
                    }
                }
                tenant_response = client.table("tenants").insert(tenant_data).execute()
                
                if tenant_response.data:
                    tenant_id = tenant_response.data[0]["id"]
                    print(f"      ✅ Tenant created: {tenant_id}")
                    
                    # Link user to tenant
                    link_data = {
                        "user_id": user_id,
                        "tenant_id": tenant_id,
                        "role": "owner",
                        "is_primary": True
                    }
                    link_response = client.table("user_tenants").insert(link_data).execute()
                    
                    if link_response.data:
                        print(f"      ✅ User linked to tenant (role: owner)")
                        created += 1
                    else:
                        print(f"      ⚠️  Tenant created but linking failed")
                        failed += 1
                else:
                    print(f"      ❌ Failed to create tenant")
                    failed += 1
                    
            except Exception as e:
                print(f"      ❌ Error processing user {user_id}: {e}")
                failed += 1
        
        # Summary
        print("\n" + "="*80)
        print("BACKFILL SUMMARY")
        print("="*80)
        print(f"✅ Tenants created and linked: {created}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total processed: {len(users_without_tenants)}")
        print("="*80)
        
        return failed == 0
        
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
    success = asyncio.run(backfill_user_tenants())
    
    sys.exit(0 if success else 1)



