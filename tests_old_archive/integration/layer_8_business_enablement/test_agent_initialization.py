#!/usr/bin/env python3
"""
Phase 1: Agent Initialization Tests (Mocked)

Tests agent creation via Agentic Foundation factory, dependency injection, and initialization.
All tests use mocked LLM to verify agent creation logic.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))

pytestmark = [pytest.mark.integration]


@pytest.fixture
async def minimal_foundation_infrastructure():
    """
    Minimal infrastructure fixture for Agentic Foundation tests.
    
    Only initializes Public Works Foundation and Curator Foundation.
    Does not require Smart City services.
    """
    from foundations.di_container.di_container_service import DIContainerService
    from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
    from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
    
    # 1. Initialize DI Container
    di_container = DIContainerService("test_platform")
    
    # 2. Initialize Public Works Foundation
    pwf = PublicWorksFoundationService(di_container=di_container)
    
    try:
        pwf_result = await asyncio.wait_for(
            pwf.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        pytest.fail("Public Works Foundation initialization timed out after 30 seconds")
    
    if not pwf_result:
        pytest.fail("Public Works Foundation initialization failed")
    
    di_container.public_works_foundation = pwf
    
    # 3. Initialize Curator Foundation
    curator = CuratorFoundationService(
        foundation_services=di_container,
        public_works_foundation=pwf
    )
    
    try:
        curator_result = await asyncio.wait_for(
            curator.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        pytest.fail("Curator Foundation initialization timed out after 30 seconds")
    
    if not curator_result:
        pytest.fail("Curator Foundation initialization failed")
    
    di_container.curator_foundation = curator
    
    return {
        "di_container": di_container,
        "public_works_foundation": pwf,
        "curator": curator
    }


@pytest.fixture
async def agentic_foundation(minimal_foundation_infrastructure):
    """Fixture providing initialized Agentic Foundation."""
    infra = smart_city_infrastructure
    di_container = infra["di_container"]
    pwf = infra["public_works_foundation"]
    curator = infra["curator"]
    
    from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
    
    agentic = AgenticFoundationService(
        di_container=di_container,
        public_works_foundation=pwf,
        curator_foundation=curator
    )
    await agentic.initialize()
    return agentic


class TestAgentCreation:
    """Test agent creation via Agentic Foundation factory."""
    
    @pytest.mark.asyncio
    async def test_create_liaison_agent(self, agentic_foundation):
        """Test creating a liaison agent via factory."""
        from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        agentic = agentic_foundation
        di_container = agentic.di_container
        
        # Create AGUI schema
        agui_schema = AGUISchema(
            agent_name="Test Liaison Agent",
            version="1.0.0",
            description="Test agent",
            components=[],
            metadata={}
        )
        
        # Create agent
        agent = await agentic.create_agent(
            agent_class=DimensionLiaisonAgent,
            agent_name="Test Liaison Agent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=di_container,
            capabilities=["conversation", "guidance"],
            required_roles=["test_orchestrator"],
            agui_schema=agui_schema
        )
        
        assert agent is not None, "Agent should be created"
        assert agent.agent_name == "Test Liaison Agent", "Agent should have correct name"
        assert agent.is_initialized, "Agent should be initialized"
        
        # Check agent is tracked
        assert "Test Liaison Agent" in agentic._agents, "Agent should be tracked in registry"
    
    @pytest.mark.asyncio
    async def test_create_specialist_agent(self, agentic_foundation):
        """Test creating a specialist agent via factory."""
        from foundations.agentic_foundation.agent_sdk.dimension_specialist_agent import DimensionSpecialistAgent
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        agentic = agentic_foundation
        di_container = agentic.di_container
        
        # Create AGUI schema
        agui_schema = AGUISchema(
            agent_name="Test Specialist Agent",
            version="1.0.0",
            description="Test specialist agent",
            components=[],
            metadata={}
        )
        
        # Create agent
        agent = await agentic.create_agent(
            agent_class=DimensionSpecialistAgent,
            agent_name="Test Specialist Agent",
            agent_type="specialist",
            realm_name="business_enablement",
            di_container=di_container,
            capabilities=["analysis", "generation"],
            required_roles=["test_orchestrator"],
            agui_schema=agui_schema
        )
        
        assert agent is not None, "Agent should be created"
        assert agent.agent_name == "Test Specialist Agent", "Agent should have correct name"
        assert agent.is_initialized, "Agent should be initialized"
    
    @pytest.mark.asyncio
    async def test_agent_creation_requires_capabilities(self, agentic_foundation):
        """Test that agent creation fails without capabilities."""
        from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        agentic = agentic_foundation
        di_container = agentic.di_container
        
        # Create AGUI schema
        agui_schema = AGUISchema(
            agent_name="Invalid Agent",
            version="1.0.0",
            description="Test agent without capabilities",
            components=[],
            metadata={}
        )
        
        # Try to create agent without capabilities (should fail)
        with pytest.raises(ValueError, match="capabilities"):
            await agentic.create_agent(
                agent_class=DimensionLiaisonAgent,
                agent_name="Invalid Agent",
                agent_type="liaison",
                realm_name="business_enablement",
                di_container=di_container,
                # Missing capabilities parameter
                required_roles=["test_orchestrator"],
                agui_schema=agui_schema
            )
    
    @pytest.mark.asyncio
    async def test_agent_creation_caching(self, agentic_foundation):
        """Test that agent creation uses caching (returns same instance)."""
        from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        agentic = agentic_foundation
        di_container = agentic.di_container
        
        # Create AGUI schema
        agui_schema = AGUISchema(
            agent_name="Cached Agent",
            version="1.0.0",
            description="Test cached agent",
            components=[],
            metadata={}
        )
        
        # Create agent first time
        agent1 = await agentic.create_agent(
            agent_class=DimensionLiaisonAgent,
            agent_name="Cached Agent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=di_container,
            capabilities=["conversation"],
            required_roles=["test_orchestrator"],
            agui_schema=agui_schema
        )
        
        # Create agent second time (should return cached instance)
        agent2 = await agentic.create_agent(
            agent_class=DimensionLiaisonAgent,
            agent_name="Cached Agent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=di_container,
            capabilities=["conversation"],
            required_roles=["test_orchestrator"],
            agui_schema=agui_schema
        )
        
        assert agent1 is agent2, "Should return same cached instance"
        assert agent1.agent_name == agent2.agent_name, "Cached agent should have same name"


class TestAgentDependencyInjection:
    """Test agent dependency injection and graceful degradation."""
    
    @pytest.mark.asyncio
    async def test_agent_has_required_dependencies(self, agentic_foundation):
        """Test that agent has all required dependencies."""
        from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        agentic = agentic_foundation
        di_container = agentic.di_container
        
        # Create AGUI schema
        agui_schema = AGUISchema(
            agent_name="Dependency Test Agent",
            version="1.0.0",
            description="Test dependencies",
            components=[],
            metadata={}
        )
        
        # Create agent
        agent = await agentic.create_agent(
            agent_class=DimensionLiaisonAgent,
            agent_name="Dependency Test Agent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=di_container,
            capabilities=["conversation"],
            required_roles=["test_orchestrator"],
            agui_schema=agui_schema
        )
        
        # Check required dependencies
        assert hasattr(agent, "foundation_services"), "Should have foundation services"
        assert hasattr(agent, "agentic_foundation"), "Should have agentic foundation"
        assert hasattr(agent, "public_works_foundation"), "Should have public works foundation"
        assert hasattr(agent, "policy_integration"), "Should have policy integration"
        assert hasattr(agent, "tool_composition"), "Should have tool composition"
    
    @pytest.mark.asyncio
    async def test_agent_has_optional_dependencies(self, agentic_foundation):
        """Test that agent handles optional dependencies gracefully."""
        from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        agentic = agentic_foundation
        di_container = agentic.di_container
        
        # Create AGUI schema
        agui_schema = AGUISchema(
            agent_name="Optional Dependency Agent",
            version="1.0.0",
            description="Test optional dependencies",
            components=[],
            metadata={}
        )
        
        # Create agent
        agent = await agentic.create_agent(
            agent_class=DimensionLiaisonAgent,
            agent_name="Optional Dependency Agent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=di_container,
            capabilities=["conversation"],
            required_roles=["test_orchestrator"],
            agui_schema=agui_schema
        )
        
        # Optional dependencies may be None (MCP, AGUI formatter)
        # Agent should still initialize successfully
        assert agent is not None, "Agent should create even with optional deps missing"
        assert agent.is_initialized, "Agent should initialize successfully"
        
        # Check optional dependencies (may be None)
        if hasattr(agent, "mcp_client_manager"):
            # MCP is optional - None is acceptable
            pass
        
        if hasattr(agent, "agui_formatter"):
            # AGUI formatter is optional - None is acceptable
            pass


class TestAgentLifecycle:
    """Test agent lifecycle management."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agentic_foundation):
        """Test agent initialization."""
        from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        agentic = agentic_foundation
        di_container = agentic.di_container
        
        # Create AGUI schema
        agui_schema = AGUISchema(
            agent_name="Lifecycle Test Agent",
            version="1.0.0",
            description="Test lifecycle",
            components=[],
            metadata={}
        )
        
        # Create agent
        agent = await agentic.create_agent(
            agent_class=DimensionLiaisonAgent,
            agent_name="Lifecycle Test Agent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=di_container,
            capabilities=["conversation"],
            required_roles=["test_orchestrator"],
            agui_schema=agui_schema
        )
        
        # Check initialization
        assert agent.is_initialized, "Agent should be initialized"
        
        # Test shutdown if available
        if hasattr(agent, "shutdown"):
            await agent.shutdown()
            # After shutdown, agent may or may not be marked as not initialized
            # (depends on implementation)
    
    @pytest.mark.asyncio
    async def test_agent_registry_tracking(self, agentic_foundation):
        """Test that agents are tracked in registry."""
        from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        agentic = agentic_foundation
        di_container = agentic.di_container
        
        # Create multiple agents
        agents = []
        for i in range(3):
            agui_schema = AGUISchema(
                agent_name=f"Tracked Agent {i}",
                version="1.0.0",
                description=f"Test agent {i}",
                components=[],
                metadata={}
            )
            
            agent = await agentic.create_agent(
                agent_class=DimensionLiaisonAgent,
                agent_name=f"Tracked Agent {i}",
                agent_type="liaison",
                realm_name="business_enablement",
                di_container=di_container,
                capabilities=["conversation"],
                required_roles=["test_orchestrator"],
                agui_schema=agui_schema
            )
            agents.append(agent)
        
        # Check all agents are tracked
        assert len(agentic._agents) == 3, "Should track all created agents"
        for i in range(3):
            assert f"Tracked Agent {i}" in agentic._agents, f"Agent {i} should be in registry"

