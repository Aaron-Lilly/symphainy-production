"""
Smoke Test: Operations Pillar

Validates critical Operations Pillar functionality:
- Health endpoint works
- SOP creation endpoint exists
- Workflow creation endpoint exists
"""

import pytest
import httpx
import logging
import os

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.critical]

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")


@pytest.mark.asyncio
async def test_operations_pillar_health(backend_server, http_client):
    """Test that Operations Pillar health endpoint works."""
    logger.info("🔍 Testing Operations Pillar health...")
    
    response = await http_client.get(f"{BASE_URL}/api/v1/operations-pillar/health")
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "Operations Pillar health endpoint missing"
    
    logger.info(f"✅ Operations Pillar health check passed (status: {response.status_code})")


@pytest.mark.asyncio
async def test_create_sop_endpoint_exists(backend_server, http_client):
    """Test that create SOP endpoint exists."""
    logger.info("🔍 Testing create SOP endpoint...")
    
    response = await http_client.post(
        f"{BASE_URL}/api/v1/operations-pillar/create-standard-operating-procedure",
        json={
            "user_id": "smoke_test_user",
            "title": "Test SOP",
            "description": "Test description"
        }
    )
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "Create SOP endpoint missing"
    
    # Should be 200 (success) or 400/422 (validation error)
    assert response.status_code in [200, 201, 400, 422], \
        f"Unexpected status: {response.status_code} - {response.text}"
    
    logger.info(f"✅ Create SOP endpoint exists (status: {response.status_code})")


@pytest.mark.asyncio
async def test_create_workflow_endpoint_exists(backend_server, http_client):
    """Test that create workflow endpoint exists."""
    logger.info("🔍 Testing create workflow endpoint...")
    
    response = await http_client.post(
        f"{BASE_URL}/api/v1/operations-pillar/create-workflow",
        json={
            "user_id": "smoke_test_user",
            "name": "Test Workflow",
            "description": "Test description"
        }
    )
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "Create workflow endpoint missing"
    
    # Should be 200 (success) or 400/422 (validation error)
    assert response.status_code in [200, 201, 400, 422], \
        f"Unexpected status: {response.status_code} - {response.text}"
    
    logger.info(f"✅ Create workflow endpoint exists (status: {response.status_code})")

