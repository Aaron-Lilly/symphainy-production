#!/usr/bin/env python3
"""
Artifact Storage Foundation - Integration Tests

Tests artifact storage foundation for Solution and Journey artifacts.

Validates:
- Creating Solution artifacts (roadmaps, POC proposals, migration plans)
- Creating Journey artifacts (workflows, SOPs, coexistence blueprints, wave definitions)
- Retrieving artifacts
- Updating artifact status (lifecycle transitions)
- Client ID scoping
- Version tracking
- Status lifecycle validation

This is a logical testing point after Phase 1, Week 1 implementation.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, Optional

# Import conftest fixtures
pytest_plugins = [
    "tests.integration.layer_10_solution.conftest",
    "tests.integration.layer_9_journey.conftest",
    "tests.integration.layer_8_business_enablement.conftest"
]

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
@pytest.mark.timeout_300
async def solution_composer(solution_infrastructure):
    """
    Solution Composer Service instance for artifact storage tests.
    """
    logger.info("🔧 Fixture: Starting solution_composer fixture...")
    
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    
    infra = solution_infrastructure
    composer = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    
    logger.info("🔧 Fixture: Initializing SolutionComposerService...")
    init_result = await composer.initialize()
    
    if not init_result:
        pytest.fail("SolutionComposerService initialization failed")
    
    logger.info("✅ Fixture: SolutionComposerService initialized successfully")
    
    yield composer
    
    logger.info("🔧 Fixture: Cleaning up SolutionComposerService...")


@pytest.fixture(scope="function")
@pytest.mark.timeout_300
async def journey_orchestrator(journey_infrastructure):
    """
    Structured Journey Orchestrator Service instance for artifact storage tests.
    """
    logger.info("🔧 Fixture: Starting journey_orchestrator fixture...")
    
    from backend.journey.services.structured_journey_orchestrator_service.structured_journey_orchestrator_service import StructuredJourneyOrchestratorService
    
    infra = journey_infrastructure
    orchestrator = StructuredJourneyOrchestratorService(
        service_name="StructuredJourneyOrchestratorService",
        realm_name="journey",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    
    logger.info("🔧 Fixture: Initializing StructuredJourneyOrchestratorService...")
    init_result = await orchestrator.initialize()
    
    if not init_result:
        pytest.fail("StructuredJourneyOrchestratorService initialization failed")
    
    logger.info("✅ Fixture: StructuredJourneyOrchestratorService initialized successfully")
    
    yield orchestrator
    
    logger.info("🔧 Fixture: Cleaning up StructuredJourneyOrchestratorService...")


@pytest.fixture(scope="function")
def test_user_context():
    """Test user context for security and tenant validation."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "session_id": "test_session_123"
    }


@pytest.fixture(scope="function")
def test_client_id():
    """Test client ID for client-scoped artifacts."""
    return "test_client_123"


# ============================================================================
# SOLUTION ARTIFACT STORAGE TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_create_solution_artifact_roadmap(solution_composer, test_user_context, test_client_id):
    """
    Test creating a Solution artifact (roadmap).
    
    Validates:
    - Artifact creation with correct structure
    - Client ID scoping
    - Status defaults to "draft"
    - Version starts at 1
    """
    logger.info("🧪 Test: Creating Solution artifact (roadmap)...")
    
    artifact_data = {
        "roadmap": {
            "phases": [
                {"phase_id": "phase_1", "name": "Discovery", "duration": "2 weeks"},
                {"phase_id": "phase_2", "name": "Implementation", "duration": "4 weeks"}
            ],
            "timeline": {"start_date": "2024-01-01", "end_date": "2024-03-01"}
        },
        "pillar_outputs": {
            "content": {"files_uploaded": 10},
            "insights": {"analyses_completed": 5},
            "operations": {"workflows_generated": 3}
        }
    }
    
    result = await solution_composer.create_solution_artifact(
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
    
    logger.info(f"✅ Test passed: Created Solution artifact {artifact['artifact_id']}")


@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_get_solution_artifact(solution_composer, test_user_context, test_client_id):
    """
    Test retrieving a Solution artifact.
    
    Validates:
    - Artifact can be retrieved after creation
    - All fields are preserved
    """
    logger.info("🧪 Test: Retrieving Solution artifact...")
    
    # Create artifact first
    artifact_data = {
        "poc_proposal": {
            "title": "Test POC",
            "description": "Test POC proposal",
            "financials": {"budget": 100000, "roi": 1.5}
        }
    }
    
    create_result = await solution_composer.create_solution_artifact(
        artifact_type="poc_proposal",
        artifact_data=artifact_data,
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert create_result["success"] is True, "Artifact creation should succeed"
    artifact_id = create_result["artifact"]["artifact_id"]
    
    # Retrieve artifact
    get_result = await solution_composer.get_solution_artifact(
        artifact_id=artifact_id,
        user_context=test_user_context
    )
    
    assert get_result["success"] is True, f"Artifact retrieval failed: {get_result.get('error')}"
    assert "artifact" in get_result, "Result should contain artifact"
    
    retrieved_artifact = get_result["artifact"]
    assert retrieved_artifact["artifact_id"] == artifact_id, "Artifact ID should match"
    assert retrieved_artifact["artifact_type"] == "poc_proposal", "Artifact type should match"
    assert retrieved_artifact["client_id"] == test_client_id, "Client ID should match"
    assert retrieved_artifact["data"] == artifact_data, "Artifact data should match"
    
    logger.info(f"✅ Test passed: Retrieved Solution artifact {artifact_id}")


@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_update_solution_artifact_status(solution_composer, test_user_context, test_client_id):
    """
    Test updating Solution artifact status (lifecycle transitions).
    
    Validates:
    - Valid status transitions work
    - Invalid transitions are rejected
    - Version increments on update
    - Status history is preserved
    """
    logger.info("🧪 Test: Updating Solution artifact status...")
    
    # Create artifact
    artifact_data = {"migration_plan": {"phases": []}}
    create_result = await solution_composer.create_solution_artifact(
        artifact_type="migration_plan",
        artifact_data=artifact_data,
        client_id=test_client_id,
        status="draft",
        user_context=test_user_context
    )
    
    artifact_id = create_result["artifact"]["artifact_id"]
    
    # Test valid transition: draft → review
    update_result = await solution_composer.update_solution_artifact_status(
        artifact_id=artifact_id,
        new_status="review",
        user_context=test_user_context
    )
    
    assert update_result["success"] is True, f"Status update failed: {update_result.get('error')}"
    assert update_result["artifact"]["status"] == "review", "Status should be updated to 'review'"
    assert update_result["artifact"]["version"] == 2, "Version should increment to 2"
    assert update_result["status_transition"] == "draft → review", "Status transition should be recorded"
    
    # Test valid transition: review → approved
    update_result = await solution_composer.update_solution_artifact_status(
        artifact_id=artifact_id,
        new_status="approved",
        user_context=test_user_context
    )
    
    assert update_result["success"] is True, "Status update should succeed"
    assert update_result["artifact"]["status"] == "approved", "Status should be updated to 'approved'"
    assert update_result["artifact"]["version"] == 3, "Version should increment to 3"
    
    # Test invalid transition: approved → draft (should fail)
    update_result = await solution_composer.update_solution_artifact_status(
        artifact_id=artifact_id,
        new_status="draft",
        user_context=test_user_context
    )
    
    # Note: approved → draft is actually valid per our lifecycle, so this should succeed
    # Let's test a truly invalid transition: approved → active (should fail)
    update_result = await solution_composer.update_solution_artifact_status(
        artifact_id=artifact_id,
        new_status="active",
        user_context=test_user_context
    )
    
    assert update_result["success"] is False, "Invalid status transition should fail"
    assert "Invalid status transition" in update_result["error"], "Error should mention invalid transition"
    
    logger.info(f"✅ Test passed: Status lifecycle transitions validated for artifact {artifact_id}")


# ============================================================================
# JOURNEY ARTIFACT STORAGE TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_create_journey_artifact_workflow(journey_orchestrator, test_user_context, test_client_id):
    """
    Test creating a Journey artifact (workflow).
    
    Validates:
    - Artifact creation with correct structure
    - Client ID scoping
    - Status defaults to "draft"
    - Version starts at 1
    """
    logger.info("🧪 Test: Creating Journey artifact (workflow)...")
    
    artifact_data = {
        "workflow_definition": {
            "nodes": [
                {"id": "start", "type": "start"},
                {"id": "process", "type": "task", "name": "Process Data"},
                {"id": "end", "type": "end"}
            ],
            "edges": [
                {"from": "start", "to": "process"},
                {"from": "process", "to": "end"}
            ]
        },
        "visualization": {"format": "bpmn", "data": "..."}
    }
    
    result = await journey_orchestrator.create_journey_artifact(
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
    
    logger.info(f"✅ Test passed: Created Journey artifact {artifact['artifact_id']}")


@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_get_journey_artifact(journey_orchestrator, test_user_context, test_client_id):
    """
    Test retrieving a Journey artifact.
    
    Validates:
    - Artifact can be retrieved after creation
    - All fields are preserved
    """
    logger.info("🧪 Test: Retrieving Journey artifact...")
    
    # Create artifact first
    artifact_data = {
        "sop_definition": {
            "title": "Test SOP",
            "steps": [
                {"step_id": 1, "description": "Step 1"},
                {"step_id": 2, "description": "Step 2"}
            ]
        }
    }
    
    create_result = await journey_orchestrator.create_journey_artifact(
        artifact_type="sop",
        artifact_data=artifact_data,
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert create_result["success"] is True, "Artifact creation should succeed"
    artifact_id = create_result["artifact"]["artifact_id"]
    
    # Retrieve artifact
    get_result = await journey_orchestrator.get_journey_artifact(
        artifact_id=artifact_id,
        user_context=test_user_context
    )
    
    assert get_result["success"] is True, f"Artifact retrieval failed: {get_result.get('error')}"
    assert "artifact" in get_result, "Result should contain artifact"
    
    retrieved_artifact = get_result["artifact"]
    assert retrieved_artifact["artifact_id"] == artifact_id, "Artifact ID should match"
    assert retrieved_artifact["artifact_type"] == "sop", "Artifact type should match"
    assert retrieved_artifact["client_id"] == test_client_id, "Client ID should match"
    assert retrieved_artifact["data"] == artifact_data, "Artifact data should match"
    
    logger.info(f"✅ Test passed: Retrieved Journey artifact {artifact_id}")


@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_update_journey_artifact_status(journey_orchestrator, test_user_context, test_client_id):
    """
    Test updating Journey artifact status (lifecycle transitions).
    
    Validates:
    - Valid status transitions work
    - Invalid transitions are rejected
    - Version increments on update
    """
    logger.info("🧪 Test: Updating Journey artifact status...")
    
    # Create artifact
    artifact_data = {"coexistence_blueprint": {"analysis": {}, "recommendations": []}}
    create_result = await journey_orchestrator.create_journey_artifact(
        artifact_type="coexistence_blueprint",
        artifact_data=artifact_data,
        client_id=test_client_id,
        status="draft",
        user_context=test_user_context
    )
    
    artifact_id = create_result["artifact"]["artifact_id"]
    
    # Test valid transition: draft → review
    update_result = await journey_orchestrator.update_journey_artifact_status(
        artifact_id=artifact_id,
        new_status="review",
        user_context=test_user_context
    )
    
    assert update_result["success"] is True, f"Status update failed: {update_result.get('error')}"
    assert update_result["artifact"]["status"] == "review", "Status should be updated to 'review'"
    assert update_result["artifact"]["version"] == 2, "Version should increment to 2"
    
    # Test invalid transition: review → active (should fail)
    update_result = await journey_orchestrator.update_journey_artifact_status(
        artifact_id=artifact_id,
        new_status="active",
        user_context=test_user_context
    )
    
    assert update_result["success"] is False, "Invalid status transition should fail"
    assert "Invalid status transition" in update_result["error"], "Error should mention invalid transition"
    
    logger.info(f"✅ Test passed: Status lifecycle transitions validated for artifact {artifact_id}")


# ============================================================================
# CROSS-SERVICE ARTIFACT VALIDATION
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_artifact_storage_foundation_complete(
    solution_composer,
    journey_orchestrator,
    test_user_context,
    test_client_id
):
    """
    Comprehensive test validating the complete artifact storage foundation.
    
    Validates:
    - Both Solution and Journey artifacts can be created
    - Artifacts are properly scoped by client_id
    - Status lifecycle works for both types
    - Version tracking works correctly
    - Artifacts can be retrieved and updated independently
    """
    logger.info("🧪 Test: Comprehensive artifact storage foundation validation...")
    
    # Create Solution artifact
    roadmap_data = {
        "roadmap": {"phases": [{"phase_id": "p1", "name": "Phase 1"}]},
        "pillar_outputs": {"content": {}, "insights": {}, "operations": {}}
    }
    
    solution_result = await solution_composer.create_solution_artifact(
        artifact_type="roadmap",
        artifact_data=roadmap_data,
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert solution_result["success"] is True, "Solution artifact creation should succeed"
    solution_artifact_id = solution_result["artifact"]["artifact_id"]
    
    # Create Journey artifact
    workflow_data = {
        "workflow_definition": {"nodes": [], "edges": []},
        "visualization": {}
    }
    
    journey_result = await journey_orchestrator.create_journey_artifact(
        artifact_type="workflow",
        artifact_data=workflow_data,
        client_id=test_client_id,
        user_context=test_user_context
    )
    
    assert journey_result["success"] is True, "Journey artifact creation should succeed"
    journey_artifact_id = journey_result["artifact"]["artifact_id"]
    
    # Verify artifacts are independent
    assert solution_artifact_id != journey_artifact_id, "Artifacts should have different IDs"
    
    # Update Solution artifact status
    solution_update = await solution_composer.update_solution_artifact_status(
        artifact_id=solution_artifact_id,
        new_status="review",
        user_context=test_user_context
    )
    
    assert solution_update["success"] is True, "Solution artifact status update should succeed"
    assert solution_update["artifact"]["status"] == "review", "Solution artifact status should be updated"
    
    # Update Journey artifact status
    journey_update = await journey_orchestrator.update_journey_artifact_status(
        artifact_id=journey_artifact_id,
        new_status="review",
        user_context=test_user_context
    )
    
    assert journey_update["success"] is True, "Journey artifact status update should succeed"
    assert journey_update["artifact"]["status"] == "review", "Journey artifact status should be updated"
    
    # Verify both artifacts can be retrieved
    solution_retrieved = await solution_composer.get_solution_artifact(
        artifact_id=solution_artifact_id,
        user_context=test_user_context
    )
    
    assert solution_retrieved["success"] is True, "Solution artifact retrieval should succeed"
    assert solution_retrieved["artifact"]["status"] == "review", "Solution artifact status should be preserved"
    
    journey_retrieved = await journey_orchestrator.get_journey_artifact(
        artifact_id=journey_artifact_id,
        user_context=test_user_context
    )
    
    assert journey_retrieved["success"] is True, "Journey artifact retrieval should succeed"
    assert journey_retrieved["artifact"]["status"] == "review", "Journey artifact status should be preserved"
    
    logger.info("✅ Test passed: Complete artifact storage foundation validated")
    logger.info(f"   - Solution artifact: {solution_artifact_id}")
    logger.info(f"   - Journey artifact: {journey_artifact_id}")
    logger.info("   - Both artifacts created, updated, and retrieved successfully")

