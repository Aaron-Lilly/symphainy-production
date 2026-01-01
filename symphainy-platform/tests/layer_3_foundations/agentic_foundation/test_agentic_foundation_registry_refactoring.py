#!/usr/bin/env python3
"""
Layer 3: Agentic Foundation Registry Refactoring Tests

Tests that validate the refactored agent registration pattern:
- Factory owns agent registration (Phase 2 pattern)
- Capabilities validation (fail fast)
- No double registration
- Standardized capabilities pattern
- Phase 2 register_agent() with characteristics/contracts

WHAT: Validate refactored agent registration architecture
HOW: Test factory registration, capabilities validation, and Phase 2 patterns
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Add symphainy-platform to path for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase
from foundations.agentic_foundation.agui_schema_registry import AGUISchema
from foundations.di_container.di_container_service import DIContainerService


class TestAgentRegistryRefactoring:
    """Test Agentic Foundation registry refactoring."""
    
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
    def mock_curator(self):
        """Create mock Curator Foundation with register_agent method."""
        curator = Mock()
        curator.register_agent = AsyncMock(return_value=True)
        curator.get_registered_services = AsyncMock(return_value={"services": {}})
        curator.discover_agents = AsyncMock(return_value={"total_agents": 0, "agents": {}})
        return curator
    
    @pytest.fixture
    def agentic_foundation(self, di_container, mock_curator):
        """Create Agentic Foundation instance with mocked dependencies."""
        di_container.service_registry["CuratorFoundationService"] = mock_curator
        
        with patch('foundations.agentic_foundation.agent_sdk.mcp_client_manager.MCPClientManager'), \
             patch('foundations.agentic_foundation.infrastructure_enablement.agui_output_formatter.AGUIOutputFormatter'), \
             patch('foundations.agentic_foundation.infrastructure_enablement.agui_schema_registry.AGUISchemaRegistry'), \
             patch('foundations.agentic_foundation.agent_dashboard_service.AgentDashboardService'), \
             patch('foundations.agentic_foundation.specialization_registry.SpecializationRegistry'), \
             patch('foundations.agentic_foundation.agent_sdk.policy_integration.PolicyIntegration'), \
             patch('foundations.agentic_foundation.agent_sdk.tool_composition.ToolComposition'):
            
            foundation = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=Mock(),
                curator_foundation=mock_curator
            )
            foundation.mcp_client_manager = Mock()
            foundation.policy_integration = Mock()
            foundation.tool_composition = Mock()
            foundation.agui_formatter = Mock()
            return foundation
    
    @pytest.fixture
    def test_agent_class(self):
        """Create a test agent class."""
        class TestAgent(AgentBase):
            def __init__(self, agent_name, business_domain, capabilities, required_roles,
                         agui_schema, foundation_services, agentic_foundation,
                         public_works_foundation, mcp_client_manager, policy_integration,
                         tool_composition, agui_formatter, curator_foundation=None, **kwargs):
                super().__init__(
                    agent_name=agent_name,
                    capabilities=capabilities,
                    required_roles=required_roles,
                    agui_schema=agui_schema,
                    foundation_services=foundation_services,
                    agentic_foundation=agentic_foundation,
                    mcp_client_manager=mcp_client_manager,
                    policy_integration=policy_integration,
                    tool_composition=tool_composition,
                    agui_formatter=agui_formatter,
                    curator_foundation=curator_foundation,
                    **kwargs
                )
                self.business_domain = business_domain
            
            async def initialize(self):
                """Initialize test agent."""
                self.is_initialized = True
                return True
            
            async def get_agent_description(self) -> str:
                return "Test agent for registry refactoring tests"
        
        return TestAgent
    
    @pytest.fixture
    def test_agui_schema(self):
        """Create a test AGUI schema."""
        return AGUISchema(
            agent_name="TestAgent",
            version="1.0.0",
            description="Test agent schema",
            components=[],
            metadata={}
        )
    
    @pytest.mark.asyncio
    async def test_factory_registers_agent_with_phase2_pattern(self, agentic_foundation, test_agent_class, test_agui_schema, mock_curator):
        """Test that factory registers agent using Phase 2 register_agent() pattern."""
        # Create agent via factory
        agent = await agentic_foundation.create_agent(
            agent_class=test_agent_class,
            agent_name="TestAgent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=agentic_foundation.di_container,
            orchestrator=None,
            capabilities=["test_capability_1", "test_capability_2"],
            required_roles=["librarian"]
        )
        
        # Verify agent was created
        assert agent is not None
        assert agent.agent_name == "TestAgent"
        
        # Verify register_agent was called (Phase 2 pattern)
        assert mock_curator.register_agent.called
        
        # Verify call arguments
        call_args = mock_curator.register_agent.call_args
        assert call_args is not None
        
        # Verify characteristics structure
        characteristics = call_args.kwargs.get("characteristics") or call_args.args[3]
        assert "capabilities" in characteristics
        assert characteristics["capabilities"] == ["test_capability_1", "test_capability_2"]
        assert "realm" in characteristics
        assert characteristics["realm"] == "business_enablement"
        assert "required_roles" in characteristics
        assert characteristics["required_roles"] == ["librarian"]
        # Verify pillar is NOT in characteristics
        assert "pillar" not in characteristics
        
        # Verify contracts structure
        contracts = call_args.kwargs.get("contracts") or call_args.args[4]
        assert "agent_api" in contracts
        assert contracts["agent_api"]["realm"] == "business_enablement"
        assert contracts["agent_api"]["agent_type"] == "liaison"
        assert contracts["agent_api"]["access_pattern"] == "direct_python_method_calls"
        assert contracts["agent_api"]["interface"] == "python_object"
        # Verify MCP tools are NOT in contracts
        assert "mcp_tools" not in contracts
    
    @pytest.mark.asyncio
    async def test_factory_validates_capabilities_fail_fast(self, agentic_foundation, test_agent_class, test_agui_schema):
        """Test that factory fails fast if capabilities are not provided."""
        # Try to create agent without capabilities
        with pytest.raises(ValueError, match="capabilities are required"):
            await agentic_foundation.create_agent(
                agent_class=test_agent_class,
                agent_name="TestAgent",
                agent_type="liaison",
                realm_name="business_enablement",
                di_container=agentic_foundation.di_container,
                orchestrator=None,
                capabilities=[],  # Empty capabilities should fail
                required_roles=[]
            )
    
    @pytest.mark.asyncio
    async def test_agent_initialize_does_not_register(self, agentic_foundation, test_agent_class, test_agui_schema, mock_curator):
        """Test that agent.initialize() does NOT call registration."""
        # Create agent via factory
        agent = await agentic_foundation.create_agent(
            agent_class=test_agent_class,
            agent_name="TestAgent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=agentic_foundation.di_container,
            orchestrator=None,
            capabilities=["test_capability"],
            required_roles=[]
        )
        
        # Verify agent was created
        assert agent is not None
        
        # Verify register_agent was called by factory (not by agent.initialize)
        assert mock_curator.register_agent.called
        
        # Reset mock to check if initialize() calls registration
        mock_curator.register_agent.reset_mock()
        
        # Call initialize() directly (should NOT register)
        await agent.initialize()
        
        # Verify register_agent was NOT called by initialize()
        assert not mock_curator.register_agent.called
    
    @pytest.mark.asyncio
    async def test_get_agent_capabilities_returns_self_capabilities(self, test_agent_class, test_agui_schema):
        """Test that get_agent_capabilities() returns self.capabilities by default."""
        # Create agent instance directly (for testing)
        agent = test_agent_class(
            agent_name="TestAgent",
            business_domain="test",
            capabilities=["cap1", "cap2", "cap3"],
            required_roles=[],
            agui_schema=test_agui_schema,
            foundation_services=Mock(),
            agentic_foundation=Mock(),
            public_works_foundation=Mock(),
            mcp_client_manager=Mock(),
            policy_integration=Mock(),
            tool_composition=Mock(),
            agui_formatter=Mock()
        )
        
        # Test get_agent_capabilities returns self.capabilities
        capabilities = await agent.get_agent_capabilities()
        assert capabilities == ["cap1", "cap2", "cap3"]
        assert capabilities == agent.capabilities
    
    @pytest.mark.asyncio
    async def test_factory_extracts_capabilities_from_agent(self, agentic_foundation, test_agent_class, test_agui_schema, mock_curator):
        """Test that factory can extract capabilities from agent instance."""
        # Create agent via factory
        agent = await agentic_foundation.create_agent(
            agent_class=test_agent_class,
            agent_name="TestAgent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=agentic_foundation.di_container,
            orchestrator=None,
            capabilities=["factory_capability"],
            required_roles=[]
        )
        
        # Verify capabilities were extracted and registered
        call_args = mock_curator.register_agent.call_args
        characteristics = call_args.kwargs.get("characteristics") or call_args.args[3]
        assert characteristics["capabilities"] == ["factory_capability"]
    
    @pytest.mark.asyncio
    async def test_factory_registers_realm_not_pillar(self, agentic_foundation, test_agent_class, test_agui_schema, mock_curator):
        """Test that factory registers realm, not pillar."""
        # Create agent via factory
        agent = await agentic_foundation.create_agent(
            agent_class=test_agent_class,
            agent_name="TestAgent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=agentic_foundation.di_container,
            orchestrator=None,
            capabilities=["test_capability"],
            required_roles=[]
        )
        
        # Verify characteristics
        call_args = mock_curator.register_agent.call_args
        characteristics = call_args.kwargs.get("characteristics") or call_args.args[3]
        
        # Verify realm is present
        assert "realm" in characteristics
        assert characteristics["realm"] == "business_enablement"
        
        # Verify pillar is NOT present
        assert "pillar" not in characteristics
    
    @pytest.mark.asyncio
    async def test_factory_registers_optional_specialization(self, agentic_foundation, test_agent_class, test_agui_schema, mock_curator):
        """Test that factory registers optional specialization."""
        # Create agent with specialization
        agent = await agentic_foundation.create_agent(
            agent_class=test_agent_class,
            agent_name="TestAgent",
            agent_type="specialist",
            realm_name="business_enablement",
            di_container=agentic_foundation.di_container,
            orchestrator=None,
            capabilities=["test_capability"],
            required_roles=[],
            specialization_config={
                "specialization": "testing_expert"
            }
        )
        
        # Verify characteristics include specialization
        call_args = mock_curator.register_agent.call_args
        characteristics = call_args.kwargs.get("characteristics") or call_args.args[3]
        assert "specialization" in characteristics
        assert characteristics["specialization"] == "testing_expert"
    
    @pytest.mark.asyncio
    async def test_factory_registers_agent_api_contract(self, agentic_foundation, test_agent_class, test_agui_schema, mock_curator):
        """Test that factory registers agent API contract (Python interface, not REST)."""
        # Create agent via factory
        mock_orchestrator = Mock()
        mock_orchestrator.service_name = "TestOrchestrator"
        
        agent = await agentic_foundation.create_agent(
            agent_class=test_agent_class,
            agent_name="TestAgent",
            agent_type="specialist",
            realm_name="business_enablement",
            di_container=agentic_foundation.di_container,
            orchestrator=mock_orchestrator,
            capabilities=["test_capability"],
            required_roles=[]
        )
        
        # Verify contracts structure
        call_args = mock_curator.register_agent.call_args
        contracts = call_args.kwargs.get("contracts") or call_args.args[4]
        
        assert "agent_api" in contracts
        agent_api = contracts["agent_api"]
        assert agent_api["service_name"] == "TestAgent"
        assert agent_api["realm"] == "business_enablement"
        assert agent_api["agent_type"] == "specialist"
        assert agent_api["orchestrator"] == "TestOrchestrator"
        assert agent_api["access_pattern"] == "direct_python_method_calls"
        assert agent_api["interface"] == "python_object"
    
    @pytest.mark.asyncio
    async def test_factory_does_not_register_mcp_tools(self, agentic_foundation, test_agent_class, test_agui_schema, mock_curator):
        """Test that factory does NOT register MCP tools (agents use them, don't expose them)."""
        # Create agent via factory
        agent = await agentic_foundation.create_agent(
            agent_class=test_agent_class,
            agent_name="TestAgent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=agentic_foundation.di_container,
            orchestrator=None,
            capabilities=["test_capability"],
            required_roles=["librarian"]  # Agent uses MCP tools via required_roles
        )
        
        # Verify contracts do NOT include MCP tools
        call_args = mock_curator.register_agent.call_args
        contracts = call_args.kwargs.get("contracts") or call_args.args[4]
        
        # MCP tools should NOT be in contracts
        assert "mcp_tools" not in contracts
    
    @pytest.mark.asyncio
    async def test_agent_base_has_no_register_with_curator_method(self):
        """Test that AgentBase no longer has register_with_curator() method."""
        # Check that method doesn't exist
        assert not hasattr(AgentBase, 'register_with_curator') or \
               not callable(getattr(AgentBase, 'register_with_curator', None))
    
    @pytest.mark.asyncio
    async def test_factory_tracks_agents_in_cache(self, agentic_foundation, test_agent_class, test_agui_schema):
        """Test that factory tracks agents in internal cache."""
        # Create agent via factory
        agent = await agentic_foundation.create_agent(
            agent_class=test_agent_class,
            agent_name="TestAgent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=agentic_foundation.di_container,
            orchestrator=None,
            capabilities=["test_capability"],
            required_roles=[]
        )
        
        # Verify agent is in factory cache
        assert "TestAgent" in agentic_foundation._agents
        assert agentic_foundation._agents["TestAgent"] == agent
        
        # Verify get_agent returns cached agent
        retrieved_agent = await agentic_foundation.get_agent("TestAgent")
        assert retrieved_agent == agent




