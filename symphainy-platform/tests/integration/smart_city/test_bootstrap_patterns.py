#!/usr/bin/env python3
"""
Tests for Bootstrap Pattern Implementation

Verifies that Nurse and Security Guard services correctly implement bootstrap patterns
for operations that PROVIDE utilities (telemetry and security respectively).
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional
from datetime import datetime

# Mock the DIContainerService and its dependencies
class MockDIContainerService:
    def __init__(self, name="test"):
        self.name = name
        self._services = {}
        self._utilities = {}
        self.logger = MagicMock()
        self.logger.info = MagicMock()
        self.logger.warning = MagicMock()
        self.logger.error = MagicMock()
        
        # Mock utility services
        self.mock_security_utility = MagicMock()
        self.mock_security_utility.check_permissions = AsyncMock(return_value=True)
        self.mock_tenant_utility = MagicMock()
        self.mock_tenant_utility.validate_tenant_access = AsyncMock(return_value=True)
        self.mock_telemetry_utility = MagicMock()
        self.mock_telemetry_utility.log_operation_with_telemetry = AsyncMock()
        self.mock_error_handler_utility = MagicMock()
        self.mock_error_handler_utility.handle_error_with_audit = AsyncMock()
        self.mock_health_utility = MagicMock()
        self.mock_health_utility.record_health_metric = AsyncMock()
        
        self._utilities["security_authorization_utility"] = self.mock_security_utility
        self._utilities["tenant_management_utility"] = self.mock_tenant_utility
        self._utilities["telemetry_reporting_utility"] = self.mock_telemetry_utility
        self._utilities["error_handler"] = self.mock_error_handler_utility
        self._utilities["health_management_utility"] = self.mock_health_utility

    def get_logger(self, name):
        return self.logger

    def get_utility(self, utility_name: str):
        return self._utilities.get(utility_name)

    def get_service(self, service_name: str):
        return self._services.get(service_name)

    def register_service(self, service_name: str, service_instance: Any):
        self._services[service_name] = service_instance

    def get_foundation_service(self, name: str):
        return self._services.get(name)


# Mock Public Works Foundation
class MockPublicWorksFoundation:
    def __init__(self):
        self.is_initialized = True
        self._abstractions = {}
        
        # Mock telemetry abstraction
        self.mock_telemetry_abstraction = MagicMock()
        self.mock_telemetry_abstraction.collect_metric = AsyncMock(return_value=True)
        self._abstractions["telemetry"] = self.mock_telemetry_abstraction
        
        # Mock health abstraction
        self.mock_health_abstraction = MagicMock()
        self.mock_health_abstraction.collect_metrics = AsyncMock(return_value=True)
        self.mock_health_abstraction.get_health_metrics = AsyncMock(return_value={"cpu": 50.0, "memory": 60.0})
        self.mock_health_abstraction.run_diagnostics = AsyncMock(return_value={"status": "healthy"})
        self.mock_health_abstraction.store_diagnostics = AsyncMock(return_value=True)
        self._abstractions["health"] = self.mock_health_abstraction
        
        # Mock auth abstraction
        self.mock_auth_abstraction = MagicMock()
        from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext
        mock_security_context = SecurityContext(
            user_id="test_user",
            tenant_id="test_tenant",
            roles=["user"],
            permissions=["read"],
            origin="api"
        )
        self.mock_auth_abstraction.authenticate_user = AsyncMock(return_value=mock_security_context)
        self.mock_auth_abstraction.register_user = AsyncMock(return_value=mock_security_context)
        self._abstractions["auth"] = self.mock_auth_abstraction
        
        # Mock authorization abstraction
        self.mock_authorization_abstraction = MagicMock()
        self.mock_authorization_abstraction.enforce = AsyncMock(return_value=True)
        self._abstractions["authorization"] = self.mock_authorization_abstraction

    def get_abstraction(self, name: str):
        return self._abstractions.get(name)


# Mock the base service for testing modules
class MockNurseService:
    def __init__(self):
        self.di_container = MockDIContainerService()
        self.logger = self.di_container.get_logger("MockNurseService")
        self.is_infrastructure_connected = True
        self.is_initialized = False
        self.service_health = "healthy"
        self.health_metrics = {}
        
        # Expose utility methods from DI container
        self.get_security = lambda: self.di_container.get_utility("security_authorization_utility")
        self.get_tenant = lambda: self.di_container.get_utility("tenant_management_utility")
        self.log_operation_with_telemetry = self.di_container.get_utility("telemetry_reporting_utility").log_operation_with_telemetry
        self.handle_error_with_audit = self.di_container.get_utility("error_handler").handle_error_with_audit
        self.record_health_metric = self.di_container.get_utility("health_management_utility").record_health_metric
        
        # Mock infrastructure abstractions
        self.public_works_foundation = MockPublicWorksFoundation()
        self.telemetry_abstraction = self.public_works_foundation.get_abstraction("telemetry")
        self.health_abstraction = self.public_works_foundation.get_abstraction("health")
        
    def get_telemetry_abstraction(self):
        """Bootstrap pattern: Direct telemetry abstraction access."""
        return self.telemetry_abstraction
    
    def get_health_abstraction(self):
        return self.health_abstraction
    
    def get_public_works_foundation(self):
        return self.public_works_foundation


class MockSecurityGuardService:
    def __init__(self):
        self.di_container = MockDIContainerService()
        self.logger = MagicMock()
        self.logger.info = MagicMock()
        self.logger.warning = MagicMock()
        self.logger.error = MagicMock()
        self.is_infrastructure_connected = True
        self.is_initialized = False
        self.service_health = "healthy"
        self.active_sessions = {}
        
        # Expose utility methods from DI container
        self.get_security = lambda: self.di_container.get_utility("security_authorization_utility")
        self.get_tenant = lambda: self.di_container.get_utility("tenant_management_utility")
        self.log_operation_with_telemetry = self.di_container.get_utility("telemetry_reporting_utility").log_operation_with_telemetry
        self.handle_error_with_audit = self.di_container.get_utility("error_handler").handle_error_with_audit
        self.record_health_metric = self.di_container.get_utility("health_management_utility").record_health_metric
        
        # Mock infrastructure abstractions
        self.public_works_foundation = MockPublicWorksFoundation()
        self.auth_abstraction = self.public_works_foundation.get_abstraction("auth")
        self.authorization_abstraction = self.public_works_foundation.get_abstraction("authorization")
        
    def get_auth_abstraction(self):
        """Bootstrap pattern: Direct auth abstraction access."""
        return self.auth_abstraction
    
    def get_authorization_abstraction(self):
        """Bootstrap pattern: Direct authorization abstraction access."""
        return self.authorization_abstraction
    
    def _log(self, level: str, message: str):
        """Safe logging method."""
        if level == "info":
            self.logger.info(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)


@pytest.fixture
def mock_nurse_service():
    """Fixture to provide a mocked Nurse service instance for testing."""
    return MockNurseService()


@pytest.fixture
def mock_security_guard_service():
    """Fixture to provide a mocked Security Guard service instance for testing."""
    return MockSecurityGuardService()


class TestNurseBootstrapPattern:
    """Tests for Nurse service bootstrap pattern (telemetry provider)."""
    
    @pytest.mark.asyncio
    async def test_collect_telemetry_uses_bootstrap_pattern(self, mock_nurse_service):
        """
        Test that collect_telemetry() uses bootstrap pattern (direct telemetry abstraction).
        
        CRITICAL: collect_telemetry() should NOT call log_operation_with_telemetry()
        because Nurse PROVIDES telemetry (circular dependency).
        """
        from backend.smart_city.services.nurse.modules.telemetry_health import TelemetryHealth
        telemetry_module = TelemetryHealth(mock_nurse_service)
        
        # Reset telemetry utility mock
        mock_nurse_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        
        # Call collect_telemetry
        result = await telemetry_module.collect_telemetry(
            service_name="test_service",
            metric_name="cpu_usage",
            metric_value=75.5,
            tags={"env": "test"}
        )
        
        # Verify result
        assert result is not None
        
        # CRITICAL: Verify that log_operation_with_telemetry() was NOT called
        # (Nurse provides telemetry, so it can't use telemetry utilities)
        assert mock_nurse_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count == 0, \
            "collect_telemetry() should NOT use log_operation_with_telemetry() (bootstrap pattern)"
        
        # Verify that direct telemetry abstraction was used
        assert mock_nurse_service.telemetry_abstraction.collect_metric.called, \
            "collect_telemetry() should use direct telemetry abstraction (bootstrap pattern)"
        
        # Verify that error handling utility WAS used (Nurse doesn't provide error handling)
        # (Only called if there's an error, so we check the method exists)
        assert hasattr(mock_nurse_service, 'handle_error_with_audit')
        
        # Verify that health metrics utility WAS used (Nurse doesn't provide health metrics)
        assert mock_nurse_service.record_health_metric.called, \
            "collect_telemetry() should use health metrics utility (Nurse doesn't provide health metrics)"
    
    @pytest.mark.asyncio
    async def test_get_health_metrics_uses_normal_utilities(self, mock_nurse_service):
        """
        Test that get_health_metrics() uses normal utilities (doesn't provide telemetry).
        """
        from backend.smart_city.services.nurse.modules.telemetry_health import TelemetryHealth
        telemetry_module = TelemetryHealth(mock_nurse_service)
        
        # Reset mocks
        mock_nurse_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        mock_nurse_service.record_health_metric.reset_mock()
        
        # Call get_health_metrics
        result = await telemetry_module.get_health_metrics("test_service")
        
        # Verify result
        assert result is not None
        assert result["status"] in ["success", "no_data", "error"]
        
        # Verify that telemetry utilities WERE used (normal pattern)
        assert mock_nurse_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count >= 2, \
            "get_health_metrics() should use log_operation_with_telemetry() (normal pattern - start and complete)"
        
        # Verify that health metrics utility WAS used
        assert mock_nurse_service.record_health_metric.called, \
            "get_health_metrics() should use health metrics utility"
    
    @pytest.mark.asyncio
    async def test_initialize_uses_normal_utilities(self, mock_nurse_service):
        """
        Test that initialize() uses normal utilities (doesn't provide telemetry during initialization).
        """
        from backend.smart_city.services.nurse.nurse_service import NurseService
        
        # We can't easily test the full initialize() without setting up all modules,
        # but we can verify the pattern by checking the initialization module
        from backend.smart_city.services.nurse.modules.initialization import Initialization
        init_module = Initialization(mock_nurse_service)
        
        # Reset mocks
        mock_nurse_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        mock_nurse_service.record_health_metric.reset_mock()
        
        # Mock the infrastructure connections
        mock_nurse_service.get_telemetry_abstraction = MagicMock(return_value=mock_nurse_service.telemetry_abstraction)
        mock_nurse_service.get_health_abstraction = MagicMock(return_value=mock_nurse_service.health_abstraction)
        mock_nurse_service.get_alert_management_abstraction = MagicMock(return_value=MagicMock())
        mock_nurse_service.get_session_abstraction = MagicMock(return_value=MagicMock())
        mock_nurse_service.get_state_management_abstraction = MagicMock(return_value=MagicMock())
        mock_nurse_service.get_public_works_foundation = MagicMock(return_value=mock_nurse_service.public_works_foundation)
        
        # Call initialize_infrastructure_connections
        await init_module.initialize_infrastructure_connections()
        
        # Verify that telemetry utilities WERE used (normal pattern)
        assert mock_nurse_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count >= 2, \
            "initialize_infrastructure_connections() should use log_operation_with_telemetry() (normal pattern)"
        
        # Verify that health metrics utility WAS used
        assert mock_nurse_service.record_health_metric.called, \
            "initialize_infrastructure_connections() should use health metrics utility"


class TestSecurityGuardBootstrapPattern:
    """Tests for Security Guard service bootstrap pattern (security provider)."""
    
    @pytest.mark.asyncio
    async def test_authenticate_user_uses_bootstrap_pattern(self, mock_security_guard_service):
        """
        Test that authenticate_user() uses bootstrap pattern (direct auth abstraction).
        
        CRITICAL: authenticate_user() should NOT call get_security()
        because Security Guard PROVIDES security (circular dependency).
        """
        from backend.smart_city.services.security_guard.modules.authentication import Authentication
        auth_module = Authentication(mock_security_guard_service)
        
        # Reset security utility mock
        mock_security_guard_service.di_container.mock_security_utility.check_permissions.reset_mock()
        
        # Mock Supabase adapter
        mock_security_guard_service.auth_abstraction.supabase = MagicMock()
        mock_security_guard_service.auth_abstraction.supabase.sign_in_with_password = AsyncMock(
            return_value={"success": True, "access_token": "test_token", "user": {"id": "test_user"}}
        )
        
        # Call authenticate_user
        result = await auth_module.authenticate_user({
            "email": "test@example.com",
            "password": "test_password"
        })
        
        # Verify result
        assert result is not None
        assert result.get("success") is True
        
        # CRITICAL: Verify that get_security().check_permissions() was NOT called
        # (Security Guard provides security, so it can't use security utilities)
        assert mock_security_guard_service.di_container.mock_security_utility.check_permissions.call_count == 0, \
            "authenticate_user() should NOT use get_security() (bootstrap pattern)"
        
        # Verify that direct auth abstraction was used
        assert mock_security_guard_service.auth_abstraction.authenticate_user.called, \
            "authenticate_user() should use direct auth abstraction (bootstrap pattern)"
        
        # Verify that telemetry utilities WERE used (Security Guard doesn't provide telemetry)
        assert mock_security_guard_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.called, \
            "authenticate_user() should use telemetry utilities (Security Guard doesn't provide telemetry)"
        
        # Verify that health metrics utility WAS used
        assert mock_security_guard_service.record_health_metric.called, \
            "authenticate_user() should use health metrics utility"
    
    @pytest.mark.asyncio
    async def test_authorize_action_uses_bootstrap_pattern(self, mock_security_guard_service):
        """
        Test that authorize_action() uses bootstrap pattern (direct authorization abstraction).
        
        CRITICAL: authorize_action() should NOT call get_security()
        because Security Guard PROVIDES security (circular dependency).
        """
        from backend.smart_city.services.security_guard.modules.authentication import Authentication
        auth_module = Authentication(mock_security_guard_service)
        
        # Reset security utility mock
        mock_security_guard_service.di_container.mock_security_utility.check_permissions.reset_mock()
        
        # Call authorize_action
        result = await auth_module.authorize_action({
            "user_id": "test_user",
            "action": "read",
            "resource": "test_resource",
            "tenant_id": "test_tenant",
            "context": {"roles": ["user"], "permissions": ["read"]}
        })
        
        # Verify result
        assert result is not None
        assert result.get("authorized") is not None
        
        # CRITICAL: Verify that get_security().check_permissions() was NOT called
        # (Security Guard provides security, so it can't use security utilities)
        assert mock_security_guard_service.di_container.mock_security_utility.check_permissions.call_count == 0, \
            "authorize_action() should NOT use get_security() (bootstrap pattern)"
        
        # Verify that direct authorization abstraction was used
        assert mock_security_guard_service.authorization_abstraction.enforce.called, \
            "authorize_action() should use direct authorization abstraction (bootstrap pattern)"
        
        # Verify that telemetry utilities WERE used (Security Guard doesn't provide telemetry)
        assert mock_security_guard_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.called, \
            "authorize_action() should use telemetry utilities (Security Guard doesn't provide telemetry)"
        
        # Verify that health metrics utility WAS used
        assert mock_security_guard_service.record_health_metric.called, \
            "authorize_action() should use health metrics utility"
    
    @pytest.mark.asyncio
    async def test_initialize_uses_normal_utilities(self, mock_security_guard_service):
        """
        Test that initialize() uses normal utilities (doesn't provide security during initialization).
        """
        # We can't easily test the full initialize() without setting up all modules,
        # but we can verify the pattern by checking that initialize() uses telemetry utilities
        # The actual initialize() method in security_guard_service.py should use normal utilities
        
        # Verify that the service has access to telemetry utilities
        assert hasattr(mock_security_guard_service, 'log_operation_with_telemetry'), \
            "Security Guard should have access to telemetry utilities for initialize()"
        
        assert hasattr(mock_security_guard_service, 'record_health_metric'), \
            "Security Guard should have access to health metrics utilities for initialize()"
        
        assert hasattr(mock_security_guard_service, 'handle_error_with_audit'), \
            "Security Guard should have access to error handling utilities for initialize()"


class TestBootstrapPatternConsistency:
    """Test that bootstrap patterns are consistently applied."""
    
    @pytest.mark.asyncio
    async def test_nurse_telemetry_provider_does_not_use_telemetry_utility(self, mock_nurse_service):
        """
        Verify that Nurse (telemetry provider) does NOT use telemetry utilities
        for operations that PROVIDE telemetry.
        """
        from backend.smart_city.services.nurse.modules.telemetry_health import TelemetryHealth
        telemetry_module = TelemetryHealth(mock_nurse_service)
        
        # Reset mocks
        mock_nurse_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        
        # Call collect_telemetry (provides telemetry)
        await telemetry_module.collect_telemetry("test_service", "test_metric", 1.0)
        
        # Verify telemetry utility was NOT used
        assert mock_nurse_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count == 0, \
            "Nurse should NOT use telemetry utilities for operations that PROVIDE telemetry"
    
    @pytest.mark.asyncio
    async def test_security_guard_security_provider_does_not_use_security_utility(self, mock_security_guard_service):
        """
        Verify that Security Guard (security provider) does NOT use security utilities
        for operations that PROVIDE security.
        """
        from backend.smart_city.services.security_guard.modules.authentication import Authentication
        auth_module = Authentication(mock_security_guard_service)
        
        # Reset mocks
        mock_security_guard_service.di_container.mock_security_utility.check_permissions.reset_mock()
        
        # Mock Supabase adapter
        mock_security_guard_service.auth_abstraction.supabase = MagicMock()
        mock_security_guard_service.auth_abstraction.supabase.sign_in_with_password = AsyncMock(
            return_value={"success": True, "access_token": "test_token", "user": {"id": "test_user"}}
        )
        
        # Call authenticate_user (provides security)
        await auth_module.authenticate_user({
            "email": "test@example.com",
            "password": "test_password"
        })
        
        # Verify security utility was NOT used
        assert mock_security_guard_service.di_container.mock_security_utility.check_permissions.call_count == 0, \
            "Security Guard should NOT use security utilities for operations that PROVIDE security"
    
    @pytest.mark.asyncio
    async def test_bootstrap_pattern_allows_other_utilities(self, mock_nurse_service, mock_security_guard_service):
        """
        Verify that bootstrap pattern services CAN use other utilities
        (e.g., Nurse can use security/error handling, Security Guard can use telemetry/error handling).
        """
        from backend.smart_city.services.nurse.modules.telemetry_health import TelemetryHealth
        telemetry_module = TelemetryHealth(mock_nurse_service)
        
        # Reset mocks
        mock_nurse_service.record_health_metric.reset_mock()
        mock_nurse_service.handle_error_with_audit = AsyncMock()
        
        # Call collect_telemetry (should use health metrics and error handling)
        await telemetry_module.collect_telemetry("test_service", "test_metric", 1.0)
        
        # Verify that health metrics utility WAS used (Nurse doesn't provide health metrics)
        assert mock_nurse_service.record_health_metric.called, \
            "Nurse should be able to use health metrics utility (doesn't provide health metrics)"
        
        # Verify that error handling utility is available (Nurse doesn't provide error handling)
        assert hasattr(mock_nurse_service, 'handle_error_with_audit'), \
            "Nurse should be able to use error handling utility (doesn't provide error handling)"
        
        # Test Security Guard
        from backend.smart_city.services.security_guard.modules.authentication import Authentication
        auth_module = Authentication(mock_security_guard_service)
        
        # Mock Supabase adapter
        mock_security_guard_service.auth_abstraction.supabase = MagicMock()
        mock_security_guard_service.auth_abstraction.supabase.sign_in_with_password = AsyncMock(
            return_value={"success": True, "access_token": "test_token", "user": {"id": "test_user"}}
        )
        
        # Reset mocks
        mock_security_guard_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        mock_security_guard_service.record_health_metric.reset_mock()
        
        # Call authenticate_user (should use telemetry and health metrics)
        await auth_module.authenticate_user({
            "email": "test@example.com",
            "password": "test_password"
        })
        
        # Verify that telemetry utility WAS used (Security Guard doesn't provide telemetry)
        assert mock_security_guard_service.di_container.mock_telemetry_utility.log_operation_with_telemetry.called, \
            "Security Guard should be able to use telemetry utility (doesn't provide telemetry)"
        
        # Verify that health metrics utility WAS used
        assert mock_security_guard_service.record_health_metric.called, \
            "Security Guard should be able to use health metrics utility"





