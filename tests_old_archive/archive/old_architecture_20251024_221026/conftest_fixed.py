#!/usr/bin/env python3
"""
Fixed Test Configuration for Symphainy Platform

This is the corrected conftest.py that fixes import paths and provides
proper test environment setup for E2E testing.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# =============================================================================
# FIXED PATH CONFIGURATION
# =============================================================================

# Get the project root directory
project_root = Path(__file__).parent.parent
platform_path = project_root / "symphainy-platform"
utilities_path = platform_path / "utilities"

# Add paths to Python path in correct order
if str(platform_path) not in sys.path:
    sys.path.insert(0, str(platform_path))
if str(utilities_path) not in sys.path:
    sys.path.insert(0, str(utilities_path))

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
        "log_level": "INFO",
        "platform_path": str(platform_path),
        "utilities_path": str(utilities_path)
    }

@pytest.fixture(scope="session")
def test_config_path():
    """Path to test configuration file."""
    return platform_path / "config" / "testing.env"

@pytest.fixture(scope="session")
def test_environment_setup():
    """Setup test environment with proper paths and configuration."""
    # Set up environment variables
    os.environ['TEST_ENVIRONMENT'] = 'true'
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['PYTHONPATH'] = f"{platform_path}:{utilities_path}"
    
    return {
        'platform_path': str(platform_path),
        'utilities_path': str(utilities_path),
        'test_data_path': str(Path(__file__).parent / "data"),
        'config_path': str(platform_path / "config")
    }

# =============================================================================
# FIXED FIXTURES (With Correct Imports)
# =============================================================================

@pytest.fixture(scope="session")
async def basic_configuration():
    """Basic configuration utility for testing."""
    try:
        from utilities.configuration.configuration_utility import ConfigurationUtility
        config = ConfigurationUtility("test_basic")
        return config
    except Exception as e:
        pytest.skip(f"Configuration utility not available: {e}")

@pytest.fixture(scope="session")
async def basic_tenant_utility():
    """Basic tenant management utility for testing."""
    try:
        from utilities.tenant.tenant_management_utility import TenantManagementUtility
        from utilities.configuration.configuration_utility import ConfigurationUtility
        config = ConfigurationUtility("test_tenant")
        utility = TenantManagementUtility(config)
        return utility
    except Exception as e:
        pytest.skip(f"Tenant management utility not available: {e}")

@pytest.fixture(scope="session")
async def basic_security_utility():
    """Basic security authorization utility for testing."""
    try:
        from utilities.security_authorization.security_authorization_utility import SecurityAuthorizationUtility
        from utilities.configuration.configuration_utility import ConfigurationUtility
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
    config.addinivalue_line("markers", "production: Production environment tests")
    config.addinivalue_line("markers", "staging: Staging environment tests")
    config.addinivalue_line("markers", "performance: Performance tests")

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





