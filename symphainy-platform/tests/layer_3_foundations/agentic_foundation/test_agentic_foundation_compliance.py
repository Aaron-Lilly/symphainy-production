#!/usr/bin/env python3
"""
Layer 3: Agentic Foundation Compliance Tests

Tests that validate Agentic Foundation complies with architectural patterns.

WHAT: Validate architectural compliance
HOW: Test that Agentic Foundation uses DI Container, utilities, and Public Works Foundation properly
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add symphainy-platform to path for absolute imports
# From test file: tests/layer_3_foundations/agentic_foundation/test_*.py
# Go up 3 levels to reach symphainy-platform root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestAgenticFoundationCompliance:
    """Test Agentic Foundation architectural compliance."""
    
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
    def agentic_foundation(self, di_container, public_works_foundation, curator_foundation):
        """Create Agentic Foundation instance."""
        with patch('foundations.agentic_foundation.agent_sdk.mcp_client_manager.MCPClientManager'), \
             patch('foundations.agentic_foundation.infrastructure_enablement.agui_output_formatter.AGUIOutputFormatter'), \
             patch('foundations.agentic_foundation.infrastructure_enablement.agui_schema_registry.AGUISchemaRegistry'), \
             patch('foundations.agentic_foundation.agent_dashboard_service.AgentDashboardService'), \
             patch('foundations.agentic_foundation.specialization_registry.SpecializationRegistry'):
            return AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation,
                curator_foundation=curator_foundation
            )
    
    def test_agentic_foundation_uses_di_container(self, agentic_foundation, di_container):
        """Test that Agentic Foundation uses DI Container."""
        assert agentic_foundation.di_container is not None
        assert agentic_foundation.di_container == di_container
    
    def test_agentic_foundation_uses_utilities(self, agentic_foundation):
        """Test that Agentic Foundation uses utilities via DI Container."""
        # Check that utility access methods exist
        assert hasattr(agentic_foundation, 'get_utility')
        assert callable(agentic_foundation.get_utility)
        assert hasattr(agentic_foundation, 'logger')
        assert agentic_foundation.logger is not None
    
    def test_agentic_foundation_extends_foundation_service_base(self, agentic_foundation):
        """Test that Agentic Foundation extends FoundationServiceBase."""
        from bases.foundation_service_base import FoundationServiceBase
        assert isinstance(agentic_foundation, FoundationServiceBase)
    
    def test_agentic_foundation_has_required_attributes(self, agentic_foundation):
        """Test that Agentic Foundation has required attributes."""
        assert hasattr(agentic_foundation, 'service_name')
        assert agentic_foundation.service_name == "agentic_foundation"
        assert hasattr(agentic_foundation, 'di_container')
        assert hasattr(agentic_foundation, 'public_works_foundation')
        assert hasattr(agentic_foundation, 'curator_foundation')
    
    def test_agentic_foundation_has_agentic_capabilities(self, agentic_foundation):
        """Test that Agentic Foundation has agentic capabilities."""
        assert hasattr(agentic_foundation, 'agent_base')
        assert hasattr(agentic_foundation, 'policy_integration')
        assert hasattr(agentic_foundation, 'tool_composition')
        assert hasattr(agentic_foundation, 'business_abstraction_helper')
        assert hasattr(agentic_foundation, 'dimension_liaison_agent')
        assert hasattr(agentic_foundation, 'dimension_specialist_agent')
        assert hasattr(agentic_foundation, 'global_guide_agent')
        assert hasattr(agentic_foundation, 'global_orchestrator_agent')
        assert hasattr(agentic_foundation, 'lightweight_llm_agent')
        assert hasattr(agentic_foundation, 'task_llm_agent')
    
    def test_agentic_foundation_has_agentic_services(self, agentic_foundation):
        """Test that Agentic Foundation has agentic services."""
        assert hasattr(agentic_foundation, 'agent_dashboard_service')
        assert hasattr(agentic_foundation, 'specialization_registry')
        assert hasattr(agentic_foundation, 'agui_schema_registry')
    
    def test_agentic_foundation_has_governance_methods(self, agentic_foundation):
        """Test that Agentic Foundation has governance methods."""
        assert hasattr(agentic_foundation, 'govern_agents')
        assert callable(agentic_foundation.govern_agents)
        assert hasattr(agentic_foundation, 'get_agent_governance_status')
        assert callable(agentic_foundation.get_agent_governance_status)
        assert hasattr(agentic_foundation, 'coordinate_agent_deployment')
        assert callable(agentic_foundation.coordinate_agent_deployment)
        assert hasattr(agentic_foundation, 'enforce_agent_policy')
        assert callable(agentic_foundation.enforce_agent_policy)
    
    def test_agentic_foundation_has_coordination_methods(self, agentic_foundation):
        """Test that Agentic Foundation has coordination methods."""
        assert hasattr(agentic_foundation, 'coordinate_with_manager')
        assert callable(agentic_foundation.coordinate_with_manager)
        assert hasattr(agentic_foundation, 'orchestrate_agents')
        assert callable(agentic_foundation.orchestrate_agents)
    
    def test_agentic_foundation_has_agent_factory_methods(self, agentic_foundation):
        """Test that Agentic Foundation has agent factory methods."""
        assert hasattr(agentic_foundation, 'create_agent')
        assert callable(agentic_foundation.create_agent)
        assert hasattr(agentic_foundation, 'get_agent')
        assert callable(agentic_foundation.get_agent)
        assert hasattr(agentic_foundation, 'list_agents')
        assert callable(agentic_foundation.list_agents)
        assert hasattr(agentic_foundation, 'discover_agents_via_curator')
        assert callable(agentic_foundation.discover_agents_via_curator)

