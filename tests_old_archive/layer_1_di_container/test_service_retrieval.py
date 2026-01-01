#!/usr/bin/env python3
"""
Layer 1: DI Container Service Retrieval Tests

Tests that validate service retrieval works correctly.

WHAT: Validate service retrieval
HOW: Test DIContainerService.discover_service() and related methods
"""

import pytest

import os
from unittest.mock import Mock, patch

from foundations.di_container.di_container_service import DIContainerService, ServiceRegistration, ServiceLifecycleState

class TestServiceRetrieval:
    """Test service retrieval."""
    
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
    
    def test_discover_service_by_name(self, di_container):
        """Test discovering a service by name."""
        # Register a service
        di_container.register_service(
            service_name="test_service",
            service_type="test_type",
            endpoint="/api/test",
            capabilities=["cap1"]
        )
        
        # Discover the service
        registration = di_container.discover_service("test_service")
        
        assert registration is not None
        assert registration.service_name == "test_service"
        assert registration.service_type == "test_type"
    
    def test_discover_nonexistent_service(self, di_container):
        """Test discovering a service that doesn't exist."""
        registration = di_container.discover_service("nonexistent_service")
        
        assert registration is None
    
    def test_discover_services_by_type(self, di_container):
        """Test discovering services by type."""
        # Register multiple services of different types
        di_container.register_service("service1", "type_a", "/api/service1", ["cap1"])
        di_container.register_service("service2", "type_a", "/api/service2", ["cap2"])
        di_container.register_service("service3", "type_b", "/api/service3", ["cap3"])
        
        # Discover services by type
        type_a_services = di_container.discover_services_by_type("type_a")
        
        assert len(type_a_services) == 2
        assert all(s.service_type == "type_a" for s in type_a_services)
        service_names = [s.service_name for s in type_a_services]
        assert "service1" in service_names
        assert "service2" in service_names
    
    def test_discover_services_by_capability(self, di_container):
        """Test discovering services by capability."""
        # Register services with different capabilities
        di_container.register_service("service1", "type_a", "/api/service1", ["cap1", "cap2"])
        di_container.register_service("service2", "type_a", "/api/service2", ["cap2", "cap3"])
        di_container.register_service("service3", "type_b", "/api/service3", ["cap3"])
        
        # Discover services by capability
        cap2_services = di_container.discover_services_by_capability("cap2")
        
        assert len(cap2_services) == 2
        service_names = [s.service_name for s in cap2_services]
        assert "service1" in service_names
        assert "service2" in service_names
        assert "service3" not in service_names
