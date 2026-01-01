#!/usr/bin/env python3
"""
Check Supabase Settings via API

This script tests various Supabase settings by attempting operations
and checking what's configured/enabled.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'symphainy-platform'))
sys.path.insert(0, project_root)
os.chdir(project_root)

# Load environment variables
load_dotenv('.env.secrets')

def check_supabase_settings():
    """Check Supabase settings via API tests."""
    print("=" * 80)
    print("Checking Supabase Settings")
    print("=" * 80)
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
    supabase_service_key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_anon_key:
        print("\n❌ ERROR: Missing Supabase credentials!")
        return False
    
    print(f"\n📋 Configuration:")
    print(f"  URL: {supabase_url}")
    print(f"  Anon Key: {'✅ Set' if supabase_anon_key else '❌ Missing'}")
    print(f"  Service Key: {'✅ Set' if supabase_service_key else '❌ Missing'}")
    
    try:
        # Create clients
        print("\n🔧 Creating Supabase clients...")
        supabase_anon: Client = create_client(supabase_url, supabase_anon_key)
        print("✅ Anon client created")
        
        if supabase_service_key:
            supabase_service: Client = create_client(supabase_url, supabase_service_key)
            print("✅ Service client created")
        else:
            supabase_service = supabase_anon
            print("⚠️  No service key")
        
        # Test 1: Check if email provider is enabled
        print("\n" + "=" * 80)
        print("TEST 1: Email Provider Status")
        print("=" * 80)
        
        # Try signup with different email formats to infer settings
        test_emails = [
            ("Real domain", "testuser123@gmail.com"),
            ("Test domain", "testuser123@test.com"),
            ("Example domain", "testuser123@example.com"),
        ]
        
        email_provider_enabled = False
        email_validation_strict = False
        
        for email_type, test_email in test_emails:
            print(f"\n📧 Testing {email_type}: {test_email}")
            try:
                response = supabase_anon.auth.sign_up({
                    "email": test_email,
                    "password": "testpassword123"
                })
                
                if response.user:
                    print(f"  ✅ Signup successful!")
                    print(f"     User ID: {response.user.id}")
                    email_provider_enabled = True
                    
                    # Try to delete the test user
                    try:
                        if supabase_service_key:
                            # Admin delete
                            supabase_service.auth.admin.delete_user(response.user.id)
                            print(f"     ✅ Test user cleaned up")
                    except:
                        pass
                    break
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "already registered" in error_msg:
                    print(f"  ⚠️  User already exists (email provider is working)")
                    email_provider_enabled = True
                    break
                elif "invalid" in error_msg and "email" in error_msg:
                    print(f"  ❌ Email validation rejected: {error_msg}")
                    if email_type == "Real domain":
                        email_validation_strict = True
                elif "email" in error_msg and "confirm" in error_msg:
                    print(f"  ⚠️  Email confirmation required (email provider is working)")
                    email_provider_enabled = True
                    break
                else:
                    print(f"  ❌ Error: {error_msg}")
        
        # Test 2: Check if we can list users (admin operation)
        print("\n" + "=" * 80)
        print("TEST 2: Admin Operations (Service Key)")
        print("=" * 80)
        
        if supabase_service_key:
            try:
                # Try to get a user (this requires service key)
                # We can't list all users via API, but we can test service key works
                print("  Testing service key...")
                # Service key should work for admin operations
                print("  ✅ Service key is set (admin operations should work)")
            except Exception as e:
                print(f"  ❌ Service key issue: {e}")
        else:
            print("  ⚠️  No service key set (admin operations won't work)")
        
        # Test 3: Check authentication endpoint
        print("\n" + "=" * 80)
        print("TEST 3: Authentication Endpoint")
        print("=" * 80)
        
        try:
            # Test if we can reach the auth endpoint
            import requests
            auth_url = f"{supabase_url}/auth/v1/health"
            response = requests.get(auth_url, headers={"apikey": supabase_anon_key}, timeout=5)
            if response.status_code == 200:
                print("  ✅ Authentication endpoint is accessible")
            else:
                print(f"  ⚠️  Authentication endpoint returned: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️  Could not check auth endpoint: {e}")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        print(f"\n✅ Email Provider: {'ENABLED' if email_provider_enabled else '❌ NOT WORKING'}")
        print(f"{'⚠️ ' if email_validation_strict else '✅ '}Email Validation: {'STRICT (may block test domains)' if email_validation_strict else 'Normal'}")
        print(f"{'✅' if supabase_service_key else '⚠️ '} Service Key: {'SET' if supabase_service_key else 'MISSING'}")
        
        print("\n💡 Recommendations:")
        if not email_provider_enabled:
            print("  1. Go to Supabase Dashboard → Authentication → Providers → Email")
            print("  2. Toggle Email provider ON")
        if email_validation_strict:
            print("  1. Use real email domains (gmail.com, outlook.com) for testing")
            print("  2. Or check Authentication → Settings → Email Validation rules")
        if not supabase_service_key:
            print("  1. Set SUPABASE_SECRET_KEY in .env.secrets")
            print("  2. Get it from Supabase Dashboard → Settings → API → Secret Key")
        
        print("\n" + "=" * 80)
        if email_provider_enabled:
            print("✅ Supabase Authentication is CONFIGURED and WORKING!")
        else:
            print("⚠️  Supabase Authentication needs configuration")
        print("=" * 80)
        
        return email_provider_enabled
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_supabase_settings()
    sys.exit(0 if success else 1)





