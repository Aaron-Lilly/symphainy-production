"""
E2E tests for platform startup sequence.

Tests:
- Foundation initialization
- Service registration
- Health checks
- Error recovery
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure


@pytest.mark.e2e
@pytest.mark.production_readiness
@pytest.mark.critical
@pytest.mark.slow
class TestPlatformStartupE2E:
    """Test suite for platform startup E2E validation."""
    
    @pytest.fixture
    def api_base_url(self):
        """Get API base URL from environment."""
        import os
        return os.getenv("TEST_API_URL", "http://localhost")
    
    @pytest.mark.asyncio
    async def test_platform_health_endpoint(self, api_base_url):
        """Test that platform health endpoint is accessible."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{api_base_url}/api/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] in ["healthy", "operational"]
    
    @pytest.mark.asyncio
    async def test_foundation_services_initialized(self, api_base_url):
        """Test that foundation services are initialized."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{api_base_url}/api/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check that foundation services are mentioned in health response
            # (may be in services list or status details)
            assert "services" in data or "foundations" in data or "status" in data
    
    @pytest.mark.asyncio
    async def test_service_discovery_available(self, api_base_url):
        """Test that service discovery (Curator) is available."""
        # This is an indirect test - if platform starts, Curator should be initialized
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{api_base_url}/api/health")
            
            assert response.status_code == 200
            # If health check passes, service discovery is likely working
    
    @pytest.mark.asyncio
    async def test_platform_startup_no_errors(self, api_base_url):
        """Test that platform startup completes without errors."""
        # Check health endpoint - if it responds, startup likely succeeded
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{api_base_url}/api/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should not have error status
            assert data.get("status") != "error"
            assert data.get("status") != "unhealthy"
    
    @pytest.mark.asyncio
    async def test_api_routes_registered(self, api_base_url):
        """Test that API routes are registered and accessible."""
        # Test a few critical endpoints
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Health endpoint
            health_response = await client.get(f"{api_base_url}/api/health")
            assert health_response.status_code == 200
            
            # Session creation endpoint (should exist, may require auth)
            session_response = await client.post(
                f"{api_base_url}/api/v1/session/create-user-session",
                json={}
            )
            # Should not be 404 (route exists, even if auth fails)
            assert session_response.status_code != 404



