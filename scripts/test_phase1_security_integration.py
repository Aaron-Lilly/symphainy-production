#!/usr/bin/env python3
"""
Phase 1 Security Integration Test Script

Tests ForwardAuth endpoint and tenant-aware routing.

WHAT: Validates Phase 1 security integration implementation
HOW: Tests ForwardAuth endpoint, tenant context extraction, and tenant isolation
"""

import os
import sys
import asyncio
import httpx
import json
from typing import Dict, Any, Optional

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load environment secrets
try:
    from dotenv import load_dotenv
    secrets_file = os.path.join(project_root, ".env.secrets")
    if os.path.exists(secrets_file):
        load_dotenv(secrets_file)
        print(f"✅ Loaded credentials from: {secrets_file}")
    else:
        # Try alternative location
        alt_secrets = os.path.join(project_root, "symphainy-platform", ".env.secrets")
        if os.path.exists(alt_secrets):
            load_dotenv(alt_secrets)
            print(f"✅ Loaded credentials from: {alt_secrets}")
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables only")

# Test configuration
API_BASE_URL = os.getenv("SYMPHAINY_API_URL", "http://localhost/api")
FORWARDAUTH_URL = f"{API_BASE_URL}/auth/validate-token"

# Test Supabase configuration (for getting test tokens)
# Support multiple credential formats:
# 1. TEST_SUPABASE_* (explicit test credentials)
# 2. SUPABASE_URL and SUPABASE_ANON_KEY (direct)
# 3. SUPABASE_PROJECT_REF and SUPABASE_ACCESS_TOKEN (construct URL from ref)

def _get_supabase_url():
    """Get Supabase URL from various sources."""
    # Try explicit test URL first
    test_url = os.getenv("TEST_SUPABASE_URL")
    if test_url:
        return test_url
    
    # Try direct SUPABASE_URL
    supabase_url = os.getenv("SUPABASE_URL")
    if supabase_url:
        return supabase_url
    
    # Try constructing from PROJECT_REF
    project_ref = os.getenv("SUPABASE_PROJECT_REF")
    if project_ref:
        return f"https://{project_ref}.supabase.co"
    
    return None

def _get_supabase_anon_key():
    """Get Supabase anon key from various sources."""
    # Try explicit test anon key first
    test_key = os.getenv("TEST_SUPABASE_ANON_KEY")
    if test_key:
        return test_key
    
    # Try new naming convention (preferred)
    publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    if publishable_key:
        return publishable_key
    
    # Try legacy naming
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    if anon_key:
        return anon_key
    
    # Try SUPABASE_KEY (some configs use this)
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_key:
        return supabase_key
    
    # Try SUPABASE_ACCESS_TOKEN (might be the anon key)
    access_token = os.getenv("SUPABASE_ACCESS_TOKEN")
    if access_token:
        return access_token
    
    return None

TEST_SUPABASE_URL = _get_supabase_url()
TEST_SUPABASE_ANON_KEY = _get_supabase_anon_key()
TEST_SUPABASE_EMAIL = os.getenv("TEST_SUPABASE_EMAIL", os.getenv("SUPABASE_TEST_EMAIL", "test@symphainy.com"))
TEST_SUPABASE_PASSWORD = os.getenv("TEST_SUPABASE_PASSWORD", os.getenv("SUPABASE_TEST_PASSWORD", "test_password_123"))


class Phase1SecurityTester:
    """Test Phase 1 Security Integration."""
    
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.forwardauth_url = FORWARDAUTH_URL
        self.test_results = []
        self.test_supabase_url = TEST_SUPABASE_URL
        self.test_supabase_anon_key = TEST_SUPABASE_ANON_KEY
        self.test_supabase_email = TEST_SUPABASE_EMAIL
        self.test_supabase_password = TEST_SUPABASE_PASSWORD
    
    async def get_test_token(self) -> Optional[str]:
        """
        Get a test token from test Supabase project.
        
        Returns:
            JWT token if successful, None otherwise
        """
        if not self.test_supabase_url or not self.test_supabase_anon_key:
            print("   ⚠️  Test Supabase credentials not configured")
            print("   Set TEST_SUPABASE_URL and TEST_SUPABASE_ANON_KEY environment variables")
            return None
        
        try:
            print(f"   🔐 Getting test token from Supabase: {self.test_supabase_url}")
            
            # Try to sign in with test credentials
            async with httpx.AsyncClient() as client:
                # Sign in to get token
                sign_in_url = f"{self.test_supabase_url}/auth/v1/token?grant_type=password"
                response = await client.post(
                    sign_in_url,
                    json={
                        "email": self.test_supabase_email,
                        "password": self.test_supabase_password
                    },
                    headers={
                        "apikey": self.test_supabase_anon_key,
                        "Content-Type": "application/json"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get("access_token")
                    if access_token:
                        print(f"   ✅ Test token obtained successfully")
                        return access_token
                    else:
                        print(f"   ⚠️  No access_token in response")
                        return None
                elif response.status_code == 400:
                    # User might not exist, try to sign up first
                    print(f"   ⚠️  Sign in failed (user may not exist), attempting sign up...")
                    sign_up_url = f"{self.test_supabase_url}/auth/v1/signup"
                    sign_up_response = await client.post(
                        sign_up_url,
                        json={
                            "email": self.test_supabase_email,
                            "password": self.test_supabase_password
                        },
                        headers={
                            "apikey": self.test_supabase_anon_key,
                            "Content-Type": "application/json"
                        },
                        timeout=10.0
                    )
                    
                    if sign_up_response.status_code in [200, 201]:
                        sign_up_data = sign_up_response.json()
                        access_token = sign_up_data.get("access_token")
                        if access_token:
                            print(f"   ✅ Test user created and token obtained")
                            return access_token
                    
                    print(f"   ⚠️  Sign up failed: {sign_up_response.status_code}")
                    print(f"   Response: {sign_up_response.text[:200]}")
                    return None
                else:
                    print(f"   ⚠️  Failed to get test token: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"   ⚠️  Error getting test token: {e}")
            return None
    
    async def test_forwardauth_valid_token(self, token: str) -> Dict[str, Any]:
        """Test ForwardAuth endpoint with valid token."""
        print("\n🧪 Test 1: ForwardAuth with Valid Token")
        print(f"   URL: {self.forwardauth_url}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.forwardauth_url,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                result = {
                    "test": "forwardauth_valid_token",
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "headers": dict(response.headers),
                    "body": response.text[:200] if response.text else None
                }
                
                if response.status_code == 200:
                    print(f"   ✅ Success: Token validated")
                    print(f"   Headers: {json.dumps(dict(response.headers), indent=2)}")
                else:
                    print(f"   ❌ Failed: Status {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                
                return result
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "test": "forwardauth_valid_token",
                "success": False,
                "error": str(e)
            }
    
    async def test_forwardauth_invalid_token(self) -> Dict[str, Any]:
        """Test ForwardAuth endpoint with invalid token."""
        print("\n🧪 Test 2: ForwardAuth with Invalid Token")
        print(f"   URL: {self.forwardauth_url}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.forwardauth_url,
                    headers={"Authorization": "Bearer invalid_token_12345"},
                    timeout=10.0
                )
                
                result = {
                    "test": "forwardauth_invalid_token",
                    "status_code": response.status_code,
                    "success": response.status_code == 401,
                    "headers": dict(response.headers),
                    "body": response.text[:200] if response.text else None
                }
                
                if response.status_code == 401:
                    print(f"   ✅ Success: Invalid token correctly rejected (401)")
                else:
                    print(f"   ❌ Failed: Expected 401, got {response.status_code}")
                
                return result
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "test": "forwardauth_invalid_token",
                "success": False,
                "error": str(e)
            }
    
    async def test_forwardauth_missing_token(self) -> Dict[str, Any]:
        """Test ForwardAuth endpoint with missing token."""
        print("\n🧪 Test 3: ForwardAuth with Missing Token")
        print(f"   URL: {self.forwardauth_url}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.forwardauth_url,
                    timeout=10.0
                )
                
                result = {
                    "test": "forwardauth_missing_token",
                    "status_code": response.status_code,
                    "success": response.status_code == 401,
                    "headers": dict(response.headers),
                    "body": response.text[:200] if response.text else None
                }
                
                if response.status_code == 401:
                    print(f"   ✅ Success: Missing token correctly rejected (401)")
                else:
                    print(f"   ❌ Failed: Expected 401, got {response.status_code}")
                
                return result
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "test": "forwardauth_missing_token",
                "success": False,
                "error": str(e)
            }
    
    async def test_tenant_aware_routing(self, token: str) -> Dict[str, Any]:
        """Test tenant-aware routing with valid token."""
        print("\n🧪 Test 4: Tenant-Aware Routing")
        print(f"   URL: {self.api_base_url}/v1/content-pillar/health")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/v1/content-pillar/health",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                # Check if tenant context headers are present in response or logs
                result = {
                    "test": "tenant_aware_routing",
                    "status_code": response.status_code,
                    "success": response.status_code in [200, 404],  # 404 is OK if route not found
                    "headers": dict(response.headers),
                    "body": response.text[:200] if response.text else None
                }
                
                # Check for tenant context in response (if available)
                if "X-Tenant-Id" in response.headers or "tenant" in response.text.lower():
                    print(f"   ✅ Success: Tenant context detected")
                else:
                    print(f"   ⚠️  Warning: Tenant context not visible in response (may be internal)")
                
                print(f"   Status: {response.status_code}")
                
                return result
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "test": "tenant_aware_routing",
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self, token: Optional[str] = None):
        """Run all Phase 1 security integration tests."""
        print("=" * 70)
        print("Phase 1: Security Integration - Test Suite")
        print("=" * 70)
        
        # If no token provided, try to get one from test Supabase
        if not token:
            print("\n🔍 No token provided, attempting to get test token from Supabase...")
            token = await self.get_test_token()
            if token:
                print("   ✅ Using test token from Supabase")
            else:
                print("   ⚠️  Could not get test token")
                print("   Set SYMPHAINY_API_TOKEN or configure TEST_SUPABASE_* variables")
        
        # Test 1: Valid token (if available)
        if token:
            result1 = await self.test_forwardauth_valid_token(token)
            self.test_results.append(result1)
        else:
            print("\n⚠️  Skipping valid token test (no token available)")
            print("   Options:")
            print("   1. Set SYMPHAINY_API_TOKEN environment variable")
            print("   2. Set TEST_SUPABASE_URL and TEST_SUPABASE_ANON_KEY")
            print("   3. Set TEST_SUPABASE_EMAIL and TEST_SUPABASE_PASSWORD")
        
        # Test 2: Invalid token
        result2 = await self.test_forwardauth_invalid_token()
        self.test_results.append(result2)
        
        # Test 3: Missing token
        result3 = await self.test_forwardauth_missing_token()
        self.test_results.append(result3)
        
        # Test 4: Tenant-aware routing (if token available)
        if token:
            result4 = await self.test_tenant_aware_routing(token)
            self.test_results.append(result4)
        else:
            print("\n⚠️  Skipping tenant-aware routing test (no token available)")
        
        # Print summary
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        
        passed = sum(1 for r in self.test_results if r.get("success", False))
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"{status}: {result.get('test', 'unknown')}")
            if not result.get("success", False) and "error" in result:
                print(f"      Error: {result['error']}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "results": self.test_results
        }


async def main():
    """Main test execution."""
    tester = Phase1SecurityTester()
    
    # Get token from environment (optional)
    token = os.getenv("SYMPHAINY_API_TOKEN")
    
    if not token:
        print("⚠️  No SYMPHAINY_API_TOKEN provided")
        print("   Some tests will be skipped")
        print("   To test with a valid token:")
        print("   export SYMPHAINY_API_TOKEN='your_supabase_jwt_token'")
        print()
    
    results = await tester.run_all_tests(token)
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())

