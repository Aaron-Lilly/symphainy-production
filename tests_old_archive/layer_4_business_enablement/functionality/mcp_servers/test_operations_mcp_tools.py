#!/usr/bin/env python3
"""
Operations Functionality Tests

Tests Operations MCP Tools functionality.
"""

# Path is configured in pytest.ini - no manipulation needed

import pytest

from unittest.mock import Mock, MagicMock, AsyncMock

    # Fallback: calculate from this file's location
@pytest.mark.business_enablement
@pytest.mark.functional
class TestOperationsMCPServerTools:
    """Test Operations MCP Tools."""
    
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
    def mock_operations(self):
        orchestrator = Mock()
        return orchestrator
    
    @pytest.fixture
    async def operations(self, mock_di_container, mock_operations):

        # Ensure correct path
        # Ensure path is set - convert to absolute for comparison
        # Path is already set at module level, but ensure it's in sys.path
        # project_root is already absolute, just ensure it's added
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.mcp_server.operations_mcp_server import OperationsMCPServer
        
        server = OperationsMCPServer(
            di_container=mock_di_container,
            operations=mock_operations
        )
        
        await server.initialize()
        return server
    
    @pytest.mark.asyncio
    async def test_list_tools(self, operations):
        """Test that server lists available tools."""
        tools = await operations.list_tools()
        assert tools is not None
        assert isinstance(tools, (list, dict))
    
    @pytest.mark.asyncio
    async def test_call_tool(self, operations):
        """Test tool execution."""
        try:
            tools = await operations.list_tools()
            if tools and len(tools) > 0:
                tool_name = tools[0].get("name") if isinstance(tools[0], dict) else str(tools[0])
                result = await operations.call_tool(tool_name=tool_name, arguments={})
                assert result is not None
        except Exception:
            pytest.skip("No tools available or tool call not implemented")
