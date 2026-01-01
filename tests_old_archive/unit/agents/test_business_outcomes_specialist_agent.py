#!/usr/bin/env python3
"""
Business Outcomes Specialist Agent Tests

Tests for BusinessOutcomesSpecialistAgent in isolation.
Verifies agent uses MCP tools correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.agents]

class TestBusinessOutcomesSpecialistAgent:
    """Test BusinessOutcomesSpecialistAgent functionality."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator for agent."""
        orchestrator = Mock()
        orchestrator.mcp_server = Mock()
        orchestrator.mcp_server.execute_tool = AsyncMock(return_value={"success": True})
        return orchestrator
    
    @pytest.fixture
    async def agent(self, mock_orchestrator):
        """Create BusinessOutcomesSpecialistAgent instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.agents.business_outcomes_specialist_agent import BusinessOutcomesSpecialistAgent
        
        agent = BusinessOutcomesSpecialistAgent(
            agent_id="test_agent_123",
            capabilities=[],
            di_container=Mock()
        )
        agent.set_orchestrator(mock_orchestrator)
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_uses_mcp_tools(self, agent, mock_orchestrator):
        """Test agent uses MCP tools, not direct orchestrator calls."""
        result = await agent.refine_poc_proposal(
            base_proposal={"proposal": "test"},
            context={}
        )
        
        assert isinstance(result, dict)
        # Verify MCP tool was called
        assert mock_orchestrator.mcp_server.execute_tool.called
    
    @pytest.mark.asyncio
    async def test_agent_enhances_strategic_roadmap(self, agent, mock_orchestrator):
        """Test agent enhances strategic roadmap using MCP tools."""
        result = await agent.enhance_strategic_roadmap(
            roadmap={"phases": []},
            context={}
        )
        
        assert isinstance(result, dict)
        # Verify MCP tool was called
        assert mock_orchestrator.mcp_server.execute_tool.called

