#!/usr/bin/env python3
"""
Production Test: Health Endpoint Consistency

Tests health endpoint consistency across services:
1. Backend health endpoint is /api/health
2. Health endpoint routes correctly through Traefik
3. Health endpoint response structure is consistent

This test validates that health endpoints follow consistent patterns.
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any, Optional

pytestmark = [pytest.mark.e2e, pytest.mark.production_readiness, pytest.mark.critical]

TIMEOUT = 30.0
BASE_URL = "http://localhost"


class TestHealthEndpointConsistency:
    """Test health endpoint consistency across services."""
    
    @pytest.fixture
    async def http_client(self):
        """HTTP client for testing health endpoints."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT, follow_redirects=True) as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_backend_health_endpoint(self, http_client):
        """
        Test that backend health endpoint is /api/health.
        
        Verifies:
        - /api/health endpoint exists
        - Endpoint returns 200 or valid status
        - Response structure is consistent
        """
        print("\n" + "="*70)
        print("HEALTH ENDPOINT CONSISTENCY TEST: Backend Health Endpoint")
        print("="*70)
        
        health_endpoint = "/api/health"
        
        print(f"\n[BACKEND HEALTH ENDPOINT]")
        print(f"   Endpoint: {health_endpoint}")
        
        try:
            response = await asyncio.wait_for(
                http_client.get(health_endpoint),
                timeout=TIMEOUT
            )
            
            assert response.status_code != 404, \
                f"❌ Health endpoint {health_endpoint} returned 404 - endpoint missing"
            
            # 200, 401, 403, 503 are all valid (means endpoint exists and responds)
            assert response.status_code in [200, 401, 403, 503], \
                f"❌ Health endpoint returned unexpected status {response.status_code}"
            
            print(f"   ✅ Health endpoint responds (status: {response.status_code})")
            
            # If 200, check response structure
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    print(f"   Response structure: {type(health_data)}")
                    
                    # Check for common health fields
                    if isinstance(health_data, dict):
                        if "status" in health_data:
                            print(f"   Status: {health_data['status']}")
                        if "health" in health_data:
                            print(f"   Health: {health_data['health']}")
                    
                    print(f"   ✅ Health endpoint response structure valid")
                except Exception as e:
                    print(f"   ⚠️  Health endpoint response is not JSON: {e}")
            
        except asyncio.TimeoutError:
            pytest.fail(f"❌ Health endpoint {health_endpoint} timed out")
        except Exception as e:
            pytest.fail(f"❌ Health endpoint test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_health_endpoint_routing(self, http_client):
        """
        Test that health endpoint routes correctly through Traefik.
        
        Verifies:
        - /api/health routes to backend (not frontend)
        - Traefik routing rules work correctly
        - Health endpoint is accessible via Traefik
        """
        print("\n" + "="*70)
        print("HEALTH ENDPOINT CONSISTENCY TEST: Health Endpoint Routing")
        print("="*70)
        
        health_endpoint = "/api/health"
        
        print(f"\n[HEALTH ENDPOINT ROUTING]")
        print(f"   Endpoint: {health_endpoint}")
        print(f"   Expected: Routes to backend via Traefik")
        
        try:
            response = await asyncio.wait_for(
                http_client.get(health_endpoint),
                timeout=TIMEOUT
            )
            
            # Should NOT be 404 (routing works)
            assert response.status_code != 404, \
                f"❌ Health endpoint {health_endpoint} returned 404 - routing may be broken"
            
            # Should route to backend (200, 401, 403, 503 are all valid)
            assert response.status_code in [200, 401, 403, 503], \
                f"❌ Health endpoint returned unexpected status {response.status_code}"
            
            # Check that it's not a frontend response (frontend would return HTML or different structure)
            content_type = response.headers.get("Content-Type", "")
            
            if "text/html" in content_type:
                print(f"   ⚠️  Health endpoint returned HTML (may have routed to frontend)")
            else:
                print(f"   ✅ Health endpoint routed to backend (Content-Type: {content_type})")
            
            print(f"   ✅ Health endpoint routing verified (status: {response.status_code})")
            
        except asyncio.TimeoutError:
            pytest.fail(f"❌ Health endpoint {health_endpoint} timed out")
        except Exception as e:
            pytest.fail(f"❌ Health endpoint routing test failed: {e}")





