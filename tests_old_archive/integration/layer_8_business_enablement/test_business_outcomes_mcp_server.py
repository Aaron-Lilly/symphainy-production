#!/usr/bin/env python3
"""
Business Outcomes MCP Server - Functional Tests

Tests BusinessOutcomesMCPServer to verify:
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
async def business_outcomes_orchestrator(smart_city_infrastructure):
    """
    BusinessOutcomesOrchestrator instance for each test.
    
    Reuses the orchestrator fixture pattern from test_business_outcomes_orchestrator.py
    """
    logger.info("🔧 Fixture: Starting business_outcomes_orchestrator fixture...")
    
    from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
    from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
    
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
    logger.info("🔧 Fixture: Creating BusinessOutcomesOrchestrator...")
    orchestrator = BusinessOutcomesOrchestrator(delivery_manager=manager)
    
    # Initialize orchestrator
    logger.info("🔧 Fixture: Initializing orchestrator...")
    try:
        result = await asyncio.wait_for(orchestrator.initialize(), timeout=90.0)
        if not result:
            pytest.fail("BusinessOutcomesOrchestrator failed to initialize")
    except asyncio.TimeoutError:
        pytest.fail("BusinessOutcomesOrchestrator initialization timed out")
    
    logger.info("✅ Fixture: Orchestrator ready")
    yield orchestrator
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture(scope="function")
def mcp_server(business_outcomes_orchestrator, smart_city_infrastructure):
    """
    BusinessOutcomesMCPServer instance for each test.
    
    The MCP server is created by the orchestrator during initialization,
    so we access it via orchestrator.mcp_server.
    """
    logger.info("🔧 Fixture: Getting MCP server from orchestrator...")
    
    if not hasattr(business_outcomes_orchestrator, 'mcp_server') or business_outcomes_orchestrator.mcp_server is None:
        pytest.fail("MCP server not initialized by orchestrator")
    
    server = business_outcomes_orchestrator.mcp_server
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

class TestBusinessOutcomesMCPServer:
    """Functional tests for Business Outcomes MCP Server."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_mcp_server_initialization(self, mcp_server):
        """Test MCP server initialization."""
        logger.info("🧪 Test: MCP server initialization")
        
        assert mcp_server is not None
        assert mcp_server.service_name == "business_outcomes_mcp"
        assert mcp_server.orchestrator is not None
        
        logger.info("✅ MCP server initialized correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_tool_registration(self, mcp_server):
        """Test that all tools are registered."""
        logger.info("🧪 Test: Tool registration")
        
        tool_list = mcp_server.get_tool_list()
        assert isinstance(tool_list, list)
        # Business Outcomes MCP Server has 10 tools
        assert len(tool_list) == 10
        
        expected_tools = [
            "track_outcomes_tool",
            "generate_roadmap_tool",
            "calculate_kpis_tool",
            "analyze_outcomes_tool",
            "generate_strategic_roadmap_tool",
            "generate_poc_proposal_tool",
            "generate_comprehensive_poc_tool",
            "create_comprehensive_strategic_plan_tool",
            "track_strategic_progress_tool",
            "analyze_strategic_trends_tool"
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
        assert guide.get("server_name") == "business_outcomes_mcp"
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
        assert health.get("server_name") == "business_outcomes_mcp"
        assert "tools_registered" in health
        assert health.get("tools_registered") == 10
        
        logger.info(f"✅ Health status: {health.get('status')}")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_version_info(self, mcp_server):
        """Test version info."""
        logger.info("🧪 Test: Version info")
        
        version_info = mcp_server.get_version_info()
        assert isinstance(version_info, dict)
        assert version_info.get("server_name") == "business_outcomes_mcp"
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
    async def test_track_outcomes_tool_delegation(self, mcp_server, business_outcomes_orchestrator, mock_user_context):
        """Test that track_outcomes_tool delegates to orchestrator."""
        logger.info("🧪 Test: track_outcomes_tool delegation")
        
        user_context_dict = {
            "user_id": mock_user_context.user_id,
            "tenant_id": mock_user_context.tenant_id,
            "permissions": mock_user_context.permissions
        }
        
        # Mock orchestrator method
        business_outcomes_orchestrator.track_outcomes = AsyncMock(return_value={
            "success": True,
            "outcomes": {"revenue": 1000, "profit": 500}
        })
        
        result = await mcp_server.execute_tool(
            tool_name="track_outcomes_tool",
            parameters={"resource_id": "test_resource_123"},
            user_context=user_context_dict
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True or "outcomes" in result
        business_outcomes_orchestrator.track_outcomes.assert_called_once()
        
        logger.info("✅ Tool delegates to orchestrator correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_calculate_kpis_tool_delegation(self, mcp_server, business_outcomes_orchestrator, mock_user_context):
        """Test that calculate_kpis_tool delegates to orchestrator."""
        logger.info("🧪 Test: calculate_kpis_tool delegation")
        
        user_context_dict = {
            "user_id": mock_user_context.user_id,
            "tenant_id": mock_user_context.tenant_id,
            "permissions": mock_user_context.permissions
        }
        
        # Mock orchestrator method
        business_outcomes_orchestrator.calculate_kpis = AsyncMock(return_value={
            "success": True,
            "kpis": {"revenue_growth": 10, "profit_margin": 20}
        })
        
        result = await mcp_server.execute_tool(
            tool_name="calculate_kpis_tool",
            parameters={"resource_id": "test_resource_123"},
            user_context=user_context_dict
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True or "kpis" in result
        business_outcomes_orchestrator.calculate_kpis.assert_called_once()
        
        logger.info("✅ Tool delegates to orchestrator correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_generate_roadmap_tool_delegation(self, mcp_server, business_outcomes_orchestrator, mock_user_context):
        """Test that generate_roadmap_tool delegates to orchestrator."""
        logger.info("🧪 Test: generate_roadmap_tool delegation")
        
        user_context_dict = {
            "user_id": mock_user_context.user_id,
            "tenant_id": mock_user_context.tenant_id,
            "permissions": mock_user_context.permissions
        }
        
        # Mock orchestrator method
        business_outcomes_orchestrator.generate_roadmap = AsyncMock(return_value={
            "success": True,
            "roadmap": {"phases": ["Phase 1", "Phase 2"]}
        })
        
        result = await mcp_server.execute_tool(
            tool_name="generate_roadmap_tool",
            parameters={"resource_id": "test_resource_123"},
            user_context=user_context_dict
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True or "roadmap" in result
        business_outcomes_orchestrator.generate_roadmap.assert_called_once()
        
        logger.info("✅ Tool delegates to orchestrator correctly")




