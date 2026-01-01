#!/usr/bin/env python3
"""
Realm Service Test Fixtures

Provides fixtures for Experience, Journey, and Solution realm services.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any, Optional


# ============================================================================
# EXPERIENCE REALM FIXTURES
# ============================================================================

@pytest.fixture
def mock_session_manager_service(mock_di_container, mock_platform_gateway):
    """Create a mock Session Manager Service for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "SessionManagerService"
    mock_service.realm_name = "experience"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.create_session = AsyncMock(return_value={"session_id": "test_session"})
    mock_service.get_session = AsyncMock(return_value={"session_id": "test_session", "data": {}})
    mock_service.update_session = AsyncMock(return_value=True)
    mock_service.delete_session = AsyncMock(return_value=True)
    
    return mock_service

@pytest.fixture
def mock_user_experience_service(mock_di_container, mock_platform_gateway):
    """Create a mock User Experience Service for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "UserExperienceService"
    mock_service.realm_name = "experience"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.get_user_preferences = AsyncMock(return_value={"preferences": {}})
    mock_service.update_user_preferences = AsyncMock(return_value=True)
    mock_service.track_interaction = AsyncMock(return_value=True)
    
    return mock_service

@pytest.fixture
def mock_frontend_gateway_service(mock_di_container, mock_platform_gateway):
    """Create a mock Frontend Gateway Service for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "FrontendGatewayService"
    mock_service.realm_name = "experience"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.handle_request = AsyncMock(return_value={"status": "success"})
    mock_service.route_request = AsyncMock(return_value={"status": "routed"})
    
    return mock_service

@pytest.fixture
async def real_session_manager_service(real_di_container, real_platform_gateway):
    """Create a real Session Manager Service for integration tests."""
    try:
        from backend.experience.services.session_manager_service.session_manager_service import SessionManagerService
        
        service = SessionManagerService(
            service_name="SessionManagerService",
            realm_name="experience",
            platform_gateway=real_platform_gateway,
            di_container=real_di_container
        )
        await service.initialize()
        return service
    except Exception as e:
        pytest.skip(f"Could not create real Session Manager Service: {e}")


# ============================================================================
# JOURNEY REALM FIXTURES
# ============================================================================

@pytest.fixture
def mock_structured_journey_orchestrator(mock_di_container, mock_platform_gateway):
    """Create a mock Structured Journey Orchestrator for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "StructuredJourneyOrchestratorService"
    mock_service.realm_name = "journey"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.design_journey = AsyncMock(return_value={"journey_id": "journey_123"})
    mock_service.execute_journey = AsyncMock(return_value={"status": "success"})
    mock_service.advance_journey_step = AsyncMock(return_value={"status": "advanced"})
    mock_service.get_journey_status = AsyncMock(return_value={"status": "active", "current_step": 1})
    
    return mock_service

@pytest.fixture
def mock_mvp_journey_orchestrator(mock_di_container, mock_platform_gateway):
    """Create a mock MVP Journey Orchestrator for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "MVPJourneyOrchestratorService"
    mock_service.realm_name = "journey"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.start_mvp_journey = AsyncMock(return_value={"journey_id": "mvp_journey_123"})
    mock_service.advance_to_next_pillar = AsyncMock(return_value={"status": "advanced"})
    mock_service.get_journey_progress = AsyncMock(return_value={"current_pillar": "content", "progress": 25})
    
    return mock_service

@pytest.fixture
def mock_journey_milestone_tracker(mock_di_container, mock_platform_gateway):
    """Create a mock Journey Milestone Tracker for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "JourneyMilestoneTrackerService"
    mock_service.realm_name = "journey"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.track_milestone = AsyncMock(return_value=True)
    mock_service.get_milestones = AsyncMock(return_value={"milestones": []})
    
    return mock_service

@pytest.fixture
async def real_mvp_journey_orchestrator(real_di_container, real_platform_gateway, real_curator_foundation):
    """Create a real MVP Journey Orchestrator for integration tests."""
    try:
        from backend.journey.services.mvp_journey_orchestrator_service.mvp_journey_orchestrator_service import MVPJourneyOrchestratorService
        
        service = MVPJourneyOrchestratorService(
            service_name="MVPJourneyOrchestratorService",
            realm_name="journey",
            platform_gateway=real_platform_gateway,
            di_container=real_di_container
        )
        
        # Register Curator
        real_di_container.foundation_services["CuratorFoundationService"] = real_curator_foundation
        
        await service.initialize()
        return service
    except Exception as e:
        pytest.skip(f"Could not create real MVP Journey Orchestrator: {e}")


# ============================================================================
# SOLUTION REALM FIXTURES
# ============================================================================

@pytest.fixture
def mock_solution_composer_service(mock_di_container, mock_platform_gateway):
    """Create a mock Solution Composer Service for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "SolutionComposerService"
    mock_service.realm_name = "solution"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.compose_solution = AsyncMock(return_value={"solution_id": "solution_123"})
    mock_service.get_solution_components = AsyncMock(return_value={"components": []})
    mock_service.validate_solution = AsyncMock(return_value={"valid": True})
    
    return mock_service

@pytest.fixture
def mock_solution_deployment_manager(mock_di_container, mock_platform_gateway):
    """Create a mock Solution Deployment Manager for testing."""
    mock_service = MagicMock()
    mock_service.service_name = "SolutionDeploymentManagerService"
    mock_service.realm_name = "solution"
    mock_service.platform_gateway = mock_platform_gateway
    mock_service.di_container = mock_di_container
    
    mock_service.logger = MagicMock()
    mock_service.initialize = AsyncMock(return_value=True)
    mock_service.deploy_solution = AsyncMock(return_value={"deployment_id": "deploy_123"})
    mock_service.get_deployment_status = AsyncMock(return_value={"status": "deployed"})
    
    return mock_service

@pytest.fixture
async def real_solution_composer_service(real_di_container, real_platform_gateway, real_curator_foundation):
    """Create a real Solution Composer Service for integration tests."""
    try:
        from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
        
        service = SolutionComposerService(
            service_name="SolutionComposerService",
            realm_name="solution",
            platform_gateway=real_platform_gateway,
            di_container=real_di_container
        )
        
        # Register Curator
        real_di_container.foundation_services["CuratorFoundationService"] = real_curator_foundation
        
        await service.initialize()
        return service
    except Exception as e:
        pytest.skip(f"Could not create real Solution Composer Service: {e}")


# ============================================================================
# MANAGER SERVICE FIXTURES (for cross-realm testing)
# ============================================================================

@pytest.fixture
def mock_experience_manager_service(mock_di_container, mock_platform_gateway):
    """Create a mock Experience Manager for testing."""
    from bases.manager_service_base import OrchestrationScope, GovernanceLevel
    
    mock_manager = MagicMock()
    mock_manager.service_name = "ExperienceManagerService"
    mock_manager.realm_name = "experience"
    mock_manager.manager_type = "experience_manager"
    mock_manager.orchestration_scope = OrchestrationScope.CROSS_DIMENSIONAL
    mock_manager.governance_level = GovernanceLevel.MODERATE
    
    mock_manager.logger = MagicMock()
    mock_manager.initialize = AsyncMock(return_value=True)
    mock_manager.coordinate_experience = AsyncMock(return_value={"status": "success"})
    
    return mock_manager

@pytest.fixture
def mock_journey_manager_service(mock_di_container, mock_platform_gateway):
    """Create a mock Journey Manager for testing."""
    from bases.manager_service_base import OrchestrationScope, GovernanceLevel
    
    mock_manager = MagicMock()
    mock_manager.service_name = "JourneyManagerService"
    mock_manager.realm_name = "journey"
    mock_manager.manager_type = "journey_manager"
    mock_manager.orchestration_scope = OrchestrationScope.CROSS_DIMENSIONAL
    mock_manager.governance_level = GovernanceLevel.MODERATE
    
    mock_manager.logger = MagicMock()
    mock_manager.initialize = AsyncMock(return_value=True)
    mock_manager.orchestrate_journey = AsyncMock(return_value={"status": "success"})
    
    return mock_manager

@pytest.fixture
def mock_solution_manager_service(mock_di_container, mock_platform_gateway):
    """Create a mock Solution Manager for testing."""
    from bases.manager_service_base import OrchestrationScope, GovernanceLevel
    
    mock_manager = MagicMock()
    mock_manager.service_name = "SolutionManagerService"
    mock_manager.realm_name = "solution"
    mock_manager.manager_type = "solution_manager"
    mock_manager.orchestration_scope = OrchestrationScope.CROSS_DIMENSIONAL
    mock_manager.governance_level = GovernanceLevel.STRICT
    
    mock_manager.logger = MagicMock()
    mock_manager.initialize = AsyncMock(return_value=True)
    mock_manager.compose_solution = AsyncMock(return_value={"status": "success"})
    
    return mock_manager



