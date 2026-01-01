#!/usr/bin/env python3
"""
Operations MCP Server - Functional Tests

Tests OperationsMCPServer to verify:
- Tool registration (19 tools)
- Tool execution (delegates to orchestrator)
- Utility usage (telemetry, security, tenant, health)
- Error handling
- Health status

Uses proven patterns from orchestrator tests.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock

from utilities import UserContext

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES - Reusing Proven Patterns
# ============================================================================

@pytest.fixture(scope="function")
async def operations_orchestrator(smart_city_infrastructure):
    """
    OperationsOrchestrator instance for each test.
    
    Reuses the orchestrator fixture pattern from other orchestrator tests.
    """
    logger.info("🔧 Fixture: Starting operations_orchestrator fixture...")
    
    from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
    from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
    
    logger.info("🔧 Fixture: Got infrastructure, creating DeliveryManagerService...")
    infra = smart_city_infrastructure
    manager = DeliveryManagerService(
        di_container=infra["di_container"],
        platform_gateway=infra["platform_gateway"]
    )
    
    # Initialize delivery manager
    logger.info("🔧 Fixture: Initializing delivery manager...")
    try:
        result = await asyncio.wait_for(manager.initialize(), timeout=90.0)
        if not result:
            pytest.fail("Delivery Manager Service failed to initialize")
    except asyncio.TimeoutError:
        pytest.fail("Delivery Manager Service initialization timed out")
    
    # Create orchestrator
    logger.info("🔧 Fixture: Creating OperationsOrchestrator...")
    orchestrator = OperationsOrchestrator(manager)
    
    # Initialize orchestrator
    logger.info("🔧 Fixture: Initializing orchestrator...")
    try:
        result = await asyncio.wait_for(orchestrator.initialize(), timeout=90.0)
        if not result:
            pytest.fail("OperationsOrchestrator failed to initialize")
    except asyncio.TimeoutError:
        pytest.fail("OperationsOrchestrator initialization timed out")
    
    logger.info("✅ Fixture: Orchestrator ready")
    yield orchestrator
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture(scope="function")
def mcp_server(operations_orchestrator, smart_city_infrastructure):
    """
    OperationsMCPServer instance for each test.
    
    The MCP server is created by the orchestrator during initialization,
    so we access it via orchestrator.mcp_server.
    """
    logger.info("🔧 Fixture: Getting MCP server from orchestrator...")
    
    if not hasattr(operations_orchestrator, 'mcp_server') or operations_orchestrator.mcp_server is None:
        pytest.fail("MCP server not initialized by orchestrator")
    
    server = operations_orchestrator.mcp_server
    logger.info(f"✅ Fixture: MCP server ready: {server.service_name}")
    return server


@pytest.fixture
def mock_user_context():
    """Create a test user context."""
    return UserContext(
        user_id="test_user_123",
        email="test@example.com",
        full_name="Test User",
        session_id="test_session_789",
        permissions=["read", "write"],
        tenant_id="test_tenant_123",
    )


# ============================================================================
# FUNCTIONAL TESTS
# ============================================================================

class TestOperationsMCPServer:
    """Functional tests for Operations MCP Server."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_mcp_server_initialization(self, mcp_server):
        """Test MCP server initialization."""
        logger.info("🧪 Test: MCP server initialization")
        
        assert mcp_server is not None
        assert mcp_server.service_name == "operations_mcp"
        assert mcp_server.orchestrator is not None
        
        logger.info("✅ MCP server initialized correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_tool_registration(self, mcp_server):
        """Test that all tools are registered."""
        logger.info("🧪 Test: Tool registration")
        
        tool_list = mcp_server.get_tool_list()
        assert isinstance(tool_list, list)
        # Operations MCP Server has 19 tools
        assert len(tool_list) == 19
        
        expected_tools = [
            "get_session_elements",
            "clear_session_elements",
            "generate_workflow_from_sop",
            "generate_sop_from_workflow",
            "analyze_file",
            "analyze_coexistence_files",
            "analyze_coexistence_content",
            "start_wizard",
            "wizard_chat",
            "wizard_publish",
            "save_blueprint",
            "process_query",
            "process_conversation",
            "get_conversation_context",
            "analyze_intent",
            "health_check",
            "refine_sop_tool",
            "optimize_workflow_tool",
            "enhance_blueprint_tool"
        ]
        
        for tool in expected_tools:
            assert tool in tool_list, f"Tool {tool} not registered"
        
        logger.info(f"✅ All {len(tool_list)} tools registered")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_usage_guide(self, mcp_server):
        """Test usage guide generation."""
        logger.info("🧪 Test: Usage guide")
        
        guide = mcp_server.get_usage_guide()
        assert isinstance(guide, dict)
        assert guide.get("server_name") == "operations_mcp"
        assert "tools" in guide
        assert len(guide.get("tools", {})) == 19
        
        logger.info("✅ Usage guide generated correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_health_status(self, mcp_server):
        """Test health status check."""
        logger.info("🧪 Test: Health status")
        
        health = await mcp_server.get_health_status()
        assert isinstance(health, dict)
        assert "status" in health
        assert "server_name" in health
        assert health.get("server_name") == "operations_mcp"
        assert "tools_registered" in health
        assert health.get("tools_registered") == 19
        
        logger.info(f"✅ Health status: {health.get('status')}")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_version_info(self, mcp_server):
        """Test version info."""
        logger.info("🧪 Test: Version info")
        
        version_info = mcp_server.get_version_info()
        assert isinstance(version_info, dict)
        assert version_info.get("server_name") == "operations_mcp"
        assert "version" in version_info
        assert "compatible_with" in version_info
        
        logger.info(f"✅ Version: {version_info.get('version')}")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_unknown_tool_handling(self, mcp_server, mock_user_context):
        """Test handling of unknown tools."""
        logger.info("🧪 Test: Unknown tool handling")
        
        user_context_dict = {
            "user_id": mock_user_context.user_id,
            "tenant_id": mock_user_context.tenant_id,
            "permissions": mock_user_context.permissions
        }
        
        result = await mcp_server.execute_tool(
            tool_name="unknown_tool",
            parameters={},
            user_context=user_context_dict
        )
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "unknown_tool" in result.get("error", "").lower()
        
        logger.info("✅ Unknown tool handled correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_health_check_tool(self, mcp_server, operations_orchestrator, mock_user_context):
        """Test that health_check tool delegates to orchestrator."""
        logger.info("🧪 Test: health_check tool delegation")
        
        user_context_dict = {
            "user_id": mock_user_context.user_id,
            "tenant_id": mock_user_context.tenant_id,
            "permissions": mock_user_context.permissions
        }
        
        # Mock orchestrator method
        operations_orchestrator.health_check = AsyncMock(return_value={
            "status": "healthy",
            "orchestrator": "operations"
        })
        
        result = await mcp_server.execute_tool(
            tool_name="health_check",
            parameters={},
            user_context=user_context_dict
        )
        
        assert isinstance(result, dict)
        assert result.get("status") == "healthy" or "orchestrator" in result
        operations_orchestrator.health_check.assert_called_once()
        
        logger.info("✅ Tool delegates to orchestrator correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_get_session_elements_tool(self, mcp_server, operations_orchestrator, mock_user_context):
        """Test that get_session_elements tool delegates to orchestrator."""
        logger.info("🧪 Test: get_session_elements tool delegation")
        
        user_context_dict = {
            "user_id": mock_user_context.user_id,
            "tenant_id": mock_user_context.tenant_id,
            "permissions": mock_user_context.permissions
        }
        
        # Mock orchestrator method
        operations_orchestrator.get_session_elements = AsyncMock(return_value={
            "success": True,
            "elements": []
        })
        
        result = await mcp_server.execute_tool(
            tool_name="get_session_elements",
            parameters={"session_token": "test_session_123"},
            user_context=user_context_dict
        )
        
        assert isinstance(result, dict)
        assert "success" in result or "elements" in result
        operations_orchestrator.get_session_elements.assert_called_once()
        
        logger.info("✅ Tool delegates to orchestrator correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_start_wizard_tool(self, mcp_server, operations_orchestrator, mock_user_context):
        """Test that start_wizard tool delegates to orchestrator."""
        logger.info("🧪 Test: start_wizard tool delegation")
        
        user_context_dict = {
            "user_id": mock_user_context.user_id,
            "tenant_id": mock_user_context.tenant_id,
            "permissions": mock_user_context.permissions
        }
        
        # Mock orchestrator method
        operations_orchestrator.start_wizard = AsyncMock(return_value={
            "success": True,
            "session_token": "wizard_session_123"
        })
        
        result = await mcp_server.execute_tool(
            tool_name="start_wizard",
            parameters={},
            user_context=user_context_dict
        )
        
        assert isinstance(result, dict)
        assert "success" in result or "session_token" in result
        operations_orchestrator.start_wizard.assert_called_once()
        
        logger.info("✅ Tool delegates to orchestrator correctly")




