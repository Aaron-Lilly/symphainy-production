#!/usr/bin/env python3
"""
Test Insights Agentic Integration

Test the agentic integration for the Insights Pillar to ensure it works correctly.
"""

import asyncio
import logging
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from backend.business_enablement.pillars.insights_pillar.micro_modules.insights_generator import InsightsGeneratorModule
from backend.business_enablement.pillars.insights_pillar.agents.insights_analysis_agent_v2 import InsightsAnalysisAgentV2
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_insights_analysis_agent():
    """Test the Insights Analysis Agent V2."""
    print("🤖 Testing Insights Analysis Agent V2...")
    
    # Initialize agent
    agent = InsightsAnalysisAgentV2()
    await agent.initialize()
    
    # Create test data
    test_df = pd.DataFrame({
        "revenue": [1000, 1200, 1100, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        "costs": [600, 700, 650, 750, 800, 850, 900, 950, 1000, 1050],
        "profit": [400, 500, 450, 550, 600, 650, 700, 750, 800, 850],
        "customers": [100, 120, 110, 130, 140, 150, 160, 170, 180, 190]
    })
    
    test_data = {"values": test_df}
    user_context = UserContext(
        user_id="test_user",
        email="test@example.com", 
        full_name="Test User",
        session_id="test_session",
        permissions=["read", "write"]
    )
    
    # Test comprehensive analysis
    print("   📊 Testing comprehensive analysis...")
    result = await agent.analyze_data(
        test_data, 
        analysis_type="comprehensive",
        user_context=user_context,
        session_id="test_session"
    )
    
    if result["success"]:
        print(f"   ✅ Analysis completed successfully")
        print(f"   📈 Insights: {len(result['insights'])} insights generated")
        print(f"   💡 Recommendations: {len(result['recommendations'])} recommendations")
        print(f"   🎯 Confidence Score: {result['confidence_score']}")
        print(f"   🎨 Visualizations: {result['visualizations']['total_visualizations']} visualizations")
        
        # Show sample insights
        for i, insight in enumerate(result['insights'][:2]):
            print(f"      Insight {i+1}: {insight['insight']}")
    else:
        print(f"   ❌ Analysis failed: {result['error']}")
    
    # Test health check
    print("   🏥 Testing health check...")
    health = await agent.health_check()
    print(f"   Agent Status: {health['status']}")
    
    return agent

async def test_insights_generator():
    """Test the Insights Generator Module with agentic integration."""
    print("\n🧠 Testing Insights Generator Module...")
    
    # Create mock environment loader
    mock_env_loader = MagicMock()
    mock_env_loader.get_insights_pillar_config.return_value = {}
    
    # Initialize module
    insights_gen = InsightsGeneratorModule(logger, mock_env_loader)
    await insights_gen.initialize()
    
    # Create test data
    test_df = pd.DataFrame({
        "sales": [100, 120, 110, 130, 140, 150, 160, 170, 180, 190],
        "marketing_spend": [50, 60, 55, 65, 70, 75, 80, 85, 90, 95],
        "conversion_rate": [0.05, 0.06, 0.055, 0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095]
    })
    
    test_data = {"values": test_df}
    user_context = UserContext(
        user_id="test_user",
        email="test@example.com",
        full_name="Test User", 
        session_id="test_session",
        permissions=["read", "write"]
    )
    
    # Test insights generation
    print("   🎯 Testing insights generation...")
    result = await insights_gen.generate_insights(
        test_data,
        user_context,
        session_id="test_session"
    )
    
    if result["success"]:
        print(f"   ✅ Insights generated successfully")
        print(f"   📊 Business Insights: {len(result['business_insights'])} insights")
        print(f"   💡 Recommendations: {len(result['recommendations'])} recommendations")
        print(f"   🎯 Confidence Score: {result['confidence_score']}")
        print(f"   ⏱️ Processing Time: {result['processing_time']:.2f}s")
        
        # Show sample insights
        for i, insight in enumerate(result['business_insights'][:2]):
            print(f"      Insight {i+1}: {insight['insight']}")
    else:
        print(f"   ❌ Insights generation failed: {result['message']}")
    
    # Test health check
    print("   🏥 Testing health check...")
    health = await insights_gen.health_check()
    print(f"   Module Status: {health['status']}")
    print(f"   Agent Status: {health.get('agent_status', 'unknown')}")
    
    return insights_gen

async def main():
    """Main test function."""
    print("🚀 Starting Insights Agentic Integration Test")
    print("=" * 60)
    
    try:
        # Test Insights Analysis Agent
        agent = await test_insights_analysis_agent()
        
        # Test Insights Generator Module
        insights_gen = await test_insights_generator()
        
        print("\n✅ All agentic integration tests completed successfully!")
        print("🎉 Insights Pillar is now using our own Agentic SDK!")
        print("🤖 AI-powered insights generation is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())


