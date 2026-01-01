#!/usr/bin/env python3
"""
Insights Orchestrator Functionality Tests

Tests Insights Orchestrator core functionality:
- Insights generation coordination
- Agent routing
- Multi-service coordination

Uses mock AI responses.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any

# Path is configured in pytest.ini - no manipulation needed
from tests.fixtures.ai_mock_responses import get_insights_analysis_response, get_liaison_agent_response
from tests.fixtures.test_datasets import get_sample_json_data


@pytest.mark.business_enablement
@pytest.mark.functional
class TestInsightsOrchestratorFunctionality:
    """Test Insights Orchestrator functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    def mock_delivery_manager(self, mock_di_container, mock_platform_gateway):
        """Create mock Delivery Manager."""
        manager = Mock()
        manager.realm_name = "business_enablement"
        manager.platform_gateway = mock_platform_gateway
        manager.di_container = mock_di_container
        manager.logger = Mock()
        return manager
    
    @pytest.fixture
    def mock_insights_analysis_agent(self):
        """Create mock Insights Analysis Agent."""
        agent = Mock()
        agent.generate_insights = AsyncMock(return_value={
            "status": "success",
            "insights": []
        })
        return agent
    
    @pytest.fixture
    def mock_insights_liaison_agent(self):
        """Create mock Insights Liaison Agent."""
        agent = Mock()
        agent.route_request = AsyncMock(return_value={
            "status": "success",
            "routed_to": "insights_analysis_agent"
        })
        return agent
    
    @pytest.fixture
    async def insights_orchestrator(self, mock_delivery_manager, mock_insights_analysis_agent, mock_insights_liaison_agent):
        """Create Insights Orchestrator instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
        
        orchestrator = InsightsOrchestrator(
            delivery_manager=mock_delivery_manager
        )
        
        # Mock agents
        orchestrator.insights_analysis_agent = mock_insights_analysis_agent
        orchestrator.insights_liaison_agent = mock_insights_liaison_agent
        
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_generate_insights(self, insights_orchestrator, mock_insights_analysis_agent):
        """Test insights generation coordination."""
        # generate_insights takes resource_id and options, not data/user_context
        result = await insights_orchestrator.generate_insights(
            resource_id="test_resource_id",
            options={"analysis_type": "descriptive", "include_visualization": False}
        )
        
        assert result is not None
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_analyze_content_for_insights(self, insights_orchestrator, mock_insights_liaison_agent):
        """Test content analysis for insights."""
        # Use analyze_content_for_insights which is the primary semantic API method
        result = await insights_orchestrator.analyze_content_for_insights(
            source_type="file",
            file_id="test_file_id",
            content_type="structured",
            analysis_options={"include_visualizations": False}
        )
        
        assert result is not None
        assert isinstance(result, dict)

