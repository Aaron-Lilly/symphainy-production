#!/usr/bin/env python3
"""
Test Supabase Authentication

Simple script to test if Supabase authentication is working with the new project.
Based on the legacy MVP pattern - it just works with the right credentials!
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

def test_supabase_auth():
    """Test Supabase authentication directly."""
    print("=" * 80)
    print("Testing Supabase Authentication")
    print("=" * 80)
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
    supabase_service_key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    print(f"\n📋 Configuration:")
    print(f"  URL: {supabase_url}")
    print(f"  Anon Key (first 30): {supabase_anon_key[:30] if supabase_anon_key else 'NOT SET'}...")
    print(f"  Service Key (first 30): {supabase_service_key[:30] if supabase_service_key else 'NOT SET'}...")
    
    if not supabase_url or not supabase_anon_key:
        print("\n❌ ERROR: Missing Supabase credentials!")
        print("   Make sure SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY (or SUPABASE_ANON_KEY) are set in .env.secrets")
        return False
    
    try:
        # Create clients (like legacy MVP)
        print("\n🔧 Creating Supabase clients...")
        supabase_anon: Client = create_client(supabase_url, supabase_anon_key)
        print("✅ Anon client created")
        
        if supabase_service_key:
            supabase_service: Client = create_client(supabase_url, supabase_service_key)
            print("✅ Service client created")
        else:
            supabase_service = supabase_anon
            print("⚠️  No service key, using anon client for admin operations")
        
        # Test signup with pre-authorized test user
        print("\n📝 Testing user login with pre-authorized test user...")
        # Use pre-confirmed test user (no email spam)
        test_email = "testuser0@symphainy.com"
        test_password = "TestPassword123!"
        
        try:
            # Test login with pre-authorized user (skip signup to avoid email spam)
            print("\n🔐 Testing user login...")
            login_response = supabase_anon.auth.sign_in_with_password({
                "email": test_email,
                "password": test_password
            })
            
            if login_response.user and login_response.session:
                print(f"✅ Login successful!")
                print(f"   User ID: {login_response.user.id}")
                print(f"   Access Token (first 30): {login_response.session.access_token[:30]}...")
                
                # Test token validation
                print("\n🔍 Testing token validation...")
                try:
                    user = supabase_service.auth.get_user(login_response.session.access_token)
                    if user.user:
                        print(f"✅ Token validation successful!")
                        print(f"   User ID: {user.user.id}")
                        print(f"   Email: {user.user.email}")
                        print("\n" + "=" * 80)
                        print("✅ ALL TESTS PASSED! Supabase authentication is working!")
                        print("=" * 80)
                        return True
                    else:
                        print("❌ Token validation failed: No user returned")
                        return False
                except Exception as e:
                    print(f"❌ Token validation failed: {e}")
                    return False
            else:
                print("❌ Login failed: No user or session returned")
                return False
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Login error: {error_msg}")
            print("\n💡 Make sure the test user exists:")
            print("   Run: python3 scripts/setup_test_users.py")
            return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Verify SUPABASE_URL is correct")
        print("   2. Verify SUPABASE_PUBLISHABLE_KEY (or SUPABASE_ANON_KEY) is correct")
        print("   3. Check Supabase Dashboard to ensure project is active")
        return False

if __name__ == "__main__":
    success = test_supabase_auth()
    sys.exit(0 if success else 1)

