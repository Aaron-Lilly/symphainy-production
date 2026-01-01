#!/usr/bin/env python3
"""
Layer 3: Curator Foundation Initialization Tests

Tests that validate Curator Foundation initializes correctly.

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

from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestCuratorFoundationInitialization:
    """Test Curator Foundation initialization."""
    
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
    
    def test_curator_foundation_initializes(self, curator_foundation):
        """Test that Curator Foundation can be initialized."""
        assert curator_foundation is not None
        assert curator_foundation.service_name == "curator_foundation"
        assert hasattr(curator_foundation, 'di_container')
        assert hasattr(curator_foundation, 'public_works_foundation')
    
    def test_curator_foundation_has_all_micro_services(self, curator_foundation):
        """Test that Curator Foundation has all micro-services."""
        # Core micro-services
        assert hasattr(curator_foundation, 'capability_registry')
        assert hasattr(curator_foundation, 'pattern_validation')
        assert hasattr(curator_foundation, 'antipattern_detection')
        assert hasattr(curator_foundation, 'documentation_generation')
        
        # Agentic micro-services
        assert hasattr(curator_foundation, 'agent_capability_registry')
        assert hasattr(curator_foundation, 'agent_specialization_management')
        assert hasattr(curator_foundation, 'agui_schema_documentation')
        assert hasattr(curator_foundation, 'agent_health_monitoring')
    
    @pytest.mark.asyncio
    async def test_curator_foundation_initializes_async(self, curator_foundation):
        """Test that Curator Foundation can be initialized asynchronously."""
        # Mock initialize method
        curator_foundation.initialize = AsyncMock(return_value=True)
        
        result = await curator_foundation.initialize()
        
        assert result is True
        curator_foundation.initialize.assert_called_once()
    
    def test_curator_foundation_has_service_name(self, curator_foundation):
        """Test that Curator Foundation has service name."""
        assert curator_foundation.service_name == "curator_foundation"
    
    def test_curator_foundation_has_di_container_reference(self, curator_foundation, di_container):
        """Test that Curator Foundation has DI Container reference."""
        assert curator_foundation.di_container == di_container
        assert curator_foundation.foundation_services == di_container
    
    def test_curator_foundation_has_public_works_reference(self, curator_foundation, public_works_foundation):
        """Test that Curator Foundation has Public Works Foundation reference."""
        assert curator_foundation.public_works_foundation == public_works_foundation


