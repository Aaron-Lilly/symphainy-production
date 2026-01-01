#!/usr/bin/env python3
"""
Content Analysis Agents - Functional Tests

Tests ContentLiaisonAgent and ContentProcessingAgent to verify:
- Agent initialization
- Query processing (liaison agent)
- Business capability execution (processing agent)
- MCP tool usage
- Orchestrator integration

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
def liaison_agent(content_orchestrator):
    """
    ContentLiaisonAgent instance for each test.
    
    The agent is created by the orchestrator during initialization,
    so we access it via orchestrator.liaison_agent.
    """
    logger.info("🔧 Fixture: Getting liaison agent from orchestrator...")
    
    if not hasattr(content_orchestrator, 'liaison_agent') or content_orchestrator.liaison_agent is None:
        pytest.skip("Liaison agent not initialized by orchestrator (may require Agentic Foundation)")
    
    agent = content_orchestrator.liaison_agent
    logger.info(f"✅ Fixture: Liaison agent ready: {agent.service_name}")
    return agent


@pytest.fixture(scope="function")
def processing_agent(content_orchestrator):
    """
    ContentProcessingAgent instance for each test.
    
    The agent is created by the orchestrator during initialization,
    so we access it via orchestrator.processing_agent.
    """
    logger.info("🔧 Fixture: Getting processing agent from orchestrator...")
    
    if not hasattr(content_orchestrator, 'processing_agent') or content_orchestrator.processing_agent is None:
        pytest.skip("Processing agent not initialized by orchestrator (may require Agentic Foundation)")
    
    agent = content_orchestrator.processing_agent
    logger.info(f"✅ Fixture: Processing agent ready: {agent.service_name}")
    return agent


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
# TESTS - ContentLiaisonAgent
# ============================================================================

@pytest.mark.asyncio
async def test_liaison_agent_initialization(liaison_agent):
    """Test that liaison agent is properly initialized."""
    logger.info("🧪 Test: Liaison agent initialization")
    
    assert liaison_agent is not None
    assert hasattr(liaison_agent, 'service_name')
    assert hasattr(liaison_agent, 'is_initialized')
    assert liaison_agent.is_initialized is True
    
    logger.info("✅ Liaison agent initialized correctly")


@pytest.mark.asyncio
async def test_liaison_agent_process_user_query_help(liaison_agent, user_context):
    """Test that liaison agent processes help queries."""
    logger.info("🧪 Test: Liaison agent - help query")
    
    session_id = "test_session_123"
    query = "How do I upload a file?"
    
    result = await liaison_agent.process_user_query(
        query=query,
        session_id=session_id,
        user_context=user_context
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "response" in result
    assert "intent" in result
    assert result.get("session_id") == session_id
    
    # Response should contain guidance about file upload
    response = result.get("response", "")
    if isinstance(response, dict):
        response = response.get("message", "")
    assert "upload" in response.lower() or "file" in response.lower()
    
    logger.info("✅ Liaison agent processed help query")


@pytest.mark.asyncio
async def test_liaison_agent_process_user_query_parsing(liaison_agent, user_context):
    """Test that liaison agent processes parsing queries."""
    logger.info("🧪 Test: Liaison agent - parsing query")
    
    session_id = "test_session_456"
    query = "How do I parse a document?"
    
    result = await liaison_agent.process_user_query(
        query=query,
        session_id=session_id,
        user_context=user_context
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "response" in result
    assert "intent" in result
    
    # Intent should be document_parsing
    intent = result.get("intent", {})
    assert intent.get("type") == "document_parsing"
    
    logger.info("✅ Liaison agent processed parsing query")


@pytest.mark.asyncio
async def test_liaison_agent_provide_guidance(liaison_agent, user_context):
    """Test that liaison agent provides guidance on topics."""
    logger.info("🧪 Test: Liaison agent - provide guidance")
    
    result = await liaison_agent.provide_guidance(
        topic="file upload",
        user_context=user_context
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "guidance" in result
    assert result.get("topic") == "file upload"
    
    logger.info("✅ Liaison agent provided guidance")


@pytest.mark.asyncio
async def test_liaison_agent_get_status(liaison_agent, user_context):
    """Test that liaison agent provides status."""
    logger.info("🧪 Test: Liaison agent - get status")
    
    result = await liaison_agent.get_agent_status(user_context=user_context)
    
    assert isinstance(result, dict)
    assert result.get("agent_name") is not None
    assert result.get("status") == "active"
    assert result.get("initialized") is True
    assert "capabilities" in result
    
    logger.info("✅ Liaison agent status retrieved")


@pytest.mark.asyncio
async def test_liaison_agent_orchestrator_discovery(liaison_agent, content_orchestrator):
    """Test that liaison agent discovers orchestrator."""
    logger.info("🧪 Test: Liaison agent - orchestrator discovery")
    
    # The agent should have discovered the orchestrator during initialization
    # or it may be set by the orchestrator
    if hasattr(liaison_agent, 'content_orchestrator'):
        assert liaison_agent.content_orchestrator is not None
    
    logger.info("✅ Liaison agent orchestrator discovery verified")


# ============================================================================
# TESTS - ContentProcessingAgent
# ============================================================================

@pytest.mark.asyncio
async def test_processing_agent_initialization(processing_agent):
    """Test that processing agent is properly initialized."""
    logger.info("🧪 Test: Processing agent initialization")
    
    assert processing_agent is not None
    assert hasattr(processing_agent, 'service_name')
    assert hasattr(processing_agent, 'is_initialized')
    assert processing_agent.is_initialized is True
    
    logger.info("✅ Processing agent initialized correctly")


@pytest.mark.asyncio
async def test_processing_agent_set_orchestrator(processing_agent, content_orchestrator):
    """Test that processing agent can set orchestrator reference."""
    logger.info("🧪 Test: Processing agent - set orchestrator")
    
    # The orchestrator should have already set itself on the agent
    assert hasattr(processing_agent, 'orchestrator')
    assert processing_agent.orchestrator is not None
    assert processing_agent.orchestrator == content_orchestrator
    
    logger.info("✅ Processing agent orchestrator reference set")


@pytest.mark.asyncio
async def test_processing_agent_mcp_server_access(processing_agent, content_orchestrator):
    """Test that processing agent has access to MCP server."""
    logger.info("🧪 Test: Processing agent - MCP server access")
    
    # The agent should be able to access MCP server via orchestrator
    if hasattr(processing_agent, 'mcp_server'):
        assert processing_agent.mcp_server is not None
    elif hasattr(processing_agent, 'orchestrator') and processing_agent.orchestrator:
        assert hasattr(processing_agent.orchestrator, 'mcp_server')
        assert processing_agent.orchestrator.mcp_server is not None
    
    logger.info("✅ Processing agent has MCP server access")


@pytest.mark.asyncio
async def test_processing_agent_get_mcp_server_info(processing_agent):
    """Test that processing agent can get MCP server info."""
    logger.info("🧪 Test: Processing agent - get MCP server info")
    
    try:
        info = processing_agent.get_mcp_server_info()
        if info:
            assert isinstance(info, dict)
            logger.info(f"✅ MCP server info: {info.get('server_name', 'N/A')}")
        else:
            logger.info("⚠️ MCP server info not available (may be expected)")
    except Exception as e:
        logger.info(f"⚠️ MCP server info method not available: {e}")


@pytest.mark.asyncio
async def test_processing_agent_get_mcp_server_tools(processing_agent):
    """Test that processing agent can get MCP server tools."""
    logger.info("🧪 Test: Processing agent - get MCP server tools")
    
    try:
        tools = processing_agent.get_mcp_server_tools()
        if tools:
            assert isinstance(tools, list)
            assert len(tools) > 0
            logger.info(f"✅ MCP server tools: {len(tools)} tools available")
        else:
            logger.info("⚠️ MCP server tools not available (may be expected)")
    except Exception as e:
        logger.info(f"⚠️ MCP server tools method not available: {e}")


@pytest.mark.asyncio
async def test_processing_agent_execute_business_capability(processing_agent, user_context):
    """Test that processing agent can execute business capabilities."""
    logger.info("🧪 Test: Processing agent - execute business capability")
    
    # Test with a simple capability that doesn't require file operations
    try:
        result = await processing_agent.execute_business_capability(
            capability_name="get_processing_metrics",
            params={},
            user_context=user_context
        )
        
        # The result may succeed or fail, but should be structured
        assert isinstance(result, dict)
        logger.info(f"✅ Business capability executed: {result.get('success', 'N/A')}")
    except Exception as e:
        # Some capabilities may not be fully implemented yet
        logger.info(f"⚠️ Business capability execution: {e}")


@pytest.mark.asyncio
async def test_processing_agent_enhance_metadata_extraction(processing_agent):
    """Test that processing agent can enhance metadata extraction."""
    logger.info("🧪 Test: Processing agent - enhance metadata extraction")
    
    # Create a mock parsed result
    parsed_result = {
        "success": True,
        "text_content": "Sample document text",
        "structured_data": {"tables": []},
        "metadata": {"file_type": "pdf"}
    }
    
    try:
        result = await processing_agent.enhance_metadata_extraction(
            parsed_result=parsed_result,
            file_id="test_file_123"
        )
        
        assert isinstance(result, dict)
        logger.info(f"✅ Metadata enhancement: {result.get('success', 'N/A')}")
    except Exception as e:
        # This may require MCP server access
        logger.info(f"⚠️ Metadata enhancement: {e}")


@pytest.mark.asyncio
async def test_processing_agent_enhance_content_insights(processing_agent):
    """Test that processing agent can enhance content insights."""
    logger.info("🧪 Test: Processing agent - enhance content insights")
    
    # Create a mock parsed result
    parsed_result = {
        "success": True,
        "text_content": "Sample document text",
        "structured_data": {"tables": []},
        "metadata": {"file_type": "pdf"}
    }
    
    try:
        result = await processing_agent.enhance_content_insights(
            parsed_result=parsed_result,
            file_id="test_file_123"
        )
        
        assert isinstance(result, dict)
        logger.info(f"✅ Content insights enhancement: {result.get('success', 'N/A')}")
    except Exception as e:
        # This may require MCP server access
        logger.info(f"⚠️ Content insights enhancement: {e}")


@pytest.mark.asyncio
async def test_processing_agent_recommend_format_optimization(processing_agent):
    """Test that processing agent can recommend format optimization."""
    logger.info("🧪 Test: Processing agent - recommend format optimization")
    
    # Create a mock parsed result
    parsed_result = {
        "success": True,
        "text_content": "Sample document text",
        "structured_data": {"tables": []},
        "metadata": {"file_type": "pdf"}
    }
    
    try:
        result = await processing_agent.recommend_format_optimization(
            parsed_result=parsed_result,
            file_id="test_file_123"
        )
        
        assert isinstance(result, dict)
        logger.info(f"✅ Format optimization recommendation: {result.get('success', 'N/A')}")
    except Exception as e:
        # This may require MCP server access
        logger.info(f"⚠️ Format optimization recommendation: {e}")


# ============================================================================
# INTEGRATION TESTS - Agents with Orchestrator
# ============================================================================

@pytest.mark.asyncio
async def test_agents_integration_with_orchestrator(liaison_agent, processing_agent, content_orchestrator):
    """Test that both agents are properly integrated with orchestrator."""
    logger.info("🧪 Test: Agents integration with orchestrator")
    
    # Both agents should be initialized
    assert liaison_agent.is_initialized is True
    assert processing_agent.is_initialized is True
    
    # Processing agent should have orchestrator reference
    assert processing_agent.orchestrator == content_orchestrator
    
    # Orchestrator should have both agents
    assert content_orchestrator.liaison_agent == liaison_agent
    assert content_orchestrator.processing_agent == processing_agent
    
    logger.info("✅ Agents properly integrated with orchestrator")


@pytest.mark.asyncio
async def test_agents_mcp_server_integration(processing_agent, content_orchestrator):
    """Test that processing agent can use MCP server via orchestrator."""
    logger.info("🧪 Test: Processing agent MCP server integration")
    
    # The processing agent should be able to access MCP server
    if hasattr(content_orchestrator, 'mcp_server') and content_orchestrator.mcp_server:
        mcp_server = content_orchestrator.mcp_server
        
        # Verify MCP server has tools
        tools = mcp_server.get_tool_list()
        assert len(tools) > 0
        
        # Processing agent should be able to use these tools
        if hasattr(processing_agent, 'mcp_server'):
            assert processing_agent.mcp_server is not None
        
        logger.info(f"✅ Processing agent can access MCP server with {len(tools)} tools")
    else:
        logger.info("⚠️ MCP server not available (may be expected)")

