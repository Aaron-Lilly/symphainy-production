"""
Shared fixtures for smoke tests.

Smoke tests use the backend_server fixture from the main e2e conftest.
"""

import pytest
import httpx
from typing import Dict, Any
import os

# Note: backend_server fixture is available from parent conftest via pytest's fixture discovery

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")


@pytest.fixture
async def http_client(backend_url):
    """Async HTTP client for smoke tests (overrides parent fixture with base_url)."""
    # Use backend_url from parent fixture, ensure it has protocol
    base_url = backend_url
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://localhost:8000"
    
    # Use base_url parameter - paths should be relative (start with /)
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
async def test_user_context() -> Dict[str, Any]:
    """Create a test user context for smoke tests."""
    return {
        "user_id": "smoke_test_user",
        "email": "smoke_test@symphainy.com",
        "name": "Smoke Test User"
    }

