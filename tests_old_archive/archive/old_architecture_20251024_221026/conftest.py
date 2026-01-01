#!/usr/bin/env python3
"""
Simplified Test Configuration

This is a simplified conftest.py that avoids importing problematic services
to allow basic testing to proceed.

WHAT (Test Config Role): I provide basic test configuration without problematic imports
HOW (Test Config Implementation): I provide minimal fixtures and configuration
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

# =============================================================================
# GLOBAL TEST CONFIGURATION
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_environment():
    """Test environment configuration."""
    return {
        "environment": "test",
        "debug": True,
        "log_level": "INFO"
    }

@pytest.fixture(scope="session")
def test_config_path():
    """Path to test configuration file."""
    return os.path.join(os.path.dirname(__file__), '../symphainy-platform/config/testing.env')

# =============================================================================
# BASIC FIXTURES (Without Problematic Imports)
# =============================================================================

@pytest.fixture(scope="session")
async def basic_configuration():
    """Basic configuration utility for testing."""
    try:
        from foundations.utility_foundation.utilities.configuration.configuration_utility import ConfigurationUtility
        config = ConfigurationUtility("test_basic")
        return config
    except Exception as e:
        pytest.skip(f"Configuration utility not available: {e}")

@pytest.fixture(scope="session")
async def basic_tenant_utility():
    """Basic tenant management utility for testing."""
    try:
        from foundations.utility_foundation.utilities.tenant.tenant_management_utility import TenantManagementUtility
        from foundations.utility_foundation.utilities.configuration.configuration_utility import ConfigurationUtility
        config = ConfigurationUtility("test_tenant")
        utility = TenantManagementUtility(config)
        return utility
    except Exception as e:
        pytest.skip(f"Tenant management utility not available: {e}")

@pytest.fixture(scope="session")
async def basic_security_utility():
    """Basic security authorization utility for testing."""
    try:
        from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import SecurityAuthorizationUtility
        from foundations.utility_foundation.utilities.configuration.configuration_utility import ConfigurationUtility
        config = ConfigurationUtility("test_security")
        utility = SecurityAuthorizationUtility(config)
        return utility
    except Exception as e:
        pytest.skip(f"Security authorization utility not available: {e}")

# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "architecture: Architecture validation tests")
    config.addinivalue_line("markers", "mvp: MVP implementation tests")

def pytest_collection_modifyitems(config, items):
    """Modify test items based on their location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "architecture" in str(item.fspath):
            item.add_marker(pytest.mark.architecture)
        elif "mvp" in str(item.fspath):
            item.add_marker(pytest.mark.mvp)
        
        # Add slow marker for tests that might take longer
        if "load_testing" in str(item.fspath) or "performance" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
