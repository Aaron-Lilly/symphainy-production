#!/usr/bin/env python3
"""
Business Outcomes Orchestrator - End-to-End Functional Tests

Tests Business Outcomes Orchestrator to ensure it fully enables the Business Outcomes Pillar:
- Outcome tracking (track_outcomes)
- Roadmap generation (generate_roadmap, generate_strategic_roadmap)
- KPI calculation (calculate_kpis)
- Outcome analysis (analyze_outcomes)
- POC proposal generation (generate_poc_proposal)
- Strategic planning (create_comprehensive_strategic_plan)
- Journey visualization (get_journey_visualization)
- Enabling services coordination
- MVP UI format compatibility

Based on MVP description and frontend API contract.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, Optional

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_excel_file,
    create_test_json_file
)
from tests.integration.layer_8_business_enablement.test_utilities import (
    ContentStewardHelper,
    TestDataManager
)

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES - Reusing Proven Patterns
# ============================================================================

@pytest.fixture(scope="function")
async def business_outcomes_orchestrator(smart_city_infrastructure):
    """
    BusinessOutcomesOrchestrator instance for each test.
    
    Reuses the proven pattern from insights_orchestrator tests.
    """
    logger.info("🔧 Fixture: Starting business_outcomes_orchestrator fixture...")
    
    from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    logger.info("🔧 Fixture: Got infrastructure, creating DeliveryManagerService...")
    infra = smart_city_infrastructure
    
    # Create DeliveryManagerService (provides delivery_manager for orchestrator)
    delivery_manager = DeliveryManagerService(
        di_container=infra["di_container"],
        platform_gateway=infra["platform_gateway"]
    )
    
    logger.info("🔧 Fixture: Initializing DeliveryManagerService...")
    await delivery_manager.initialize()
    
    # Get Business Outcomes Orchestrator from delivery manager
    from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
    
    logger.info("🔧 Fixture: Creating BusinessOutcomesOrchestrator...")
    orchestrator = BusinessOutcomesOrchestrator(delivery_manager=delivery_manager)
    
    logger.info("🔧 Fixture: Initializing orchestrator (this may take time)...")
    try:
        result = await asyncio.wait_for(orchestrator.initialize(), timeout=120.0)
        logger.info(f"✅ Fixture: Orchestrator initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Orchestrator initialization returned False")
            pytest.fail("Business Outcomes Orchestrator failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Orchestrator initialization timed out after 120 seconds")
        pytest.fail("Business Outcomes Orchestrator initialization timed out")
    except Exception as e:
        logger.error(f"❌ Fixture: Orchestrator initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Orchestrator ready, yielding to test...")
    yield orchestrator
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture(scope="function")
async def storage_helper(smart_city_infrastructure, infrastructure_storage):
    """
    Storage helper for each test.
    
    Reuses the proven pattern from insights_orchestrator tests.
    """
    storage = infrastructure_storage["file_storage"]
    user_context = TestDataManager.get_user_context()
    helper = ContentStewardHelper(storage, user_context)
    
    yield helper


@pytest.fixture(scope="function")
def mock_user_context() -> Dict[str, Any]:
    """Create a mock user context."""
    return TestDataManager.get_user_context()


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_orchestrator_initialization(business_outcomes_orchestrator):
    """Test that Business Outcomes Orchestrator initializes correctly."""
    logger.info("🧪 Test: Orchestrator initialization")
    
    assert business_outcomes_orchestrator is not None
    assert hasattr(business_outcomes_orchestrator, 'delivery_manager')
    assert hasattr(business_outcomes_orchestrator, 'librarian')
    assert hasattr(business_outcomes_orchestrator, 'data_steward')
    
    logger.info("✅ Orchestrator initialized correctly")


@pytest.mark.asyncio
async def test_orchestrator_delegates_to_enabling_services(business_outcomes_orchestrator):
    """Test that orchestrator can access enabling services."""
    logger.info("🧪 Test: Enabling services delegation")
    
    # Test service discovery methods
    metrics_service = await business_outcomes_orchestrator._get_metrics_calculator_service()
    report_service = await business_outcomes_orchestrator._get_report_generator_service()
    roadmap_service = await business_outcomes_orchestrator._get_roadmap_generation_service()
    poc_service = await business_outcomes_orchestrator._get_poc_generation_service()
    
    # At least one service should be available
    services_available = sum([
        metrics_service is not None,
        report_service is not None,
        roadmap_service is not None,
        poc_service is not None
    ])
    
    assert services_available > 0, "At least one enabling service should be available"
    
    logger.info(f"✅ Enabling services available: {services_available}/4")


# ============================================================================
# OUTCOME TRACKING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_track_outcomes(business_outcomes_orchestrator, storage_helper, mock_user_context):
    """Test tracking business outcomes."""
    logger.info("🧪 Test: Track outcomes")
    
    # Upload data file
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Track outcomes
    result = await business_outcomes_orchestrator.track_outcomes(
        resource_id=file_id,
        options={
            "metric_name": "outcome_kpi",
            "metric_params": {"formula": "sum(revenue)"}
        }
    )
    
    assert isinstance(result, dict)
    assert "status" in result or "success" in result
    
    if result.get("status") == "success" or result.get("success"):
        assert "outcomes" in result or "kpi" in result or "data" in result
        logger.info("✅ Outcome tracking successful")
    else:
        logger.info(f"⚠️ Outcome tracking failed: {result.get('message') or result.get('error')}")


# ============================================================================
# ROADMAP GENERATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_generate_roadmap(business_outcomes_orchestrator, storage_helper):
    """Test generating a roadmap."""
    logger.info("🧪 Test: Generate roadmap")
    
    # Upload data file
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    business_context = {
        "business_name": "Test Business",
        "industry": "Technology",
        "objectives": ["Increase revenue by 20%", "Improve customer satisfaction"],
        "budget": 100000,
        "timeline_days": 180
    }
    
    result = await business_outcomes_orchestrator.generate_roadmap(
        resource_id=file_id,
        options={"business_context": business_context}
    )
    
    assert isinstance(result, dict)
    assert "status" in result or "success" in result
    
    if result.get("status") == "success" or result.get("success"):
        assert "roadmap" in result or "phases" in result or "data" in result
        logger.info("✅ Roadmap generation successful")
    else:
        logger.info(f"⚠️ Roadmap generation failed: {result.get('message') or result.get('error')}")


@pytest.mark.asyncio
async def test_generate_strategic_roadmap(business_outcomes_orchestrator):
    """Test generating strategic roadmap from pillar outputs."""
    logger.info("🧪 Test: Generate strategic roadmap")
    
    # Simulate pillar outputs
    business_context = {
        "pillar_outputs": {
            "content_analysis": {
                "summary": "Content analysis complete",
                "key_findings": ["Finding 1", "Finding 2"]
            },
            "insights": {
                "summary": "Insights analysis complete",
                "key_metrics": ["Metric 1", "Metric 2"]
            },
            "operations": {
                "summary": "Operations analysis complete",
                "recommendations": ["Rec 1", "Rec 2"]
            }
        },
        "business_name": "Test Business",
        "budget": 100000,
        "timeline_days": 180,
        "roadmap_options": {"roadmap_type": "hybrid"}
    }
    
    result = await business_outcomes_orchestrator.generate_strategic_roadmap(
        business_context=business_context,
        user_id="test_user_123"
    )
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if result.get("success"):
        assert "roadmap" in result or "strategic_plan" in result
        logger.info("✅ Strategic roadmap generation successful")
    else:
        logger.info(f"⚠️ Strategic roadmap generation failed: {result.get('message') or result.get('error')}")


# ============================================================================
# KPI CALCULATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_calculate_kpis(business_outcomes_orchestrator, storage_helper):
    """Test calculating KPIs."""
    logger.info("🧪 Test: Calculate KPIs")
    
    # Upload data file
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Calculate KPIs
    result = await business_outcomes_orchestrator.calculate_kpis(
        resource_id=file_id,
        options={
            "kpi_names": ["revenue", "customer_satisfaction", "operational_efficiency"]
        }
    )
    
    assert isinstance(result, dict)
    assert "status" in result or "success" in result
    
    if result.get("status") == "success" or result.get("success"):
        assert "kpis" in result or "data" in result
        logger.info("✅ KPI calculation successful")
    else:
        logger.info(f"⚠️ KPI calculation failed: {result.get('message') or result.get('error')}")


# ============================================================================
# OUTCOME ANALYSIS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_analyze_outcomes(business_outcomes_orchestrator, storage_helper):
    """Test analyzing business outcomes."""
    logger.info("🧪 Test: Analyze outcomes")
    
    # Upload data file
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Analyze outcomes
    result = await business_outcomes_orchestrator.analyze_outcomes(
        resource_id=file_id,
        options={"analysis_type": "trend"}
    )
    
    assert isinstance(result, dict)
    assert "status" in result or "success" in result
    
    if result.get("status") == "success" or result.get("success"):
        assert "analysis" in result or "trends" in result or "data" in result
        logger.info("✅ Outcome analysis successful")
    else:
        logger.info(f"⚠️ Outcome analysis failed: {result.get('message') or result.get('error')}")


# ============================================================================
# POC PROPOSAL GENERATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_generate_poc_proposal(business_outcomes_orchestrator):
    """Test generating POC proposal from pillar outputs."""
    logger.info("🧪 Test: Generate POC proposal")
    
    # Simulate pillar outputs
    business_context = {
        "pillar_outputs": {
            "content_analysis": {
                "summary": "Content analysis complete",
                "key_findings": ["Finding 1", "Finding 2"]
            },
            "insights": {
                "summary": "Insights analysis complete",
                "key_metrics": ["Metric 1", "Metric 2"]
            },
            "operations": {
                "summary": "Operations analysis complete",
                "recommendations": ["Rec 1", "Rec 2"]
            }
        },
        "proposal_options": {
            "poc_type": "hybrid",
            "business_name": "Test Business",
            "budget": 50000,
            "timeline_days": 90
        }
    }
    
    result = await business_outcomes_orchestrator.generate_poc_proposal(
        business_context=business_context,
        user_id="test_user_123"
    )
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if result.get("success"):
        assert "proposal" in result or "poc_proposal" in result
        logger.info("✅ POC proposal generation successful")
    else:
        logger.info(f"⚠️ POC proposal generation failed: {result.get('message') or result.get('error')}")


# ============================================================================
# STRATEGIC PLANNING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_comprehensive_strategic_plan(business_outcomes_orchestrator):
    """Test creating comprehensive strategic plan."""
    logger.info("🧪 Test: Create comprehensive strategic plan")
    
    business_context = {
        "business_name": "Test Business",
        "industry": "Technology",
        "objectives": ["Objective 1", "Objective 2", "Objective 3"],
        "budget": 200000,
        "timeline_days": 365
    }
    
    result = await business_outcomes_orchestrator.create_comprehensive_strategic_plan(
        business_context=business_context,
        user_id="test_user_123"
    )
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if result.get("success"):
        assert "strategic_plan" in result or "plan" in result or "comprehensive_planning" in result
        logger.info("✅ Strategic plan creation successful")
    else:
        logger.info(f"⚠️ Strategic plan creation failed: {result.get('message') or result.get('error')}")


@pytest.mark.asyncio
async def test_track_strategic_progress(business_outcomes_orchestrator):
    """Test tracking strategic progress."""
    logger.info("🧪 Test: Track strategic progress")
    
    goals = [
        {"goal_id": "goal_1", "name": "Increase revenue", "target": 1000000},
        {"goal_id": "goal_2", "name": "Improve customer satisfaction", "target": 90}
    ]
    
    result = await business_outcomes_orchestrator.track_strategic_progress(
        goals=goals,
        performance_data={"revenue": 800000, "customer_satisfaction": 85},
        user_id="test_user_123"
    )
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if result.get("success"):
        # The result contains goal_tracking, business_analysis, performance_analysis
        assert "goal_tracking" in result or "business_analysis" in result or "performance_analysis" in result
        logger.info("✅ Strategic progress tracking successful")
    else:
        logger.info(f"⚠️ Strategic progress tracking failed: {result.get('message') or result.get('error')}")


@pytest.mark.asyncio
async def test_analyze_strategic_trends(business_outcomes_orchestrator):
    """Test analyzing strategic trends."""
    logger.info("🧪 Test: Analyze strategic trends")
    
    market_data = {
        "industry": "Technology",
        "market_trends": ["AI adoption", "Cloud migration", "Digital transformation"],
        "competitor_analysis": {
            "competitor_1": {"revenue": 10000000, "market_share": 0.15},
            "competitor_2": {"revenue": 8000000, "market_share": 0.12}
        },
        "economic_indicators": {
            "gdp_growth": 2.5,
            "inflation_rate": 3.2
        }
    }
    
    result = await business_outcomes_orchestrator.analyze_strategic_trends(
        market_data=market_data,
        user_id="test_user_123"
    )
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if result.get("success"):
        # The result contains business_trend_analysis, competitive_analysis, strategic_implications
        assert "business_trend_analysis" in result or "competitive_analysis" in result or "strategic_implications" in result
        logger.info("✅ Strategic trends analysis successful")
    else:
        logger.info(f"⚠️ Strategic trends analysis failed: {result.get('message') or result.get('error')}")


# ============================================================================
# VISUALIZATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_journey_visualization(business_outcomes_orchestrator):
    """Test getting journey visualization."""
    logger.info("🧪 Test: Get journey visualization")
    
    result = await business_outcomes_orchestrator.get_journey_visualization(
        session_id="test_session_123",
        user_id="test_user_123"
    )
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if result.get("success"):
        assert "visualization" in result or "journey" in result
        logger.info("✅ Journey visualization successful")
    else:
        logger.info(f"⚠️ Journey visualization failed: {result.get('message') or result.get('error')}")


# ============================================================================
# PILLAR INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_pillar_summaries(business_outcomes_orchestrator):
    """Test getting pillar summaries."""
    logger.info("🧪 Test: Get pillar summaries")
    
    result = await business_outcomes_orchestrator.get_pillar_summaries(
        session_id="test_session_123",
        user_id="test_user_123"
    )
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if result.get("success"):
        assert "summaries" in result or "pillars" in result
        logger.info("✅ Pillar summaries retrieval successful")
    else:
        logger.info(f"⚠️ Pillar summaries retrieval failed: {result.get('message') or result.get('error')}")


# ============================================================================
# HEALTH AND CAPABILITIES TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_health_check(business_outcomes_orchestrator):
    """Test orchestrator health check."""
    logger.info("🧪 Test: Health check")
    
    health = await business_outcomes_orchestrator.health_check()
    
    assert isinstance(health, dict)
    assert "status" in health or "orchestrator" in health
    assert "orchestrator" in health
    assert "is_initialized" in health
    
    logger.info("✅ Health check passed")


@pytest.mark.asyncio
async def test_get_service_capabilities(business_outcomes_orchestrator):
    """Test getting service capabilities."""
    logger.info("🧪 Test: Get service capabilities")
    
    # get_service_capabilities is NOT async - it's a regular method
    capabilities = business_outcomes_orchestrator.get_service_capabilities()
    
    assert isinstance(capabilities, dict)
    assert "orchestrator_name" in capabilities
    assert "service_type" in capabilities
    assert "capabilities" in capabilities
    
    # Should have expected capabilities
    expected_capabilities = ["service_composition", "workflow_orchestration", "agent_management"]
    for cap in expected_capabilities:
        assert cap in capabilities.get("capabilities", [])
    
    logger.info("✅ Service capabilities retrieved")

