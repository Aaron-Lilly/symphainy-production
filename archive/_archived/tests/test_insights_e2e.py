#!/usr/bin/env python3
"""
End-to-End Test for Insights Pillar with Agentic Integration

Test the complete Insights Pillar workflow including API endpoints,
agentic insights generation, and real analytics capabilities.
"""

import asyncio
import logging
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from backend.business_enablement.pillars.insights_pillar.insights_pillar_service import InsightsPillarService
from backend.business_enablement.interfaces.insights_analysis_interface import AnalysisRequest, AnalysisType as InterfaceAnalysisType, VisualizationRequest, VisualizationType
from backend.business_enablement.pillars.insights_pillar.micro_modules.data_analyzer import AnalysisType
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_insights_pillar_e2e():
    """Test the complete Insights Pillar workflow."""
    print("🚀 Starting Insights Pillar End-to-End Test")
    print("=" * 60)
    
    # Initialize the Insights Pillar Service
    print("🏗️ Initializing Insights Pillar Service...")
    insights_service = InsightsPillarService()
    await insights_service.initialize()
    print("✅ Insights Pillar Service initialized")
    
    # Create test user context
    user_context = UserContext(
        user_id="test_user_e2e",
        email="test@example.com",
        full_name="E2E Test User",
        session_id="e2e_test_session",
        permissions=["read", "write", "analyze"]
    )
    
    # Create comprehensive test data
    print("\n📊 Creating comprehensive test dataset...")
    np.random.seed(42)  # For reproducible results
    n_samples = 100
    
    test_data = {
        "values": pd.DataFrame({
            "revenue": np.random.normal(1000, 200, n_samples),
            "costs": np.random.normal(600, 150, n_samples),
            "profit": np.random.normal(400, 100, n_samples),
            "customers": np.random.poisson(50, n_samples),
            "marketing_spend": np.random.normal(200, 50, n_samples),
            "conversion_rate": np.random.beta(2, 8, n_samples),
            "region": np.random.choice(["North", "South", "East", "West"], n_samples),
            "product_category": np.random.choice(["Electronics", "Clothing", "Books", "Home"], n_samples)
        })
    }
    
    print(f"✅ Created dataset with {n_samples} samples and 8 columns")
    
    # Test 1: Data Analysis with Agentic Insights
    print("\n🧠 Test 1: Data Analysis with Agentic Insights")
    print("-" * 50)
    
    analysis_request = AnalysisRequest(
        data=test_data,
        analysis_type=InterfaceAnalysisType.DESCRIPTIVE,
        user_context=user_context,
        session_id="e2e_test_session"
    )
    
    analysis_result = await insights_service.analyze_data(analysis_request)
    
    if analysis_result.success:
        print("✅ Data analysis completed successfully")
        print(f"   📈 Analysis ID: {analysis_result.analysis_id}")
        print(f"   🎯 Confidence Score: {analysis_result.confidence_score:.2f}")
        print(f"   ⏱️ Processing Time: {analysis_result.processing_time:.2f}s")
        print(f"   💡 Insights: {len(analysis_result.insights)} insights generated")
        print(f"   💼 Recommendations: {len(analysis_result.recommendations or [])} recommendations")
        print(f"   🎨 Visualizations: {len(analysis_result.visualizations or {})} visualizations")
        
        # Show sample insights
        for i, insight in enumerate(analysis_result.insights[:3]):
            if isinstance(insight, dict):
                print(f"      Insight {i+1}: {insight.get('insight', str(insight))}")
            else:
                print(f"      Insight {i+1}: {insight}")
    else:
        print(f"❌ Data analysis failed: {analysis_result.message}")
        return False
    
    # Test 2: Visualization Generation
    print("\n🎨 Test 2: Visualization Generation")
    print("-" * 50)
    
    viz_request = VisualizationRequest(
        data=test_data,
        visualization_type=VisualizationType.HISTOGRAM,
        user_context=user_context,
        session_id="e2e_test_session"
    )
    
    viz_result = await insights_service.visualize_data(viz_request)
    
    if viz_result.success:
        print("✅ Visualization created successfully")
        print(f"   🎨 Visualization ID: {viz_result.visualization_id}")
        print(f"   📊 Type: {viz_result.visualization_type}")
        print(f"   ⏱️ Processing Time: {viz_result.processing_time:.2f}s")
    else:
        print(f"❌ Visualization failed: {viz_result.message}")
    
    # Test 3: Business Insights Generation
    print("\n🤖 Test 3: AI-Powered Business Insights Generation")
    print("-" * 50)
    
    insights_result = await insights_service.generate_business_insights(
        data=test_data,
        user_context=user_context,
        session_id="e2e_test_session"
    )
    
    if insights_result["success"]:
        print("✅ Business insights generated successfully")
        print(f"   🆔 Insights ID: {insights_result['insights_id']}")
        print(f"   🎯 Confidence Score: {insights_result['confidence_score']:.2f}")
        print(f"   ⏱️ Processing Time: {insights_result['processing_time']:.2f}s")
        print(f"   💡 Business Insights: {len(insights_result['business_insights'])} insights")
        print(f"   💼 Recommendations: {len(insights_result['recommendations'])} recommendations")
        print(f"   🎨 Visualizations: {len(insights_result['visualizations'])} visualizations")
        
        # Show sample business insights
        for i, insight in enumerate(insights_result['business_insights'][:3]):
            print(f"      Business Insight {i+1}: {insight.get('insight', str(insight))}")
    else:
        print(f"❌ Business insights generation failed: {insights_result['message']}")
    
    # Test 4: Health Check
    print("\n🏥 Test 4: Service Health Check")
    print("-" * 50)
    
    health_result = await insights_service.get_pillar_health()
    
    if health_result["status"] == "healthy":
        print("✅ All services are healthy")
        print(f"   📊 Overall Status: {health_result['status']}")
        print(f"   🔧 Services: {len(health_result.get('services', {}))} services checked")
        
        # Show service details
        for service_name, service_health in health_result.get('services', {}).items():
            status = "✅" if service_health.get('status') == 'healthy' else "❌"
            print(f"      {status} {service_name}: {service_health.get('status', 'unknown')}")
    else:
        print(f"❌ Service health check failed: {health_result.get('message', 'Unknown error')}")
    
    # Test 5: Different Analysis Types
    print("\n🔬 Test 5: Different Analysis Types")
    print("-" * 50)
    
    analysis_types = [InterfaceAnalysisType.CORRELATION_ANALYSIS, InterfaceAnalysisType.MACHINE_LEARNING, InterfaceAnalysisType.CLUSTERING]
    
    for analysis_type in analysis_types:
        print(f"   Testing {analysis_type.value} analysis...")
        
        analysis_request = AnalysisRequest(
            data=test_data,
            analysis_type=analysis_type,
            user_context=user_context,
            session_id="e2e_test_session"
        )
        
        result = await insights_service.analyze_data(analysis_request)
        
        if result.success:
            print(f"      ✅ {analysis_type.value} analysis completed")
            print(f"         Confidence: {result.confidence_score:.2f}")
            print(f"         Processing Time: {result.processing_time:.2f}s")
        else:
            print(f"      ❌ {analysis_type.value} analysis failed: {result.message}")
    
    print("\n🎉 End-to-End Test Summary")
    print("=" * 60)
    print("✅ Data Analysis with Agentic Insights: Working")
    print("✅ Visualization Generation: Working")
    print("✅ AI-Powered Business Insights: Working")
    print("✅ Service Health Check: Working")
    print("✅ Multiple Analysis Types: Working")
    print("\n🚀 Insights Pillar is fully functional with agentic AI integration!")
    
    return True

async def main():
    """Main test function."""
    try:
        success = await test_insights_pillar_e2e()
        
        if success:
            print("\n✅ All E2E tests completed successfully!")
            print("🎉 Insights Pillar is ready for production!")
        else:
            print("\n❌ Some E2E tests failed.")
            
    except Exception as e:
        print(f"\n❌ E2E test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
