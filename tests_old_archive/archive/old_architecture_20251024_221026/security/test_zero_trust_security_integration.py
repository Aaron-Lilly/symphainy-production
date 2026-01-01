#!/usr/bin/env python3
"""
Test Zero-Trust Security Integration - Comprehensive Test Suite

This test suite validates the zero-trust security integration including:
- ServiceBase as ground zero base class
- Security context management across all services
- Authorization guard integration
- "Secure by design, open by policy" implementation
- Manager Vision security integration

WHAT (Test Role): I validate the zero-trust security integration across the platform
HOW (Test Implementation): I test all security components and their integration
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import security components
from symphainy_platform.bases.service_base import ServiceBase
from symphainy_platform.bases.manager_service_base import ManagerServiceBase, ManagerServiceType, GovernanceLevel, OrchestrationScope
from symphainy_platform.foundations.di_container.di_container_service import DIContainerService
from symphainy_platform.foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from symphainy_platform.utilities import UserContext


class TestZeroTrustSecurityIntegration:
    """Test suite for zero-trust security integration."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container with security attributes."""
        di_container = Mock(spec=DIContainerService)
        di_container.get_logger = Mock(return_value=Mock())
        di_container.logger = Mock()
        di_container.config = Mock()
        di_container.health = Mock()
        di_container.telemetry = Mock()
        di_container.error_handler = Mock()
        di_container.tenant = Mock()
        di_container.validation = Mock()
        di_container.serialization = Mock()
        di_container.security = Mock()
        return di_container
    
    @pytest.fixture
    def mock_security_provider(self):
        """Create mock security provider."""
        security_provider = Mock()
        security_provider.get_security_context = AsyncMock()
        security_provider.validate_token = AsyncMock()
        security_provider.get_user_permissions = AsyncMock()
        return security_provider
    
    @pytest.fixture
    def mock_authorization_guard(self):
        """Create mock authorization guard."""
        auth_guard = Mock()
        auth_guard.check_permission = AsyncMock()
        auth_guard.enforce_policy = AsyncMock()
        auth_guard.get_user_roles = AsyncMock()
        return auth_guard
    
    @pytest.fixture
    def mock_user_context(self):
        """Create mock user context."""
        return UserContext(
            user_id="test_user",
            email="test@symphainy.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["admin", "test"],
            tenant_id="test_tenant"
        )
    
    @pytest.fixture
    def service_base_instance(self, mock_di_container, mock_security_provider, mock_authorization_guard):
        """Create ServiceBase instance for testing."""
        return ServiceBase(
            service_name="test_service",
            di_container=mock_di_container,
            security_provider=mock_security_provider,
            authorization_guard=mock_authorization_guard
        )
    
    # ============================================================================
    # ZERO-TRUST SECURITY FOUNDATION TESTS
    # ============================================================================
    
    def test_service_base_security_foundation(self, service_base_instance):
        """Test ServiceBase security foundation."""
        # Test that ServiceBase has security attributes
        assert hasattr(service_base_instance, 'security_provider')
        assert hasattr(service_base_instance, 'authorization_guard')
        assert hasattr(service_base_instance, 'current_security_context')
        
        # Test that security attributes are properly set
        assert service_base_instance.security_provider is not None
        assert service_base_instance.authorization_guard is not None
        assert service_base_instance.current_security_context is None  # Initially None
    
    def test_service_base_security_methods(self, service_base_instance):
        """Test ServiceBase security methods."""
        # Test that security methods are available
        assert hasattr(service_base_instance, 'get_security_context')
        assert hasattr(service_base_instance, 'check_authorization')
        assert hasattr(service_base_instance, 'enforce_security_policy')
        assert hasattr(service_base_instance, 'validate_user_permissions')
        assert hasattr(service_base_instance, 'get_user_roles')
        assert hasattr(service_base_instance, 'check_tenant_access')
        assert hasattr(service_base_instance, 'enforce_tenant_isolation')
        assert hasattr(service_base_instance, 'audit_security_event')
        assert hasattr(service_base_instance, 'get_security_metrics')
        assert hasattr(service_base_instance, 'check_service_permissions')
        assert hasattr(service_base_instance, 'enforce_service_policy')
        assert hasattr(service_base_instance, 'validate_service_access')
        assert hasattr(service_base_instance, 'get_service_roles')
        assert hasattr(service_base_instance, 'check_service_tenant_access')
        assert hasattr(service_base_instance, 'enforce_service_tenant_isolation')
        assert hasattr(service_base_instance, 'audit_service_security_event')
        assert hasattr(service_base_instance, 'get_service_security_metrics')
    
    @pytest.mark.asyncio
    async def test_security_context_management(self, service_base_instance, mock_user_context):
        """Test security context management."""
        # Test get_security_context
        security_context = await service_base_instance.get_security_context("test_token")
        assert security_context is not None
        assert hasattr(security_context, 'user_id')
        assert hasattr(security_context, 'permissions')
        assert hasattr(security_context, 'tenant_id')
        
        # Test that security context is cached
        assert service_base_instance.current_security_context is not None
    
    @pytest.mark.asyncio
    async def test_authorization_checks(self, service_base_instance, mock_user_context):
        """Test authorization checks."""
        # Test check_authorization
        auth_result = await service_base_instance.check_authorization(
            user_context=mock_user_context,
            required_permission="test_permission"
        )
        assert isinstance(auth_result, bool)
        
        # Test enforce_security_policy
        policy_result = await service_base_instance.enforce_security_policy(
            user_context=mock_user_context,
            policy_name="test_policy"
        )
        assert isinstance(policy_result, dict)
        assert "policy_id" in policy_result
        
        # Test validate_user_permissions
        permissions_result = await service_base_instance.validate_user_permissions(
            user_context=mock_user_context,
            required_permissions=["test_permission"]
        )
        assert isinstance(permissions_result, bool)
    
    @pytest.mark.asyncio
    async def test_user_role_management(self, service_base_instance, mock_user_context):
        """Test user role management."""
        # Test get_user_roles
        roles = await service_base_instance.get_user_roles(mock_user_context)
        assert isinstance(roles, list)
        
        # Test check_tenant_access
        tenant_access = await service_base_instance.check_tenant_access(
            user_context=mock_user_context,
            tenant_id="test_tenant"
        )
        assert isinstance(tenant_access, bool)
        
        # Test enforce_tenant_isolation
        isolation_result = await service_base_instance.enforce_tenant_isolation(
            user_context=mock_user_context,
            resource_tenant_id="test_tenant"
        )
        assert isinstance(isolation_result, bool)
    
    @pytest.mark.asyncio
    async def test_security_auditing(self, service_base_instance, mock_user_context):
        """Test security auditing."""
        # Test audit_security_event
        audit_result = await service_base_instance.audit_security_event(
            event_type="test_event",
            user_context=mock_user_context,
            details={"test": "details"}
        )
        assert isinstance(audit_result, dict)
        assert "audit_id" in audit_result
        
        # Test get_security_metrics
        metrics = await service_base_instance.get_security_metrics()
        assert isinstance(metrics, dict)
        assert "security_metrics" in metrics
    
    @pytest.mark.asyncio
    async def test_service_security_management(self, service_base_instance, mock_user_context):
        """Test service security management."""
        # Test check_service_permissions
        service_permissions = await service_base_instance.check_service_permissions(
            service_name="test_service",
            user_context=mock_user_context
        )
        assert isinstance(service_permissions, bool)
        
        # Test enforce_service_policy
        service_policy = await service_base_instance.enforce_service_policy(
            service_name="test_service",
            policy_name="test_policy",
            user_context=mock_user_context
        )
        assert isinstance(service_policy, dict)
        assert "policy_id" in service_policy
        
        # Test validate_service_access
        service_access = await service_base_instance.validate_service_access(
            service_name="test_service",
            user_context=mock_user_context
        )
        assert isinstance(service_access, bool)
    
    @pytest.mark.asyncio
    async def test_service_role_management(self, service_base_instance, mock_user_context):
        """Test service role management."""
        # Test get_service_roles
        service_roles = await service_base_instance.get_service_roles("test_service")
        assert isinstance(service_roles, list)
        
        # Test check_service_tenant_access
        service_tenant_access = await service_base_instance.check_service_tenant_access(
            service_name="test_service",
            user_context=mock_user_context,
            tenant_id="test_tenant"
        )
        assert isinstance(service_tenant_access, bool)
        
        # Test enforce_service_tenant_isolation
        service_isolation = await service_base_instance.enforce_service_tenant_isolation(
            service_name="test_service",
            user_context=mock_user_context,
            resource_tenant_id="test_tenant"
        )
        assert isinstance(service_isolation, bool)
    
    @pytest.mark.asyncio
    async def test_service_security_auditing(self, service_base_instance, mock_user_context):
        """Test service security auditing."""
        # Test audit_service_security_event
        service_audit = await service_base_instance.audit_service_security_event(
            service_name="test_service",
            event_type="test_event",
            user_context=mock_user_context,
            details={"test": "details"}
        )
        assert isinstance(service_audit, dict)
        assert "audit_id" in service_audit
        
        # Test get_service_security_metrics
        service_metrics = await service_base_instance.get_service_security_metrics("test_service")
        assert isinstance(service_metrics, dict)
        assert "security_metrics" in service_metrics
    
    def test_secure_by_design_implementation(self, service_base_instance):
        """Test 'secure by design' implementation."""
        # Test that security is built into the foundation
        assert hasattr(service_base_instance, 'security_provider')
        assert hasattr(service_base_instance, 'authorization_guard')
        assert hasattr(service_base_instance, 'current_security_context')
        
        # Test that security methods are always available
        security_methods = [
            'get_security_context', 'check_authorization', 'enforce_security_policy',
            'validate_user_permissions', 'get_user_roles', 'check_tenant_access',
            'enforce_tenant_isolation', 'audit_security_event', 'get_security_metrics'
        ]
        
        for method_name in security_methods:
            assert hasattr(service_base_instance, method_name), f"Security method {method_name} should be available"
            method = getattr(service_base_instance, method_name)
            assert callable(method), f"Security method {method_name} should be callable"
    
    def test_open_by_policy_implementation(self, service_base_instance):
        """Test 'open by policy' implementation."""
        # Test that policies can be enforced
        assert hasattr(service_base_instance, 'enforce_security_policy')
        assert hasattr(service_base_instance, 'enforce_service_policy')
        
        # Test that policies are configurable
        assert hasattr(service_base_instance, 'authorization_guard')
        assert service_base_instance.authorization_guard is not None


class TestManagerVisionSecurityIntegration:
    """Test Manager Vision security integration."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container."""
        di_container = Mock(spec=DIContainerService)
        di_container.get_logger = Mock(return_value=Mock())
        di_container.logger = Mock()
        di_container.config = Mock()
        di_container.health = Mock()
        di_container.telemetry = Mock()
        di_container.error_handler = Mock()
        di_container.tenant = Mock()
        di_container.validation = Mock()
        di_container.serialization = Mock()
        di_container.security = Mock()
        return di_container
    
    @pytest.fixture
    def mock_public_works_foundation(self):
        """Create mock Public Works Foundation."""
        foundation = Mock(spec=PublicWorksFoundationService)
        foundation.di_container = Mock()
        foundation.initialize = AsyncMock()
        return foundation
    
    @pytest.fixture
    def mock_security_provider(self):
        """Create mock security provider."""
        security_provider = Mock()
        security_provider.get_security_context = AsyncMock()
        security_provider.validate_token = AsyncMock()
        security_provider.get_user_permissions = AsyncMock()
        return security_provider
    
    @pytest.fixture
    def mock_authorization_guard(self):
        """Create mock authorization guard."""
        auth_guard = Mock()
        auth_guard.check_permission = AsyncMock()
        auth_guard.enforce_policy = AsyncMock()
        auth_guard.get_user_roles = AsyncMock()
        return auth_guard
    
    def test_manager_service_base_security_inheritance(self, mock_di_container, mock_public_works_foundation, mock_security_provider, mock_authorization_guard):
        """Test that ManagerServiceBase inherits zero-trust security."""
        manager = ManagerServiceBase(
            manager_type=ManagerServiceType.CUSTOM,
            realm_name="test_realm",
            di_container=mock_di_container,
            public_works_foundation=mock_public_works_foundation,
            security_provider=mock_security_provider,
            authorization_guard=mock_authorization_guard
        )
        
        # Test that ManagerServiceBase inherits from ServiceBase
        assert isinstance(manager, ServiceBase)
        
        # Test that security attributes are available
        assert hasattr(manager, 'security_provider')
        assert hasattr(manager, 'authorization_guard')
        assert hasattr(manager, 'current_security_context')
        
        # Test that security methods are available
        assert hasattr(manager, 'get_security_context')
        assert hasattr(manager, 'check_authorization')
        assert hasattr(manager, 'enforce_security_policy')
    
    @pytest.mark.asyncio
    async def test_manager_vision_security_coordination(self, mock_di_container, mock_public_works_foundation, mock_security_provider, mock_authorization_guard):
        """Test Manager Vision security coordination."""
        manager = ManagerServiceBase(
            manager_type=ManagerServiceType.CUSTOM,
            realm_name="test_realm",
            di_container=mock_di_container,
            public_works_foundation=mock_public_works_foundation,
            security_provider=mock_security_provider,
            authorization_guard=mock_authorization_guard
        )
        
        # Test that Manager Vision capabilities include security
        assert hasattr(manager, 'get_cicd_dashboard_data')
        assert hasattr(manager, 'get_soa_endpoints')
        assert hasattr(manager, 'orchestrate_user_journey')
        assert hasattr(manager, 'get_service_capabilities')
        assert hasattr(manager, 'health_check')
        
        # Test that security is integrated into Manager Vision capabilities
        capabilities = await manager.get_service_capabilities()
        assert isinstance(capabilities, dict)
        assert "security_enabled" in capabilities
        assert "authorization_enabled" in capabilities
    
    @pytest.mark.asyncio
    async def test_content_pillar_security_integration(self, mock_di_container, mock_public_works_foundation, mock_security_provider, mock_authorization_guard):
        """Test Content Pillar security integration."""
        from symphainy_platform.backend.business_enablement.pillars.content_pillar.content_pillar_service import ContentPillarService
        
        content_pillar = ContentPillarService(
            di_container=mock_di_container,
            public_works_foundation=mock_public_works_foundation,
            security_provider=mock_security_provider,
            authorization_guard=mock_authorization_guard
        )
        
        # Test that Content Pillar inherits zero-trust security
        assert isinstance(content_pillar, ServiceBase)
        assert hasattr(content_pillar, 'security_provider')
        assert hasattr(content_pillar, 'authorization_guard')
        assert hasattr(content_pillar, 'current_security_context')
        
        # Test that Content Pillar has security methods
        assert hasattr(content_pillar, 'get_security_context')
        assert hasattr(content_pillar, 'check_authorization')
        assert hasattr(content_pillar, 'enforce_security_policy')
        
        # Test that Content Pillar capabilities include security
        capabilities = await content_pillar.get_service_capabilities()
        assert isinstance(capabilities, dict)
        assert "security_enabled" in capabilities
        assert "authorization_enabled" in capabilities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




