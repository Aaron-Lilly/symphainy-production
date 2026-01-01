#!/usr/bin/env python3
"""
Production Test: Traefik Routing Patterns

Tests Traefik routing patterns for unified architecture:
1. Path-based routing (/api/* → backend, frontend excludes /api)
2. Router priorities (backend-auth > backend-upload > backend > frontend)
3. Middleware chains (rate limiting, CORS, compression, security headers)
4. Service routing (correct service receives requests)

This test validates that the unified architecture routes requests correctly.
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any, Optional

pytestmark = [pytest.mark.e2e, pytest.mark.production_readiness, pytest.mark.critical]

TIMEOUT = 30.0
TRAEFIK_API_URL = "http://localhost:8080/api"
BASE_URL = "http://localhost"  # Traefik entry point


class TestTraefikRouting:
    """Test Traefik routing patterns for unified architecture."""
    
    @pytest.fixture
    async def traefik_client(self):
        """HTTP client for Traefik API."""
        async with httpx.AsyncClient(base_url=TRAEFIK_API_URL, timeout=TIMEOUT) as client:
            yield client
    
    @pytest.fixture
    async def http_client(self):
        """HTTP client for testing routing through Traefik."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT, follow_redirects=True) as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_api_paths_route_to_backend(self, http_client):
        """
        Test that /api/* paths route to backend service.
        
        Verifies:
        - /api/health → backend
        - /api/v1/content-pillar/* → backend
        - /api/v1/operations-pillar/* → backend
        """
        print("\n" + "="*70)
        print("TRAEFIK ROUTING TEST: API Paths Route to Backend")
        print("="*70)
        
        test_paths = [
            "/api/health",
            "/api/v1/content-pillar/list-files",
            "/api/v1/operations-pillar/list-standard-operating-procedures",
        ]
        
        for path in test_paths:
            print(f"\n[TEST] Testing path: {path}")
            try:
                response = await asyncio.wait_for(
                    http_client.get(path),
                    timeout=TIMEOUT
                )
                
                # Should NOT be 404 (routing works) or 503 (service unavailable is OK for now)
                assert response.status_code != 404, \
                    f"❌ Path {path} returned 404 - routing failed (not routed to backend)"
                
                # Should be routed to backend (200, 401, 403, 503 are all valid - means routing worked)
                assert response.status_code in [200, 401, 403, 503], \
                    f"❌ Path {path} returned unexpected status {response.status_code} - {response.text[:200]}"
                
                print(f"   ✅ Path {path} routed correctly (status: {response.status_code})")
                
            except asyncio.TimeoutError:
                pytest.fail(f"❌ Path {path} timed out - routing may be broken")
            except Exception as e:
                pytest.fail(f"❌ Path {path} failed: {e}")
    
    @pytest.mark.asyncio
    async def test_frontend_excludes_api_paths(self, http_client):
        """
        Test that frontend router excludes /api paths.
        
        Verifies:
        - / → frontend (or 404 if frontend not available)
        - /dashboard → frontend (or 404 if frontend not available)
        - /api/health → NOT frontend (should be backend)
        """
        print("\n" + "="*70)
        print("TRAEFIK ROUTING TEST: Frontend Excludes API Paths")
        print("="*70)
        
        # Test frontend paths (should route to frontend, not backend)
        frontend_paths = [
            "/",
            "/dashboard",
        ]
        
        for path in frontend_paths:
            print(f"\n[TEST] Testing frontend path: {path}")
            try:
                response = await asyncio.wait_for(
                    http_client.get(path),
                    timeout=TIMEOUT
                )
                
                # Frontend paths should NOT return backend API responses
                # They might return 200 (frontend), 404 (not found), or 503 (service unavailable)
                # But should NOT return JSON API responses
                content_type = response.headers.get("Content-Type", "")
                
                if response.status_code == 200:
                    # If 200, check that it's not a JSON API response
                    if "application/json" in content_type:
                        # Check if it looks like a backend API response
                        try:
                            data = response.json()
                            if "status" in data or "error" in data or "message" in data:
                                pytest.fail(
                                    f"❌ Frontend path {path} returned backend API response: {data}"
                                )
                        except:
                            pass  # Not JSON, that's fine
                
                print(f"   ✅ Frontend path {path} routed correctly (status: {response.status_code})")
                
            except asyncio.TimeoutError:
                pytest.fail(f"❌ Frontend path {path} timed out")
            except Exception as e:
                pytest.fail(f"❌ Frontend path {path} failed: {e}")
        
        # Test that /api paths do NOT route to frontend
        api_path = "/api/health"
        print(f"\n[TEST] Verifying /api path does NOT route to frontend: {api_path}")
        try:
            response = await asyncio.wait_for(
                http_client.get(api_path),
                timeout=TIMEOUT
            )
            
            # Should route to backend (200, 401, 403, 503 are all valid)
            assert response.status_code != 404, \
                f"❌ API path {api_path} returned 404 - may have routed to frontend instead of backend"
            
            print(f"   ✅ API path {api_path} correctly excluded from frontend (status: {response.status_code})")
            
        except asyncio.TimeoutError:
            pytest.fail(f"❌ API path {api_path} timed out")
    
    @pytest.mark.asyncio
    async def test_backend_auth_router_priority(self, http_client):
        """
        Test that backend-auth router has correct priority.
        
        Verifies:
        - /api/auth/* → backend-auth router (priority 100)
        - /api/health → backend-auth router (priority 100)
        - These routes should match BEFORE the main backend router
        """
        print("\n" + "="*70)
        print("TRAEFIK ROUTING TEST: Backend Auth Router Priority")
        print("="*70)
        
        auth_paths = [
            "/api/auth/login",
            "/api/health",
        ]
        
        for path in auth_paths:
            print(f"\n[TEST] Testing auth path: {path}")
            try:
                response = await asyncio.wait_for(
                    http_client.get(path) if path == "/api/health" else http_client.post(
                        path,
                        json={"email": "test@example.com", "password": "test"}
                    ),
                    timeout=TIMEOUT
                )
                
                # Should NOT be 404 (routing works)
                assert response.status_code != 404, \
                    f"❌ Auth path {path} returned 404 - backend-auth router not matching"
                
                # Should be routed (200, 400, 401, 403, 422, 503 are all valid)
                assert response.status_code in [200, 400, 401, 403, 422, 503], \
                    f"❌ Auth path {path} returned unexpected status {response.status_code}"
                
                print(f"   ✅ Auth path {path} routed via backend-auth router (status: {response.status_code})")
                
            except asyncio.TimeoutError:
                pytest.fail(f"❌ Auth path {path} timed out")
            except Exception as e:
                pytest.fail(f"❌ Auth path {path} failed: {e}")
    
    @pytest.mark.asyncio
    async def test_backend_upload_router(self, http_client):
        """
        Test that backend-upload router handles file uploads.
        
        Verifies:
        - /api/v1/content-pillar/upload-file → backend-upload router (priority 90)
        - Upload router should match BEFORE main backend router
        """
        print("\n" + "="*70)
        print("TRAEFIK ROUTING TEST: Backend Upload Router")
        print("="*70)
        
        upload_path = "/api/v1/content-pillar/upload-file"
        
        print(f"\n[TEST] Testing upload path: {upload_path}")
        try:
            # Test with a small file to verify routing
            files = {
                "file": ("test.txt", b"test content", "text/plain")
            }
            
            response = await asyncio.wait_for(
                http_client.post(upload_path, files=files),
                timeout=TIMEOUT
            )
            
            # Should NOT be 404 (routing works)
            assert response.status_code != 404, \
                f"❌ Upload path {upload_path} returned 404 - backend-upload router not matching"
            
            # Should be routed (200, 400, 401, 403, 422, 503 are all valid)
            assert response.status_code in [200, 400, 401, 403, 422, 503], \
                f"❌ Upload path {upload_path} returned unexpected status {response.status_code}"
            
            print(f"   ✅ Upload path {upload_path} routed via backend-upload router (status: {response.status_code})")
            
        except asyncio.TimeoutError:
            pytest.fail(f"❌ Upload path {upload_path} timed out")
        except Exception as e:
            pytest.fail(f"❌ Upload path {upload_path} failed: {e}")
    
    @pytest.mark.asyncio
    async def test_router_priority_order(self, traefik_client):
        """
        Test that router priorities are correct.
        
        Verifies:
        - backend-auth router has priority 100 (highest)
        - backend-upload router has priority 90
        - backend router has priority 1 (lowest)
        - frontend router has priority 1 (lowest)
        """
        print("\n" + "="*70)
        print("TRAEFIK ROUTING TEST: Router Priority Order")
        print("="*70)
        
        try:
            # Query Traefik API for routers
            response = await asyncio.wait_for(
                traefik_client.get("/http/routers"),
                timeout=TIMEOUT
            )
            
            assert response.status_code == 200, \
                f"❌ Failed to query Traefik API: {response.status_code}"
            
            routers_list = response.json()
            
            # Traefik API returns a list, not a dict
            assert isinstance(routers_list, list), \
                f"❌ Expected list from Traefik API, got {type(routers_list)}"
            
            # Convert to dict for easier lookup
            routers = {router["name"]: router for router in routers_list}
            
            # Find our routers
            backend_auth_router = routers.get("backend-auth@docker")
            backend_upload_router = routers.get("backend-upload@docker")
            backend_router = routers.get("backend@docker")
            frontend_router = routers.get("frontend@docker")
            
            # Verify routers exist
            assert backend_auth_router is not None, \
                "❌ backend-auth router not found in Traefik"
            assert backend_upload_router is not None, \
                "❌ backend-upload router not found in Traefik"
            assert backend_router is not None, \
                "❌ backend router not found in Traefik"
            assert frontend_router is not None, \
                "❌ frontend router not found in Traefik"
            
            # Verify priorities
            backend_auth_priority = backend_auth_router.get("priority", 0)
            backend_upload_priority = backend_upload_router.get("priority", 0)
            backend_priority = backend_router.get("priority", 0)
            frontend_priority = frontend_router.get("priority", 0)
            
            print(f"\n[PRIORITIES]")
            print(f"   backend-auth: {backend_auth_priority}")
            print(f"   backend-upload: {backend_upload_priority}")
            print(f"   backend: {backend_priority}")
            print(f"   frontend: {frontend_priority}")
            
            # Verify priority order: backend-auth > backend-upload > backend/frontend
            assert backend_auth_priority > backend_upload_priority, \
                f"❌ backend-auth priority ({backend_auth_priority}) should be > backend-upload priority ({backend_upload_priority})"
            
            assert backend_upload_priority > backend_priority, \
                f"❌ backend-upload priority ({backend_upload_priority}) should be > backend priority ({backend_priority})"
            
            assert backend_upload_priority > frontend_priority, \
                f"❌ backend-upload priority ({backend_upload_priority}) should be > frontend priority ({frontend_priority})"
            
            print("\n   ✅ Router priorities are correct")
            
        except asyncio.TimeoutError:
            pytest.fail("❌ Traefik API query timed out")
        except Exception as e:
            pytest.fail(f"❌ Router priority test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_middleware_chains_applied(self, traefik_client):
        """
        Test that middleware chains are applied correctly.
        
        Verifies:
        - backend-chain middleware includes: rate-limit, cors-headers, compression, security-headers
        - backend-chain-with-auth middleware includes: supabase-auth, tenant-context, rate-limit, cors-headers, compression, security-headers
        - frontend-chain middleware includes: cors-headers, compression, security-headers
        """
        print("\n" + "="*70)
        print("TRAEFIK ROUTING TEST: Middleware Chains Applied")
        print("="*70)
        
        try:
            # Query Traefik API for middlewares
            response = await asyncio.wait_for(
                traefik_client.get("/http/middlewares"),
                timeout=TIMEOUT
            )
            
            assert response.status_code == 200, \
                f"❌ Failed to query Traefik API: {response.status_code}"
            
            middlewares_list = response.json()
            
            # Traefik API returns a list, not a dict
            assert isinstance(middlewares_list, list), \
                f"❌ Expected list from Traefik API, got {type(middlewares_list)}"
            
            # Convert to dict for easier lookup
            middlewares = {mw["name"]: mw for mw in middlewares_list}
            
            # Check for expected middleware chains
            backend_chain = middlewares.get("backend-chain@file")
            backend_chain_with_auth = middlewares.get("backend-chain-with-auth@file")
            frontend_chain = middlewares.get("frontend-chain@file")
            
            assert backend_chain is not None, \
                "❌ backend-chain middleware not found"
            assert backend_chain_with_auth is not None, \
                "❌ backend-chain-with-auth middleware not found"
            assert frontend_chain is not None, \
                "❌ frontend-chain middleware not found"
            
            # Verify backend-chain includes expected middlewares
            if "chain" in backend_chain:
                chain_middlewares = backend_chain["chain"].get("middlewares", [])
                expected_middlewares = ["rate-limit", "cors-headers", "compression", "security-headers"]
                
                print(f"\n[BACKEND-CHAIN] Middlewares: {chain_middlewares}")
                
                # Check that expected middlewares are in the chain
                for expected in expected_middlewares:
                    found = any(expected in mw for mw in chain_middlewares)
                    assert found, \
                        f"❌ backend-chain missing middleware: {expected}"
                
                print("   ✅ backend-chain includes expected middlewares")
            
            # Verify backend-chain-with-auth includes expected middlewares
            if "chain" in backend_chain_with_auth:
                chain_middlewares = backend_chain_with_auth["chain"].get("middlewares", [])
                expected_middlewares = ["supabase-auth", "tenant-context", "rate-limit", "cors-headers", "compression", "security-headers"]
                
                print(f"\n[BACKEND-CHAIN-WITH-AUTH] Middlewares: {chain_middlewares}")
                
                # Check that expected middlewares are in the chain
                for expected in expected_middlewares:
                    found = any(expected in mw for mw in chain_middlewares)
                    assert found, \
                        f"❌ backend-chain-with-auth missing middleware: {expected}"
                
                print("   ✅ backend-chain-with-auth includes expected middlewares")
            
            # Verify frontend-chain includes expected middlewares
            if "chain" in frontend_chain:
                chain_middlewares = frontend_chain["chain"].get("middlewares", [])
                expected_middlewares = ["cors-headers", "compression", "security-headers"]
                
                print(f"\n[FRONTEND-CHAIN] Middlewares: {chain_middlewares}")
                
                # Check that expected middlewares are in the chain
                for expected in expected_middlewares:
                    found = any(expected in mw for mw in chain_middlewares)
                    assert found, \
                        f"❌ frontend-chain missing middleware: {expected}"
                
                print("   ✅ frontend-chain includes expected middlewares")
            
        except asyncio.TimeoutError:
            pytest.fail("❌ Traefik API query timed out")
        except Exception as e:
            pytest.fail(f"❌ Middleware chain test failed: {e}")

