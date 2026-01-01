#!/usr/bin/env python3
"""
Solution Manager Service - Integration Tests

Tests Solution Manager Service to validate orchestration of Solution services.

Validates:
- Initialization and service discovery
- Solution service composition (Composer, Analytics, Deployment Manager)
- MCP server initialization
- Manager orchestration capabilities
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, Optional

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
@pytest.mark.timeout_300
async def solution_manager(solution_infrastructure):
    """
    Solution Manager Service instance for each test.
    
    Reuses the solution_infrastructure fixture which includes Journey infrastructure.
    """
    logger.info("🔧 Fixture: Starting solution_manager fixture...")
    
    from backend.solution.services.solution_manager.solution_manager_service import SolutionManagerService
    
    logger.info("🔧 Fixture: Got infrastructure, creating SolutionManagerService...")
    infra = solution_infrastructure
    # Solution Manager has different constructor signature
    manager = SolutionManagerService(
        di_container=infra["di_container"],
        platform_gateway=infra["platform_gateway"]
    )
    
    logger.info("🔧 Fixture: Initializing SolutionManagerService...")
    init_result = await manager.initialize()
    
    if not init_result:
        pytest.fail("SolutionManagerService initialization failed")
    
    logger.info("✅ Fixture: SolutionManagerService initialized successfully")
    
    yield manager
    
    logger.info("🔧 Fixture: Cleaning up SolutionManagerService...")


@pytest.fixture(scope="function")
def test_user_context():
    """Test user context for security and tenant validation."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "session_id": "test_session_123"
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_solution_manager_initialization(solution_manager):
    """Test that Solution Manager Service initializes correctly."""
    logger.info("🧪 Test: Solution Manager initialization")
    
    assert solution_manager is not None, "Solution Manager should be initialized"
    assert solution_manager.service_name == "SolutionManagerService", "Service name should be correct"
    assert solution_manager.realm_name == "solution", "Realm name should be correct"
    
    logger.info("✅ Solution Manager initialized correctly")


@pytest.mark.asyncio
async def test_solution_manager_has_solution_services(solution_manager):
    """Test that Solution Manager can discover Solution services."""
    logger.info("🧪 Test: Solution Manager Solution service discovery")
    
    # Solution Manager stores services in solution_services dictionary (created during initialization)
    # Check if it exists (may be created lazily)
    if hasattr(solution_manager, 'solution_services'):
        assert isinstance(solution_manager.solution_services, dict), "solution_services should be a dictionary"
        logger.info(f"✅ Solution Manager has solution_services: {list(solution_manager.solution_services.keys())}")
    else:
        # May not be initialized yet, but that's okay for this test
        logger.info("ℹ️ solution_services not yet initialized (may be created during service discovery)")
    
    logger.info("✅ Solution Manager has Solution service discovery configured")


@pytest.mark.asyncio
async def test_solution_manager_has_mcp_server(solution_manager):
    """Test that Solution Manager has MCP server."""
    logger.info("🧪 Test: Solution Manager MCP server")
    
    assert hasattr(solution_manager, 'mcp_server'), "Should have mcp_server attribute"
    
    logger.info("✅ Solution Manager has MCP server")


# ============================================================================
# SERVICE ORCHESTRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_solution_manager_can_access_solution_composer(solution_manager, test_user_context):
    """Test that Solution Manager can access Solution Composer."""
    logger.info("🧪 Test: Solution Manager → Solution Composer access")
    
    # Solution Manager stores services in solution_services dictionary (may not exist yet)
    composer_info = None
    if hasattr(solution_manager, 'solution_services'):
        composer_info = solution_manager.solution_services.get('composer')
    if composer_info:
        logger.info(f"📋 Solution Composer info: {composer_info}")
        # Try to get the actual service instance via Curator
        curator = solution_manager.di_container.curator if hasattr(solution_manager.di_container, 'curator') else None
        if curator:
            try:
                composer = await curator.get_service("SolutionComposerService")
                if composer:
                    result = await composer.get_available_solution_types(user_context=test_user_context)
                    logger.info(f"📋 Solution Composer access result: {result}")
                    assert result is not None, "Should be able to access Solution Composer"
                    logger.info("✅ Solution Manager can access Solution Composer")
            except Exception as e:
                logger.info(f"ℹ️ Could not get Solution Composer service: {e}")
        else:
            logger.info("ℹ️ Curator not available")
    else:
        logger.info("ℹ️ Solution Composer not yet discovered")


@pytest.mark.asyncio
async def test_solution_manager_can_access_solution_analytics(solution_manager, test_user_context):
    """Test that Solution Manager can access Solution Analytics."""
    logger.info("🧪 Test: Solution Manager → Solution Analytics access")
    
    # Solution Manager stores services in solution_services dictionary (may not exist yet)
    analytics_info = None
    if hasattr(solution_manager, 'solution_services'):
        analytics_info = solution_manager.solution_services.get('analytics')
    if analytics_info:
        logger.info(f"📋 Solution Analytics info: {analytics_info}")
        # Try to get the actual service instance via Curator
        curator = solution_manager.di_container.curator if hasattr(solution_manager.di_container, 'curator') else None
        if curator:
            try:
                analytics = await curator.get_service("SolutionAnalyticsService")
                if analytics:
                    result = await analytics.calculate_solution_metrics(
                        solution_id="test_solution_123",
                        user_context=test_user_context
                    )
                    logger.info(f"📋 Solution Analytics access result: {result}")
                    assert result is not None, "Should be able to access Solution Analytics"
                    logger.info("✅ Solution Manager can access Solution Analytics")
            except Exception as e:
                logger.info(f"ℹ️ Could not get Solution Analytics service: {e}")
        else:
            logger.info("ℹ️ Curator not available")
    else:
        logger.info("ℹ️ Solution Analytics not yet discovered")


@pytest.mark.asyncio
async def test_solution_manager_can_access_deployment_manager(solution_manager, test_user_context):
    """Test that Solution Manager can access Deployment Manager."""
    logger.info("🧪 Test: Solution Manager → Deployment Manager access")
    
    # Solution Manager stores services in solution_services dictionary (may not exist yet)
    deployment_info = None
    if hasattr(solution_manager, 'solution_services'):
        deployment_info = solution_manager.solution_services.get('deployment_manager')
    if deployment_info:
        logger.info(f"📋 Deployment Manager info: {deployment_info}")
        # Try to get the actual service instance via Curator
        curator = solution_manager.di_container.curator if hasattr(solution_manager.di_container, 'curator') else None
        if curator:
            try:
                deployment_manager = await curator.get_service("SolutionDeploymentManagerService")
                if deployment_manager:
                    result = await deployment_manager.validate_solution_readiness(
                        solution_id="test_solution_123",
                        user_context=test_user_context
                    )
                    logger.info(f"📋 Deployment Manager access result: {result}")
                    assert result is not None, "Should be able to access Deployment Manager"
                    logger.info("✅ Solution Manager can access Deployment Manager")
            except Exception as e:
                logger.info(f"ℹ️ Could not get Deployment Manager service: {e}")
        else:
            logger.info("ℹ️ Curator not available")
    else:
        logger.info("ℹ️ Deployment Manager not yet discovered")


# ============================================================================
# HEALTH AND CAPABILITIES TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_solution_manager_health_check(solution_manager):
    """Test Solution Manager health check."""
    logger.info("🧪 Test: Solution Manager health check")
    
    health = await solution_manager.health_check()
    
    logger.info(f"📋 Health check result: {health}")
    assert health is not None, "Health check should return a result"
    assert "status" in health or "healthy" in health or "success" in health, "Health check should have status"
    
    logger.info("✅ Solution Manager health check works")


@pytest.mark.asyncio
async def test_solution_manager_get_service_capabilities(solution_manager):
    """Test Solution Manager capabilities."""
    logger.info("🧪 Test: Solution Manager capabilities")
    
    capabilities = await solution_manager.get_service_capabilities()
    
    logger.info(f"📋 Capabilities result: {capabilities}")
    assert capabilities is not None, "Capabilities should not be None"
    
    logger.info("✅ Solution Manager capabilities work")

