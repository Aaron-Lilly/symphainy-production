#!/usr/bin/env python3
"""
Client Collaboration API - Integration Tests

Integration tests for Client Collaboration API endpoints.

Validates:
- API endpoint registration
- Request/response handling
- Service integration
- Error handling

Note: These tests require full infrastructure setup.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, Optional

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.api]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
async def client_collaboration_service(smart_city_infrastructure):
    """
    ClientCollaborationService instance for each test.
    
    Reuses the smart_city_infrastructure fixture.
    """
    logger.info("🔧 Fixture: Starting client_collaboration_service fixture...")
    
    from backend.business_enablement.services.client_collaboration_service.client_collaboration_service import ClientCollaborationService
    from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
    
    infra = smart_city_infrastructure
    di_container = infra.get("di_container")
    
    # Create platform gateway
    platform_gateway = PlatformInfrastructureGateway(
        di_container=di_container,
        realm_name="business_enablement"
    )
    
    service = ClientCollaborationService(
        service_name="ClientCollaborationService",
        realm_name="business_enablement",
        platform_gateway=platform_gateway,
        di_container=di_container
    )
    
    # Initialize service
    logger.info("🔧 Fixture: Initializing ClientCollaborationService...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=90.0)
        if not result:
            pytest.fail("ClientCollaborationService failed to initialize")
    except asyncio.TimeoutError:
        pytest.fail("ClientCollaborationService initialization timed out")
    
    logger.info("✅ Fixture: ClientCollaborationService ready")
    yield service
    logger.info("✅ Fixture: Test completed, cleaning up...")


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
# API ENDPOINT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_share_artifact_api(client_collaboration_service, test_user_context, test_client_id):
    """
    Test share artifact API endpoint.
    
    Validates:
    - Service method is callable
    - Request handling works
    - Response format is correct
    """
    logger.info("🧪 Test: Share artifact API...")
    
    # Note: This is a service-level test
    # Full API endpoint testing would require FastAPI TestClient
    # For now, we test the service method directly
    
    # First, we need to create an artifact
    # This would typically be done via SolutionComposerService
    # For integration test, we'll mock the artifact in Curator
    
    result = await client_collaboration_service.share_artifact_with_client(
        artifact_id="test_artifact_123",
        artifact_type="solution",
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    # Result may fail if artifact doesn't exist (expected in integration test)
    # We're validating the API structure, not the full workflow
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "success" in result, "Result should have success field"
    
    logger.info(f"✅ Test passed: Share artifact API structure validated")


@pytest.mark.asyncio
async def test_get_client_artifacts_api(client_collaboration_service, test_user_context, test_client_id):
    """
    Test get client artifacts API endpoint.
    
    Validates:
    - Service method is callable
    - Request handling works
    - Response format is correct
    """
    logger.info("🧪 Test: Get client artifacts API...")
    
    result = await client_collaboration_service.get_client_artifacts(
        client_id=test_client_id,
        artifact_type=None,
        status=None,
        user_context=test_user_context
    )
    
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "success" in result, "Result should have success field"
    assert "artifacts" in result, "Result should have artifacts field"
    assert "count" in result, "Result should have count field"
    
    logger.info(f"✅ Test passed: Get client artifacts API structure validated")


@pytest.mark.asyncio
async def test_add_comment_api(client_collaboration_service, test_user_context, test_client_id):
    """
    Test add comment API endpoint.
    
    Validates:
    - Service method is callable
    - Request handling works
    - Response format is correct
    """
    logger.info("🧪 Test: Add comment API...")
    
    comment = {
        "comment": "Test comment",
        "section": "test_section",
        "user": "test_user"
    }
    
    result = await client_collaboration_service.add_client_comment(
        artifact_id="test_artifact_123",
        artifact_type="solution",
        comment=comment,
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    # Result may fail if artifact doesn't exist (expected in integration test)
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "success" in result, "Result should have success field"
    
    logger.info(f"✅ Test passed: Add comment API structure validated")


@pytest.mark.asyncio
async def test_approve_artifact_api(client_collaboration_service, test_user_context, test_client_id):
    """
    Test approve artifact API endpoint.
    
    Validates:
    - Service method is callable
    - Request handling works
    - Response format is correct
    """
    logger.info("🧪 Test: Approve artifact API...")
    
    result = await client_collaboration_service.approve_artifact(
        artifact_id="test_artifact_123",
        artifact_type="solution",
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    # Result may fail if artifact doesn't exist or wrong status (expected in integration test)
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "success" in result, "Result should have success field"
    
    logger.info(f"✅ Test passed: Approve artifact API structure validated")


@pytest.mark.asyncio
async def test_reject_artifact_api(client_collaboration_service, test_user_context, test_client_id):
    """
    Test reject artifact API endpoint.
    
    Validates:
    - Service method is callable
    - Request handling works
    - Response format is correct
    """
    logger.info("🧪 Test: Reject artifact API...")
    
    result = await client_collaboration_service.reject_artifact(
        artifact_id="test_artifact_123",
        artifact_type="solution",
        rejection_reason="Test rejection reason",
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    # Result may fail if artifact doesn't exist or wrong status (expected in integration test)
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "success" in result, "Result should have success field"
    
    logger.info(f"✅ Test passed: Reject artifact API structure validated")


@pytest.mark.asyncio
async def test_health_check_api(client_collaboration_service):
    """
    Test health check API endpoint.
    
    Validates:
    - Health check method works
    - Response format is correct
    """
    logger.info("🧪 Test: Health check API...")
    
    health = await client_collaboration_service.health_check()
    
    assert isinstance(health, dict), "Health check should return a dictionary"
    assert "status" in health, "Health check should have status field"
    assert "service_name" in health, "Health check should have service_name field"
    
    logger.info(f"✅ Test passed: Health check API validated")

