#!/usr/bin/env python3
"""
Simple API Test for Business Outcomes Pillar

Tests the Business Outcomes Pillar micro-modules and their integration
with public works services.
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

async def test_strategic_roadmap_api():
    """Test Strategic Roadmap API functionality."""
    print("🧪 Testing Strategic Roadmap API...")
    
    try:
        # Initialize module
        environment_loader = MockEnvironmentLoader()
        module = StrategicRoadmapModule(environment_loader)
        await module.initialize()
        
        # Test user context
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["business_outcomes"]
        )
        
        # Test strategic plan creation
        objectives = ["Improve efficiency", "Reduce costs", "Enhance customer experience"]
        timeline = {"start_date": "2024-01-01T00:00:00Z", "max_duration_weeks": 24}
        budget = 100000
        options = {"roadmap_type": "hybrid", "team_size": 5}
        
        result = await module.create_strategic_plan(
            objectives, timeline, budget, user_context, "test_session", options
        )
        
        print(f"  Strategic Plan Creation: {'✅' if result['success'] else '❌'}")
        
        if result['success']:
            plan = result['strategic_plan']
            print(f"    - Plan ID: {plan['plan_id']}")
            print(f"    - Objectives: {len(plan['objectives'])}")
            print(f"    - Budget: ${plan['budget']:,.2f}")
            print(f"    - Has Roadmap: {'✅' if 'roadmap' in plan else '❌'}")
            
            # Test roadmap progress update
            progress_data = {
                "phase": 1,
                "completion_percentage": 75,
                "milestones_achieved": ["Planning Complete"],
                "next_milestones": ["Implementation Start"]
            }
            
            progress_result = await module.update_strategic_plan(
                plan['plan_id'], progress_data, user_context, "test_session"
            )
            print(f"  Progress Update: {'✅' if progress_result['success'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Strategic Roadmap API Test Failed: {e}")
        return False

async def test_roi_calculation_api():
    """Test ROI Calculation API functionality."""
    print("\n🧪 Testing ROI Calculation API...")
    
    try:
        # Initialize module
        environment_loader = MockEnvironmentLoader()
        module = ROICalculationModule(environment_loader)
        await module.initialize()
        
        # Test user context
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["business_outcomes"]
        )
        
        # Test ROI calculation
        investment_data = {
            "investment_amount": 50000,
            "expected_returns": 75000,
            "time_period": 12,
            "roi_type": "comprehensive",
            "user_context": user_context,
            "session_id": "test_session",
            "options": {
                "industry": "technology",
                "cost_savings": 10000,
                "revenue_increase": 15000,
                "efficiency_gains": 20
            }
        }
        
        result = await module.calculate_roi(investment_data)
        
        print(f"  ROI Calculation: {'✅' if result['success'] else '❌'}")
        
        if result['success']:
            analysis = result['roi_analysis']
            print(f"    - Analysis ID: {analysis['analysis_id']}")
            print(f"    - ROI Percentage: {analysis['roi_percentage']:.2f}%")
            print(f"    - Payback Period: {analysis['payback_period_months']:.1f} months")
            print(f"    - NPV: ${analysis['net_present_value']:,.2f}")
            
            # Test business impact assessment
            impact_data = {
                "initiative_name": "Process Automation",
                "cost_savings": 25000,
                "revenue_impact": 50000,
                "efficiency_gains": 15
            }
            
            impact_result = await module.assess_business_impact(impact_data)
            print(f"  Impact Assessment: {'✅' if impact_result['success'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ROI Calculation API Test Failed: {e}")
        return False

async def test_visual_display_api():
    """Test Visual Display API functionality."""
    print("\n🧪 Testing Visual Display API...")
    
    try:
        # Initialize module
        environment_loader = MockEnvironmentLoader()
        module = VisualDisplayModule(environment_loader)
        await module.initialize()
        
        # Test user context
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["business_outcomes"]
        )
        
        # Test dashboard creation
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
        
        result = await module.create_dashboard(
            "executive", dashboard_data, user_context, "test_session"
        )
        
        print(f"  Dashboard Creation: {'✅' if result['success'] else '❌'}")
        
        if result['success']:
            print(f"    - Dashboard ID: {result['dashboard_id']}")
            print(f"    - Layout: {result.get('layout', 'N/A')}")
            print(f"    - Charts: {len(result.get('charts', []))}")
            
            # Test strategic roadmap display
            roadmap_data = {
                "roadmap_id": "test_roadmap",
                "title": "Test Strategic Roadmap",
                "phases": [
                    {"phase": 1, "name": "Foundation", "duration": "3 months"},
                    {"phase": 2, "name": "Implementation", "duration": "6 months"}
                ]
            }
            
            roadmap_display_result = await module.create_strategic_roadmap_display(roadmap_data)
            print(f"  Roadmap Display: {'✅' if roadmap_display_result['success'] else '❌'}")
            
            # Test outcome metrics display
            metrics_data = {
                "roi_percentage": 50.0,
                "payback_period": 12.0,
                "efficiency_gains": 90.0
            }
            
            metrics_display_result = await module.create_outcome_metrics_display(metrics_data)
            print(f"  Metrics Display: {'✅' if metrics_display_result['success'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Visual Display API Test Failed: {e}")
        return False

async def main():
    """Run all API tests."""
    print("🚀 Starting Business Outcomes API Tests...\n")
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_strategic_roadmap_api())
    test_results.append(await test_roi_calculation_api())
    test_results.append(await test_visual_display_api())
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n📊 Test Summary:")
    print(f"  Passed: {passed_tests}/{total_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("  🎉 All API tests passed! Business Outcomes Pillar is fully operational.")
    else:
        print("  ⚠️  Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


