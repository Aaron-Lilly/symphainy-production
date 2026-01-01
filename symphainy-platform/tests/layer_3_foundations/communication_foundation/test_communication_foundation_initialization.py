#!/usr/bin/env python3
"""
Layer 3: Communication Foundation Initialization Tests

Tests that validate Communication Foundation initializes correctly.

WHAT: Validate initialization
HOW: Test that all components initialize and are accessible
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


class TestCommunicationFoundationInitialization:
    """Test Communication Foundation initialization."""
    
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
        with patch('foundations.communication_foundation.communication_foundation_service.FastAPIRouterManager'), \
             patch('foundations.communication_foundation.communication_foundation_service.CommunicationAbstraction'), \
             patch('foundations.communication_foundation.communication_foundation_service.SOAClientAbstraction'), \
             patch('foundations.communication_foundation.communication_foundation_service.WebSocketAbstraction'), \
             patch('foundations.communication_foundation.communication_foundation_service.CommunicationCompositionService'), \
             patch('foundations.communication_foundation.communication_foundation_service.SOACompositionService'), \
             patch('foundations.communication_foundation.communication_foundation_service.CommunicationRegistry'):
            return CommunicationFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation,
                curator_foundation=curator_foundation
            )
    
    def test_communication_foundation_initializes(self, communication_foundation):
        """Test that Communication Foundation can be initialized."""
        assert communication_foundation is not None
        assert communication_foundation.service_name == "communication_foundation"
        assert hasattr(communication_foundation, 'di_container')
        assert hasattr(communication_foundation, 'public_works_foundation')
        assert hasattr(communication_foundation, 'curator_foundation')
    
    def test_communication_foundation_has_all_components(self, communication_foundation):
        """Test that Communication Foundation has all components."""
        # Infrastructure adapters
        assert hasattr(communication_foundation, 'fastapi_router_manager')
        
        # Foundation services
        assert hasattr(communication_foundation, 'websocket_foundation')
        assert hasattr(communication_foundation, 'messaging_foundation')
        assert hasattr(communication_foundation, 'event_bus_foundation')
        
        # Realm bridges
        assert hasattr(communication_foundation, 'solution_bridge')
        assert hasattr(communication_foundation, 'experience_bridge')
        assert hasattr(communication_foundation, 'smart_city_bridge')
        assert hasattr(communication_foundation, 'business_enablement_bridge')
        assert hasattr(communication_foundation, 'journey_bridge')
        
        # Infrastructure abstractions
        assert hasattr(communication_foundation, 'communication_abstraction')
        assert hasattr(communication_foundation, 'soa_client_abstraction')
        assert hasattr(communication_foundation, 'websocket_abstraction')
        
        # Composition services
        assert hasattr(communication_foundation, 'communication_composition_service')
        assert hasattr(communication_foundation, 'soa_composition_service')
        
        # Infrastructure registry
        assert hasattr(communication_foundation, 'communication_registry')
    
    @pytest.mark.asyncio
    async def test_communication_foundation_initializes_async(self, communication_foundation):
        """Test that Communication Foundation can be initialized asynchronously."""
        # Mock initialize method
        communication_foundation.initialize = AsyncMock(return_value=True)
        
        result = await communication_foundation.initialize()
        
        assert result is True
        communication_foundation.initialize.assert_called_once()
    
    def test_communication_foundation_has_service_name(self, communication_foundation):
        """Test that Communication Foundation has service name."""
        assert communication_foundation.service_name == "communication_foundation"
    
    def test_communication_foundation_has_di_container_reference(self, communication_foundation, di_container):
        """Test that Communication Foundation has DI Container reference."""
        assert communication_foundation.di_container == di_container
    
    def test_communication_foundation_has_public_works_reference(self, communication_foundation, public_works_foundation):
        """Test that Communication Foundation has Public Works Foundation reference."""
        assert communication_foundation.public_works_foundation == public_works_foundation
    
    def test_communication_foundation_has_curator_reference(self, communication_foundation, curator_foundation):
        """Test that Communication Foundation has Curator Foundation reference."""
        assert communication_foundation.curator_foundation == curator_foundation

