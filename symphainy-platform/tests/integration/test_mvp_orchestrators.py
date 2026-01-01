#!/usr/bin/env python3
"""
Integration Test for MVP Orchestrators

Tests that orchestrators can be discovered and initialized by Business Orchestrator,
and that they can access enabling services.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any

# Import orchestrators (updated to new locations)
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator


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


class MockBusinessOrchestrator:
    """Mock Business Orchestrator for testing."""
    
    def __init__(self):
        self.realm_name = "business_enablement"
        self.platform_gateway = MockPlatformGateway()
        self.di_container = MockDIContainer()
        self.logger = Mock()
        self.logger.info = Mock()
        self.logger.debug = Mock()
        self.logger.error = Mock()
        self.logger.warning = Mock()
        
        # Mock enabling services with correct method signatures
        self.data_analyzer_service = Mock()
        self.data_analyzer_service.analyze_data = AsyncMock(return_value={"success": True, "data": {"analysis": "test"}})
        
        self.metrics_calculator_service = Mock()
        self.metrics_calculator_service.calculate_kpi = AsyncMock(return_value={"success": True, "kpi_value": {"kpi1": 100}})
        self.metrics_calculator_service.calculate_metric = AsyncMock(return_value={"success": True, "metric_value": 100})
        
        self.visualization_engine_service = Mock()
        self.visualization_engine_service.create_visualization = AsyncMock(return_value={"success": True, "visualization": "chart"})
        
        self.workflow_manager_service = Mock()
        self.workflow_manager_service.execute_workflow = AsyncMock(return_value={"success": True, "workflow": "optimized"})


class MockCurator:
    """Mock Curator for Smart City service discovery."""
    
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


@pytest.fixture
def mock_business_orchestrator():
    """Create mock Business Orchestrator."""
    return MockBusinessOrchestrator()


@pytest.fixture
def mock_curator():
    """Create mock Curator."""
    return MockCurator()


@pytest.mark.asyncio
async def test_insights_orchestrator_initialization(mock_business_orchestrator):
    """Test Insights Orchestrator can be initialized."""
    try:
        # Create orchestrator
        orchestrator = InsightsOrchestrator(mock_business_orchestrator)
        
        # Mock Curator access
        mock_curator = MockCurator()
        orchestrator.di_container.foundation_services["CuratorFoundationService"] = mock_curator
        
        # Mock Smart City service discovery
        orchestrator.get_librarian_api = AsyncMock(return_value=Mock())
        orchestrator.get_data_steward_api = AsyncMock(return_value=Mock())
        orchestrator.register_with_curator = AsyncMock(return_value=True)
        orchestrator.store_document = AsyncMock(return_value={"document_id": "test_doc"})
        orchestrator.track_data_lineage = AsyncMock(return_value=True)
        
        # Initialize
        result = await orchestrator.initialize()
        
        assert result is True, "Insights Orchestrator should initialize successfully"
        assert orchestrator.is_initialized is True, "Orchestrator should be initialized"
        
        print("✅ Insights Orchestrator initialization test passed")
        
    except Exception as e:
        pytest.fail(f"Insights Orchestrator initialization failed: {e}")


@pytest.mark.asyncio
async def test_operations_orchestrator_initialization(mock_business_orchestrator):
    """Test Operations Orchestrator can be initialized."""
    try:
        # Create orchestrator
        orchestrator = OperationsOrchestrator(mock_business_orchestrator)
        
        # Mock Smart City service discovery
        orchestrator.get_librarian_api = AsyncMock(return_value=Mock())
        orchestrator.get_conductor_api = AsyncMock(return_value=Mock())
        orchestrator.register_with_curator = AsyncMock(return_value=True)
        orchestrator.store_document = AsyncMock(return_value={"document_id": "test_doc"})
        
        # Initialize
        result = await orchestrator.initialize()
        
        assert result is True, "Operations Orchestrator should initialize successfully"
        assert orchestrator.is_initialized is True, "Orchestrator should be initialized"
        
        print("✅ Operations Orchestrator initialization test passed")
        
    except Exception as e:
        pytest.fail(f"Operations Orchestrator initialization failed: {e}")


@pytest.mark.asyncio
async def test_insights_orchestrator_calculate_metrics(mock_business_orchestrator):
    """Test Insights Orchestrator can calculate metrics."""
    try:
        orchestrator = InsightsOrchestrator(mock_business_orchestrator)
        
        # Mock methods
        orchestrator.get_librarian_api = AsyncMock(return_value=Mock())
        orchestrator.get_data_steward_api = AsyncMock(return_value=Mock())
        orchestrator.register_with_curator = AsyncMock(return_value=True)
        orchestrator.store_document = AsyncMock(return_value={"document_id": "test_doc"})
        orchestrator.track_data_lineage = AsyncMock(return_value=True)
        
        await orchestrator.initialize()
        
        # Test calculate_metrics
        result = await orchestrator.calculate_metrics("test_resource", {})
        
        assert result.get("status") == "success", "Calculate metrics should succeed"
        assert "data" in result, "Result should contain data"
        
        print("✅ Insights Orchestrator calculate_metrics test passed")
        
    except Exception as e:
        pytest.fail(f"Insights Orchestrator calculate_metrics failed: {e}")


@pytest.mark.asyncio
async def test_operations_orchestrator_optimize_process(mock_business_orchestrator):
    """Test Operations Orchestrator can optimize process."""
    try:
        orchestrator = OperationsOrchestrator(mock_business_orchestrator)
        
        # Mock methods
        orchestrator.get_librarian_api = AsyncMock(return_value=Mock())
        orchestrator.get_conductor_api = AsyncMock(return_value=Mock())
        orchestrator.register_with_curator = AsyncMock(return_value=True)
        orchestrator.store_document = AsyncMock(return_value={"document_id": "test_doc"})
        
        await orchestrator.initialize()
        
        # Test optimize_process
        result = await orchestrator.optimize_process("test_resource", {})
        
        assert result.get("status") == "success", "Optimize process should succeed"
        
        print("✅ Operations Orchestrator optimize_process test passed")
        
    except Exception as e:
        pytest.fail(f"Operations Orchestrator optimize_process failed: {e}")


@pytest.mark.asyncio
async def test_orchestrator_execute_method(mock_business_orchestrator):
    """Test orchestrators execute method works."""
    try:
        # Test Insights Orchestrator
        insights = InsightsOrchestrator(mock_business_orchestrator)
        insights.get_librarian_api = AsyncMock(return_value=Mock())
        insights.get_data_steward_api = AsyncMock(return_value=Mock())
        insights.register_with_curator = AsyncMock(return_value=True)
        insights.store_document = AsyncMock(return_value={"document_id": "test_doc"})
        insights.track_data_lineage = AsyncMock(return_value=True)
        insights.calculate_metrics = AsyncMock(return_value={"status": "success"})
        
        await insights.initialize()
        
        result = await insights.execute({
            "action": "calculate_metrics",
            "params": {"resource_id": "test", "options": {}}
        })
        
        assert result.get("status") == "success", "Execute method should work"
        
        # Test Operations Orchestrator
        operations = OperationsOrchestrator(mock_business_orchestrator)
        operations.get_librarian_api = AsyncMock(return_value=Mock())
        operations.get_conductor_api = AsyncMock(return_value=Mock())
        operations.register_with_curator = AsyncMock(return_value=True)
        operations.store_document = AsyncMock(return_value={"document_id": "test_doc"})
        operations.optimize_process = AsyncMock(return_value={"status": "success"})
        
        await operations.initialize()
        
        result = await operations.execute({
            "action": "optimize_process",
            "params": {"resource_id": "test", "options": {}}
        })
        
        assert result.get("status") == "success", "Execute method should work"
        
        print("✅ Orchestrator execute method test passed")
        
    except Exception as e:
        pytest.fail(f"Orchestrator execute method failed: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

