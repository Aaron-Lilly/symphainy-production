#!/usr/bin/env python3
"""
Layer 1: DI Container Utility Integration Tests

Tests that validate utility integration works correctly.

WHAT: Validate utility integration
HOW: Test DIContainerService utility access methods
"""

import pytest

import os
from unittest.mock import Mock, patch

from foundations.di_container.di_container_service import DIContainerService

class TestUtilityIntegration:
    """Test utility integration."""
    
    @pytest.fixture
    def di_container(self):
        """Create DI Container instance."""
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
            return DIContainerService("test_realm")
    
    def test_logger_utility_available(self, di_container):
        """Test that logger utility is available."""
        assert di_container.logger is not None
    
    def test_health_utility_available(self, di_container):
        """Test that health utility is available."""
        assert di_container.health is not None
    
    def test_telemetry_utility_available(self, di_container):
        """Test that telemetry utility is available."""
        assert di_container.telemetry is not None
    
    def test_security_utility_available(self, di_container):
        """Test that security utility is available."""
        assert di_container.security is not None
    
    def test_tenant_utility_available(self, di_container):
        """Test that tenant utility is available."""
        assert di_container.tenant is not None
    
    def test_validation_utility_available(self, di_container):
        """Test that validation utility is available."""
        assert di_container.validation is not None
    
    def test_serialization_utility_available(self, di_container):
        """Test that serialization utility is available."""
        assert di_container.serialization is not None
    
    def test_get_tenant_utility(self, di_container):
        """Test getting tenant utility via getter."""
        tenant = di_container.get_tenant()
        
        assert tenant is not None
        assert tenant == di_container.tenant
