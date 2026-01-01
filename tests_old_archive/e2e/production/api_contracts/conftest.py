"""
Shared fixtures for API contract tests.
"""

import pytest
import httpx
import os

# Note: backend_server fixture is available from parent conftest via pytest's fixture discovery

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")


@pytest.fixture
async def http_client():
    """Async HTTP client for API contract tests."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client

