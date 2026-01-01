#!/usr/bin/env python3
"""
Content Analysis MCP Server Tests

Tests for ContentAnalysisMCPServer in isolation.
Verifies MCP server exposes tools correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.mcp]

class TestContentAnalysisMCPServer:
    """Test ContentAnalysisMCPServer functionality."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator for MCP server."""
        orchestrator = Mock()
        orchestrator.parse_file = AsyncMock(return_value={"success": True})
        orchestrator.list_uploaded_files = AsyncMock(return_value={"success": True})
        orchestrator.get_file_details = AsyncMock(return_value={"success": True})
        orchestrator.process_documents = AsyncMock(return_value={"success": True})
        orchestrator.convert_format = AsyncMock(return_value={"success": True})
        return orchestrator
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    def mcp_server(self, mock_orchestrator, mock_di_container):
        """Create ContentAnalysisMCPServer instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.mcp_server.content_analysis_mcp_server import ContentAnalysisMCPServer
        
        return ContentAnalysisMCPServer(mock_orchestrator, mock_di_container)
    
    @pytest.mark.asyncio
    async def test_mcp_server_initializes(self, mock_orchestrator, mock_di_container):
        """Test MCP server initializes correctly."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.mcp_server.content_analysis_mcp_server import ContentAnalysisMCPServer
        
        mcp_server = ContentAnalysisMCPServer(mock_orchestrator, mock_di_container)
        assert mcp_server.orchestrator == mock_orchestrator
        assert len(mcp_server.tools) > 0
    
    @pytest.mark.asyncio
    async def test_execute_tool_routes_to_orchestrator(self, mcp_server, mock_orchestrator):
        """Test MCP tool execution routes to orchestrator."""
        result = await mcp_server.execute_tool(
            "parse_file_tool",
            {"file_id": "test_file_123"}
        )
        
        assert result["success"] is True
        mock_orchestrator.parse_file.assert_called_once()

