#!/usr/bin/env python3
"""
Client Collaboration API Endpoints - Unit Tests

FastAPI TestClient tests for API endpoints.
Tests the HTTP layer without requiring full infrastructure.

Validates:
- Endpoint registration
- Request/response handling
- HTTP status codes
- Error handling
- Request validation
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from typing import Dict, Any, Optional

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.unit]


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_client_collaboration_service():
    """Mock ClientCollaborationService."""
    service = AsyncMock()
    service.share_artifact_with_client = AsyncMock(return_value={
        "success": True,
        "artifact_id": "artifact_123",
        "artifact_type": "solution",
        "client_id": "client_456",
        "status": "review",
        "shared_at": "2024-12-16T21:30:00Z"
    })
    service.get_client_artifacts = AsyncMock(return_value={
        "success": True,
        "client_id": "client_456",
        "artifacts": {
            "artifact_123": {
                "artifact_id": "artifact_123",
                "status": "review"
            }
        },
        "count": 1,
        "filters": {"artifact_type": None, "status": None}
    })
    service.add_client_comment = AsyncMock(return_value={
        "success": True,
        "artifact_id": "artifact_123",
        "comment": {
            "comment_id": "comment_789",
            "comment": "Test comment",
            "timestamp": "2024-12-16T21:35:00Z"
        },
        "total_comments": 1
    })
    service.approve_artifact = AsyncMock(return_value={
        "success": True,
        "artifact_id": "artifact_123",
        "artifact_type": "solution",
        "client_id": "client_456",
        "status": "approved",
        "approved_at": "2024-12-16T21:40:00Z"
    })
    service.reject_artifact = AsyncMock(return_value={
        "success": True,
        "artifact_id": "artifact_123",
        "artifact_type": "solution",
        "client_id": "client_456",
        "status": "draft",
        "rejection_reason": "Test rejection",
        "rejected_at": "2024-12-16T21:45:00Z"
    })
    service.health_check = AsyncMock(return_value={
        "status": "healthy",
        "service_name": "ClientCollaborationService",
        "realm": "business_enablement"
    })
    return service


@pytest.fixture
def api_app(mock_client_collaboration_service):
    """Create FastAPI app with client collaboration router."""
    from backend.business_enablement.services.client_collaboration_service.api.client_collaboration_router import (
        router,
        set_client_collaboration_service
    )
    
    app = FastAPI()
    
    # Set the mock service
    set_client_collaboration_service(mock_client_collaboration_service)
    
    # Include router
    app.include_router(router)
    
    return app


@pytest.fixture
def client(api_app):
    """Create TestClient for API testing."""
    return TestClient(api_app)


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

def test_share_artifact_endpoint(client, mock_client_collaboration_service):
    """
    Test share artifact API endpoint.
    
    Validates:
    - Endpoint is accessible
    - Request body is parsed correctly
    - Service method is called
    - Response format is correct
    """
    logger.info("🧪 Test: Share artifact API endpoint...")
    
    response = client.post(
        "/api/v1/client-collaboration/share-artifact",
        json={
            "artifact_id": "artifact_123",
            "artifact_type": "solution",
            "client_id": "client_456"
        },
        headers={
            "X-User-Id": "test_user",
            "X-Tenant-Id": "test_tenant"
        }
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["success"] is True, "Response should indicate success"
    assert data["artifact_id"] == "artifact_123", "Artifact ID should match"
    assert data["status"] == "review", "Status should be 'review'"
    
    # Verify service was called
    mock_client_collaboration_service.share_artifact_with_client.assert_called_once()
    
    logger.info("✅ Test passed: Share artifact endpoint validated")


def test_get_client_artifacts_endpoint(client, mock_client_collaboration_service):
    """
    Test get client artifacts API endpoint.
    
    Validates:
    - Endpoint is accessible
    - Query parameters are parsed correctly
    - Service method is called
    - Response format is correct
    """
    logger.info("🧪 Test: Get client artifacts API endpoint...")
    
    response = client.get(
        "/api/v1/client-collaboration/client/client_456/artifacts?artifact_type=solution&status=review",
        headers={
            "X-User-Id": "test_user",
            "X-Tenant-Id": "test_tenant"
        }
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["success"] is True, "Response should indicate success"
    assert data["client_id"] == "client_456", "Client ID should match"
    assert "artifacts" in data, "Response should contain artifacts"
    assert data["count"] == 1, "Count should match"
    
    # Verify service was called
    mock_client_collaboration_service.get_client_artifacts.assert_called_once()
    
    logger.info("✅ Test passed: Get client artifacts endpoint validated")


def test_add_comment_endpoint(client, mock_client_collaboration_service):
    """
    Test add comment API endpoint.
    
    Validates:
    - Endpoint is accessible
    - Request body is parsed correctly
    - Service method is called
    - Response format is correct
    """
    logger.info("🧪 Test: Add comment API endpoint...")
    
    response = client.post(
        "/api/v1/client-collaboration/artifacts/artifact_123/comments",
        json={
            "comment": "Test comment",
            "section": "test_section",
            "artifact_type": "solution",
            "client_id": "client_456"
        },
        headers={
            "X-User-Id": "test_user",
            "X-Tenant-Id": "test_tenant"
        }
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["success"] is True, "Response should indicate success"
    assert "comment" in data, "Response should contain comment"
    assert data["total_comments"] == 1, "Total comments should match"
    
    # Verify service was called
    mock_client_collaboration_service.add_client_comment.assert_called_once()
    
    logger.info("✅ Test passed: Add comment endpoint validated")


def test_approve_artifact_endpoint(client, mock_client_collaboration_service):
    """
    Test approve artifact API endpoint.
    
    Validates:
    - Endpoint is accessible
    - Request body is parsed correctly
    - Service method is called
    - Response format is correct
    """
    logger.info("🧪 Test: Approve artifact API endpoint...")
    
    response = client.post(
        "/api/v1/client-collaboration/artifacts/artifact_123/approve",
        json={
            "client_id": "client_456",
            "artifact_type": "solution"
        },
        headers={
            "X-User-Id": "test_user",
            "X-Tenant-Id": "test_tenant"
        }
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["success"] is True, "Response should indicate success"
    assert data["status"] == "approved", "Status should be 'approved'"
    assert "approved_at" in data, "Response should contain approved_at"
    
    # Verify service was called
    mock_client_collaboration_service.approve_artifact.assert_called_once()
    
    logger.info("✅ Test passed: Approve artifact endpoint validated")


def test_reject_artifact_endpoint(client, mock_client_collaboration_service):
    """
    Test reject artifact API endpoint.
    
    Validates:
    - Endpoint is accessible
    - Request body is parsed correctly
    - Service method is called
    - Response format is correct
    """
    logger.info("🧪 Test: Reject artifact API endpoint...")
    
    response = client.post(
        "/api/v1/client-collaboration/artifacts/artifact_123/reject",
        json={
            "client_id": "client_456",
            "rejection_reason": "Test rejection reason",
            "artifact_type": "solution"
        },
        headers={
            "X-User-Id": "test_user",
            "X-Tenant-Id": "test_tenant"
        }
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["success"] is True, "Response should indicate success"
    assert data["status"] == "draft", "Status should be 'draft'"
    assert "rejection_reason" in data, "Response should contain rejection_reason"
    
    # Verify service was called
    mock_client_collaboration_service.reject_artifact.assert_called_once()
    
    logger.info("✅ Test passed: Reject artifact endpoint validated")


def test_health_check_endpoint(client, mock_client_collaboration_service):
    """
    Test health check API endpoint.
    
    Validates:
    - Endpoint is accessible
    - Response format is correct
    """
    logger.info("🧪 Test: Health check API endpoint...")
    
    response = client.get("/api/v1/client-collaboration/health")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "status" in data, "Response should contain status"
    assert "service_name" in data, "Response should contain service_name"
    
    logger.info("✅ Test passed: Health check endpoint validated")


def test_share_artifact_validation_error(client):
    """
    Test share artifact endpoint with invalid request.
    
    Validates:
    - Request validation works
    - Returns 422 for invalid request
    """
    logger.info("🧪 Test: Share artifact validation error...")
    
    # Missing required fields
    response = client.post(
        "/api/v1/client-collaboration/share-artifact",
        json={
            "artifact_id": "artifact_123"
            # Missing artifact_type and client_id
        }
    )
    
    assert response.status_code == 422, f"Expected 422 for validation error, got {response.status_code}"
    
    logger.info("✅ Test passed: Request validation works")


def test_get_client_artifacts_with_filters(client, mock_client_collaboration_service):
    """
    Test get client artifacts with query parameter filters.
    
    Validates:
    - Query parameters are parsed correctly
    - Filters are passed to service
    """
    logger.info("🧪 Test: Get client artifacts with filters...")
    
    response = client.get(
        "/api/v1/client-collaboration/client/client_456/artifacts?artifact_type=journey&status=approved"
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    # Verify service was called with correct filters
    call_args = mock_client_collaboration_service.get_client_artifacts.call_args
    assert call_args[1]["artifact_type"] == "journey", "Artifact type filter should be passed"
    assert call_args[1]["status"] == "approved", "Status filter should be passed"
    
    logger.info("✅ Test passed: Query parameter filters validated")


def test_error_handling_service_unavailable():
    """
    Test error handling when service is unavailable.
    
    Validates:
    - Returns 503 when service is not available
    """
    logger.info("🧪 Test: Service unavailable error handling...")
    
    # Create app without service
    from backend.business_enablement.services.client_collaboration_service.api.client_collaboration_router import (
        router,
        set_client_collaboration_service
    )
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    # Explicitly set service to None to test unavailable behavior
    set_client_collaboration_service(None)
    
    test_client = TestClient(app)
    
    response = test_client.post(
        "/api/v1/client-collaboration/share-artifact",
        json={
            "artifact_id": "artifact_123",
            "artifact_type": "solution",
            "client_id": "client_456"
        }
    )
    
    assert response.status_code == 503, f"Expected 503 for service unavailable, got {response.status_code}: {response.text}"
    
    logger.info("✅ Test passed: Service unavailable error handling validated")

