#!/usr/bin/env python3
"""
Test Configurable Specializations

Comprehensive test suite for the configurable specialization system.
Tests specialization registry, agent SDK integration, and dynamic specialization loading.
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utilities import UserContext
from agentic.specialization_registry import get_specialization_registry, SpecializationRegistry
from agentic.agent_sdk import AgentBase
from backend.business_pillars.insights_pillar.specialist_agents.agent_sdk_data_analyst_agent import AgentSDKDataAnalystAgent


async def test_specialization_registry():
    """Test specialization registry functionality."""
    print("🧪 Testing Specialization Registry...")
    
    try:
        # Create a test registry
        registry = SpecializationRegistry("test_specializations.json")
        
        # Test getting all specializations
        all_specs = registry.get_all_specializations()
        print(f"✅ Loaded {len(all_specs)} specializations")
        
        # Test getting specializations for insights pillar
        insights_specs = registry.get_specializations_for_pillar("insights")
        print(f"✅ Found {len(insights_specs)} insights specializations")
        
        # Test getting specific specialization
        call_center_spec = registry.get_specialization("call_center_volumetric_analysis")
        if call_center_spec:
            print(f"✅ Retrieved call center specialization: {call_center_spec['name']}")
        
        # Test registering a new specialization
        new_spec = {
            "name": "E-commerce Customer Analytics",
            "description": "Expert in e-commerce customer behavior, conversion optimization, and retention analysis",
            "pillar": "insights",
            "capabilities": ["customer_analytics", "conversion_optimization", "retention_analysis"],
            "system_prompt_template": "You are an expert in e-commerce customer analytics. You understand customer journey mapping, conversion funnels, A/B testing, and customer lifetime value optimization.",
            "keywords": ["ecommerce", "customer", "conversion", "retention", "analytics"]
        }
        
        success = registry.register_specialization("ecommerce_customer_analytics", new_spec)
        if success:
            print("✅ Successfully registered new specialization")
        
        # Test validation
        validation_result = registry.validate_specialization("ecommerce_customer_analytics")
        if validation_result["valid"]:
            print("✅ Specialization validation passed")
        else:
            print(f"❌ Specialization validation failed: {validation_result['errors']}")
        
        # Test search
        search_results = registry.search_specializations("customer", "insights")
        print(f"✅ Found {len(search_results)} specializations matching 'customer'")
        
        # Test stats
        stats = registry.get_specialization_stats()
        print(f"✅ Registry stats: {stats}")
        
        # Cleanup
        os.remove("test_specializations.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Specialization registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_with_specialization():
    """Test agent initialization with specialization configuration."""
    print("\n🧪 Testing Agent with Specialization...")
    
    try:
        # Get specialization configuration
        registry = get_specialization_registry()
        call_center_spec = registry.get_specialization("call_center_volumetric_analysis")
        
        if not call_center_spec:
            print("❌ Call center specialization not found")
            return False
        
        # Create agent with specialization configuration
        agent = AgentSDKDataAnalystAgent(
            expertise="call_center_volumetric_analysis",
            specialization_config=call_center_spec
        )
        
        print("✅ Agent created with specialization configuration")
        
        # Test specialization info
        spec_info = agent.get_specialization_info()
        print(f"✅ Specialization info: {spec_info['specialization_name']}")
        print(f"   Description: {spec_info['specialization_description']}")
        print(f"   Pillar: {spec_info['specialization_pillar']}")
        print(f"   Capabilities: {spec_info['specialization_capabilities']}")
        
        # Test system prompt generation
        system_prompt = agent.get_system_prompt("call volume analysis")
        print(f"✅ System prompt generated: {len(system_prompt)} characters")
        
        # Test with user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        # Initialize agent
        await agent.initialize("test_session", user_context)
        print("✅ Agent initialized successfully")
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Agent health: {health['overall_status']}")
        
        # Cleanup
        await agent.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Agent with specialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_dynamic_specialization_loading():
    """Test dynamic specialization loading and agent creation."""
    print("\n🧪 Testing Dynamic Specialization Loading...")
    
    try:
        # Create a custom specialization
        custom_spec = {
            "name": "Custom Financial Analysis",
            "description": "Expert in custom financial analysis and risk assessment",
            "pillar": "insights",
            "capabilities": ["financial_analysis", "risk_assessment", "custom_modeling"],
            "system_prompt_template": "You are an expert in custom financial analysis. You understand complex financial models, risk assessment methodologies, and regulatory compliance requirements.",
            "keywords": ["financial", "analysis", "risk", "custom", "modeling"]
        }
        
        # Register the specialization
        registry = get_specialization_registry()
        success = registry.register_specialization("custom_financial_analysis", custom_spec)
        
        if not success:
            print("❌ Failed to register custom specialization")
            return False
        
        print("✅ Custom specialization registered")
        
        # Create agent with custom specialization
        agent = AgentSDKDataAnalystAgent(
            expertise="custom_financial_analysis",
            specialization_config=custom_spec
        )
        
        print("✅ Agent created with custom specialization")
        
        # Test specialization info
        spec_info = agent.get_specialization_info()
        print(f"✅ Custom specialization: {spec_info['specialization_name']}")
        
        # Test system prompt
        system_prompt = agent.get_system_prompt("financial risk analysis")
        print(f"✅ Custom system prompt: {len(system_prompt)} characters")
        
        # Test with user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        # Initialize and test
        await agent.initialize("test_session", user_context)
        health = await agent.health_check()
        print(f"✅ Agent health: {health['overall_status']}")
        
        await agent.shutdown()
        
        # Cleanup - remove custom specialization
        registry.remove_specialization("custom_financial_analysis")
        print("✅ Custom specialization removed")
        
        return True
        
    except Exception as e:
        print(f"❌ Dynamic specialization loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_specialization_flexibility():
    """Test the flexibility of the specialization system."""
    print("\n🧪 Testing Specialization Flexibility...")
    
    try:
        registry = get_specialization_registry()
        
        # Test different ways to create agents
        print("Testing different agent creation methods...")
        
        # Method 1: With expertise string (backward compatibility)
        agent1 = AgentSDKDataAnalystAgent(expertise="call_center_volumetric_analysis")
        spec_info1 = agent1.get_specialization_info()
        print(f"✅ Method 1 - Expertise string: {spec_info1['specialization_name']}")
        
        # Method 2: With specialization config directly
        call_center_spec = registry.get_specialization("call_center_volumetric_analysis")
        agent2 = AgentSDKDataAnalystAgent(specialization_config=call_center_spec)
        spec_info2 = agent2.get_specialization_info()
        print(f"✅ Method 2 - Direct config: {spec_info2['specialization_name']}")
        
        # Method 3: No specialization (general agent)
        agent3 = AgentSDKDataAnalystAgent()
        spec_info3 = agent3.get_specialization_info()
        print(f"✅ Method 3 - No specialization: {spec_info3['specialization_name']}")
        
        # Test system prompt generation for each
        prompt1 = agent1.get_system_prompt("test context")
        prompt2 = agent2.get_system_prompt("test context")
        prompt3 = agent3.get_system_prompt("test context")
        
        print(f"✅ System prompts generated: {len(prompt1)}, {len(prompt2)}, {len(prompt3)} characters")
        
        # Test that specializations are different
        assert spec_info1['specialization_name'] == spec_info2['specialization_name']
        assert spec_info1['specialization_name'] != spec_info3['specialization_name']
        print("✅ Specialization differentiation working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Specialization flexibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all configurable specialization tests."""
    print("🚀 Starting Configurable Specializations Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test specialization registry
    test_results.append(await test_specialization_registry())
    
    # Test agent with specialization
    test_results.append(await test_agent_with_specialization())
    
    # Test dynamic specialization loading
    test_results.append(await test_dynamic_specialization_loading())
    
    # Test specialization flexibility
    test_results.append(await test_specialization_flexibility())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Configurable Specializations are working correctly!")
        print("\n📋 Configurable Specialization System Complete:")
        print("  ✅ SpecializationRegistry: Dynamic specialization management")
        print("  ✅ Agent SDK Integration: Configurable specialization support")
        print("  ✅ Backward Compatibility: Existing expertise parameter still works")
        print("  ✅ Forward Flexibility: New specializations can be added without code changes")
        print("\n🎯 Ready for production deployment!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)



