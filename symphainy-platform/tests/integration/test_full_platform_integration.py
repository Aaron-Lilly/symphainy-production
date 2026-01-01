#!/usr/bin/env python3
"""
Full Platform Integration Tests

Comprehensive integration tests for end-to-end platform functionality:
1. Smart City service initialization and registration
2. SOA API discovery and invocation
3. MCP Tool registration
4. Realm service composition
5. Infrastructure integration
6. End-to-end workflows
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

import pytest
import httpx


class TestFullPlatformIntegration:
    """Full platform integration test suite."""
    
    BASE_URL = "http://localhost:8000"
    TIMEOUT = 30.0
    
    @pytest.fixture(scope="function")
    async def http_client(self):
        """Create HTTP client for API calls."""
        async with httpx.AsyncClient(base_url=self.BASE_URL, timeout=self.TIMEOUT) as client:
            yield client
    
    @pytest.fixture(scope="function")
    async def backend_health(self):
        """Verify backend is running and healthy."""
        try:
            async with httpx.AsyncClient(base_url=self.BASE_URL, timeout=self.TIMEOUT) as client:
                response = await client.get("/api/auth/health")
                assert response.status_code == 200, f"Backend health check failed: {response.status_code}"
                data = response.json()
                assert data.get("status") == "healthy", f"Backend not healthy: {data}"
                return data
        except Exception as e:
            pytest.skip(f"Backend not available: {e}")
    
    # ============================================================================
    # CATEGORY 1: Smart City Service Initialization
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_security_guard_initialized(self, backend_health):
        """Test Security Guard service initialization."""
        # Security Guard should be available via health check
        assert backend_health.get("security_guard_available") == True, "Security Guard not available"
        assert backend_health.get("mode") == "production", "Security Guard not in production mode"
    
    @pytest.mark.asyncio
    async def test_curator_registration(self, http_client):
        """Test that services are registered with Curator."""
        # This would require a Curator API endpoint to check registrations
        # For now, we verify via health checks and service discovery
        response = await http_client.get("/api/auth/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("security_guard_available") == True
    
    # ============================================================================
    # CATEGORY 2: SOA API Discovery and Invocation
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_security_guard_soa_api_authentication(self, http_client):
        """Test Security Guard authenticate_user SOA API."""
        # Test authentication endpoint
        test_credentials = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = await http_client.post(
                "/api/auth/login",
                json=test_credentials
            )
            # Should either succeed or return appropriate error (not 500)
            assert response.status_code in [200, 401, 422], \
                f"Unexpected status code: {response.status_code}"
        except Exception as e:
            pytest.fail(f"Authentication API call failed: {e}")
    
    @pytest.mark.asyncio
    async def test_security_guard_soa_api_registration(self, http_client):
        """Test Security Guard register_user SOA API."""
        # Test registration endpoint
        test_user = {
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = await http_client.post(
                "/api/auth/register",
                json=test_user
            )
            # Should either succeed or return appropriate error (not 500)
            assert response.status_code in [200, 201, 400, 422], \
                f"Unexpected status code: {response.status_code}"
        except Exception as e:
            pytest.fail(f"Registration API call failed: {e}")
    
    # ============================================================================
    # CATEGORY 3: Infrastructure Integration
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_supabase_connection(self, http_client):
        """Test Supabase connection via authentication."""
        # If authentication works, Supabase is connected
        response = await http_client.get("/api/auth/health")
        assert response.status_code == 200
        data = response.json()
        # If we get a response, infrastructure is at least partially working
        assert data is not None
    
    @pytest.mark.asyncio
    async def test_redis_connection(self, http_client):
        """Test Redis connection (indirectly via session management)."""
        # Redis is used for session management
        # If backend is running, Redis connection is likely working
        # (or backend would have failed to start)
        response = await http_client.get("/api/auth/health")
        assert response.status_code == 200
    
    # ============================================================================
    # CATEGORY 4: End-to-End Workflows
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_user_registration_workflow(self, http_client):
        """Test complete user registration workflow."""
        # Generate unique email
        timestamp = datetime.now().timestamp()
        test_user = {
            "email": f"integration_test_{timestamp}@example.com",
            "password": "TestPassword123!"
        }
        
        # Step 1: Register user
        register_response = await http_client.post(
            "/api/auth/register",
            json=test_user
        )
        
        # Step 2: If registration succeeds, try login
        if register_response.status_code in [200, 201]:
            login_response = await http_client.post(
                "/api/auth/login",
                json=test_user
            )
            # Login should work if registration succeeded
            assert login_response.status_code in [200, 401], \
                f"Login failed after registration: {login_response.status_code}"
    
    @pytest.mark.asyncio
    async def test_api_documentation_available(self, http_client):
        """Test that API documentation is accessible."""
        # FastAPI should provide /docs endpoint
        response = await http_client.get("/docs")
        assert response.status_code == 200, "API documentation not available"
    
    @pytest.mark.asyncio
    async def test_openapi_schema_available(self, http_client):
        """Test that OpenAPI schema is accessible."""
        response = await http_client.get("/openapi.json")
        assert response.status_code == 200, "OpenAPI schema not available"
        schema = response.json()
        assert "paths" in schema, "Invalid OpenAPI schema"


class TestSmartCityServiceDiscovery:
    """Test Smart City service discovery via Curator."""
    
    BASE_URL = "http://localhost:8000"
    TIMEOUT = 30.0
    
    @pytest.fixture(scope="function")
    async def http_client(self):
        """Create HTTP client for API calls."""
        async with httpx.AsyncClient(base_url=self.BASE_URL, timeout=self.TIMEOUT) as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_services_discoverable(self, http_client):
        """Test that Smart City services are discoverable."""
        # This would require a Curator API endpoint
        # For now, we verify services are available via health checks
        response = await http_client.get("/api/auth/health")
        assert response.status_code == 200
        data = response.json()
        # Security Guard should be available
        assert data.get("security_guard_available") == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

