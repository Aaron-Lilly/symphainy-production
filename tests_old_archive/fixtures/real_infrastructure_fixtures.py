"""
Real Infrastructure Fixtures for Integration Testing

These fixtures provide real infrastructure adapters and services for testing,
ensuring we catch actual infrastructure issues rather than mock-related problems.
"""

import pytest
import os
import sys
from typing import AsyncGenerator

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../symphainy-platform"))

from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway


@pytest.fixture(scope="session")
def test_env_file():
    """Path to test environment file."""
    return os.path.join(os.path.dirname(__file__), "../../.env.test")


@pytest.fixture(scope="session")
async def real_public_works_foundation(test_env_file) -> AsyncGenerator[PublicWorksFoundationService, None]:
    """
    Create Public Works Foundation with real infrastructure.
    
    This fixture initializes the Public Works Foundation with real adapters
    connecting to test infrastructure (Redis, ArangoDB, Meilisearch, etc.).
    """
    foundation = PublicWorksFoundationService(
        service_name="test_public_works_foundation",
        realm_name="smart_city"
    )
    
    # Initialize with test environment
    config_file = test_env_file if os.path.exists(test_env_file) else ".env"
    success = await foundation.initialize_foundation(config_file=config_file)
    
    if not success:
        pytest.skip("Public Works Foundation initialization failed. Ensure test infrastructure is running.")
    
    yield foundation
    
    # Cleanup
    try:
        await foundation.shutdown()
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture(scope="session")
async def real_platform_gateway(real_public_works_foundation) -> AsyncGenerator[PlatformInfrastructureGateway, None]:
    """
    Create Platform Gateway with real Public Works Foundation.
    
    This fixture provides a Platform Gateway that uses the real Public Works
    Foundation, allowing tests to verify realm access patterns.
    """
    gateway = PlatformInfrastructureGateway(real_public_works_foundation)
    await gateway.initialize()
    
    yield gateway
    
    # Cleanup
    try:
        await gateway.shutdown()
    except Exception:
        pass  # Ignore cleanup errors
