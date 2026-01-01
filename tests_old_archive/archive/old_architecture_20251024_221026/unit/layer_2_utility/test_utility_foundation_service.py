#!/usr/bin/env python3
"""
Layer 3: Utility Foundation Service Tests

Tests the core utility foundation service that provides comprehensive utilities
and common services for all foundation services.

Key Components:
- Utility Foundation Service
- Error Handling
- Health Monitoring
- Telemetry
- Security
- Tool Factory
- Service Registration
- Audit Logging
"""

import pytest
import pytest_asyncio
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the platform directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-source/symphainy-platform'))

from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from foundations.utility_foundation.utilities import UserContext, ServiceStatus, ServiceMetrics
from config.environment_loader import EnvironmentLoader
from config import Environment


class TestUtilityFoundationService:
    """Test Utility Foundation Service with real implementations."""

    @pytest.fixture
    def env_loader(self):
        """Create Environment Loader instance."""
        return EnvironmentLoader(Environment.TESTING)

    @pytest_asyncio.fixture
    async def utility_foundation(self):
        """Create Utility Foundation Service instance."""
        service = UtilityFoundationService()
        await service.initialize()
        return service

    @pytest.mark.asyncio
    async def test_utility_foundation_initialization(self):
        """Test that Utility Foundation Service initializes correctly."""
        service = UtilityFoundationService()
        assert service is not None
        assert service.service_name == "utility_foundation"
        assert service.service_status == ServiceStatus.INITIALIZING
        assert service.is_initialized is False

    @pytest.mark.asyncio
    async def test_utility_foundation_async_initialization(self, utility_foundation):
        """Test that Utility Foundation Service initializes asynchronously."""
        assert utility_foundation is not None
        assert utility_foundation.service_name == "utility_foundation"
        assert utility_foundation.is_initialized is True
        assert utility_foundation.service_status == ServiceStatus.RUNNING

    @pytest.mark.asyncio
    async def test_utilities_initialization(self, utility_foundation):
        """Test that all utilities are properly initialized."""
        assert utility_foundation.logger is not None
        assert utility_foundation.error_handler is not None
        assert utility_foundation.health_service is not None
        assert utility_foundation.telemetry_service is not None
        assert utility_foundation.security_service is not None
        assert utility_foundation.tool_factory is not None

    @pytest.mark.asyncio
    async def test_service_registration(self, utility_foundation):
        """Test service registration functionality."""
        # Test registering a service
        utility_foundation.register_service("test_service", "foundation_service")
        assert "test_service" in utility_foundation.services_registered
        service_info = utility_foundation.services_registered["test_service"]
        assert service_info["type"] == "foundation_service"
        assert "registered_at" in service_info
        assert service_info["status"] == "active"

    @pytest.mark.asyncio
    async def test_utility_usage_tracking(self, utility_foundation):
        """Test utility usage tracking."""
        # Test tracking utility usage
        utility_foundation.track_utility_usage("test_utility")
        assert "test_utility" in utility_foundation.utility_usage_stats
        assert utility_foundation.utility_usage_stats["test_utility"] >= 1

    @pytest.mark.asyncio
    async def test_health_monitoring(self, utility_foundation):
        """Test health monitoring functionality."""
        # Test health check
        health_status = await utility_foundation.health_check()
        assert health_status is not None
        assert isinstance(health_status, dict)
        assert "service" in health_status
        assert health_status["service"] == "utility_foundation"

    @pytest.mark.asyncio
    async def test_telemetry_integration(self, utility_foundation):
        """Test telemetry integration."""
        # Test logging operation with telemetry
        await utility_foundation.log_operation_with_telemetry(
            "test_operation",
            success=True,
            details={"test": "data"}
        )
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_error_handling(self, utility_foundation):
        """Test error handling functionality."""
        # Test error handling with audit
        test_error = Exception("Test error")
        await utility_foundation.handle_error_with_audit(
            test_error,
            context={"test": "context"}
        )
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_security_integration(self, utility_foundation):
        """Test security service integration."""
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

    @pytest.mark.asyncio
    async def test_tool_factory_integration(self, utility_foundation):
        """Test tool factory integration."""
        # Test tool factory availability
        assert utility_foundation.tool_factory is not None
        # Tool factory should be available for MCP client creation

    @pytest.mark.asyncio
    async def test_service_metrics(self, utility_foundation):
        """Test service metrics functionality."""
        # Test service metrics
        assert utility_foundation.service_metrics is not None
        assert isinstance(utility_foundation.service_metrics, ServiceMetrics)

    @pytest.mark.asyncio
    async def test_audit_logging(self, utility_foundation):
        """Test audit logging functionality."""
        # Test audit log
        initial_log_count = len(utility_foundation.audit_log)
        
        # Perform an operation that should be audited
        await utility_foundation.log_operation_with_telemetry(
            "audit_test_operation",
            success=True
        )
        
        # Audit log should have entries (implementation dependent)
        assert isinstance(utility_foundation.audit_log, list)

    @pytest.mark.asyncio
    async def test_health_check_available(self, utility_foundation):
        """Test that health check method is available."""
        assert hasattr(utility_foundation, 'health_check')
        assert callable(utility_foundation.health_check)

    @pytest.mark.asyncio
    async def test_health_check_execution(self, utility_foundation):
        """Test that health check can be executed."""
        health_status = await utility_foundation.health_check()
        assert health_status is not None
        assert isinstance(health_status, dict)
        assert "service" in health_status
        assert health_status["service"] == "utility_foundation"

    @pytest.mark.asyncio
    async def test_service_coordination_structure(self, utility_foundation):
        """Test that service coordination structure is correct."""
        # Test that all required utilities are initialized
        assert utility_foundation.logger is not None
        assert utility_foundation.error_handler is not None
        assert utility_foundation.health_service is not None
        assert utility_foundation.telemetry_service is not None
        assert utility_foundation.security_service is not None
        assert utility_foundation.tool_factory is not None

    @pytest.mark.asyncio
    async def test_utility_foundation_environment_integration(self, utility_foundation, env_loader):
        """Test that utility foundation integrates with environment configuration."""
        # Test that utility foundation can work with environment loader
        assert env_loader is not None
        assert utility_foundation is not None
        # Should not raise any exceptions when used together

    @pytest.mark.asyncio
    async def test_utility_foundation_multi_tenant_awareness(self, utility_foundation, env_loader):
        """Test that utility foundation is aware of multi-tenant configuration."""
        # Test multi-tenant configuration awareness
        multi_tenant_config = env_loader.get_multi_tenant_config()
        assert multi_tenant_config is not None
        assert isinstance(multi_tenant_config, dict)
        assert "enabled" in multi_tenant_config
        # Multi-tenancy is disabled by default in testing environment
        assert multi_tenant_config["enabled"] is False

    @pytest.mark.asyncio
    async def test_utility_foundation_tenant_management_integration(self, utility_foundation, env_loader):
        """Test that utility foundation integrates with tenant management."""
        # Test tenant management utility integration
        from foundations.utility_foundation.utilities.tenant.tenant_management_utility import TenantManagementUtility
        
        tenant_utility = TenantManagementUtility(env_loader)
        assert tenant_utility is not None
        assert tenant_utility.is_multi_tenant_enabled() is False  # Disabled by default in testing

    @pytest.mark.asyncio
    async def test_utility_foundation_security_service_integration(self, utility_foundation):
        """Test that utility foundation integrates with security service."""
        # Test security service integration
        assert utility_foundation.security_service is not None
        
        # Test user context creation
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["user"],
            tenant_id="test_tenant"
        )
        assert user_context.tenant_id == "test_tenant"

    @pytest.mark.asyncio
    async def test_utility_foundation_telemetry_service_integration(self, utility_foundation):
        """Test that utility foundation integrates with telemetry service."""
        # Test telemetry service integration
        assert utility_foundation.telemetry_service is not None
        
        # Test recording health metric
        await utility_foundation.record_health_metric(
            "test_metric",
            value=1.0,
            tags={"test": "tag"}
        )
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_utility_foundation_error_handler_integration(self, utility_foundation):
        """Test that utility foundation integrates with error handler."""
        # Test error handler integration
        assert utility_foundation.error_handler is not None
        
        # Test error handling
        test_error = Exception("Test error for integration")
        await utility_foundation.handle_error_with_audit(
            test_error,
            context={"test": "integration"}
        )
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_utility_foundation_health_service_integration(self, utility_foundation):
        """Test that utility foundation integrates with health service."""
        # Test health service integration
        assert utility_foundation.health_service is not None
        
        # Test health check
        health_status = await utility_foundation.health_check()
        assert health_status is not None
        assert "status" in health_status
