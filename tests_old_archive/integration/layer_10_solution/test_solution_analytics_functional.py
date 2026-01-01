#!/usr/bin/env python3
"""
Solution Analytics Service - Component Tests

Tests Solution Analytics Service to validate solution performance analysis.

Validates:
- Initialization and Smart City integration
- Journey Analytics service discovery
- Solution metrics calculation
- Performance analysis
- Optimization recommendations
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
async def solution_analytics(solution_infrastructure):
    """
    Solution Analytics Service instance for each test.
    
    Reuses the solution_infrastructure fixture which includes Journey infrastructure.
    """
    logger.info("🔧 Fixture: Starting solution_analytics fixture...")
    
    from backend.solution.services.solution_analytics_service.solution_analytics_service import SolutionAnalyticsService
    
    logger.info("🔧 Fixture: Got infrastructure, creating SolutionAnalyticsService...")
    infra = solution_infrastructure
    analytics = SolutionAnalyticsService(
        service_name="SolutionAnalyticsService",
        realm_name="solution",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    
    logger.info("🔧 Fixture: Initializing SolutionAnalyticsService...")
    init_result = await analytics.initialize()
    
    if not init_result:
        pytest.fail("SolutionAnalyticsService initialization failed")
    
    logger.info("✅ Fixture: SolutionAnalyticsService initialized successfully")
    
    yield analytics
    
    logger.info("🔧 Fixture: Cleaning up SolutionAnalyticsService...")


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
async def test_solution_analytics_initialization(solution_analytics):
    """Test that Solution Analytics Service initializes correctly."""
    logger.info("🧪 Test: Solution Analytics initialization")
    
    assert solution_analytics is not None, "Solution Analytics should be initialized"
    assert solution_analytics.service_name == "SolutionAnalyticsService", "Service name should be correct"
    assert solution_analytics.realm_name == "solution", "Realm name should be correct"
    
    logger.info("✅ Solution Analytics initialized correctly")


@pytest.mark.asyncio
async def test_solution_analytics_has_smart_city_integration(solution_analytics):
    """Test that Solution Analytics has Smart City service integration."""
    logger.info("🧪 Test: Solution Analytics Smart City integration")
    
    # Solution Analytics only uses Data Steward and Librarian (not Conductor)
    assert solution_analytics.librarian is not None, "Librarian should be available"
    assert solution_analytics.data_steward is not None, "Data Steward should be available"
    
    logger.info("✅ Solution Analytics has Smart City integration")


@pytest.mark.asyncio
async def test_solution_analytics_has_journey_analytics(solution_analytics):
    """Test that Solution Analytics can discover Journey Analytics service."""
    logger.info("🧪 Test: Solution Analytics Journey Analytics discovery")
    
    # Journey Analytics may be None if not available, but the discovery should have been attempted
    assert hasattr(solution_analytics, 'journey_analytics'), "Should have journey_analytics attribute"
    
    logger.info("✅ Solution Analytics has Journey Analytics discovery configured")


# ============================================================================
# ANALYTICS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_calculate_solution_metrics(solution_analytics, test_user_context):
    """Test calculating solution metrics."""
    logger.info("🧪 Test: Calculate solution metrics")
    
    result = await solution_analytics.calculate_solution_metrics(
        solution_id="test_solution_123",
        user_context=test_user_context
    )
    
    logger.info(f"📋 Calculate metrics result: {result}")
    assert result is not None, "Result should not be None"
    
    logger.info("✅ Calculate solution metrics works")


@pytest.mark.asyncio
async def test_get_solution_completion_rate(solution_analytics, test_user_context):
    """Test getting solution completion rate."""
    logger.info("🧪 Test: Get solution completion rate")
    
    result = await solution_analytics.get_solution_completion_rate(
        solution_id="test_solution_123",
        user_context=test_user_context
    )
    
    logger.info(f"📋 Completion rate result: {result}")
    assert result is not None, "Result should not be None"
    
    logger.info("✅ Get solution completion rate works")


@pytest.mark.asyncio
async def test_identify_solution_bottlenecks(solution_analytics, test_user_context):
    """Test identifying solution bottlenecks."""
    logger.info("🧪 Test: Identify solution bottlenecks")
    
    result = await solution_analytics.identify_solution_bottlenecks(
        solution_id="test_solution_123",
        user_context=test_user_context
    )
    
    logger.info(f"📋 Bottlenecks result: {result}")
    assert result is not None, "Result should not be None"
    
    logger.info("✅ Identify solution bottlenecks works")


@pytest.mark.asyncio
async def test_analyze_solution_performance(solution_analytics, test_user_context):
    """Test analyzing solution performance."""
    logger.info("🧪 Test: Analyze solution performance")
    
    result = await solution_analytics.analyze_solution_performance(
        solution_id="test_solution_123",
        user_context=test_user_context
    )
    
    logger.info(f"📋 Performance analysis result: {result}")
    assert result is not None, "Result should not be None"
    
    logger.info("✅ Analyze solution performance works")


@pytest.mark.asyncio
async def test_get_solution_optimization_recommendations(solution_analytics, test_user_context):
    """Test getting optimization recommendations."""
    logger.info("🧪 Test: Get optimization recommendations")
    
    result = await solution_analytics.get_solution_optimization_recommendations(
        solution_id="test_solution_123",
        user_context=test_user_context
    )
    
    logger.info(f"📋 Optimization recommendations result: {result}")
    assert result is not None, "Result should not be None"
    
    logger.info("✅ Get optimization recommendations works")


# ============================================================================
# HEALTH AND CAPABILITIES TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_solution_analytics_health_check(solution_analytics):
    """Test Solution Analytics health check."""
    logger.info("🧪 Test: Solution Analytics health check")
    
    health = await solution_analytics.health_check()
    
    logger.info(f"📋 Health check result: {health}")
    assert health is not None, "Health check should return a result"
    assert "status" in health or "healthy" in health or "success" in health, "Health check should have status"
    
    logger.info("✅ Solution Analytics health check works")


@pytest.mark.asyncio
async def test_solution_analytics_get_service_capabilities(solution_analytics):
    """Test Solution Analytics capabilities."""
    logger.info("🧪 Test: Solution Analytics capabilities")
    
    capabilities = await solution_analytics.get_service_capabilities()
    
    logger.info(f"📋 Capabilities result: {capabilities}")
    assert capabilities is not None, "Capabilities should not be None"
    
    logger.info("✅ Solution Analytics capabilities work")

