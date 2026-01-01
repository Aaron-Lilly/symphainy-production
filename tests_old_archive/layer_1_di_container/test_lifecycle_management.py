#!/usr/bin/env python3
"""
Layer 1: DI Container Lifecycle Management Tests

Tests that validate service lifecycle management works correctly.

WHAT: Validate lifecycle management
HOW: Test DIContainerService lifecycle methods
"""

import pytest
import asyncio

import os
from unittest.mock import Mock, AsyncMock, patch

from foundations.di_container.di_container_service import DIContainerService, ServiceLifecycleState

class TestLifecycleManagement:
    """Test lifecycle management."""
    
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
    
    def test_container_lifecycle_state(self, di_container):
        """Test that container has correct lifecycle state."""
        assert di_container.lifecycle_state == ServiceLifecycleState.RUNNING
    
    @pytest.mark.asyncio
    async def test_get_container_health(self, di_container):
        """Test getting container health status."""
        health = await di_container.get_container_health()
        
        assert "container_name" in health
        assert health["container_name"] == "test_realm"
        assert "lifecycle_state" in health
        assert health["lifecycle_state"] == ServiceLifecycleState.RUNNING.value
        assert "initialization_time" in health
    
    @pytest.mark.asyncio
    async def test_start_all_services(self, di_container):
        """Test starting all registered services."""
        # Register a manager service with start_service method (actual method name)
        mock_manager = Mock()
        mock_manager.service_name = "test_manager"
        mock_manager.start_service = AsyncMock(return_value=True)
        
        di_container.manager_services["test_manager"] = mock_manager
        
        # Start all services
        result = await di_container.start_all_services()
        
        assert result is True
        assert mock_manager.start_service.called
        assert di_container.lifecycle_state == ServiceLifecycleState.RUNNING
    
    @pytest.mark.asyncio
    async def test_stop_all_services(self, di_container):
        """Test stopping all registered services."""
        # Register a manager service with shutdown_service method (actual method name)
        mock_manager = Mock()
        mock_manager.service_name = "test_manager"
        mock_manager.shutdown_service = AsyncMock(return_value=True)
        
        di_container.manager_services["test_manager"] = mock_manager
        
        # Stop all services
        result = await di_container.stop_all_services()
        
        assert result is True
        assert mock_manager.shutdown_service.called
        assert di_container.lifecycle_state == ServiceLifecycleState.STOPPED
    
    @pytest.mark.asyncio
    async def test_start_all_services_with_no_services(self, di_container):
        """Test starting services when no services are registered."""
        di_container.manager_services = {}
        
        result = await di_container.start_all_services()
        
        # Should return True even with no services (successful operation)
        assert result is True
