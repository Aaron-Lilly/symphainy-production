"""
Smoke Test: Platform Health

Validates that the platform infrastructure is healthy and ready.
This is the first test that must pass for any deployment.
"""

import pytest
import httpx
import logging
import os

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.critical]

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")


@pytest.mark.asyncio
async def test_backend_health_endpoint(http_client):
    """Test that backend health endpoint responds correctly."""
    logger.info("🔍 Testing backend health endpoint...")
    
    # Use absolute URL to avoid base_url issues
    response = await http_client.get(f"{BASE_URL}/health")
    
    assert response.status_code == 200, f"Health check failed: {response.status_code} - {response.text}"
    
    data = response.json()
    # Health endpoint returns detailed structure - verify it's valid
    assert isinstance(data, dict), f"Health response should be JSON object, got: {data}"
    # Should have at least one of these fields
    assert any(key in data for key in ["status", "foundation_services", "infrastructure_services", "managers"]), \
        f"Health response missing expected fields: {list(data.keys())}"
    
    logger.info(f"✅ Backend health check passed: {list(data.keys())}")


@pytest.mark.asyncio
async def test_backend_api_accessible(http_client):
    """Test that backend API is accessible and responding."""
    logger.info("🔍 Testing backend API accessibility...")
    
    # Test a simple endpoint that should exist
    response = await http_client.get(f"{BASE_URL}/health")
    
    assert response.status_code == 200, "Backend API not accessible"
    
    logger.info("✅ Backend API is accessible")


@pytest.mark.asyncio
async def test_semantic_api_base_paths(http_client):
    """Test that semantic API base paths are accessible."""
    logger.info("🔍 Testing semantic API base paths...")
    
    # Test that semantic API paths exist (even if they return errors, they should not be 404)
    test_paths = [
        "/api/v1/content-pillar/health",
        "/api/v1/insights-pillar/health",
        "/api/v1/operations-pillar/health",
        "/api/v1/business-outcomes-pillar/health",
    ]
    
    for path in test_paths:
        response = await http_client.get(f"{BASE_URL}{path}")
        # Should not be 404 (endpoint missing)
        assert response.status_code != 404, f"Endpoint missing: {path}"
        logger.info(f"✅ {path} exists (status: {response.status_code})")

