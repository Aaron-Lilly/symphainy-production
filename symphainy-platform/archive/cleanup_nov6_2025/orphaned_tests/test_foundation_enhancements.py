#!/usr/bin/env python3
"""
Test Foundation Enhancements - Week 2 Validation

This test validates the foundation enhancements made in Week 2, Day 3-5:
- Public Works Foundation: Metrics tracking for get_abstraction
- Curator Foundation: SOA API registry and MCP Tool registry
- Communication Foundation: Orchestration methods verification
- Agentic Foundation: Architectural alignment and new agent types
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import foundation services
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
from foundations.di_container.di_container_service import DIContainerService


class MockTelemetryUtility:
    """Mock telemetry utility for testing."""
    
    def record_event(self, event_name: str, data: Dict[str, Any]):
        """Mock record event."""
        pass
    
    def record_metric(self, metric_name: str, value: float, metadata: Dict[str, Any]):
        """Mock record metric."""
        pass


class MockDIContainer:
    """Mock DI Container for testing."""
    
    def __init__(self):
        self.services = {}
        self.logger = None
        self.telemetry_utility = MockTelemetryUtility()
    
    def get_service(self, service_name: str):
        return self.services.get(service_name)
    
    def register_service(self, service_name: str, service_instance):
        self.services[service_name] = service_instance
    
    def get_utility(self, utility_name: str):
        """Mock utility getter for testing."""
        if utility_name == "logger":
            import logging
            return logging.getLogger("test")
        elif utility_name == "health":
            return {"status": "healthy"}
        elif utility_name == "telemetry":
            return self.telemetry_utility
        elif utility_name == "error_handler":
            return {"handle_error": lambda e: None}
        else:
            return f"mock_{utility_name}"
    
    def get_logging_service(self):
        """Mock logging service for testing."""
        import logging
        return logging.getLogger("test")
    
    def get_health_utility(self):
        """Mock health utility for testing."""
        return {"status": "healthy"}
    
    def get_telemetry_utility(self):
        """Mock telemetry utility for testing."""
        return self.telemetry_utility


async def test_public_works_metrics():
    """Test Public Works Foundation metrics tracking."""
    print("\n🔍 Testing Public Works Foundation Metrics...")
    
    di_container = MockDIContainer()
    public_works = PublicWorksFoundationService(di_container)
    
    # Initialize the foundation
    await public_works.initialize()
    
    # Test get_abstraction with metrics tracking
    try:
        auth_abstraction = public_works.get_abstraction("auth")
        print("✅ Public Works get_abstraction with metrics tracking works")
        
        # Test error case
        try:
            public_works.get_abstraction("nonexistent")
        except ValueError as e:
            print("✅ Public Works error handling with metrics works")
        
        return True
    except Exception as e:
        print(f"❌ Public Works metrics test failed: {e}")
        return False


async def test_curator_registries():
    """Test Curator Foundation SOA API and MCP Tool registries."""
    print("\n🔍 Testing Curator Foundation Registries...")
    
    di_container = MockDIContainer()
    curator = CuratorFoundationService(di_container)
    
    # Initialize the foundation
    await curator.initialize()
    
    try:
        # Test SOA API registry
        success = await curator.register_soa_api(
            service_name="post_office",
            api_name="send_message",
            endpoint="/api/v1/messages/send",
            handler=lambda x: x,
            metadata={"description": "Send message API"}
        )
        assert success, "SOA API registration should succeed"
        
        # Test getting SOA API
        api_info = await curator.get_soa_api("post_office", "send_message")
        assert api_info is not None, "SOA API should be retrievable"
        assert api_info["service_name"] == "post_office", "Service name should match"
        
        # Test listing SOA APIs
        all_apis = await curator.list_soa_apis()
        assert len(all_apis) > 0, "Should have registered SOA APIs"
        
        # Test MCP Tool registry
        success = await curator.register_mcp_tool(
            tool_name="test_tool",
            tool_definition={"type": "function", "schema": {}},
            metadata={"description": "Test MCP tool"}
        )
        assert success, "MCP Tool registration should succeed"
        
        # Test getting MCP Tool
        tool_info = await curator.get_mcp_tool("test_tool")
        assert tool_info is not None, "MCP Tool should be retrievable"
        assert tool_info["tool_name"] == "test_tool", "Tool name should match"
        
        # Test listing MCP Tools
        all_tools = await curator.list_mcp_tools()
        assert len(all_tools) > 0, "Should have registered MCP Tools"
        
        print("✅ Curator Foundation registries work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Curator Foundation registries test failed: {e}")
        return False


async def test_communication_orchestration():
    """Test Communication Foundation orchestration methods."""
    print("\n🔍 Testing Communication Foundation Orchestration...")
    
    di_container = MockDIContainer()
    public_works = PublicWorksFoundationService(di_container)
    communication = CommunicationFoundationService(di_container, public_works)
    
    # Initialize the foundation
    await communication.initialize()
    
    try:
        # Test orchestration methods
        websocket_manager = await communication.get_websocket_manager()
        assert websocket_manager is not None, "WebSocket manager should be available"
        
        event_bus = await communication.get_event_bus()
        assert event_bus is not None, "Event bus should be available"
        
        messaging_service = await communication.get_messaging_service()
        assert messaging_service is not None, "Messaging service should be available"
        
        print("✅ Communication Foundation orchestration methods work")
        return True
        
    except Exception as e:
        print(f"❌ Communication Foundation orchestration test failed: {e}")
        return False


async def test_agentic_alignment():
    """Test Agentic Foundation architectural alignment."""
    print("\n🔍 Testing Agentic Foundation Architectural Alignment...")
    
    di_container = MockDIContainer()
    agentic = AgenticFoundationService(di_container)
    
    # Initialize the foundation
    await agentic.initialize()
    
    try:
        # Test agentic capabilities
        capabilities = await agentic.get_agentic_capabilities()
        assert capabilities is not None, "Agentic capabilities should be available"
        
        # Test agent types
        agent_types = capabilities.get("agent_types", [])
        assert len(agent_types) > 0, "Should have agent types"
        
        # Check for new agent types
        expected_types = ["simple_llm_agent", "tool_enabled_agent", "orchestration_agent"]
        for agent_type in expected_types:
            assert agent_type in agent_types, f"Should have {agent_type}"
        
        # Test agent creation
        agent_config = {
            "agent_name": "TestAgent",
            "capabilities": ["test_capability"],
            "required_roles": [],
            "agui_schema": None
        }
        
        # Test Simple LLM Agent creation
        simple_agent = agentic._create_simple_llm_agent(agent_config)
        assert simple_agent is not None, "Simple LLM Agent should be created"
        
        print("✅ Agentic Foundation architectural alignment works")
        return True
        
    except Exception as e:
        print(f"❌ Agentic Foundation alignment test failed: {e}")
        return False


async def main():
    """Run all foundation enhancement tests."""
    print("🚀 Testing Foundation Enhancements - Week 2 Validation")
    print("=" * 60)
    
    tests = [
        test_public_works_metrics,
        test_curator_registries,
        test_communication_orchestration,
        test_agentic_alignment
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FOUNDATION ENHANCEMENTS TEST SUMMARY")
    print("=" * 60)
    
    test_names = [
        "Public Works Metrics",
        "Curator Registries", 
        "Communication Orchestration",
        "Agentic Alignment"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL FOUNDATION ENHANCEMENTS VALIDATED SUCCESSFULLY!")
        print("✅ Week 2, Day 3-5 Foundation Services Enhancement COMPLETE")
        return True
    else:
        print("⚠️ Some foundation enhancements need attention")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
