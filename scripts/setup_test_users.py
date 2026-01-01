#!/usr/bin/env python3
"""
Setup Pre-Confirmed Test Users for E2E Testing

Creates and confirms 4 test users in Supabase:
- testuser0@symphainy.com (for E2E tests)
- testuser1@symphainy.com (for UAT/Demo 1)
- testuser2@symphainy.com (for UAT/Demo 2)
- testuser3@symphainy.com (for UAT/Demo 3)

All users are pre-confirmed so they can log in immediately.
"""

import os
import sys
import uuid
from pathlib import Path
from supabase import create_client, Client
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_env_secrets() -> Dict[str, Optional[str]]:
    """Load Supabase credentials from environment or .env.secrets file."""
    env_file = project_root / "symphainy-platform" / ".env.secrets"
    
    secrets = {}
    
    # Try environment variables first
    secrets["SUPABASE_URL"] = os.getenv("SUPABASE_URL")
    secrets["SUPABASE_SERVICE_KEY"] = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
    
    # Fall back to .env.secrets file
    if not secrets["SUPABASE_URL"] or not secrets["SUPABASE_SERVICE_KEY"]:
        if env_file.exists():
            print(f"📄 Reading from {env_file}")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            
                            # Map various key names to standard names
                            if key in ["SUPABASE_URL"]:
                                secrets["SUPABASE_URL"] = value
                            elif key in ["SUPABASE_SERVICE_KEY", "SUPABASE_SECRET_KEY"]:
                                secrets["SUPABASE_SERVICE_KEY"] = value
    
    return secrets

def create_and_confirm_user(
    supabase_service: Client,
    email: str,
    password: str,
    name: str
) -> Dict:
    """Create a user and confirm them immediately using admin API."""
    print(f"\n👤 Creating user: {email}")
    
    try:
        # Step 1: Create user via admin API (bypasses email confirmation)
        response = supabase_service.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Pre-confirm the email
            "user_metadata": {
                "name": name,
                "test_user": True
            }
        })
        
        if response.user:
            user_id = response.user.id
            print(f"   ✅ User created: {user_id}")
            
            # Step 2: Verify user is confirmed
            user = supabase_service.auth.admin.get_user_by_id(user_id)
            if user and hasattr(user, 'user') and user.user:
                is_confirmed = user.user.email_confirmed_at is not None
                if is_confirmed:
                    print(f"   ✅ Email confirmed: {user.user.email_confirmed_at}")
                else:
                    print(f"   ⚠️  Email not confirmed, attempting manual confirmation...")
                    # Try to update user to confirm
                    supabase_service.auth.admin.update_user_by_id(
                        user_id,
                        {"email_confirm": True}
                    )
                    print(f"   ✅ Manual confirmation attempted")
            
            # ✅ NEW: Step 3: Create tenant for user
            tenant_id = None
            print(f"   📋 Creating tenant for user...")
            try:
                # Create tenant
                tenant_data = {
                    "name": f"Tenant for {name}",
                    "slug": f"tenant-{user_id[:8]}-{uuid.uuid4().hex[:8]}",
                    "type": "individual",
                    "owner_id": user_id,
                    "status": "active",
                    "metadata": {
                        "created_by": user_id,
                        "created_for": email,
                        "test_user": True
                    }
                }
                tenant_response = supabase_service.table("tenants").insert(tenant_data).execute()
                
                if tenant_response.data:
                    tenant_id = tenant_response.data[0]["id"]
                    print(f"   ✅ Tenant created: {tenant_id}")
                    
                    # Link user to tenant
                    link_data = {
                        "user_id": user_id,
                        "tenant_id": tenant_id,
                        "role": "owner",
                        "is_primary": True
                    }
                    link_response = supabase_service.table("user_tenants").insert(link_data).execute()
                    
                    if link_response.data:
                        print(f"   ✅ User linked to tenant (role: owner, is_primary: true)")
                    else:
                        print(f"   ⚠️  Failed to link user to tenant")
                else:
                    print(f"   ⚠️  Failed to create tenant")
            except Exception as tenant_error:
                print(f"   ⚠️  Error creating tenant: {tenant_error}")
                # Continue anyway - user is created, tenant can be created later
            
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "confirmed": True,
                "tenant_id": tenant_id
            }
        else:
            print(f"   ❌ User creation failed: No user returned")
            return {"success": False, "error": "No user returned"}
            
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            print(f"   ⚠️  User already exists, checking status...")
            # Try to get existing user and confirm if needed
            try:
                # List users and find by email (admin operation)
                users_response = supabase_service.auth.admin.list_users()
                existing_user = None
                if hasattr(users_response, 'users'):
                    for user in users_response.users:
                        if hasattr(user, 'email') and user.email == email:
                            existing_user = user
                            break
                
                if existing_user:
                    user_id = existing_user.id
                    is_confirmed = existing_user.email_confirmed_at is not None
                    
                    if not is_confirmed:
                        print(f"   ⚠️  User exists but not confirmed, confirming now...")
                        # Update user to confirm
                        supabase_service.auth.admin.update_user_by_id(
                            user_id,
                            {"email_confirm": True}
                        )
                        print(f"   ✅ User confirmed")
                    
                    # ✅ NEW: Check if user has tenant, create if missing
                    tenant_id = None
                    try:
                        # Check if user has tenant
                        tenant_check = supabase_service.table("user_tenants").select("tenant_id").eq("user_id", user_id).eq("is_primary", True).limit(1).execute()
                        
                        if tenant_check.data:
                            tenant_id = tenant_check.data[0]["tenant_id"]
                            print(f"   ✅ User already has tenant: {tenant_id}")
                        else:
                            # Create tenant for existing user
                            print(f"   📋 User exists but has no tenant - creating tenant...")
                            tenant_data = {
                                "name": f"Tenant for {name}",
                                "slug": f"tenant-{user_id[:8]}-{uuid.uuid4().hex[:8]}",
                                "type": "individual",
                                "owner_id": user_id,
                                "status": "active",
                                "metadata": {
                                    "created_by": user_id,
                                    "created_for": email,
                                    "test_user": True
                                }
                            }
                            tenant_response = supabase_service.table("tenants").insert(tenant_data).execute()
                            
                            if tenant_response.data:
                                tenant_id = tenant_response.data[0]["id"]
                                print(f"   ✅ Tenant created: {tenant_id}")
                                
                                # Link user to tenant
                                link_data = {
                                    "user_id": user_id,
                                    "tenant_id": tenant_id,
                                    "role": "owner",
                                    "is_primary": True
                                }
                                link_response = supabase_service.table("user_tenants").insert(link_data).execute()
                                
                                if link_response.data:
                                    print(f"   ✅ User linked to tenant (role: owner, is_primary: true)")
                                else:
                                    print(f"   ⚠️  Failed to link user to tenant")
                    except Exception as tenant_error:
                        print(f"   ⚠️  Error checking/creating tenant: {tenant_error}")
                    
                    return {
                        "success": True,
                        "user_id": user_id,
                        "email": email,
                        "confirmed": True,
                        "existing": True,
                        "tenant_id": tenant_id
                    }
                else:
                    print(f"   ❌ User exists but could not retrieve details")
                    return {"success": False, "error": "Could not retrieve existing user"}
            except Exception as e2:
                print(f"   ❌ Error checking existing user: {e2}")
                return {"success": False, "error": f"User exists but error: {str(e2)}"}
        else:
            print(f"   ❌ Error creating user: {error_msg}")
            return {"success": False, "error": error_msg}

def main():
    """Main function to create all test users."""
    print("=" * 80)
    print("🔧 Setting Up Pre-Confirmed Test Users")
    print("=" * 80)
    
    # Load credentials
    secrets = load_env_secrets()
    
    supabase_url = secrets.get("SUPABASE_URL")
    supabase_service_key = secrets.get("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ Missing Supabase credentials!")
        print("   Required: SUPABASE_URL, SUPABASE_SERVICE_KEY")
        print("   Set in environment or .env.secrets file")
        return 1
    
    print(f"\n✅ Supabase URL: {supabase_url}")
    print(f"✅ Service Key: {'*' * 20}...{supabase_service_key[-8:]}")
    
    # Create Supabase service client (admin operations)
    try:
        supabase_service: Client = create_client(supabase_url, supabase_service_key)
        print("✅ Supabase service client created")
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return 1
    
    # Test users to create
    test_users = [
        {
            "email": "testuser0@symphainy.com",
            "password": "TestPassword123!",
            "name": "E2E Test User"
        },
        {
            "email": "testuser1@symphainy.com",
            "password": "TestPassword123!",
            "name": "UAT Demo 1 User"
        },
        {
            "email": "testuser2@symphainy.com",
            "password": "TestPassword123!",
            "name": "UAT Demo 2 User"
        },
        {
            "email": "testuser3@symphainy.com",
            "password": "TestPassword123!",
            "name": "UAT Demo 3 User"
        }
    ]
    
    results = []
    for user_info in test_users:
        result = create_and_confirm_user(
            supabase_service,
            user_info["email"],
            user_info["password"],
            user_info["name"]
        )
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Summary")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n✅ Successfully created/confirmed: {success_count}/{len(test_users)}")
    
    for i, result in enumerate(results):
        status = "✅" if result.get("success") else "❌"
        existing = " (existing)" if result.get("existing") else ""
        print(f"   {status} {test_users[i]['email']}{existing}")
    
    if success_count == len(test_users):
        print("\n🎉 All test users are ready!")
        print("\n📝 Test User Credentials:")
        print("   Email: testuser0@symphainy.com")
        print("   Password: TestPassword123!")
        print("\n   (Same password for all test users)")
        return 0
    else:
        print(f"\n⚠️  {len(test_users) - success_count} user(s) failed to create/confirm")
        return 1

if __name__ == "__main__":
    sys.exit(main())

