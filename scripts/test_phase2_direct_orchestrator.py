#!/usr/bin/env python3
"""
Phase 2 Direct Test - Call Orchestrator.parse_file() directly
Bypasses API/auth to test semantic processing directly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/app')

async def test_direct_orchestrator():
    """Test semantic processing by calling orchestrator directly."""
    print("=" * 70)
    print("Phase 2 Direct Test: ContentAnalysisOrchestrator.parse_file()")
    print("=" * 70)
    print()
    
    try:
        # Import required components
        from foundations.di_container.di_container_service import DIContainerService
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        print("✅ Imports successful")
        
        # Create test files
        print("\n📝 Creating test files...")
        csv_file = Path("/tmp/test_structured.csv")
        csv_content = """policy_number,policyholder_name,policy_type,premium,coverage_amount,start_date
POL-001,John Doe,Home Insurance,1200.00,500000,2020-01-15
POL-002,Jane Smith,Auto Insurance,800.50,100000,2019-06-20
POL-003,Bob Johnson,Life Insurance,2500.00,1000000,2021-03-10"""
        csv_file.write_text(csv_content)
        print(f"✅ Created CSV: {csv_file}")
        
        # Note: We can't easily initialize the full orchestrator without the full platform
        # But we can verify the code is correct and check if we can test via a simpler method
        print("\n⚠️  Direct orchestrator testing requires full platform initialization")
        print("   (DI Container, Platform Gateway, etc.)")
        print("\n💡 Alternative: Test via API with authentication")
        print("   Or: Check if there's a way to get a test token")
        
        return False  # Can't test directly without full setup
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_via_simple_http():
    """Try to test via HTTP with a simple approach."""
    print("\n" + "=" * 70)
    print("Alternative: Check if we can get a test token")
    print("=" * 70)
    
    import httpx
    
    # Try to login and get token
    base_url = "http://localhost:8000"
    test_email = os.getenv("TEST_USER_EMAIL") or os.getenv("TEST_SUPABASE_EMAIL") or "test_user@symphainy.com"
    test_password = os.getenv("TEST_USER_PASSWORD") or os.getenv("TEST_SUPABASE_PASSWORD") or "test_password_123"
    
    print(f"🔐 Attempting authentication...")
    print(f"   Email: {test_email}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{base_url}/api/auth/login",
                json={"email": test_email, "password": test_password}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token") or data.get("access_token")
                if token:
                    print(f"✅ Authentication successful!")
                    print(f"   Token: {token[:20]}...")
                    return token
                else:
                    print(f"⚠️  No token in response: {data}")
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Auth request failed: {e}")
    
    return None

async def main():
    """Main test function."""
    print("\n🧪 Phase 2 Semantic Processing - Direct Orchestrator Test")
    print("=" * 70)
    
    # Try direct orchestrator test
    direct_ok = await test_direct_orchestrator()
    
    # Try to get auth token
    token = await test_via_simple_http()
    
    print("\n" + "=" * 70)
    if token:
        print("✅ Authentication successful!")
        print("   You can now use this token to test via API")
        print(f"   Token: Bearer {token[:30]}...")
        print("\n📝 Next: Use this token in API requests")
    else:
        print("⚠️  Could not authenticate")
        print("   Options:")
        print("   1. Test via frontend (which handles auth)")
        print("   2. Set up test user credentials")
        print("   3. Use existing file_id if available")
    print("=" * 70)
    
    return token is not None

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)






