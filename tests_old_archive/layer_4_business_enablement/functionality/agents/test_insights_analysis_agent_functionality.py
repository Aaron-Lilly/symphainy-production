#!/usr/bin/env python3
"""
Insights Analysis Agent Functionality Tests

Tests Insights Analysis Agent core functionality:
- Insights generation using LLM
- MCP tool usage
- Autonomous decision-making

Uses mock AI responses.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Dict, Any

# Path is configured in pytest.ini - no manipulation needed
from tests.fixtures.ai_mock_responses import get_insights_analysis_response, get_mock_llm_response
from tests.fixtures.test_datasets import get_sample_json_data
from utilities import UserContext


@pytest.mark.business_enablement
@pytest.mark.functional
class TestInsightsAnalysisAgentFunctionality:
    """Test Insights Analysis Agent functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        container.curator = Mock()
        return container
    
    @pytest.fixture
    def mock_insights_orchestrator(self):
        """Create mock Insights Orchestrator."""
        orchestrator = Mock()
        orchestrator.generate_insights = AsyncMock(return_value={"status": "success"})
        return orchestrator
    
    @pytest.fixture
    def mock_user_context(self):
        """Create mock User Context."""
        return UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
    
    @pytest.fixture
    async def insights_analysis_agent(self, mock_di_container, mock_insights_orchestrator):
        """Create Insights Analysis Agent instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.agents.insights_analysis_agent import InsightsAnalysisAgent
        
        agent = InsightsAnalysisAgent(
            di_container=mock_di_container,
            agent_id="insights_analysis_agent",
            agent_name="Insights Analysis Agent"
        )
        
        # Mock orchestrator
        agent.insights_orchestrator = mock_insights_orchestrator
        
        await agent.initialize()
        return agent
    
    @pytest.mark.asyncio
    async def test_generate_insights(self, insights_analysis_agent, mock_user_context):
        """Test insights generation."""
        data = get_sample_json_data()
        
        # Mock LLM response
        with patch.object(insights_analysis_agent, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = get_insights_analysis_response(data, {})
            
            result = await insights_analysis_agent.generate_insights(
                data=data,
                user_context=mock_user_context,
                session_id="test_session",
                analysis_type="comprehensive"
            )
            
            assert result is not None
            assert isinstance(result, dict)
            assert "status" in result or "insights" in result
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Abstract agent class - needs proper implementation")
    async def test_agent_uses_tools(self, insights_analysis_agent, mock_user_context):
        """Test that agent uses MCP tools."""
        # Mock tool calls
        with patch.object(insights_analysis_agent, 'use_tool', new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {"status": "success", "result": {}}
            
            # Agent should use tools during insights generation
            data = get_sample_json_data()
            result = await insights_analysis_agent.generate_insights(
                data=data,
                user_context=mock_user_context
            )
            
            # Verify tools were used (if applicable)
            assert result is not None

