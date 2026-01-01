#!/usr/bin/env python3
"""
Business Outcomes MCP Server Tests

Tests for BusinessOutcomesMCPServer in isolation.
Verifies MCP server exposes tools correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.mcp]

class TestBusinessOutcomesMCPServer:
    """Test BusinessOutcomesMCPServer functionality."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator for MCP server."""
        orchestrator = Mock()
        orchestrator.generate_strategic_roadmap = AsyncMock(return_value={"success": True})
        orchestrator.generate_poc_proposal = AsyncMock(return_value={"success": True})
        orchestrator.create_comprehensive_strategic_plan = AsyncMock(return_value={"success": True})
        orchestrator.track_strategic_progress = AsyncMock(return_value={"success": True})
        orchestrator.analyze_strategic_trends = AsyncMock(return_value={"success": True})
        return orchestrator
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    def mcp_server(self, mock_orchestrator, mock_di_container):
        """Create BusinessOutcomesMCPServer instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.mcp_server.business_outcomes_mcp_server import BusinessOutcomesMCPServer
        
        return BusinessOutcomesMCPServer(mock_orchestrator, mock_di_container)
    
    @pytest.mark.asyncio
    async def test_mcp_server_initializes(self, mock_orchestrator, mock_di_container):
        """Test MCP server initializes correctly."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.mcp_server.business_outcomes_mcp_server import BusinessOutcomesMCPServer
        
        mcp_server = BusinessOutcomesMCPServer(mock_orchestrator, mock_di_container)
        assert mcp_server.orchestrator == mock_orchestrator
        assert len(mcp_server.tools) > 0
    
    @pytest.mark.asyncio
    async def test_execute_tool_routes_to_orchestrator(self, mcp_server, mock_orchestrator):
        """Test MCP tool execution routes to orchestrator."""
        result = await mcp_server.execute_tool(
            "generate_strategic_roadmap_tool",
            {"business_context": {"objectives": ["obj1"]}}
        )
        
        assert result["success"] is True
        mock_orchestrator.generate_strategic_roadmap.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_poc_proposal_tool(self, mcp_server, mock_orchestrator):
        """Test POC proposal tool execution."""
        result = await mcp_server.execute_tool(
            "generate_poc_proposal_tool",
            {"pillar_outputs": {}}
        )
        
        assert result["success"] is True
        mock_orchestrator.generate_poc_proposal.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_strategic_plan_tool(self, mcp_server, mock_orchestrator):
        """Test strategic plan tool execution."""
        result = await mcp_server.execute_tool(
            "create_comprehensive_strategic_plan_tool",
            {"context_data": {}}
        )
        
        assert result["success"] is True
        mock_orchestrator.create_comprehensive_strategic_plan.assert_called_once()

