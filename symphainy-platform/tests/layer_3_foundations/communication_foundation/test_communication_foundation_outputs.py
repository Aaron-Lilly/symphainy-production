#!/usr/bin/env python3
"""
Layer 3: Communication Foundation Outputs Tests

Tests that validate Communication Foundation outputs are properly accessible.

WHAT: Validate outputs are accessible
HOW: Test that Communication Foundation exposes its services and abstractions correctly
"""

import pytest
import sys
import os
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestCommunicationFoundationOutputs:
    """Test Communication Foundation outputs are accessible."""
    
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
            container = DIContainerService("test_realm")
            # Mock foundation service getters
            container.get_websocket_foundation = Mock(return_value=Mock())
            container.get_messaging_foundation = Mock(return_value=Mock())
            container.get_event_bus_foundation = Mock(return_value=Mock())
            return container
    
    @pytest.fixture
    def public_works_foundation(self):
        """Create mock Public Works Foundation."""
        return Mock()
    
    @pytest.fixture
    def curator_foundation(self):
        """Create mock Curator Foundation."""
        return Mock()
    
    @pytest.fixture
    def communication_foundation(self, di_container, public_works_foundation, curator_foundation):
        """Create Communication Foundation instance."""
        # Create mock abstractions
        mock_communication_abstraction = Mock()
        mock_soa_client_abstraction = Mock()
        mock_websocket_abstraction = Mock()
        
        with patch('foundations.communication_foundation.communication_foundation_service.FastAPIRouterManager') as mock_router, \
             patch('foundations.communication_foundation.communication_foundation_service.CommunicationAbstraction', return_value=mock_communication_abstraction), \
             patch('foundations.communication_foundation.communication_foundation_service.SOAClientAbstraction', return_value=mock_soa_client_abstraction), \
             patch('foundations.communication_foundation.communication_foundation_service.WebSocketAbstraction', return_value=mock_websocket_abstraction), \
             patch('foundations.communication_foundation.communication_foundation_service.CommunicationCompositionService'), \
             patch('foundations.communication_foundation.communication_foundation_service.SOACompositionService'), \
             patch('foundations.communication_foundation.communication_foundation_service.CommunicationRegistry'):
            foundation = CommunicationFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation,
                curator_foundation=curator_foundation
            )
            # Set up mock abstractions
            foundation.communication_abstraction = mock_communication_abstraction
            foundation.soa_client_abstraction = mock_soa_client_abstraction
            foundation.websocket_abstraction = mock_websocket_abstraction
            foundation.event_bus_foundation = Mock()
            return foundation
    
    @pytest.mark.asyncio
    async def test_get_api_gateway_returns_communication_abstraction(self, communication_foundation):
        """Test that get_api_gateway() returns communication abstraction."""
        api_gateway = await communication_foundation.get_api_gateway()
        
        assert api_gateway is not None
        assert api_gateway == communication_foundation.communication_abstraction
    
    @pytest.mark.asyncio
    async def test_get_soa_client_returns_soa_client_abstraction(self, communication_foundation):
        """Test that get_soa_client() returns SOA client abstraction."""
        soa_client = await communication_foundation.get_soa_client()
        
        assert soa_client is not None
        assert soa_client == communication_foundation.soa_client_abstraction
    
    @pytest.mark.asyncio
    async def test_get_websocket_manager_returns_websocket_abstraction(self, communication_foundation):
        """Test that get_websocket_manager() returns WebSocket abstraction."""
        websocket_manager = await communication_foundation.get_websocket_manager()
        
        assert websocket_manager is not None
        assert websocket_manager == communication_foundation.websocket_abstraction
    
    @pytest.mark.asyncio
    async def test_get_messaging_service_returns_communication_abstraction(self, communication_foundation):
        """Test that get_messaging_service() returns communication abstraction."""
        messaging_service = await communication_foundation.get_messaging_service()
        
        assert messaging_service is not None
        assert messaging_service == communication_foundation.communication_abstraction
    
    @pytest.mark.asyncio
    async def test_get_event_bus_returns_communication_abstraction(self, communication_foundation):
        """Test that get_event_bus() returns communication abstraction."""
        event_bus = await communication_foundation.get_event_bus()
        
        assert event_bus is not None
        # get_event_bus() returns communication_abstraction (as per implementation)
        assert event_bus == communication_foundation.communication_abstraction
    
    def test_communication_foundation_exposes_public_api_methods(self, communication_foundation):
        """Test that Communication Foundation exposes public API methods."""
        # Check that all public API methods exist
        assert hasattr(communication_foundation, 'get_api_gateway')
        assert callable(communication_foundation.get_api_gateway)
        
        assert hasattr(communication_foundation, 'get_soa_client')
        assert callable(communication_foundation.get_soa_client)
        
        assert hasattr(communication_foundation, 'get_websocket_manager')
        assert callable(communication_foundation.get_websocket_manager)
        
        assert hasattr(communication_foundation, 'get_messaging_service')
        assert callable(communication_foundation.get_messaging_service)
        
        assert hasattr(communication_foundation, 'get_event_bus')
        assert callable(communication_foundation.get_event_bus)
    
    def test_communication_foundation_exposes_composition_services(self, communication_foundation):
        """Test that Communication Foundation exposes composition services."""
        assert hasattr(communication_foundation, 'communication_composition_service')
        assert hasattr(communication_foundation, 'soa_composition_service')
    
    def test_communication_foundation_exposes_infrastructure_registry(self, communication_foundation):
        """Test that Communication Foundation exposes infrastructure registry."""
        assert hasattr(communication_foundation, 'communication_registry')
    
    def test_communication_foundation_exposes_realm_bridges(self, communication_foundation):
        """Test that Communication Foundation exposes realm bridges."""
        assert hasattr(communication_foundation, 'solution_bridge')
        assert hasattr(communication_foundation, 'experience_bridge')
        assert hasattr(communication_foundation, 'smart_city_bridge')
        assert hasattr(communication_foundation, 'business_enablement_bridge')
        assert hasattr(communication_foundation, 'journey_bridge')

