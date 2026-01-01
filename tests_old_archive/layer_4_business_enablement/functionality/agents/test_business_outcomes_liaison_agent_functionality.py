#!/usr/bin/env python3
"""
BusinessOutcomesLiaison Functionality Tests

Tests BusinessOutcomesLiaison core functionality.
"""

# Path is configured in pytest.ini - no manipulation needed

import pytest

from unittest.mock import Mock, MagicMock, AsyncMock

    # Fallback: calculate from this file's location
from tests.fixtures.ai_mock_responses import get_mock_llm_response
from utilities import UserContext

@pytest.mark.business_enablement
@pytest.mark.functional
class TestBusinessOutcomesLiaisonAgentFunctionality:
    """Test BusinessOutcomesLiaison functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        container.curator = Mock()
        return container
    
    @pytest.fixture
    def mock_business_outcomes(self):
        orchestrator = Mock()
        return orchestrator
    
    @pytest.fixture
    def mock_user_context(self):
        return UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
    
    @pytest.fixture
    async def business_outcomes_liaison_agent(self, mock_di_container, mock_business_outcomes):

        # Ensure correct path

        # Ensure correct path
        # Ensure path is set - convert to absolute for comparison
        # Path is already set at module level, but ensure it's in sys.path
        # project_root is already absolute, just ensure it's added
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.agents.business_outcomes_liaison_agent import BusinessOutcomesLiaisonAgent
        
        agent = BusinessOutcomesLiaisonAgent(
            di_container=mock_di_container,
            agent_id="business_outcomes_liaison_agent",
            agent_name="BusinessOutcomesLiaison"
        )
        
        agent.business_outcomes = mock_business_outcomes
        
        await agent.initialize()
        return agent
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Abstract agent class - needs proper implementation")
    async def test_agent_initialization(self, business_outcomes_liaison_agent):
        """Test agent initialization."""
        assert business_outcomes_liaison_agent is not None
        assert hasattr(business_outcomes_liaison_agent, 'di_container')
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Abstract agent class - needs proper implementation")
    async def test_agent_uses_tools(self, business_outcomes_liaison_agent, mock_user_context):
        """Test that agent uses MCP tools."""
        # TODO: Add specific test based on agent capabilities
        assert business_outcomes_liaison_agent is not None
