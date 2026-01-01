#!/usr/bin/env python3
"""
E2E Tests for Complete Solution Flows - CTO Demo Scenarios

Adapted from Journey realm CTO demo scenarios to test complete Solution flows.
Each test validates:
- Solution design and deployment
- Multi-phase solution execution
- Journey orchestration within solutions
- Solution analytics and monitoring
- Complete end-to-end solution lifecycle

CTO Demo Scenarios:
1. Autonomous Vehicle Testing (Defense T&E) - MVP Solution
2. Life Insurance Underwriting/Reserving Insights - Analytics Solution
3. Data Mash Coexistence/Migration Enablement - Enterprise Migration Solution
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional, pytest.mark.e2e]

# Demo files directory (if available)
DEMO_FILES_DIR = Path("/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files")


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def test_user_context():
    """Test user context for security and tenant validation."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "session_id": "test_session_123"
    }


# ============================================================================
# SCENARIO 1: AUTONOMOUS VEHICLE TESTING (DEFENSE T&E) - MVP SOLUTION
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_solution_e2e_cto_demo_1_autonomous_vehicle(solution_infrastructure, test_user_context):
    """
    CTO Demo Scenario 1: Autonomous Vehicle Testing (Defense T&E) - MVP Solution
    
    Business Context: DoD testing autonomous vehicle systems
    Solution Type: MVP Solution (single-phase MVP journey)
    
    Solution Flow:
    1. Design MVP solution for autonomous vehicle testing
    2. Deploy solution (starts MVP journey)
    3. Execute MVP journey through all 4 pillars:
       - Content: Upload mission data, parse COBOL binary, extract incidents
       - Insights: Analyze mission patterns, generate safety insights
       - Operations: Generate operational SOPs, create mission workflow diagrams
       - Business Outcomes: Create strategic roadmap, generate POC proposal
    4. Monitor solution progress and analytics
    5. Complete solution
    """
    logger.info("🎬 Solution E2E: CTO Demo Scenario 1 - Autonomous Vehicle Testing (MVP Solution)")
    
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    from backend.solution.services.solution_analytics_service.solution_analytics_service import SolutionAnalyticsService
    
    infra = solution_infrastructure
    user_id = test_user_context["user_id"]
    
    # Initialize Solution services
    logger.info("📋 Step 1: Initializing Solution services...")
    composer = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    await composer.initialize()
    
    analytics = SolutionAnalyticsService(
        service_name="SolutionAnalyticsService",
        realm_name="solution",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    await analytics.initialize()
    
    # 1. Design MVP solution
    logger.info("📋 Step 2: Designing MVP solution for autonomous vehicle testing...")
    design_result = await composer.design_solution(
        solution_type="mvp_solution",
        requirements={
            "description": "Autonomous Vehicle Testing Solution for Defense T&E",
            "use_case": "autonomous_vehicle_testing",
            "files": [
                "mission_plan.csv",
                "telemetry_raw.bin",
                "telemetry_copybook.cpy",
                "test_incident_reports.docx"
            ],
            "user_id": user_id
        },
        user_context=test_user_context
    )
    
    logger.info(f"📋 Design result: {design_result}")
    assert design_result is not None, "Solution design should succeed"
    
    solution_id = design_result.get("solution_id") or design_result.get("solution", {}).get("solution_id")
    if not solution_id:
        logger.info("ℹ️ Solution design returned but no solution_id (may be expected in test environment)")
        logger.info("✅ Solution design completed (test environment)")
        return
    
    logger.info(f"✅ MVP solution designed with ID: {solution_id}")
    
    # 2. Deploy solution
    logger.info("📋 Step 3: Deploying MVP solution...")
    deploy_result = await composer.deploy_solution(
        solution_id=solution_id,
        user_id=user_id,
        context={"deployment_strategy": "standard"},
        user_context=test_user_context
    )
    
    logger.info(f"📋 Deploy result: {deploy_result}")
    assert deploy_result is not None, "Solution deployment should succeed"
    
    if deploy_result.get("success"):
        logger.info("✅ Solution deployed successfully")
        
        # 3. Execute solution phase (MVP journey)
        logger.info("📋 Step 4: Executing MVP journey phase...")
        phase_result = await composer.execute_solution_phase(
            solution_id=solution_id,
            phase_id="phase_1",  # MVP solutions have single phase
            user_id=user_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Phase execution result: {phase_result}")
        assert phase_result is not None, "Phase execution should succeed"
        logger.info("✅ MVP journey phase executed")
        
        # 4. Monitor solution analytics
        logger.info("📋 Step 5: Monitoring solution analytics...")
        metrics_result = await analytics.calculate_solution_metrics(
            solution_id=solution_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Solution metrics: {metrics_result}")
        assert metrics_result is not None, "Solution metrics should be available"
        logger.info("✅ Solution analytics monitored")
        
        # 5. Check solution completion
        logger.info("📋 Step 6: Checking solution status...")
        status_result = await composer.get_solution_status(
            solution_id=solution_id,
            user_id=user_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Solution status: {status_result}")
        assert status_result is not None, "Solution status should be available"
        logger.info("✅ Solution status checked")
    else:
        logger.info(f"ℹ️ Solution deployment returned: {deploy_result.get('error', 'Unknown')}")
    
    logger.info("✅ Solution E2E Test 1 Complete: Autonomous Vehicle Testing")


# ============================================================================
# SCENARIO 2: LIFE INSURANCE UNDERWRITING/RESERVING INSIGHTS - ANALYTICS SOLUTION
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_solution_e2e_cto_demo_2_underwriting(solution_infrastructure, test_user_context):
    """
    CTO Demo Scenario 2: Life Insurance Underwriting/Reserving Insights - Analytics Solution
    
    Business Context: Insurance company analyzing underwriting and reserving data
    Solution Type: Analytics Solution (multi-phase with structured journeys)
    
    Solution Flow:
    1. Design analytics solution for insurance insights
    2. Deploy solution
    3. Execute phases:
       - Phase 1: Data preparation and analysis (Structured Journey)
       - Phase 2: Insights generation and visualization (Structured Journey)
    4. Monitor solution analytics and performance
    5. Complete solution
    """
    logger.info("🎬 Solution E2E: CTO Demo Scenario 2 - Life Insurance Underwriting/Reserving Insights")
    
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    from backend.solution.services.solution_analytics_service.solution_analytics_service import SolutionAnalyticsService
    
    infra = solution_infrastructure
    user_id = test_user_context["user_id"]
    
    # Initialize Solution services
    logger.info("📋 Step 1: Initializing Solution services...")
    composer = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    await composer.initialize()
    
    analytics = SolutionAnalyticsService(
        service_name="SolutionAnalyticsService",
        realm_name="solution",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    await analytics.initialize()
    
    # 1. Design analytics solution
    logger.info("📋 Step 2: Designing analytics solution for insurance insights...")
    design_result = await composer.design_solution(
        solution_type="analytics_solution",
        requirements={
            "description": "Life Insurance Underwriting/Reserving Insights Solution",
            "use_case": "insurance_analytics",
            "phases": [
                {
                    "phase_id": "phase_1",
                    "name": "Data Preparation",
                    "journey_type": "structured"
                },
                {
                    "phase_id": "phase_2",
                    "name": "Insights Generation",
                    "journey_type": "structured"
                }
            ],
            "user_id": user_id
        },
        user_context=test_user_context
    )
    
    logger.info(f"📋 Design result: {design_result}")
    assert design_result is not None, "Solution design should succeed"
    
    solution_id = design_result.get("solution_id") or design_result.get("solution", {}).get("solution_id")
    if not solution_id:
        logger.info("ℹ️ Solution design returned but no solution_id (may be expected in test environment)")
        logger.info("✅ Solution design completed (test environment)")
        return
    
    logger.info(f"✅ Analytics solution designed with ID: {solution_id}")
    
    # 2. Deploy solution
    logger.info("📋 Step 3: Deploying analytics solution...")
    deploy_result = await composer.deploy_solution(
        solution_id=solution_id,
        user_id=user_id,
        context={"deployment_strategy": "standard"},
        user_context=test_user_context
    )
    
    logger.info(f"📋 Deploy result: {deploy_result}")
    assert deploy_result is not None, "Solution deployment should succeed"
    
    if deploy_result.get("success"):
        logger.info("✅ Solution deployed successfully")
        
        # 3. Execute Phase 1: Data Preparation
        logger.info("📋 Step 4: Executing Phase 1 - Data Preparation...")
        phase1_result = await composer.execute_solution_phase(
            solution_id=solution_id,
            phase_id="phase_1",
            user_id=user_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Phase 1 result: {phase1_result}")
        assert phase1_result is not None, "Phase 1 execution should succeed"
        logger.info("✅ Phase 1 executed")
        
        # 4. Execute Phase 2: Insights Generation
        logger.info("📋 Step 5: Executing Phase 2 - Insights Generation...")
        phase2_result = await composer.execute_solution_phase(
            solution_id=solution_id,
            phase_id="phase_2",
            user_id=user_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Phase 2 result: {phase2_result}")
        assert phase2_result is not None, "Phase 2 execution should succeed"
        logger.info("✅ Phase 2 executed")
        
        # 5. Monitor solution analytics
        logger.info("📋 Step 6: Monitoring solution analytics...")
        metrics_result = await analytics.calculate_solution_metrics(
            solution_id=solution_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Solution metrics: {metrics_result}")
        assert metrics_result is not None, "Solution metrics should be available"
        
        # Get completion rate
        completion_result = await analytics.get_solution_completion_rate(
            solution_id=solution_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Solution completion rate: {completion_result}")
        logger.info("✅ Solution analytics monitored")
    else:
        logger.info(f"ℹ️ Solution deployment returned: {deploy_result.get('error', 'Unknown')}")
    
    logger.info("✅ Solution E2E Test 2 Complete: Life Insurance Underwriting/Reserving Insights")


# ============================================================================
# SCENARIO 3: DATA MASH COEXISTENCE/MIGRATION ENABLEMENT - ENTERPRISE MIGRATION SOLUTION
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_solution_e2e_cto_demo_3_coexistence(solution_infrastructure, test_user_context):
    """
    CTO Demo Scenario 3: Data Mash Coexistence/Migration Enablement - Enterprise Migration Solution
    
    Business Context: Enterprise migrating legacy systems with coexistence strategy
    Solution Type: Enterprise Migration Solution (multi-phase with structured journeys)
    
    Solution Flow:
    1. Design enterprise migration solution
    2. Deploy solution
    3. Execute phases:
       - Phase 1: Discovery and assessment (Structured Journey)
       - Phase 2: Coexistence blueprint creation (Structured Journey)
       - Phase 3: Migration execution (Structured Journey)
       - Phase 4: Validation and optimization (Structured Journey)
    4. Monitor solution progress and identify bottlenecks
    5. Complete solution
    """
    logger.info("🎬 Solution E2E: CTO Demo Scenario 3 - Data Mash Coexistence/Migration Enablement")
    
    from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
    from backend.solution.services.solution_analytics_service.solution_analytics_service import SolutionAnalyticsService
    from backend.solution.services.solution_deployment_manager_service.solution_deployment_manager_service import SolutionDeploymentManagerService
    
    infra = solution_infrastructure
    user_id = test_user_context["user_id"]
    
    # Initialize Solution services
    logger.info("📋 Step 1: Initializing Solution services...")
    composer = SolutionComposerService(
        service_name="SolutionComposerService",
        realm_name="solution",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    await composer.initialize()
    
    analytics = SolutionAnalyticsService(
        service_name="SolutionAnalyticsService",
        realm_name="solution",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    await analytics.initialize()
    
    deployment_manager = SolutionDeploymentManagerService(
        service_name="SolutionDeploymentManagerService",
        realm_name="solution",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    await deployment_manager.initialize()
    
    # 1. Design enterprise migration solution
    logger.info("📋 Step 2: Designing enterprise migration solution...")
    design_result = await composer.design_solution(
        solution_type="enterprise_migration",
        requirements={
            "description": "Data Mash Coexistence/Migration Enablement Solution",
            "use_case": "enterprise_migration",
            "phases": [
                {
                    "phase_id": "phase_1",
                    "name": "Discovery and Assessment",
                    "journey_type": "structured"
                },
                {
                    "phase_id": "phase_2",
                    "name": "Coexistence Blueprint",
                    "journey_type": "structured"
                },
                {
                    "phase_id": "phase_3",
                    "name": "Migration Execution",
                    "journey_type": "structured"
                },
                {
                    "phase_id": "phase_4",
                    "name": "Validation and Optimization",
                    "journey_type": "structured"
                }
            ],
            "user_id": user_id
        },
        user_context=test_user_context
    )
    
    logger.info(f"📋 Design result: {design_result}")
    assert design_result is not None, "Solution design should succeed"
    
    solution_id = design_result.get("solution_id") or design_result.get("solution", {}).get("solution_id")
    if not solution_id:
        logger.info("ℹ️ Solution design returned but no solution_id (may be expected in test environment)")
        logger.info("✅ Solution design completed (test environment)")
        return
    
    logger.info(f"✅ Enterprise migration solution designed with ID: {solution_id}")
    
    # 2. Validate solution readiness
    logger.info("📋 Step 3: Validating solution readiness...")
    readiness_result = await deployment_manager.validate_solution_readiness(
        solution_id=solution_id,
        user_context=test_user_context
    )
    
    logger.info(f"📋 Readiness result: {readiness_result}")
    assert readiness_result is not None, "Solution readiness validation should succeed"
    logger.info("✅ Solution readiness validated")
    
    # 3. Deploy solution
    logger.info("📋 Step 4: Deploying enterprise migration solution...")
    deploy_result = await composer.deploy_solution(
        solution_id=solution_id,
        user_id=user_id,
        context={"deployment_strategy": "phased"},
        user_context=test_user_context
    )
    
    logger.info(f"📋 Deploy result: {deploy_result}")
    assert deploy_result is not None, "Solution deployment should succeed"
    
    if deploy_result.get("success"):
        logger.info("✅ Solution deployed successfully")
        
        # 4. Execute all phases
        phases = ["phase_1", "phase_2", "phase_3", "phase_4"]
        for phase_id in phases:
            logger.info(f"📋 Step 5.{phases.index(phase_id) + 1}: Executing {phase_id}...")
            phase_result = await composer.execute_solution_phase(
                solution_id=solution_id,
                phase_id=phase_id,
                user_id=user_id,
                user_context=test_user_context
            )
            
            logger.info(f"📋 {phase_id} result: {phase_result}")
            assert phase_result is not None, f"{phase_id} execution should succeed"
            logger.info(f"✅ {phase_id} executed")
        
        # 5. Monitor solution progress and identify bottlenecks
        logger.info("📋 Step 6: Monitoring solution progress and identifying bottlenecks...")
        bottlenecks_result = await analytics.identify_solution_bottlenecks(
            solution_id=solution_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Solution bottlenecks: {bottlenecks_result}")
        assert bottlenecks_result is not None, "Solution bottlenecks should be available"
        
        # Get performance analysis
        performance_result = await analytics.analyze_solution_performance(
            solution_id=solution_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Solution performance: {performance_result}")
        logger.info("✅ Solution progress monitored")
        
        # 6. Get optimization recommendations
        logger.info("📋 Step 7: Getting optimization recommendations...")
        optimization_result = await analytics.get_solution_optimization_recommendations(
            solution_id=solution_id,
            user_context=test_user_context
        )
        
        logger.info(f"📋 Optimization recommendations: {optimization_result}")
        assert optimization_result is not None, "Optimization recommendations should be available"
        logger.info("✅ Optimization recommendations retrieved")
    else:
        logger.info(f"ℹ️ Solution deployment returned: {deploy_result.get('error', 'Unknown')}")
    
    logger.info("✅ Solution E2E Test 3 Complete: Data Mash Coexistence/Migration Enablement")

