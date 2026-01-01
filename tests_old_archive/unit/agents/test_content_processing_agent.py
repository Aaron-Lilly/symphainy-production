#!/usr/bin/env python3
"""
Content Processing Agent Tests

Tests for ContentProcessingAgent in isolation.
Verifies agent uses MCP tools correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.agents]

class TestContentProcessingAgent:
    """Test ContentProcessingAgent functionality."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator for agent."""
        orchestrator = Mock()
        orchestrator.mcp_server = Mock()
        orchestrator.mcp_server.execute_tool = AsyncMock(return_value={"success": True})
        return orchestrator
    
    @pytest.fixture
    async def agent(self, mock_orchestrator):
        """Create ContentProcessingAgent instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.agents.content_processing_agent import ContentProcessingAgent
        
        agent = ContentProcessingAgent(
            agent_id="test_agent_123",
            capabilities=[],
            di_container=Mock()
        )
        agent.set_orchestrator(mock_orchestrator)
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_uses_mcp_tools(self, agent, mock_orchestrator):
        """Test agent uses MCP tools, not direct orchestrator calls."""
        result = await agent.enhance_metadata_extraction(
            file_id="test_file_123",
            parsed_data={}
        )
        
        assert isinstance(result, dict)
        # Verify MCP tool was called
        assert mock_orchestrator.mcp_server.execute_tool.called

