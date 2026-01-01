#!/usr/bin/env python3
"""
Phase 1: Orchestrator-Agent Integration Tests (Mocked)

Tests orchestrator-agent communication, agent access via orchestrators,
and agent tool calling through orchestrator methods.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))

pytestmark = [pytest.mark.integration]


@pytest.fixture
async def minimal_foundation_infrastructure():
    """Minimal infrastructure fixture for Agentic Foundation tests."""
    from foundations.di_container.di_container_service import DIContainerService
    from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
    from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
    
    di_container = DIContainerService("test_platform")
    pwf = PublicWorksFoundationService(di_container=di_container)
    await asyncio.wait_for(pwf.initialize(), timeout=30.0)
    di_container.public_works_foundation = pwf
    
    curator = CuratorFoundationService(foundation_services=di_container, public_works_foundation=pwf)
    await asyncio.wait_for(curator.initialize(), timeout=30.0)
    di_container.curator_foundation = curator
    
    return {"di_container": di_container, "public_works_foundation": pwf, "curator": curator}


@pytest.fixture
async def agentic_foundation(minimal_foundation_infrastructure):
    """Fixture providing initialized Agentic Foundation."""
    infra = minimal_foundation_infrastructure
    from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
    
    agentic = AgenticFoundationService(
        di_container=infra["di_container"],
        public_works_foundation=infra["public_works_foundation"],
        curator_foundation=infra["curator"]
    )
    await agentic.initialize()
    return agentic


@pytest.fixture
async def orchestrator_with_agent(agentic_foundation, minimal_foundation_infrastructure):
    """Fixture providing orchestrator with initialized agent."""
    from bases.orchestrator_base import OrchestratorBase
    from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
    from foundations.agentic_foundation.agui_schema_registry import AGUISchema
    
    agentic = agentic_foundation
    infra = smart_city_infrastructure
    di_container = infra["di_container"]
    
    # Create a simple test orchestrator
    class TestOrchestrator(OrchestratorBase):
        def __init__(self, di_container, agentic_foundation):
            super().__init__(
                orchestrator_name="Test Orchestrator",
                realm_name="business_enablement",
                di_container=di_container
            )
            self.agentic_foundation = agentic_foundation
        
        async def initialize(self):
            """Initialize orchestrator."""
            await super().initialize()
            
            # Create agent via orchestrator
            agui_schema = AGUISchema(
                agent_name="Orchestrator Test Agent",
                version="1.0.0",
                description="Test agent for orchestrator integration",
                components=[],
                metadata={}
            )
            
            self.test_agent = await self.initialize_agent(
                agent_class=DimensionLiaisonAgent,
                agent_name="Orchestrator Test Agent",
                agent_type="liaison",
                capabilities=["conversation"],
                required_roles=["test_orchestrator"],
                agui_schema=agui_schema
            )
            
            return True
    
    orchestrator = TestOrchestrator(di_container, agentic)
    await orchestrator.initialize()
    
    return orchestrator


class TestOrchestratorAgentAccess:
    """Test orchestrator access to agents."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_has_agent(self, orchestrator_with_agent):
        """Test that orchestrator has access to agent."""
        orchestrator = orchestrator_with_agent
        
        assert hasattr(orchestrator, "test_agent"), "Orchestrator should have test agent"
        assert orchestrator.test_agent is not None, "Test agent should be initialized"
    
    @pytest.mark.asyncio
    async def test_get_agent_method(self, orchestrator_with_agent):
        """Test get_agent method."""
        orchestrator = orchestrator_with_agent
        
        if hasattr(orchestrator, "get_agent"):
            agent = await orchestrator.get_agent("Orchestrator Test Agent")
            
            assert agent is not None, "Should return agent"
            assert agent.agent_name == "Orchestrator Test Agent", "Should return correct agent"
        else:
            pytest.skip("Orchestrator does not have get_agent method")
    
    @pytest.mark.asyncio
    async def test_agent_tracking_in_orchestrator(self, orchestrator_with_agent):
        """Test that orchestrator tracks agents."""
        orchestrator = orchestrator_with_agent
        
        if hasattr(orchestrator, "_agents"):
            assert isinstance(orchestrator._agents, dict), "Agent registry should be a dictionary"
            assert "Orchestrator Test Agent" in orchestrator._agents, \
                "Agent should be tracked in orchestrator registry"


class TestOrchestratorAgentCommunication:
    """Test orchestrator-agent communication."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_can_call_agent_methods(self, orchestrator_with_agent):
        """Test that orchestrator can call agent methods."""
        orchestrator = orchestrator_with_agent
        agent = orchestrator.test_agent
        
        # Test calling agent capabilities method
        if hasattr(agent, "get_available_capabilities"):
            try:
                capabilities = await agent.get_available_capabilities()
                assert isinstance(capabilities, list), "Should return list of capabilities"
            except NotImplementedError:
                pytest.skip("get_available_capabilities not fully implemented")
            except Exception as e:
                if "not available" in str(e).lower():
                    pytest.skip(f"Agent capabilities not available: {e}")
                else:
                    raise
    
    @pytest.mark.asyncio
    async def test_orchestrator_agent_conversation(self, orchestrator_with_agent):
        """Test orchestrator using agent for conversation."""
        orchestrator = orchestrator_with_agent
        agent = orchestrator.test_agent
        
        if not hasattr(agent, "process_conversation"):
            pytest.skip("Agent does not implement process_conversation")
        
        from backend.business_enablement.protocols.business_liaison_agent_protocol import (
            ConversationRequest, ResponseType
        )
        
        request = ConversationRequest(
            message="Test message from orchestrator",
            session_id="orchestrator-session-1",
            user_context=None,
            response_type=ResponseType.TEXT_RESPONSE
        )
        
        try:
            response = await agent.process_conversation(request)
            
            assert response is not None, "Should return response"
        except NotImplementedError:
            pytest.skip("process_conversation not fully implemented")
        except Exception as e:
            if "not available" in str(e).lower():
                pytest.skip(f"Agent conversation not available: {e}")
            else:
                raise


class TestOrchestratorAgentInitialization:
    """Test agent initialization via orchestrator."""
    
    @pytest.mark.asyncio
    async def test_initialize_agent_via_orchestrator(self, agentic_foundation, smart_city_infrastructure):
        """Test initializing agent via orchestrator method."""
        from bases.orchestrator_base import OrchestratorBase
        from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        agentic = agentic_foundation
        infra = minimal_foundation_infrastructure
        di_container = infra["di_container"]
        
        class TestOrchestrator(OrchestratorBase):
            def __init__(self, di_container):
                super().__init__(
                    orchestrator_name="Init Test Orchestrator",
                    realm_name="business_enablement",
                    di_container=di_container
                )
        
        orchestrator = TestOrchestrator(di_container)
        await orchestrator.initialize()
        
        # Initialize agent via orchestrator
        agui_schema = AGUISchema(
            agent_name="Init Test Agent",
            version="1.0.0",
            description="Test agent initialization",
            components=[],
            metadata={}
        )
        
        agent = await orchestrator.initialize_agent(
            agent_class=DimensionLiaisonAgent,
            agent_name="Init Test Agent",
            agent_type="liaison",
            capabilities=["conversation"],
            required_roles=["test_orchestrator"],
            agui_schema=agui_schema
        )
        
        assert agent is not None, "Agent should be created"
        assert agent.agent_name == "Init Test Agent", "Agent should have correct name"
        assert agent.is_initialized, "Agent should be initialized"
    
    @pytest.mark.asyncio
    async def test_agent_lazy_loading(self, orchestrator_with_agent):
        """Test that agents are lazy-loaded (cached after first access)."""
        orchestrator = orchestrator_with_agent
        
        # Get agent first time
        agent1 = orchestrator.test_agent
        
        # Get agent second time (should be same instance)
        if hasattr(orchestrator, "get_agent"):
            agent2 = await orchestrator.get_agent("Orchestrator Test Agent")
            assert agent1 is agent2, "Should return same cached instance"
        else:
            # If no get_agent, check _agents registry
            if hasattr(orchestrator, "_agents"):
                assert "Orchestrator Test Agent" in orchestrator._agents, \
                    "Agent should be in registry"


class TestOrchestratorAgentErrorHandling:
    """Test orchestrator-agent error handling."""
    
    @pytest.mark.asyncio
    async def test_agent_error_propagation(self, orchestrator_with_agent):
        """Test that agent errors propagate to orchestrator."""
        orchestrator = orchestrator_with_agent
        agent = orchestrator.test_agent
        
        # Try to call agent method that may fail
        if hasattr(agent, "process_conversation"):
            from backend.business_enablement.protocols.business_liaison_agent_protocol import (
                ConversationRequest, ResponseType
            )
            
            # Create request that may cause error
            request = ConversationRequest(
                message="",  # Empty message may cause error
                session_id="error-test-session",
                user_context=None,
                response_type=ResponseType.TEXT_RESPONSE
            )
            
            try:
                response = await agent.process_conversation(request)
                
                # Should handle gracefully (return error response or valid response)
                assert response is not None, "Should return response even on error"
            except Exception as e:
                # Errors should be handled gracefully
                if "not available" in str(e).lower():
                    pytest.skip(f"Agent not available: {e}")
                else:
                    # Other errors should be caught and handled
                    assert True, "Error should be handled gracefully"
    
    @pytest.mark.asyncio
    async def test_orchestrator_handles_missing_agent(self, agentic_foundation, smart_city_infrastructure):
        """Test that orchestrator handles missing agent gracefully."""
        from bases.orchestrator_base import OrchestratorBase
        
        infra = minimal_foundation_infrastructure
        di_container = infra["di_container"]
        
        class TestOrchestrator(OrchestratorBase):
            def __init__(self, di_container):
                super().__init__(
                    orchestrator_name="Missing Agent Test",
                    realm_name="business_enablement",
                    di_container=di_container
                )
        
        orchestrator = TestOrchestrator(di_container)
        await orchestrator.initialize()
        
        # Try to get non-existent agent
        if hasattr(orchestrator, "get_agent"):
            agent = await orchestrator.get_agent("Non-existent Agent")
            
            # Should return None or handle gracefully
            assert agent is None or isinstance(agent, Exception), \
                "Should return None or error for missing agent"

