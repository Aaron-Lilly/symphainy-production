#!/usr/bin/env python3
"""
Business Enablement Integration Test Fixtures

Provides real infrastructure fixtures for comprehensive integration testing.
Tests all enabling services, orchestrators, content types, and output types.
"""

import pytest
import os
import sys
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from pathlib import Path

# Path is configured in pytest.ini - no manipulation needed
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService


# ============================================================================
# INFRASTRUCTURE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent.parent.parent / "data" / "test_files"


@pytest.fixture(scope="session")
def ensure_test_data_dir(test_data_dir):
    """Ensure test data directory exists."""
    test_data_dir.mkdir(parents=True, exist_ok=True)
    return test_data_dir


@pytest.fixture(scope="session")
async def real_public_works_foundation() -> AsyncGenerator[PublicWorksFoundationService, None]:
    """
    Create Public Works Foundation with real infrastructure.
    
    This is the foundation for all integration tests - it provides real
    infrastructure adapters (ArangoDB, Redis, Meilisearch, Consul, etc.).
    """
    foundation = PublicWorksFoundationService(
        service_name="test_public_works_foundation",
        realm_name="smart_city"
    )
    
    # Initialize with test environment
    config_file = os.path.join(os.path.dirname(__file__), "../../../.env.test")
    if not os.path.exists(config_file):
        config_file = os.path.join(os.path.dirname(__file__), "../../../symphainy-platform/config/development.env")
    
    success = await foundation.initialize_foundation(config_file=config_file)
    
    if not success:
        pytest.skip(
            "Public Works Foundation initialization failed. "
            "Ensure test infrastructure is running: docker-compose -f tests/docker-compose.test.yml up -d"
        )
    
    yield foundation
    
    # Cleanup
    try:
        await foundation.shutdown()
    except Exception:
        pass


@pytest.fixture(scope="session")
async def real_curator_foundation(real_public_works_foundation) -> AsyncGenerator[CuratorFoundationService, None]:
    """Create Curator Foundation with real Public Works Foundation."""
    foundation = CuratorFoundationService(
        service_name="test_curator_foundation",
        realm_name="smart_city",
        di_container=None  # Will be set by DI Container
    )
    
    # Get DI Container from Public Works
    di_container = real_public_works_foundation.di_container
    
    # Initialize Curator
    success = await foundation.initialize_foundation(
        di_container=di_container,
        public_works_foundation=real_public_works_foundation
    )
    
    if not success:
        pytest.skip("Curator Foundation initialization failed")
    
    yield foundation
    
    # Cleanup
    try:
        await foundation.shutdown()
    except Exception:
        pass


@pytest.fixture(scope="session")
async def real_communication_foundation(
    real_public_works_foundation,
    real_curator_foundation
) -> AsyncGenerator[CommunicationFoundationService, None]:
    """Create Communication Foundation with real dependencies."""
    foundation = CommunicationFoundationService(
        service_name="test_communication_foundation",
        realm_name="smart_city",
        di_container=None
    )
    
    di_container = real_public_works_foundation.di_container
    
    success = await foundation.initialize_foundation(
        di_container=di_container,
        public_works_foundation=real_public_works_foundation,
        curator_foundation=real_curator_foundation
    )
    
    if not success:
        pytest.skip("Communication Foundation initialization failed")
    
    yield foundation
    
    # Cleanup
    try:
        await foundation.shutdown()
    except Exception:
        pass


@pytest.fixture(scope="session")
async def real_platform_gateway(
    real_public_works_foundation
) -> AsyncGenerator[PlatformInfrastructureGateway, None]:
    """Create Platform Gateway with real Public Works Foundation."""
    gateway = PlatformInfrastructureGateway(real_public_works_foundation)
    await gateway.initialize()
    
    yield gateway
    
    # Cleanup
    try:
        await gateway.shutdown()
    except Exception:
        pass


@pytest.fixture(scope="session")
async def real_di_container(
    real_public_works_foundation,
    real_curator_foundation,
    real_communication_foundation
) -> AsyncGenerator[DIContainerService, None]:
    """
    Create DI Container with all foundations initialized.
    
    This provides a fully initialized DI Container with:
    - Public Works Foundation
    - Curator Foundation
    - Communication Foundation
    - All utilities
    - All infrastructure adapters
    """
    di_container = real_public_works_foundation.di_container
    
    # DI Container should already have foundations registered
    # Verify they're available
    assert di_container is not None, "DI Container should be available"
    
    yield di_container


# ============================================================================
# BUSINESS ENABLEMENT FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
async def real_delivery_manager(
    real_di_container,
    real_platform_gateway
) -> AsyncGenerator[DeliveryManagerService, None]:
    """
    Create Delivery Manager with real infrastructure.
    
    This is the top-level service that orchestrates all Business Enablement
    capabilities. All integration tests should use this fixture.
    """
    delivery_manager = DeliveryManagerService(
        service_name="DeliveryManagerService",
        realm_name="business_enablement",
        platform_gateway=real_platform_gateway,
        di_container=real_di_container
    )
    
    success = await delivery_manager.initialize()
    
    if not success:
        pytest.skip("Delivery Manager initialization failed")
    
    yield delivery_manager
    
    # Cleanup
    try:
        await delivery_manager.shutdown()
    except Exception:
        pass


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing."""
    return """name,age,city
John,30,New York
Jane,25,San Francisco
Bob,35,Chicago"""


@pytest.fixture
def sample_json_content():
    """Sample JSON content for testing."""
    return {
        "users": [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "San Francisco"},
            {"name": "Bob", "age": 35, "city": "Chicago"}
        ]
    }


@pytest.fixture
def sample_text_content():
    """Sample plain text content for testing."""
    return """This is a sample text document for testing.
It contains multiple lines of text.
We can use this to test text parsing and analysis capabilities."""


@pytest.fixture
def content_types():
    """List of all content types to test."""
    return [
        "csv",
        "xlsx",
        "xls",
        "json",
        "xml",
        "pdf",
        "docx",
        "doc",
        "txt",
        "html",
        "rtf",
        "cbl",
        "cob",
        "png",
        "jpg",
        "pptx",
        "ppt"
    ]


@pytest.fixture
def output_types():
    """List of all output types to test."""
    return [
        "parquet",
        "json_structured",
        "json_chunks"
    ]


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
async def cleanup_test_data(real_di_container):
    """Cleanup test data after tests."""
    yield
    
    # Cleanup can be implemented here if needed
    # For now, we'll rely on test isolation


@pytest.fixture
def assert_service_initialized():
    """Helper to assert service is properly initialized."""
    def _assert(service, service_name: str):
        assert service is not None, f"{service_name} should be initialized"
        assert hasattr(service, 'di_container'), f"{service_name} should have di_container"
        assert hasattr(service, 'logger'), f"{service_name} should have logger"
        assert service.di_container is not None, f"{service_name} di_container should not be None"
    
    return _assert


@pytest.fixture
def assert_result_success():
    """Helper to assert result is successful."""
    def _assert(result: Dict[str, Any], operation: str = "operation"):
        assert result is not None, f"{operation} should return a result"
        assert isinstance(result, dict), f"{operation} result should be a dictionary"
        if "success" in result:
            assert result.get("success") is not False, f"{operation} should succeed: {result.get('error', 'Unknown error')}"
    
    return _assert













