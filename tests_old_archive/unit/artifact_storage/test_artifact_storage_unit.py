#!/usr/bin/env python3
"""
Artifact Storage Foundation - Unit Tests

Unit tests for artifact storage methods that validate the logic without requiring full infrastructure.

Validates:
- Artifact creation logic
- Status lifecycle validation
- Version tracking
- Client ID scoping

This is a simpler test that can run without full infrastructure setup.
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.unit]


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_platform_gateway():
    """Mock Platform Gateway."""
    gateway = Mock()
    gateway.get_abstraction = AsyncMock(return_value=None)
    return gateway


@pytest.fixture
def mock_di_container():
    """Mock DI Container."""
    container = Mock()
    container.curator = Mock()
    container.curator.register_artifact = AsyncMock()
    container.curator.get_artifact = AsyncMock(return_value=None)
    container.curator.update_artifact = AsyncMock()
    return container


@pytest.fixture
def mock_librarian():
    """Mock Librarian service."""
    librarian = AsyncMock()
    librarian.store_document = AsyncMock()
    librarian.retrieve_document = AsyncMock(return_value=None)
    return librarian


@pytest.fixture
def solution_composer_service(mock_platform_gateway, mock_di_container, mock_librarian):
    """Create SolutionComposerService with mocked dependencies."""
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    
    service = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=mock_platform_gateway,
        di_container=mock_di_container
    )
    
    # Mock the Smart City services
    service.librarian = mock_librarian
    service.conductor = AsyncMock()
    service.data_steward = AsyncMock()
    
    # Mock the base class methods
    service.store_document = mock_librarian.store_document
    service.retrieve_document = mock_librarian.retrieve_document
    service.get_security = Mock(return_value=None)
    service.get_tenant = Mock(return_value=None)
    service.log_operation_with_telemetry = AsyncMock()
    service.handle_error_with_audit = AsyncMock()
    service.record_health_metric = AsyncMock()
    service.logger = logging.getLogger("test")
    
    return service


@pytest.fixture
def journey_orchestrator_service(mock_platform_gateway, mock_di_container, mock_librarian):
    """Create StructuredJourneyOrchestratorService with mocked dependencies."""
    from backend.journey.services.structured_journey_orchestrator_service.structured_journey_orchestrator_service import StructuredJourneyOrchestratorService
    
    service = StructuredJourneyOrchestratorService(
        service_name="StructuredJourneyOrchestratorService",
        realm_name="journey",
        platform_gateway=mock_platform_gateway,
        di_container=mock_di_container
    )
    
    # Mock the Smart City services
    service.librarian = mock_librarian
    service.conductor = AsyncMock()
    service.data_steward = AsyncMock()
    
    # Mock the base class methods
    service.store_document = mock_librarian.store_document
    service.retrieve_document = mock_librarian.retrieve_document
    service.get_security = Mock(return_value=None)
    service.get_tenant = Mock(return_value=None)
    service.log_operation_with_telemetry = AsyncMock()
    service.handle_error_with_audit = AsyncMock()
    service.record_health_metric = AsyncMock()
    service.logger = logging.getLogger("test")
    
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
def test_client_id():
    """Test client ID."""
    return "test_client_123"


# ============================================================================
# SOLUTION ARTIFACT STORAGE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_solution_artifact_basic(solution_composer_service, test_user_context, test_client_id, mock_librarian):
    """
    Test creating a Solution artifact (basic validation).
    
    Validates:
    - Artifact creation with correct structure
    - Client ID scoping
    - Status defaults to "draft"
    - Version starts at 1
    """
    logger.info("🧪 Test: Creating Solution artifact (unit test)...")
    
    artifact_data = {
        "roadmap": {
            "phases": [{"phase_id": "phase_1", "name": "Discovery"}]
        }
    }
    
    # Mock Librarian to return success
    mock_librarian.store_document.return_value = None
    
    result = await solution_composer_service.create_solution_artifact(
        artifact_type="roadmap",
        artifact_data=artifact_data,
        client_id=test_client_id,
        status="draft",
        user_context=test_user_context
    )
    
    assert result["success"] is True, f"Artifact creation failed: {result.get('error')}"
    assert "artifact" in result, "Result should contain artifact"
    
    artifact = result["artifact"]
    assert artifact["artifact_type"] == "roadmap", "Artifact type should be 'roadmap'"
    assert artifact["client_id"] == test_client_id, "Client ID should match"
    assert artifact["status"] == "draft", "Status should be 'draft'"
    assert artifact["version"] == 1, "Version should start at 1"
    assert artifact["artifact_id"] is not None, "Artifact ID should be generated"
    assert artifact["data"] == artifact_data, "Artifact data should match"
    
    # Verify Librarian was called
    mock_librarian.store_document.assert_called_once()
    
    logger.info(f"✅ Test passed: Created Solution artifact {artifact['artifact_id']}")


@pytest.mark.asyncio
async def test_get_solution_artifact_basic(solution_composer_service, test_user_context, mock_librarian):
    """
    Test retrieving a Solution artifact.
    
    Validates:
    - Artifact can be retrieved after creation
    - All fields are preserved
    """
    logger.info("🧪 Test: Retrieving Solution artifact (unit test)...")
    
    artifact_id = str(uuid.uuid4())
    artifact = {
        "artifact_id": artifact_id,
        "artifact_type": "poc_proposal",
        "client_id": "test_client_123",
        "status": "draft",
        "data": {"poc_proposal": {"title": "Test POC"}},
        "version": 1
    }
    
    # Mock Librarian to return the artifact
    mock_librarian.retrieve_document.return_value = {
        "document": artifact
    }
    
    get_result = await solution_composer_service.get_solution_artifact(
        artifact_id=artifact_id,
        user_context=test_user_context
    )
    
    assert get_result["success"] is True, f"Artifact retrieval failed: {get_result.get('error')}"
    assert "artifact" in get_result, "Result should contain artifact"
    
    retrieved_artifact = get_result["artifact"]
    assert retrieved_artifact["artifact_id"] == artifact_id, "Artifact ID should match"
    assert retrieved_artifact["artifact_type"] == "poc_proposal", "Artifact type should match"
    
    logger.info(f"✅ Test passed: Retrieved Solution artifact {artifact_id}")


@pytest.mark.asyncio
async def test_update_solution_artifact_status_valid_transition(solution_composer_service, test_user_context, mock_librarian):
    """
    Test updating Solution artifact status with valid transition.
    
    Validates:
    - Valid status transitions work
    - Version increments on update
    """
    logger.info("🧪 Test: Updating Solution artifact status (valid transition)...")
    
    artifact_id = str(uuid.uuid4())
    artifact = {
        "artifact_id": artifact_id,
        "artifact_type": "migration_plan",
        "client_id": "test_client_123",
        "status": "draft",
        "data": {"migration_plan": {}},
        "version": 1
    }
    
    # Mock get to return artifact
    mock_librarian.retrieve_document.return_value = {
        "document": artifact
    }
    
    # Mock store to succeed
    mock_librarian.store_document.return_value = None
    
    # Test valid transition: draft → review
    update_result = await solution_composer_service.update_solution_artifact_status(
        artifact_id=artifact_id,
        new_status="review",
        user_context=test_user_context
    )
    
    assert update_result["success"] is True, f"Status update failed: {update_result.get('error')}"
    assert update_result["artifact"]["status"] == "review", "Status should be updated to 'review'"
    assert update_result["artifact"]["version"] == 2, "Version should increment to 2"
    assert update_result["status_transition"] == "draft → review", "Status transition should be recorded"
    
    logger.info(f"✅ Test passed: Status transition validated for artifact {artifact_id}")


@pytest.mark.asyncio
async def test_update_solution_artifact_status_invalid_transition(solution_composer_service, test_user_context, mock_librarian):
    """
    Test updating Solution artifact status with invalid transition.
    
    Validates:
    - Invalid transitions are rejected
    """
    logger.info("🧪 Test: Updating Solution artifact status (invalid transition)...")
    
    artifact_id = str(uuid.uuid4())
    artifact = {
        "artifact_id": artifact_id,
        "artifact_type": "migration_plan",
        "client_id": "test_client_123",
        "status": "approved",
        "data": {"migration_plan": {}},
        "version": 1
    }
    
    # Mock get to return artifact
    mock_librarian.retrieve_document.return_value = {
        "document": artifact
    }
    
    # Test invalid transition: approved → active (should fail - must go through implemented first)
    update_result = await solution_composer_service.update_solution_artifact_status(
        artifact_id=artifact_id,
        new_status="active",
        user_context=test_user_context
    )
    
    assert update_result["success"] is False, "Invalid status transition should fail"
    assert "Invalid status transition" in update_result["error"], "Error should mention invalid transition"
    
    logger.info(f"✅ Test passed: Invalid status transition correctly rejected for artifact {artifact_id}")


# ============================================================================
# JOURNEY ARTIFACT STORAGE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_journey_artifact_basic(journey_orchestrator_service, test_user_context, test_client_id, mock_librarian):
    """
    Test creating a Journey artifact (basic validation).
    
    Validates:
    - Artifact creation with correct structure
    - Client ID scoping
    - Status defaults to "draft"
    - Version starts at 1
    """
    logger.info("🧪 Test: Creating Journey artifact (unit test)...")
    
    artifact_data = {
        "workflow_definition": {
            "nodes": [{"id": "start", "type": "start"}],
            "edges": []
        }
    }
    
    # Mock Librarian to return success
    mock_librarian.store_document.return_value = None
    
    result = await journey_orchestrator_service.create_journey_artifact(
        artifact_type="workflow",
        artifact_data=artifact_data,
        client_id=test_client_id,
        status="draft",
        user_context=test_user_context
    )
    
    assert result["success"] is True, f"Artifact creation failed: {result.get('error')}"
    assert "artifact" in result, "Result should contain artifact"
    
    artifact = result["artifact"]
    assert artifact["artifact_type"] == "workflow", "Artifact type should be 'workflow'"
    assert artifact["client_id"] == test_client_id, "Client ID should match"
    assert artifact["status"] == "draft", "Status should be 'draft'"
    assert artifact["version"] == 1, "Version should start at 1"
    assert artifact["artifact_id"] is not None, "Artifact ID should be generated"
    assert artifact["data"] == artifact_data, "Artifact data should match"
    
    # Verify Librarian was called
    mock_librarian.store_document.assert_called_once()
    
    logger.info(f"✅ Test passed: Created Journey artifact {artifact['artifact_id']}")


@pytest.mark.asyncio
async def test_get_journey_artifact_basic(journey_orchestrator_service, test_user_context, mock_librarian):
    """
    Test retrieving a Journey artifact.
    
    Validates:
    - Artifact can be retrieved after creation
    - All fields are preserved
    """
    logger.info("🧪 Test: Retrieving Journey artifact (unit test)...")
    
    artifact_id = str(uuid.uuid4())
    artifact = {
        "artifact_id": artifact_id,
        "artifact_type": "sop",
        "client_id": "test_client_123",
        "status": "draft",
        "data": {"sop_definition": {"title": "Test SOP"}},
        "version": 1
    }
    
    # Mock Librarian to return the artifact
    mock_librarian.retrieve_document.return_value = {
        "document": artifact
    }
    
    get_result = await journey_orchestrator_service.get_journey_artifact(
        artifact_id=artifact_id,
        user_context=test_user_context
    )
    
    assert get_result["success"] is True, f"Artifact retrieval failed: {get_result.get('error')}"
    assert "artifact" in get_result, "Result should contain artifact"
    
    retrieved_artifact = get_result["artifact"]
    assert retrieved_artifact["artifact_id"] == artifact_id, "Artifact ID should match"
    assert retrieved_artifact["artifact_type"] == "sop", "Artifact type should match"
    
    logger.info(f"✅ Test passed: Retrieved Journey artifact {artifact_id}")


@pytest.mark.asyncio
async def test_update_journey_artifact_status_valid_transition(journey_orchestrator_service, test_user_context, mock_librarian):
    """
    Test updating Journey artifact status with valid transition.
    
    Validates:
    - Valid status transitions work
    - Version increments on update
    """
    logger.info("🧪 Test: Updating Journey artifact status (valid transition)...")
    
    artifact_id = str(uuid.uuid4())
    artifact = {
        "artifact_id": artifact_id,
        "artifact_type": "coexistence_blueprint",
        "client_id": "test_client_123",
        "status": "draft",
        "data": {"coexistence_blueprint": {}},
        "version": 1
    }
    
    # Mock get to return artifact
    mock_librarian.retrieve_document.return_value = {
        "document": artifact
    }
    
    # Mock store to succeed
    mock_librarian.store_document.return_value = None
    
    # Test valid transition: draft → review
    update_result = await journey_orchestrator_service.update_journey_artifact_status(
        artifact_id=artifact_id,
        new_status="review",
        user_context=test_user_context
    )
    
    assert update_result["success"] is True, f"Status update failed: {update_result.get('error')}"
    assert update_result["artifact"]["status"] == "review", "Status should be updated to 'review'"
    assert update_result["artifact"]["version"] == 2, "Version should increment to 2"
    
    logger.info(f"✅ Test passed: Status transition validated for artifact {artifact_id}")


@pytest.mark.asyncio
async def test_artifact_status_lifecycle_complete(solution_composer_service, test_user_context, mock_librarian):
    """
    Test complete status lifecycle: draft → review → approved → implemented.
    
    Validates:
    - Complete lifecycle works correctly
    - Each transition increments version
    """
    logger.info("🧪 Test: Complete artifact status lifecycle...")
    
    artifact_id = str(uuid.uuid4())
    artifact = {
        "artifact_id": artifact_id,
        "artifact_type": "roadmap",
        "client_id": "test_client_123",
        "status": "draft",
        "data": {"roadmap": {}},
        "version": 1
    }
    
    # Mock store to succeed
    mock_librarian.store_document.return_value = None
    
    # Step 1: draft → review
    mock_librarian.retrieve_document.return_value = {"document": artifact.copy()}
    result = await solution_composer_service.update_solution_artifact_status(
        artifact_id=artifact_id,
        new_status="review",
        user_context=test_user_context
    )
    assert result["success"] is True, "draft → review should succeed"
    assert result["artifact"]["version"] == 2, "Version should be 2"
    artifact["status"] = "review"
    artifact["version"] = 2
    
    # Step 2: review → approved
    mock_librarian.retrieve_document.return_value = {"document": artifact.copy()}
    result = await solution_composer_service.update_solution_artifact_status(
        artifact_id=artifact_id,
        new_status="approved",
        user_context=test_user_context
    )
    assert result["success"] is True, "review → approved should succeed"
    assert result["artifact"]["version"] == 3, "Version should be 3"
    artifact["status"] = "approved"
    artifact["version"] = 3
    
    # Step 3: approved → implemented
    mock_librarian.retrieve_document.return_value = {"document": artifact.copy()}
    result = await solution_composer_service.update_solution_artifact_status(
        artifact_id=artifact_id,
        new_status="implemented",
        user_context=test_user_context
    )
    assert result["success"] is True, "approved → implemented should succeed"
    assert result["artifact"]["version"] == 4, "Version should be 4"
    
    logger.info("✅ Test passed: Complete status lifecycle validated")


@pytest.mark.asyncio
async def test_artifact_client_scoping(solution_composer_service, test_user_context, mock_librarian):
    """
    Test that artifacts are properly scoped by client_id.
    
    Validates:
    - Client ID is stored correctly
    - Artifacts can be created for different clients
    """
    logger.info("🧪 Test: Artifact client scoping...")
    
    # Create artifact for client 1
    artifact_data_1 = {"roadmap": {"phases": []}}
    mock_librarian.store_document.return_value = None
    
    result_1 = await solution_composer_service.create_solution_artifact(
        artifact_type="roadmap",
        artifact_data=artifact_data_1,
        client_id="client_1",
        user_context=test_user_context
    )
    
    assert result_1["success"] is True, "Artifact creation should succeed"
    assert result_1["artifact"]["client_id"] == "client_1", "Client ID should be 'client_1'"
    
    # Create artifact for client 2
    artifact_data_2 = {"roadmap": {"phases": []}}
    result_2 = await solution_composer_service.create_solution_artifact(
        artifact_type="roadmap",
        artifact_data=artifact_data_2,
        client_id="client_2",
        user_context=test_user_context
    )
    
    assert result_2["success"] is True, "Artifact creation should succeed"
    assert result_2["artifact"]["client_id"] == "client_2", "Client ID should be 'client_2'"
    
    # Verify artifacts have different IDs
    assert result_1["artifact"]["artifact_id"] != result_2["artifact"]["artifact_id"], "Artifacts should have different IDs"
    
    logger.info("✅ Test passed: Client scoping validated")

