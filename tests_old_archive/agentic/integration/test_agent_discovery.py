#!/usr/bin/env python3
"""
Agent Discovery Integration Tests

Tests that agents can discover orchestrators and Smart City services via Curator.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.integration
@pytest.mark.agentic
class TestAgentDiscovery:
    """Test agents discover orchestrators via Curator."""
    
    @pytest.mark.asyncio
    async def test_guide_agent_discovers_orchestrators(self, mock_di_container, mock_curator):
        """Test GuideAgent discovers all 4 MVP orchestrators via Curator."""
        from backend.business_enablement.agents.guide_agent import GuideAgentService
        
        # Mock orchestrators
        mock_content_orch = MagicMock()
        mock_insights_orch = MagicMock()
        mock_operations_orch = MagicMock()
        mock_business_orch = MagicMock()
        
        # Configure Curator to return orchestrators
        async def mock_get_service(name):
            orchestrators = {
                "ContentAnalysisOrchestrator": mock_content_orch,
                "InsightsOrchestrator": mock_insights_orch,
                "OperationsOrchestrator": mock_operations_orch,
                "BusinessOutcomesOrchestrator": mock_business_orch
            }
            if name in orchestrators:
                return orchestrators[name]
            raise Exception(f"Service {name} not found")
        
        mock_curator.get_service = AsyncMock(side_effect=mock_get_service)
        mock_di_container.curator = mock_curator
        
        # Create GuideAgent
        guide_agent = GuideAgentService(
            di_container=mock_di_container,
            platform_gateway=MagicMock()
        )
        
        # Initialize (should discover orchestrators)
        await guide_agent._discover_orchestrators()
        
        # Verify all orchestrators discovered
        assert guide_agent.content_orchestrator is not None
        assert guide_agent.insights_orchestrator is not None
        assert guide_agent.operations_orchestrator is not None
        assert guide_agent.business_outcomes_orchestrator is not None
        
        # Verify they're the right orchestrators
        assert guide_agent.content_orchestrator == mock_content_orch
        assert guide_agent.insights_orchestrator == mock_insights_orch
        assert guide_agent.operations_orchestrator == mock_operations_orch
        assert guide_agent.business_outcomes_orchestrator == mock_business_orch
    
    @pytest.mark.asyncio
    async def test_content_liaison_discovers_orchestrator(self, mock_di_container, mock_curator):
        """Test Content Liaison Agent discovers ContentAnalysisOrchestrator via Curator."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.agents import ContentLiaisonAgent
        
        # Mock orchestrator
        mock_content_orch = MagicMock()
        
        # Configure Curator
        mock_curator.get_service = AsyncMock(return_value=mock_content_orch)
        mock_di_container.curator = mock_curator
        
        # Create Content Liaison Agent
        liaison = ContentLiaisonAgent(di_container=mock_di_container)
        
        # Initialize
        await liaison.initialize()
        
        # Verify orchestrator discovered
        assert liaison.content_orchestrator is not None
        assert liaison.content_orchestrator == mock_content_orch
        assert liaison.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_insights_liaison_discovers_orchestrator(self, mock_di_container, mock_curator):
        """Test Insights Liaison Agent discovers InsightsOrchestrator via Curator."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator.agents import InsightsLiaisonAgent
        
        # Mock orchestrator
        mock_insights_orch = MagicMock()
        
        # Configure Curator
        mock_curator.get_service = AsyncMock(return_value=mock_insights_orch)
        mock_di_container.curator = mock_curator
        
        # Create Insights Liaison Agent
        liaison = InsightsLiaisonAgent(di_container=mock_di_container)
        
        # Initialize
        await liaison.initialize()
        
        # Verify orchestrator discovered
        assert liaison.insights_orchestrator is not None
        assert liaison.insights_orchestrator == mock_insights_orch
        assert liaison.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_operations_liaison_discovers_orchestrator(self, mock_di_container, mock_curator):
        """Test Operations Liaison Agent discovers OperationsOrchestrator via Curator."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator.agents import OperationsLiaisonAgent
        
        # Mock orchestrator
        mock_operations_orch = MagicMock()
        
        # Configure Curator
        mock_curator.get_service = AsyncMock(return_value=mock_operations_orch)
        mock_di_container.curator = mock_curator
        
        # Create Operations Liaison Agent
        liaison = OperationsLiaisonAgent(di_container=mock_di_container)
        
        # Initialize
        await liaison.initialize()
        
        # Verify orchestrator discovered
        assert liaison.operations_orchestrator is not None
        assert liaison.operations_orchestrator == mock_operations_orch
        assert liaison.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_business_outcomes_liaison_discovers_orchestrator(self, mock_di_container, mock_curator):
        """Test Business Outcomes Liaison Agent discovers BusinessOutcomesOrchestrator via Curator."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator.agents import BusinessOutcomesLiaisonAgent
        
        # Mock orchestrator
        mock_business_orch = MagicMock()
        
        # Configure Curator
        mock_curator.get_service = AsyncMock(return_value=mock_business_orch)
        mock_di_container.curator = mock_curator
        
        # Create Business Outcomes Liaison Agent
        liaison = BusinessOutcomesLiaisonAgent(di_container=mock_di_container)
        
        # Initialize
        await liaison.initialize()
        
        # Verify orchestrator discovered
        assert liaison.business_outcomes_orchestrator is not None
        assert liaison.business_outcomes_orchestrator == mock_business_orch
        assert liaison.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_agent_handles_missing_orchestrator_gracefully(self, mock_di_container, mock_curator):
        """Test agents handle missing orchestrators gracefully without crashing."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.agents import ContentLiaisonAgent
        
        # Configure Curator to raise exception (orchestrator not found)
        mock_curator.get_service = AsyncMock(side_effect=Exception("Orchestrator not found"))
        mock_di_container.curator = mock_curator
        
        # Create Content Liaison Agent
        liaison = ContentLiaisonAgent(di_container=mock_di_container)
        
        # Initialize (should not crash)
        await liaison.initialize()
        
        # Verify agent is initialized but orchestrator is None
        assert liaison.is_initialized is True
        assert liaison.content_orchestrator is None  # Not available, but agent still works
    
    @pytest.mark.asyncio
    async def test_all_liaison_agents_discover_orchestrators(self, mock_di_container, mock_curator):
        """Test all 4 liaison agents can discover their orchestrators."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.agents import ContentLiaisonAgent
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator.agents import InsightsLiaisonAgent
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator.agents import OperationsLiaisonAgent
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator.agents import BusinessOutcomesLiaisonAgent
        
        # Mock orchestrators
        orchestrators = {
            "ContentAnalysisOrchestrator": MagicMock(),
            "InsightsOrchestrator": MagicMock(),
            "OperationsOrchestrator": MagicMock(),
            "BusinessOutcomesOrchestrator": MagicMock()
        }
        
        # Configure Curator
        mock_curator.get_service = AsyncMock(side_effect=lambda name: orchestrators[name])
        mock_di_container.curator = mock_curator
        
        # Create all liaison agents
        liaisons = [
            ContentLiaisonAgent(di_container=mock_di_container),
            InsightsLiaisonAgent(di_container=mock_di_container),
            OperationsLiaisonAgent(di_container=mock_di_container),
            BusinessOutcomesLiaisonAgent(di_container=mock_di_container)
        ]
        
        # Initialize all
        for liaison in liaisons:
            await liaison.initialize()
        
        # Verify all initialized and discovered orchestrators
        assert liaisons[0].content_orchestrator is not None
        assert liaisons[1].insights_orchestrator is not None
        assert liaisons[2].operations_orchestrator is not None
        assert liaisons[3].business_outcomes_orchestrator is not None
        
        # Verify all marked as initialized
        for liaison in liaisons:
            assert liaison.is_initialized is True

