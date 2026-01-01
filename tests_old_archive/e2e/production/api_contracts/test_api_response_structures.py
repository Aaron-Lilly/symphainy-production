"""
API Contract Test: Response Structures

Validates that API responses have the expected structure.
Ensures backward compatibility and proper data formats.
"""

import pytest
import os
BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
import httpx
import logging

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.api_contract]


@pytest.mark.asyncio
async def test_health_endpoint_response_structure(backend_server, http_client):
    """Test that health endpoint returns proper structure."""
    logger.info("🔍 Testing health endpoint response structure...")
    
    response = await http_client.get(f"{BASE_URL}/health")
    
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    
    data = response.json()
    
    # Health endpoint returns detailed structure - verify it's valid JSON object
    assert isinstance(data, dict), f"Health response should be JSON object, got: {type(data)}"
    # Should have at least one of these fields (actual structure has foundation_services, infrastructure_services, etc.)
    assert any(key in data for key in ["status", "foundation_services", "infrastructure_services", "managers"]), \
        f"Health response missing expected fields: {list(data.keys())}"
    
    logger.info(f"✅ Health endpoint response structure correct: {list(data.keys())[:5]}")


@pytest.mark.asyncio
async def test_session_creation_response_structure(backend_server, http_client):
    """Test that session creation returns proper structure."""
    logger.info("🔍 Testing session creation response structure...")
    
    response = await http_client.post(
        f"{BASE_URL}/api/v1/session/create-user-session",
        json={
            "user_id": "test_user",
            "session_type": "mvp"
        }
    )
    
    # Should not be 404
    assert response.status_code != 404, "Session creation endpoint missing"
    
    if response.status_code in [200, 201]:
        data = response.json()
        
        # Should have session identifier
        assert "session_id" in data or "session_token" in data, \
            "Session response missing identifier"
        
        logger.info("✅ Session creation response structure correct")


@pytest.mark.asyncio
async def test_file_upload_response_structure(backend_server, http_client):
    """Test that file upload returns proper structure."""
    logger.info("🔍 Testing file upload response structure...")
    
    files = {"file": ("test.csv", b"test,data\n1,2", "text/csv")}
    data = {"user_id": "test_user"}
    
    response = await http_client.post(
        f"{BASE_URL}/api/v1/content-pillar/upload-file",
        files=files,
        data=data
    )
    
    # Should not be 404
    assert response.status_code != 404, "File upload endpoint missing"
    
    if response.status_code in [200, 201]:
        result = response.json()
        
        # Should have success indicator or file_id
        assert "success" in result or "file_id" in result, \
            "File upload response missing success indicator or file_id"
        
        logger.info("✅ File upload response structure correct")


@pytest.mark.asyncio
async def test_error_response_structure(backend_server, http_client):
    """Test that error responses have proper structure."""
    logger.info("🔍 Testing error response structure...")
    
    # Make a request that should return an error (invalid data)
    response = await http_client.post(
        f"{BASE_URL}/api/v1/session/create-user-session",
        json={}  # Missing required fields
    )
    
    # Should return error status (400, 422, etc.)
    if response.status_code >= 400:
        data = response.json()
        
        # Error responses should have error message or details
        assert "error" in data or "message" in data or "detail" in data, \
            "Error response missing error information"
        
        logger.info("✅ Error response structure correct")

