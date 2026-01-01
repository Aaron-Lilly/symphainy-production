#!/usr/bin/env python3
"""
Client-Scoped Execution Tests

Unit tests for client-scoped solution and journey execution.

Validates:
- deploy_solution() with client_id validation
- execute_journey() with client_id validation
- Client ID mismatch errors
- Client ID extraction from context
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Optional

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.unit]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_solution_composer():
    """Mock SolutionComposerService."""
    service = AsyncMock()
    
    # Mock methods
    service.retrieve_document = AsyncMock()
    service.store_document = AsyncMock()
    
    # Mock base class methods
    service.get_security = Mock(return_value=Mock(check_permissions=AsyncMock(return_value=True)))
    service.get_tenant = Mock(return_value=None)
    service.handle_error_with_audit = AsyncMock()
    service.record_health_metric = AsyncMock()
    service.log_operation_with_telemetry = AsyncMock()
    service.logger = Mock()
    
    return service


@pytest.fixture
def mock_journey_orchestrator():
    """Mock StructuredJourneyOrchestratorService."""
    service = AsyncMock()
    
    # Mock methods
    service.retrieve_document = AsyncMock()
    service.store_document = AsyncMock()
    service.session_manager = None
    
    # Mock base class methods
    service.get_security = Mock(return_value=Mock(check_permissions=AsyncMock(return_value=True)))
    service.get_tenant = Mock(return_value=Mock(validate_tenant_access=AsyncMock(return_value=True)))
    service.handle_error_with_audit = AsyncMock()
    service.record_health_metric = AsyncMock()
    service.log_operation_with_telemetry = AsyncMock()
    service.logger = Mock()
    
    return service


@pytest.fixture
def test_user_context():
    """Test user context."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "session_id": "test_session_123"
    }


@pytest.fixture
def solution_with_client_id():
    """Solution with client_id."""
    return {
        "solution_id": "solution_123",
        "solution_type": "mvp_solution",
        "client_id": "client_456",
        "phases": [{"phase_id": "phase_1"}],
        "status": "designed"
    }


@pytest.fixture
def journey_with_client_id():
    """Journey with client_id."""
    return {
        "journey_id": "journey_123",
        "journey_type": "workflow",
        "client_id": "client_456",
        "milestones": [{"milestone_id": "milestone_1"}],
        "status": "designed"
    }


# ============================================================================
# SOLUTION EXECUTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_deploy_solution_with_client_id_validation(
    mock_solution_composer,
    solution_with_client_id,
    test_user_context
):
    """
    Test deploy_solution with client_id validation (success).
    
    Validates:
    - Client ID validation works
    - Solution deployment succeeds when client_id matches
    """
    logger.info("🧪 Test: Deploy solution with client_id validation (success)...")
    
    # Setup mocks
    mock_solution_composer.retrieve_document.return_value = {
        "document": solution_with_client_id
    }
    
    # Import and patch
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    
    service = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    # Patch methods
    service.retrieve_document = mock_solution_composer.retrieve_document
    service.store_document = mock_solution_composer.store_document
    service.get_security = mock_solution_composer.get_security
    service.get_tenant = mock_solution_composer.get_tenant
    service.handle_error_with_audit = mock_solution_composer.handle_error_with_audit
    service.record_health_metric = mock_solution_composer.record_health_metric
    service.log_operation_with_telemetry = mock_solution_composer.log_operation_with_telemetry
    service.logger = mock_solution_composer.logger
    service.active_solutions = {}
    
    # Execute
    result = await service.deploy_solution(
        solution_id="solution_123",
        user_id="user_123",
        context={"deployment_strategy": "standard"},
        client_id="client_456",
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is True, "Deployment should succeed"
    assert result["deployment"]["client_id"] == "client_456", "Client ID should be stored"
    
    logger.info("✅ Test passed: Client ID validation works")


@pytest.mark.asyncio
async def test_deploy_solution_client_id_mismatch(
    mock_solution_composer,
    solution_with_client_id,
    test_user_context
):
    """
    Test deploy_solution fails when client_id doesn't match.
    
    Validates:
    - Client ID mismatch is detected
    - Deployment fails with appropriate error
    """
    logger.info("🧪 Test: Deploy solution with client_id mismatch...")
    
    # Setup mocks
    mock_solution_composer.retrieve_document.return_value = {
        "document": solution_with_client_id
    }
    
    # Import and patch
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    
    service = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    # Patch methods
    service.retrieve_document = mock_solution_composer.retrieve_document
    service.get_security = mock_solution_composer.get_security
    service.get_tenant = mock_solution_composer.get_tenant
    service.handle_error_with_audit = mock_solution_composer.handle_error_with_audit
    service.record_health_metric = mock_solution_composer.record_health_metric
    service.log_operation_with_telemetry = mock_solution_composer.log_operation_with_telemetry
    service.logger = mock_solution_composer.logger
    
    # Execute with wrong client_id
    result = await service.deploy_solution(
        solution_id="solution_123",
        user_id="user_123",
        context={"deployment_strategy": "standard"},
        client_id="wrong_client",
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is False, "Deployment should fail"
    assert "client_id" in result["error"].lower(), "Error should mention client_id mismatch"
    
    logger.info("✅ Test passed: Client ID mismatch detection works")


@pytest.mark.asyncio
async def test_deploy_solution_client_id_from_context(
    mock_solution_composer,
    solution_with_client_id,
    test_user_context
):
    """
    Test deploy_solution extracts client_id from context.
    
    Validates:
    - Client ID can be extracted from context if not provided as parameter
    """
    logger.info("🧪 Test: Deploy solution with client_id from context...")
    
    # Setup mocks
    mock_solution_composer.retrieve_document.return_value = {
        "document": solution_with_client_id
    }
    
    # Import and patch
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    
    service = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    # Patch methods
    service.retrieve_document = mock_solution_composer.retrieve_document
    service.store_document = mock_solution_composer.store_document
    service.get_security = mock_solution_composer.get_security
    service.get_tenant = mock_solution_composer.get_tenant
    service.handle_error_with_audit = mock_solution_composer.handle_error_with_audit
    service.record_health_metric = mock_solution_composer.record_health_metric
    service.log_operation_with_telemetry = mock_solution_composer.log_operation_with_telemetry
    service.logger = mock_solution_composer.logger
    service.active_solutions = {}
    
    # Execute with client_id in context (not as parameter)
    result = await service.deploy_solution(
        solution_id="solution_123",
        user_id="user_123",
        context={"deployment_strategy": "standard", "client_id": "client_456"},
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is True, "Deployment should succeed"
    assert result["deployment"]["client_id"] == "client_456", "Client ID should be extracted from context"
    
    logger.info("✅ Test passed: Client ID extraction from context works")


# ============================================================================
# JOURNEY EXECUTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_execute_journey_with_client_id_validation(
    mock_journey_orchestrator,
    journey_with_client_id,
    test_user_context
):
    """
    Test execute_journey with client_id validation (success).
    
    Validates:
    - Client ID validation works
    - Journey execution succeeds when client_id matches
    """
    logger.info("🧪 Test: Execute journey with client_id validation (success)...")
    
    # Setup mocks
    mock_journey_orchestrator.retrieve_document.return_value = {
        "document": journey_with_client_id
    }
    
    # Import and patch
    from backend.journey.services.structured_journey_orchestrator_service.structured_journey_orchestrator_service import StructuredJourneyOrchestratorService
    
    service = StructuredJourneyOrchestratorService(
        service_name="StructuredJourneyOrchestratorService",
        realm_name="journey",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    # Patch methods
    service.retrieve_document = mock_journey_orchestrator.retrieve_document
    service.store_document = mock_journey_orchestrator.store_document
    service.security = Mock(check_permissions=AsyncMock(return_value=True))  # Journey uses self.security directly
    service.tenant = Mock(validate_tenant_access=AsyncMock(return_value=True))  # Journey uses self.tenant directly
    service.handle_error_with_audit = mock_journey_orchestrator.handle_error_with_audit
    service.record_health_metric = mock_journey_orchestrator.record_health_metric
    service.log_operation_with_telemetry = mock_journey_orchestrator.log_operation_with_telemetry
    service.logger = mock_journey_orchestrator.logger
    service.session_manager = None
    service.active_journeys = {}
    
    # Execute
    result = await service.execute_journey(
        journey_id="journey_123",
        user_id="user_123",
        context={"execution_mode": "standard"},
        client_id="client_456",
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is True, "Execution should succeed"
    assert result["execution"]["client_id"] == "client_456", "Client ID should be stored"
    
    logger.info("✅ Test passed: Client ID validation works")


@pytest.mark.asyncio
async def test_execute_journey_client_id_mismatch(
    mock_journey_orchestrator,
    journey_with_client_id,
    test_user_context
):
    """
    Test execute_journey fails when client_id doesn't match.
    
    Validates:
    - Client ID mismatch is detected
    - Execution fails with appropriate error
    """
    logger.info("🧪 Test: Execute journey with client_id mismatch...")
    
    # Setup mocks
    mock_journey_orchestrator.retrieve_document.return_value = {
        "document": journey_with_client_id
    }
    
    # Import and patch
    from backend.journey.services.structured_journey_orchestrator_service.structured_journey_orchestrator_service import StructuredJourneyOrchestratorService
    
    service = StructuredJourneyOrchestratorService(
        service_name="StructuredJourneyOrchestratorService",
        realm_name="journey",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    # Patch methods
    service.retrieve_document = mock_journey_orchestrator.retrieve_document
    service.security = Mock(check_permissions=AsyncMock(return_value=True))  # Journey uses self.security directly
    service.tenant = Mock(validate_tenant_access=AsyncMock(return_value=True))  # Journey uses self.tenant directly
    service.handle_error_with_audit = mock_journey_orchestrator.handle_error_with_audit
    service.record_health_metric = mock_journey_orchestrator.record_health_metric
    service.log_operation_with_telemetry = mock_journey_orchestrator.log_operation_with_telemetry
    service.logger = mock_journey_orchestrator.logger
    
    # Execute with wrong client_id
    result = await service.execute_journey(
        journey_id="journey_123",
        user_id="user_123",
        context={"execution_mode": "standard"},
        client_id="wrong_client",
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is False, "Execution should fail"
    assert "client_id" in result["error"].lower(), "Error should mention client_id mismatch"
    
    logger.info("✅ Test passed: Client ID mismatch detection works")


@pytest.mark.asyncio
async def test_execute_journey_client_id_from_context(
    mock_journey_orchestrator,
    journey_with_client_id,
    test_user_context
):
    """
    Test execute_journey extracts client_id from context.
    
    Validates:
    - Client ID can be extracted from context if not provided as parameter
    """
    logger.info("🧪 Test: Execute journey with client_id from context...")
    
    # Setup mocks
    mock_journey_orchestrator.retrieve_document.return_value = {
        "document": journey_with_client_id
    }
    
    # Import and patch
    from backend.journey.services.structured_journey_orchestrator_service.structured_journey_orchestrator_service import StructuredJourneyOrchestratorService
    
    service = StructuredJourneyOrchestratorService(
        service_name="StructuredJourneyOrchestratorService",
        realm_name="journey",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    # Patch methods
    service.retrieve_document = mock_journey_orchestrator.retrieve_document
    service.store_document = mock_journey_orchestrator.store_document
    service.security = Mock(check_permissions=AsyncMock(return_value=True))  # Journey uses self.security directly
    service.tenant = Mock(validate_tenant_access=AsyncMock(return_value=True))  # Journey uses self.tenant directly
    service.handle_error_with_audit = mock_journey_orchestrator.handle_error_with_audit
    service.record_health_metric = mock_journey_orchestrator.record_health_metric
    service.log_operation_with_telemetry = mock_journey_orchestrator.log_operation_with_telemetry
    service.logger = mock_journey_orchestrator.logger
    service.session_manager = None
    service.active_journeys = {}
    
    # Execute with client_id in context (not as parameter)
    result = await service.execute_journey(
        journey_id="journey_123",
        user_id="user_123",
        context={"execution_mode": "standard", "client_id": "client_456"},
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is True, "Execution should succeed"
    assert result["execution"]["client_id"] == "client_456", "Client ID should be extracted from context"
    
    logger.info("✅ Test passed: Client ID extraction from context works")

