#!/usr/bin/env python3
"""
Layer 1: DI Container Security Integration Tests

Tests that validate security integration works correctly.

WHAT: Validate security integration
HOW: Test DIContainerService security methods
"""

import pytest

import os
from unittest.mock import Mock, patch

from foundations.di_container.di_container_service import DIContainerService, SecurityContext, SecurityProvider, AuthorizationGuard

class TestSecurityIntegration:
    """Test security integration."""
    
    @pytest.fixture
    def security_provider(self):
        """Create security provider."""
        return SecurityProvider()
    
    @pytest.fixture
    def authorization_guard(self):
        """Create authorization guard."""
        return AuthorizationGuard()
    
    @pytest.fixture
    def di_container(self, security_provider, authorization_guard):
        """Create DI Container instance with security."""
        with patch('foundations.di_container.di_container_service.UnifiedConfigurationManager'), \
             patch('foundations.di_container.di_container_service.SmartCityLoggingService'), \
             patch('foundations.di_container.di_container_service.HealthManagementUtility'), \
             patch('foundations.di_container.di_container_service.TelemetryReportingUtility'), \
             patch('foundations.di_container.di_container_service.SecurityAuthorizationUtility'), \
             patch('foundations.di_container.di_container_service.SmartCityErrorHandler'), \
             patch('foundations.di_container.di_container_service.TenantManagementUtility'), \
             patch('foundations.di_container.di_container_service.ValidationUtility'), \
             patch('foundations.di_container.di_container_service.SerializationUtility'), \
             patch('foundations.di_container.di_container_service.PublicWorksFoundationService'), \
             patch('platform_infrastructure.infrastructure.platform_gateway.PlatformInfrastructureGateway'):
            return DIContainerService(
                "test_realm",
                security_provider=security_provider,
                authorization_guard=authorization_guard
            )
    
    def test_security_provider_integration(self, di_container, security_provider):
        """Test that security provider is integrated."""
        assert di_container.security_provider is not None
        assert di_container.security_provider == security_provider
    
    def test_authorization_guard_integration(self, di_container, authorization_guard):
        """Test that authorization guard is integrated."""
        assert di_container.authorization_guard is not None
        assert di_container.authorization_guard == authorization_guard
    
    def test_create_security_context(self, di_container):
        """Test creating security context."""
        context = di_container.security_provider.create_security_context(
            user_id="user123",
            tenant_id="tenant456",
            roles=["admin"],
            permissions=["read", "write"]
        )
        
        assert context.user_id == "user123"
        assert context.tenant_id == "tenant456"
        assert "admin" in context.roles
        assert "read" in context.permissions
    
    def test_validate_security_context(self, di_container):
        """Test validating security context."""
        context = SecurityContext(
            user_id="user123",
            tenant_id="tenant456",
            roles=[],
            permissions=[]
        )
        
        result = di_container.validate_security_context(context)
        
        assert result is True
    
    def test_validate_invalid_security_context(self, di_container):
        """Test validating invalid security context."""
        context = SecurityContext(
            user_id=None,
            tenant_id="tenant456",
            roles=[],
            permissions=[]
        )
        
        result = di_container.validate_security_context(context)
        
        assert result is False
    
    def test_enforce_authorization(self, di_container):
        """Test enforcing authorization."""
        context = SecurityContext(
            user_id="user123",
            tenant_id="tenant456",
            roles=[],
            permissions=[]
        )
        
        # With default open policy (no engine), should return True
        result = di_container.enforce_authorization("read", "resource1", context)
        
        assert result is True
