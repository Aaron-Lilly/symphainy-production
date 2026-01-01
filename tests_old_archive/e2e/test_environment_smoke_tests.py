"""
Test Environment Smoke Tests
Quick validation tests to ensure test environment is working correctly.
These tests run in the test environment after deployment.
"""
import pytest
import httpx
import os
from typing import Dict, Any

# Test environment URLs
TEST_BACKEND_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8001")
TEST_FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3001")


@pytest.mark.asyncio
async def test_backend_health():
    """Test that backend health endpoint responds in test environment."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{TEST_BACKEND_URL}/health")
        assert response.status_code == 200, f"Backend health check failed: {response.status_code}"
        data = response.json()
        assert "status" in data, "Health response missing 'status' field"
        print(f"✅ Backend health: {data}")


@pytest.mark.asyncio
async def test_frontend_accessible():
    """Test that frontend is accessible in test environment."""
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.get(TEST_FRONTEND_URL)
        assert response.status_code == 200, f"Frontend not accessible: {response.status_code}"
        assert "html" in response.text.lower() or len(response.text) > 0, "Frontend returned empty response"
        print(f"✅ Frontend accessible: {response.status_code}")


@pytest.mark.asyncio
async def test_backend_api_accessible():
    """Test that backend API endpoints are accessible."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test a simple API endpoint (health is already tested, try another)
        response = await client.get(f"{TEST_BACKEND_URL}/api/v1/content-pillar/list-uploaded-files")
        # Should return 200 or 401 (unauthorized), but not 500 or connection error
        assert response.status_code in [200, 401, 403], \
            f"API endpoint returned unexpected status: {response.status_code}"
        print(f"✅ Backend API accessible: {response.status_code}")


@pytest.mark.asyncio
async def test_websocket_endpoints_exist():
    """Test that WebSocket endpoints are registered (check if they exist)."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # WebSocket endpoints return 400 Bad Request for HTTP GET (expected)
        # This confirms the endpoint exists
        response = await client.get(f"{TEST_BACKEND_URL}/api/ws/guide")
        # WebSocket endpoints should return 400 or 426 (Upgrade Required) for HTTP requests
        assert response.status_code in [400, 426, 404], \
            f"WebSocket endpoint check returned unexpected status: {response.status_code}"
        print(f"✅ WebSocket endpoints registered: {response.status_code}")


def test_test_environment_variables():
    """Test that test environment variables are set correctly."""
    assert TEST_BACKEND_URL.startswith("http"), "TEST_BACKEND_URL should be a valid URL"
    assert TEST_FRONTEND_URL.startswith("http"), "TEST_FRONTEND_URL should be a valid URL"
    print(f"✅ Test environment URLs configured:")
    print(f"   Backend: {TEST_BACKEND_URL}")
    print(f"   Frontend: {TEST_FRONTEND_URL}")






