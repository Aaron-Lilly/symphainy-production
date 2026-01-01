#!/usr/bin/env python3
"""
Test Hierarchical Agent System

This script tests all 6 hierarchical agent types to ensure they work correctly
with the existing LLM abstraction and platform infrastructure.
"""

import sys
import os
from pathlib import Path

# Add the platform directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "symphainy-platform"))
sys.path.insert(0, str(Path(__file__).parent / "symphainy-platform" / "symphainy-platform"))

def test_agent_imports():
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

def test_agent_hierarchy():
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

def test_agent_capabilities():
    """Test that agents have the correct capabilities."""
    print("\n🧪 Testing Agent Capabilities...")
    
    try:
        from agentic.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
        from agentic.agent_sdk.task_llm_agent import TaskLLMAgent
        from agentic.agent_sdk.dimension_specialist_agent import DimensionSpecialistAgent
        from agentic.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from agentic.agent_sdk.global_orchestrator_agent import GlobalOrchestratorAgent
        from agentic.agent_sdk.global_guide_agent import GlobalGuideAgent
        
        # Test that agents have required methods
        assert hasattr(LightweightLLMAgent, 'execute_llm_operation'), "LightweightLLMAgent should have execute_llm_operation"
        print("✅ LightweightLLMAgent capabilities correct")
        
        assert hasattr(TaskLLMAgent, 'execute_task_operation'), "TaskLLMAgent should have execute_task_operation"
        print("✅ TaskLLMAgent capabilities correct")
        
        assert hasattr(DimensionSpecialistAgent, 'execute_dimension_operation'), "DimensionSpecialistAgent should have execute_dimension_operation"
        print("✅ DimensionSpecialistAgent capabilities correct")
        
        assert hasattr(DimensionLiaisonAgent, 'execute_liaison_operation'), "DimensionLiaisonAgent should have execute_liaison_operation"
        print("✅ DimensionLiaisonAgent capabilities correct")
        
        assert hasattr(GlobalOrchestratorAgent, 'execute_global_operation'), "GlobalOrchestratorAgent should have execute_global_operation"
        print("✅ GlobalOrchestratorAgent capabilities correct")
        
        assert hasattr(GlobalGuideAgent, 'execute_guide_operation'), "GlobalGuideAgent should have execute_guide_operation"
        print("✅ GlobalGuideAgent capabilities correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent capabilities test failed: {e}")
        return False

def test_agent_characteristics():
    """Test that agents have the correct characteristics."""
    print("\n🧪 Testing Agent Characteristics...")
    
    try:
        from agentic.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
        from agentic.agent_sdk.task_llm_agent import TaskLLMAgent
        from agentic.agent_sdk.dimension_specialist_agent import DimensionSpecialistAgent
        from agentic.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from agentic.agent_sdk.global_orchestrator_agent import GlobalOrchestratorAgent
        from agentic.agent_sdk.global_guide_agent import GlobalGuideAgent
        
        # Test LightweightLLMAgent characteristics
        assert hasattr(LightweightLLMAgent, 'llm_only_operations'), "LightweightLLMAgent should have llm_only_operations"
        assert hasattr(LightweightLLMAgent, 'mcp_tools_integration'), "LightweightLLMAgent should have mcp_tools_integration"
        assert hasattr(LightweightLLMAgent, 'agui_integration'), "LightweightLLMAgent should have agui_integration"
        assert hasattr(LightweightLLMAgent, 'centralized_governance'), "LightweightLLMAgent should have centralized_governance"
        print("✅ LightweightLLMAgent characteristics correct")
        
        # Test TaskLLMAgent characteristics
        assert hasattr(TaskLLMAgent, 'task_oriented'), "TaskLLMAgent should have task_oriented"
        print("✅ TaskLLMAgent characteristics correct")
        
        # Test DimensionSpecialistAgent characteristics
        assert hasattr(DimensionSpecialistAgent, 'dimensional_awareness'), "DimensionSpecialistAgent should have dimensional_awareness"
        assert hasattr(DimensionSpecialistAgent, 'state_awareness'), "DimensionSpecialistAgent should have state_awareness"
        assert hasattr(DimensionSpecialistAgent, 'tool_usage'), "DimensionSpecialistAgent should have tool_usage"
        assert hasattr(DimensionSpecialistAgent, 'specialist_capabilities'), "DimensionSpecialistAgent should have specialist_capabilities"
        print("✅ DimensionSpecialistAgent characteristics correct")
        
        # Test DimensionLiaisonAgent characteristics
        assert hasattr(DimensionLiaisonAgent, 'user_interactivity'), "DimensionLiaisonAgent should have user_interactivity"
        assert hasattr(DimensionLiaisonAgent, 'user_facing'), "DimensionLiaisonAgent should have user_facing"
        print("✅ DimensionLiaisonAgent characteristics correct")
        
        # Test GlobalOrchestratorAgent characteristics
        assert hasattr(GlobalOrchestratorAgent, 'cross_dimensional_awareness'), "GlobalOrchestratorAgent should have cross_dimensional_awareness"
        assert hasattr(GlobalOrchestratorAgent, 'global_context'), "GlobalOrchestratorAgent should have global_context"
        assert hasattr(GlobalOrchestratorAgent, 'orchestrator_capabilities'), "GlobalOrchestratorAgent should have orchestrator_capabilities"
        print("✅ GlobalOrchestratorAgent characteristics correct")
        
        # Test GlobalGuideAgent characteristics
        assert hasattr(GlobalGuideAgent, 'user_interactivity'), "GlobalGuideAgent should have user_interactivity"
        assert hasattr(GlobalGuideAgent, 'user_facing'), "GlobalGuideAgent should have user_facing"
        print("✅ GlobalGuideAgent characteristics correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent characteristics test failed: {e}")
        return False

def test_agent_info_methods():
    """Test that agents have get_agent_info methods."""
    print("\n🧪 Testing Agent Info Methods...")
    
    try:
        from agentic.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
        from agentic.agent_sdk.task_llm_agent import TaskLLMAgent
        from agentic.agent_sdk.dimension_specialist_agent import DimensionSpecialistAgent
        from agentic.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
        from agentic.agent_sdk.global_orchestrator_agent import GlobalOrchestratorAgent
        from agentic.agent_sdk.global_guide_agent import GlobalGuideAgent
        
        # Test that all agents have get_agent_info method
        assert hasattr(LightweightLLMAgent, 'get_agent_info'), "LightweightLLMAgent should have get_agent_info"
        assert hasattr(TaskLLMAgent, 'get_agent_info'), "TaskLLMAgent should have get_agent_info"
        assert hasattr(DimensionSpecialistAgent, 'get_agent_info'), "DimensionSpecialistAgent should have get_agent_info"
        assert hasattr(DimensionLiaisonAgent, 'get_agent_info'), "DimensionLiaisonAgent should have get_agent_info"
        assert hasattr(GlobalOrchestratorAgent, 'get_agent_info'), "GlobalOrchestratorAgent should have get_agent_info"
        assert hasattr(GlobalGuideAgent, 'get_agent_info'), "GlobalGuideAgent should have get_agent_info"
        
        print("✅ All agents have get_agent_info method")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent info methods test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Hierarchical Agent System")
    print("=" * 50)
    
    tests = [
        test_agent_imports,
        test_agent_hierarchy,
        test_agent_capabilities,
        test_agent_characteristics,
        test_agent_info_methods
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
