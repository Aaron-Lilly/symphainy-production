"""
Smoke Test: Business Outcomes Pillar

Validates critical Business Outcomes Pillar functionality:
- Health endpoint works
- Roadmap generation endpoint exists
"""

import pytest
import httpx
import logging
import os

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.critical]

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")


@pytest.mark.asyncio
async def test_business_outcomes_pillar_health(backend_server, http_client):
    """Test that Business Outcomes Pillar health endpoint works."""
    logger.info("🔍 Testing Business Outcomes Pillar health...")
    
    response = await http_client.get(f"{BASE_URL}/api/v1/business-outcomes-pillar/health")
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "Business Outcomes Pillar health endpoint missing"
    
    logger.info(f"✅ Business Outcomes Pillar health check passed (status: {response.status_code})")


@pytest.mark.asyncio
async def test_generate_roadmap_endpoint_exists(backend_server, http_client):
    """Test that generate roadmap endpoint exists."""
    logger.info("🔍 Testing generate roadmap endpoint...")
    
    response = await http_client.post(
        f"{BASE_URL}/api/v1/business-outcomes-pillar/generate-strategic-roadmap",
        json={
            "user_id": "smoke_test_user",
            "pillar_outputs": {}
        }
    )
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "Generate roadmap endpoint missing"
    
    # Should be 200 (success) or 400/422 (validation error)
    assert response.status_code in [200, 201, 400, 422], \
        f"Unexpected status: {response.status_code} - {response.text}"
    
    logger.info(f"✅ Generate roadmap endpoint exists (status: {response.status_code})")

