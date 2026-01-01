"""
Global pytest configuration and shared fixtures for all test layers.

This file provides:
- Global pytest configuration
- Shared fixtures for common test scenarios
- Test utilities and helpers
- SSH access protection (prevents VM lockout)
- Infrastructure safety checks

NOTE: Python path is configured in pytest.ini via the 'pythonpath' option.
No need to manipulate sys.path here - pytest handles it automatically.
"""

import pytest
import asyncio
import os
import subprocess
import logging
from typing import AsyncGenerator, Dict, Any
from unittest.mock import Mock, AsyncMock

# Path is configured in pytest.ini - no manipulation needed
# This variable is available for fixtures that need the project root path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

logger = logging.getLogger(__name__)

# Critical GCP environment variables that must NEVER be modified
CRITICAL_GCP_ENV_VARS = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GCLOUD_PROJECT",
    "GOOGLE_CLOUD_PROJECT",
    "GCLOUD_CONFIG",
    "CLOUDSDK_CONFIG"
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
    from pathlib import Path
    return Path(project_root)


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
        "roles": ["user", "admin"]
    }


@pytest.fixture
def admin_user_context():
    """Admin user context for testing."""
    return {
        "user_id": "admin_user_123",
        "tenant_id": "test_tenant_456",
        "permissions": ["read", "write", "execute", "admin"],
        "roles": ["admin", "super_admin"]
    }


@pytest.fixture
def invalid_user_context():
    """User context with no permissions."""
    return {
        "user_id": "restricted_user_123",
        "tenant_id": "test_tenant_456",
        "permissions": [],
        "roles": ["viewer"]
    }


@pytest.fixture
def invalid_tenant_context():
    """User context with invalid tenant."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "invalid_tenant_999",
        "permissions": ["read", "write", "execute"],
        "roles": ["user"]
    }


# ============================================================================
# UTILITY SERVICE MOCKS
# ============================================================================

@pytest.fixture
def mock_telemetry_foundation():
    """Mock TelemetryFoundationService with new methods."""
    telemetry = AsyncMock()
    telemetry.record_platform_operation_event = AsyncMock(return_value=True)
    telemetry.emit_operation_start = AsyncMock(return_value=True)
    telemetry.emit_operation_complete = AsyncMock(return_value=True)
    return telemetry


@pytest.fixture
def mock_health_foundation():
    """Mock HealthFoundationService with new methods."""
    health = AsyncMock()
    health.record_metric = AsyncMock(return_value=True)
    health.record_health_metric = AsyncMock(return_value=True)
    return health


@pytest.fixture
def mock_security_foundation():
    """Mock SecurityFoundationService with new methods."""
    security = AsyncMock()
    security.check_permissions = AsyncMock(return_value=True)
    security.validate_access = AsyncMock(return_value=True)
    return security


@pytest.fixture
def mock_tenant_foundation():
    """Mock TenantFoundationService with new methods."""
    tenant = AsyncMock()
    tenant.validate_tenant_access = AsyncMock(return_value=True)
    tenant.get_tenant_service = Mock(return_value=tenant)
    return tenant


@pytest.fixture
def mock_error_handling_foundation():
    """Mock ErrorHandlingFoundationService with new methods."""
    error_handler = AsyncMock()
    error_handler.handle_error_with_audit = AsyncMock(return_value=True)
    return error_handler


@pytest.fixture
def mock_curator_foundation():
    """Mock CuratorFoundationService with Phase 2 registration support."""
    curator = AsyncMock()
    curator.register_service = AsyncMock(return_value={"success": True})
    curator.get_service = AsyncMock(return_value=None)
    curator.discover_services = AsyncMock(return_value=[])
    return curator


@pytest.fixture
def mock_public_works_foundation():
    """Mock PublicWorksFoundationService."""
    pwf = Mock()
    pwf.is_initialized = True
    pwf.get_tenant_service = Mock(return_value=Mock())
    pwf.get_security_service = Mock(return_value=Mock())
    return pwf


@pytest.fixture
def mock_platform_gateway():
    """Mock PlatformInfrastructureGateway."""
    gateway = Mock()
    gateway.is_initialized = True
    return gateway


@pytest.fixture
def mock_di_container_with_utilities(
    mock_telemetry_foundation,
    mock_health_foundation,
    mock_security_foundation,
    mock_tenant_foundation,
    mock_error_handling_foundation,
    mock_curator_foundation,
    mock_public_works_foundation,
    mock_platform_gateway
):
    """DI Container with all utility foundations properly mocked."""
    container = Mock()
    
    def get_foundation_service(name):
        services = {
            "TelemetryFoundationService": mock_telemetry_foundation,
            "HealthFoundationService": mock_health_foundation,
            "SecurityFoundationService": mock_security_foundation,
            "TenantFoundationService": mock_tenant_foundation,
            "ErrorHandlingFoundationService": mock_error_handling_foundation,
            "CuratorFoundationService": mock_curator_foundation,
            "PlatformInfrastructureGateway": mock_platform_gateway,
            "PublicWorksFoundationService": mock_public_works_foundation,
            "PolicyIntegrationService": Mock(),
            "AGUISchemaRegistry": Mock(),
        }
        return services.get(name)
    
    container.get_foundation_service = Mock(side_effect=get_foundation_service)
    container.get_logger = Mock(return_value=Mock())
    container.get_config = Mock(return_value={})
    
    return container


# ============================================================================
# SSH ACCESS PROTECTION & INFRASTRUCTURE SAFETY
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def protect_critical_env_vars():
    """
    Global fixture that protects critical GCP environment variables.
    Runs automatically for all tests to prevent SSH access issues.
    
    CRITICAL: This prevents modification of GOOGLE_APPLICATION_CREDENTIALS
    which would break SSH access to GCP VMs.
    
    Enhanced with logging to track any modifications (even if restored).
    """
    # Capture original values
    original_values = {}
    for var in CRITICAL_GCP_ENV_VARS:
        original_values[var] = os.environ.get(var)
    
    # Track modifications for logging (even if restored)
    modifications_detected = []
    
    yield
    
    # Verify they weren't modified
    violations = []
    for var in CRITICAL_GCP_ENV_VARS:
        original = original_values[var]
        current = os.environ.get(var)
        if current != original:
            violation_info = {
                "variable": var,
                "original": original,
                "current": current
            }
            violations.append(violation_info)
            modifications_detected.append(violation_info)
            
            # Log warning even if it gets restored (helps identify problematic tests)
            logger.warning(
                f"⚠️  {var} was modified during tests "
                f"(original: {original}, current: {current}). "
                f"This can break SSH access to GCP VMs if not restored."
            )
    
    if violations:
        error_msg = "CRITICAL: Critical GCP environment variables were modified!\n"
        error_msg += "This breaks SSH access to GCP VMs.\n\n"
        for v in violations:
            error_msg += f"  {v['variable']}:\n"
            error_msg += f"    Original: {v['original']}\n"
            error_msg += f"    Current: {v['current']}\n"
        error_msg += "\nFix: Use test-specific credential variables instead.\n"
        error_msg += "Example: Use TEST_GCS_CREDENTIALS instead of GOOGLE_APPLICATION_CREDENTIALS\n"
        error_msg += "\nSee: tests/integration/layer_8_business_enablement/SSH_ACCESS_GUARDRAILS.md"
        pytest.fail(error_msg)
    
    # Log summary if any modifications were detected but restored
    if modifications_detected:
        logger.info(
            f"✅ All critical env vars were restored after tests "
            f"(detected {len(modifications_detected)} temporary modifications)"
        )


@pytest.fixture(scope="session", autouse=True)
def check_vm_resources_before_tests():
    """
    Check VM resources before running tests.
    Alerts if resources are low (could cause SSH issues).
    
    Can be skipped by setting TEST_SKIP_RESOURCE_CHECK=true environment variable.
    """
    # Allow skipping resource check via environment variable
    if os.getenv("TEST_SKIP_RESOURCE_CHECK", "false").lower() == "true":
        logger.warning("⚠️  VM resource check skipped (TEST_SKIP_RESOURCE_CHECK=true)")
        return
    
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        alerts = []
        if cpu_percent > 85:
            alerts.append(f"CPU: {cpu_percent}% (threshold: 85%)")
        if memory.percent > 85:
            alerts.append(f"Memory: {memory.percent}% (threshold: 85%)")
        if disk.percent > 90:
            alerts.append(f"Disk: {disk.percent}% (threshold: 90%)")
        
        if alerts:
            pytest.fail(
                f"VM resources are low before tests:\n{chr(10).join(alerts)}\n"
                f"This may cause SSH access issues if resources are exhausted.\n"
                f"Free up resources before running tests.\n"
                f"Or set TEST_SKIP_RESOURCE_CHECK=true to skip this check."
            )
    except ImportError:
        # psutil not available - skip check
        logger.warning("psutil not available - skipping VM resource check")
    except Exception as e:
        # Don't fail tests if resource check fails
        logger.warning(f"VM resource check failed: {e}")


@pytest.fixture(scope="session", autouse=True)
def check_container_health_before_tests():
    """
    Check container health before running tests.
    Detects restart loops that could cause resource exhaustion.
    """
    try:
        from tests.utils.safe_docker import check_container_status
        
        containers = [
            "symphainy-redis",
            "symphainy-arangodb",
            "symphainy-consul",
            "symphainy-celery-worker",
            "symphainy-celery-beat"
        ]
        
        unhealthy = []
        for container in containers:
            status = check_container_status(container)
            if status.get("restart_count", 0) > 10:
                unhealthy.append(
                    f"{container}: restart_count={status['restart_count']} (possible restart loop)"
                )
            if status.get("failing_streak", 0) > 10:
                unhealthy.append(
                    f"{container}: failing_streak={status['failing_streak']} (health check failing)"
                )
        
        if unhealthy:
            pytest.fail(
                f"Container health issues detected before tests:\n"
                f"{chr(10).join([f'  - {c}' for c in unhealthy])}\n"
                f"This may cause VM resource exhaustion and SSH access issues.\n"
                f"Fix container issues before running tests."
            )
    except ImportError:
        # safe_docker not available - skip check
        logger.warning("safe_docker not available - skipping container health check")
    except Exception as e:
        # Don't fail tests if health check fails (containers might not be running)
        logger.debug(f"Container health check failed: {e}")


# ============================================================================
# TIMEOUT CONFIGURATION (pytest-timeout)
# ============================================================================

def pytest_configure(config):
    """
    Configure pytest-timeout markers.
    
    Registers timeout markers for documentation and IDE support.
    Tests should use @pytest.mark.timeout(seconds) directly.
    """
    # Register timeout markers for documentation
    timeout_markers = {
        'timeout_10': 'Test with 10 second timeout (very fast unit tests)',
        'timeout_30': 'Test with 30 second timeout (fast integration tests)',
        'timeout_60': 'Test with 60 second timeout (default, most tests)',
        'timeout_120': 'Test with 120 second timeout (slower integration tests)',
        'timeout_300': 'Test with 300 second timeout (E2E tests, complex scenarios)',
        'timeout_600': 'Test with 600 second timeout (very long-running tests, rare)',
    }
    
    for marker_name, description in timeout_markers.items():
        config.addinivalue_line('markers', f'{marker_name}: {description}')


def pytest_collection_modifyitems(config, items):
    """
    Automatically apply timeouts based on test markers.
    
    This ensures all tests have timeout protection without requiring
    explicit timeout markers on every test.
    
    Priority:
    1. Explicit timeout markers (timeout_10, timeout_30, etc.) - highest priority
    2. Test type markers (unit, integration, e2e, functional) - automatic assignment
    3. Default timeout (60 seconds) - fallback
    """
    import pytest
    
    # Map test type markers to timeout values
    marker_timeout_map = {
        'unit': 10,           # Unit tests: 10 seconds
        'integration': 60,    # Integration tests: 60 seconds (default)
        'e2e': 300,           # E2E tests: 300 seconds (5 minutes)
        'functional': 120,    # Functional tests: 120 seconds (2 minutes)
        'ai': 300,            # AI tests: 300 seconds (5 minutes)
    }
    
    # Map timeout marker names to timeout values
    timeout_marker_map = {
        'timeout_10': 10,
        'timeout_30': 30,
        'timeout_60': 60,
        'timeout_120': 120,
        'timeout_300': 300,
        'timeout_600': 600,
    }
    
    for item in items:
        # Skip if test already has explicit timeout marker
        has_explicit_timeout = any(
            marker.name.startswith('timeout_') or marker.name == 'timeout'
            for marker in item.iter_markers()
        )
        
        if has_explicit_timeout:
            # Test already has explicit timeout - don't override
            continue
        
        # Check for explicit timeout marker values
        timeout_marker = item.get_closest_marker('timeout')
        if timeout_marker and timeout_marker.args:
            # Test has @pytest.mark.timeout(seconds) - don't override
            continue
        
        # Check timeout_* markers
        for marker_name, timeout_value in timeout_marker_map.items():
            if item.get_closest_marker(marker_name):
                item.add_marker(pytest.mark.timeout(timeout_value))
                break
        else:
            # No explicit timeout marker - check test type markers
            for marker_name, timeout_value in marker_timeout_map.items():
                if item.get_closest_marker(marker_name):
                    item.add_marker(pytest.mark.timeout(timeout_value))
                    break
            # If no markers match, test will use default timeout from pytest.ini (60 seconds)
