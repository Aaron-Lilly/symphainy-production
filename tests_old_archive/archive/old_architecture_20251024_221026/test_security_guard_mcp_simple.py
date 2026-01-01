#!/usr/bin/env python3
"""
Simple Test for Security Guard MCP Server Refactored

Tests the refactored SecurityGuardMCPServer to ensure it works with the new MCPServerBase
and full utility integration via DIContainer.
"""

import os
import sys
import asyncio
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('symphainy-platform'))

# Mock the dependencies that might not be available
class MockDIContainerService:
    """Mock DI Container Service for testing."""
    
    def __init__(self):
        self.config = Mock()
        self.logger = Mock()
        self.health = Mock()
        self.telemetry = Mock()
        self.security = Mock()
        self.error_handler = Mock()
        self.tenant = Mock()
        
        # Configure mock logger
        self.logger.info = Mock()
        self.logger.error = Mock()
        self.logger.warning = Mock()
        
        # Configure mock error handler
        self.error_handler.handle_error = Mock()

class MockSecurityGuardService:
    """Mock Security Guard Service for testing."""
    
    def __init__(self, di_container):
        self.di_container = di_container
    
    async def get_user_context_with_tenant(self, token: str):
        """Mock get user context with tenant."""
        return {
            "success": True,
            "user_id": "test_user_123",
            "tenant_id": "test_tenant_456",
            "permissions": ["read", "write"]
        }
    
    async def create_tenant(self, tenant_name: str, tenant_type: str, admin_user_id: str, admin_email: str):
        """Mock create tenant."""
        return {
            "success": True,
            "tenant_id": "new_tenant_789",
            "tenant_name": tenant_name,
            "tenant_type": tenant_type
        }

def test_security_guard_mcp_server():
    """Test the refactored Security Guard MCP Server."""
    print("🧪 Testing Security Guard MCP Server Refactored...")
    
    try:
        # Mock the SecurityGuardService import
        with patch('backend.smart_city.services.security_guard.mcp_server.security_guard_mcp_server.SecurityGuardService', MockSecurityGuardService):
            from backend.smart_city.services.security_guard.mcp_server.security_guard_mcp_server import SecurityGuardMCPServer
            
            # Create mock DI container
            mock_di_container = MockDIContainerService()
            
            # Initialize the MCP server
            print("  ✅ Initializing SecurityGuardMCPServer...")
            mcp_server = SecurityGuardMCPServer(mock_di_container)
            
            # Test initialization
            print("  ✅ Testing initialization...")
            assert mcp_server is not None
            assert mcp_server.service_name == "security_guard_mcp"
            assert mcp_server.di_container == mock_di_container
            
            # Test utilities are available via DI container
            print("  ✅ Testing utility integration...")
            assert mcp_server.config is not None
            assert mcp_server.logger is not None
            assert mcp_server.health is not None
            assert mcp_server.telemetry is not None
            assert mcp_server.security is not None
            assert mcp_server.error_handler is not None
            assert mcp_server.tenant is not None
            
            # Test Security Guard Service was initialized
            assert mcp_server.security_guard_service is not None
            
            # Test get_server_info
            print("  ✅ Testing get_server_info...")
            server_info = mcp_server.get_server_info()
            assert isinstance(server_info, dict)
            assert server_info["name"] == "SecurityGuardMCPServer"
            assert server_info["version"] == "1.0.0"
            assert "Multi-tenant security operations" in server_info["description"]
            assert "tenant_management" in server_info["capabilities"]
            assert "security_validation" in server_info["capabilities"]
            
            # Test get_server_capabilities
            print("  ✅ Testing get_server_capabilities...")
            capabilities = mcp_server.get_server_capabilities()
            assert isinstance(capabilities, dict)
            assert capabilities["tenant_management"] is True
            assert capabilities["security_validation"] is True
            assert capabilities["access_control"] is True
            assert capabilities["multi_tenant"] is True
            
            # Test register_server_tools
            print("  ✅ Testing register_server_tools...")
            mcp_server.register_server_tools()
            
            # Check that tools were registered
            registered_tools = mcp_server.get_registered_tools()
            assert len(registered_tools) > 0
            
            # Check specific tools
            tool_names = list(registered_tools.keys())
            assert "get_user_context_with_tenant" in tool_names
            assert "create_tenant" in tool_names
            assert "validate_user_permission" in tool_names
            assert "audit_user_action" in tool_names
            assert "get_tenant_info" in tool_names
            assert "add_user_to_tenant" in tool_names
            
            # Test tool definitions
            print("  ✅ Testing tool definitions...")
            tool = registered_tools["get_user_context_with_tenant"]
            assert tool.name == "get_user_context_with_tenant"
            assert "Get user context with full tenant information" in tool.description
            assert tool.requires_tenant is True
            assert tool.tenant_scope == "user"
            assert "security" in tool.tags
            assert "tenant" in tool.tags
            
            tool = registered_tools["create_tenant"]
            assert tool.name == "create_tenant"
            assert "Create a new tenant" in tool.description
            assert tool.requires_tenant is False
            assert tool.tenant_scope == "global"
            assert "tenant" in tool.tags
            assert "management" in tool.tags
            
            # Test tool validation
            print("  ✅ Testing tool validation...")
            validation = mcp_server.validate_tool_definition(tool)
            assert validation["valid"] is True
            assert len(validation["errors"]) == 0
            
            # Test tool discovery
            print("  ✅ Testing tool discovery...")
            security_tools = mcp_server.discover_tools(filter_tags=["security"])
            assert len(security_tools) > 0
            
            tenant_tools = mcp_server.discover_tools(filter_tags=["tenant"])
            assert len(tenant_tools) > 0
            
            tenant_aware_tools = mcp_server.discover_tools(requires_tenant=True)
            assert len(tenant_aware_tools) > 0
            
            non_tenant_tools = mcp_server.discover_tools(requires_tenant=False)
            assert len(non_tenant_tools) > 0
            
            # Test tool metadata
            print("  ✅ Testing tool metadata...")
            metadata = mcp_server.get_tool_metadata("get_user_context_with_tenant")
            assert metadata is not None
            assert metadata["name"] == "get_user_context_with_tenant"
            assert "description" in metadata
            assert "input_schema" in metadata
            assert "tags" in metadata
            assert "requires_tenant" in metadata
            assert "tenant_scope" in metadata
            
            # Test tool statistics
            print("  ✅ Testing tool statistics...")
            stats = mcp_server.get_tool_statistics()
            assert isinstance(stats, dict)
            assert "total_tools" in stats
            assert "tenant_aware_tools" in stats
            assert "tag_distribution" in stats
            assert "service_name" in stats
            assert "timestamp" in stats
            assert stats["total_tools"] > 0
            assert stats["tenant_aware_tools"] > 0
            
            # Test MCP summary
            print("  ✅ Testing MCP summary...")
            summary = mcp_server.get_mcp_summary()
            assert isinstance(summary, dict)
            assert summary["service_name"] == "security_guard_mcp"
            assert summary["server_type"] == "mcp"
            assert summary["status"] == "operational"
            assert summary["registered_tools"] > 0
            assert "timestamp" in summary
            
            print("🎉 All tests passed! SecurityGuardMCPServer refactoring is working correctly!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_tool_execution():
    """Test tool execution."""
    print("🧪 Testing tool execution...")
    
    try:
        with patch('backend.smart_city.services.security_guard.mcp_server.security_guard_mcp_server.SecurityGuardService', MockSecurityGuardService):
            from backend.smart_city.services.security_guard.mcp_server.security_guard_mcp_server import SecurityGuardMCPServer
            
            # Create mock DI container
            mock_di_container = MockDIContainerService()
            
            # Initialize the MCP server
            mcp_server = SecurityGuardMCPServer(mock_di_container)
            mcp_server.register_server_tools()
            
            # Test get_user_context_with_tenant
            print("  ✅ Testing get_user_context_with_tenant...")
            result = await mcp_server.execute_tool(
                "get_user_context_with_tenant",
                {"token": "test_token_123"},
                None
            )
            assert result.success is True
            assert "user_id" in result.result
            assert "tenant_id" in result.result
            
            # Test create_tenant
            print("  ✅ Testing create_tenant...")
            result = await mcp_server.execute_tool(
                "create_tenant",
                {
                    "tenant_name": "Test Tenant",
                    "tenant_type": "enterprise",
                    "admin_user_id": "admin_123",
                    "admin_email": "admin@test.com"
                },
                None
            )
            assert result.success is True
            assert "tenant_id" in result.result
            assert result.result["tenant_name"] == "Test Tenant"
            
            print("🎉 Tool execution tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Security Guard MCP Server Tests...")
    
    # Run synchronous tests
    success1 = test_security_guard_mcp_server()
    
    # Run asynchronous tests
    success2 = asyncio.run(test_tool_execution())
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! SecurityGuardMCPServer refactoring is working correctly!")
        print("✅ Foundation is solid for refactoring other MCP servers!")
        exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        exit(1)





















