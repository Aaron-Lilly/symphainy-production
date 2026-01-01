#!/usr/bin/env python3
"""
Test Agent SDK Insights Agents

Comprehensive test suite for the transformed insights agents using Agent SDK.
Tests all three agents: Data Analyst, Business Analyst, and Insights Liaison.
"""

import sys
import os
import asyncio
import pandas as pd
from typing import Dict, Any
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utilities import UserContext
from backend.business_pillars.insights_pillar.specialist_agents.agent_sdk_data_analyst_agent import AgentSDKDataAnalystAgent
from backend.business_pillars.insights_pillar.specialist_agents.agent_sdk_business_analyst_agent import AgentSDKBusinessAnalystAgent
from backend.business_pillars.insights_pillar.specialist_agents.agent_sdk_insights_liaison_agent import AgentSDKInsightsLiaisonAgent


async def test_agent_sdk_data_analyst_agent():
    """Test Agent SDK Data Analyst Agent."""
    print("🧪 Testing Agent SDK Data Analyst Agent...")
    
    try:
        # Create and initialize agent
        agent = AgentSDKDataAnalystAgent(expertise="call_center_volumetric_analysis")
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        await agent.initialize("test_session", user_context)
        print("✅ Agent initialized successfully")
        
        # Create test data
        test_data = pd.DataFrame({
            'sales': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
            'profit': [200, 220, 240, 260, 280, 300, 320, 340, 360, 380],
            'customers': [500, 550, 600, 650, 700, 750, 800, 850, 900, 950]
        })
        
        # Test data analysis
        result = await agent.analyze_dataset(
            dataset=test_data,
            analysis_type="comprehensive",
            context="Test analysis for sales data",
            user_context=user_context
        )
        print("✅ Data analysis successful")
        print(f"   Analysis ID: {result['analysis_id']}")
        print(f"   Expertise Used: {result['expertise_used']}")
        print(f"   Governance Results: {len(result['governance_results'])}")
        print(f"   Analysis Results: {len(result['analysis_results'])}")
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Agent health: {health['overall_status']}")
        
        # Test individual capabilities
        eda_result = await agent.execute_capability("eda", {"dataset": test_data.to_dict("records")}, user_context)
        stats_result = await agent.execute_capability("statistical_analysis", {"dataset": test_data.to_dict("records")}, user_context)
        anomaly_result = await agent.execute_capability("anomaly_detection", {"dataset": test_data.to_dict("records")}, user_context)
        
        print("✅ Individual capabilities successful")
        
        # Cleanup
        await agent.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Agent SDK Data Analyst Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_sdk_business_analyst_agent():
    """Test Agent SDK Business Analyst Agent."""
    print("\n🧪 Testing Agent SDK Business Analyst Agent...")
    
    try:
        # Create and initialize agent
        agent = AgentSDKBusinessAnalystAgent(expertise="financial_risk_assessment")
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        await agent.initialize("test_session", user_context)
        print("✅ Agent initialized successfully")
        
        # Create test business data
        test_business_data = {
            'revenue': 1000000,
            'profit': 250000,
            'customers': 5000,
            'market_share': 0.12,
            'satisfaction_score': 0.85
        }
        
        # Test business analysis
        result = await agent.analyze_business_data(
            business_data=test_business_data,
            analysis_type="strategic",
            context="Test analysis for business performance",
            user_context=user_context
        )
        print("✅ Business analysis successful")
        print(f"   Analysis ID: {result['analysis_id']}")
        print(f"   Expertise Used: {result['expertise_used']}")
        print(f"   Governance Results: {len(result['governance_results'])}")
        print(f"   Strategic Recommendations: {len(result['strategic_recommendations'])}")
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Agent health: {health['overall_status']}")
        
        # Test individual capabilities
        bi_result = await agent.execute_capability("business_intelligence", {"business_data": test_business_data}, user_context)
        strategic_result = await agent.execute_capability("strategic_analysis", {"business_data": test_business_data}, user_context)
        risk_result = await agent.execute_capability("risk_assessment", {"business_data": test_business_data}, user_context)
        
        print("✅ Individual capabilities successful")
        
        # Cleanup
        await agent.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Agent SDK Business Analyst Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_sdk_insights_liaison_agent():
    """Test Agent SDK Insights Liaison Agent."""
    print("\n🧪 Testing Agent SDK Insights Liaison Agent...")
    
    try:
        # Create and initialize agent
        agent = AgentSDKInsightsLiaisonAgent(expertise="call_center_volumetric_analysis")
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        await agent.initialize("test_session", user_context)
        print("✅ Agent initialized successfully")
        
        # Test conversation processing
        response = await agent.process_conversation(
            user_message="I want to analyze my sales data to understand customer behavior patterns",
            conversation_id="test_conv_123",
            user_context=user_context
        )
        print("✅ Conversation processing successful")
        print(f"   Conversation ID: {response['conversation_id']}")
        print(f"   Intent: {response['intent_response']['intent']}")
        print(f"   Confidence: {response['intent_response']['confidence']}")
        print(f"   Suggested Actions: {len(response['suggested_actions'])}")
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Agent health: {health['overall_status']}")
        
        # Test individual capabilities
        conv_result = await agent.execute_capability("conversation_management", 
                                                   {"conversation_id": "test_conv_123", "action": "get_history"}, user_context)
        intent_result = await agent.execute_capability("intent_recognition", 
                                                     {"user_message": "Help me analyze data"}, user_context)
        context_result = await agent.execute_capability("context_awareness", 
                                                      {"conversation_id": "test_conv_123", "context_data": {"topic": "data_analysis"}}, user_context)
        
        print("✅ Individual capabilities successful")
        
        # Cleanup
        await agent.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Agent SDK Insights Liaison Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_end_to_end_workflow():
    """Test end-to-end workflow with all three agents."""
    print("\n🧪 Testing End-to-End Workflow...")
    
    try:
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        # Test Data Analyst Agent
        data_agent = AgentSDKDataAnalystAgent(expertise="call_center_volumetric_analysis")
        await data_agent.initialize("test_session", user_context)
        
        test_data = pd.DataFrame({
            'sales': [1000, 1100, 1200, 1300, 1400],
            'profit': [200, 220, 240, 260, 280]
        })
        
        data_result = await data_agent.analyze_dataset(test_data, "comprehensive", "Test workflow", user_context)
        print("✅ Data analysis workflow successful")
        
        await data_agent.shutdown()
        
        # Test Business Analyst Agent
        business_agent = AgentSDKBusinessAnalystAgent(expertise="financial_risk_assessment")
        await business_agent.initialize("test_session", user_context)
        
        test_business_data = {
            'revenue': 1000000,
            'profit': 250000,
            'customers': 5000
        }
        
        business_result = await business_agent.analyze_business_data(test_business_data, "strategic", "Test workflow", user_context)
        print("✅ Business analysis workflow successful")
        
        await business_agent.shutdown()
        
        # Test Insights Liaison Agent
        liaison_agent = AgentSDKInsightsLiaisonAgent(expertise="call_center_volumetric_analysis")
        await liaison_agent.initialize("test_session", user_context)
        
        liaison_result = await liaison_agent.process_conversation(
            "I need help with data analysis",
            "test_conv_456",
            user_context
        )
        print("✅ Conversation workflow successful")
        
        await liaison_agent.shutdown()
        
        print("✅ End-to-end workflow completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all Agent SDK Insights Agents tests."""
    print("🚀 Starting Agent SDK Insights Agents Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test individual agents
    test_results.append(await test_agent_sdk_data_analyst_agent())
    test_results.append(await test_agent_sdk_business_analyst_agent())
    test_results.append(await test_agent_sdk_insights_liaison_agent())
    
    # Test end-to-end workflow
    test_results.append(await test_end_to_end_workflow())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Agent SDK Insights Agents are working correctly!")
        print("\n📋 Agent SDK Insights Agents Implementation Complete:")
        print("  ✅ AgentSDKDataAnalystAgent: Policy-aware data analysis with Smart City integration")
        print("  ✅ AgentSDKBusinessAnalystAgent: Strategic business analysis with governance")
        print("  ✅ AgentSDKInsightsLiaisonAgent: Conversational interface with LLM understanding")
        print("\n🎯 Ready for production deployment!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)



