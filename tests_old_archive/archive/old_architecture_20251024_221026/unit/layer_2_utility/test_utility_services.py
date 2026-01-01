#!/usr/bin/env python3
"""
Layer 3: Utility Services Tests

Tests the individual utility services that make up the utility foundation.

Key Services:
- Error Handler
- Health Service
- Telemetry Service
- Security Service
- Tool Factory
- Logging Service
- Tenant Management Utility
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the platform directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-source/symphainy-platform'))

from foundations.utility_foundation.utilities import (
    get_error_handler, get_health_service, get_logging_service,
    get_telemetry_service, get_security_service, get_tool_factory,
    UserContext, ServiceStatus, ServiceMetrics
)
from foundations.utility_foundation.utilities.tenant.tenant_management_utility import TenantManagementUtility
from foundations.utility_foundation.utilities.security.security_service import SecurityService
from foundations.utility_foundation.utilities.health.health_service import HealthService
from foundations.utility_foundation.utilities.telemetry.telemetry_service import TelemetryService
from foundations.utility_foundation.utilities.error.error_handler import SmartCityErrorHandler
from foundations.utility_foundation.utilities.logging.logging_service import SmartCityLoggingService
from foundations.utility_foundation.utilities.tool_factory.tool_factory_service import ToolFactoryService
from config.environment_loader import EnvironmentLoader
from config import Environment


class TestUtilityServices:
    """Test individual utility services with real implementations."""

    @pytest.fixture
    def env_loader(self):
        """Create Environment Loader instance."""
        return EnvironmentLoader(Environment.TESTING)

    # Error Handler Tests
    @pytest.mark.asyncio
    async def test_error_handler_initialization(self):
        """Test error handler initialization."""
        error_handler = get_error_handler("test_service")
        assert error_handler is not None
        assert hasattr(error_handler, 'handle_error')

    @pytest.mark.asyncio
    async def test_error_handler_functionality(self):
        """Test error handler functionality."""
        error_handler = get_error_handler("test_service")
        
        # Test error handling
        test_error = Exception("Test error")
        result = error_handler.handle_error(test_error)
        assert result is not None
        assert "error_type" in result
        assert "error_message" in result

    # Health Service Tests
    @pytest.mark.asyncio
    async def test_health_service_initialization(self):
        """Test health service initialization."""
        health_service = get_health_service("test_service")
        assert health_service is not None
        assert hasattr(health_service, 'record_health_metric')

    @pytest.mark.asyncio
    async def test_health_service_functionality(self):
        """Test health service functionality."""
        health_service = get_health_service("test_service")
        
        # Test recording health metric
        await health_service.record_health_metric("test_metric", 1.0, {"test": "tag"})
        # Should not raise any exceptions

    # Telemetry Service Tests
    @pytest.mark.asyncio
    async def test_telemetry_service_initialization(self):
        """Test telemetry service initialization."""
        telemetry_service = get_telemetry_service("test_service")
        assert telemetry_service is not None
        assert hasattr(telemetry_service, 'record_metric')

    @pytest.mark.asyncio
    async def test_telemetry_service_functionality(self):
        """Test telemetry service functionality."""
        telemetry_service = get_telemetry_service("test_service")
        
        # Test recording metric
        await telemetry_service.record_metric("test_metric", 1.0, {"test": "tag"})
        # Should not raise any exceptions

    # Security Service Tests
    @pytest.mark.asyncio
    async def test_security_service_initialization(self):
        """Test security service initialization."""
        security_service = get_security_service("test_service")
        assert security_service is not None
        assert hasattr(security_service, 'get_user_context')

    @pytest.mark.asyncio
    async def test_security_service_functionality(self):
        """Test security service functionality."""
        security_service = get_security_service("test_service")
        
        # Test user context creation
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["user"]
        )
        assert user_context is not None
        assert user_context.user_id == "test_user"

    # Tool Factory Tests
    @pytest.mark.asyncio
    async def test_tool_factory_initialization(self):
        """Test tool factory initialization."""
        tool_factory = get_tool_factory()
        assert tool_factory is not None
        assert hasattr(tool_factory, 'get_tool')
        assert hasattr(tool_factory, 'execute_tool')
        assert hasattr(tool_factory, 'discover_tools')

    @pytest.mark.asyncio
    async def test_tool_factory_functionality(self):
        """Test tool factory functionality."""
        tool_factory = get_tool_factory()
        
        # Test tool discovery (may return empty list if no domain managers registered)
        try:
            tools = await tool_factory.discover_tools()
            assert isinstance(tools, list)
        except Exception as e:
            # Expected if no domain managers are registered
            assert "domain manager" in str(e).lower() or "not available" in str(e).lower()

    # Logging Service Tests
    @pytest.mark.asyncio
    async def test_logging_service_initialization(self):
        """Test logging service initialization."""
        logging_service = get_logging_service("test_service")
        assert logging_service is not None
        assert hasattr(logging_service, 'info')
        assert hasattr(logging_service, 'error')
        assert hasattr(logging_service, 'warning')
        assert hasattr(logging_service, 'debug')

    @pytest.mark.asyncio
    async def test_logging_service_functionality(self):
        """Test logging service functionality."""
        logging_service = get_logging_service("test_service")
        
        # Test logging methods
        logging_service.info("Test info message")
        logging_service.error("Test error message")
        logging_service.warning("Test warning message")
        logging_service.debug("Test debug message")
        # Should not raise any exceptions

    # Tenant Management Utility Tests
    @pytest.mark.asyncio
    async def test_tenant_management_utility_initialization(self, env_loader):
        """Test tenant management utility initialization."""
        tenant_utility = TenantManagementUtility(env_loader)
        assert tenant_utility is not None
        assert hasattr(tenant_utility, 'is_multi_tenant_enabled')
        assert hasattr(tenant_utility, 'get_multi_tenant_config')

    @pytest.mark.asyncio
    async def test_tenant_management_utility_functionality(self, env_loader):
        """Test tenant management utility functionality."""
        tenant_utility = TenantManagementUtility(env_loader)
        
        # Test multi-tenant configuration
        multi_tenant_config = tenant_utility.get_multi_tenant_config()
        assert multi_tenant_config is not None
        assert isinstance(multi_tenant_config, dict)
        assert "enabled" in multi_tenant_config
        
        # Test tenant type configuration
        tenant_config = tenant_utility.get_tenant_config("individual")
        assert tenant_config is not None
        assert isinstance(tenant_config, dict)
        assert "max_users" in tenant_config
        assert "features" in tenant_config

    # UserContext Tests
    @pytest.mark.asyncio
    async def test_user_context_creation(self):
        """Test user context creation."""
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["user"],
            tenant_id="test_tenant"
        )
        assert user_context is not None
        assert user_context.user_id == "test_user"
        assert user_context.email == "test@example.com"
        assert user_context.full_name == "Test User"
        assert user_context.session_id == "test_session"
        assert user_context.permissions == ["user"]
        assert user_context.tenant_id == "test_tenant"

    @pytest.mark.asyncio
    async def test_user_context_to_dict(self):
        """Test user context to dictionary conversion."""
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["user"],
            tenant_id="test_tenant"
        )
        
        user_dict = user_context.to_dict()
        assert isinstance(user_dict, dict)
        assert user_dict["user_id"] == "test_user"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["full_name"] == "Test User"
        assert user_dict["session_id"] == "test_session"
        assert user_dict["permissions"] == ["user"]
        assert user_dict["tenant_id"] == "test_tenant"

    # ServiceStatus Tests
    @pytest.mark.asyncio
    async def test_service_status_enum(self):
        """Test service status enum values."""
        assert ServiceStatus.INITIALIZING is not None
        assert ServiceStatus.RUNNING is not None
        assert ServiceStatus.STOPPING is not None
        assert ServiceStatus.STOPPED is not None
        assert ServiceStatus.ERROR is not None

    # ServiceMetrics Tests
    @pytest.mark.asyncio
    async def test_service_metrics_initialization(self):
        """Test service metrics initialization."""
        metrics = ServiceMetrics()
        assert metrics is not None
        assert hasattr(metrics, 'start_time')
        assert hasattr(metrics, 'operation_count')
        assert hasattr(metrics, 'error_count')
        assert hasattr(metrics, 'success_count')

    @pytest.mark.asyncio
    async def test_service_metrics_functionality(self):
        """Test service metrics functionality."""
        metrics = ServiceMetrics()
        
        # Test metrics tracking
        initial_count = metrics.operation_count
        metrics.increment_operation_count()
        assert metrics.operation_count == initial_count + 1
        
        initial_error_count = metrics.error_count
        metrics.increment_error_count()
        assert metrics.error_count == initial_error_count + 1
        
        initial_success_count = metrics.success_count
        metrics.increment_success_count()
        assert metrics.success_count == initial_success_count + 1

    # Integration Tests
    @pytest.mark.asyncio
    async def test_utility_services_integration(self, env_loader):
        """Test that all utility services work together."""
        # Initialize all services
        error_handler = get_error_handler("integration_test")
        health_service = get_health_service("integration_test")
        telemetry_service = get_telemetry_service("integration_test")
        security_service = get_security_service("integration_test")
        tool_factory = get_tool_factory()
        logging_service = get_logging_service("integration_test")
        tenant_utility = TenantManagementUtility(env_loader)
        
        # Test that all services are available
        assert error_handler is not None
        assert health_service is not None
        assert telemetry_service is not None
        assert security_service is not None
        assert tool_factory is not None
        assert logging_service is not None
        assert tenant_utility is not None
        
        # Test integration - should not raise any exceptions
        logging_service.info("Integration test started")
        
        user_context = UserContext(
            user_id="integration_user",
            email="integration@example.com",
            full_name="Integration User",
            session_id="integration_session",
            permissions=["user"],
            tenant_id="integration_tenant"
        )
        
        await health_service.record_health_metric("integration_metric", 1.0, {"test": "integration"})
        await telemetry_service.record_metric("integration_telemetry", 1.0, {"test": "integration"})
        
        multi_tenant_config = tenant_utility.get_multi_tenant_config()
        assert multi_tenant_config is not None
        
        logging_service.info("Integration test completed")

    @pytest.mark.asyncio
    async def test_utility_services_error_handling(self):
        """Test error handling across utility services."""
        error_handler = get_error_handler("error_test")
        logging_service = get_logging_service("error_test")
        
        # Test error handling
        test_error = Exception("Integration test error")
        result = error_handler.handle_error(test_error)
        assert result is not None
        logging_service.error(f"Handled error: {test_error}")
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_utility_services_health_monitoring(self):
        """Test health monitoring across utility services."""
        health_service = get_health_service("health_test")
        telemetry_service = get_telemetry_service("health_test")
        
        # Test health monitoring
        await health_service.record_health_metric("health_test_metric", 1.0, {"test": "health"})
        await telemetry_service.record_metric("health_test_telemetry", 1.0, {"test": "health"})
        # Should not raise any exceptions
