#!/usr/bin/env python3
"""
Global Test Configuration

Provides real test fixtures and configuration for testing the entire platform
using real infrastructure with isolated test data.
"""

import pytest
import asyncio
import os
import sys
import tempfile
import shutil
from typing import AsyncGenerator, Dict, Any
from pathlib import Path

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

# Import real platform components
try:
    from config.environment_loader import EnvironmentLoader
except ImportError:
    EnvironmentLoader = None

try:
    from foundations.infrastructure_foundation.abstractions.supabase_metadata_abstraction import SupabaseMetadataAbstraction
except ImportError:
    SupabaseMetadataAbstraction = None

try:
    from foundations.utility_foundation.utilities.tenant.tenant_management_utility import TenantManagementUtility
except ImportError:
    TenantManagementUtility = None

try:
    from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import SecurityAuthorizationUtility
except ImportError:
    SecurityAuthorizationUtility = None

try:
    from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
except ImportError:
    PublicWorksFoundationService = None

try:
    from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
except ImportError:
    CuratorFoundationService = None

# =============================================================================
# GLOBAL TEST CONFIGURATION
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_environment():
    """Setup test environment for all layers."""
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "INFO"
    
    yield
    
    # Cleanup test environment
    test_env_vars = ["ENVIRONMENT", "LOG_LEVEL"]
    for var in test_env_vars:
        if var in os.environ:
            del os.environ[var]

@pytest.fixture(scope="session")
def test_config_path():
    """Get path to test configuration file."""
    return os.path.join(os.path.dirname(__file__), '../symphainy-platform/config/test.env')

# =============================================================================
# REAL INFRASTRUCTURE FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
async def real_environment_loader(test_config_path):
    """Real EnvironmentLoader with test configuration."""
    if EnvironmentLoader is None:
        pytest.skip("EnvironmentLoader not available")
    loader = EnvironmentLoader(test_config_path)
    return loader

@pytest.fixture(scope="session")
async def real_supabase_abstraction(real_environment_loader):
    """Real Supabase abstraction with test database."""
    if SupabaseMetadataAbstraction is None:
        pytest.skip("SupabaseMetadataAbstraction not available")
    config = real_environment_loader.get_external_services_config()["supabase"]
    abstraction = SupabaseMetadataAbstraction(
        config["url"], 
        config["key"], 
        multi_tenant_enabled=True
    )
    return abstraction

@pytest.fixture(scope="session")
async def real_tenant_management_utility(real_environment_loader):
    """Real TenantManagementUtility with test configuration."""
    if TenantManagementUtility is None:
        pytest.skip("TenantManagementUtility not available")
    utility = TenantManagementUtility(real_environment_loader)
    return utility

@pytest.fixture(scope="session")
async def real_security_service():
    """Real SecurityAuthorizationUtility for testing."""
    if SecurityAuthorizationUtility is None:
        pytest.skip("SecurityAuthorizationUtility not available")
    service = SecurityAuthorizationUtility("test_service")
    return service

# =============================================================================
# REAL FOUNDATION FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
async def real_public_works_foundation(real_environment_loader, real_security_service):
    """Real PublicWorksFoundation with real infrastructure."""
    # Note: We'll need to provide real infrastructure foundation
    # For now, we'll create with None and let individual tests handle it
    foundation = PublicWorksFoundationService(
        utility_foundation=None,  # Will be provided by individual tests
        curator_foundation=None,  # Will be provided by individual tests
        infrastructure_foundation=None,  # Will be provided by individual tests
        env_loader=real_environment_loader,
        security_guard_client=None  # Will be provided by individual tests
    )
    return foundation

@pytest.fixture(scope="session")
async def real_pattern_validation_service(real_environment_loader, real_security_service):
    """Real PatternValidationService with test configuration."""
    service = PatternValidationService(
        utility_foundation=None,  # Will be provided by individual tests
        env_loader=real_environment_loader,
        security_service=real_security_service
    )
    return service

# =============================================================================
# TEST DATA FIXTURES
# =============================================================================

@pytest.fixture(scope="function")
def test_tenant_data():
    """Test tenant data for testing."""
    return {
        "id": "test_tenant_123",
        "name": "Test Tenant",
        "type": "organization",
        "status": "active",
        "admin_user_id": "test_admin_123",
        "admin_email": "admin@testtenant.com",
        "max_users": 50,
        "features": ["basic_analytics", "file_upload", "team_collaboration", "advanced_insights"]
    }

@pytest.fixture(scope="function")
def test_user_context():
    """Test user context for testing."""
    return {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "full_name": "Test User",
        "session_id": "test_session_123",
        "permissions": ["user"],
        "tenant_id": "test_tenant_123",
        "request_id": "test_request_123",
        "timestamp": "2025-01-01T00:00:00Z"
    }

@pytest.fixture(scope="function")
def test_file_data():
    """Test file data for testing."""
    return {
        "file_id": "test_file_123",
        "filename": "test_document.pdf",
        "content_type": "application/pdf",
        "size": 1024,
        "tenant_id": "test_tenant_123",
        "user_id": "test_user_123"
    }

# =============================================================================
# TEST UTILITIES
# =============================================================================

@pytest.fixture(scope="function")
def test_temp_directory():
    """Create temporary directory for test files."""
    temp_dir = tempfile.mkdtemp(prefix="symphainy_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="function")
def test_database_cleanup():
    """Cleanup test database after tests."""
    # This will be implemented when we have real database tests
    yield
    # Cleanup logic will go here

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest with test-specific settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "contract: mark test as a contract test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "contract" in str(item.fspath):
            item.add_marker(pytest.mark.contract)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

# =============================================================================
# TEST HELPERS
# =============================================================================

class TestHelpers:
    """Helper functions for tests."""
    
    @staticmethod
    def create_test_tenant(tenant_type: str = "organization") -> Dict[str, Any]:
        """Create test tenant data."""
        return {
            "id": f"test_tenant_{tenant_type}_123",
            "name": f"Test {tenant_type.title()} Tenant",
            "type": tenant_type,
            "status": "active",
            "admin_user_id": f"test_admin_{tenant_type}_123",
            "admin_email": f"admin@{tenant_type}.com",
            "max_users": 50 if tenant_type == "organization" else 1,
            "features": ["basic_analytics", "file_upload"]
        }
    
    @staticmethod
    def create_test_user_context(tenant_id: str = "test_tenant_123") -> Dict[str, Any]:
        """Create test user context."""
        return {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "full_name": "Test User",
            "session_id": "test_session_123",
            "permissions": ["user"],
            "tenant_id": tenant_id,
            "request_id": "test_request_123",
            "timestamp": "2025-01-01T00:00:00Z"
        }

@pytest.fixture
def test_helpers():
    """Provide test helpers."""
    return TestHelpers()




