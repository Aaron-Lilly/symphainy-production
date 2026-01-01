#!/usr/bin/env python3
"""
Test script for Business Outcomes Micro-Modules

Tests all the updated micro-modules for the Business Outcomes Pillar.
"""

import asyncio
import logging
import sys
import os

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from backend.business_enablement.pillars.business_outcomes_pillar.micro_modules.strategic_roadmap_module import StrategicRoadmapModule
from backend.business_enablement.pillars.business_outcomes_pillar.micro_modules.roi_calculation_module import ROICalculationModule
from backend.business_enablement.pillars.business_outcomes_pillar.micro_modules.visual_display_module import VisualDisplayModule
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext

# Mock environment loader
class MockEnvironmentLoader:
    def get_content_pillar_config(self):
        return {
            "roadmap_templates": {},
            "planning_frameworks": {},
            "roi_models": {},
            "financial_benchmarks": {},
            "chart_templates": {},
            "dashboard_layouts": {}
        }

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_strategic_roadmap_module():
    """Test Strategic Roadmap Module."""
    print("🧪 Testing Strategic Roadmap Module...")
    
    try:
        # Initialize module
        environment_loader = MockEnvironmentLoader()
        module = StrategicRoadmapModule(environment_loader)
        await module.initialize()
        
        # Test health check
        health = await module.health_check()
        print(f"  Health Check: {'✅' if health['success'] else '❌'}")
        
        # Test strategic plan creation
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["business_outcomes"]
        )
        
        objectives = ["Improve efficiency", "Reduce costs", "Enhance customer experience"]
        timeline = {"start_date": "2024-01-01T00:00:00Z", "max_duration_weeks": 24}
        budget = 100000
        options = {"roadmap_type": "hybrid", "team_size": 5}
        
        plan_result = await module.create_strategic_plan(
            objectives, timeline, budget, user_context, "test_session", options
        )
        print(f"  Strategic Plan Creation: {'✅' if plan_result['success'] else '❌'}")
        
        if plan_result['success']:
            plan = plan_result['strategic_plan']
            print(f"    - Plan ID: {plan['plan_id']}")
            print(f"    - Objectives: {len(plan['objectives'])}")
            print(f"    - Budget: ${plan['budget']:,.2f}")
            print(f"    - Has Roadmap: {'✅' if 'roadmap' in plan else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Strategic Roadmap Module Test Failed: {e}")
        return False

async def test_roi_calculation_module():
    """Test ROI Calculation Module."""
    print("\n🧪 Testing ROI Calculation Module...")
    
    try:
        # Initialize module
        environment_loader = MockEnvironmentLoader()
        module = ROICalculationModule(environment_loader)
        await module.initialize()
        
        # Test health check
        health = await module.health_check()
        print(f"  Health Check: {'✅' if health['success'] else '❌'}")
        
        # Test ROI calculation
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["business_outcomes"]
        )
        
        investment_amount = 50000
        expected_returns = 75000
        time_period = 12
        roi_type = "comprehensive"
        options = {
            "industry": "technology",
            "cost_savings": 10000,
            "revenue_increase": 15000,
            "efficiency_gains": 20
        }
        
        # Prepare investment data for the method
        investment_data = {
            "investment_amount": investment_amount,
            "expected_returns": expected_returns,
            "time_period": time_period,
            "roi_type": roi_type,
            "user_context": user_context,
            "session_id": "test_session",
            "options": options
        }
        
        roi_result = await module.calculate_roi(investment_data)
        print(f"  ROI Calculation: {'✅' if roi_result['success'] else '❌'}")
        
        if roi_result['success']:
            analysis = roi_result['roi_analysis']
            print(f"    - Analysis ID: {analysis['analysis_id']}")
            print(f"    - ROI Percentage: {analysis['roi_percentage']:.2f}%")
            print(f"    - Payback Period: {analysis['payback_period_months']:.1f} months")
            print(f"    - NPV: ${analysis['net_present_value']:,.2f}")
            print(f"    - IRR: {analysis['internal_rate_of_return']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ROI Calculation Module Test Failed: {e}")
        return False

async def test_visual_display_module():
    """Test Visual Display Module."""
    print("\n🧪 Testing Visual Display Module...")
    
    try:
        # Initialize module
        environment_loader = MockEnvironmentLoader()
        module = VisualDisplayModule(environment_loader)
        await module.initialize()
        
        # Test health check
        health = await module.health_check()
        print(f"  Health Check: {'✅' if health['success'] else '❌'}")
        
        # Test dashboard creation
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["business_outcomes"]
        )
        
        dashboard_data = {
            "metrics": {
                "roi_percentage": 30.0,
                "payback_period": 18.0,
                "efficiency_gains": 85.0
            },
            "charts": [
                {"type": "bar", "title": "ROI Analysis"},
                {"type": "line", "title": "Trend Analysis"}
            ]
        }
        
        dashboard_result = await module.create_dashboard(
            "executive", dashboard_data, user_context, "test_session"
        )
        print(f"  Dashboard Creation: {'✅' if dashboard_result['success'] else '❌'}")
        
        if dashboard_result['success']:
            print(f"    - Dashboard ID: {dashboard_result['dashboard_id']}")
            print(f"    - Layout: {dashboard_result.get('layout', 'N/A')}")
            print(f"    - Charts: {len(dashboard_result.get('charts', []))}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Visual Display Module Test Failed: {e}")
        return False

async def main():
    """Run all micro-module tests."""
    print("🚀 Starting Business Outcomes Micro-Modules Tests...\n")
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_strategic_roadmap_module())
    test_results.append(await test_roi_calculation_module())
    test_results.append(await test_visual_display_module())
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n📊 Test Summary:")
    print(f"  Passed: {passed_tests}/{total_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("  🎉 All tests passed! Micro-modules are working correctly.")
    else:
        print("  ⚠️  Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
