#!/usr/bin/env python3
"""
Orchestrator Integration Test - Enabling Services and Agents

Tests that refactored orchestrators can:
1. Initialize with utility methods
2. Discover and use enabling services via Curator
3. Initialize agents via Agentic Foundation factory
4. Orchestrate enabling services and agents together
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Dict, Any, Optional

# Test all three refactored orchestrators
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator


# Mock DIContainerService
class MockDIContainerService:
    def __init__(self):
        self._services = {}
        self._utilities = {}
        self.logger = MagicMock()
        
        # Mock utility services
        self.mock_security = MagicMock()
        self.mock_security.check_permissions = AsyncMock(return_value=True)
        self.mock_tenant = MagicMock()
        self.mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        self.mock_telemetry = MagicMock()
        self.mock_telemetry.log_operation_with_telemetry = AsyncMock()
        self.mock_telemetry.record_platform_operation_event = AsyncMock()
        self.mock_telemetry.record_metric = AsyncMock()
        self.mock_error_handler = MagicMock()
        self.mock_error_handler.handle_error_with_audit = AsyncMock()
        self.mock_health = MagicMock()
        self.mock_health.record_metric = AsyncMock()
        
        self._utilities["security_authorization_utility"] = self.mock_security
        self._utilities["tenant_management_utility"] = self.mock_tenant
        self._utilities["telemetry_reporting_utility"] = self.mock_telemetry
        self._utilities["error_handler"] = self.mock_error_handler
        self._utilities["health_management_utility"] = self.mock_health

    def get_logger(self, name):
        return self.logger

    def get_utility(self, utility_name: str):
        return self._utilities.get(utility_name)

    def get_foundation_service(self, name: str):
        return self._services.get(name)

    def register_service(self, name: str, service: Any):
        self._services[name] = service


# Mock Platform Gateway
class MockPlatformGateway:
    def __init__(self):
        pass
    
    def get_abstraction(self, realm_name: str, abstraction_name: str):
        return None


# Mock Delivery Manager
class MockDeliveryManager:
    def __init__(self, di_container, platform_gateway):
        self.realm_name = "business_enablement"
        self.platform_gateway = platform_gateway
        self.di_container = di_container


# Mock Enabling Services
class MockDataAnalyzerService:
    def __init__(self):
        self.analyze_data = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_123",
            "results": {"summary": "Analysis complete"}
        })
        self.extract_entities = AsyncMock(return_value={
            "success": True,
            "entities": []
        })


class MockMetricsCalculatorService:
    def __init__(self):
        self.calculate_kpi = AsyncMock(return_value={
            "success": True,
            "kpi_value": 85.5,
            "kpi_name": "test_kpi"
        })


class MockVisualizationEngineService:
    def __init__(self):
        self.create_visualization = AsyncMock(return_value={
            "success": True,
            "visualization_id": "viz_123",
            "chart_data": {}
        })


class MockWorkflowConversionService:
    def __init__(self):
        self.convert_sop_to_workflow = AsyncMock(return_value={
            "success": True,
            "workflow_id": "workflow_123",
            "workflow": {"steps": []}
        })


class MockCoexistenceAnalysisService:
    def __init__(self):
        self.analyze_coexistence = AsyncMock(return_value={
            "success": True,
            "blueprint_id": "blueprint_123",
            "analysis": {}
        })


class MockReportGeneratorService:
    def __init__(self):
        self.generate_report = AsyncMock(return_value={
            "success": True,
            "report_id": "report_123",
            "report": {}
        })


# Mock Curator Foundation
class MockCuratorFoundation:
    def __init__(self):
        self.register_service = AsyncMock(return_value=True)
        self.register_agent = AsyncMock(return_value={"success": True})
        self.get_service = AsyncMock(return_value=None)
        self.get_registered_services = AsyncMock(return_value={"services": {}})
        self.discover_service = AsyncMock(return_value=None)


# Mock Agentic Foundation
class MockAgenticFoundation:
    def __init__(self):
        self.create_agent = AsyncMock()
        self._agent_cache = {}


# Mock Agents
class MockLiaisonAgent:
    def __init__(self):
        self.agent_name = "TestLiaisonAgent"
        self.agent_id = "test_liaison_agent"
        self.capabilities = ["conversation", "guidance"]
        self.process_query = AsyncMock(return_value={"response": "Test response"})
        self.process_message = AsyncMock(return_value={"response": "Test message response"})
        self.initialize = AsyncMock(return_value=True)
        self.is_initialized = True


class MockSpecialistAgent:
    def __init__(self):
        self.agent_name = "TestSpecialistAgent"
        self.agent_id = "test_specialist_agent"
        self.capabilities = ["specialist_capability"]
        self.execute_capability = AsyncMock(return_value={"success": True, "result": "Test result"})
        self.initialize = AsyncMock(return_value=True)
        self.is_initialized = True
        self.set_orchestrator = Mock()


# Mock Smart City Services
class MockLibrarian:
    def __init__(self):
        self.get_document = AsyncMock(return_value=None)
        self.store_document = AsyncMock(return_value={"document_id": "doc_123"})
        self.query_documents = AsyncMock(return_value={"documents": []})


class MockDataSteward:
    def __init__(self):
        self.track_lineage = AsyncMock(return_value=True)


class MockConductor:
    def __init__(self):
        self.execute_workflow = AsyncMock(return_value={"success": True})


# Fixtures
@pytest.fixture
def mock_di_container():
    return MockDIContainerService()


@pytest.fixture
def mock_platform_gateway():
    return MockPlatformGateway()


@pytest.fixture
def mock_delivery_manager(mock_di_container, mock_platform_gateway):
    return MockDeliveryManager(mock_di_container, mock_platform_gateway)


@pytest.fixture
def mock_curator_foundation():
    return MockCuratorFoundation()


@pytest.fixture
def mock_agentic_foundation():
    return MockAgenticFoundation()


@pytest.fixture
def mock_librarian():
    return MockLibrarian()


@pytest.fixture
def mock_data_steward():
    return MockDataSteward()


@pytest.fixture
def mock_conductor():
    return MockConductor()


@pytest.fixture
def mock_liaison_agent():
    return MockLiaisonAgent()


@pytest.fixture
def mock_specialist_agent():
    return MockSpecialistAgent()


@pytest.fixture
def mock_data_analyzer_service():
    return MockDataAnalyzerService()


@pytest.fixture
def mock_metrics_calculator_service():
    return MockMetricsCalculatorService()


@pytest.fixture
def mock_visualization_engine_service():
    return MockVisualizationEngineService()


@pytest.fixture
def mock_workflow_conversion_service():
    return MockWorkflowConversionService()


@pytest.fixture
def mock_coexistence_analysis_service():
    return MockCoexistenceAnalysisService()


@pytest.fixture
def mock_report_generator_service():
    return MockReportGeneratorService()


# Test Insights Orchestrator
@pytest.mark.asyncio
async def test_insights_orchestrator_initialization_with_utilities(
    mock_delivery_manager, mock_curator_foundation, mock_agentic_foundation,
    mock_librarian, mock_data_steward, mock_liaison_agent, mock_specialist_agent
):
    """Test that Insights Orchestrator initializes with utility methods."""
    mock_delivery_manager.di_container.register_service("CuratorFoundationService", mock_curator_foundation)
    mock_delivery_manager.di_container.register_service("AgenticFoundationService", mock_agentic_foundation)
    
    # Mock agent creation
    mock_agentic_foundation.create_agent = AsyncMock(side_effect=[
        mock_liaison_agent,
        mock_specialist_agent
    ])
    
    # Mock Smart City services and MCP server
    with patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator.InsightsMCPServer', new=MagicMock()), \
         patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator.StructuredAnalysisWorkflow', new=MagicMock()), \
         patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator.DataInsightsQueryService') as mock_query_service:
        
        mock_query_service_instance = MagicMock()
        mock_query_service_instance.initialize = AsyncMock(return_value=True)
        mock_query_service.return_value = mock_query_service_instance
        
        orchestrator = InsightsOrchestrator(mock_delivery_manager)
        
        # Mock realm service methods
        orchestrator._realm_service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        orchestrator._realm_service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        
        result = await orchestrator.initialize()
        
        assert result is True
        assert orchestrator.is_initialized is True
        
        # Verify utility methods were called
        assert mock_delivery_manager.di_container.mock_telemetry.log_operation_with_telemetry.called
        assert mock_delivery_manager.di_container.mock_health.record_metric.called
        
        # Verify agents were initialized
        assert orchestrator.liaison_agent is not None
        assert orchestrator.specialist_agent is not None
        
        print("✅ Insights Orchestrator initialization with utilities: PASSED")


@pytest.mark.asyncio
async def test_insights_orchestrator_enabling_service_orchestration(
    mock_delivery_manager, mock_data_analyzer_service, mock_metrics_calculator_service,
    mock_visualization_engine_service, mock_curator_foundation
):
    """Test that Insights Orchestrator can discover and use enabling services."""
    mock_delivery_manager.di_container.register_service("CuratorFoundationService", mock_curator_foundation)
    
    # Mock Curator to return enabling services
    async def mock_get_enabling_service(service_name):
        if service_name == "DataAnalyzerService":
            return mock_data_analyzer_service
        elif service_name == "MetricsCalculatorService":
            return mock_metrics_calculator_service
        elif service_name == "VisualizationEngineService":
            return mock_visualization_engine_service
        return None
    
    orchestrator = InsightsOrchestrator(mock_delivery_manager)
    orchestrator.get_enabling_service = mock_get_enabling_service
    
    # Test enabling service access
    data_analyzer = await orchestrator._get_data_analyzer_service()
    assert data_analyzer is not None
    assert data_analyzer == mock_data_analyzer_service
    
    metrics_calculator = await orchestrator._get_metrics_calculator_service()
    assert metrics_calculator is not None
    assert metrics_calculator == mock_metrics_calculator_service
    
    visualization_engine = await orchestrator._get_visualization_engine_service()
    assert visualization_engine is not None
    assert visualization_engine == mock_visualization_engine_service
    
    # Test orchestration - calculate metrics
    result = await mock_metrics_calculator_service.calculate_kpi(
        kpi_name="test_kpi",
        data_sources="test_data",
        kpi_formula=None
    )
    assert result["success"] is True
    assert result["kpi_value"] == 85.5
    
    print("✅ Insights Orchestrator enabling service orchestration: PASSED")


@pytest.mark.asyncio
async def test_operations_orchestrator_initialization_with_utilities(
    mock_delivery_manager, mock_curator_foundation, mock_agentic_foundation,
    mock_librarian, mock_conductor, mock_liaison_agent, mock_specialist_agent
):
    """Test that Operations Orchestrator initializes with utility methods."""
    mock_delivery_manager.di_container.register_service("CuratorFoundationService", mock_curator_foundation)
    mock_delivery_manager.di_container.register_service("AgenticFoundationService", mock_agentic_foundation)
    
    # Mock agent creation
    mock_agentic_foundation.create_agent = AsyncMock(side_effect=[
        mock_liaison_agent,
        mock_specialist_agent
    ])
    
    # Mock MCP server
    with patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator.OperationsMCPServer', new=MagicMock()):
        
        orchestrator = OperationsOrchestrator(mock_delivery_manager)
        
        # Mock realm service methods
        orchestrator._realm_service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        orchestrator._realm_service.get_conductor_api = AsyncMock(return_value=mock_conductor)
        
        result = await orchestrator.initialize()
        
        assert result is True
        assert orchestrator.is_initialized is True
        
        # Verify utility methods were called
        assert mock_delivery_manager.di_container.mock_telemetry.log_operation_with_telemetry.called
        assert mock_delivery_manager.di_container.mock_health.record_metric.called
        
        # Verify agents were initialized
        assert orchestrator.liaison_agent is not None
        assert orchestrator.specialist_agent is not None
        
        print("✅ Operations Orchestrator initialization with utilities: PASSED")


@pytest.mark.asyncio
async def test_operations_orchestrator_enabling_service_orchestration(
    mock_delivery_manager, mock_workflow_conversion_service,
    mock_coexistence_analysis_service, mock_curator_foundation
):
    """Test that Operations Orchestrator can discover and use enabling services."""
    mock_delivery_manager.di_container.register_service("CuratorFoundationService", mock_curator_foundation)
    
    # Mock Curator to return enabling services
    async def mock_get_enabling_service(service_name):
        if service_name == "WorkflowConversionService":
            return mock_workflow_conversion_service
        elif service_name == "CoexistenceAnalysisService":
            return mock_coexistence_analysis_service
        return None
    
    orchestrator = OperationsOrchestrator(mock_delivery_manager)
    orchestrator.get_enabling_service = mock_get_enabling_service
    
    # Test enabling service access
    workflow_conversion = await orchestrator._get_workflow_conversion_service()
    assert workflow_conversion is not None
    assert workflow_conversion == mock_workflow_conversion_service
    
    coexistence_analysis = await orchestrator._get_coexistence_analysis_service()
    assert coexistence_analysis is not None
    assert coexistence_analysis == mock_coexistence_analysis_service
    
    # Test orchestration - convert SOP to workflow
    result = await mock_workflow_conversion_service.convert_sop_to_workflow("sop_123")
    assert result["success"] is True
    assert result["workflow_id"] == "workflow_123"
    
    print("✅ Operations Orchestrator enabling service orchestration: PASSED")


@pytest.mark.asyncio
async def test_business_outcomes_orchestrator_initialization_with_utilities(
    mock_delivery_manager, mock_curator_foundation, mock_agentic_foundation,
    mock_librarian, mock_data_steward, mock_liaison_agent, mock_specialist_agent
):
    """Test that Business Outcomes Orchestrator initializes with utility methods."""
    mock_delivery_manager.di_container.register_service("CuratorFoundationService", mock_curator_foundation)
    mock_delivery_manager.di_container.register_service("AgenticFoundationService", mock_agentic_foundation)
    
    # Mock agent creation
    mock_agentic_foundation.create_agent = AsyncMock(side_effect=[
        mock_liaison_agent,
        mock_specialist_agent
    ])
    
    # Mock MCP server
    with patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator.BusinessOutcomesMCPServer', new=MagicMock()):
        
        orchestrator = BusinessOutcomesOrchestrator(mock_delivery_manager)
        
        # Mock realm service methods
        orchestrator._realm_service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        orchestrator._realm_service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        
        result = await orchestrator.initialize()
        
        assert result is True
        assert orchestrator.is_initialized is True
        
        # Verify utility methods were called
        assert mock_delivery_manager.di_container.mock_telemetry.log_operation_with_telemetry.called
        assert mock_delivery_manager.di_container.mock_health.record_metric.called
        
        # Verify agents were initialized
        assert orchestrator.liaison_agent is not None
        assert orchestrator.specialist_agent is not None
        
        print("✅ Business Outcomes Orchestrator initialization with utilities: PASSED")


@pytest.mark.asyncio
async def test_business_outcomes_orchestrator_enabling_service_orchestration(
    mock_delivery_manager, mock_metrics_calculator_service,
    mock_report_generator_service, mock_curator_foundation
):
    """Test that Business Outcomes Orchestrator can discover and use enabling services."""
    mock_delivery_manager.di_container.register_service("CuratorFoundationService", mock_curator_foundation)
    
    # Mock Curator to return enabling services
    async def mock_get_enabling_service(service_name):
        if service_name == "MetricsCalculatorService":
            return mock_metrics_calculator_service
        elif service_name == "ReportGeneratorService":
            return mock_report_generator_service
        return None
    
    orchestrator = BusinessOutcomesOrchestrator(mock_delivery_manager)
    orchestrator.get_enabling_service = mock_get_enabling_service
    
    # Test enabling service access
    metrics_calculator = await orchestrator._get_metrics_calculator_service()
    assert metrics_calculator is not None
    assert metrics_calculator == mock_metrics_calculator_service
    
    report_generator = await orchestrator._get_report_generator_service()
    assert report_generator is not None
    assert report_generator == mock_report_generator_service
    
    # Test orchestration - generate report
    result = await mock_report_generator_service.generate_report(
        template_id="test_template",
        data_id="test_data",
        options={}
    )
    assert result["success"] is True
    assert result["report_id"] == "report_123"
    
    print("✅ Business Outcomes Orchestrator enabling service orchestration: PASSED")


@pytest.mark.asyncio
async def test_orchestrator_agent_integration(
    mock_delivery_manager, mock_curator_foundation, mock_agentic_foundation,
    mock_liaison_agent, mock_specialist_agent, mock_librarian, mock_data_steward
):
    """Test that orchestrators can initialize and use agents via factory."""
    mock_delivery_manager.di_container.register_service("CuratorFoundationService", mock_curator_foundation)
    mock_delivery_manager.di_container.register_service("AgenticFoundationService", mock_agentic_foundation)
    
    # Mock agent creation
    mock_agentic_foundation.create_agent = AsyncMock(side_effect=[
        mock_liaison_agent,
        mock_specialist_agent
    ])
    
    # Test Insights Orchestrator agent integration
    with patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator.InsightsMCPServer', new=MagicMock()), \
         patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator.StructuredAnalysisWorkflow', new=MagicMock()), \
         patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator.DataInsightsQueryService') as mock_query_service:
        
        mock_query_service_instance = MagicMock()
        mock_query_service_instance.initialize = AsyncMock(return_value=True)
        mock_query_service.return_value = mock_query_service_instance
        
        orchestrator = InsightsOrchestrator(mock_delivery_manager)
        
        # Mock realm service methods
        orchestrator._realm_service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        orchestrator._realm_service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        
        result = await orchestrator.initialize()
        
        assert result is True
        assert orchestrator.liaison_agent is not None
        assert orchestrator.specialist_agent is not None
        
        # Test agent usage
        agent_response = await orchestrator.liaison_agent.process_query("test query", "session_123")
        assert agent_response["response"] == "Test response"
        
        # Verify agent was created via factory
        assert mock_agentic_foundation.create_agent.called
        create_agent_calls = mock_agentic_foundation.create_agent.call_args_list
        assert len(create_agent_calls) >= 2  # At least liaison and specialist
        
        print("✅ Orchestrator agent integration: PASSED")


@pytest.mark.asyncio
async def test_orchestrator_full_orchestration_flow(
    mock_delivery_manager, mock_curator_foundation, mock_agentic_foundation,
    mock_data_analyzer_service, mock_metrics_calculator_service,
    mock_liaison_agent, mock_specialist_agent, mock_librarian, mock_data_steward
):
    """Test full orchestration flow: enabling services + agents."""
    mock_delivery_manager.di_container.register_service("CuratorFoundationService", mock_curator_foundation)
    mock_delivery_manager.di_container.register_service("AgenticFoundationService", mock_agentic_foundation)
    
    # Mock agent creation
    mock_agentic_foundation.create_agent = AsyncMock(side_effect=[
        mock_liaison_agent,
        mock_specialist_agent
    ])
    
    # Mock enabling service discovery
    async def mock_get_enabling_service(service_name):
        if service_name == "DataAnalyzerService":
            return mock_data_analyzer_service
        elif service_name == "MetricsCalculatorService":
            return mock_metrics_calculator_service
        return None
    
    # Test Insights Orchestrator full flow
    with patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator.InsightsMCPServer', new=MagicMock()), \
         patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator.StructuredAnalysisWorkflow', new=MagicMock()), \
         patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator.DataInsightsQueryService') as mock_query_service:
        
        mock_query_service_instance = MagicMock()
        mock_query_service_instance.initialize = AsyncMock(return_value=True)
        mock_query_service.return_value = mock_query_service_instance
        
        orchestrator = InsightsOrchestrator(mock_delivery_manager)
        
        # Mock realm service methods
        orchestrator._realm_service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        orchestrator._realm_service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        orchestrator.get_enabling_service = mock_get_enabling_service
        
        # Initialize orchestrator
        result = await orchestrator.initialize()
        assert result is True
        
        # Test full orchestration: use enabling service + agent
        # 1. Get enabling service
        data_analyzer = await orchestrator._get_data_analyzer_service()
        assert data_analyzer is not None
        
        # 2. Use enabling service
        analysis_result = await data_analyzer.analyze_data(
            data_id="test_data",
            analysis_type="descriptive",
            analysis_options={}
        )
        assert analysis_result["success"] is True
        
        # 3. Use agent
        agent_response = await orchestrator.liaison_agent.process_query("analyze this data", "session_123")
        assert agent_response["response"] == "Test response"
        
        print("✅ Full orchestration flow (enabling services + agents): PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

