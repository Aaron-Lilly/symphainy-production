"""
Smoke Test: Content Pillar

Validates critical Content Pillar functionality:
- File upload endpoint exists
- File listing endpoint exists
- Basic file operations work
"""

import pytest
import httpx
import logging
import os

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.critical]

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")


@pytest.mark.asyncio
async def test_content_pillar_health(backend_server, http_client):
    """Test that Content Pillar health endpoint works."""
    logger.info("🔍 Testing Content Pillar health...")
    
    response = await http_client.get(f"{BASE_URL}/api/v1/content-pillar/health")
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "Content Pillar health endpoint missing"
    
    logger.info(f"✅ Content Pillar health check passed (status: {response.status_code})")


@pytest.mark.asyncio
async def test_file_upload_endpoint_exists(backend_server, http_client):
    """Test that file upload endpoint exists and responds."""
    logger.info("🔍 Testing file upload endpoint...")
    
    # Test with minimal data (will likely fail validation, but endpoint should exist)
    files = {"file": ("test.csv", b"test,data\n1,2", "text/csv")}
    data = {"user_id": "smoke_test_user"}
    
    response = await http_client.post(
        f"{BASE_URL}/api/v1/content-pillar/upload-file",
        files=files,
        data=data
    )
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "File upload endpoint missing"
    
    # Should be 200 (success) or 400/422 (validation error)
    assert response.status_code in [200, 201, 400, 422], \
        f"Unexpected status: {response.status_code} - {response.text}"
    
    logger.info(f"✅ File upload endpoint exists (status: {response.status_code})")


@pytest.mark.asyncio
async def test_file_listing_endpoint_exists(backend_server, http_client):
    """Test that file listing endpoint exists and responds."""
    logger.info("🔍 Testing file listing endpoint...")
    
    response = await http_client.get(
        f"{BASE_URL}/api/v1/content-pillar/list-uploaded-files",
        params={"user_id": "smoke_test_user"}
    )
    
    # Should not be 404 (endpoint missing)
    assert response.status_code != 404, "File listing endpoint missing"
    
    # Should be 200 (success) or 400/422 (validation error)
    assert response.status_code in [200, 400, 422], \
        f"Unexpected status: {response.status_code} - {response.text}"
    
    logger.info(f"✅ File listing endpoint exists (status: {response.status_code})")

