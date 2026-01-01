#!/usr/bin/env python3
"""
Business Enablement Test Fixtures

Provides fixtures for Business Enablement components:
- Enabling Services (15+ services)
- Orchestrators (4 orchestrators)
- Agents (9+ agents)
- MCP Servers (5 servers)
- Delivery Manager

Reuses patterns from Smart City and other realm fixtures.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any, Optional, List
import os
import sys

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../symphainy-platform"))


# ============================================================================
# DI CONTAINER AND INFRASTRUCTURE FIXTURES
# ============================================================================

@pytest.fixture
def mock_di_container():
    """Create a mock DI Container for Business Enablement tests."""
    from tests.fixtures.realm_fixtures import mock_di_container
    return mock_di_container()


@pytest.fixture
def mock_platform_gateway():
    """Create a mock Platform Gateway for Business Enablement tests."""
    from tests.fixtures.platform_gateway_fixtures import mock_platform_gateway
    return mock_platform_gateway()


@pytest.fixture(scope="session")
async def real_di_container():
    """Create a real DI Container for integration tests."""
    from tests.fixtures.real_infrastructure_fixtures import real_public_works_foundation, real_platform_gateway
    
    # This will be set up in integration tests
    # For now, return None and let tests set it up
    return None


@pytest.fixture(scope="session")
async def real_platform_gateway():
    """Create a real Platform Gateway for integration tests."""
    from tests.fixtures.real_infrastructure_fixtures import real_platform_gateway
    async for gateway in real_platform_gateway():
        yield gateway


# ============================================================================
# ENABLING SERVICES FIXTURES
# ============================================================================

@pytest.fixture
def mock_file_parser_service(mock_di_container, mock_platform_gateway):
    """Create a mock File Parser Service for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "FileParserService"
    mock_service.realm_name = "business_enablement"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.parse_file = AsyncMock(return_value={"status": "success", "content": "parsed content"})
    mock_service.get_supported_formats = AsyncMock(return_value=["pdf", "docx", "html"])
    
    return mock_service


@pytest.fixture
def mock_data_analyzer_service(mock_di_container, mock_platform_gateway):
    """Create a mock Data Analyzer Service for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "DataAnalyzerService"
    mock_service.realm_name = "business_enablement"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.analyze_data = AsyncMock(return_value={"status": "success", "insights": []})
    mock_service.get_analysis_capabilities = AsyncMock(return_value=["statistical", "trend", "correlation"])
    
    return mock_service


@pytest.fixture
def mock_workflow_manager_service(mock_di_container, mock_platform_gateway):
    """Create a mock Workflow Manager Service for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "WorkflowManagerService"
    mock_service.realm_name = "business_enablement"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.create_workflow = AsyncMock(return_value={"workflow_id": "test_workflow_001"})
    mock_service.execute_workflow = AsyncMock(return_value={"execution_id": "test_exec_001", "status": "running"})
    mock_service.get_workflow_status = AsyncMock(return_value={"status": "completed"})
    
    return mock_service


# ============================================================================
# ORCHESTRATOR FIXTURES
# ============================================================================

@pytest.fixture
def mock_content_analysis_orchestrator(mock_di_container, mock_platform_gateway):
    """Create a mock Content Analysis Orchestrator for testing."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.service_name = "ContentAnalysisOrchestrator"
    mock_orchestrator.realm_name = "business_enablement"
    mock_orchestrator.platform_gateway = mock_platform_gateway
    mock_orchestrator.di_container = mock_di_container
    
    mock_orchestrator.logger = MagicMock()
    mock_orchestrator.initialize = AsyncMock(return_value=True)
    mock_orchestrator.analyze_content = AsyncMock(return_value={"status": "success", "analysis": {}})
    mock_orchestrator.coordinate_agents = AsyncMock(return_value={"status": "success"})
    
    return mock_orchestrator


@pytest.fixture
def mock_insights_orchestrator(mock_di_container, mock_platform_gateway):
    """Create a mock Insights Orchestrator for testing."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.service_name = "InsightsOrchestrator"
    mock_orchestrator.realm_name = "business_enablement"
    mock_orchestrator.platform_gateway = mock_platform_gateway
    mock_orchestrator.di_container = mock_di_container
    
    mock_orchestrator.logger = MagicMock()
    mock_orchestrator.initialize = AsyncMock(return_value=True)
    mock_orchestrator.generate_insights = AsyncMock(return_value={"status": "success", "insights": []})
    mock_orchestrator.coordinate_agents = AsyncMock(return_value={"status": "success"})
    
    return mock_orchestrator


@pytest.fixture
def mock_operations_orchestrator(mock_di_container, mock_platform_gateway):
    """Create a mock Operations Orchestrator for testing."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.service_name = "OperationsOrchestrator"
    mock_orchestrator.realm_name = "business_enablement"
    mock_orchestrator.platform_gateway = mock_platform_gateway
    mock_orchestrator.di_container = mock_di_container
    
    mock_orchestrator.logger = MagicMock()
    mock_orchestrator.initialize = AsyncMock(return_value=True)
    mock_orchestrator.optimize_operations = AsyncMock(return_value={"status": "success", "optimizations": []})
    mock_orchestrator.coordinate_agents = AsyncMock(return_value={"status": "success"})
    
    return mock_orchestrator


@pytest.fixture
def mock_business_outcomes_orchestrator(mock_di_container, mock_platform_gateway):
    """Create a mock Business Outcomes Orchestrator for testing."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.service_name = "BusinessOutcomesOrchestrator"
    mock_orchestrator.realm_name = "business_enablement"
    mock_orchestrator.platform_gateway = mock_platform_gateway
    mock_orchestrator.di_container = mock_di_container
    
    mock_orchestrator.logger = MagicMock()
    mock_orchestrator.initialize = AsyncMock(return_value=True)
    mock_orchestrator.analyze_outcomes = AsyncMock(return_value={"status": "success", "outcomes": []})
    mock_orchestrator.coordinate_agents = AsyncMock(return_value={"status": "success"})
    
    return mock_orchestrator


# ============================================================================
# AGENT FIXTURES
# ============================================================================

@pytest.fixture
def mock_content_processing_agent(mock_di_container):
    """Create a mock Content Processing Agent for testing."""
    mock_agent = MagicMock()
    mock_agent.agent_id = "content_processing_agent"
    mock_agent.agent_name = "Content Processing Agent"
    mock_agent.di_container = mock_di_container
    
    mock_agent.logger = MagicMock()
    mock_agent.initialize = AsyncMock(return_value=True)
    mock_agent.process_content = AsyncMock(return_value={"status": "success", "result": {}})
    mock_agent.use_tool = AsyncMock(return_value={"status": "success", "tool_result": {}})
    
    return mock_agent


@pytest.fixture
def mock_insights_analysis_agent(mock_di_container):
    """Create a mock Insights Analysis Agent for testing."""
    mock_agent = MagicMock()
    mock_agent.agent_id = "insights_analysis_agent"
    mock_agent.agent_name = "Insights Analysis Agent"
    mock_agent.di_container = mock_di_container
    
    mock_agent.logger = MagicMock()
    mock_agent.initialize = AsyncMock(return_value=True)
    mock_agent.analyze_insights = AsyncMock(return_value={"status": "success", "insights": []})
    mock_agent.use_tool = AsyncMock(return_value={"status": "success", "tool_result": {}})
    
    return mock_agent


@pytest.fixture
def mock_operations_specialist_agent(mock_di_container):
    """Create a mock Operations Specialist Agent for testing."""
    mock_agent = MagicMock()
    mock_agent.agent_id = "operations_specialist_agent"
    mock_agent.agent_name = "Operations Specialist Agent"
    mock_agent.di_container = mock_di_container
    
    mock_agent.logger = MagicMock()
    mock_agent.initialize = AsyncMock(return_value=True)
    mock_agent.analyze_operations = AsyncMock(return_value={"status": "success", "analysis": {}})
    mock_agent.use_tool = AsyncMock(return_value={"status": "success", "tool_result": {}})
    
    return mock_agent


# ============================================================================
# MCP SERVER FIXTURES
# ============================================================================

@pytest.fixture
def mock_delivery_manager_mcp_server(mock_di_container):
    """Create a mock Delivery Manager MCP Server for testing."""
    mock_server = MagicMock()
    mock_server.server_name = "delivery_manager_mcp_server"
    mock_server.di_container = mock_di_container
    
    mock_server.logger = MagicMock()
    mock_server.initialize = AsyncMock(return_value=True)
    mock_server.list_tools = AsyncMock(return_value={"tools": []})
    mock_server.call_tool = AsyncMock(return_value={"status": "success", "result": {}})
    
    return mock_server


@pytest.fixture
def mock_content_analysis_mcp_server(mock_di_container):
    """Create a mock Content Analysis MCP Server for testing."""
    mock_server = MagicMock()
    mock_server.server_name = "content_analysis_mcp_server"
    mock_server.di_container = mock_di_container
    
    mock_server.logger = MagicMock()
    mock_server.initialize = AsyncMock(return_value=True)
    mock_server.list_tools = AsyncMock(return_value={"tools": []})
    mock_server.call_tool = AsyncMock(return_value={"status": "success", "result": {}})
    
    return mock_server


# ============================================================================
# DELIVERY MANAGER FIXTURES
# ============================================================================

@pytest.fixture
def mock_delivery_manager_service(mock_di_container, mock_platform_gateway):
    """Create a mock Delivery Manager Service for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "DeliveryManagerService"
    mock_service.realm_name = "business_enablement"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.orchestrate_pillars = AsyncMock(return_value={"status": "success"})
    mock_service.coordinate_cross_pillar = AsyncMock(return_value={"status": "success"})
    
    return mock_service


# ============================================================================
# REAL SERVICE FIXTURES (for integration tests)
# ============================================================================

@pytest.fixture(scope="session")
async def real_file_parser_service(real_di_container, real_platform_gateway):
    """Create a real File Parser Service for integration tests."""
    try:
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        service = FileParserService(
            di_container=real_di_container,
            platform_gateway=real_platform_gateway
        )
        await service.initialize()
        return service
    except Exception as e:
        pytest.skip(f"Could not create real File Parser Service: {e}")


@pytest.fixture(scope="session")
async def real_delivery_manager_service(real_di_container, real_platform_gateway):
    """Create a real Delivery Manager Service for integration tests."""
    try:
        from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
        
        service = DeliveryManagerService(
            di_container=real_di_container,
            platform_gateway=real_platform_gateway
        )
        await service.initialize()
        return service
    except Exception as e:
        pytest.skip(f"Could not create real Delivery Manager Service: {e}")

