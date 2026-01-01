#!/usr/bin/env python3
"""
Simple test to verify test Supabase authentication works.
This tests the full flow: backend → test Supabase → authentication.
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load test environment
test_env_file = project_root / "tests" / ".env.test"
if test_env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(test_env_file)
    print("✅ Loaded test environment")
else:
    print("❌ .env.test file not found")
    sys.exit(1)

async def test_auth():
    """Test authentication with test Supabase."""
    base_url = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
    test_email = os.getenv("TEST_USER_EMAIL", "test_user@symphainy.com")
    test_password = os.getenv("TEST_USER_PASSWORD", "test_password_123")
    
    print(f"\n{'='*60}")
    print("Testing Authentication with Test Supabase")
    print(f"{'='*60}")
    print(f"Backend URL: {base_url}")
    print(f"Test User: {test_email}")
    print()
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        # Step 1: Register user
        print("[STEP 1] Registering test user...")
        try:
            register_response = await client.post(
                "/api/auth/register",
                json={
                    "email": test_email,
                    "password": test_password,
                    "name": "Test User"
                }
            )
            
            if register_response.status_code in [200, 201]:
                print("✅ User registered successfully")
            elif register_response.status_code == 400 and "already exists" in register_response.text.lower():
                print("⚠️  User already exists, proceeding with login")
            else:
                print(f"❌ Registration failed: {register_response.status_code} - {register_response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
        
        # Step 2: Login user
        print("\n[STEP 2] Logging in test user...")
        try:
            login_response = await client.post(
                "/api/auth/login",
                json={
                    "email": test_email,
                    "password": test_password
                }
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get("token") or login_data.get("access_token")
                if token:
                    print(f"✅ Login successful! Token: {token[:30]}...")
                    return True
                else:
                    print(f"❌ Login succeeded but no token: {login_data}")
                    return False
            else:
                print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

if __name__ == "__main__":
    print("\n⚠️  NOTE: Backend must be running with TEST_MODE=true")
    print("   Start backend: cd symphainy-platform && TEST_MODE=true python3 main.py\n")
    
    result = asyncio.run(test_auth())
    
    if result:
        print(f"\n{'='*60}")
        print("✅ Test Supabase authentication verified!")
        print("✅ Ready to run full test suite")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print("❌ Test Supabase authentication failed")
        print("   Check:")
        print("   1. Backend is running with TEST_MODE=true")
        print("   2. Test Supabase credentials are correct")
        print("   3. Migrations were run successfully")
        print(f"{'='*60}\n")
        sys.exit(1)



