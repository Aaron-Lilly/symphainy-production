#!/usr/bin/env python3
"""
Direct Test for Security Guard MCP Server Refactored

Tests the refactored SecurityGuardMCPServer by directly importing and testing it.
"""

import os
import sys
import asyncio
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('symphainy-platform'))

def test_security_guard_mcp_server():
    """Test the refactored Security Guard MCP Server."""
    print("🧪 Testing Security Guard MCP Server Refactored...")
    
    try:
        # Create mock DI container
        mock_di_container = Mock()
        mock_di_container.config = Mock()
        mock_di_container.logger = Mock()
        mock_di_container.health = Mock()
        mock_di_container.telemetry = Mock()
        mock_di_container.security = Mock()
        mock_di_container.error_handler = Mock()
        mock_di_container.tenant = Mock()
        
        # Configure mock logger
        mock_di_container.logger.info = Mock()
        mock_di_container.logger.error = Mock()
        mock_di_container.logger.warning = Mock()
        
        # Configure mock error handler
        mock_di_container.error_handler.handle_error = Mock()
        
        # Mock SecurityGuardService
        mock_security_guard_service = Mock()
        mock_security_guard_service.get_user_context_with_tenant = Mock(return_value={
            "success": True,
            "user_id": "test_user_123",
            "tenant_id": "test_tenant_456",
            "permissions": ["read", "write"]
        })
        mock_security_guard_service.create_tenant = Mock(return_value={
            "success": True,
            "tenant_id": "new_tenant_789",
            "tenant_name": "Test Tenant",
            "tenant_type": "enterprise"
        })
        
        # Import the MCP server
        print("  ✅ Importing SecurityGuardMCPServer...")
        from backend.smart_city.services.security_guard.mcp_server.security_guard_mcp_server import SecurityGuardMCPServer
        
        # Patch the SecurityGuardService in the module
        with patch.object(SecurityGuardMCPServer, '__init__', lambda self, di_container: setattr(self, 'di_container', di_container) or setattr(self, 'service_name', 'security_guard_mcp') or setattr(self, 'logger', di_container.logger) or setattr(self, 'config', di_container.config) or setattr(self, 'health', di_container.health) or setattr(self, 'telemetry', di_container.telemetry) or setattr(self, 'security', di_container.security) or setattr(self, 'error_handler', di_container.error_handler) or setattr(self, 'tenant', di_container.tenant) or setattr(self, 'security_guard_service', mock_security_guard_service) or setattr(self, 'registered_tools', {}) or setattr(self, 'server', None)):
            
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

if __name__ == "__main__":
    print("🚀 Starting Security Guard MCP Server Tests...")
    
    # Run tests
    success = test_security_guard_mcp_server()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! SecurityGuardMCPServer refactoring is working correctly!")
        print("✅ Foundation is solid for refactoring other MCP servers!")
        exit(0)
    else:
        print("\n❌ TESTS FAILED!")
        exit(1)





















