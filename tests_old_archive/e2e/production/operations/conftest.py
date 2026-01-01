"""
Production Operations E2E Test Fixtures

Uses production containers (does NOT start new servers).
"""

import pytest
import httpx
import os
import requests
from typing import Dict, Any

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://35.215.64.103")
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://35.215.64.103")


@pytest.fixture(scope="session")
def production_backend_available():
    """Verify that the production backend is available."""
    base_url = BASE_URL
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://35.215.64.103"
    
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            yield base_url
        else:
            pytest.fail(f"Backend health check failed: {response.status_code}")
    except Exception as e:
        pytest.fail(f"Backend is not accessible at {base_url}: {e}")


@pytest.fixture(scope="session")
def production_frontend_available():
    """Verify that the production frontend is available."""
    frontend_url = FRONTEND_URL
    if not frontend_url or not frontend_url.startswith(("http://", "https://")):
        frontend_url = f"http://{frontend_url}" if frontend_url else "http://localhost:3000"
    
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code in [200, 404]:  # 404 is OK if frontend is behind a proxy
            yield frontend_url
        else:
            pytest.skip(f"Frontend not accessible: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Frontend is not accessible at {frontend_url}: {e}")


@pytest.fixture(scope="session")
def both_servers(production_backend_available, production_frontend_available):
    """Production version - verifies both servers are accessible."""
    yield {
        "backend_url": production_backend_available,
        "frontend_url": production_frontend_available
    }


@pytest.fixture
def backend_url() -> str:
    """Fixture that provides the backend URL."""
    return BASE_URL


@pytest.fixture
async def http_client(backend_url):
    """Async HTTP client for production tests."""
    base_url = backend_url
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://35.215.64.103"
    
    async with httpx.AsyncClient(base_url=base_url, timeout=60.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
async def test_session(both_servers, production_client) -> Dict[str, Any]:
    """Create a test session for operations tests with proper authentication."""
    # Use production_client to get authenticated token
    token = await production_client.authenticate()
    
    # Create session using authenticated client
    response = await production_client.post(
        "/api/v1/session/create-user-session",
        json={
            "user_id": "operations_test_user",
            "session_type": "mvp"
        }
    )
    
    assert response.status_code in [200, 201], \
        f"Session creation failed: {response.status_code} - {response.text}"
    
    data = response.json()
    
    session_id = (
        data.get("session_id") or 
        data.get("id") or 
        data.get("sessionId") or
        data.get("uuid") or
        f"test_session_{os.urandom(8).hex()}"
    )
    session_token = (
        data.get("session_token") or 
        data.get("token") or 
        data.get("sessionToken") or
        data.get("access_token") or
        token or
        session_id
    )
    
    return {
        "session_id": session_id,
        "session_token": session_token,
        "auth_token": token,  # Add Bearer token for Authorization header
        "user_id": "operations_test_user",
        "raw_response": data
    }
