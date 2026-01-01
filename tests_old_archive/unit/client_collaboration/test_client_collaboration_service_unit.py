#!/usr/bin/env python3
"""
Client Collaboration Service - Unit Tests

Unit tests for client collaboration methods that validate the logic without requiring full infrastructure.

Validates:
- Artifact sharing workflow
- Client artifact retrieval
- Comment management
- Approval/rejection workflows
- Status transition validation

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
    container.get_foundation_service = Mock(return_value=None)
    return container


@pytest.fixture
def mock_curator():
    """Mock Curator Foundation Service."""
    curator = AsyncMock()
    curator.artifact_registry = {}
    curator.get_artifact = AsyncMock(return_value=None)
    curator.list_client_artifacts = AsyncMock(return_value={})
    curator.update_artifact = AsyncMock(return_value={"success": True})
    curator.discover_service_by_name = AsyncMock(return_value=None)
    return curator


@pytest.fixture
def mock_solution_composer():
    """Mock SolutionComposerService."""
    composer = AsyncMock()
    composer.update_solution_artifact_status = AsyncMock(return_value={"success": True, "artifact": {}})
    composer.get_solution_artifact = AsyncMock(return_value={"success": True, "artifact": {}})
    composer.store_document = AsyncMock(return_value=None)
    return composer


@pytest.fixture
def mock_journey_orchestrator():
    """Mock StructuredJourneyOrchestratorService."""
    orchestrator = AsyncMock()
    orchestrator.update_journey_artifact_status = AsyncMock(return_value={"success": True, "artifact": {}})
    orchestrator.get_journey_artifact = AsyncMock(return_value={"success": True, "artifact": {}})
    orchestrator.store_document = AsyncMock(return_value=None)
    return orchestrator


@pytest.fixture
def mock_post_office():
    """Mock Post Office service."""
    post_office = AsyncMock()
    post_office.send_notification = AsyncMock(return_value=None)
    return post_office


@pytest.fixture
def client_collaboration_service(mock_platform_gateway, mock_di_container, mock_curator, mock_solution_composer, mock_journey_orchestrator, mock_post_office):
    """Create ClientCollaborationService with mocked dependencies."""
    from backend.business_enablement.services.client_collaboration_service.client_collaboration_service import ClientCollaborationService
    
    service = ClientCollaborationService(
        service_name="ClientCollaborationService",
        realm_name="business_enablement",
        platform_gateway=mock_platform_gateway,
        di_container=mock_di_container
    )
    
    # Mock the dependencies
    service.curator = mock_curator
    service.solution_composer = mock_solution_composer
    service.journey_orchestrator = mock_journey_orchestrator
    service.post_office = mock_post_office
    
    # Mock the base class methods
    service.get_security = Mock(return_value=None)
    service.get_tenant = Mock(return_value=None)
    service.log_operation_with_telemetry = AsyncMock()
    service.handle_error_with_audit = AsyncMock()
    service.record_health_metric = AsyncMock()
    service.logger = logging.getLogger("test")
    service.is_initialized = True
    
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


@pytest.fixture
def test_artifact():
    """Test artifact data."""
    return {
        "artifact_id": "artifact_123",
        "artifact_type": "solution",
        "client_id": "test_client_123",
        "status": "draft",
        "data": {"roadmap": {"phases": []}},
        "version": 1
    }


# ============================================================================
# SHARE ARTIFACT WITH CLIENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_share_artifact_with_client_success(client_collaboration_service, test_user_context, test_client_id, test_artifact, mock_curator, mock_solution_composer):
    """
    Test sharing artifact with client (draft → review).
    
    Validates:
    - Artifact retrieval from Curator
    - Client ID validation
    - Status update to "review"
    - Success response
    """
    logger.info("🧪 Test: Sharing artifact with client...")
    
    # Setup mocks
    mock_curator.get_artifact.return_value = test_artifact
    mock_curator.artifact_registry = {
        "artifact_123": {
            "artifact_type": "solution",
            "client_id": test_client_id
        }
    }
    
    result = await client_collaboration_service.share_artifact_with_client(
        artifact_id="artifact_123",
        artifact_type="solution",
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert result["success"] is True, f"Share artifact failed: {result.get('error')}"
    assert result["status"] == "review", "Status should be 'review'"
    assert result["client_id"] == test_client_id, "Client ID should match"
    
    # Verify status was updated
    mock_solution_composer.update_solution_artifact_status.assert_called_once_with(
        "artifact_123", "review", test_user_context
    )
    
    logger.info("✅ Test passed: Artifact shared with client")


@pytest.mark.asyncio
async def test_share_artifact_with_client_id_mismatch(client_collaboration_service, test_user_context, test_client_id, mock_curator):
    """
    Test sharing artifact with mismatched client_id.
    
    Validates:
    - Client ID validation rejects mismatched IDs
    """
    logger.info("🧪 Test: Sharing artifact with mismatched client_id...")
    
    artifact = {
        "artifact_id": "artifact_123",
        "client_id": "different_client_456",
        "status": "draft"
    }
    
    mock_curator.get_artifact.return_value = artifact
    
    result = await client_collaboration_service.share_artifact_with_client(
        artifact_id="artifact_123",
        artifact_type="solution",
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert result["success"] is False, "Should fail with mismatched client_id"
    assert "client_id" in result["error"].lower(), "Error should mention client_id"
    
    logger.info("✅ Test passed: Client ID mismatch correctly rejected")


# ============================================================================
# GET CLIENT ARTIFACTS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_client_artifacts_success(client_collaboration_service, test_user_context, test_client_id, mock_curator):
    """
    Test getting all artifacts for a client.
    
    Validates:
    - Artifact retrieval from Curator
    - Filtering by artifact_type and status
    - Response format
    """
    logger.info("🧪 Test: Getting client artifacts...")
    
    artifacts = {
        "artifact_1": {"artifact_id": "artifact_1", "status": "review"},
        "artifact_2": {"artifact_id": "artifact_2", "status": "draft"}
    }
    
    mock_curator.list_client_artifacts.return_value = artifacts
    
    result = await client_collaboration_service.get_client_artifacts(
        client_id=test_client_id,
        artifact_type="solution",
        status="review",
        user_context=test_user_context
    )
    
    assert result["success"] is True, f"Get client artifacts failed: {result.get('error')}"
    assert result["client_id"] == test_client_id, "Client ID should match"
    assert "artifacts" in result, "Result should contain artifacts"
    assert result["count"] == len(artifacts), "Count should match"
    
    # Verify Curator was called with correct filters
    mock_curator.list_client_artifacts.assert_called_once_with(
        test_client_id, "solution", "review", test_user_context
    )
    
    logger.info("✅ Test passed: Client artifacts retrieved")


# ============================================================================
# ADD CLIENT COMMENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_add_client_comment_success(client_collaboration_service, test_user_context, test_client_id, test_artifact, mock_curator, mock_solution_composer):
    """
    Test adding comment to artifact.
    
    Validates:
    - Comment is added to artifact
    - Artifact is updated in Curator
    - Comment metadata is tracked
    """
    logger.info("🧪 Test: Adding client comment...")
    
    # Setup mocks
    mock_curator.get_artifact.return_value = test_artifact.copy()
    mock_curator.artifact_registry = {
        "artifact_123": {
            "artifact_type": "solution",
            "client_id": test_client_id
        }
    }
    mock_solution_composer.get_solution_artifact.return_value = {
        "success": True,
        "artifact": test_artifact.copy()
    }
    
    comment = {
        "comment": "This looks good, but we need to adjust Phase 2 timeline",
        "section": "phase_2",
        "user": "client_user"
    }
    
    result = await client_collaboration_service.add_client_comment(
        artifact_id="artifact_123",
        artifact_type="solution",
        comment=comment,
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert result["success"] is True, f"Add comment failed: {result.get('error')}"
    assert "comment" in result, "Result should contain comment"
    assert result["comment"]["comment"] == comment["comment"], "Comment text should match"
    assert "comment_id" in result["comment"], "Comment should have ID"
    assert "timestamp" in result["comment"], "Comment should have timestamp"
    
    # Verify Curator was updated
    mock_curator.update_artifact.assert_called_once()
    
    logger.info("✅ Test passed: Comment added to artifact")


# ============================================================================
# APPROVE ARTIFACT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_approve_artifact_success(client_collaboration_service, test_user_context, test_client_id, mock_curator, mock_solution_composer):
    """
    Test approving artifact (review → approved).
    
    Validates:
    - Status validation (must be "review")
    - Status update to "approved"
    - Success response
    """
    logger.info("🧪 Test: Approving artifact...")
    
    artifact = {
        "artifact_id": "artifact_123",
        "client_id": test_client_id,
        "status": "review",
        "version": 1
    }
    
    mock_curator.get_artifact.return_value = artifact
    mock_solution_composer.update_solution_artifact_status.return_value = {
        "success": True,
        "artifact": {**artifact, "status": "approved"}
    }
    
    result = await client_collaboration_service.approve_artifact(
        artifact_id="artifact_123",
        artifact_type="solution",
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert result["success"] is True, f"Approve artifact failed: {result.get('error')}"
    assert result["status"] == "approved", "Status should be 'approved'"
    assert "approved_at" in result, "Should have approval timestamp"
    
    # Verify status was updated
    mock_solution_composer.update_solution_artifact_status.assert_called_once_with(
        "artifact_123", "approved", test_user_context
    )
    
    logger.info("✅ Test passed: Artifact approved")


@pytest.mark.asyncio
async def test_approve_artifact_wrong_status(client_collaboration_service, test_user_context, test_client_id, mock_curator):
    """
    Test approving artifact that's not in "review" status.
    
    Validates:
    - Status validation rejects non-review artifacts
    """
    logger.info("🧪 Test: Approving artifact with wrong status...")
    
    artifact = {
        "artifact_id": "artifact_123",
        "client_id": test_client_id,
        "status": "draft",  # Not in review
        "version": 1
    }
    
    mock_curator.get_artifact.return_value = artifact
    
    result = await client_collaboration_service.approve_artifact(
        artifact_id="artifact_123",
        artifact_type="solution",
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert result["success"] is False, "Should fail with wrong status"
    assert "review" in result["error"].lower(), "Error should mention review status"
    
    logger.info("✅ Test passed: Wrong status correctly rejected")


# ============================================================================
# REJECT ARTIFACT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_reject_artifact_success(client_collaboration_service, test_user_context, test_client_id, mock_curator, mock_solution_composer):
    """
    Test rejecting artifact (review → draft).
    
    Validates:
    - Rejection comment is added
    - Status is updated to "draft"
    - Rejection reason is tracked
    """
    logger.info("🧪 Test: Rejecting artifact...")
    
    artifact = {
        "artifact_id": "artifact_123",
        "client_id": test_client_id,
        "status": "review",
        "version": 1,
        "comments": []
    }
    
    mock_curator.get_artifact.return_value = artifact.copy()
    mock_curator.artifact_registry = {
        "artifact_123": {
            "artifact_type": "solution",
            "client_id": test_client_id
        }
    }
    mock_solution_composer.get_solution_artifact.return_value = {
        "success": True,
        "artifact": artifact.copy()
    }
    mock_solution_composer.update_solution_artifact_status.return_value = {
        "success": True,
        "artifact": {**artifact, "status": "draft"}
    }
    
    rejection_reason = "Timeline is too aggressive, need more time for Phase 2"
    
    result = await client_collaboration_service.reject_artifact(
        artifact_id="artifact_123",
        artifact_type="solution",
        rejection_reason=rejection_reason,
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert result["success"] is True, f"Reject artifact failed: {result.get('error')}"
    assert result["status"] == "draft", "Status should be 'draft'"
    assert result["rejection_reason"] == rejection_reason, "Rejection reason should match"
    assert "rejected_at" in result, "Should have rejection timestamp"
    
    # Verify status was updated
    mock_solution_composer.update_solution_artifact_status.assert_called_once_with(
        "artifact_123", "draft", test_user_context
    )
    
    logger.info("✅ Test passed: Artifact rejected")


# ============================================================================
# INTEGRATION TESTS (Multiple Operations)
# ============================================================================

@pytest.mark.asyncio
async def test_complete_review_workflow(client_collaboration_service, test_user_context, test_client_id, mock_curator, mock_solution_composer):
    """
    Test complete review workflow: share → comment → approve.
    
    Validates:
    - Complete workflow works end-to-end
    - Status transitions are correct
    """
    logger.info("🧪 Test: Complete review workflow...")
    
    artifact = {
        "artifact_id": "artifact_123",
        "client_id": test_client_id,
        "status": "draft",
        "version": 1,
        "comments": []
    }
    
    # Step 1: Share artifact
    mock_curator.get_artifact.return_value = artifact.copy()
    mock_curator.artifact_registry = {
        "artifact_123": {
            "artifact_type": "solution",
            "client_id": test_client_id
        }
    }
    
    share_result = await client_collaboration_service.share_artifact_with_client(
        artifact_id="artifact_123",
        artifact_type="solution",
        client_id=test_client_id,
        user_context=test_user_context
    )
    assert share_result["success"] is True, "Share should succeed"
    artifact["status"] = "review"
    
    # Step 2: Add comment
    mock_curator.get_artifact.return_value = artifact.copy()
    mock_solution_composer.get_solution_artifact.return_value = {
        "success": True,
        "artifact": artifact.copy()
    }
    
    comment_result = await client_collaboration_service.add_client_comment(
        artifact_id="artifact_123",
        artifact_type="solution",
        comment={"comment": "Looks good!", "section": "overview"},
        client_id=test_client_id,
        user_context=test_user_context
    )
    assert comment_result["success"] is True, "Comment should succeed"
    
    # Step 3: Approve
    mock_curator.get_artifact.return_value = artifact.copy()
    mock_solution_composer.update_solution_artifact_status.return_value = {
        "success": True,
        "artifact": {**artifact, "status": "approved"}
    }
    
    approve_result = await client_collaboration_service.approve_artifact(
        artifact_id="artifact_123",
        artifact_type="solution",
        client_id=test_client_id,
        user_context=test_user_context
    )
    assert approve_result["success"] is True, "Approve should succeed"
    assert approve_result["status"] == "approved", "Status should be approved"
    
    logger.info("✅ Test passed: Complete review workflow validated")


@pytest.mark.asyncio
async def test_journey_artifact_workflow(client_collaboration_service, test_user_context, test_client_id, mock_curator, mock_journey_orchestrator):
    """
    Test workflow with Journey artifacts.
    
    Validates:
    - Journey artifact workflows work correctly
    - Journey orchestrator is used instead of Solution composer
    """
    logger.info("🧪 Test: Journey artifact workflow...")
    
    artifact = {
        "artifact_id": "journey_artifact_123",
        "client_id": test_client_id,
        "status": "review",
        "version": 1
    }
    
    mock_curator.get_artifact.return_value = artifact
    mock_journey_orchestrator.update_journey_artifact_status.return_value = {
        "success": True,
        "artifact": {**artifact, "status": "approved"}
    }
    
    result = await client_collaboration_service.approve_artifact(
        artifact_id="journey_artifact_123",
        artifact_type="journey",
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert result["success"] is True, "Approve should succeed"
    
    # Verify Journey orchestrator was used (not Solution composer)
    mock_journey_orchestrator.update_journey_artifact_status.assert_called_once()
    
    logger.info("✅ Test passed: Journey artifact workflow validated")









