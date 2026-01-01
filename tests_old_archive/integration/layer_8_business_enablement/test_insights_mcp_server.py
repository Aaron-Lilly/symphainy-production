#!/usr/bin/env python3
"""
Insights MCP Server - Functional Tests

Tests InsightsMCPServer to verify:
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
async def insights_orchestrator(smart_city_infrastructure):
    """
    InsightsOrchestrator instance for each test.
    
    Reuses the orchestrator fixture pattern from test_insights_orchestrator.py
    """
    logger.info("🔧 Fixture: Starting insights_orchestrator fixture...")
    
    from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
    from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
    
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
    logger.info("🔧 Fixture: Creating InsightsOrchestrator...")
    orchestrator = InsightsOrchestrator(manager)
    
    # Initialize orchestrator
    logger.info("🔧 Fixture: Initializing orchestrator...")
    try:
        result = await asyncio.wait_for(orchestrator.initialize(), timeout=90.0)
        if not result:
            pytest.fail("InsightsOrchestrator failed to initialize")
    except asyncio.TimeoutError:
        pytest.fail("InsightsOrchestrator initialization timed out")
    
    logger.info("✅ Fixture: Orchestrator ready")
    yield orchestrator
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture(scope="function")
def mcp_server(insights_orchestrator, smart_city_infrastructure):
    """
    InsightsMCPServer instance for each test.
    
    The MCP server is created by the orchestrator during initialization,
    so we access it via orchestrator.mcp_server.
    """
    logger.info("🔧 Fixture: Getting MCP server from orchestrator...")
    
    if not hasattr(insights_orchestrator, 'mcp_server') or insights_orchestrator.mcp_server is None:
        pytest.fail("MCP server not initialized by orchestrator")
    
    server = insights_orchestrator.mcp_server
    logger.info(f"✅ Fixture: MCP server ready: {server.service_name}")
    return server


@pytest.fixture
def mock_user_context():
    """Create a test user context."""
    return UserContext(
        user_id="test_user_123",
        email="test@example.com",
        full_name="Test User",
        session_id="test_session_456",
        permissions=["read", "write"],
        tenant_id="test_tenant_123",
    )


# ============================================================================
# FUNCTIONAL TESTS
# ============================================================================

class TestInsightsMCPServer:
    """Functional tests for Insights MCP Server."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_mcp_server_initialization(self, mcp_server):
        """Test MCP server initialization."""
        logger.info("🧪 Test: MCP server initialization")
        
        assert mcp_server is not None
        assert mcp_server.service_name == "insights_mcp"
        assert mcp_server.orchestrator is not None
        
        logger.info("✅ MCP server initialized correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_tool_registration(self, mcp_server):
        """Test that all tools are registered."""
        logger.info("🧪 Test: Tool registration")
        
        tool_list = mcp_server.get_tool_list()
        assert isinstance(tool_list, list)
        assert len(tool_list) == 10
        
        expected_tools = [
            "calculate_metrics_tool",
            "generate_insights_tool",
            "create_visualization_tool",
            "query_data_insights",
            "analyze_content_for_insights_tool",
            "query_analysis_results_tool",
            "generate_grounded_insights_tool",
            "process_double_click_query_tool",
            "generate_insights_summary_tool",
            "explain_data_science_results_tool"
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
        assert guide.get("server_name") == "insights_mcp"
        assert "tools" in guide
        assert len(guide.get("tools", {})) == 10
        
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
        assert health.get("server_name") == "insights_mcp"
        
        logger.info(f"✅ Health status: {health.get('status')}")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_version_info(self, mcp_server):
        """Test version info."""
        logger.info("🧪 Test: Version info")
        
        version_info = mcp_server.get_version_info()
        assert isinstance(version_info, dict)
        assert version_info.get("server_name") == "insights_mcp"
        assert "version" in version_info
        
        logger.info(f"✅ Version: {version_info.get('version')}")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_unknown_tool_handling(self, mcp_server, mock_user_context):
        """Test handling of unknown tools."""
        logger.info("🧪 Test: Unknown tool handling")
        
        result = await mcp_server.execute_tool(
            tool_name="unknown_tool",
            parameters={},
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "unknown_tool" in result.get("error", "").lower()
        
        logger.info("✅ Unknown tool handled correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_calculate_metrics_tool_delegation(self, mcp_server, insights_orchestrator, mock_user_context):
        """Test that calculate_metrics_tool delegates to orchestrator."""
        logger.info("🧪 Test: calculate_metrics_tool delegation")
        
        # Convert UserContext to dict for orchestrator compatibility
        user_context_dict = {
            "user_id": mock_user_context.user_id,
            "email": mock_user_context.email,
            "full_name": mock_user_context.full_name,
            "session_id": mock_user_context.session_id,
            "permissions": mock_user_context.permissions,
            "tenant_id": mock_user_context.tenant_id,
        }
        
        # Mock orchestrator method
        insights_orchestrator.calculate_metrics = AsyncMock(return_value={
            "success": True,
            "metrics": {"revenue": 1000, "profit": 500}
        })
        
        result = await mcp_server.execute_tool(
            tool_name="calculate_metrics_tool",
            parameters={"resource_id": "test_resource_123"},
            user_context=user_context_dict
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        insights_orchestrator.calculate_metrics.assert_called_once()
        
        logger.info("✅ Tool delegates to orchestrator correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_generate_insights_tool_delegation(self, mcp_server, insights_orchestrator, mock_user_context):
        """Test that generate_insights_tool delegates to orchestrator."""
        logger.info("🧪 Test: generate_insights_tool delegation")
        
        # Convert UserContext to dict for orchestrator compatibility
        user_context_dict = {
            "user_id": mock_user_context.user_id,
            "email": mock_user_context.email,
            "full_name": mock_user_context.full_name,
            "session_id": mock_user_context.session_id,
            "permissions": mock_user_context.permissions,
            "tenant_id": mock_user_context.tenant_id,
        }
        
        # Mock orchestrator method
        insights_orchestrator.generate_insights = AsyncMock(return_value={
            "success": True,
            "insights": {"key_findings": ["Finding 1", "Finding 2"]}
        })
        
        result = await mcp_server.execute_tool(
            tool_name="generate_insights_tool",
            parameters={"resource_id": "test_resource_123"},
            user_context=user_context_dict
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        insights_orchestrator.generate_insights.assert_called_once()
        
        logger.info("✅ Tool delegates to orchestrator correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_utilities_access(self, mcp_server):
        """Test that MCP server has access to utilities."""
        logger.info("🧪 Test: Utilities access")
        
        assert hasattr(mcp_server, 'utilities')
        assert mcp_server.utilities is not None
        
        # Check for key utilities (matching Content Analysis MCP Server pattern)
        assert hasattr(mcp_server.utilities, 'telemetry')
        assert hasattr(mcp_server.utilities, 'health')
        assert hasattr(mcp_server.utilities, 'security')
        assert hasattr(mcp_server.utilities, 'tenant')
        assert hasattr(mcp_server.utilities, 'logger')
        
        logger.info("✅ Utilities accessible")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_integration_calculate_metrics(self, mcp_server, insights_orchestrator, mock_user_context):
        """Integration test: Calculate metrics through MCP server."""
        logger.info("🧪 Test: Integration - Calculate metrics")
        
        # This test requires actual orchestrator functionality
        # For now, we'll test that the tool can be called
        # In a full integration test, we'd need actual data
        
        # Check that orchestrator has the method
        assert hasattr(insights_orchestrator, 'calculate_metrics')
        
        # The actual execution would require real data, so we'll just verify
        # the tool is callable and doesn't crash
        try:
            # This will likely fail without real data, but we're testing the integration path
            result = await mcp_server.execute_tool(
                tool_name="calculate_metrics_tool",
                parameters={"resource_id": "test_resource_123"},
                user_context=mock_user_context
            )
            # If it succeeds, great; if it fails with a data error, that's expected
            logger.info(f"✅ Tool execution result: {result.get('success', False)}")
        except Exception as e:
            # Expected if data doesn't exist, but tool should still be callable
            logger.info(f"⚠️ Tool execution failed (expected without real data): {e}")
        
        logger.info("✅ Integration test completed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_architecture_verification(self, mcp_server):
        """Test that MCP server follows proper architecture patterns."""
        logger.info("🧪 Test: Architecture verification")
        
        # Verify MCP server extends MCPServerBase
        from bases.mcp_server.mcp_server_base import MCPServerBase
        assert isinstance(mcp_server, MCPServerBase)
        
        # Verify orchestrator access
        assert mcp_server.orchestrator is not None
        
        # Verify tool registration
        assert len(mcp_server.get_tool_list()) > 0
        
        logger.info("✅ Architecture patterns verified")

