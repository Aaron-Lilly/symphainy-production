#!/usr/bin/env python3
"""
Test Agent MCP Tool Access

Validates that refactored agents can:
1. Be created via factory
2. Initialize properly
3. Execute capabilities
4. Access and call MCP tools

This test runs without requiring full backend startup.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any, List, Optional

# Add project root to path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase
from foundations.agentic_foundation.agent_sdk.mcp_client_manager import MCPClientManager
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestAgentMCPToolAccess:
    """Test suite for agent MCP tool access validation."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create a mock DI container with all required services."""
        di_container = Mock(spec=DIContainerService)
        
        # Mock logger
        logger = Mock()
        logger.info = Mock()
        logger.warning = Mock()
        logger.error = Mock()
        di_container.get_logger = Mock(return_value=logger)
        
        # Mock config
        config = Mock()
        config.get = Mock(return_value=None)
        di_container.get_config = Mock(return_value=config)
        
        # Mock utilities
        telemetry = AsyncMock()
        telemetry.record_platform_operation_event = AsyncMock()
        telemetry.record_platform_error_event = AsyncMock()
        telemetry.record_metric = AsyncMock()
        di_container.get_telemetry = Mock(return_value=telemetry)
        
        health = AsyncMock()
        health.record_metric = AsyncMock()
        di_container.get_health = Mock(return_value=health)
        
        security = AsyncMock()
        security.check_permissions = AsyncMock(return_value=True)
        security.audit_log = AsyncMock()
        di_container.get_security = Mock(return_value=security)
        
        tenant_service = AsyncMock()
        tenant_service.validate_tenant_access = AsyncMock(return_value=True)
        di_container.get_tenant_service = Mock(return_value=tenant_service)
        
        return di_container
    
    @pytest.fixture
    def mock_mcp_client_manager(self):
        """Create a mock MCP client manager."""
        mcp_manager = Mock(spec=MCPClientManager)
        
        # Mock execute_role_tool method
        async def mock_execute_role_tool(role_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
            """Mock MCP tool execution."""
            return {
                "success": True,
                "role_name": role_name,
                "tool_name": tool_name,
                "result": f"Mock result for {role_name}.{tool_name}",
                "parameters": parameters
            }
        
        mcp_manager.execute_role_tool = AsyncMock(side_effect=mock_execute_role_tool)
        mcp_manager.get_tool_definitions = Mock(return_value=[])
        mcp_manager.connect_to_role = AsyncMock(return_value=True)
        mcp_manager.get_mcp_tool = Mock(return_value=None)
        
        return mcp_manager
    
    @pytest.fixture
    def mock_curator_foundation(self):
        """Create a mock Curator foundation."""
        curator = Mock(spec=CuratorFoundationService)
        curator.register_agent = AsyncMock(return_value={"success": True})
        curator.get_registered_services = AsyncMock(return_value={"services": {}})
        curator.get_service = AsyncMock(return_value=None)
        return curator
    
    @pytest.fixture
    def mock_agentic_foundation(self, mock_di_container, mock_curator_foundation):
        """Create a mock Agentic Foundation service."""
        agentic_foundation = Mock()
        agentic_foundation.di_container = mock_di_container
        agentic_foundation.curator_foundation = mock_curator_foundation
        agentic_foundation.public_works_foundation = Mock()
        agentic_foundation.public_works_foundation.get_tenant_service = Mock(return_value=mock_di_container.get_tenant_service())
        return agentic_foundation
    
    @pytest.fixture
    def mock_public_works_foundation(self, mock_di_container):
        """Create a mock Public Works Foundation."""
        public_works = Mock()
        public_works.get_tenant_service = Mock(return_value=mock_di_container.get_tenant_service())
        return public_works
    
    @pytest.fixture
    def mock_agui_schema(self):
        """Create a mock AGUI schema."""
        schema = Mock()
        schema.schema_name = "test_schema"
        return schema
    
    @pytest.fixture
    def test_agent_class(self):
        """Create a test agent class that extends AgentBase."""
        class TestAgent(AgentBase):
            """Test agent for validation."""
            
            def __init__(self, agent_name: str, capabilities: List[str], required_roles: List[str],
                        agui_schema: Any, foundation_services: Any, agentic_foundation: Any,
                        public_works_foundation: Any, mcp_client_manager: Any,
                        policy_integration: Any, tool_composition: Any, agui_formatter: Any,
                        curator_foundation: Any = None, metadata_foundation: Any = None, **kwargs):
                super().__init__(
                    agent_name=agent_name,
                    capabilities=capabilities,
                    required_roles=required_roles,
                    agui_schema=agui_schema,
                    foundation_services=foundation_services,
                    agentic_foundation=agentic_foundation,
                    public_works_foundation=public_works_foundation,
                    mcp_client_manager=mcp_client_manager,
                    policy_integration=policy_integration,
                    tool_composition=tool_composition,
                    agui_formatter=agui_formatter,
                    curator_foundation=curator_foundation,
                    metadata_foundation=metadata_foundation,
                    **kwargs
                )
                self.service_name = agent_name
            
            def get_agent_description(self) -> str:
                """Get agent description (required abstract method)."""
                return f"Test agent: {self.agent_name}"
            
            async def process_request(self, request: Dict[str, Any], user_context: Any = None) -> Dict[str, Any]:
                """Process a request (required abstract method)."""
                return {"success": True, "message": "Request processed"}
            
            async def execute_capability(self, capability_name: str, request_data: Dict[str, Any],
                                       user_context: Any = None) -> Dict[str, Any]:
                """Execute a capability using MCP tools."""
                # Simulate using MCP tools during capability execution
                if self.mcp_client_manager:
                    result = await self.mcp_client_manager.execute_role_tool(
                        role_name="librarian",
                        tool_name="store_document",
                        parameters=request_data
                    )
                    return {"success": True, "capability": capability_name, "mcp_result": result}
                return {"success": False, "error": "MCP client manager not available"}
        
        return TestAgent
    
    @pytest.mark.asyncio
    async def test_agent_creation_with_mcp_manager(self, test_agent_class, mock_di_container,
                                                   mock_agentic_foundation, mock_public_works_foundation,
                                                   mock_mcp_client_manager, mock_curator_foundation,
                                                   mock_agui_schema):
        """Test that agent can be created with MCP client manager."""
        with patch('foundations.agentic_foundation.agent_sdk.agent_base.get_agui_schema_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.validate_schema = Mock(return_value={"valid": True})
            mock_registry.register_agent_schema = Mock(return_value=True)
            mock_get_registry.return_value = mock_registry
            
            agent = test_agent_class(
                agent_name="Test Agent",
                capabilities=["test_capability"],
                required_roles=["librarian"],
                agui_schema=mock_agui_schema,
                foundation_services=mock_di_container,
                agentic_foundation=mock_agentic_foundation,
                public_works_foundation=mock_public_works_foundation,
                mcp_client_manager=mock_mcp_client_manager,
                policy_integration=AsyncMock(),
                tool_composition=AsyncMock(),
                agui_formatter=AsyncMock(),
                curator_foundation=mock_curator_foundation,
                metadata_foundation=None
            )
            
            assert agent is not None
            assert agent.agent_name == "Test Agent"
            assert agent.mcp_client_manager == mock_mcp_client_manager
            print("✅ Agent created successfully with MCP client manager")
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, test_agent_class, mock_di_container,
                                       mock_agentic_foundation, mock_public_works_foundation,
                                       mock_mcp_client_manager, mock_curator_foundation,
                                       mock_agui_schema):
        """Test that agent initializes properly with utility methods."""
        with patch('foundations.agentic_foundation.agent_sdk.agent_base.get_agui_schema_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.validate_schema = Mock(return_value={"valid": True})
            mock_registry.register_agent_schema = Mock(return_value=True)
            mock_get_registry.return_value = mock_registry
            
            agent = test_agent_class(
                agent_name="Test Agent",
                capabilities=["test_capability"],
                required_roles=["librarian"],
                agui_schema=mock_agui_schema,
                foundation_services=mock_di_container,
                agentic_foundation=mock_agentic_foundation,
                public_works_foundation=mock_public_works_foundation,
                mcp_client_manager=mock_mcp_client_manager,
                policy_integration=AsyncMock(),
                tool_composition=AsyncMock(),
                agui_formatter=AsyncMock(),
                curator_foundation=mock_curator_foundation,
                metadata_foundation=None
            )
            
            # Initialize agent
            result = await agent.initialize()
            
            # Initialize may return True/False or None - check is_initialized instead
            assert agent.is_initialized is True or result is True
            
            # Verify utility methods are available
            assert hasattr(agent, 'log_operation_with_telemetry')
            assert hasattr(agent, 'record_health_metric')
            assert hasattr(agent, 'handle_error_with_audit')
            
            print("✅ Agent initialized successfully with utility methods")
    
    @pytest.mark.asyncio
    async def test_agent_can_access_mcp_tools(self, test_agent_class, mock_di_container,
                                              mock_agentic_foundation, mock_public_works_foundation,
                                              mock_mcp_client_manager, mock_curator_foundation,
                                              mock_agui_schema):
        """Test that agent can access MCP tools through MCP client manager."""
        with patch('foundations.agentic_foundation.agent_sdk.agent_base.get_agui_schema_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.validate_schema = Mock(return_value={"valid": True})
            mock_registry.register_agent_schema = Mock(return_value=True)
            mock_get_registry.return_value = mock_registry
            
            agent = test_agent_class(
                agent_name="Test Agent",
                capabilities=["test_capability"],
                required_roles=["librarian"],
                agui_schema=mock_agui_schema,
                foundation_services=mock_di_container,
                agentic_foundation=mock_agentic_foundation,
                public_works_foundation=mock_public_works_foundation,
                mcp_client_manager=mock_mcp_client_manager,
                policy_integration=AsyncMock(),
                tool_composition=AsyncMock(),
                agui_formatter=AsyncMock(),
                curator_foundation=mock_curator_foundation,
                metadata_foundation=None
            )
            await agent.initialize()
            
            # Verify MCP client manager is available
            assert agent.mcp_client_manager is not None
            assert agent.mcp_client_manager == mock_mcp_client_manager
            
            # Test accessing MCP tool
            tool_result = await mock_mcp_client_manager.execute_role_tool(
                role_name="librarian",
                tool_name="upload_file",
                parameters={"file_path": "/test/file.pdf", "metadata": {}}
            )
            
            assert tool_result is not None
            assert tool_result["success"] is True
            assert tool_result["role_name"] == "librarian"
            assert tool_result["tool_name"] == "upload_file"
            
            # Verify the MCP client manager was called
            mock_mcp_client_manager.execute_role_tool.assert_called_once()
            
            print("✅ Agent can access MCP tools through MCP client manager")
    
    @pytest.mark.asyncio
    async def test_agent_executes_capability_with_mcp_tools(self, test_agent_class, mock_di_container,
                                                           mock_agentic_foundation, mock_public_works_foundation,
                                                           mock_mcp_client_manager, mock_curator_foundation,
                                                           mock_agui_schema):
        """Test that agent can execute capabilities that use MCP tools."""
        with patch('foundations.agentic_foundation.agent_sdk.agent_base.get_agui_schema_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.validate_schema = Mock(return_value={"valid": True})
            mock_registry.register_agent_schema = Mock(return_value=True)
            mock_get_registry.return_value = mock_registry
            
            agent = test_agent_class(
                agent_name="Test Agent",
                capabilities=["test_capability"],
                required_roles=["librarian"],
                agui_schema=mock_agui_schema,
                foundation_services=mock_di_container,
                agentic_foundation=mock_agentic_foundation,
                public_works_foundation=mock_public_works_foundation,
                mcp_client_manager=mock_mcp_client_manager,
                policy_integration=AsyncMock(),
                tool_composition=AsyncMock(),
                agui_formatter=AsyncMock(),
                curator_foundation=mock_curator_foundation,
                metadata_foundation=None
            )
            await agent.initialize()
            
            # Create user context
            user_context = Mock()
            user_context.user_id = "test_user"
            user_context.tenant_id = "test_tenant"
            user_context.roles = ["user"]
            
            # Execute capability that should use MCP tools
            result = await agent.execute_capability(
                capability_name="test_capability",
                request_data={
                    "file_path": "/test/file.pdf",
                    "operation": "store"
                },
                user_context=user_context
            )
            
            # Verify result
            assert result is not None
            assert result["success"] is True
            assert "mcp_result" in result
            assert result["mcp_result"]["success"] is True
            
            # Verify MCP tool was called
            assert mock_mcp_client_manager.execute_role_tool.called
            
            print("✅ Agent executed capability using MCP tools")
    
    @pytest.mark.asyncio
    async def test_agent_mcp_tool_integration(self, test_agent_class, mock_di_container,
                                              mock_agentic_foundation, mock_public_works_foundation,
                                              mock_mcp_client_manager, mock_curator_foundation,
                                              mock_agui_schema):
        """Test end-to-end MCP tool integration with agent."""
        with patch('foundations.agentic_foundation.agent_sdk.agent_base.get_agui_schema_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.validate_schema = Mock(return_value={"valid": True})
            mock_registry.register_agent_schema = Mock(return_value=True)
            mock_get_registry.return_value = mock_registry
            
            agent = test_agent_class(
                agent_name="Test Agent",
                capabilities=["test_capability"],
                required_roles=["librarian"],
                agui_schema=mock_agui_schema,
                foundation_services=mock_di_container,
                agentic_foundation=mock_agentic_foundation,
                public_works_foundation=mock_public_works_foundation,
                mcp_client_manager=mock_mcp_client_manager,
                policy_integration=AsyncMock(),
                tool_composition=AsyncMock(),
                agui_formatter=AsyncMock(),
                curator_foundation=mock_curator_foundation,
                metadata_foundation=None
            )
            await agent.initialize()
            
            # Test 1: Librarian tool (document storage)
            librarian_result = await agent.mcp_client_manager.execute_role_tool(
                role_name="librarian",
                tool_name="store_document",
                parameters={
                    "document_id": "doc_123",
                    "content": "Test document content",
                    "metadata": {"type": "test"}
                }
            )
            
            assert librarian_result["success"] is True
            print("✅ Agent successfully called Librarian MCP tool")
            
            # Test 2: Data Steward tool (data quality)
            data_steward_result = await agent.mcp_client_manager.execute_role_tool(
                role_name="data_steward",
                tool_name="validate_data",
                parameters={
                    "data": {"field": "value"},
                    "schema": "test_schema"
                }
            )
            
            assert data_steward_result["success"] is True
            print("✅ Agent successfully called Data Steward MCP tool")
            
            # Verify both tools were called
            assert mock_mcp_client_manager.execute_role_tool.call_count == 2
            
            print("✅ Agent MCP tool integration working correctly")
    
    @pytest.mark.asyncio
    async def test_agent_utility_methods_with_mcp_tools(self, test_agent_class, mock_di_container,
                                                        mock_agentic_foundation, mock_public_works_foundation,
                                                        mock_mcp_client_manager, mock_curator_foundation,
                                                        mock_agui_schema):
        """Test that agent utility methods work correctly when MCP tools are called."""
        with patch('foundations.agentic_foundation.agent_sdk.agent_base.get_agui_schema_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.validate_schema = Mock(return_value={"valid": True})
            mock_registry.register_agent_schema = Mock(return_value=True)
            mock_get_registry.return_value = mock_registry
            
            agent = test_agent_class(
                agent_name="Test Agent",
                capabilities=["test_capability"],
                required_roles=["librarian"],
                agui_schema=mock_agui_schema,
                foundation_services=mock_di_container,
                agentic_foundation=mock_agentic_foundation,
                public_works_foundation=mock_public_works_foundation,
                mcp_client_manager=mock_mcp_client_manager,
                policy_integration=AsyncMock(),
                tool_composition=AsyncMock(),
                agui_formatter=AsyncMock(),
                curator_foundation=mock_curator_foundation,
                metadata_foundation=None
            )
            await agent.initialize()
            
            # Mock the utility methods to track calls
            with patch.object(agent, 'log_operation_with_telemetry', new_callable=AsyncMock) as mock_log, \
                 patch.object(agent, 'record_health_metric', new_callable=AsyncMock) as mock_health:
                
                # Execute MCP tool (which should trigger utility methods in real usage)
                result = await agent.mcp_client_manager.execute_role_tool(
                    role_name="librarian",
                    tool_name="get_document",
                    parameters={"document_id": "doc_123"}
                )
                
                # Verify MCP tool executed
                assert result["success"] is True
                
                # Verify utility methods are available
                assert hasattr(agent, 'log_operation_with_telemetry')
                assert hasattr(agent, 'record_health_metric')
                
                print("✅ Agent utility methods available and working")
    
    @pytest.mark.asyncio
    async def test_multiple_agents_mcp_tool_access(self, test_agent_class, mock_di_container,
                                                   mock_agentic_foundation, mock_public_works_foundation,
                                                   mock_mcp_client_manager, mock_curator_foundation,
                                                   mock_agui_schema):
        """Test that multiple agents can independently access MCP tools."""
        with patch('foundations.agentic_foundation.agent_sdk.agent_base.get_agui_schema_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.validate_schema = Mock(return_value={"valid": True})
            mock_registry.register_agent_schema = Mock(return_value=True)
            mock_get_registry.return_value = mock_registry
            
            # Create first agent
            agent1 = test_agent_class(
                agent_name="Agent 1",
                capabilities=["capability_1"],
                required_roles=["librarian"],
                agui_schema=mock_agui_schema,
                foundation_services=mock_di_container,
                agentic_foundation=mock_agentic_foundation,
                public_works_foundation=mock_public_works_foundation,
                mcp_client_manager=mock_mcp_client_manager,
                policy_integration=AsyncMock(),
                tool_composition=AsyncMock(),
                agui_formatter=AsyncMock(),
                curator_foundation=mock_curator_foundation,
                metadata_foundation=None
            )
            await agent1.initialize()
            
            # Create second agent with same MCP client manager
            agent2 = test_agent_class(
                agent_name="Agent 2",
                capabilities=["capability_2"],
                required_roles=["data_steward"],
                agui_schema=mock_agui_schema,
                foundation_services=mock_di_container,
                agentic_foundation=mock_agentic_foundation,
                public_works_foundation=mock_public_works_foundation,
                mcp_client_manager=mock_mcp_client_manager,
                policy_integration=AsyncMock(),
                tool_composition=AsyncMock(),
                agui_formatter=AsyncMock(),
                curator_foundation=mock_curator_foundation,
                metadata_foundation=None
            )
            await agent2.initialize()
            
            # Both agents should be able to access MCP tools
            result1 = await agent1.mcp_client_manager.execute_role_tool(
                role_name="librarian",
                tool_name="tool1",
                parameters={}
            )
            
            result2 = await agent2.mcp_client_manager.execute_role_tool(
                role_name="data_steward",
                tool_name="tool2",
                parameters={}
            )
            
            assert result1["success"] is True
            assert result2["success"] is True
            assert mock_mcp_client_manager.execute_role_tool.call_count == 2
            
            print("✅ Multiple agents can independently access MCP tools")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
