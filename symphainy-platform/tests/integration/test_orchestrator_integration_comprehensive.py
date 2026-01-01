#!/usr/bin/env python3
"""
Comprehensive Integration Test for MVP Orchestrators

Tests that all orchestrators work properly with:
- Business Orchestrator discovery and initialization
- Enabling services integration
- Smart City services integration
- End-to-end API execution
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any

# Import orchestrators (updated to new locations)
from backend.business_enablement.business_orchestrator.business_orchestrator_service import BusinessOrchestratorService
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
# Note: data_operations_orchestrator was non-functional and has been archived


class MockDIContainer:
    """Mock DI Container for testing."""
    
    def __init__(self):
        self.services = {}
        self.foundation_services = {}
        self.utilities = {}
        self.abstractions = {}
    
    def get_service(self, name: str):
        return self.services.get(name)
    
    def get_foundation_service(self, name: str):
        return self.foundation_services.get(name)
    
    def get_abstraction(self, name: str):
        if name not in self.abstractions:
            self.abstractions[name] = Mock()
        return self.abstractions.get(name)
    
    def get_utility(self, name: str):
        if name not in self.utilities:
            self.utilities[name] = Mock()
        return self.utilities.get(name)


class MockPlatformGateway:
    """Mock Platform Gateway for testing."""
    
    def get_abstraction(self, name: str):
        return Mock()
    
    def validate_access(self, realm_name: str, abstraction_name: str):
        return True


class MockCurator:
    """Mock Curator for Smart City service discovery."""
    
    def __init__(self):
        self.registered_services = {}
    
    async def get_registered_services(self):
        return {
            "services": {
                "Librarian": {
                    "realm": "smart_city",
                    "service_type": "smart_city_service",
                    "service_instance": Mock()
                },
                "DataSteward": {
                    "realm": "smart_city",
                    "service_type": "smart_city_service",
                    "service_instance": Mock()
                },
                "Conductor": {
                    "realm": "smart_city",
                    "service_type": "smart_city_service",
                    "service_instance": Mock()
                }
            }
        }
    
    async def register_service(self, **kwargs):
        return True
    
    async def register_capability(self, **kwargs):
        return True


class MockEnablingService:
    """Mock enabling service for testing."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.is_initialized = False
    
    async def initialize(self):
        self.is_initialized = True
        return True
    
    async def analyze_data(self, data_id: str, analysis_type: str, analysis_options: Optional[Dict[str, Any]] = None):
        return {"success": True, "data": {"analysis": "test_analysis", "type": analysis_type}}
    
    async def calculate_kpi(self, resource_id: str, metric_name: str, metric_params: Optional[Dict[str, Any]] = None):
        return {"success": True, "kpi_value": {"value": 100, "metric_name": metric_name}}
    
    async def create_visualization(self, data_id: str, visualization_type: str, options: Optional[Dict[str, Any]] = None):
        return {"success": True, "visualization": {"id": "viz_123", "type": visualization_type}}
    
    async def execute_workflow(self, workflow_definition: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
        return {"success": True, "workflow": {"id": "workflow_123", "status": "completed"}}
    
    async def generate_report(self, template_id: str, data_id: str, options: Optional[Dict[str, Any]] = None):
        return {"success": True, "report": {"id": "report_123", "template_id": template_id}}
    
    async def transform_data(self, data_id: str, transformation_rules: Dict[str, Any]):
        return {"success": True, "transformed_data_id": f"{data_id}_transformed", "transformation": "complete"}
    
    async def validate_data(self, data_id: str, validation_rules: Dict[str, Any]):
        return {"success": True, "validation": {"passed": True, "issues": []}}
    
    async def reconcile_data(self, source1_id: str, source2_id: str):
        return {"success": True, "reconciliation_id": "recon_123", "differences": []}
    
    async def export_data(self, data_id: str, export_format: str, options: Optional[Dict[str, Any]] = None):
        return {"success": True, "export": {"id": "export_123", "format": export_format}}


@pytest.fixture
def mock_setup():
    """Create mock setup for testing."""
    di_container = MockDIContainer()
    platform_gateway = MockPlatformGateway()
    curator = MockCurator()
    di_container.foundation_services["CuratorFoundationService"] = curator
    
    # Create mock enabling services
    enabling_services = {
        "data_analyzer_service": MockEnablingService("DataAnalyzerService"),
        "metrics_calculator_service": MockEnablingService("MetricsCalculatorService"),
        "visualization_engine_service": MockEnablingService("VisualizationEngineService"),
        "workflow_manager_service": MockEnablingService("WorkflowManagerService"),
        "report_generator_service": MockEnablingService("ReportGeneratorService"),
        "transformation_engine_service": MockEnablingService("TransformationEngineService"),
        "validation_engine_service": MockEnablingService("ValidationEngineService"),
        "reconciliation_service": MockEnablingService("ReconciliationService"),
        "export_formatter_service": MockEnablingService("ExportFormatterService")
    }
    
    # Create Business Orchestrator
    business_orchestrator = BusinessOrchestratorService(
        service_name="BusinessOrchestratorService",
        realm_name="business_enablement",
        platform_gateway=platform_gateway,
        di_container=di_container
    )
    
    # Attach enabling services
    for service_name, service_instance in enabling_services.items():
        setattr(business_orchestrator, service_name, service_instance)
    
    # Mock methods
    business_orchestrator._discover_enabling_services = AsyncMock(return_value=None)
    business_orchestrator.register_with_curator = AsyncMock(return_value=True)
    business_orchestrator.get_curator = Mock(return_value=curator)
    
    return {
        "business_orchestrator": business_orchestrator,
        "di_container": di_container,
        "platform_gateway": platform_gateway,
        "curator": curator,
        "enabling_services": enabling_services
    }


@pytest.mark.asyncio
async def test_all_orchestrators_initialized(mock_setup):
    """Test that Business Orchestrator initializes all 4 orchestrators."""
    business_orchestrator = mock_setup["business_orchestrator"]
    
    # Initialize Business Orchestrator
    result = await business_orchestrator.initialize()
    
    assert result is True, "Business Orchestrator should initialize successfully"
    
    # Check that all orchestrators were initialized
    expected_orchestrators = ["insights", "operations", "business_outcomes", "data_operations"]
    for orchestrator_name in expected_orchestrators:
        assert orchestrator_name in business_orchestrator.mvp_orchestrators, f"{orchestrator_name} orchestrator should be initialized"
        assert business_orchestrator.mvp_orchestrators[orchestrator_name].is_initialized is True, f"{orchestrator_name} orchestrator should be initialized"
    
    print(f"✅ All {len(business_orchestrator.mvp_orchestrators)} orchestrators initialized successfully")


@pytest.mark.asyncio
async def test_insights_orchestrator_execution(mock_setup):
    """Test Insights Orchestrator can execute use cases."""
    business_orchestrator = mock_setup["business_orchestrator"]
    await business_orchestrator.initialize()
    
    insights_orchestrator = business_orchestrator.mvp_orchestrators["insights"]
    
    # Mock Smart City services
    insights_orchestrator.store_document = AsyncMock(return_value={"document_id": "doc_123"})
    insights_orchestrator.track_data_lineage = AsyncMock(return_value=True)
    
    # Test calculate_metrics
    result = await insights_orchestrator.calculate_metrics("test_resource", {"analysis_type": "descriptive"})
    
    assert result.get("status") == "success", "Calculate metrics should succeed"
    assert "data" in result, "Result should contain data"
    
    print("✅ Insights Orchestrator calculate_metrics test passed")


@pytest.mark.asyncio
async def test_operations_orchestrator_execution(mock_setup):
    """Test Operations Orchestrator can execute use cases."""
    business_orchestrator = mock_setup["business_orchestrator"]
    await business_orchestrator.initialize()
    
    operations_orchestrator = business_orchestrator.mvp_orchestrators["operations"]
    
    # Mock Smart City services
    operations_orchestrator.store_document = AsyncMock(return_value={"document_id": "doc_123"})
    
    # Test optimize_process
    result = await operations_orchestrator.optimize_process(
        "test_resource",
        {"workflow_definition": {"steps": [{"name": "step1", "type": "action"}]}}
    )
    
    assert result.get("status") == "success", "Optimize process should succeed"
    
    print("✅ Operations Orchestrator optimize_process test passed")


@pytest.mark.asyncio
async def test_business_outcomes_orchestrator_execution(mock_setup):
    """Test Business Outcomes Orchestrator can execute use cases."""
    business_orchestrator = mock_setup["business_orchestrator"]
    await business_orchestrator.initialize()
    
    outcomes_orchestrator = business_orchestrator.mvp_orchestrators["business_outcomes"]
    
    # Mock Smart City services
    outcomes_orchestrator.store_document = AsyncMock(return_value={"document_id": "doc_123"})
    outcomes_orchestrator.track_data_lineage = AsyncMock(return_value=True)
    
    # Test track_outcomes
    result = await outcomes_orchestrator.track_outcomes("test_resource", {"metric_name": "test_kpi"})
    
    assert result.get("status") == "success", "Track outcomes should succeed"
    assert "data" in result, "Result should contain data"
    
    print("✅ Business Outcomes Orchestrator track_outcomes test passed")


@pytest.mark.asyncio
async def test_data_operations_orchestrator_execution(mock_setup):
    """Test Data Operations Orchestrator can execute use cases."""
    business_orchestrator = mock_setup["business_orchestrator"]
    await business_orchestrator.initialize()
    
    data_ops_orchestrator = business_orchestrator.mvp_orchestrators["data_operations"]
    
    # Mock Smart City services
    data_ops_orchestrator.store_document = AsyncMock(return_value={"document_id": "doc_123"})
    data_ops_orchestrator.track_data_lineage = AsyncMock(return_value=True)
    
    # Test transform_data
    result = await data_ops_orchestrator.transform_data(
        "test_resource",
        {"transformation_rules": {"mapping": "test"}}
    )
    
    assert result.get("status") == "success", "Transform data should succeed"
    assert "data" in result, "Result should contain data"
    
    print("✅ Data Operations Orchestrator transform_data test passed")


@pytest.mark.asyncio
async def test_business_orchestrator_routing(mock_setup):
    """Test Business Orchestrator routes requests correctly to all orchestrators."""
    business_orchestrator = mock_setup["business_orchestrator"]
    await business_orchestrator.initialize()
    
    # Mock orchestrator execute methods
    for orchestrator in business_orchestrator.mvp_orchestrators.values():
        orchestrator.store_document = AsyncMock(return_value={"document_id": "doc_123"})
        orchestrator.track_data_lineage = AsyncMock(return_value=True)
    
    # Test routing to each orchestrator
    test_cases = [
        ("insights", "calculate_metrics", {"resource_id": "test", "options": {}}),
        ("operations", "optimize_process", {"resource_id": "test", "options": {"workflow_definition": {"steps": []}}}),
        ("business_outcomes", "track_outcomes", {"resource_id": "test", "options": {}}),
        ("data_operations", "transform_data", {"resource_id": "test", "options": {"transformation_rules": {}}})
    ]
    
    for use_case, action, params in test_cases:
        result = await business_orchestrator.execute_use_case(
            use_case=use_case,
            request={"action": action, "params": params}
        )
        
        assert result.get("status") == "success" or "error" not in result, f"{use_case} routing should work"
        print(f"✅ {use_case} routing test passed")
    
    print("✅ All orchestrator routing tests passed")


@pytest.mark.asyncio
async def test_enabling_services_integration(mock_setup):
    """Test that orchestrators can access enabling services."""
    business_orchestrator = mock_setup["business_orchestrator"]
    await business_orchestrator.initialize()
    
    # Verify enabling services are accessible
    expected_services = [
        "data_analyzer_service",
        "metrics_calculator_service",
        "visualization_engine_service",
        "workflow_manager_service",
        "report_generator_service",
        "transformation_engine_service",
        "validation_engine_service",
        "reconciliation_service",
        "export_formatter_service"
    ]
    
    for service_name in expected_services:
        service = getattr(business_orchestrator, service_name, None)
        assert service is not None, f"{service_name} should be available"
        assert hasattr(service, "initialize"), f"{service_name} should have initialize method"
        print(f"✅ {service_name} is accessible")
    
    print("✅ All enabling services are accessible from orchestrators")


@pytest.mark.asyncio
async def test_orchestrator_execute_methods(mock_setup):
    """Test that all orchestrators' execute methods work."""
    business_orchestrator = mock_setup["business_orchestrator"]
    await business_orchestrator.initialize()
    
    # Mock Smart City services for all orchestrators
    for orchestrator in business_orchestrator.mvp_orchestrators.values():
        orchestrator.store_document = AsyncMock(return_value={"document_id": "doc_123"})
        orchestrator.track_data_lineage = AsyncMock(return_value=True)
    
    # Test execute method for each orchestrator
    test_cases = [
        ("insights", {"action": "calculate_metrics", "params": {"resource_id": "test", "options": {}}}),
        ("operations", {"action": "optimize_process", "params": {"resource_id": "test", "options": {"workflow_definition": {"steps": []}}}}),
        ("business_outcomes", {"action": "track_outcomes", "params": {"resource_id": "test", "options": {}}}),
        ("data_operations", {"action": "transform_data", "params": {"resource_id": "test", "options": {"transformation_rules": {}}}})
    ]
    
    for orchestrator_name, request in test_cases:
        orchestrator = business_orchestrator.mvp_orchestrators[orchestrator_name]
        result = await orchestrator.execute(request)
        
        assert result.get("status") == "success" or "error" not in result, f"{orchestrator_name} execute should work"
        print(f"✅ {orchestrator_name} execute method test passed")
    
    print("✅ All orchestrator execute methods work correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



