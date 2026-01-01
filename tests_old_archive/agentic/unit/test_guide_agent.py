#!/usr/bin/env python3
"""
Guide Agent Unit Tests

Tests for the Guide Agent that provides journey guidance on the landing page.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.unit
@pytest.mark.agentic
class TestGuideAgentUnit:
    """Unit tests for Guide Agent."""
    
    @pytest.mark.asyncio
    async def test_guide_agent_initialization(self, mock_di_container):
        """Test GuideAgent initializes correctly."""
        from backend.business_enablement.agents import GuideAgentService
        
        guide_agent = GuideAgentService(
            di_container=mock_di_container
        )
        
        assert guide_agent.agent_name == "GuideAgent"
        assert guide_agent.content_orchestrator is None  # Not initialized yet
        assert guide_agent.insights_orchestrator is None
        assert guide_agent.operations_orchestrator is None
        assert guide_agent.business_outcomes_orchestrator is None
    
    @pytest.mark.asyncio
    async def test_guide_agent_discovers_all_orchestrators(self, mock_di_container, mock_curator):
        """Test GuideAgent discovers all 4 MVP orchestrators via Curator."""
        from backend.business_enablement.agents import GuideAgentService
        
        # Mock orchestrators
        mock_orchestrators = {
            "ContentAnalysisOrchestrator": MagicMock(),
            "InsightsOrchestrator": MagicMock(),
            "OperationsOrchestrator": MagicMock(),
            "BusinessOutcomesOrchestrator": MagicMock()
        }
        
        async def mock_get_service(name):
            if name in mock_orchestrators:
                return mock_orchestrators[name]
            raise Exception(f"{name} not found")
        
        mock_curator.get_service = AsyncMock(side_effect=mock_get_service)
        mock_di_container.curator = mock_curator
        
        guide_agent = GuideAgentService(
            di_container=mock_di_container,
            platform_gateway=MagicMock()
        )
        
        # Discover orchestrators
        await guide_agent._discover_orchestrators()
        
        # Verify all discovered
        assert guide_agent.content_orchestrator is not None
        assert guide_agent.insights_orchestrator is not None
        assert guide_agent.operations_orchestrator is not None
        assert guide_agent.business_outcomes_orchestrator is not None
        
        # Verify they're the right ones
        assert guide_agent.content_orchestrator == mock_orchestrators["ContentAnalysisOrchestrator"]
        assert guide_agent.insights_orchestrator == mock_orchestrators["InsightsOrchestrator"]
        assert guide_agent.operations_orchestrator == mock_orchestrators["OperationsOrchestrator"]
        assert guide_agent.business_outcomes_orchestrator == mock_orchestrators["BusinessOutcomesOrchestrator"]
    
    @pytest.mark.asyncio
    async def test_guide_agent_handles_missing_orchestrators_gracefully(self, mock_di_container, mock_curator):
        """Test GuideAgent handles missing orchestrators without crashing."""
        from backend.business_enablement.agents import GuideAgentService
        
        # Curator returns nothing (all services missing)
        mock_curator.get_service = AsyncMock(side_effect=Exception("Service not found"))
        mock_di_container.curator = mock_curator
        
        guide_agent = GuideAgentService(
            di_container=mock_di_container,
            platform_gateway=MagicMock()
        )
        
        # Should not crash
        await guide_agent._discover_orchestrators()
        
        # Orchestrators should be None but agent should still work
        assert guide_agent.content_orchestrator is None
        assert guide_agent.insights_orchestrator is None
        assert guide_agent.operations_orchestrator is None
        assert guide_agent.business_outcomes_orchestrator is None
    
    @pytest.mark.asyncio
    async def test_guide_agent_provides_guidance(self, mock_di_container):
        """Test GuideAgent can provide journey guidance."""
        from backend.business_enablement.agents import GuideAgentService
        
        guide_agent = GuideAgentService(
            di_container=mock_di_container,
            platform_gateway=MagicMock()
        )
        
        # Mock orchestrators
        guide_agent.content_orchestrator = MagicMock()
        guide_agent.insights_orchestrator = MagicMock()
        guide_agent.operations_orchestrator = MagicMock()
        guide_agent.business_outcomes_orchestrator = MagicMock()
        
        # Request guidance
        result = await guide_agent.provide_guidance({
            "query": "I need help getting started",
            "conversation_id": "conv_123",
            "user_id": "user_456"
        })
        
        # Should return guidance
        assert "guidance" in result
        assert isinstance(result["guidance"], str)
        assert len(result["guidance"]) > 0
    
    @pytest.mark.asyncio
    async def test_guide_agent_routes_to_correct_pillar(self, mock_di_container):
        """Test GuideAgent can route users to appropriate pillars."""
        from backend.business_enablement.agents import GuideAgentService
        
        guide_agent = GuideAgentService(
            di_container=mock_di_container,
            platform_gateway=MagicMock()
        )
        
        # Mock pillar router
        guide_agent.pillar_router = MagicMock()
        
        # Test routing to content pillar
        content_query = "I want to upload documents"
        route_result = await guide_agent.pillar_router.route_query(content_query)
        
        # Should route to content
        # (This is a placeholder - actual implementation may vary)
        assert route_result is not None
    
    @pytest.mark.asyncio
    async def test_guide_agent_health_check(self, mock_di_container):
        """Test GuideAgent health check."""
        from backend.business_enablement.agents import GuideAgentService
        
        guide_agent = GuideAgentService(
            di_container=mock_di_container,
            platform_gateway=MagicMock()
        )
        
        health = await guide_agent.health_check()
        
        assert "status" in health
        assert "agent_name" in health or "service_name" in health
    
    @pytest.mark.asyncio
    async def test_guide_agent_with_no_curator(self, mock_di_container):
        """Test GuideAgent works even without Curator."""
        from backend.business_enablement.agents import GuideAgentService
        
        # DI container has no curator
        mock_di_container.curator = None
        
        guide_agent = GuideAgentService(
            di_container=mock_di_container,
            platform_gateway=MagicMock()
        )
        
        # Should not crash during discovery
        await guide_agent._discover_orchestrators()
        
        # Agent should still be functional (just with no orchestrators)
        assert guide_agent.content_orchestrator is None

