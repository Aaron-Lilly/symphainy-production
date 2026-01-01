#!/usr/bin/env python3
"""
Layer 3: Agentic Foundation Outputs Tests

Tests that validate Agentic Foundation outputs are properly accessible.

WHAT: Validate outputs are accessible
HOW: Test that Agentic Foundation exposes its services, SDK components, and capabilities correctly
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


class TestAgenticFoundationOutputs:
    """Test Agentic Foundation outputs are accessible."""
    
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
            container.get_foundation_service = Mock(return_value=None)
            return container
    
    @pytest.fixture
    def public_works_foundation(self):
        """Create mock Public Works Foundation."""
        mock_pw = Mock()
        mock_pw.get_tenant_abstraction = Mock(return_value=Mock())
        mock_pw.get_mcp_abstraction = Mock(return_value=Mock())
        mock_pw.get_llm_business_abstraction = Mock(return_value=Mock())
        mock_pw.get_tool_registry_abstraction = Mock(return_value=Mock())
        return mock_pw
    
    @pytest.fixture
    def curator_foundation(self):
        """Create mock Curator Foundation."""
        mock_curator = Mock()
        mock_curator.get_registered_service = Mock(return_value=None)
        mock_curator.register_service = AsyncMock(return_value={"success": True})
        mock_curator.discover_agents = AsyncMock(return_value={"total_agents": 0, "agents": {}})
        mock_curator.get_agent = AsyncMock(return_value=None)
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
    async def test_get_agentic_capabilities_returns_capabilities(self, agentic_foundation):
        """Test that get_agentic_capabilities returns capabilities."""
        await agentic_foundation.initialize()
        
        capabilities = await agentic_foundation.get_agentic_capabilities()
        
        assert capabilities is not None
        assert "foundation_name" in capabilities
        assert capabilities["foundation_name"] == "agentic_foundation"
        assert "agent_sdk" in capabilities
        assert "agent_types" in capabilities
        assert "agentic_services" in capabilities
        assert "infrastructure_abstractions" in capabilities
        assert "timestamp" in capabilities
    
    @pytest.mark.asyncio
    async def test_get_tenant_abstraction_returns_abstraction(self, agentic_foundation, public_works_foundation):
        """Test that get_tenant_abstraction returns abstraction."""
        await agentic_foundation.initialize()
        
        abstraction = await agentic_foundation.get_tenant_abstraction()
        
        assert abstraction is not None
        public_works_foundation.get_tenant_abstraction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_mcp_abstraction_returns_abstraction(self, agentic_foundation, public_works_foundation):
        """Test that get_mcp_abstraction returns abstraction."""
        await agentic_foundation.initialize()
        
        abstraction = await agentic_foundation.get_mcp_abstraction()
        
        assert abstraction is not None
        public_works_foundation.get_mcp_abstraction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_llm_abstraction_returns_abstraction(self, agentic_foundation, public_works_foundation):
        """Test that get_llm_abstraction returns abstraction."""
        await agentic_foundation.initialize()
        
        abstraction = await agentic_foundation.get_llm_abstraction()
        
        assert abstraction is not None
        public_works_foundation.get_llm_business_abstraction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tool_abstraction_returns_abstraction(self, agentic_foundation, public_works_foundation):
        """Test that get_tool_abstraction returns abstraction."""
        await agentic_foundation.initialize()
        
        abstraction = await agentic_foundation.get_tool_abstraction()
        
        assert abstraction is not None
        public_works_foundation.get_tool_registry_abstraction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_govern_agents_returns_governance_result(self, agentic_foundation):
        """Test that govern_agents returns governance result."""
        await agentic_foundation.initialize()
        
        governance_context = {"policy": "test_policy"}
        result = await agentic_foundation.govern_agents(governance_context)
        
        assert result is not None
        assert "governance_type" in result
        assert result["governance_type"] == "agent_governance"
        assert "status" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_get_agent_governance_status_returns_status(self, agentic_foundation):
        """Test that get_agent_governance_status returns status."""
        await agentic_foundation.initialize()
        
        status = await agentic_foundation.get_agent_governance_status()
        
        assert status is not None
        assert "overall_status" in status
        assert "governed_agents" in status
        assert "healthy_agents" in status
        assert "timestamp" in status
    
    @pytest.mark.asyncio
    async def test_get_agent_overview_returns_overview(self, agentic_foundation):
        """Test that get_agent_overview returns overview."""
        await agentic_foundation.initialize()
        
        overview = await agentic_foundation.get_agent_overview()
        
        assert overview is not None
        assert "total_agents" in overview
        assert "healthy_agents" in overview
        assert "overall_status" in overview
        assert "agents" in overview
        assert "timestamp" in overview
    
    @pytest.mark.asyncio
    async def test_get_all_agents_returns_agents(self, agentic_foundation):
        """Test that get_all_agents returns agents."""
        await agentic_foundation.initialize()
        
        agents = await agentic_foundation.get_all_agents()
        
        assert agents is not None
        assert "agents" in agents
        assert "total_agents" in agents
        assert isinstance(agents["agents"], list)
        assert isinstance(agents["total_agents"], int)
        assert "timestamp" in agents
    
    @pytest.mark.asyncio
    async def test_get_domain_agents_returns_domain_agents(self, agentic_foundation):
        """Test that get_domain_agents returns domain agents."""
        await agentic_foundation.initialize()
        
        domain_agents = await agentic_foundation.get_domain_agents("smart_city")
        
        assert domain_agents is not None
        assert "domain" in domain_agents
        assert domain_agents["domain"] == "smart_city"
        assert "agent_count" in domain_agents
        assert "agents" in domain_agents
        assert isinstance(domain_agents["agents"], list)
        assert "timestamp" in domain_agents
    
    @pytest.mark.asyncio
    async def test_coordinate_with_manager_returns_coordination_result(self, agentic_foundation):
        """Test that coordinate_with_manager returns coordination result."""
        await agentic_foundation.initialize()
        
        result = await agentic_foundation.coordinate_with_manager("city_manager")
        
        assert result is not None
        assert "manager_name" in result
        assert result["manager_name"] == "city_manager"
        assert "status" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_agent_dashboard_service_accessible(self, agentic_foundation):
        """Test that Agent Dashboard Service is accessible."""
        await agentic_foundation.initialize()
        
        assert agentic_foundation.agent_dashboard_service is not None
        assert hasattr(agentic_foundation.agent_dashboard_service, 'get_agent_overview')
        assert callable(agentic_foundation.agent_dashboard_service.get_agent_overview)
    
    @pytest.mark.asyncio
    async def test_specialization_registry_accessible(self, agentic_foundation):
        """Test that Specialization Registry is accessible."""
        await agentic_foundation.initialize()
        
        assert agentic_foundation.specialization_registry is not None
    
    @pytest.mark.asyncio
    async def test_agui_schema_registry_accessible(self, agentic_foundation):
        """Test that AGUI Schema Registry is accessible."""
        await agentic_foundation.initialize()
        
        assert agentic_foundation.agui_schema_registry is not None
    
    @pytest.mark.asyncio
    async def test_agent_sdk_components_accessible(self, agentic_foundation):
        """Test that Agent SDK components are accessible."""
        await agentic_foundation.initialize()
        
        capabilities = await agentic_foundation.get_agentic_capabilities()
        agent_sdk = capabilities.get("agent_sdk", {})
        
        assert "agent_base" in agent_sdk
        assert "policy_integration" in agent_sdk
        assert "tool_composition" in agent_sdk
        assert "business_abstraction_helper" in agent_sdk
    
    @pytest.mark.asyncio
    async def test_agent_types_accessible(self, agentic_foundation):
        """Test that agent types are accessible."""
        await agentic_foundation.initialize()
        
        capabilities = await agentic_foundation.get_agentic_capabilities()
        agent_types = capabilities.get("agent_types", [])
        
        assert isinstance(agent_types, list)
        assert len(agent_types) > 0
        assert "dimension_liaison_agent" in agent_types or any("liaison" in t for t in agent_types)
        assert "dimension_specialist_agent" in agent_types or any("specialist" in t for t in agent_types)
        assert "global_guide_agent" in agent_types or any("guide" in t for t in agent_types)
        assert "global_orchestrator_agent" in agent_types or any("orchestrator" in t for t in agent_types)
        assert "lightweight_llm_agent" in agent_types or any("llm" in t for t in agent_types)
        assert "task_llm_agent" in agent_types or any("task" in t for t in agent_types)

