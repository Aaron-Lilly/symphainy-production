#!/usr/bin/env python3
"""
Operations MCP Server Tests

Tests for OperationsMCPServer in isolation.
Verifies MCP server exposes tools correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.mcp]

class TestOperationsMCPServer:
    """Test OperationsMCPServer functionality."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator for MCP server."""
        orchestrator = Mock()
        orchestrator.generate_workflow_from_sop = AsyncMock(return_value={"success": True})
        orchestrator.visualize_workflow = AsyncMock(return_value={"success": True})
        return orchestrator
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    def mcp_server(self, mock_orchestrator, mock_di_container):
        """Create OperationsMCPServer instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.mcp_server.operations_mcp_server import OperationsMCPServer
        
        return OperationsMCPServer(mock_orchestrator, mock_di_container)
    
    @pytest.mark.asyncio
    async def test_mcp_server_initializes(self, mock_orchestrator, mock_di_container):
        """Test MCP server initializes correctly."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.mcp_server.operations_mcp_server import OperationsMCPServer
        
        mcp_server = OperationsMCPServer(mock_orchestrator, mock_di_container)
        assert mcp_server.orchestrator == mock_orchestrator
        assert len(mcp_server.tools) > 0
    
    @pytest.mark.asyncio
    async def test_execute_tool_routes_to_orchestrator(self, mcp_server, mock_orchestrator):
        """Test MCP tool execution routes to orchestrator."""
        result = await mcp_server.execute_tool(
            "generate_workflow_from_sop_tool",
            {"sop_id": "sop_123"}
        )
        
        assert result["success"] is True
        mock_orchestrator.generate_workflow_from_sop.assert_called_once()

