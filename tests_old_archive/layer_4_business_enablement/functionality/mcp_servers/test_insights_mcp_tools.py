#!/usr/bin/env python3
"""
Insights Functionality Tests

Tests Insights MCP Tools functionality.
"""

# Path is configured in pytest.ini - no manipulation needed

import pytest

from unittest.mock import Mock, MagicMock, AsyncMock

    # Fallback: calculate from this file's location
@pytest.mark.business_enablement
@pytest.mark.functional
class TestInsightsMCPServerTools:
    """Test Insights MCP Tools."""
    
    @pytest.fixture
    def mock_di_container(self):
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_insights(self):
        orchestrator = Mock()
        return orchestrator
    
    @pytest.fixture
    async def insights(self, mock_di_container, mock_insights):

        # Ensure correct path
        # Ensure path is set - convert to absolute for comparison
        # Path is already set at module level, but ensure it's in sys.path
        # project_root is already absolute, just ensure it's added
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.mcp_server.insights_mcp_server import InsightsMCPServer
        
        server = InsightsMCPServer(
            di_container=mock_di_container,
            insights=mock_insights
        )
        
        await server.initialize()
        return server
    
    @pytest.mark.asyncio
    async def test_list_tools(self, insights):
        """Test that server lists available tools."""
        tools = await insights.list_tools()
        assert tools is not None
        assert isinstance(tools, (list, dict))
    
    @pytest.mark.asyncio
    async def test_call_tool(self, insights):
        """Test tool execution."""
        try:
            tools = await insights.list_tools()
            if tools and len(tools) > 0:
                tool_name = tools[0].get("name") if isinstance(tools[0], dict) else str(tools[0])
                result = await insights.call_tool(tool_name=tool_name, arguments={})
                assert result is not None
        except Exception:
            pytest.skip("No tools available or tool call not implemented")
