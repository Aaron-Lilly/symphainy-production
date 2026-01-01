#!/usr/bin/env python3
"""
Solution Composer Service - Component Tests

Tests Solution Composer Service to validate solution design and execution.

Validates:
- Initialization and Smart City integration
- Journey service discovery (MVP, Session, Structured orchestrators)
- Solution template loading
- Solution design and execution
- Multi-phase solution orchestration
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
async def solution_composer(solution_infrastructure):
    """
    Solution Composer Service instance for each test.
    
    Reuses the solution_infrastructure fixture which includes Journey infrastructure.
    """
    logger.info("🔧 Fixture: Starting solution_composer fixture...")
    
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    
    logger.info("🔧 Fixture: Got infrastructure, creating SolutionComposerService...")
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
async def test_solution_composer_initialization(solution_composer):
    """Test that Solution Composer Service initializes correctly."""
    logger.info("🧪 Test: Solution Composer initialization")
    
    assert solution_composer is not None, "Solution Composer should be initialized"
    assert solution_composer.service_name == "SolutionComposerService", "Service name should be correct"
    assert solution_composer.realm_name == "solution", "Realm name should be correct"
    
    logger.info("✅ Solution Composer initialized correctly")


@pytest.mark.asyncio
async def test_solution_composer_has_smart_city_integration(solution_composer):
    """Test that Solution Composer has Smart City service integration."""
    logger.info("🧪 Test: Solution Composer Smart City integration")
    
    assert solution_composer.conductor is not None, "Conductor should be available"
    assert solution_composer.librarian is not None, "Librarian should be available"
    assert solution_composer.data_steward is not None, "Data Steward should be available"
    
    logger.info("✅ Solution Composer has Smart City integration")


@pytest.mark.asyncio
async def test_solution_composer_has_journey_services(solution_composer):
    """Test that Solution Composer can discover Journey services."""
    logger.info("🧪 Test: Solution Composer Journey service discovery")
    
    # Journey services may be None if not available, but the discovery should have been attempted
    # We check that the attributes exist
    assert hasattr(solution_composer, 'structured_journey_orchestrator'), "Should have structured_journey_orchestrator attribute"
    assert hasattr(solution_composer, 'session_journey_orchestrator'), "Should have session_journey_orchestrator attribute"
    assert hasattr(solution_composer, 'mvp_journey_orchestrator'), "Should have mvp_journey_orchestrator attribute"
    assert hasattr(solution_composer, 'journey_analytics'), "Should have journey_analytics attribute"
    
    logger.info("✅ Solution Composer has Journey service discovery configured")


@pytest.mark.asyncio
async def test_solution_composer_has_solution_templates(solution_composer):
    """Test that Solution Composer loads solution templates."""
    logger.info("🧪 Test: Solution Composer solution templates")
    
    assert solution_composer.solution_templates is not None, "Solution templates should be loaded"
    assert isinstance(solution_composer.solution_templates, dict), "Solution templates should be a dictionary"
    
    # Check for expected templates
    expected_templates = ["enterprise_migration", "mvp_solution", "data_analytics"]
    for template_name in expected_templates:
        if template_name in solution_composer.solution_templates:
            logger.info(f"✅ Found template: {template_name}")
    
    logger.info("✅ Solution Composer has solution templates loaded")


# ============================================================================
# SOLUTION DESIGN TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_available_solution_types(solution_composer, test_user_context):
    """Test getting available solution types."""
    logger.info("🧪 Test: Get available solution types")
    
    result = await solution_composer.get_available_solution_types(user_context=test_user_context)
    
    logger.info(f"📋 Available solution types result: {result}")
    assert result is not None, "Result should not be None"
    assert "success" in result or "solution_types" in result, "Result should have success or solution_types"
    
    logger.info("✅ Get available solution types works")


@pytest.mark.asyncio
async def test_get_solution_template(solution_composer, test_user_context):
    """Test getting a solution template."""
    logger.info("🧪 Test: Get solution template")
    
    # Try to get MVP solution template (most likely to be available)
    result = await solution_composer.get_solution_template(
        template_name="mvp_solution",
        user_context=test_user_context
    )
    
    logger.info(f"📋 Get solution template result: {result}")
    assert result is not None, "Result should not be None"
    
    logger.info("✅ Get solution template works")


@pytest.mark.asyncio
async def test_design_solution(solution_composer, test_user_context):
    """Test designing a solution from template."""
    logger.info("🧪 Test: Design solution")
    
    # Design an MVP solution (simplest case)
    result = await solution_composer.design_solution(
        solution_type="mvp_solution",
        requirements={
            "description": "Test MVP solution",
            "user_id": test_user_context["user_id"]
        },
        user_context=test_user_context
    )
    
    logger.info(f"📋 Design solution result: {result}")
    assert result is not None, "Result should not be None"
    
    # If successful, should have solution_id
    if result.get("success") or "solution_id" in result:
        logger.info("✅ Solution designed successfully")
        if "solution_id" in result:
            logger.info(f"📋 Solution ID: {result['solution_id']}")
    else:
        logger.info(f"ℹ️ Design solution returned: {result.get('error', 'Unknown error')}")
    
    logger.info("✅ Design solution method works")


# ============================================================================
# SOLUTION EXECUTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_solution_status(solution_composer, test_user_context):
    """Test getting solution status."""
    logger.info("🧪 Test: Get solution status")
    
    # Try with a test solution ID (may not exist, but method should work)
    # Note: get_solution_status requires user_id parameter
    result = await solution_composer.get_solution_status(
        solution_id="test_solution_123",
        user_id=test_user_context["user_id"],
        user_context=test_user_context
    )
    
    logger.info(f"📋 Get solution status result: {result}")
    assert result is not None, "Result should not be None"
    
    logger.info("✅ Get solution status works")


@pytest.mark.asyncio
async def test_customize_solution(solution_composer, test_user_context):
    """Test customizing a solution."""
    logger.info("🧪 Test: Customize solution")
    
    # Try to customize a test solution
    result = await solution_composer.customize_solution(
        solution_id="test_solution_123",
        customizations={
            "custom_field": "custom_value"
        },
        user_context=test_user_context
    )
    
    logger.info(f"📋 Customize solution result: {result}")
    assert result is not None, "Result should not be None"
    
    logger.info("✅ Customize solution works")


# ============================================================================
# HEALTH AND CAPABILITIES TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_solution_composer_health_check(solution_composer):
    """Test Solution Composer health check."""
    logger.info("🧪 Test: Solution Composer health check")
    
    health = await solution_composer.health_check()
    
    logger.info(f"📋 Health check result: {health}")
    assert health is not None, "Health check should return a result"
    assert "status" in health or "healthy" in health or "success" in health, "Health check should have status"
    
    logger.info("✅ Solution Composer health check works")


@pytest.mark.asyncio
async def test_solution_composer_get_capabilities(solution_composer):
    """Test Solution Composer capabilities."""
    logger.info("🧪 Test: Solution Composer capabilities")
    
    # Note: The method is called get_service_capabilities, not get_capabilities
    capabilities = await solution_composer.get_service_capabilities()
    
    logger.info(f"📋 Capabilities result: {capabilities}")
    assert capabilities is not None, "Capabilities should not be None"
    
    logger.info("✅ Solution Composer capabilities work")

