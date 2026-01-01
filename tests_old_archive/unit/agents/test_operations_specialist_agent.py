#!/usr/bin/env python3
"""
Operations Specialist Agent Tests

Tests for OperationsSpecialistAgent in isolation.
Verifies agent uses MCP tools correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.agents]

class TestOperationsSpecialistAgent:
    """Test OperationsSpecialistAgent functionality."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator for agent."""
        orchestrator = Mock()
        orchestrator.mcp_server = Mock()
        orchestrator.mcp_server.execute_tool = AsyncMock(return_value={"success": True})
        return orchestrator
    
    @pytest.fixture
    async def agent(self, mock_orchestrator):
        """Create OperationsSpecialistAgent instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.agents.operations_specialist_agent import OperationsSpecialistAgent
        
        agent = OperationsSpecialistAgent(
            agent_id="test_agent_123",
            capabilities=[],
            di_container=Mock()
        )
        agent.set_orchestrator(mock_orchestrator)
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_uses_mcp_tools(self, agent, mock_orchestrator):
        """Test agent uses MCP tools, not direct orchestrator calls."""
        result = await agent.refine_sop(
            sop_id="sop_123",
            refinement_context={}
        )
        
        assert isinstance(result, dict)
        # Verify MCP tool was called
        assert mock_orchestrator.mcp_server.execute_tool.called

