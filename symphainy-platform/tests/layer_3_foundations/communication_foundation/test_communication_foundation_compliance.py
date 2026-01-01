#!/usr/bin/env python3
"""
Layer 3: Communication Foundation Compliance Tests

Tests that validate Communication Foundation complies with architectural patterns.

WHAT: Validate architectural compliance
HOW: Test that Communication Foundation uses DI Container, utilities, and Public Works Foundation properly
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestCommunicationFoundationCompliance:
    """Test Communication Foundation architectural compliance."""
    
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
    
    def test_communication_foundation_uses_di_container(self, communication_foundation, di_container):
        """Test that Communication Foundation uses DI Container."""
        assert communication_foundation.di_container is not None
        assert communication_foundation.di_container == di_container
    
    def test_communication_foundation_uses_utilities(self, communication_foundation):
        """Test that Communication Foundation uses utilities via DI Container."""
        # Check that utility access methods exist
        assert hasattr(communication_foundation, 'get_utility')
        assert callable(communication_foundation.get_utility)
        assert hasattr(communication_foundation, 'logger')
        # Logger should be accessible (may be None in test setup)
        assert hasattr(communication_foundation, 'get_logger') or communication_foundation.logger is not None
    
    def test_communication_foundation_uses_public_works_foundation(self, communication_foundation, public_works_foundation):
        """Test that Communication Foundation uses Public Works Foundation."""
        assert communication_foundation.public_works_foundation is not None
        assert communication_foundation.public_works_foundation == public_works_foundation
    
    def test_communication_foundation_uses_curator_foundation(self, communication_foundation, curator_foundation):
        """Test that Communication Foundation uses Curator Foundation."""
        assert communication_foundation.curator_foundation is not None
        assert communication_foundation.curator_foundation == curator_foundation
    
    def test_communication_foundation_inherits_from_foundation_service_base(self, communication_foundation):
        """Test that Communication Foundation inherits from FoundationServiceBase."""
        from bases.foundation_service_base import FoundationServiceBase
        assert isinstance(communication_foundation, FoundationServiceBase)
    
    def test_communication_foundation_has_infrastructure_adapters(self, communication_foundation):
        """Test that Communication Foundation has infrastructure adapters."""
        assert hasattr(communication_foundation, 'fastapi_router_manager')
    
    def test_communication_foundation_has_foundation_services(self, communication_foundation):
        """Test that Communication Foundation has foundation services."""
        assert hasattr(communication_foundation, 'websocket_foundation')
        assert hasattr(communication_foundation, 'messaging_foundation')
        assert hasattr(communication_foundation, 'event_bus_foundation')
    
    def test_communication_foundation_has_realm_bridges(self, communication_foundation):
        """Test that Communication Foundation has realm bridges."""
        assert hasattr(communication_foundation, 'solution_bridge')
        assert hasattr(communication_foundation, 'experience_bridge')
        assert hasattr(communication_foundation, 'smart_city_bridge')
        assert hasattr(communication_foundation, 'business_enablement_bridge')
        assert hasattr(communication_foundation, 'journey_bridge')
    
    def test_communication_foundation_has_infrastructure_abstractions(self, communication_foundation):
        """Test that Communication Foundation has infrastructure abstractions."""
        assert hasattr(communication_foundation, 'communication_abstraction')
        assert hasattr(communication_foundation, 'soa_client_abstraction')
        assert hasattr(communication_foundation, 'websocket_abstraction')
    
    def test_communication_foundation_has_composition_services(self, communication_foundation):
        """Test that Communication Foundation has composition services."""
        assert hasattr(communication_foundation, 'communication_composition_service')
        assert hasattr(communication_foundation, 'soa_composition_service')
    
    def test_communication_foundation_has_infrastructure_registry(self, communication_foundation):
        """Test that Communication Foundation has infrastructure registry."""
        assert hasattr(communication_foundation, 'communication_registry')
    
    def test_communication_foundation_has_initialization_method(self, communication_foundation):
        """Test that Communication Foundation has initialization method."""
        assert hasattr(communication_foundation, 'initialize')
        assert callable(communication_foundation.initialize)
    
    def test_communication_foundation_has_shutdown_method(self, communication_foundation):
        """Test that Communication Foundation has shutdown method."""
        assert hasattr(communication_foundation, 'shutdown')
        assert callable(communication_foundation.shutdown)

