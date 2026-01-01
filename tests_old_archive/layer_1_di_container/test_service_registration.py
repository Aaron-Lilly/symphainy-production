#!/usr/bin/env python3
"""
Layer 1: DI Container Service Registration Tests

Tests that validate service registration works correctly.

WHAT: Validate service registration
HOW: Test DIContainerService.register_service()
"""

import pytest

import os
from unittest.mock import Mock, patch

from foundations.di_container.di_container_service import DIContainerService, ServiceLifecycleState

class TestServiceRegistration:
    """Test service registration."""
    
    @pytest.fixture
    def di_container(self):
        """Create DI Container instance."""
        # Patch imports that happen inside methods
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
    
    def test_register_service_success(self, di_container):
        """Test successful service registration."""
        result = di_container.register_service(
            service_name="test_service",
            service_type="test_type",
            endpoint="/api/test",
            capabilities=["cap1", "cap2"],
            dependencies=["dep1"]
        )
        
        assert result is True, "Service registration should succeed"
        assert "test_service" in di_container.service_registry
        registration = di_container.service_registry["test_service"]
        assert registration.service_name == "test_service"
        assert registration.service_type == "test_type"
        assert registration.endpoint == "/api/test"
        assert registration.capabilities == ["cap1", "cap2"]
        assert registration.dependencies == ["dep1"]
        assert registration.lifecycle_state == ServiceLifecycleState.RUNNING
    
    def test_register_service_without_dependencies(self, di_container):
        """Test service registration without dependencies."""
        result = di_container.register_service(
            service_name="test_service",
            service_type="test_type",
            endpoint="/api/test",
            capabilities=["cap1"]
        )
        
        assert result is True
        registration = di_container.service_registry["test_service"]
        assert registration.dependencies == []
    
    def test_register_duplicate_service(self, di_container):
        """Test registering duplicate service overwrites previous registration."""
        # Register first time
        di_container.register_service(
            service_name="test_service",
            service_type="test_type",
            endpoint="/api/test",
            capabilities=["cap1"]
        )
        
        # Register again with different values
        result = di_container.register_service(
            service_name="test_service",
            service_type="test_type_2",
            endpoint="/api/test2",
            capabilities=["cap2"]
        )
        
        assert result is True
        registration = di_container.service_registry["test_service"]
        assert registration.service_type == "test_type_2"
        assert registration.endpoint == "/api/test2"
        assert registration.capabilities == ["cap2"]
    
    def test_register_service_with_empty_capabilities(self, di_container):
        """Test service registration with empty capabilities."""
        result = di_container.register_service(
            service_name="test_service",
            service_type="test_type",
            endpoint="/api/test",
            capabilities=[]
        )
        
        assert result is True
        registration = di_container.service_registry["test_service"]
        assert registration.capabilities == []
