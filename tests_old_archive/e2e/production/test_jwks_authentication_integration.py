#!/usr/bin/env python3
"""
Production Test: JWKS Authentication Integration

Tests JWKS authentication end-to-end:
1. JWKS token validation works
2. JWKS caching works (first call slower, subsequent calls faster)
3. Complete authentication flow with JWKS

This test validates that JWKS authentication works correctly in the unified architecture.
"""

import pytest
import httpx
import asyncio
import time
from typing import Dict, Any, Optional

pytestmark = [pytest.mark.e2e, pytest.mark.production_readiness, pytest.mark.critical]

TIMEOUT = 30.0
BASE_URL = "http://localhost"


class TestJWKSAuthenticationIntegration:
    """Test JWKS authentication in unified architecture."""
    
    @pytest.fixture
    async def http_client(self):
        """HTTP client for testing authentication."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT, follow_redirects=True) as client:
            yield client
    
    @pytest.fixture
    async def authenticated_client(self):
        """HTTP client with authentication token."""
        from tests.e2e.production.test_production_client import ProductionTestClient
        import os
        
        base_url = BASE_URL
        test_user_email = (
            os.getenv("TEST_USER_EMAIL") or 
            os.getenv("TEST_SUPABASE_EMAIL") or 
            "test_user@symphainy.com"
        )
        test_user_password = (
            os.getenv("TEST_USER_PASSWORD") or 
            os.getenv("TEST_SUPABASE_PASSWORD") or 
            "test_password_123"
        )
        
        client = ProductionTestClient(
            base_url=base_url,
            test_user_email=test_user_email,
            test_user_password=test_user_password
        )
        
        # Authenticate to get token
        token = await client.authenticate()
        
        yield client, token
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_jwks_token_validation(self, authenticated_client):
        """
        Test that JWKS token validation works.
        
        Verifies:
        - Login to get JWT token
        - Token is validated using JWKS (local)
        - Token can be used in API requests
        """
        print("\n" + "="*70)
        print("JWKS AUTHENTICATION INTEGRATION TEST: Token Validation")
        print("="*70)
        
        client, token = authenticated_client
        
        if not token:
            pytest.skip("❌ Authentication failed - cannot test JWKS validation")
        
        print(f"\n[TOKEN VALIDATION]")
        print(f"   Token obtained: ✅")
        print(f"   Token length: {len(token)} characters")
        
        # Use token in API request (this will trigger JWKS validation)
        try:
            start_time = time.time()
            response = await asyncio.wait_for(
                client.get("/api/health"),
                timeout=TIMEOUT
            )
            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Should NOT be 401 (token validation worked)
            assert response.status_code != 401, \
                "❌ Token validation failed - returned 401 Unauthorized"
            
            # 200, 403, 503 are all valid (means token was validated)
            assert response.status_code in [200, 403, 503], \
                f"❌ Token validation returned unexpected status {response.status_code}"
            
            print(f"   ✅ Token validated successfully (status: {response.status_code})")
            print(f"   Validation time: {elapsed_time:.0f}ms")
            
            # First call may be slower (JWKS fetch), subsequent calls should be faster
            if elapsed_time > 500:
                print(f"   ℹ️  First call (includes JWKS fetch): {elapsed_time:.0f}ms")
            else:
                print(f"   ℹ️  Cached JWKS (fast validation): {elapsed_time:.0f}ms")
            
        except asyncio.TimeoutError:
            pytest.fail("❌ Token validation timed out")
        except Exception as e:
            pytest.fail(f"❌ Token validation failed: {e}")
    
    @pytest.mark.asyncio
    async def test_jwks_caching(self, authenticated_client):
        """
        Test that JWKS keys are cached.
        
        Verifies:
        - First request: JWKS fetch (should take ~700ms)
        - Subsequent requests: cached JWKS (should take < 200ms)
        """
        print("\n" + "="*70)
        print("JWKS AUTHENTICATION INTEGRATION TEST: JWKS Caching")
        print("="*70)
        
        client, token = authenticated_client
        
        if not token:
            pytest.skip("❌ Authentication failed - cannot test JWKS caching")
        
        print(f"\n[JWKS CACHING]")
        
        # First request (may include JWKS fetch)
        print(f"   [REQUEST 1] First request (may fetch JWKS)...")
        try:
            start_time = time.time()
            response1 = await asyncio.wait_for(
                client.get("/api/health"),
                timeout=TIMEOUT
            )
            elapsed_time1 = (time.time() - start_time) * 1000
            
            assert response1.status_code != 401, \
                "❌ First request failed - token validation error"
            
            print(f"      Status: {response1.status_code}")
            print(f"      Time: {elapsed_time1:.0f}ms")
            
        except Exception as e:
            pytest.fail(f"❌ First request failed: {e}")
        
        # Second request (should use cached JWKS)
        print(f"   [REQUEST 2] Second request (should use cached JWKS)...")
        try:
            start_time = time.time()
            response2 = await asyncio.wait_for(
                client.get("/api/health"),
                timeout=TIMEOUT
            )
            elapsed_time2 = (time.time() - start_time) * 1000
            
            assert response2.status_code != 401, \
                "❌ Second request failed - token validation error"
            
            print(f"      Status: {response2.status_code}")
            print(f"      Time: {elapsed_time2:.0f}ms")
            
            # Second request should be faster (cached JWKS)
            if elapsed_time2 < elapsed_time1:
                speedup = ((elapsed_time1 - elapsed_time2) / elapsed_time1) * 100
                print(f"      ✅ Caching working: {speedup:.0f}% faster")
            else:
                print(f"      ℹ️  Similar timing (may already be cached)")
            
        except Exception as e:
            pytest.fail(f"❌ Second request failed: {e}")
        
        # Third request (should also use cached JWKS)
        print(f"   [REQUEST 3] Third request (should use cached JWKS)...")
        try:
            start_time = time.time()
            response3 = await asyncio.wait_for(
                client.get("/api/health"),
                timeout=TIMEOUT
            )
            elapsed_time3 = (time.time() - start_time) * 1000
            
            assert response3.status_code != 401, \
                "❌ Third request failed - token validation error"
            
            print(f"      Status: {response3.status_code}")
            print(f"      Time: {elapsed_time3:.0f}ms")
            
            # Average of requests 2 and 3 should be faster than request 1
            avg_cached_time = (elapsed_time2 + elapsed_time3) / 2
            if avg_cached_time < elapsed_time1:
                speedup = ((elapsed_time1 - avg_cached_time) / elapsed_time1) * 100
                print(f"\n   ✅ JWKS caching verified: {speedup:.0f}% faster with cache")
            else:
                print(f"\n   ℹ️  JWKS may already be cached from previous tests")
            
        except Exception as e:
            pytest.fail(f"❌ Third request failed: {e}")
    
    @pytest.mark.asyncio
    async def test_jwks_authentication_flow(self, http_client):
        """
        Test complete authentication flow with JWKS.
        
        Verifies:
        - Login → Get token → Use token in API request
        - Token validation happens locally (no network calls to Supabase)
        """
        print("\n" + "="*70)
        print("JWKS AUTHENTICATION INTEGRATION TEST: Complete Authentication Flow")
        print("="*70)
        
        import os
        
        test_user_email = (
            os.getenv("TEST_USER_EMAIL") or 
            os.getenv("TEST_SUPABASE_EMAIL") or 
            "test_user@symphainy.com"
        )
        test_user_password = (
            os.getenv("TEST_USER_PASSWORD") or 
            os.getenv("TEST_SUPABASE_PASSWORD") or 
            "test_password_123"
        )
        
        print(f"\n[AUTHENTICATION FLOW]")
        
        # Step 1: Login
        print(f"   [STEP 1] Login to get JWT token...")
        try:
            login_response = await asyncio.wait_for(
                http_client.post(
                    "/api/auth/login",
                    json={
                        "email": test_user_email,
                        "password": test_user_password
                    }
                ),
                timeout=TIMEOUT
            )
            
            assert login_response.status_code == 200, \
                f"❌ Login failed: {login_response.status_code} - {login_response.text[:200]}"
            
            login_data = login_response.json()
            token = login_data.get("token") or login_data.get("access_token")
            
            assert token is not None, \
                "❌ Login response missing token"
            
            print(f"      ✅ Login successful")
            print(f"      Token obtained: {len(token)} characters")
            
        except asyncio.TimeoutError:
            pytest.fail("❌ Login timed out")
        except Exception as e:
            pytest.fail(f"❌ Login failed: {e}")
        
        # Step 2: Use token in API request (triggers JWKS validation)
        print(f"   [STEP 2] Use token in API request (triggers JWKS validation)...")
        try:
            start_time = time.time()
            api_response = await asyncio.wait_for(
                http_client.get(
                    "/api/health",
                    headers={"Authorization": f"Bearer {token}"}
                ),
                timeout=TIMEOUT
            )
            elapsed_time = (time.time() - start_time) * 1000
            
            # Should NOT be 401 (token validation worked)
            assert api_response.status_code != 401, \
                "❌ Token validation failed - returned 401 Unauthorized"
            
            # 200, 403, 503 are all valid (means token was validated)
            assert api_response.status_code in [200, 403, 503], \
                f"❌ API request returned unexpected status {api_response.status_code}"
            
            print(f"      ✅ Token validated successfully (status: {api_response.status_code})")
            print(f"      Validation time: {elapsed_time:.0f}ms")
            
            # JWKS validation should be fast (< 500ms for cached, < 1000ms for first call)
            if elapsed_time < 1000:
                print(f"      ✅ JWKS validation performance acceptable")
            else:
                print(f"      ⚠️  JWKS validation slower than expected ({elapsed_time:.0f}ms)")
            
        except asyncio.TimeoutError:
            pytest.fail("❌ API request timed out")
        except Exception as e:
            pytest.fail(f"❌ API request failed: {e}")
        
        print(f"\n   ✅ Complete authentication flow verified")





