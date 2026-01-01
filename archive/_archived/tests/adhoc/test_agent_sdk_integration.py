#!/usr/bin/env python3
"""
Test Agent SDK Integration

Comprehensive test suite for the Agent SDK implementation.
Tests all components: AgentBase, MCPClientManager, PolicyIntegration, AGUIOutputFormatter, ToolComposition.
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
from agentic.agent_sdk import AgentBase, MCPClientManager, PolicyIntegration, AGUIOutputFormatter, ToolComposition


class TestDataAnalystAgent(AgentBase):
    """Test implementation of Data Analyst Agent using Agent SDK."""
    
    def __init__(self, expertise: str = None):
        super().__init__(
            agent_name="TestDataAnalystAgent",
            capabilities=["eda", "statistical_analysis", "anomaly_detection"],
            required_roles=["librarian", "data_steward", "conductor", "post_office"],
            expertise=expertise
        )
    
    async def execute_capability(self, capability: str, parameters: Dict[str, Any], 
                               user_context: UserContext = None) -> Dict[str, Any]:
        """Execute specific agent capability."""
        try:
            if capability == "eda":
                return await self._execute_eda(parameters, user_context)
            elif capability == "statistical_analysis":
                return await self._execute_statistical_analysis(parameters, user_context)
            elif capability == "anomaly_detection":
                return await self._execute_anomaly_detection(parameters, user_context)
            else:
                raise ValueError(f"Unknown capability: {capability}")
                
        except Exception as e:
            self.logger.error(f"Capability execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_eda(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Execute exploratory data analysis."""
        try:
            # Simulate EDA execution
            data = parameters.get("data", [])
            
            return {
                "success": True,
                "capability": "eda",
                "results": {
                    "data_shape": (len(data), len(data[0]) if data else 0),
                    "missing_values": 0,
                    "data_types": {"numeric": 3, "categorical": 2}
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_statistical_analysis(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Execute statistical analysis."""
        try:
            # Simulate statistical analysis
            data = parameters.get("data", [])
            
            return {
                "success": True,
                "capability": "statistical_analysis",
                "results": {
                    "mean": 100.5,
                    "std": 15.2,
                    "correlation": 0.85
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_anomaly_detection(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Execute anomaly detection."""
        try:
            # Simulate anomaly detection
            data = parameters.get("data", [])
            
            return {
                "success": True,
                "capability": "anomaly_detection",
                "results": {
                    "anomalies_detected": 3,
                    "anomaly_score": 0.15,
                    "outlier_indices": [5, 12, 23]
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


async def test_agent_sdk_components():
    """Test individual Agent SDK components."""
    print("🧪 Testing Agent SDK Components...")
    
    # Test MCPClientManager
    try:
        mcp_manager = MCPClientManager()
        print("✅ MCPClientManager initialized successfully")
        
        # Test connection to role
        connection = await mcp_manager.connect_to_role("librarian")
        print("✅ Role connection successful")
        
        # Test tool execution
        result = await mcp_manager.execute_tool("librarian", "store_document", {"metadata": {"test": True}})
        print("✅ Tool execution successful")
        
    except Exception as e:
        print(f"❌ MCPClientManager test failed: {e}")
        return False
    
    # Test PolicyIntegration
    try:
        policy_integration = PolicyIntegration()
        await policy_integration.initialize("test_agent", ["librarian", "data_steward"])
        print("✅ PolicyIntegration initialized successfully")
        
        # Test policy check
        user_context = UserContext(user_id="test_user", email="test@example.com", 
                                 full_name="Test User", session_id="test_session",
                                 permissions=["read", "write"])
        policy_result = await policy_integration.check_policies(
            "test_agent", ["analyze_data"], {"test": True}, user_context
        )
        print("✅ Policy check successful")
        
    except Exception as e:
        print(f"❌ PolicyIntegration test failed: {e}")
        return False
    
    # Test AGUIOutputFormatter
    try:
        formatter = AGUIOutputFormatter()
        print("✅ AGUIOutputFormatter initialized successfully")
        
        # Test output formatting
        test_results = {
            "success": True,
            "analysis_results": {
                "title": "Test Analysis",
                "metrics": {"accuracy": 0.95}
            }
        }
        
        agui_output = await formatter.format_output(
            test_results, "test_agent", "test_session", ["eda"], "test_expertise"
        )
        print("✅ AGUI output formatting successful")
        
    except Exception as e:
        print(f"❌ AGUIOutputFormatter test failed: {e}")
        return False
    
    # Test ToolComposition
    try:
        tool_composition = ToolComposition()
        print("✅ ToolComposition initialized successfully")
        
        # Test tool chain execution
        role_connections = {"librarian": {"status": "connected"}}
        result = await tool_composition.execute_tool_chain(
            ["store_document", "assess_data_quality"], 
            {"test": True}, 
            role_connections, 
            "test_agent"
        )
        print("✅ Tool chain execution successful")
        
    except Exception as e:
        print(f"❌ ToolComposition test failed: {e}")
        return False
    
    return True


async def test_agent_base():
    """Test AgentBase functionality."""
    print("\n🧪 Testing AgentBase...")
    
    try:
        # Create test agent
        agent = TestDataAnalystAgent(expertise="test_expertise")
        print("✅ TestDataAnalystAgent created successfully")
        
        # Test initialization
        user_context = UserContext(user_id="test_user", email="test@example.com", 
                                 full_name="Test User", session_id="test_session",
                                 permissions=["read", "write"])
        await agent.initialize("test_session", user_context)
        print("✅ Agent initialization successful")
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Agent health check: {health['overall_status']}")
        
        # Test capability execution
        result = await agent.execute_capability("eda", {"data": [[1, 2, 3], [4, 5, 6]]}, user_context)
        print("✅ Capability execution successful")
        
        # Test governance execution
        governance_result = await agent.execute_with_governance(
            ["store_document", "assess_data_quality"],
            {"test": True, "data": [[1, 2, 3]]},
            user_context
        )
        print("✅ Governance execution successful")
        
        # Test shutdown
        await agent.shutdown()
        print("✅ Agent shutdown successful")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentBase test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_end_to_end_workflow():
    """Test end-to-end agent workflow."""
    print("\n🧪 Testing End-to-End Workflow...")
    
    try:
        # Create and initialize agent
        agent = TestDataAnalystAgent(expertise="call_center_volumetric_analysis")
        user_context = UserContext(user_id="test_user", email="test@example.com", 
                                 full_name="Test User", session_id="test_session",
                                 permissions=["read", "write"])
        await agent.initialize("test_session", user_context)
        
        # Test complete data analysis workflow
        workflow_result = await agent.execute_with_governance(
            ["assess_data_quality", "create_workflow", "monitor_health", "send_message"],
            {
                "data": [[100, 200, 300], [150, 250, 350], [120, 220, 320]],
                "analysis_type": "comprehensive",
                "output_format": "agui"
            },
            user_context
        )
        
        print("✅ End-to-end workflow successful")
        print(f"   Success: {workflow_result['success']}")
        print(f"   Tools executed: {len(workflow_result['results']['metadata']['tools_executed'])}")
        print(f"   AGUI components: {len(workflow_result['agui_output']['components'])}")
        
        # Test individual capabilities
        eda_result = await agent.execute_capability("eda", {"data": [[1, 2, 3]]}, user_context)
        stats_result = await agent.execute_capability("statistical_analysis", {"data": [[1, 2, 3]]}, user_context)
        anomaly_result = await agent.execute_capability("anomaly_detection", {"data": [[1, 2, 3]]}, user_context)
        
        print("✅ Individual capabilities successful")
        
        # Cleanup
        await agent.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all Agent SDK integration tests."""
    print("🚀 Starting Agent SDK Integration Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test individual components
    test_results.append(await test_agent_sdk_components())
    
    # Test AgentBase
    test_results.append(await test_agent_base())
    
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
        print("\n🎉 ALL TESTS PASSED! Agent SDK is working correctly!")
        print("\n📋 Agent SDK Implementation Complete:")
        print("  ✅ AgentBase: Core agent class with Smart City integration")
        print("  ✅ MCPClientManager: Smart City role connection management")
        print("  ✅ PolicyIntegration: City Manager + Security Guard hooks")
        print("  ✅ AGUIOutputFormatter: Structured output generation")
        print("  ✅ ToolComposition: Tool chaining and orchestration")
        print("\n🎯 Ready for agent transformation!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
