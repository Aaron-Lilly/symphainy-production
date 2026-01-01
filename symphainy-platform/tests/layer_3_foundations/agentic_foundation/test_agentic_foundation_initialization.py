#!/usr/bin/env python3
"""
Layer 3: Agentic Foundation Initialization Tests

Tests that validate Agentic Foundation initializes correctly.

WHAT: Validate initialization
HOW: Test that Agentic Foundation initializes all components correctly
"""

import pytest
import sys
import os
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add symphainy-platform to path for absolute imports
# From test file: tests/layer_3_foundations/agentic_foundation/test_*.py
# Go up 3 levels to reach symphainy-platform root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestAgenticFoundationInitialization:
    """Test Agentic Foundation initialization."""
    
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
        mock_curator = Mock()
        mock_curator.get_registered_service = Mock(return_value=None)
        return mock_curator
    
    @pytest.fixture
    def agentic_foundation(self, di_container, public_works_foundation, curator_foundation):
        """Create Agentic Foundation instance."""
        with patch('foundations.agentic_foundation.agent_sdk.mcp_client_manager.MCPClientManager') as mock_mcp, \
             patch('foundations.agentic_foundation.infrastructure_enablement.agui_output_formatter.AGUIOutputFormatter') as mock_agui, \
             patch('foundations.agentic_foundation.infrastructure_enablement.agui_schema_registry.AGUISchemaRegistry') as mock_schema, \
             patch('foundations.agentic_foundation.agent_dashboard_service.AgentDashboardService') as mock_dashboard, \
             patch('foundations.agentic_foundation.specialization_registry.SpecializationRegistry') as mock_spec:
            # Configure mocks
            mock_mcp_instance = AsyncMock()
            mock_mcp_instance.initialize = AsyncMock(return_value=True)
            mock_mcp.return_value = mock_mcp_instance
            
            foundation = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation,
                curator_foundation=curator_foundation
            )
            return foundation
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_initializes(self, agentic_foundation):
        """Test that Agentic Foundation initializes."""
        result = await agentic_foundation.initialize()
        assert result is True
        assert agentic_foundation.is_initialized is True
        assert agentic_foundation.service_health == "healthy"
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_initializes_services(self, agentic_foundation):
        """Test that Agentic Foundation initializes services."""
        await agentic_foundation.initialize()
        
        # Check that services are initialized
        assert agentic_foundation.agui_schema_registry is not None
        assert agentic_foundation.agent_dashboard_service is not None
        assert agentic_foundation.specialization_registry is not None
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_initializes_capabilities(self, agentic_foundation):
        """Test that Agentic Foundation initializes capabilities."""
        await agentic_foundation.initialize()
        
        # Check that capabilities are registered
        assert agentic_foundation.agentic_capabilities is not None
        assert "agent_sdk" in agentic_foundation.agentic_capabilities
        assert "agent_types" in agentic_foundation.agentic_capabilities
        assert "agentic_services" in agentic_foundation.agentic_capabilities
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_has_agent_sdk_components(self, agentic_foundation):
        """Test that Agentic Foundation has agent SDK components."""
        await agentic_foundation.initialize()
        
        agent_sdk = agentic_foundation.agentic_capabilities.get("agent_sdk", {})
        assert "agent_base" in agent_sdk
        assert "policy_integration" in agent_sdk
        assert "tool_composition" in agent_sdk
        assert "business_abstraction_helper" in agent_sdk
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_has_agent_types(self, agentic_foundation):
        """Test that Agentic Foundation has agent types."""
        await agentic_foundation.initialize()
        
        agent_types = agentic_foundation.agentic_capabilities.get("agent_types", {})
        assert "dimension_liaison_agent" in agent_types
        assert "dimension_specialist_agent" in agent_types
        assert "global_guide_agent" in agent_types
        assert "global_orchestrator_agent" in agent_types
        assert "lightweight_llm_agent" in agent_types
        assert "task_llm_agent" in agent_types
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_shutdown(self, agentic_foundation):
        """Test that Agentic Foundation shuts down gracefully."""
        await agentic_foundation.initialize()
        assert agentic_foundation.is_initialized is True
        
        await agentic_foundation.shutdown()
        assert agentic_foundation.is_initialized is False

