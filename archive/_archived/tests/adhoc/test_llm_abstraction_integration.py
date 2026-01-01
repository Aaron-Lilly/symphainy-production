#!/usr/bin/env python3
"""
Test LLM Abstraction Integration

Comprehensive test suite for the LLM abstraction implementation.
Tests all phases: Core Infrastructure, Business Abstraction, and Agent Integration.
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
from foundations.infrastructure_foundation.abstractions.llm_abstraction import LLMAbstraction
from foundations.public_works_foundation.abstractions.agent_llm_abstraction import AgentLLMAbstraction
from backend.business_pillars.insights_pillar.specialist_agents.llm_enhanced_data_analyst_agent import LLMEnhancedDataAnalystAgent
from backend.business_pillars.insights_pillar.specialist_agents.llm_enhanced_business_analyst_agent import LLMEnhancedBusinessAnalystAgent
from backend.business_pillars.insights_pillar.specialist_agents.llm_enhanced_insights_liaison_agent import LLMEnhancedInsightsLiaisonAgent


async def test_llm_abstraction():
    """Test core LLM abstraction functionality."""
    print("🧪 Testing LLM Abstraction...")
    
    try:
        # Test LLM abstraction initialization
        llm_abstraction = LLMAbstraction(provider="openai")
        print("✅ LLM Abstraction initialized successfully")
        
        # Test health check
        health = await llm_abstraction.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Test result interpretation
        test_results = {
            "statistical_analysis": {"mean": 100, "std": 15},
            "anomaly_detection": {"anomalies": 3}
        }
        
        interpretation = await llm_abstraction.interpret_results(
            results=test_results,
            context="test analysis",
            expertise="call_center_volumetric_analysis",
            format="agui"
        )
        print("✅ Result interpretation successful")
        
        # Test user guidance
        guidance = await llm_abstraction.guide_user(
            user_input="I want to analyze my data",
            available_tools=["analyze_data", "create_visualization"],
            context="insights analysis",
            expertise="retail_customer_behavior"
        )
        print("✅ User guidance successful")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Abstraction test failed: {e}")
        return False


async def test_agent_llm_abstraction():
    """Test business layer agent LLM abstraction."""
    print("\n🧪 Testing Agent LLM Abstraction...")
    
    try:
        # Test agent LLM abstraction initialization
        agent_llm = AgentLLMAbstraction()
        print("✅ Agent LLM Abstraction initialized successfully")
        
        # Test health check
        health = await agent_llm.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Test analysis result interpretation
        test_results = {
            "business_metrics": {"revenue_growth": 0.15},
            "risk_assessment": {"overall_risk_score": 0.35}
        }
        
        interpretation = await agent_llm.interpret_analysis_results(
            results=test_results,
            pillar="insights",
            expertise="financial_risk_assessment",
            format="agui"
        )
        print("✅ Analysis result interpretation successful")
        
        # Test user guidance
        guidance = await agent_llm.guide_user_through_tools(
            user_input="I need help with business analysis",
            available_tools=["analyze_business_metrics", "assess_business_risk"],
            pillar="insights",
            expertise="financial_risk_assessment"
        )
        print("✅ User guidance successful")
        
        # Test expertise domains
        expertise_domains = await agent_llm.get_expertise_domains("insights")
        print(f"✅ Retrieved {len(expertise_domains)} expertise domains")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent LLM Abstraction test failed: {e}")
        return False


async def test_llm_enhanced_data_analyst_agent():
    """Test LLM-enhanced data analyst agent."""
    print("\n🧪 Testing LLM-Enhanced Data Analyst Agent...")
    
    try:
        # Test agent initialization
        agent = LLMEnhancedDataAnalystAgent(expertise="call_center_volumetric_analysis")
        print("✅ LLM-Enhanced Data Analyst Agent initialized successfully")
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Create test data
        test_data = pd.DataFrame({
            'sales': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
            'profit': [200, 220, 240, 260, 280, 300, 320, 340, 360, 380],
            'customers': [500, 550, 600, 650, 700, 750, 800, 850, 900, 950]
        })
        
        # Create test user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="session_abc"
        )
        
        # Test data analysis
        result = await agent.analyze_dataset(
            dataset=test_data,
            analysis_type="comprehensive",
            context="Test analysis for sales data",
            user_context=user_context,
            expertise="call_center_volumetric_analysis"
        )
        print("✅ Data analysis successful")
        print(f"   Analysis ID: {result['analysis_id']}")
        print(f"   Expertise Used: {result['expertise_used']}")
        
        # Test user guidance
        guidance = await agent.guide_user(
            user_input="I want to analyze my sales data",
            expertise="retail_customer_behavior"
        )
        print("✅ User guidance successful")
        
        # Test expertise domains
        expertise_domains = await agent.get_expertise_domains()
        print(f"✅ Retrieved {len(expertise_domains)} expertise domains")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM-Enhanced Data Analyst Agent test failed: {e}")
        return False


async def test_llm_enhanced_business_analyst_agent():
    """Test LLM-enhanced business analyst agent."""
    print("\n🧪 Testing LLM-Enhanced Business Analyst Agent...")
    
    try:
        # Test agent initialization
        agent = LLMEnhancedBusinessAnalystAgent(expertise="financial_risk_assessment")
        print("✅ LLM-Enhanced Business Analyst Agent initialized successfully")
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Create test business data
        test_business_data = {
            'revenue': 1000000,
            'profit': 250000,
            'customers': 5000,
            'market_share': 0.12,
            'satisfaction_score': 0.85
        }
        
        # Create test user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="session_abc"
        )
        
        # Test business analysis
        result = await agent.analyze_business_data(
            business_data=test_business_data,
            analysis_type="strategic",
            context="Test analysis for business performance",
            user_context=user_context,
            expertise="financial_risk_assessment"
        )
        print("✅ Business analysis successful")
        print(f"   Analysis ID: {result['analysis_id']}")
        print(f"   Expertise Used: {result['expertise_used']}")
        print(f"   Strategic Recommendations: {len(result['strategic_recommendations'])}")
        
        # Test user guidance
        guidance = await agent.guide_user(
            user_input="I need help with business analysis",
            expertise="workflow_optimization"
        )
        print("✅ User guidance successful")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM-Enhanced Business Analyst Agent test failed: {e}")
        return False


async def test_llm_enhanced_insights_liaison_agent():
    """Test LLM-enhanced insights liaison agent."""
    print("\n🧪 Testing LLM-Enhanced Insights Liaison Agent...")
    
    try:
        # Test agent initialization
        agent = LLMEnhancedInsightsLiaisonAgent(expertise="call_center_volumetric_analysis")
        print("✅ LLM-Enhanced Insights Liaison Agent initialized successfully")
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Create test user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="session_abc"
        )
        
        # Test conversation processing
        response = await agent.process_conversation(
            user_message="I want to analyze my sales data to understand customer behavior patterns",
            conversation_id="test_conv_123",
            user_context=user_context,
            expertise="retail_customer_behavior"
        )
        print("✅ Conversation processing successful")
        print(f"   Conversation ID: {response['conversation_id']}")
        print(f"   Intent: {response['intent_response']['intent']}")
        print(f"   Confidence: {response['intent_response']['confidence']}")
        print(f"   Suggested Actions: {len(response['suggested_actions'])}")
        
        # Test expertise domains
        expertise_domains = await agent.get_expertise_domains()
        print(f"✅ Retrieved {len(expertise_domains)} expertise domains")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM-Enhanced Insights Liaison Agent test failed: {e}")
        return False


async def main():
    """Run all LLM abstraction integration tests."""
    print("🚀 Starting LLM Abstraction Integration Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test Phase 1: Core LLM Infrastructure
    test_results.append(await test_llm_abstraction())
    
    # Test Phase 2: Business Abstraction
    test_results.append(await test_agent_llm_abstraction())
    
    # Test Phase 3: Agent Integration
    test_results.append(await test_llm_enhanced_data_analyst_agent())
    test_results.append(await test_llm_enhanced_business_analyst_agent())
    test_results.append(await test_llm_enhanced_insights_liaison_agent())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! LLM Abstraction Integration is working correctly!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)



