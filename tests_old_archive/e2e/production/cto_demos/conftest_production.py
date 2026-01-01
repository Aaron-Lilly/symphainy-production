"""
Production-specific fixtures for CTO demo tests.

These fixtures assume the platform is already running in containers
and just verify connectivity rather than starting new servers.
"""

import pytest
import os
import requests
from typing import Dict, Any

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")


# Override backend_server and frontend_server to prevent parent conftest from starting new servers
@pytest.fixture(scope="session")
def backend_server():
    """
    Production version - does NOT start a server, just verifies backend is accessible.
    """
    base_url = BASE_URL
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://localhost:8000"
    
    # Verify backend is accessible
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code != 200:
            pytest.fail(f"Backend health check failed: {response.status_code}")
    except Exception as e:
        pytest.fail(f"Backend is not accessible at {base_url}: {e}")
    
    yield base_url


@pytest.fixture(scope="session")
def frontend_server():
    """
    Production version - does NOT start a server, just verifies frontend is accessible.
    """
    frontend_url = FRONTEND_URL
    if not frontend_url or not frontend_url.startswith(("http://", "https://")):
        frontend_url = f"http://{frontend_url}" if frontend_url else "http://localhost:3000"
    
    # Verify frontend is accessible (optional - may not be needed for API tests)
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code not in [200, 404]:  # 404 is OK if frontend is behind a proxy
            pytest.skip(f"Frontend not accessible: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Frontend is not accessible at {frontend_url}: {e}")
    
    yield frontend_url


@pytest.fixture(scope="session")
def production_backend_available():
    """
    Verify that the production backend is available.
    
    This fixture does NOT start a server - it just verifies connectivity.
    """
    # Ensure URL has protocol
    base_url = BASE_URL
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://localhost:8000"
    
    # Check if backend is accessible
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
    """
    Verify that the production frontend is available.
    
    This fixture does NOT start a server - it just verifies connectivity.
    """
    # Ensure URL has protocol
    frontend_url = FRONTEND_URL
    if not frontend_url or not frontend_url.startswith(("http://", "https://")):
        frontend_url = f"http://{frontend_url}" if frontend_url else "http://localhost:3000"
    
    # Check if frontend is accessible (optional - may not be needed for API tests)
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
    """
    Production version of both_servers fixture.
    
    This does NOT start servers - it just verifies that both are accessible.
    Use this for production container testing.
    
    This fixture overrides the parent conftest's both_servers fixture.
    """
    # Both fixtures verify connectivity
    # This fixture just ensures both checks pass
    yield {
        "backend_url": production_backend_available,
        "frontend_url": production_frontend_available
    }

