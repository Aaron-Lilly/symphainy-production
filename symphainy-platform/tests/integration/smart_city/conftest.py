"""
Pytest configuration for Smart City integration tests.

Provides fixtures and setup for integration tests with real infrastructure.
"""

import pytest
import subprocess
import time
import os
from pathlib import Path


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "integration: Integration tests with real infrastructure")
    config.addinivalue_line("markers", "real_infrastructure: Tests that require real infrastructure (Redis, ArangoDB, etc.)")
    config.addinivalue_line("markers", "slow: Slow running tests")


def check_infrastructure_available():
    """Check if infrastructure services are available."""
    # Check if Docker Compose services are running
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=symphainy-", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            services = result.stdout.strip().split('\n')
            services = [s for s in services if s]
            return len(services) > 0
    except Exception:
        pass
    
    return False


@pytest.fixture(scope="session")
def infrastructure_available():
    """Check if infrastructure is available before running tests."""
    available = check_infrastructure_available()
    if not available:
        pytest.skip("Infrastructure not available. Start with: docker-compose -f docker-compose.infrastructure.yml up -d")
    return available

