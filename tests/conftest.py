"""
Global pytest configuration and shared fixtures for all test layers.

This file provides:
- Global pytest configuration
- Shared fixtures for common test scenarios
- Test utilities and helpers
- Infrastructure safety checks

NOTE: Python path is configured in pytest.ini via the 'pythonpath' option.
We also ensure the path is set here as a fallback for reliability.
This MUST happen before any other imports that depend on the platform code.
"""

# CRITICAL: Set up Python path BEFORE any other imports
# This ensures imports from symphainy-platform work even if pytest.ini doesn't apply
import sys
from pathlib import Path

# Resolve paths relative to this conftest.py file
_tests_dir = Path(__file__).parent.resolve()
_platform_dir = _tests_dir.parent / "symphainy-platform"
if _platform_dir.exists() and str(_platform_dir) not in sys.path:
    sys.path.insert(0, str(_platform_dir))

# Now safe to import other modules
import pytest
import asyncio
import os
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from unittest.mock import Mock, AsyncMock

# Pytest hook to ensure path is set before test collection
def pytest_configure(config):
    """Configure pytest - ensure Python path is set before test collection."""
    # Double-check path is set (in case pytest.ini didn't work)
    _tests_dir = Path(__file__).parent.resolve()
    _platform_dir = _tests_dir.parent / "symphainy-platform"
    if _platform_dir.exists() and str(_platform_dir) not in sys.path:
        sys.path.insert(0, str(_platform_dir))

# Import test configuration
# Ensure tests directory is in path for config imports
_test_dir_str = str(_tests_dir)
if _test_dir_str not in sys.path:
    sys.path.insert(0, _test_dir_str)

try:
    from config.test_config import TestConfig
except ImportError:
    # Fallback: use direct file import
    import importlib.util
    _config_file = _tests_dir / "config" / "test_config.py"
    if _config_file.exists():
        spec = importlib.util.spec_from_file_location("config.test_config", _config_file)
        test_config_module = importlib.util.module_from_spec(spec)
        sys.modules["config.test_config"] = test_config_module
        spec.loader.exec_module(test_config_module)
        TestConfig = test_config_module.TestConfig
    else:
        raise ImportError(f"Could not find config/test_config.py in {_tests_dir}")

# Path is configured in pytest.ini - no manipulation needed
project_root = Path(__file__).parent.parent / "symphainy-platform"

logger = logging.getLogger(__name__)

# Validate real infrastructure configuration at module load
if TestConfig.USE_REAL_INFRASTRUCTURE:
    missing = TestConfig.get_missing_infrastructure()
    if missing:
        logger.warning(
            f"⚠️  Real infrastructure enabled but missing configuration: {', '.join(missing)}\n"
            f"   Set environment variables or disable with TEST_USE_REAL_INFRASTRUCTURE=false"
        )

# Critical environment variables that must NEVER be modified in tests
CRITICAL_ENV_VARS = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GCLOUD_PROJECT",
    "GOOGLE_CLOUD_PROJECT",
    "GCLOUD_CONFIG",
    "CLOUDSDK_CONFIG",
]


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def project_root_path():
    """Return project root path as Path object."""
    return project_root


# ============================================================================
# USER CONTEXT FIXTURES
# ============================================================================

@pytest.fixture
def user_context():
    """Standard user context for testing."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_456",
        "permissions": ["read", "write", "execute"],
        "roles": ["user", "admin"],
        "email": "testuser@symphainy.com",
    }


@pytest.fixture
def admin_user_context():
    """Admin user context for testing."""
    return {
        "user_id": "admin_user_123",
        "tenant_id": "test_tenant_456",
        "permissions": ["read", "write", "execute", "admin"],
        "roles": ["admin", "super_admin"],
        "email": "admin@symphainy.com",
    }


@pytest.fixture
def invalid_user_context():
    """User context with no permissions."""
    return {
        "user_id": "restricted_user_123",
        "tenant_id": "test_tenant_456",
        "permissions": [],
        "roles": ["viewer"],
        "email": "restricted@symphainy.com",
    }


# ============================================================================
# DI CONTAINER FIXTURES
# ============================================================================

@pytest.fixture
def mock_di_container():
    """Mock DI Container for unit tests."""
    container = Mock()
    container.get_logger = Mock(return_value=logging.getLogger("test"))
    container.get_config_adapter = Mock(return_value=Mock())
    container.get_service = Mock(return_value=Mock())
    return container


@pytest.fixture
async def di_container():
    """
    Real DI Container for integration tests.
    
    Uses real infrastructure when TEST_USE_REAL_INFRASTRUCTURE=true (default).
    """
    from foundations.di_container.di_container_service import (
        DIContainerService,
    )
    
    # Set TEST_MODE to enable test Supabase credentials
    if TestConfig.USE_REAL_INFRASTRUCTURE and TestConfig.SUPABASE_URL:
        os.environ["TEST_MODE"] = "true"
        # Override with test Supabase credentials if available
        if TestConfig.SUPABASE_URL:
            os.environ["SUPABASE_URL"] = TestConfig.SUPABASE_URL
        if TestConfig.SUPABASE_ANON_KEY:
            os.environ["SUPABASE_ANON_KEY"] = TestConfig.SUPABASE_ANON_KEY
        if TestConfig.SUPABASE_SERVICE_KEY:
            os.environ["SUPABASE_SERVICE_KEY"] = TestConfig.SUPABASE_SERVICE_KEY
    
    container = DIContainerService(realm_name="test")
    # DIContainerService initializes itself in __init__, no separate initialize() call needed
    
    yield container
    
    # Cleanup
    if hasattr(container, "shutdown"):
        await container.shutdown()
    
    # Restore environment
    if "TEST_MODE" in os.environ:
        del os.environ["TEST_MODE"]


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def mock_config_adapter():
    """Mock ConfigAdapter for unit tests."""
    config = Mock()
    config.get = Mock(return_value=None)
    config.get_int = Mock(return_value=0)
    config.get_bool = Mock(return_value=False)
    config.get_float = Mock(return_value=0.0)
    return config


@pytest.fixture
def test_config():
    """Test configuration values."""
    return {
        "ARANGO_URL": os.getenv("TEST_ARANGO_URL", "http://localhost:8529"),
        "ARANGO_DB": os.getenv("TEST_ARANGO_DB", "symphainy_test"),
        "REDIS_URL": os.getenv("TEST_REDIS_URL", "redis://localhost:6379"),
        "CONSUL_HOST": os.getenv("TEST_CONSUL_HOST", "localhost"),
        "CONSUL_PORT": int(os.getenv("TEST_CONSUL_PORT", "8500")),
        "ENVIRONMENT": "test",
    }


# ============================================================================
# FOUNDATION SERVICE FIXTURES
# ============================================================================

@pytest.fixture
async def public_works_foundation(di_container):
    """
    Public Works Foundation Service fixture.
    
    Uses real infrastructure adapters when TEST_USE_REAL_INFRASTRUCTURE=true (default).
    """
    from foundations.public_works_foundation.public_works_foundation_service import (
        PublicWorksFoundationService,
    )
    
    # Configure LLM for real but cheaper models if enabled
    if TestConfig.USE_REAL_LLM and not TestConfig.USE_MOCK_LLM:
        llm_config = TestConfig.get_llm_config()
        if llm_config["openai"]["api_key"]:
            os.environ["LLM_OPENAI_API_KEY"] = llm_config["openai"]["api_key"]
            os.environ["OPENAI_API_KEY"] = llm_config["openai"]["api_key"]
            # Use cheaper model for testing
            os.environ["LLM_MODEL"] = llm_config["openai"]["model"]
        if llm_config["anthropic"]["api_key"]:
            os.environ["ANTHROPIC_API_KEY"] = llm_config["anthropic"]["api_key"]
            os.environ["LLM_MODEL"] = llm_config["anthropic"]["model"]
    
    foundation = PublicWorksFoundationService(di_container)
    await foundation.initialize()
    
    yield foundation
    
    # Cleanup
    if hasattr(foundation, "shutdown"):
        await foundation.shutdown()


@pytest.fixture
async def curator_foundation(di_container):
    """Curator Foundation Service fixture."""
    from foundations.curator_foundation.curator_foundation_service import (
        CuratorFoundationService,
    )
    
    foundation = CuratorFoundationService(di_container)
    await foundation.initialize()
    
    yield foundation
    
    # Cleanup
    if hasattr(foundation, "shutdown"):
        await foundation.shutdown()


# ============================================================================
# SMART CITY SERVICE FIXTURES
# ============================================================================

@pytest.fixture
async def librarian_service(di_container):
    """Librarian Service fixture."""
    from backend.smart_city.services.librarian.librarian_service import (
        LibrarianService,
    )
    
    service = LibrarianService(di_container)
    await service.initialize()
    
    yield service
    
    # Cleanup
    if hasattr(service, "shutdown"):
        await service.shutdown()


@pytest.fixture
async def data_steward_service(di_container):
    """Data Steward Service fixture."""
    from backend.smart_city.services.data_steward.data_steward_service import (
        DataStewardService,
    )
    
    service = DataStewardService(di_container)
    await service.initialize()
    
    yield service
    
    # Cleanup
    if hasattr(service, "shutdown"):
        await service.shutdown()


@pytest.fixture
async def post_office_service(di_container):
    """Post Office Service fixture with WebSocket Gateway."""
    from backend.smart_city.services.post_office.post_office_service import PostOfficeService
    
    service = PostOfficeService(di_container)
    await service.initialize()
    
    yield service
    
    # Cleanup
    if hasattr(service, "shutdown"):
        await service.shutdown()


@pytest.fixture
async def traffic_cop_service(di_container, public_works_foundation):
    """Traffic Cop Service fixture (for session validation)."""
    from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
    
    # Public Works Foundation must be initialized first (Traffic Cop needs session abstraction)
    service = TrafficCopService(di_container)
    await service.initialize()
    
    yield service
    
    # Cleanup
    if hasattr(service, "shutdown"):
        await service.shutdown()


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_file_data():
    """Sample file data for testing."""
    return {
        "filename": "test_file.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "size": 1024,
        "data": b"sample file data",
    }


@pytest.fixture
def sample_structured_data():
    """Sample structured data for testing."""
    return {
        "columns": ["id", "name", "value"],
        "rows": [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
        ],
    }


@pytest.fixture
def sample_unstructured_data():
    """Sample unstructured data for testing."""
    return {
        "text": "This is a sample document for testing purposes.",
        "metadata": {
            "title": "Test Document",
            "author": "Test Author",
            "date": "2025-01-01",
        },
    }


# ============================================================================
# ASYNC HELPERS
# ============================================================================

@pytest.fixture
def async_helper():
    """Async test helper utilities."""
    class AsyncHelper:
        @staticmethod
        async def wait_for_condition(condition, timeout=5.0, interval=0.1):
            """Wait for a condition to become true."""
            import asyncio
            elapsed = 0.0
            while elapsed < timeout:
                if await condition() if asyncio.iscoroutinefunction(condition) else condition():
                    return True
                await asyncio.sleep(interval)
                elapsed += interval
            return False
    
    return AsyncHelper()


# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

@pytest.fixture(autouse=True)
def preserve_critical_env_vars(monkeypatch):
    """Preserve critical environment variables during tests."""
    preserved = {}
    for var in CRITICAL_ENV_VARS:
        if var in os.environ:
            preserved[var] = os.environ[var]
    
    yield
    
    # Restore preserved variables
    for var, value in preserved.items():
        os.environ[var] = value

