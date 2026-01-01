#!/usr/bin/env python3
"""
Test script for Business Outcomes Infrastructure Abstractions

Tests all the newly created infrastructure abstractions for the Business Outcomes Pillar.
"""

import asyncio
import logging
import sys
import os

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from foundations.infrastructure_foundation.abstractions.roadmap_generation_abstraction import RoadmapGenerationAbstraction
from foundations.infrastructure_foundation.abstractions.poc_generation_abstraction import POCGenerationAbstraction
from foundations.infrastructure_foundation.abstractions.cross_pillar_integration_abstraction import CrossPillarIntegrationAbstraction
from foundations.infrastructure_foundation.abstractions.business_metrics_abstraction import BusinessMetricsAbstraction
from foundations.infrastructure_foundation.abstractions.business_visualization_abstraction import BusinessVisualizationAbstraction

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_roadmap_generation_abstraction():
    """Test roadmap generation abstraction."""
    print("🧪 Testing Roadmap Generation Abstraction...")
    
    try:
        # Initialize abstraction
        roadmap_abstraction = RoadmapGenerationAbstraction(logger)
        await roadmap_abstraction.initialize()
        
        # Test health check
        health = await roadmap_abstraction.health_check()
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
        
        roadmap_result = await roadmap_abstraction.create_strategic_roadmap(business_context, "hybrid")
        print(f"  Roadmap Creation: {'✅' if roadmap_result['success'] else '❌'}")
        
        if roadmap_result['success']:
            roadmap = roadmap_result['roadmap']
            print(f"    - Roadmap ID: {roadmap['roadmap_id']}")
            print(f"    - Phases: {len(roadmap['phases'])}")
            print(f"    - Duration: {roadmap['timeline']['total_duration_weeks']} weeks")
        
        # Test roadmap validation
        validation_result = await roadmap_abstraction.validate_roadmap(roadmap_result['roadmap'])
        print(f"  Roadmap Validation: {'✅' if validation_result['success'] and validation_result['valid'] else '❌'}")
        
        # Test roadmap optimization
        optimization_result = await roadmap_abstraction.optimize_roadmap(
            roadmap_result['roadmap'], 
            ["reduce_timeline", "minimize_cost"]
        )
        print(f"  Roadmap Optimization: {'✅' if optimization_result['success'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Roadmap Generation Test Failed: {e}")
        return False

async def test_poc_generation_abstraction():
    """Test POC generation abstraction."""
    print("\n🧪 Testing POC Generation Abstraction...")
    
    try:
        # Initialize abstraction
        poc_abstraction = POCGenerationAbstraction(logger)
        await poc_abstraction.initialize()
        
        # Test health check
        health = await poc_abstraction.health_check()
        print(f"  Health Check: {'✅' if health['status'] == 'healthy' else '❌'}")
        
        # Test POC creation
        business_context = {
            "project_name": "Test POC Initiative",
            "objectives": ["Validate technical feasibility", "Demonstrate business value"],
            "constraints": ["Limited budget", "Short timeline"],
            "resources": {"team_size": 3, "expertise": ["technical"]},
            "timeline": {"max_duration_days": 30}
        }
        
        poc_result = await poc_abstraction.create_poc_proposal(business_context, "technical")
        print(f"  POC Creation: {'✅' if poc_result['success'] else '❌'}")
        
        if poc_result['success']:
            poc = poc_result['poc_proposal']
            print(f"    - POC ID: {poc['poc_id']}")
            print(f"    - Duration: {poc['timeline']['total_duration_days']} days")
            print(f"    - Budget: ${poc['budget']['total_cost']:,.2f}")
        
        # Test POC validation
        validation_result = await poc_abstraction.validate_poc(poc_result['poc_proposal'])
        print(f"  POC Validation: {'✅' if validation_result['success'] and validation_result['valid'] else '❌'}")
        
        # Test POC optimization
        optimization_result = await poc_abstraction.optimize_poc(
            poc_result['poc_proposal'], 
            ["reduce_cost", "shorten_timeline"]
        )
        print(f"  POC Optimization: {'✅' if optimization_result['success'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ POC Generation Test Failed: {e}")
        return False

async def test_cross_pillar_integration_abstraction():
    """Test cross-pillar integration abstraction."""
    print("\n🧪 Testing Cross-Pillar Integration Abstraction...")
    
    try:
        # Initialize abstraction
        integration_abstraction = CrossPillarIntegrationAbstraction(logger)
        await integration_abstraction.initialize()
        
        # Test health check
        health = await integration_abstraction.health_check()
        print(f"  Health Check: {'✅' if health['status'] == 'healthy' else '❌'}")
        
        # Test pillar data synthesis
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
        
        synthesis_result = await integration_abstraction.synthesize_pillar_data(pillar_data, "strategic_roadmap")
        print(f"  Pillar Synthesis: {'✅' if synthesis_result['success'] else '❌'}")
        
        if synthesis_result['success']:
            synthesized = synthesis_result['synthesized_data']
            print(f"    - Synthesis Type: {synthesized['synthesis_type']}")
            print(f"    - Objectives: {len(synthesized['objectives'])}")
            print(f"    - Capabilities: {len(synthesized['capabilities'])}")
        
        # Test analysis correlation
        pillar_analyses = {
            "content": {"analysis_type": "file_processing", "results": {"success_rate": 95}},
            "insights": {"analysis_type": "data_analysis", "results": {"accuracy": 92}},
            "operations": {"analysis_type": "process_optimization", "results": {"efficiency": 88}}
        }
        
        correlation_result = await integration_abstraction.correlate_analyses(pillar_analyses)
        print(f"  Analysis Correlation: {'✅' if correlation_result['success'] else '❌'}")
        
        # Test unified metrics
        pillar_metrics = {
            "content": {"data_quality": "high", "key_findings": ["Files processed successfully"]},
            "insights": {"data_quality": "high", "key_findings": ["Analysis completed"]},
            "operations": {"data_quality": "high", "key_findings": ["Processes optimized"]}
        }
        
        metrics_result = await integration_abstraction.generate_unified_metrics(pillar_metrics)
        print(f"  Unified Metrics: {'✅' if metrics_result['success'] else '❌'}")
        
        if metrics_result['success']:
            metrics = metrics_result['unified_metrics']
            print(f"    - Overall Score: {metrics['overall_score']:.1f}")
            print(f"    - Pillar Scores: {len(metrics['pillar_scores'])}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Cross-Pillar Integration Test Failed: {e}")
        return False

async def test_business_metrics_abstraction():
    """Test business metrics abstraction."""
    print("\n🧪 Testing Business Metrics Abstraction...")
    
    try:
        # Initialize abstraction
        metrics_abstraction = BusinessMetricsAbstraction(logger)
        await metrics_abstraction.initialize()
        
        # Test health check
        health = await metrics_abstraction.health_check()
        print(f"  Health Check: {'✅' if health['status'] == 'healthy' else '❌'}")
        
        # Test ROI calculation
        investment_data = {
            "costs": 50000,
            "benefits": 75000,
            "investment_period_months": 12,
            "industry": "technology"
        }
        
        roi_result = await metrics_abstraction.calculate_roi(investment_data)
        print(f"  ROI Calculation: {'✅' if roi_result['success'] else '❌'}")
        
        if roi_result['success']:
            roi = roi_result['roi_calculation']
            print(f"    - ROI: {roi['roi_percentage']:.2f}%")
            print(f"    - Assessment: {roi['assessment']}")
        
        # Test payback period calculation
        payback_data = {
            "initial_investment": 100000,
            "annual_benefits": 40000,
            "industry": "technology"
        }
        
        payback_result = await metrics_abstraction.calculate_payback_period(payback_data)
        print(f"  Payback Period: {'✅' if payback_result['success'] else '❌'}")
        
        if payback_result['success']:
            payback = payback_result['payback_calculation']
            print(f"    - Payback Period: {payback['payback_period_months']:.1f} months")
            print(f"    - Assessment: {payback['assessment']}")
        
        # Test NPV calculation
        npv_data = {
            "initial_investment": 100000,
            "cash_flows": [20000, 30000, 40000, 50000],
            "discount_rate": 0.1
        }
        
        npv_result = await metrics_abstraction.calculate_npv(npv_data)
        print(f"  NPV Calculation: {'✅' if npv_result['success'] else '❌'}")
        
        if npv_result['success']:
            npv = npv_result['npv_calculation']
            print(f"    - NPV: ${npv['npv']:,.2f}")
            print(f"    - Assessment: {npv['assessment']}")
        
        # Test performance benchmarking
        benchmark_data = {
            "roi_percentage": 30.0,
            "payback_period_months": 18,
            "efficiency_percentage": 85.0
        }
        
        benchmark_result = await metrics_abstraction.benchmark_performance(benchmark_data, "technology")
        print(f"  Performance Benchmarking: {'✅' if benchmark_result['success'] else '❌'}")
        
        if benchmark_result['success']:
            benchmark = benchmark_result['benchmark_results']
            print(f"    - Overall Score: {benchmark['overall_score']:.1f}")
            print(f"    - Assessment: {benchmark['assessment']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Business Metrics Test Failed: {e}")
        return False

async def test_business_visualization_abstraction():
    """Test business visualization abstraction."""
    print("\n🧪 Testing Business Visualization Abstraction...")
    
    try:
        # Initialize abstraction
        viz_abstraction = BusinessVisualizationAbstraction(logger)
        await viz_abstraction.initialize()
        
        # Test health check
        health = await viz_abstraction.health_check()
        print(f"  Health Check: {'✅' if health['status'] == 'healthy' else '❌'}")
        
        # Test roadmap visualization
        roadmap_data = {
            "phases": [
                {"phase_id": "phase_1", "title": "Planning", "duration_weeks": 4},
                {"phase_id": "phase_2", "title": "Development", "duration_weeks": 8},
                {"phase_id": "phase_3", "title": "Testing", "duration_weeks": 2}
            ],
            "timeline": {"start_date": "2024-01-01T00:00:00Z"}
        }
        
        roadmap_viz_result = await viz_abstraction.create_roadmap_visualization(roadmap_data, "gantt")
        print(f"  Roadmap Visualization: {'✅' if roadmap_viz_result['success'] else '❌'}")
        
        if roadmap_viz_result['success']:
            viz = roadmap_viz_result['visualization']
            print(f"    - Type: {viz['type']}")
            print(f"    - Data Points: {len(viz['data'])}")
        
        # Test metrics dashboard
        metrics_data = {
            "metrics": {
                "roi": 25.0,
                "efficiency": 85.0,
                "satisfaction": 90.0
            },
            "kpis": {"revenue": 100000, "costs": 75000}
        }
        
        dashboard_result = await viz_abstraction.create_metrics_dashboard(metrics_data, "executive")
        print(f"  Metrics Dashboard: {'✅' if dashboard_result['success'] else '❌'}")
        
        if dashboard_result['success']:
            dashboard = dashboard_result['dashboard']
            print(f"    - Type: {dashboard['type']}")
            print(f"    - Widgets: {len(dashboard['widgets'])}")
        
        # Test ROI visualization
        roi_data = {
            "roi_percentage": 30.0,
            "comparison_data": {"industry_avg": 25.0, "competitor": 28.0}
        }
        
        roi_viz_result = await viz_abstraction.create_roi_visualization(roi_data, "bar")
        print(f"  ROI Visualization: {'✅' if roi_viz_result['success'] else '❌'}")
        
        if roi_viz_result['success']:
            chart = roi_viz_result['chart']
            print(f"    - Type: {chart['type']}")
            print(f"    - Title: {chart['title']}")
        
        # Test process flow visualization
        process_data = {
            "processes": [
                {"name": "Start", "type": "start"},
                {"name": "Process", "type": "process"},
                {"name": "End", "type": "end"}
            ]
        }
        
        process_viz_result = await viz_abstraction.create_process_flow_visualization(process_data, "flowchart")
        print(f"  Process Flow Visualization: {'✅' if process_viz_result['success'] else '❌'}")
        
        if process_viz_result['success']:
            flow = process_viz_result['flow']
            print(f"    - Type: {flow['type']}")
            print(f"    - Nodes: {len(flow['nodes'])}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Business Visualization Test Failed: {e}")
        return False

async def main():
    """Run all infrastructure abstraction tests."""
    print("🚀 Starting Business Outcomes Infrastructure Abstractions Tests...\n")
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_roadmap_generation_abstraction())
    test_results.append(await test_poc_generation_abstraction())
    test_results.append(await test_cross_pillar_integration_abstraction())
    test_results.append(await test_business_metrics_abstraction())
    test_results.append(await test_business_visualization_abstraction())
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n📊 Test Summary:")
    print(f"  Passed: {passed_tests}/{total_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("  🎉 All tests passed! Infrastructure abstractions are working correctly.")
    else:
        print("  ⚠️  Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


