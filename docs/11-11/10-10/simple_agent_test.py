#!/usr/bin/env python3
"""
Simple Test for Hierarchical Agent System

This script tests the hierarchical agent types from the correct directory.
"""

import sys
import os

# Add the platform directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'symphainy-platform'))

def test_imports():
    """Test that all hierarchical agent types can be imported."""
    print("🧪 Testing Agent Imports...")
    
    try:
        from agentic.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
        print("✅ LightweightLLMAgent import successful")
    except Exception as e:
        print(f"❌ LightweightLLMAgent import failed: {e}")
        return False
    
    try:
        from agentic.agent_sdk.task_llm_agent import TaskLLMAgent
        print("✅ TaskLLMAgent import successful")
    except Exception as e:
        print(f"❌ TaskLLMAgent import failed: {e}")
        return False
    
    try:
        from agentic.agent_sdk.dimension_specialist_agent import DimensionSpecialistAgent
        print("✅ DimensionSpecialistAgent import successful")
    except Exception as e:
        print(f"❌ DimensionSpecialistAgent import failed: {e}")
        return False
    
    try:
        from agentic.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        print("✅ DimensionLiaisonAgent import successful")
    except Exception as e:
        print(f"❌ DimensionLiaisonAgent import failed: {e}")
        return False
    
    try:
        from agentic.agent_sdk.global_orchestrator_agent import GlobalOrchestratorAgent
        print("✅ GlobalOrchestratorAgent import successful")
    except Exception as e:
        print(f"❌ GlobalOrchestratorAgent import failed: {e}")
        return False
    
    try:
        from agentic.agent_sdk.global_guide_agent import GlobalGuideAgent
        print("✅ GlobalGuideAgent import successful")
    except Exception as e:
        print(f"❌ GlobalGuideAgent import failed: {e}")
        return False
    
    return True

def test_hierarchy():
    """Test that the agent hierarchy is correct."""
    print("\n🧪 Testing Agent Hierarchy...")
    
    try:
        from agentic.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
        from agentic.agent_sdk.task_llm_agent import TaskLLMAgent
        from agentic.agent_sdk.dimension_specialist_agent import DimensionSpecialistAgent
        from agentic.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from agentic.agent_sdk.global_orchestrator_agent import GlobalOrchestratorAgent
        from agentic.agent_sdk.global_guide_agent import GlobalGuideAgent
        
        # Test inheritance hierarchy
        assert issubclass(TaskLLMAgent, LightweightLLMAgent), "TaskLLMAgent should inherit from LightweightLLMAgent"
        print("✅ TaskLLMAgent inheritance correct")
        
        assert issubclass(DimensionSpecialistAgent, LightweightLLMAgent), "DimensionSpecialistAgent should inherit from LightweightLLMAgent"
        print("✅ DimensionSpecialistAgent inheritance correct")
        
        assert issubclass(DimensionLiaisonAgent, DimensionSpecialistAgent), "DimensionLiaisonAgent should inherit from DimensionSpecialistAgent"
        print("✅ DimensionLiaisonAgent inheritance correct")
        
        assert issubclass(GlobalOrchestratorAgent, DimensionSpecialistAgent), "GlobalOrchestratorAgent should inherit from DimensionSpecialistAgent"
        print("✅ GlobalOrchestratorAgent inheritance correct")
        
        assert issubclass(GlobalGuideAgent, GlobalOrchestratorAgent), "GlobalGuideAgent should inherit from GlobalOrchestratorAgent"
        print("✅ GlobalGuideAgent inheritance correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent hierarchy test failed: {e}")
        return False

def test_characteristics():
    """Test that agents have the correct characteristics."""
    print("\n🧪 Testing Agent Characteristics...")
    
    try:
        from agentic.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
        from agentic.agent_sdk.task_llm_agent import TaskLLMAgent
        from agentic.agent_sdk.dimension_specialist_agent import DimensionSpecialistAgent
        from agentic.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from agentic.agent_sdk.global_orchestrator_agent import GlobalOrchestratorAgent
        from agentic.agent_sdk.global_guide_agent import GlobalGuideAgent
        
        # Test that agents have required attributes
        assert hasattr(LightweightLLMAgent, 'llm_only_operations'), "LightweightLLMAgent should have llm_only_operations"
        assert hasattr(TaskLLMAgent, 'task_oriented'), "TaskLLMAgent should have task_oriented"
        assert hasattr(DimensionSpecialistAgent, 'dimensional_awareness'), "DimensionSpecialistAgent should have dimensional_awareness"
        assert hasattr(DimensionLiaisonAgent, 'user_interactivity'), "DimensionLiaisonAgent should have user_interactivity"
        assert hasattr(GlobalOrchestratorAgent, 'cross_dimensional_awareness'), "GlobalOrchestratorAgent should have cross_dimensional_awareness"
        assert hasattr(GlobalGuideAgent, 'user_interactivity'), "GlobalGuideAgent should have user_interactivity"
        
        print("✅ All agent characteristics correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent characteristics test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Hierarchical Agent System")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_hierarchy,
        test_characteristics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ Test failed: {test.__name__}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Hierarchical Agent System is working correctly!")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
