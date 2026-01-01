#!/usr/bin/env python3
"""
Tests for MCP Server Protocols.

Tests the MCP server protocol definitions, base classes, and data models
for Smart City MCP servers.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Callable
from unittest.mock import Mock, AsyncMock

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add the symphainy-platform path
platform_path = project_root / "symphainy-source" / "symphainy-platform"
sys.path.insert(0, str(platform_path))

from backend.smart_city.protocols import (
    MCPServerProtocol,
    MCPBaseServer,
    MCPTool,
    MCPServerInfo
)
from foundations.utility_foundation.utilities import UserContext
from .test_base import SmartCityProtocolsTestBase


class TestMCPTool:
    """Test MCPTool data model."""
    
    def test_mcp_tool_creation(self):
        """Test creating an MCP tool."""
        def test_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "success", "input": input_data}
        
        tool = MCPTool(
            name="test_tool",
            description="A test MCP tool",
            input_schema={
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Input data"}
                },
                "required": ["input"]
            },
            handler=test_handler,
            tags=["test", "mcp"]
        )
        
        assert tool.name == "test_tool"
        assert tool.description == "A test MCP tool"
        assert tool.input_schema["type"] == "object"
        assert tool.input_schema["properties"]["input"]["type"] == "string"
        assert tool.handler == test_handler
        assert "test" in tool.tags
        assert "mcp" in tool.tags
    
    def test_mcp_tool_defaults(self):
        """Test MCP tool with default values."""
        def minimal_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "minimal"}
        
        tool = MCPTool(
            name="minimal_tool",
            description="A minimal MCP tool",
            input_schema={"type": "object"},
            handler=minimal_handler
        )
        
        assert tool.name == "minimal_tool"
        assert tool.description == "A minimal MCP tool"
        assert tool.input_schema["type"] == "object"
        assert tool.handler == minimal_handler
        assert tool.tags == []
    
    def test_mcp_tool_serialization(self):
        """Test MCP tool serialization."""
        from dataclasses import asdict
        
        def serializable_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "serializable"}
        
        tool = MCPTool(
            name="serializable_tool",
            description="Test serialization",
            input_schema={"type": "object"},
            handler=serializable_handler,
            tags=["serialization"]
        )
        
        tool_dict = asdict(tool)
        
        assert isinstance(tool_dict, dict)
        assert tool_dict["name"] == "serializable_tool"
        assert tool_dict["description"] == "Test serialization"
        assert tool_dict["input_schema"]["type"] == "object"
        assert tool_dict["tags"] == ["serialization"]
        # Note: handler is a function and won't serialize properly with asdict


class TestMCPServerInfo:
    """Test MCPServerInfo data model."""
    
    def test_mcp_server_info_creation(self):
        """Test creating MCP server info."""
        def tool1_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "tool1"}
        
        def tool2_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "tool2"}
        
        tools = [
            MCPTool(
                name="tool1",
                description="First tool",
                input_schema={"type": "object"},
                handler=tool1_handler
            ),
            MCPTool(
                name="tool2",
                description="Second tool",
                input_schema={"type": "object"},
                handler=tool2_handler
            )
        ]
        
        server_info = MCPServerInfo(
            server_name="test_server",
            version="1.0.0",
            description="A test MCP server",
            interface_name="TestMCPServerInterface",
            tools=tools,
            capabilities=["tool_execution", "data_processing"]
        )
        
        assert server_info.server_name == "test_server"
        assert server_info.version == "1.0.0"
        assert server_info.description == "A test MCP server"
        assert server_info.interface_name == "TestMCPServerInterface"
        assert len(server_info.tools) == 2
        assert server_info.tools[0].name == "tool1"
        assert server_info.tools[1].name == "tool2"
        assert "tool_execution" in server_info.capabilities
        assert "data_processing" in server_info.capabilities
    
    def test_mcp_server_info_defaults(self):
        """Test MCP server info with default values."""
        server_info = MCPServerInfo(
            server_name="minimal_server",
            version="1.0.0",
            description="Minimal server",
            interface_name="MinimalInterface",
            tools=[]
        )
        
        assert server_info.server_name == "minimal_server"
        assert server_info.version == "1.0.0"
        assert server_info.description == "Minimal server"
        assert server_info.interface_name == "MinimalInterface"
        assert server_info.tools == []
        assert server_info.capabilities == []


class TestMCPServerProtocol:
    """Test MCPServerProtocol abstract class."""
    
    def test_mcp_server_protocol_interface(self):
        """Test MCP server protocol interface methods."""
        # Check that MCPServerProtocol has the required abstract methods
        assert hasattr(MCPServerProtocol, 'get_server_info')
        assert hasattr(MCPServerProtocol, 'get_tools')
        assert hasattr(MCPServerProtocol, 'execute_tool')
        
        # Check that these are abstract methods
        assert getattr(MCPServerProtocol.get_server_info, '__isabstractmethod__', False)
        assert getattr(MCPServerProtocol.get_tools, '__isabstractmethod__', False)
        assert getattr(MCPServerProtocol.execute_tool, '__isabstractmethod__', False)


class TestMCPBaseServer(SmartCityProtocolsTestBase):
    """Test MCPBaseServer implementation."""
    
    @pytest.mark.asyncio
    async def test_mcp_base_server_initialization(self, mock_utility_foundation, mock_public_works_foundation):
        """Test MCP base server initialization."""
        # Create a concrete implementation for testing
        class TestMCPServer(MCPBaseServer):
            def __init__(self, utility_foundation, curator_foundation=None):
                super().__init__("test_mcp_server", utility_foundation, curator_foundation)
            
            async def get_server_info(self) -> MCPServerInfo:
                return MCPServerInfo(
                    server_name="test_server",
                    version="1.0.0",
                    description="Test server",
                    interface_name="TestInterface",
                    tools=[]
                )
            
            async def get_tools(self) -> List[MCPTool]:
                return []
            
            async def execute_tool(self, tool_name: str, input_data: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
                return {"status": "success"}
        
        server = TestMCPServer(mock_utility_foundation)
        
        assert server is not None
        assert server.service_name == "test_mcp_server"
        assert server.utility_foundation == mock_utility_foundation
    
    @pytest.mark.asyncio
    async def test_mcp_base_server_methods(self, mock_utility_foundation, mock_public_works_foundation):
        """Test MCP base server method implementations."""
        def test_tool_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "test_tool_executed", "input": input_data}
        
        class TestMCPServer(MCPBaseServer):
            def __init__(self, utility_foundation, curator_foundation=None):
                super().__init__("test_mcp_server", utility_foundation, curator_foundation)
            
            async def get_server_info(self) -> MCPServerInfo:
                return MCPServerInfo(
                    server_name="test_server",
                    version="1.0.0",
                    description="Test server",
                    interface_name="TestInterface",
                    tools=[
                        MCPTool(
                            name="test_tool",
                            description="A test tool",
                            input_schema={"type": "object"},
                            handler=test_tool_handler
                        )
                    ]
                )
            
            async def get_tools(self) -> List[MCPTool]:
                return [
                    MCPTool(
                        name="test_tool",
                        description="A test tool",
                        input_schema={"type": "object"},
                        handler=test_tool_handler
                    )
                ]
            
            async def execute_tool(self, tool_name: str, input_data: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
                if tool_name == "test_tool":
                    return test_tool_handler(input_data)
                return {"error": "Tool not found"}
        
        server = TestMCPServer(mock_utility_foundation)
        
        # Test get_server_info
        server_info = await server.get_server_info()
        assert server_info.server_name == "test_server"
        assert server_info.version == "1.0.0"
        
        # Test get_tools
        tools = await server.get_tools()
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
        assert tools[0].description == "A test tool"
        
        # Test tool validation through execution
        result = await server.execute_tool("test_tool", {"test": "data"})
        assert result["result"] == "test_tool_executed"
        
        error_result = await server.execute_tool("invalid_tool", {"test": "data"})
        assert "error" in error_result
        
        # Test execute_tool with invalid tool
        error_result = await server.execute_tool("invalid_tool", {"test": "data"})
        assert "error" in error_result
        assert error_result["error"] == "Tool not found"
    
    @pytest.mark.asyncio
    async def test_mcp_base_server_health_check(self, mock_utility_foundation, mock_public_works_foundation):
        """Test MCP base server health check."""
        class TestMCPServer(MCPBaseServer):
            def __init__(self, utility_foundation, curator_foundation=None):
                super().__init__("test_mcp_server", utility_foundation, curator_foundation)
            
            async def get_server_info(self) -> MCPServerInfo:
                return MCPServerInfo(
                    server_name="test_server",
                    version="1.0.0",
                    description="Test server",
                    interface_name="TestInterface",
                    tools=[]
                )
            
            async def get_tools(self) -> List[MCPTool]:
                return []
            
            async def execute_tool(self, tool_name: str, input_data: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
                return {"status": "success"}
        
        server = TestMCPServer(mock_utility_foundation)
        
        # Test health check (inherited from FoundationServiceBase)
        health_status = await server.get_service_health()
        
        assert health_status is not None
        assert "service" in health_status
        assert "status" in health_status
        assert "timestamp" in health_status
        assert health_status["service"] == "test_mcp_server"
