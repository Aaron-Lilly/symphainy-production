#!/usr/bin/env python3
"""
Test script for Business Outcomes Public Works Services

Tests all the newly created public works services for the Business Outcomes Pillar.
"""

import asyncio
import logging
import sys
import os

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# from foundations.public_works_foundation.services.strategic_planning_service import StrategicPlanningService
# from foundations.public_works_foundation.services.poc_management_service import POCManagementService
# from foundations.public_works_foundation.services.business_metrics_service import BusinessMetricsService
# from foundations.public_works_foundation.services.cross_pillar_synthesis_service import CrossPillarSynthesisService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_strategic_planning_service():
    """Test Strategic Planning Service."""
    print("🧪 Testing Strategic Planning Service...")
    
    try:
        # Initialize service
        service = StrategicPlanningService(logger)
        await service.initialize()
        
        # Test health check
        health = await service.health_check()
        print(f"  Health Check: {'✅' if health['status'] == 'healthy' else '❌'}")
        
        # Test roadmap creation
        business_context = {
            "project_name": "Test Strategic Initiative",
            "objectives": ["Improve efficiency", "Reduce costs", "Enhance customer experience"],
            "timeline": {"start_date": "2024-01-01T00:00:00Z", "max_duration_weeks": 24},
            "budget": 100000,
            "resources": {"team_size": 5, "expertise": ["technical", "business"]},
            "constraints": ["Budget limitations", "Timeline constraints"]
        }
        
        roadmap_result = await service.create_strategic_roadmap(business_context, "hybrid")
        print(f"  Roadmap Creation: {'✅' if roadmap_result['success'] else '❌'}")
        
        if roadmap_result['success']:
            roadmap = roadmap_result['roadmap']
            print(f"    - Roadmap ID: {roadmap['roadmap_id']}")
            print(f"    - Phases: {len(roadmap['phases'])}")
            print(f"    - Duration: {roadmap['timeline']['total_duration_weeks']} weeks")
        
        # Test roadmap optimization
        optimization_result = await service.optimize_strategic_roadmap(
            roadmap_result['roadmap'], 
            ["reduce_timeline", "minimize_cost"]
        )
        print(f"  Roadmap Optimization: {'✅' if optimization_result['success'] else '❌'}")
        
        # Test cross-pillar synthesis
        pillar_data = {
            "content": {
                "files": [{"file_type": "pdf", "status": "parsed"}],
                "metadata": {"total_files": 5, "processed": 5}
            },
            "insights": {
                "analysis_results": [{"type": "descriptive", "status": "completed"}],
                "visualizations": [{"type": "chart", "status": "generated"}]
            },
            "operations": {
                "workflows": [{"name": "test_workflow", "status": "optimized"}],
                "sops": [{"name": "test_sop", "status": "validated"}]
            }
        }
        
        synthesis_result = await service.synthesize_cross_pillar_roadmap(pillar_data)
        print(f"  Cross-Pillar Synthesis: {'✅' if synthesis_result['success'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Strategic Planning Service Test Failed: {e}")
        return False

async def test_poc_management_service():
    """Test POC Management Service."""
    print("\n🧪 Testing POC Management Service...")
    
    try:
        # Initialize service
        service = POCManagementService(logger)
        await service.initialize()
        
        # Test health check
        health = await service.health_check()
        print(f"  Health Check: {'✅' if health['status'] == 'healthy' else '❌'}")
        
        # Test POC creation
        business_context = {
            "project_name": "Test POC Initiative",
            "objectives": ["Validate technical feasibility", "Demonstrate business value"],
            "constraints": ["Limited budget", "Short timeline"],
            "resources": {"team_size": 3, "expertise": ["technical"]},
            "timeline": {"max_duration_days": 30}
        }
        
        poc_result = await service.create_poc_proposal(business_context, "technical")
        print(f"  POC Creation: {'✅' if poc_result['success'] else '❌'}")
        
        if poc_result['success']:
            poc = poc_result['poc_proposal']
            print(f"    - POC ID: {poc['poc_id']}")
            print(f"    - Duration: {poc['timeline']['total_duration_days']} days")
            print(f"    - Budget: ${poc['budget']['total_cost']:,.2f}")
        
        # Test POC optimization
        optimization_result = await service.optimize_poc_proposal(
            poc_result['poc_proposal'], 
            ["reduce_cost", "shorten_timeline"]
        )
        print(f"  POC Optimization: {'✅' if optimization_result['success'] else '❌'}")
        
        # Test cross-pillar synthesis
        pillar_data = {
            "content": {
                "files": [{"file_type": "pdf", "status": "parsed"}],
                "metadata": {"total_files": 3, "processed": 3}
            },
            "insights": {
                "analysis_results": [{"type": "predictive", "status": "completed"}],
                "visualizations": [{"type": "dashboard", "status": "generated"}]
            }
        }
        
        synthesis_result = await service.synthesize_cross_pillar_poc(pillar_data)
        print(f"  Cross-Pillar Synthesis: {'✅' if synthesis_result['success'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ POC Management Service Test Failed: {e}")
        return False

async def test_business_metrics_service():
    """Test Business Metrics Service."""
    print("\n🧪 Testing Business Metrics Service...")
    
    try:
        # Initialize service
        service = BusinessMetricsService(logger)
        await service.initialize()
        
        # Test health check
        health = await service.health_check()
        print(f"  Health Check: {'✅' if health['status'] == 'healthy' else '❌'}")
        
        # Test comprehensive ROI calculation
        investment_data = {
            "costs": 50000,
            "benefits": 75000,
            "investment_period_months": 12,
            "industry": "technology",
            "cost_savings": 10000,
            "revenue_increase": 15000,
            "efficiency_gains": 20,
            "quality_improvements": 15,
            "customer_satisfaction": 85
        }
        
        roi_result = await service.calculate_comprehensive_roi(investment_data)
        print(f"  Comprehensive ROI: {'✅' if roi_result['success'] else '❌'}")
        
        if roi_result['success']:
            analysis = roi_result['comprehensive_analysis']
            print(f"    - ROI: {analysis['roi_analysis']['roi_percentage']:.2f}%")
            print(f"    - Payback: {analysis['payback_analysis']['payback_period_months']:.1f} months")
            print(f"    - NPV: ${analysis['npv_analysis']['npv']:,.2f}")
            print(f"    - Overall Score: {analysis['overall_assessment']['overall_score']:.1f}")
        
        # Test performance benchmarking
        metrics_data = {
            "roi_percentage": 30.0,
            "payback_period_months": 18,
            "efficiency_percentage": 85.0
        }
        
        benchmark_result = await service.benchmark_performance(metrics_data, "technology")
        print(f"  Performance Benchmarking: {'✅' if benchmark_result['success'] else '❌'}")
        
        if benchmark_result['success']:
            benchmark = benchmark_result['benchmark_results']
            print(f"    - Overall Score: {benchmark['overall_score']:.1f}")
            print(f"    - Assessment: {benchmark['assessment']}")
        
        # Test cross-pillar metrics synthesis
        pillar_metrics = {
            "content": {"data_quality": "high", "key_findings": ["Files processed successfully"]},
            "insights": {"data_quality": "high", "key_findings": ["Analysis completed"]},
            "operations": {"data_quality": "high", "key_findings": ["Processes optimized"]}
        }
        
        synthesis_result = await service.synthesize_cross_pillar_metrics(pillar_metrics)
        print(f"  Cross-Pillar Metrics: {'✅' if synthesis_result['success'] else '❌'}")
        
        if synthesis_result['success']:
            metrics = synthesis_result['unified_metrics']
            print(f"    - Overall Score: {metrics['overall_score']:.1f}")
            print(f"    - Pillar Scores: {len(metrics['pillar_scores'])}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Business Metrics Service Test Failed: {e}")
        return False

async def test_cross_pillar_synthesis_service():
    """Test Cross-Pillar Synthesis Service."""
    print("\n🧪 Testing Cross-Pillar Synthesis Service...")
    
    try:
        # Initialize service
        service = CrossPillarSynthesisService(logger)
        await service.initialize()
        
        # Test health check
        health = await service.health_check()
        print(f"  Health Check: {'✅' if health['status'] == 'healthy' else '❌'}")
        
        # Test strategic roadmap synthesis
        pillar_data = {
            "content": {
                "files": [{"file_type": "pdf", "status": "parsed"}],
                "metadata": {"total_files": 5, "processed": 5}
            },
            "insights": {
                "analysis_results": [{"type": "descriptive", "status": "completed"}],
                "visualizations": [{"type": "chart", "status": "generated"}]
            },
            "operations": {
                "workflows": [{"name": "test_workflow", "status": "optimized"}],
                "sops": [{"name": "test_sop", "status": "validated"}]
            }
        }
        
        roadmap_result = await service.synthesize_strategic_roadmap(pillar_data)
        print(f"  Strategic Roadmap Synthesis: {'✅' if roadmap_result['success'] else '❌'}")
        
        # Test POC proposal synthesis
        poc_result = await service.synthesize_poc_proposal(pillar_data)
        print(f"  POC Proposal Synthesis: {'✅' if poc_result['success'] else '❌'}")
        
        # Test pillar analysis correlation
        pillar_analyses = {
            "content": {"analysis_type": "file_processing", "results": {"success_rate": 95}},
            "insights": {"analysis_type": "data_analysis", "results": {"accuracy": 92}},
            "operations": {"analysis_type": "process_optimization", "results": {"efficiency": 88}}
        }
        
        correlation_result = await service.correlate_pillar_analyses(pillar_analyses)
        print(f"  Analysis Correlation: {'✅' if correlation_result['success'] else '❌'}")
        
        if correlation_result['success']:
            correlation = correlation_result['correlation_results']
            print(f"    - Correlations: {len(correlation['correlations'])}")
            print(f"    - Patterns: {len(correlation['patterns'])}")
        
        # Test unified insights generation
        insights_result = await service.generate_unified_insights(pillar_data)
        print(f"  Unified Insights: {'✅' if insights_result['success'] else '❌'}")
        
        if insights_result['success']:
            insights = insights_result['unified_insights']
            print(f"    - Recommendations: {len(insights['unified_recommendations'])}")
            print(f"    - Priorities: {len(insights['strategic_priorities'])}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Cross-Pillar Synthesis Service Test Failed: {e}")
        return False

async def main():
    """Run all public works service tests."""
    print("🚀 Starting Business Outcomes Public Works Services Tests...\n")
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_strategic_planning_service())
    test_results.append(await test_poc_management_service())
    test_results.append(await test_business_metrics_service())
    test_results.append(await test_cross_pillar_synthesis_service())
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n📊 Test Summary:")
    print(f"  Passed: {passed_tests}/{total_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("  🎉 All tests passed! Public works services are working correctly.")
    else:
        print("  ⚠️  Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


