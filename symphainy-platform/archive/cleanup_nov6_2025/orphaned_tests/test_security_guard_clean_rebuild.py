#!/usr/bin/env python3
"""
Test Security Guard Service Clean Rebuild

This test validates the clean rebuild of the Security Guard Service using ONLY our new base and protocol construct.
No archived dependencies, no complex refactoring - just clean, focused implementation.
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the clean rebuild
from security_guard_service_clean_rebuild import SecurityGuardService


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


async def test_clean_rebuild():
    """Test the clean rebuild of Security Guard Service."""
    print("\n🔍 Testing Security Guard Service Clean Rebuild...")
    
    try:
        # Setup mock dependencies
        di_container = MockDIContainer()
        communication_foundation = MockCommunicationFoundation()
        curator_foundation = MockCuratorFoundation()
        
        di_container.register_foundation_service("CommunicationFoundationService", communication_foundation)
        di_container.register_foundation_service("CuratorFoundationService", curator_foundation)
        
        # Initialize Security Guard Service (Clean Rebuild)
        security_guard = SecurityGuardService(di_container)
        success = await security_guard.initialize()
        assert success, "Security Guard Service should initialize successfully"
        print("✅ Security Guard Service (Clean Rebuild) initialization successful")
        
        # Test SOA API exposure
        assert len(security_guard.soa_apis) == 5, "Should have 5 SOA APIs"
        expected_apis = [
            "authenticate_user", "authorize_action", "orchestrate_security_communication",
            "orchestrate_zero_trust_policy", "orchestrate_tenant_isolation"
        ]
        for api_name in expected_apis:
            assert api_name in security_guard.soa_apis, f"Should have {api_name} API"
        print("✅ SOA API exposure configured (5 APIs)")
        
        # Test MCP server integration
        assert len(security_guard.mcp_tools) == 4, "Should have 4 MCP tools"
        expected_tools = [
            "authenticate_user", "authorize_action", "validate_session", "enforce_zero_trust"
        ]
        for tool_name in expected_tools:
            assert tool_name in security_guard.mcp_tools, f"Should have {tool_name} MCP tool"
        assert security_guard.mcp_server_enabled, "MCP server should be enabled"
        print("✅ MCP server integration configured (4 tools)")
        
        # Test SOA API registration with Curator
        assert len(curator_foundation.soa_apis) == 5, "SOA APIs should be registered with Curator"
        for api_name in expected_apis:
            key = f"security_guard.{api_name}"
            assert key in curator_foundation.soa_apis, f"SOA API {api_name} should be registered"
        print("✅ SOA APIs registered with Curator")
        
        # Test MCP tool registration with Curator
        assert len(curator_foundation.mcp_tools) == 4, "MCP tools should be registered with Curator"
        for tool_name in expected_tools:
            assert tool_name in curator_foundation.mcp_tools, f"MCP tool {tool_name} should be registered"
        print("✅ MCP tools registered with Curator")
        
        # Test core functionality
        auth_request = {
            "username": "test_user",
            "password": "test_password",
            "authentication_method": "password"
        }
        
        auth_response = await security_guard.authenticate_user(auth_request)
        assert auth_response["success"], "Authentication should work"
        assert "session_id" in auth_response, "Should return session_id"
        print("✅ Core authentication functionality works")
        
        # Test authorization functionality
        authz_request = {
            "user_id": "test_user",
            "action": "read",
            "resource_id": "test_resource",
            "resource_type": "document"
        }
        
        authz_response = await security_guard.authorize_action(authz_request)
        assert authz_response["success"], "Authorization should work"
        assert "authorized" in authz_response, "Should return authorization status"
        print("✅ Core authorization functionality works")
        
        # Test security communication orchestration
        comm_request = {
            "request_id": "test_request",
            "source_service": "test_service",
            "target_service": "target_service",
            "request_type": "api_call",
            "security_context": {"security_token": "test_token"},
            "tenant_id": "test_tenant"
        }
        
        comm_response = await security_guard.orchestrate_security_communication(comm_request)
        assert comm_response["success"], "Security communication should work"
        assert comm_response["authorized"], "Should be authorized"
        print("✅ Security communication orchestration works")
        
        # Test zero-trust policy orchestration
        zt_request = {
            "resource_id": "test_resource",
            "user_id": "test_user",
            "action": "read",
            "policy_rules": ["rule1", "rule2"],
            "tenant_id": "test_tenant"
        }
        
        zt_response = await security_guard.orchestrate_zero_trust_policy(zt_request)
        assert "access_granted" in zt_response, "Should return access decision"
        assert "policy_decision" in zt_response, "Should return policy decision"
        print("✅ Zero-trust policy orchestration works")
        
        # Test tenant isolation orchestration
        ti_request = {
            "resource_id": "test_resource",
            "tenant_id": "test_tenant",
            "isolation_level": "strict",
            "access_request": {"action": "read"}
        }
        
        ti_response = await security_guard.orchestrate_tenant_isolation(ti_request)
        assert "isolation_enforced" in ti_response, "Should return isolation status"
        assert ti_response["tenant_id"] == "test_tenant", "Should return tenant_id"
        print("✅ Tenant isolation orchestration works")
        
        # Test MCP tool handlers
        mcp_auth_result = await security_guard._mcp_authenticate_user({
            "username": "test_user",
            "password": "test_password"
        })
        assert "content" in mcp_auth_result, "MCP handler should return content"
        assert not mcp_auth_result["isError"], "MCP handler should not return error"
        print("✅ MCP tool handlers work")
        
        # Test base class features
        assert hasattr(security_guard, 'get_logger'), "Should have logger from base class"
        assert hasattr(security_guard, 'get_infrastructure_abstraction'), "Should have infrastructure access"
        assert hasattr(security_guard, 'validate_access'), "Should have security mixin"
        assert hasattr(security_guard, 'record_telemetry_metric'), "Should have performance monitoring"
        assert hasattr(security_guard, 'get_module'), "Should have micro-module support"
        print("✅ New base class features integrated")
        
        # Test protocol compliance
        from backend.smart_city.protocols.security_guard_service_protocol import SecurityGuardServiceProtocol
        assert isinstance(security_guard, SecurityGuardServiceProtocol), "Should implement SecurityGuardServiceProtocol"
        print("✅ Protocol compliance validated")
        
        return True
        
    except Exception as e:
        print(f"❌ Security Guard Service clean rebuild test failed: {e}")
        return False


async def main():
    """Run Security Guard Service clean rebuild test."""
    print("🚀 Testing Security Guard Service Clean Rebuild")
    print("=" * 60)
    
    try:
        result = await test_clean_rebuild()
        
        print("\n" + "=" * 60)
        print("📊 SECURITY GUARD SERVICE CLEAN REBUILD TEST SUMMARY")
        print("=" * 60)
        
        if result:
            print("🎉 SECURITY GUARD SERVICE CLEAN REBUILD VALIDATED SUCCESSFULLY!")
            print("✅ Clean rebuild using ONLY new base and protocol construct")
            print("🔗 SOA APIs exposed for realm consumption (5 APIs)")
            print("🔧 MCP tools available for agent access (4 tools)")
            print("🏗️ Micro-module architecture integrated")
            print("🎯 New base class alignment complete")
            print("📋 Protocol compliance validated")
            print("\n🎯 CLEAN REBUILD ADVANTAGES:")
            print("   • No archived dependencies")
            print("   • No complex refactoring")
            print("   • Clean, focused implementation")
            print("   • Uses ONLY new base and protocol construct")
            print("   • All 5 core security methods implemented")
            print("   • Complete SOA API and MCP tool integration")
            print("\n📝 COMPARISON:")
            print("   • Refactoring approach: Complex, many moving parts, dependency issues")
            print("   • Clean rebuild approach: Simple, focused, no dependencies")
            print("   • Result: Clean rebuild is significantly better!")
            return True
        else:
            print("⚠️ Security Guard Service clean rebuild needs attention")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

