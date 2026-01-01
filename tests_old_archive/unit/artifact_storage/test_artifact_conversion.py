#!/usr/bin/env python3
"""
Artifact Conversion Tests

Unit tests for artifact → solution/journey conversion.

Validates:
- create_solution_from_artifact() method
- create_journey_from_artifact() method
- Status validation
- Client ID validation
- Artifact linking
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
    
    # Mock artifact methods
    service.get_solution_artifact = AsyncMock()
    service.update_solution_artifact_status = AsyncMock()
    service.design_solution = AsyncMock()
    service.store_document = AsyncMock()
    
    # Mock base class methods
    service.get_security = Mock(return_value=Mock(check_permissions=AsyncMock(return_value=True)))
    service.get_tenant = Mock(return_value=None)
    service.handle_error_with_audit = AsyncMock()
    service.record_health_metric = AsyncMock()
    service.log_operation_with_telemetry = AsyncMock()
    service.logger = Mock()
    
    # Mock DI container
    service.di_container = Mock()
    service.di_container.get_foundation_service = Mock(return_value=None)
    
    return service


@pytest.fixture
def mock_journey_orchestrator():
    """Mock StructuredJourneyOrchestratorService."""
    service = AsyncMock()
    
    # Mock artifact methods
    service.get_journey_artifact = AsyncMock()
    service.update_journey_artifact_status = AsyncMock()
    service.design_journey = AsyncMock()
    service.store_document = AsyncMock()
    
    # Mock base class methods
    service.get_security = Mock(return_value=Mock(check_permissions=AsyncMock(return_value=True)))
    service.get_tenant = Mock(return_value=Mock(validate_tenant_access=AsyncMock(return_value=True)))
    service.handle_error_with_audit = AsyncMock()
    service.record_health_metric = AsyncMock()
    service.log_operation_with_telemetry = AsyncMock()
    service.logger = Mock()
    
    # Mock DI container
    service.di_container = Mock()
    service.di_container.get_foundation_service = Mock(return_value=None)
    
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
def approved_solution_artifact():
    """Approved solution artifact for testing."""
    return {
        "artifact_id": "artifact_123",
        "artifact_type": "roadmap",
        "client_id": "client_456",
        "status": "approved",
        "data": {
            "requirements": {
                "phases": ["phase1", "phase2"],
                "timeline": "6 months"
            }
        },
        "version": 1
    }


@pytest.fixture
def approved_journey_artifact():
    """Approved journey artifact for testing."""
    return {
        "artifact_id": "artifact_789",
        "artifact_type": "workflow",
        "client_id": "client_456",
        "status": "approved",
        "data": {
            "requirements": {
                "steps": ["step1", "step2"],
                "milestones": ["milestone1"]
            }
        },
        "version": 1
    }


# ============================================================================
# SOLUTION CONVERSION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_solution_from_artifact_success(
    mock_solution_composer,
    approved_solution_artifact,
    test_user_context
):
    """
    Test successful solution creation from approved artifact.
    
    Validates:
    - Artifact retrieval
    - Client ID validation
    - Status validation
    - Solution creation
    - Artifact status update
    - Artifact linking
    """
    logger.info("🧪 Test: Create solution from artifact (success)...")
    
    # Setup mocks
    mock_solution_composer.get_solution_artifact.return_value = {
        "success": True,
        "artifact": approved_solution_artifact
    }
    
    mock_solution_composer.design_solution.return_value = {
        "success": True,
        "solution": {
            "solution_id": "solution_123",
            "solution_type": "roadmap",
            "status": "designed"
        }
    }
    
    mock_solution_composer.update_solution_artifact_status.return_value = {
        "success": True,
        "artifact": {**approved_solution_artifact, "status": "implemented"}
    }
    
    # Get updated artifact (after status update)
    updated_artifact = {**approved_solution_artifact, "status": "implemented", "solution_id": "solution_123"}
    mock_solution_composer.get_solution_artifact.side_effect = [
        {"success": True, "artifact": approved_solution_artifact},  # First call (initial get)
        {"success": True, "artifact": updated_artifact}  # Second call (after status update)
    ]
    
    # Import and patch the method
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    
    # Create instance and patch methods
    service = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    # Patch methods
    service.get_solution_artifact = mock_solution_composer.get_solution_artifact
    service.update_solution_artifact_status = mock_solution_composer.update_solution_artifact_status
    service.design_solution = mock_solution_composer.design_solution
    service.store_document = mock_solution_composer.store_document
    service.get_security = mock_solution_composer.get_security
    service.get_tenant = mock_solution_composer.get_tenant
    service.handle_error_with_audit = mock_solution_composer.handle_error_with_audit
    service.record_health_metric = mock_solution_composer.record_health_metric
    service.log_operation_with_telemetry = mock_solution_composer.log_operation_with_telemetry
    service.logger = mock_solution_composer.logger
    service.di_container = mock_solution_composer.di_container
    service.solution_templates = {"mvp_solution": {"template_name": "MVP Solution"}}
    
    # Execute
    result = await service.create_solution_from_artifact(
        artifact_id="artifact_123",
        client_id="client_456",
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is True, "Conversion should succeed"
    assert result["solution_id"] == "solution_123", "Solution ID should match"
    assert result["artifact_id"] == "artifact_123", "Artifact ID should match"
    assert result["status"] == "implemented", "Status should be 'implemented'"
    
    # Verify method calls
    mock_solution_composer.get_solution_artifact.assert_called()
    mock_solution_composer.design_solution.assert_called_once()
    mock_solution_composer.update_solution_artifact_status.assert_called_once_with(
        artifact_id="artifact_123",
        new_status="implemented",
        user_context=test_user_context
    )
    
    logger.info("✅ Test passed: Solution conversion validated")


@pytest.mark.asyncio
async def test_create_solution_from_artifact_wrong_status(
    mock_solution_composer,
    approved_solution_artifact,
    test_user_context
):
    """
    Test solution creation fails when artifact is not approved.
    
    Validates:
    - Status validation prevents conversion
    """
    logger.info("🧪 Test: Create solution from artifact (wrong status)...")
    
    # Setup artifact with wrong status
    draft_artifact = {**approved_solution_artifact, "status": "draft"}
    mock_solution_composer.get_solution_artifact.return_value = {
        "success": True,
        "artifact": draft_artifact
    }
    
    # Import and patch
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    
    service = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    service.get_solution_artifact = mock_solution_composer.get_solution_artifact
    service.get_security = mock_solution_composer.get_security
    service.get_tenant = mock_solution_composer.get_tenant
    service.handle_error_with_audit = mock_solution_composer.handle_error_with_audit
    service.record_health_metric = mock_solution_composer.record_health_metric
    service.log_operation_with_telemetry = mock_solution_composer.log_operation_with_telemetry
    service.logger = mock_solution_composer.logger
    
    # Execute
    result = await service.create_solution_from_artifact(
        artifact_id="artifact_123",
        client_id="client_456",
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is False, "Conversion should fail"
    assert "approved" in result["error"].lower(), "Error should mention approval requirement"
    
    # Verify design_solution was NOT called
    mock_solution_composer.design_solution.assert_not_called()
    
    logger.info("✅ Test passed: Status validation works")


@pytest.mark.asyncio
async def test_create_solution_from_artifact_client_id_mismatch(
    mock_solution_composer,
    approved_solution_artifact,
    test_user_context
):
    """
    Test solution creation fails when client_id doesn't match.
    
    Validates:
    - Client ID validation prevents unauthorized conversion
    """
    logger.info("🧪 Test: Create solution from artifact (client_id mismatch)...")
    
    mock_solution_composer.get_solution_artifact.return_value = {
        "success": True,
        "artifact": approved_solution_artifact
    }
    
    # Import and patch
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    
    service = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    service.get_solution_artifact = mock_solution_composer.get_solution_artifact
    service.get_security = mock_solution_composer.get_security
    service.get_tenant = mock_solution_composer.get_tenant
    service.handle_error_with_audit = mock_solution_composer.handle_error_with_audit
    service.record_health_metric = mock_solution_composer.record_health_metric
    service.log_operation_with_telemetry = mock_solution_composer.log_operation_with_telemetry
    service.logger = mock_solution_composer.logger
    
    # Execute with wrong client_id
    result = await service.create_solution_from_artifact(
        artifact_id="artifact_123",
        client_id="wrong_client",
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is False, "Conversion should fail"
    assert "client_id" in result["error"].lower(), "Error should mention client_id mismatch"
    
    # Verify design_solution was NOT called
    mock_solution_composer.design_solution.assert_not_called()
    
    logger.info("✅ Test passed: Client ID validation works")


# ============================================================================
# JOURNEY CONVERSION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_journey_from_artifact_success(
    mock_journey_orchestrator,
    approved_journey_artifact,
    test_user_context
):
    """
    Test successful journey creation from approved artifact.
    
    Validates:
    - Artifact retrieval
    - Client ID validation
    - Status validation
    - Journey creation
    - Artifact status update
    - Artifact linking
    """
    logger.info("🧪 Test: Create journey from artifact (success)...")
    
    # Setup mocks
    mock_journey_orchestrator.get_journey_artifact.return_value = {
        "success": True,
        "artifact": approved_journey_artifact
    }
    
    mock_journey_orchestrator.design_journey.return_value = {
        "success": True,
        "journey": {
            "journey_id": "journey_123",
            "journey_type": "workflow",
            "status": "designed"
        }
    }
    
    mock_journey_orchestrator.update_journey_artifact_status.return_value = {
        "success": True,
        "artifact": {**approved_journey_artifact, "status": "implemented"}
    }
    
    # Get updated artifact (after status update)
    updated_artifact = {**approved_journey_artifact, "status": "implemented", "journey_id": "journey_123"}
    mock_journey_orchestrator.get_journey_artifact.side_effect = [
        {"success": True, "artifact": approved_journey_artifact},  # First call
        {"success": True, "artifact": updated_artifact}  # Second call
    ]
    
    # Import and patch
    from backend.journey.services.structured_journey_orchestrator_service.structured_journey_orchestrator_service import StructuredJourneyOrchestratorService
    
    service = StructuredJourneyOrchestratorService(
        service_name="StructuredJourneyOrchestratorService",
        realm_name="journey",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    # Patch methods
    service.get_journey_artifact = mock_journey_orchestrator.get_journey_artifact
    service.update_journey_artifact_status = mock_journey_orchestrator.update_journey_artifact_status
    service.design_journey = mock_journey_orchestrator.design_journey
    service.store_document = mock_journey_orchestrator.store_document
    service.get_security = mock_journey_orchestrator.get_security
    service.get_tenant = mock_journey_orchestrator.get_tenant
    service.handle_error_with_audit = mock_journey_orchestrator.handle_error_with_audit
    service.record_health_metric = mock_journey_orchestrator.record_health_metric
    service.log_operation_with_telemetry = mock_journey_orchestrator.log_operation_with_telemetry
    service.logger = mock_journey_orchestrator.logger
    service.di_container = mock_journey_orchestrator.di_container
    service.journey_templates = {"workflow": {"template_name": "Workflow"}}
    
    # Execute
    result = await service.create_journey_from_artifact(
        artifact_id="artifact_789",
        client_id="client_456",
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is True, "Conversion should succeed"
    assert result["journey_id"] == "journey_123", "Journey ID should match"
    assert result["artifact_id"] == "artifact_789", "Artifact ID should match"
    assert result["status"] == "implemented", "Status should be 'implemented'"
    
    # Verify method calls
    mock_journey_orchestrator.get_journey_artifact.assert_called()
    mock_journey_orchestrator.design_journey.assert_called_once()
    mock_journey_orchestrator.update_journey_artifact_status.assert_called_once_with(
        artifact_id="artifact_789",
        new_status="implemented",
        user_context=test_user_context
    )
    
    logger.info("✅ Test passed: Journey conversion validated")


@pytest.mark.asyncio
async def test_create_journey_from_artifact_wrong_status(
    mock_journey_orchestrator,
    approved_journey_artifact,
    test_user_context
):
    """
    Test journey creation fails when artifact is not approved.
    
    Validates:
    - Status validation prevents conversion
    """
    logger.info("🧪 Test: Create journey from artifact (wrong status)...")
    
    # Setup artifact with wrong status
    draft_artifact = {**approved_journey_artifact, "status": "draft"}
    mock_journey_orchestrator.get_journey_artifact.return_value = {
        "success": True,
        "artifact": draft_artifact
    }
    
    # Import and patch
    from backend.journey.services.structured_journey_orchestrator_service.structured_journey_orchestrator_service import StructuredJourneyOrchestratorService
    
    service = StructuredJourneyOrchestratorService(
        service_name="StructuredJourneyOrchestratorService",
        realm_name="journey",
        platform_gateway=Mock(),
        di_container=Mock()
    )
    
    service.get_journey_artifact = mock_journey_orchestrator.get_journey_artifact
    service.get_security = mock_journey_orchestrator.get_security
    service.get_tenant = mock_journey_orchestrator.get_tenant
    service.handle_error_with_audit = mock_journey_orchestrator.handle_error_with_audit
    service.record_health_metric = mock_journey_orchestrator.record_health_metric
    service.log_operation_with_telemetry = mock_journey_orchestrator.log_operation_with_telemetry
    service.logger = mock_journey_orchestrator.logger
    
    # Execute
    result = await service.create_journey_from_artifact(
        artifact_id="artifact_789",
        client_id="client_456",
        user_context=test_user_context
    )
    
    # Assertions
    assert result["success"] is False, "Conversion should fail"
    assert "approved" in result["error"].lower(), "Error should mention approval requirement"
    
    # Verify design_journey was NOT called
    mock_journey_orchestrator.design_journey.assert_not_called()
    
    logger.info("✅ Test passed: Status validation works")








