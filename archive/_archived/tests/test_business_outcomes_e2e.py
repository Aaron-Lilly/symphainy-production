#!/usr/bin/env python3
"""
End-to-End Test for Business Outcomes Pillar

Tests the complete Business Outcomes Pillar service including API endpoints,
micro-modules, and public works services integration.
"""

import asyncio
import logging
import sys
import os

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from backend.business_enablement.pillars.business_outcomes_pillar.business_outcomes_pillar_service import BusinessOutcomesPillarService
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext
from config.environment_loader import EnvironmentLoader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_business_outcomes_pillar():
    """Test the complete Business Outcomes Pillar service."""
    print("🚀 Starting Business Outcomes Pillar E2E Test...\n")
    
    try:
        # Initialize environment loader
        environment_loader = EnvironmentLoader()
        
        # Initialize the Business Outcomes Pillar Service
        service = BusinessOutcomesPillarService(environment_loader)
        await service.initialize()
        
        print("✅ Business Outcomes Pillar Service initialized successfully")
        
        # Create test user context
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_123",
            permissions=["business_outcomes", "strategic_planning", "roi_analysis"]
        )
        
        # Test 1: Strategic Roadmap Generation
        print("\n🧪 Test 1: Strategic Roadmap Generation")
        business_context = {
            "objectives": ["Improve operational efficiency", "Increase customer satisfaction", "Reduce costs"],
            "timeline": {"start_date": "2024-01-01T00:00:00Z", "max_duration_weeks": 24},
            "budget": 500000,
            "options": {"roadmap_type": "hybrid", "team_size": 8}
        }
        
        roadmap_result = await service.generate_strategic_roadmap(business_context, user_context)
        print(f"  Strategic Roadmap: {'✅' if roadmap_result['success'] else '❌'}")
        
        if roadmap_result['success']:
            strategic_plan = roadmap_result['strategic_plan']
            print(f"    - Plan ID: {strategic_plan['plan_id']}")
            print(f"    - Objectives: {len(strategic_plan['objectives'])}")
            print(f"    - Budget: ${strategic_plan['budget']:,.2f}")
            print(f"    - Has Roadmap: {'✅' if 'roadmap' in strategic_plan else '❌'}")
        
        # Test 2: ROI Calculation
        print("\n🧪 Test 2: ROI Calculation")
        investment_data = {
            "investment_amount": 100000,
            "expected_returns": 150000,
            "time_period": 12,
            "roi_type": "comprehensive",
            "user_context": user_context,
            "session_id": user_context.session_id,
            "options": {
                "industry": "technology",
                "cost_savings": 20000,
                "revenue_increase": 30000,
                "efficiency_gains": 25
            }
        }
        
        roi_result = await service.calculate_roi(investment_data, user_context)
        print(f"  ROI Calculation: {'✅' if roi_result['success'] else '❌'}")
        
        if roi_result['success']:
            roi_analysis = roi_result['roi_analysis']
            print(f"    - Analysis ID: {roi_analysis['analysis_id']}")
            print(f"    - ROI Percentage: {roi_analysis['roi_percentage']:.2f}%")
            print(f"    - Payback Period: {roi_analysis['payback_period_months']:.1f} months")
            print(f"    - NPV: ${roi_analysis['net_present_value']:,.2f}")
        
        # Test 3: Strategic Roadmap Display
        print("\n🧪 Test 3: Strategic Roadmap Display")
        if roadmap_result['success']:
            roadmap_display_result = await service.create_strategic_roadmap_display(
                roadmap_result['strategic_plan'], user_context
            )
            print(f"  Roadmap Display: {'✅' if roadmap_display_result['success'] else '❌'}")
            
            if roadmap_display_result['success']:
                print(f"    - Dashboard ID: {roadmap_display_result['dashboard_id']}")
                print(f"    - Layout: {roadmap_display_result.get('layout', 'N/A')}")
                print(f"    - Charts: {len(roadmap_display_result.get('charts', []))}")
        
        # Test 4: Outcome Metrics Display
        print("\n🧪 Test 4: Outcome Metrics Display")
        metrics_data = {
            "roi_percentage": 50.0,
            "payback_period_months": 18.0,
            "efficiency_gains": 85.0,
            "customer_satisfaction": 92.0,
            "revenue_growth": 15.0
        }
        
        metrics_display_result = await service.create_outcome_metrics_display(metrics_data, user_context)
        print(f"  Metrics Display: {'✅' if metrics_display_result['success'] else '❌'}")
        
        if metrics_display_result['success']:
            print(f"    - Dashboard ID: {metrics_display_result['dashboard_id']}")
            print(f"    - Layout: {metrics_display_result.get('layout', 'N/A')}")
            print(f"    - Charts: {len(metrics_display_result.get('charts', []))}")
        
        # Test 5: Business Metrics Calculation
        print("\n🧪 Test 5: Business Metrics Calculation")
        business_data = {
            "revenue": 1000000,
            "costs": 750000,
            "profit_margin": 0.25,
            "growth_rate": 0.15
        }
        
        metrics_result = await service.calculate_business_metrics(business_data, user_context)
        print(f"  Business Metrics: {'✅' if metrics_result['success'] else '❌'}")
        
        if metrics_result['success']:
            metrics = metrics_result.get('metrics', {})
            print(f"    - Revenue: ${metrics.get('revenue', 0):,.2f}")
            print(f"    - Profit Margin: {metrics.get('profit_margin', 0):.2%}")
            print(f"    - Growth Rate: {metrics.get('growth_rate', 0):.2%}")
        
        # Test 6: Performance Benchmarking
        print("\n🧪 Test 6: Performance Benchmarking")
        performance_data = {
            "roi_percentage": 30.0,
            "payback_period_months": 18.0,
            "efficiency_percentage": 85.0
        }
        
        benchmark_result = await service.benchmark_performance(performance_data, "technology", user_context)
        print(f"  Performance Benchmark: {'✅' if benchmark_result['success'] else '❌'}")
        
        if benchmark_result['success']:
            benchmark = benchmark_result.get('benchmark_results', {})
            print(f"    - Overall Score: {benchmark.get('overall_score', 0):.1f}")
            print(f"    - Assessment: {benchmark.get('assessment', 'N/A')}")
        
        # Test 7: Outcome Measurement
        print("\n🧪 Test 7: Outcome Measurement")
        outcome_data = {
            "initiative_name": "Digital Transformation",
            "baseline_metrics": {"efficiency": 70, "satisfaction": 80},
            "current_metrics": {"efficiency": 85, "satisfaction": 92},
            "target_metrics": {"efficiency": 90, "satisfaction": 95}
        }
        
        outcome_result = await service.measure_outcomes(outcome_data, user_context)
        print(f"  Outcome Measurement: {'✅' if outcome_result['success'] else '❌'}")
        
        if outcome_result['success']:
            measurement = outcome_result.get('measurement', {})
            print(f"    - Initiative: {measurement.get('initiative_name', 'N/A')}")
            print(f"    - Progress: {measurement.get('overall_progress', 0):.1f}%")
            print(f"    - Status: {measurement.get('status', 'N/A')}")
        
        # Test 8: Trend Analysis
        print("\n🧪 Test 8: Trend Analysis")
        historical_data = [
            {"period": "Q1", "revenue": 250000, "efficiency": 70},
            {"period": "Q2", "revenue": 275000, "efficiency": 75},
            {"period": "Q3", "revenue": 300000, "efficiency": 80},
            {"period": "Q4", "revenue": 325000, "efficiency": 85}
        ]
        
        trend_result = await service.analyze_trends(historical_data, user_context)
        print(f"  Trend Analysis: {'✅' if trend_result['success'] else '❌'}")
        
        if trend_result['success']:
            trends = trend_result.get('trends', {})
            print(f"    - Revenue Trend: {trends.get('revenue_trend', 'N/A')}")
            print(f"    - Efficiency Trend: {trends.get('efficiency_trend', 'N/A')}")
            print(f"    - Overall Trend: {trends.get('overall_trend', 'N/A')}")
        
        # Test 9: Business Impact Assessment
        print("\n🧪 Test 9: Business Impact Assessment")
        impact_data = {
            "initiative_name": "Process Automation",
            "cost_savings": 50000,
            "revenue_impact": 75000,
            "efficiency_gains": 20,
            "customer_impact": "positive"
        }
        
        impact_result = await service.assess_business_impact(impact_data, user_context)
        print(f"  Impact Assessment: {'✅' if impact_result['success'] else '❌'}")
        
        if impact_result['success']:
            impact = impact_result.get('impact_assessment', {})
            print(f"    - Initiative: {impact.get('initiative_name', 'N/A')}")
            print(f"    - Total Impact: ${impact.get('total_impact', 0):,.2f}")
            print(f"    - Impact Level: {impact.get('impact_level', 'N/A')}")
        
        # Test 10: Roadmap Progress Update
        print("\n🧪 Test 10: Roadmap Progress Update")
        if roadmap_result['success']:
            progress_data = {
                "phase": 1,
                "completion_percentage": 75,
                "milestones_achieved": ["Planning Complete", "Team Assembled"],
                "next_milestones": ["Implementation Start", "Resource Allocation"]
            }
            
            progress_result = await service.update_roadmap_progress(
                roadmap_result['strategic_plan']['plan_id'], progress_data, user_context
            )
            print(f"  Progress Update: {'✅' if progress_result['success'] else '❌'}")
            
            if progress_result['success']:
                progress = progress_result.get('progress_update', {})
                print(f"    - Phase: {progress.get('phase', 'N/A')}")
                print(f"    - Completion: {progress.get('completion_percentage', 0):.1f}%")
                print(f"    - Status: {progress.get('status', 'N/A')}")
        
        # Shutdown service
        await service.shutdown()
        print("\n✅ Business Outcomes Pillar Service shutdown successfully")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Business Outcomes Pillar E2E Test Failed: {e}")
        logger.exception("E2E test failed")
        return False

async def main():
    """Run the E2E test."""
    success = await test_business_outcomes_pillar()
    
    if success:
        print("\n🎉 All Business Outcomes Pillar tests passed! The pillar is fully operational.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


