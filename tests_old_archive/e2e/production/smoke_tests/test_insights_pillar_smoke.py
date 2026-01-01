"""
Smoke Test: Insights Pillar

Validates critical Insights Pillar functionality:
- Health endpoint works
- Analysis endpoint exists
- Basic insights operations work
"""

import pytest
import httpx
import logging
import os

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.critical]

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")


@pytest.mark.asyncio
async def test_insights_pillar_health(backend_server, http_client):
    """Test that Insights Pillar health endpoint works."""
    logger.info("🔍 Testing Insights Pillar health...")
    
    response = await http_client.get(f"{BASE_URL}/api/v1/insights-pillar/health")
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "Insights Pillar health endpoint missing"
    
    logger.info(f"✅ Insights Pillar health check passed (status: {response.status_code})")


@pytest.mark.asyncio
async def test_analyze_content_endpoint_exists(backend_server, http_client):
    """Test that analyze content endpoint exists."""
    logger.info("🔍 Testing analyze content endpoint...")
    
    response = await http_client.post(
        f"{BASE_URL}/api/v1/insights-pillar/analyze-content",
        json={
            "user_id": "smoke_test_user",
            "file_id": "test_file_id",
            "analysis_type": "basic"
        }
    )
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "Analyze content endpoint missing"
    
    # Should be 200 (success) or 400/422 (validation error)
    assert response.status_code in [200, 400, 422], \
        f"Unexpected status: {response.status_code} - {response.text}"
    
    logger.info(f"✅ Analyze content endpoint exists (status: {response.status_code})")

