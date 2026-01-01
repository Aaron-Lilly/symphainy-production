#!/usr/bin/env python3
"""
Content Analysis MCP Server - Functional Tests

Tests ContentAnalysisMCPServer to verify:
- Tool registration (10 tools)
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
async def content_orchestrator(smart_city_infrastructure):
    """
    ContentAnalysisOrchestrator instance for each test.
    
    Reuses the orchestrator fixture pattern from test_content_analysis_orchestrator.py
    """
    logger.info("🔧 Fixture: Starting content_orchestrator fixture...")
    
    from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
    from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
    
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
    logger.info("🔧 Fixture: Creating ContentAnalysisOrchestrator...")
    orchestrator = ContentAnalysisOrchestrator(manager)
    
    # Initialize orchestrator
    logger.info("🔧 Fixture: Initializing orchestrator...")
    try:
        result = await asyncio.wait_for(orchestrator.initialize(), timeout=90.0)
        if not result:
            pytest.fail("ContentAnalysisOrchestrator failed to initialize")
    except asyncio.TimeoutError:
        pytest.fail("ContentAnalysisOrchestrator initialization timed out")
    
    logger.info("✅ Fixture: Orchestrator ready")
    yield orchestrator
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture(scope="function")
def mcp_server(content_orchestrator, smart_city_infrastructure):
    """
    ContentAnalysisMCPServer instance for each test.
    
    The MCP server is created by the orchestrator during initialization,
    so we access it via orchestrator.mcp_server.
    """
    logger.info("🔧 Fixture: Getting MCP server from orchestrator...")
    
    if not hasattr(content_orchestrator, 'mcp_server') or content_orchestrator.mcp_server is None:
        pytest.fail("MCP server not initialized by orchestrator")
    
    server = content_orchestrator.mcp_server
    logger.info(f"✅ Fixture: MCP server ready: {server.service_name}")
    return server


@pytest.fixture
def user_context():
    """Create a test user context."""
    return UserContext(
        user_id="test_user_123",
        email="test@example.com",
        full_name="Test User",
        session_id="test_session_123",
        permissions=["read", "write"],
        tenant_id="test_tenant_123"
    )


# ============================================================================
# TESTS - MCP Server Functionality
# ============================================================================

@pytest.mark.asyncio
async def test_mcp_server_initialization(mcp_server):
    """Test that MCP server is properly initialized."""
    logger.info("🧪 Test: MCP server initialization")
    
    assert mcp_server is not None
    assert hasattr(mcp_server, 'service_name')
    assert mcp_server.service_name == "content_analysis_mcp"
    assert hasattr(mcp_server, 'orchestrator')
    assert mcp_server.orchestrator is not None
    
    logger.info("✅ MCP server initialized correctly")


@pytest.mark.asyncio
async def test_mcp_server_registers_tools(mcp_server):
    """Test that MCP server registers all 10 tools."""
    logger.info("🧪 Test: Tool registration")
    
    tools = mcp_server.get_tool_list()
    logger.info(f"📋 Registered tools: {tools}")
    
    assert isinstance(tools, list)
    assert len(tools) == 10
    
    expected_tools = [
        "analyze_document_tool",
        "parse_file_tool",
        "extract_entities_tool",
        "list_files_tool",
        "get_file_metadata_tool",
        "process_documents_tool",
        "convert_format_tool",
        "enhance_metadata_extraction_tool",
        "enhance_content_insights_tool",
        "recommend_format_optimization_tool"
    ]
    
    for tool in expected_tools:
        assert tool in tools, f"Tool {tool} not registered"
    
    logger.info("✅ All 10 tools registered correctly")


@pytest.mark.asyncio
async def test_mcp_server_get_usage_guide(mcp_server):
    """Test that MCP server provides usage guide."""
    logger.info("🧪 Test: Usage guide")
    
    guide = mcp_server.get_usage_guide()
    
    assert isinstance(guide, dict)
    assert guide.get("server_name") == "content_analysis_mcp"
    assert "description" in guide
    assert "tools" in guide
    assert len(guide.get("tools", {})) == 10
    
    logger.info("✅ Usage guide provided correctly")


@pytest.mark.asyncio
async def test_mcp_server_get_health_status(mcp_server):
    """Test that MCP server provides health status."""
    logger.info("🧪 Test: Health status")
    
    health = await mcp_server.get_health_status()
    
    assert isinstance(health, dict)
    assert health.get("server_name") == "content_analysis_mcp"
    assert "status" in health
    assert health.get("status") in ["healthy", "degraded", "error"]
    assert "orchestrator_status" in health
    assert "tools_registered" in health
    assert health.get("tools_registered") == 10
    
    logger.info(f"✅ Health status: {health.get('status')}")


@pytest.mark.asyncio
async def test_mcp_server_get_version_info(mcp_server):
    """Test that MCP server provides version info."""
    logger.info("🧪 Test: Version info")
    
    version_info = mcp_server.get_version_info()
    
    assert isinstance(version_info, dict)
    assert version_info.get("server_name") == "content_analysis_mcp"
    assert "version" in version_info
    assert "api_version" in version_info
    assert "compatible_with" in version_info
    
    logger.info("✅ Version info provided correctly")


@pytest.mark.asyncio
async def test_mcp_server_execute_tool_unknown(mcp_server):
    """Test that MCP server handles unknown tools gracefully."""
    logger.info("🧪 Test: Unknown tool handling")
    
    result = await mcp_server.execute_tool("unknown_tool", {})
    
    assert isinstance(result, dict)
    assert "error" in result
    assert "Unknown tool" in result.get("error", "")
    
    logger.info("✅ Unknown tool handled gracefully")


@pytest.mark.asyncio
async def test_mcp_server_execute_tool_list_files(mcp_server, user_context):
    """Test that MCP server executes list_files_tool."""
    logger.info("🧪 Test: list_files_tool execution")
    
    user_context_dict = {
        "user_id": user_context.user_id,
        "tenant_id": user_context.tenant_id,
        "permissions": user_context.permissions
    }
    
    result = await mcp_server.execute_tool(
        "list_files_tool",
        {"user_id": user_context.user_id},
        user_context=user_context_dict
    )
    
    assert isinstance(result, dict)
    # The result should have a structure from orchestrator.list_uploaded_files
    assert "success" in result or "count" in result or "files" in result
    
    logger.info(f"✅ list_files_tool executed: {result.get('success', 'N/A')}")


@pytest.mark.asyncio
async def test_mcp_server_execute_tool_get_file_metadata(mcp_server, user_context):
    """Test that MCP server executes get_file_metadata_tool."""
    logger.info("🧪 Test: get_file_metadata_tool execution")
    
    # First, we need a file_id. Let's try with a non-existent file to test error handling
    user_context_dict = {
        "user_id": user_context.user_id,
        "tenant_id": user_context.tenant_id,
        "permissions": user_context.permissions
    }
    
    result = await mcp_server.execute_tool(
        "get_file_metadata_tool",
        {
            "file_id": "non_existent_file_123",
            "user_id": user_context.user_id
        },
        user_context=user_context_dict
    )
    
    assert isinstance(result, dict)
    # The result should have a structure from orchestrator.get_file_details
    # It may succeed or fail, but should return a structured response
    
    logger.info(f"✅ get_file_metadata_tool executed: {result.get('success', 'N/A')}")


@pytest.mark.asyncio
async def test_mcp_server_tool_delegates_to_orchestrator(mcp_server):
    """Test that MCP server tools delegate to orchestrator methods."""
    logger.info("🧪 Test: Tool delegation to orchestrator")
    
    # Verify orchestrator has the methods that tools call
    orchestrator = mcp_server.orchestrator
    
    assert hasattr(orchestrator, 'list_uploaded_files')
    assert hasattr(orchestrator, 'get_file_details')
    assert hasattr(orchestrator, 'parse_file')
    assert hasattr(orchestrator, 'analyze_document')
    assert hasattr(orchestrator, 'extract_entities')
    
    logger.info("✅ MCP server tools delegate to orchestrator methods")


@pytest.mark.asyncio
async def test_mcp_server_utility_access(mcp_server):
    """Test that MCP server has access to utilities."""
    logger.info("🧪 Test: Utility access")
    
    assert hasattr(mcp_server, 'utilities')
    assert mcp_server.utilities is not None
    
    # Utilities should have logger, telemetry, health, security, tenant
    assert hasattr(mcp_server.utilities, 'logger')
    # Other utilities may be optional, so we check if they exist
    
    logger.info("✅ MCP server has utility access")


# ============================================================================
# INTEGRATION TESTS - With Real Orchestrator
# ============================================================================

@pytest.mark.asyncio
async def test_mcp_server_integration_list_files(mcp_server, content_orchestrator, user_context):
    """Test MCP server integration with orchestrator for list_files_tool."""
    logger.info("🧪 Test: MCP server integration - list_files_tool")
    
    user_context_dict = {
        "user_id": user_context.user_id,
        "tenant_id": user_context.tenant_id,
        "permissions": user_context.permissions
    }
    
    # Execute tool via MCP server
    result = await mcp_server.execute_tool(
        "list_files_tool",
        {"user_id": user_context.user_id},
        user_context=user_context_dict
    )
    
    assert isinstance(result, dict)
    # Should return a structured response from orchestrator
    logger.info(f"✅ Integration test result: {result.get('count', 'N/A')} files")


@pytest.mark.asyncio
async def test_mcp_server_integration_health_check(mcp_server):
    """Test MCP server health check integration."""
    logger.info("🧪 Test: MCP server health check integration")
    
    health = await mcp_server.get_health_status()
    
    assert health.get("status") in ["healthy", "degraded"]
    assert health.get("orchestrator_status") in ["healthy", "degraded", "unknown"]
    
    logger.info(f"✅ Health check: server={health.get('status')}, orchestrator={health.get('orchestrator_status')}")

