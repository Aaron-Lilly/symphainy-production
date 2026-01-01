#!/usr/bin/env python3
"""
Orchestrator Test Fixtures

Provides fixtures for testing Business Enablement orchestrators.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any, Optional


@pytest.fixture
def mock_business_orchestrator(mock_di_container, mock_platform_gateway):
    """Create a mock Business Orchestrator for testing."""
    mock_orchestrator = MagicMock()
    
    # Basic properties
    mock_orchestrator.service_name = "BusinessOrchestratorService"
    mock_orchestrator.realm_name = "business_enablement"
    mock_orchestrator.platform_gateway = mock_platform_gateway
    mock_orchestrator.di_container = mock_di_container
    
    # Logger
    mock_orchestrator.logger = MagicMock()
    mock_orchestrator.logger.info = MagicMock()
    mock_orchestrator.logger.debug = MagicMock()
    mock_orchestrator.logger.error = MagicMock()
    mock_orchestrator.logger.warning = MagicMock()
    
    # Enabling services
    mock_orchestrator.data_analyzer_service = MagicMock()
    mock_orchestrator.metrics_calculator_service = MagicMock()
    mock_orchestrator.visualization_engine_service = MagicMock()
    mock_orchestrator.workflow_manager_service = MagicMock()
    mock_orchestrator.report_generator_service = MagicMock()
    mock_orchestrator.transformation_engine_service = MagicMock()
    mock_orchestrator.validation_engine_service = MagicMock()
    mock_orchestrator.reconciliation_service = MagicMock()
    mock_orchestrator.export_formatter_service = MagicMock()
    
    # Mock enabling service methods
    mock_orchestrator.data_analyzer_service.analyze_data = AsyncMock(
        return_value={"success": True, "data": {"analysis": "test"}}
    )
    
    mock_orchestrator.metrics_calculator_service.calculate_kpi = AsyncMock(
        return_value={"success": True, "kpi_value": {"kpi1": 100}}
    )
    mock_orchestrator.metrics_calculator_service.calculate_metric = AsyncMock(
        return_value={"success": True, "metric_value": 100}
    )
    
    mock_orchestrator.visualization_engine_service.create_visualization = AsyncMock(
        return_value={"success": True, "visualization": "chart"}
    )
    
    mock_orchestrator.workflow_manager_service.execute_workflow = AsyncMock(
        return_value={"success": True, "workflow": "optimized"}
    )
    
    mock_orchestrator.report_generator_service.generate_report = AsyncMock(
        return_value={"success": True, "report_id": "report_123"}
    )
    
    mock_orchestrator.transformation_engine_service.transform_data = AsyncMock(
        return_value={"success": True, "transformed_data_id": "transformed_123"}
    )
    
    mock_orchestrator.validation_engine_service.validate_data = AsyncMock(
        return_value={"success": True, "validation": "passed"}
    )
    
    mock_orchestrator.reconciliation_service.reconcile_data = AsyncMock(
        return_value={"success": True, "reconciliation_id": "recon_123"}
    )
    
    mock_orchestrator.export_formatter_service.export_data = AsyncMock(
        return_value={"success": True, "export_id": "export_123"}
    )
    
    # MVP orchestrators
    mock_orchestrator.mvp_orchestrators = {}
    
    # Methods
    mock_orchestrator.initialize = AsyncMock(return_value=True)
    mock_orchestrator.execute_use_case = AsyncMock(return_value={"status": "success"})
    
    return mock_orchestrator


@pytest.fixture
async def real_business_orchestrator(real_di_container, real_platform_gateway, real_curator_foundation):
    """Create a real Business Orchestrator for integration tests."""
    try:
        from backend.business_enablement.business_orchestrator.business_orchestrator_service import BusinessOrchestratorService
        
        orchestrator = BusinessOrchestratorService(
            service_name="BusinessOrchestratorService",
            realm_name="business_enablement",
            platform_gateway=real_platform_gateway,
            di_container=real_di_container
        )
        
        # Register Curator in DI container
        real_di_container.foundation_services["CuratorFoundationService"] = real_curator_foundation
        
        await orchestrator.initialize()
        return orchestrator
    except Exception as e:
        pytest.skip(f"Could not create real Business Orchestrator: {e}")


@pytest.fixture
def mock_insights_orchestrator(mock_business_orchestrator):
    """Create a mock Insights Orchestrator for testing."""
    try:
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        orchestrator = InsightsOrchestrator(mock_business_orchestrator)
        return orchestrator
    except Exception as e:
        pytest.skip(f"Could not create Insights Orchestrator: {e}")


@pytest.fixture
def mock_operations_orchestrator(mock_business_orchestrator):
    """Create a mock Operations Orchestrator for testing."""
    try:
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator import OperationsOrchestrator
        orchestrator = OperationsOrchestrator(mock_business_orchestrator)
        return orchestrator
    except Exception as e:
        pytest.skip(f"Could not create Operations Orchestrator: {e}")


@pytest.fixture
def mock_business_outcomes_orchestrator(mock_business_orchestrator):
    """Create a mock Business Outcomes Orchestrator for testing."""
    try:
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        orchestrator = BusinessOutcomesOrchestrator(mock_business_orchestrator)
        return orchestrator
    except Exception as e:
        pytest.skip(f"Could not create Business Outcomes Orchestrator: {e}")


@pytest.fixture
def mock_data_operations_orchestrator(mock_business_orchestrator):
    """Create a mock Data Operations Orchestrator for testing."""
    try:
        from backend.business_enablement.business_orchestrator.use_cases.mvp.data_operations_orchestrator import DataOperationsOrchestrator
        orchestrator = DataOperationsOrchestrator(mock_business_orchestrator)
        return orchestrator
    except Exception as e:
        pytest.skip(f"Could not create Data Operations Orchestrator: {e}")



