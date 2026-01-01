#!/usr/bin/env python3
"""
Test Security Guard MCP Server Refactored

Tests the refactored SecurityGuardMCPServer to ensure it works with the new MCPServerBase
and full utility integration via DIContainer.
"""

import os
import sys
import asyncio
import unittest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

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
    
    async def get_user_context_with_tenant(self, token: str) -> Dict[str, Any]:
        """Mock get user context with tenant."""
        return {
            "success": True,
            "user_id": "test_user_123",
            "tenant_id": "test_tenant_456",
            "permissions": ["read", "write"]
        }
    
    async def create_tenant(self, tenant_name: str, tenant_type: str, admin_user_id: str, admin_email: str) -> Dict[str, Any]:
        """Mock create tenant."""
        return {
            "success": True,
            "tenant_id": "new_tenant_789",
            "tenant_name": tenant_name,
            "tenant_type": tenant_type
        }
    
    async def validate_user_permission(self, user_id: str, resource: str, action: str, user_permissions: list) -> Dict[str, Any]:
        """Mock validate user permission."""
        return {
            "success": True,
            "authorized": True,
            "user_id": user_id,
            "resource": resource,
            "action": action
        }
    
    async def audit_user_action(self, user_context: Dict, action: str, resource: str, service: str, details: Dict) -> Dict[str, Any]:
        """Mock audit user action."""
        return {
            "success": True,
            "audit_id": "audit_123",
            "timestamp": "2025-01-09T10:00:00Z"
        }
    
    async def get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Mock get tenant info."""
        return {
            "success": True,
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "tenant_type": "enterprise"
        }
    
    async def add_user_to_tenant(self, tenant_id: str, user_id: str, permissions: list) -> Dict[str, Any]:
        """Mock add user to tenant."""
        return {
            "success": True,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "permissions": permissions
        }

class TestSecurityGuardMCPServerRefactored(unittest.TestCase):
    """Test the refactored Security Guard MCP Server."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_di_container = MockDIContainerService()
        
        # Mock the SecurityGuardService import
        with patch('backend.smart_city.services.security_guard.mcp_server.security_guard_mcp_server.SecurityGuardService', MockSecurityGuardService):
            from backend.smart_city.services.security_guard.mcp_server.security_guard_mcp_server import SecurityGuardMCPServer
            
            self.mcp_server = SecurityGuardMCPServer(self.mock_di_container)
    
    def test_initialization(self):
        """Test that the MCP server initializes correctly."""
        # Check that the server was initialized
        self.assertIsNotNone(self.mcp_server)
        self.assertEqual(self.mcp_server.service_name, "security_guard_mcp")
        self.assertEqual(self.mcp_server.di_container, self.mock_di_container)
        
        # Check that utilities are available via DI container
        self.assertIsNotNone(self.mcp_server.config)
        self.assertIsNotNone(self.mcp_server.logger)
        self.assertIsNotNone(self.mcp_server.health)
        self.assertIsNotNone(self.mcp_server.telemetry)
        self.assertIsNotNone(self.mcp_server.security)
        self.assertIsNotNone(self.mcp_server.error_handler)
        self.assertIsNotNone(self.mcp_server.tenant)
        
        # Check that Security Guard Service was initialized
        self.assertIsNotNone(self.mcp_server.security_guard_service)
    
    def test_get_server_info(self):
        """Test get_server_info method."""
        server_info = self.mcp_server.get_server_info()
        
        self.assertIsInstance(server_info, dict)
        self.assertEqual(server_info["name"], "SecurityGuardMCPServer")
        self.assertEqual(server_info["version"], "1.0.0")
        self.assertIn("Multi-tenant security operations", server_info["description"])
        self.assertIn("tenant_management", server_info["capabilities"])
        self.assertIn("security_validation", server_info["capabilities"])
        self.assertIn("access_control", server_info["capabilities"])
        self.assertIn("audit_logging", server_info["capabilities"])
    
    def test_get_server_capabilities(self):
        """Test get_server_capabilities method."""
        capabilities = self.mcp_server.get_server_capabilities()
        
        self.assertIsInstance(capabilities, dict)
        self.assertTrue(capabilities["tenant_management"])
        self.assertTrue(capabilities["security_validation"])
        self.assertTrue(capabilities["access_control"])
        self.assertTrue(capabilities["audit_logging"])
        self.assertTrue(capabilities["multi_tenant"])
        self.assertTrue(capabilities["permission_validation"])
    
    def test_register_server_tools(self):
        """Test register_server_tools method."""
        # Register tools
        self.mcp_server.register_server_tools()
        
        # Check that tools were registered
        registered_tools = self.mcp_server.get_registered_tools()
        self.assertGreater(len(registered_tools), 0)
        
        # Check specific tools
        tool_names = list(registered_tools.keys())
        self.assertIn("get_user_context_with_tenant", tool_names)
        self.assertIn("create_tenant", tool_names)
        self.assertIn("validate_user_permission", tool_names)
        self.assertIn("audit_user_action", tool_names)
        self.assertIn("get_tenant_info", tool_names)
        self.assertIn("add_user_to_tenant", tool_names)
    
    def test_tool_definitions(self):
        """Test that tool definitions are correct."""
        self.mcp_server.register_server_tools()
        registered_tools = self.mcp_server.get_registered_tools()
        
        # Test get_user_context_with_tenant tool
        tool = registered_tools["get_user_context_with_tenant"]
        self.assertEqual(tool.name, "get_user_context_with_tenant")
        self.assertIn("Get user context with full tenant information", tool.description)
        self.assertTrue(tool.requires_tenant)
        self.assertEqual(tool.tenant_scope, "user")
        self.assertIn("security", tool.tags)
        self.assertIn("tenant", tool.tags)
        
        # Test create_tenant tool
        tool = registered_tools["create_tenant"]
        self.assertEqual(tool.name, "create_tenant")
        self.assertIn("Create a new tenant", tool.description)
        self.assertFalse(tool.requires_tenant)
        self.assertEqual(tool.tenant_scope, "global")
        self.assertIn("tenant", tool.tags)
        self.assertIn("management", tool.tags)
    
    @patch('backend.smart_city.services.security_guard.mcp_server.security_guard_mcp_server.SecurityGuardService', MockSecurityGuardService)
    async def test_tool_execution(self):
        """Test tool execution."""
        # Register tools
        self.mcp_server.register_server_tools()
        
        # Test get_user_context_with_tenant
        result = await self.mcp_server.execute_tool(
            "get_user_context_with_tenant",
            {"token": "test_token_123"},
            None
        )
        
        self.assertTrue(result.success)
        self.assertIn("user_id", result.result)
        self.assertIn("tenant_id", result.result)
        
        # Test create_tenant
        result = await self.mcp_server.execute_tool(
            "create_tenant",
            {
                "tenant_name": "Test Tenant",
                "tenant_type": "enterprise",
                "admin_user_id": "admin_123",
                "admin_email": "admin@test.com"
            },
            None
        )
        
        self.assertTrue(result.success)
        self.assertIn("tenant_id", result.result)
        self.assertEqual(result.result["tenant_name"], "Test Tenant")
        
        # Test validate_user_permission
        result = await self.mcp_server.execute_tool(
            "validate_user_permission",
            {
                "user_id": "user_123",
                "resource": "test_resource",
                "action": "read",
                "user_permissions": ["read", "write"]
            },
            None
        )
        
        self.assertTrue(result.success)
        self.assertTrue(result.result["authorized"])
        
        # Test audit_user_action
        result = await self.mcp_server.execute_tool(
            "audit_user_action",
            {
                "user_context": {"user_id": "user_123", "tenant_id": "tenant_456"},
                "action": "read",
                "resource": "test_resource",
                "service": "test_service",
                "details": {"additional": "info"}
            },
            None
        )
        
        self.assertTrue(result.success)
        self.assertIn("audit_id", result.result)
        
        # Test get_tenant_info
        result = await self.mcp_server.execute_tool(
            "get_tenant_info",
            {"tenant_id": "tenant_123"},
            None
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.result["tenant_id"], "tenant_123")
        
        # Test add_user_to_tenant
        result = await self.mcp_server.execute_tool(
            "add_user_to_tenant",
            {
                "tenant_id": "tenant_123",
                "user_id": "user_456",
                "permissions": ["read", "write"]
            },
            None
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.result["tenant_id"], "tenant_123")
        self.assertEqual(result.result["user_id"], "user_456")
    
    def test_tool_validation(self):
        """Test tool validation."""
        self.mcp_server.register_server_tools()
        
        # Test tool validation
        tool = self.mcp_server.get_registered_tools()["get_user_context_with_tenant"]
        validation = self.mcp_server.validate_tool_definition(tool)
        
        self.assertTrue(validation["valid"])
        self.assertEqual(len(validation["errors"]), 0)
    
    def test_tool_discovery(self):
        """Test tool discovery."""
        self.mcp_server.register_server_tools()
        
        # Test discover tools by tags
        security_tools = self.mcp_server.discover_tools(filter_tags=["security"])
        self.assertGreater(len(security_tools), 0)
        
        tenant_tools = self.mcp_server.discover_tools(filter_tags=["tenant"])
        self.assertGreater(len(tenant_tools), 0)
        
        # Test discover tenant-aware tools
        tenant_aware_tools = self.mcp_server.discover_tools(requires_tenant=True)
        self.assertGreater(len(tenant_aware_tools), 0)
        
        # Test discover non-tenant tools
        non_tenant_tools = self.mcp_server.discover_tools(requires_tenant=False)
        self.assertGreater(len(non_tenant_tools), 0)
    
    def test_tool_metadata(self):
        """Test tool metadata retrieval."""
        self.mcp_server.register_server_tools()
        
        # Test get tool metadata
        metadata = self.mcp_server.get_tool_metadata("get_user_context_with_tenant")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["name"], "get_user_context_with_tenant")
        self.assertIn("description", metadata)
        self.assertIn("input_schema", metadata)
        self.assertIn("tags", metadata)
        self.assertIn("requires_tenant", metadata)
        self.assertIn("tenant_scope", metadata)
        
        # Test get non-existent tool metadata
        metadata = self.mcp_server.get_tool_metadata("non_existent_tool")
        self.assertIsNone(metadata)
    
    def test_tool_statistics(self):
        """Test tool statistics."""
        self.mcp_server.register_server_tools()
        
        stats = self.mcp_server.get_tool_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_tools", stats)
        self.assertIn("tenant_aware_tools", stats)
        self.assertIn("tag_distribution", stats)
        self.assertIn("service_name", stats)
        self.assertIn("timestamp", stats)
        
        self.assertGreater(stats["total_tools"], 0)
        self.assertGreater(stats["tenant_aware_tools"], 0)
    
    def test_mcp_summary(self):
        """Test MCP server summary."""
        self.mcp_server.register_server_tools()
        
        summary = self.mcp_server.get_mcp_summary()
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["service_name"], "security_guard_mcp")
        self.assertEqual(summary["server_type"], "mcp")
        self.assertEqual(summary["status"], "operational")
        self.assertGreater(summary["registered_tools"], 0)
        self.assertIn("timestamp", summary)

def run_async_test(test_func):
    """Helper to run async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(test_func())
    finally:
        loop.close()

if __name__ == "__main__":
    # Run the tests
    unittest.main()
