#!/usr/bin/env python3
"""
Test Security Guard Service Enhancement - Week 3 Validation

This test validates the Security Guard Service enhancement made in Week 3, Day 1:
- SOA API exposure for realm consumption
- MCP server integration for agent access
- Micro-module architecture integration
- New base class alignment

NOTE: This test focuses on Security Guard Service only, avoiding broader interface cleanup
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import Security Guard Service directly (avoiding __init__.py imports)
sys.path.insert(0, os.path.abspath('./backend/smart_city/services/security_guard'))

# Import Security Guard Service
from security_guard_service import SecurityGuardService

# Import protocol data models
from bases.protocols.security_guard_protocol import (
    AuthenticateUserRequest, AuthenticateUserResponse,
    AuthorizeActionRequest, AuthorizeActionResponse,
    SecurityCommunicationRequest, SecurityCommunicationResponse
)


class MockDIContainer:
    """Mock DI Container for testing."""
    
    def __init__(self):
        self.services = {}
        self.foundations = {}
        self.logger = None
        self.telemetry_utility = MockTelemetryUtility()
    
    def get_service(self, service_name: str):
        return self.services.get(service_name)
    
    def register_service(self, service_name: str, service_instance):
        self.services[service_name] = service_instance
    
    def get_foundation_service(self, foundation_name: str):
        return self.foundations.get(foundation_name)
    
    def register_foundation_service(self, foundation_name: str, foundation_instance):
        self.foundations[foundation_name] = foundation_instance
    
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


class MockTelemetryUtility:
    """Mock telemetry utility for testing."""
    
    def record_event(self, event_name: str, data: Dict[str, Any]):
        """Mock record event."""
        pass
    
    def record_metric(self, metric_name: str, value: float, metadata: Dict[str, Any]):
        """Mock record metric."""
        pass


class MockCommunicationFoundation:
    """Mock Communication Foundation for testing."""
    
    def __init__(self):
        self.logger = None
    
    async def get_websocket_manager(self):
        return {"websocket": "mock"}
    
    async def get_event_bus(self):
        return {"event_bus": "mock"}
    
    async def get_messaging_service(self):
        return {"messaging": "mock"}


class MockCuratorFoundation:
    """Mock Curator Foundation for testing."""
    
    def __init__(self):
        self.soa_apis = {}
        self.mcp_tools = {}
        self.capabilities = {}
    
    async def register_soa_api(self, service_name: str, api_name: str, endpoint: str, handler: Any, metadata: Dict[str, Any] = None):
        """Mock SOA API registration."""
        key = f"{service_name}.{api_name}"
        self.soa_apis[key] = {
            "service_name": service_name,
            "api_name": api_name,
            "endpoint": endpoint,
            "handler": handler,
            "metadata": metadata or {}
        }
        return True
    
    async def register_mcp_tool(self, tool_name: str, tool_definition: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Mock MCP tool registration."""
        self.mcp_tools[tool_name] = {
            "tool_name": tool_name,
            "tool_definition": tool_definition,
            "metadata": metadata or {}
        }
        return True


async def test_security_guard_enhancement():
    """Test Security Guard Service enhancement."""
    print("\n🔍 Testing Security Guard Service Enhancement...")
    
    # Setup mock dependencies
    di_container = MockDIContainer()
    communication_foundation = MockCommunicationFoundation()
    curator_foundation = MockCuratorFoundation()
    
    di_container.register_foundation_service("CommunicationFoundationService", communication_foundation)
    di_container.register_foundation_service("CuratorFoundationService", curator_foundation)
    
    # Initialize Security Guard Service
    security_guard = SecurityGuardService(di_container)
    
    try:
        # Test initialization
        success = await security_guard.initialize()
        assert success, "Security Guard Service should initialize successfully"
        print("✅ Security Guard Service initialization successful")
        
        # Test SOA API exposure
        assert len(security_guard.soa_apis) > 0, "Should have SOA APIs defined"
        assert "authenticate_user" in security_guard.soa_apis, "Should have authenticate_user API"
        assert "authorize_action" in security_guard.soa_apis, "Should have authorize_action API"
        assert "orchestrate_security_communication" in security_guard.soa_apis, "Should have security communication API"
        print("✅ SOA API exposure configured")
        
        # Test MCP server integration
        assert len(security_guard.mcp_tools) > 0, "Should have MCP tools defined"
        assert "authenticate_user" in security_guard.mcp_tools, "Should have authenticate_user MCP tool"
        assert "authorize_action" in security_guard.mcp_tools, "Should have authorize_action MCP tool"
        assert "validate_session" in security_guard.mcp_tools, "Should have validate_session MCP tool"
        assert security_guard.mcp_server_enabled, "MCP server should be enabled"
        print("✅ MCP server integration configured")
        
        # Test SOA API registration with Curator
        assert len(curator_foundation.soa_apis) > 0, "SOA APIs should be registered with Curator"
        for api_name in security_guard.soa_apis.keys():
            key = f"security_guard.{api_name}"
            assert key in curator_foundation.soa_apis, f"SOA API {api_name} should be registered"
        print("✅ SOA APIs registered with Curator")
        
        # Test MCP tool registration with Curator
        assert len(curator_foundation.mcp_tools) > 0, "MCP tools should be registered with Curator"
        for tool_name in security_guard.mcp_tools.keys():
            assert tool_name in curator_foundation.mcp_tools, f"MCP tool {tool_name} should be registered"
        print("✅ MCP tools registered with Curator")
        
        # Test core functionality
        auth_request = AuthenticateUserRequest(
            username="test_user",
            password="test_password",
            authentication_method="password"
        )
        
        auth_response = await security_guard.authenticate_user(auth_request)
        assert isinstance(auth_response, AuthenticateUserResponse), "Should return AuthenticateUserResponse"
        print("✅ Core authentication functionality works")
        
        # Test authorization functionality
        authz_request = AuthorizeActionRequest(
            user_id="test_user",
            action="read",
            resource_id="test_resource",
            resource_type="document"
        )
        
        authz_response = await security_guard.authorize_action(authz_request)
        assert isinstance(authz_response, AuthorizeActionResponse), "Should return AuthorizeActionResponse"
        print("✅ Core authorization functionality works")
        
        # Test MCP tool handlers
        mcp_auth_result = await security_guard._mcp_authenticate_user({
            "username": "test_user",
            "password": "test_password"
        })
        assert "content" in mcp_auth_result, "MCP handler should return content"
        assert isinstance(mcp_auth_result["content"], list), "Content should be a list"
        print("✅ MCP tool handlers work")
        
        # Test micro-module architecture
        assert hasattr(security_guard, 'get_module'), "Should have micro-module support"
        print("✅ Micro-module architecture integrated")
        
        # Test new base class features
        assert hasattr(security_guard, 'get_logger'), "Should have logger from base class"
        assert hasattr(security_guard, 'get_infrastructure_abstraction'), "Should have infrastructure access"
        assert hasattr(security_guard, 'validate_access'), "Should have security mixin"
        assert hasattr(security_guard, 'record_telemetry_metric'), "Should have performance monitoring"
        print("✅ New base class features integrated")
        
        return True
        
    except Exception as e:
        print(f"❌ Security Guard Service enhancement test failed: {e}")
        return False


async def test_soa_api_consumption():
    """Test SOA API consumption by other realms."""
    print("\n🔍 Testing SOA API Consumption...")
    
    # Setup mock dependencies
    di_container = MockDIContainer()
    communication_foundation = MockCommunicationFoundation()
    curator_foundation = MockCuratorFoundation()
    
    di_container.register_foundation_service("CommunicationFoundationService", communication_foundation)
    di_container.register_foundation_service("CuratorFoundationService", curator_foundation)
    
    # Initialize Security Guard Service
    security_guard = SecurityGuardService(di_container)
    await security_guard.initialize()
    
    try:
        # Simulate realm consuming SOA API
        api_info = await curator_foundation.get_soa_api("security_guard", "authenticate_user")
        assert api_info is not None, "Should be able to get SOA API info"
        assert api_info["service_name"] == "security_guard", "Service name should match"
        assert api_info["api_name"] == "authenticate_user", "API name should match"
        assert api_info["endpoint"] == "/api/v1/security/authenticate", "Endpoint should match"
        print("✅ SOA API consumption works")
        
        return True
        
    except Exception as e:
        print(f"❌ SOA API consumption test failed: {e}")
        return False


async def test_mcp_tool_access():
    """Test MCP tool access by agents."""
    print("\n🔍 Testing MCP Tool Access...")
    
    # Setup mock dependencies
    di_container = MockDIContainer()
    communication_foundation = MockCommunicationFoundation()
    curator_foundation = MockCuratorFoundation()
    
    di_container.register_foundation_service("CommunicationFoundationService", communication_foundation)
    di_container.register_foundation_service("CuratorFoundationService", curator_foundation)
    
    # Initialize Security Guard Service
    security_guard = SecurityGuardService(di_container)
    await security_guard.initialize()
    
    try:
        # Simulate agent accessing MCP tool
        tool_info = await curator_foundation.get_mcp_tool("authenticate_user")
        assert tool_info is not None, "Should be able to get MCP tool info"
        assert tool_info["tool_name"] == "authenticate_user", "Tool name should match"
        assert "inputSchema" in tool_info["tool_definition"], "Should have input schema"
        print("✅ MCP tool access works")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP tool access test failed: {e}")
        return False


async def main():
    """Run all Security Guard Service enhancement tests."""
    print("🚀 Testing Security Guard Service Enhancement - Week 3 Validation")
    print("=" * 70)
    
    tests = [
        test_security_guard_enhancement,
        test_soa_api_consumption,
        test_mcp_tool_access
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
    print("\n" + "=" * 70)
    print("📊 SECURITY GUARD SERVICE ENHANCEMENT TEST SUMMARY")
    print("=" * 70)
    
    test_names = [
        "Security Guard Enhancement",
        "SOA API Consumption", 
        "MCP Tool Access"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SECURITY GUARD SERVICE ENHANCEMENTS VALIDATED SUCCESSFULLY!")
        print("✅ Week 3, Day 1: Security Guard Service Enhancement COMPLETE")
        print("🔗 SOA APIs exposed for realm consumption")
        print("🔧 MCP tools available for agent access")
        print("🏗️ Micro-module architecture integrated")
        print("🎯 New base class alignment complete")
        return True
    else:
        print("⚠️ Some Security Guard Service enhancements need attention")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
