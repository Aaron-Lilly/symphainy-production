#!/usr/bin/env python3
"""
Layer 3: Curator Foundation Compliance Tests

Tests that validate Curator Foundation complies with architectural patterns.

WHAT: Validate architectural compliance
HOW: Test that Curator Foundation uses DI Container, utilities, and Public Works Foundation properly
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

from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestCuratorFoundationCompliance:
    """Test Curator Foundation architectural compliance."""
    
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
    def curator_foundation(self, di_container, public_works_foundation):
        """Create Curator Foundation instance."""
        with patch('foundations.curator_foundation.curator_foundation_service.CapabilityRegistryService'), \
             patch('foundations.curator_foundation.curator_foundation_service.PatternValidationService'), \
             patch('foundations.curator_foundation.curator_foundation_service.AntiPatternDetectionService'), \
             patch('foundations.curator_foundation.curator_foundation_service.DocumentationGenerationService'), \
             patch('foundations.curator_foundation.curator_foundation_service.AgentCapabilityRegistryService'), \
             patch('foundations.curator_foundation.curator_foundation_service.AgentSpecializationManagementService'), \
             patch('foundations.curator_foundation.curator_foundation_service.AGUISchemaDocumentationService'), \
             patch('foundations.curator_foundation.curator_foundation_service.AgentHealthMonitoringService'):
            return CuratorFoundationService(di_container, public_works_foundation)
    
    def test_curator_foundation_uses_di_container(self, curator_foundation, di_container):
        """Test that Curator Foundation uses DI Container."""
        assert curator_foundation.di_container is not None
        assert curator_foundation.di_container == di_container
        assert hasattr(curator_foundation, 'foundation_services')
        assert curator_foundation.foundation_services == di_container
    
    def test_curator_foundation_uses_utilities(self, curator_foundation):
        """Test that Curator Foundation uses utilities via DI Container."""
        # Check that utility access methods exist
        assert hasattr(curator_foundation, 'get_utility')
        assert callable(curator_foundation.get_utility)
        assert hasattr(curator_foundation, 'logger')
        # Logger should be accessible (may be None in test setup)
        assert hasattr(curator_foundation, 'get_logger') or curator_foundation.logger is not None
    
    def test_curator_foundation_uses_public_works_foundation(self, curator_foundation, public_works_foundation):
        """Test that Curator Foundation uses Public Works Foundation."""
        assert curator_foundation.public_works_foundation is not None
        assert curator_foundation.public_works_foundation == public_works_foundation
    
    def test_curator_foundation_inherits_from_foundation_service_base(self, curator_foundation):
        """Test that Curator Foundation inherits from FoundationServiceBase."""
        from bases.foundation_service_base import FoundationServiceBase
        assert isinstance(curator_foundation, FoundationServiceBase)
    
    def test_curator_foundation_has_core_micro_services(self, curator_foundation):
        """Test that Curator Foundation has core micro-services."""
        assert hasattr(curator_foundation, 'capability_registry')
        assert hasattr(curator_foundation, 'pattern_validation')
        assert hasattr(curator_foundation, 'antipattern_detection')
        assert hasattr(curator_foundation, 'documentation_generation')
    
    def test_curator_foundation_has_agentic_micro_services(self, curator_foundation):
        """Test that Curator Foundation has agentic micro-services."""
        assert hasattr(curator_foundation, 'agent_capability_registry')
        assert hasattr(curator_foundation, 'agent_specialization_management')
        assert hasattr(curator_foundation, 'agui_schema_documentation')
        assert hasattr(curator_foundation, 'agent_health_monitoring')
    
    def test_curator_foundation_has_initialization_method(self, curator_foundation):
        """Test that Curator Foundation has initialization method."""
        assert hasattr(curator_foundation, 'initialize')
        assert callable(curator_foundation.initialize)
    
    def test_curator_foundation_has_shutdown_method(self, curator_foundation):
        """Test that Curator Foundation has shutdown method."""
        assert hasattr(curator_foundation, 'shutdown')
        assert callable(curator_foundation.shutdown)


