#!/usr/bin/env python3
"""
Test MCP Refactoring - Agentic Realm Business Service

Tests the refactored MCP Client Manager as a business service in the agentic realm
using MCP infrastructure from Public Works Foundation.
"""

import asyncio
import sys
import os
import logging
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_refactoring():
    """Test the refactored MCP Client Manager."""
    try:
        logger.info("🧪 Testing MCP Refactoring - Agentic Realm Business Service")
        
        # Test 1: MCP Infrastructure from Public Works Foundation
        logger.info("📋 Test 1: MCP Infrastructure from Public Works Foundation")
        
        from symphainy-platform.foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        # Initialize Public Works Foundation
        public_works = PublicWorksFoundationService()
        foundation_initialized = await public_works.initialize_foundation()
        
        if not foundation_initialized:
            logger.error("❌ Failed to initialize Public Works Foundation")
            return False
        
        # Get MCP infrastructure
        mcp_abstraction = public_works.get_mcp_abstraction()
        mcp_composition_service = public_works.get_mcp_composition_service()
        
        if not mcp_abstraction:
            logger.error("❌ MCP abstraction not available")
            return False
        
        if not mcp_composition_service:
            logger.error("❌ MCP composition service not available")
            return False
        
        logger.info("✅ MCP infrastructure available from Public Works Foundation")
        
        # Test 2: MCP Client Manager as Business Service
        logger.info("📋 Test 2: MCP Client Manager as Business Service")
        
        from symphainy-platform.foundations.agentic_foundation.business_services.mcp_client_manager import MCPClientManager
        
        # Create MCP Client Manager with MCP infrastructure
        mcp_client_manager = MCPClientManager(mcp_abstraction)
        
        # Test tenant context
        tenant_context = {
            "tenant_id": "test_tenant_123",
            "user_id": "test_user_456",
            "organization": "Test Organization"
        }
        
        await mcp_client_manager.set_tenant_context(tenant_context)
        logger.info("✅ MCP Client Manager initialized with tenant context")
        
        # Test 3: Role Connection
        logger.info("📋 Test 3: Role Connection")
        
        # Connect to a role
        connection_result = await mcp_client_manager.connect_to_role(
            role_name="librarian",
            tenant_context=tenant_context
        )
        
        if not connection_result.get("success", False):
            logger.error(f"❌ Failed to connect to librarian role: {connection_result}")
            return False
        
        logger.info("✅ Connected to librarian role")
        
        # Test 4: Tool Execution
        logger.info("📋 Test 4: Tool Execution")
        
        # Execute a tool
        tool_result = await mcp_client_manager.execute_role_tool(
            role_name="librarian",
            tool_name="store_document",
            parameters={
                "document_id": "test_doc_123",
                "content": "This is a test document",
                "metadata": {
                    "title": "Test Document",
                    "author": "Test Author",
                    "category": "Test"
                }
            }
        )
        
        if not tool_result.get("status") == "success":
            logger.error(f"❌ Tool execution failed: {tool_result}")
            return False
        
        logger.info("✅ Tool executed successfully")
        
        # Test 5: Health Check
        logger.info("📋 Test 5: Health Check")
        
        health_result = await mcp_client_manager.get_role_health("librarian")
        
        if not health_result.get("status") == "connected":
            logger.error(f"❌ Health check failed: {health_result}")
            return False
        
        logger.info("✅ Role health check passed")
        
        # Test 6: Manager Health
        logger.info("📋 Test 6: Manager Health")
        
        manager_health = mcp_client_manager.get_manager_health()
        
        if not manager_health.get("status") == "healthy":
            logger.error(f"❌ Manager health check failed: {manager_health}")
            return False
        
        logger.info("✅ Manager health check passed")
        
        # Test 7: Disconnect
        logger.info("📋 Test 7: Disconnect")
        
        disconnect_result = await mcp_client_manager.disconnect_from_role("librarian")
        
        if not disconnect_result:
            logger.error("❌ Failed to disconnect from role")
            return False
        
        logger.info("✅ Disconnected from role successfully")
        
        # Test 8: Architecture Verification
        logger.info("📋 Test 8: Architecture Verification")
        
        # Verify business service nature
        manager_health = mcp_client_manager.get_manager_health()
        
        if manager_health.get("service_type") != "business_service":
            logger.error("❌ MCP Client Manager is not properly identified as business service")
            return False
        
        if manager_health.get("realm") != "agentic":
            logger.error("❌ MCP Client Manager is not properly identified as agentic realm")
            return False
        
        logger.info("✅ Architecture verification passed")
        
        logger.info("🎉 All MCP refactoring tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP refactoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_composition_service():
    """Test MCP Composition Service business logic."""
    try:
        logger.info("🧪 Testing MCP Composition Service")
        
        from symphainy-platform.foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        # Initialize Public Works Foundation
        public_works = PublicWorksFoundationService()
        foundation_initialized = await public_works.initialize_foundation()
        
        if not foundation_initialized:
            logger.error("❌ Failed to initialize Public Works Foundation")
            return False
        
        # Get MCP composition service
        mcp_composition_service = public_works.get_mcp_composition_service()
        
        if not mcp_composition_service:
            logger.error("❌ MCP composition service not available")
            return False
        
        # Test tenant connection establishment
        tenant_id = "test_tenant_456"
        role_requirements = ["librarian", "data_steward", "conductor"]
        
        connection_result = await mcp_composition_service.establish_tenant_connections(
            tenant_id=tenant_id,
            role_requirements=role_requirements
        )
        
        if not connection_result.get("success", False):
            logger.error(f"❌ Failed to establish tenant connections: {connection_result}")
            return False
        
        logger.info(f"✅ Established {connection_result['successful_connections']} connections for tenant {tenant_id}")
        
        # Test tenant operation
        operation_result = await mcp_composition_service.execute_tenant_operation(
            tenant_id=tenant_id,
            role_name="librarian",
            tool_name="search_documents",
            parameters={"query": "test query"}
        )
        
        if not operation_result.get("success", False):
            logger.error(f"❌ Tenant operation failed: {operation_result}")
            return False
        
        logger.info("✅ Tenant operation executed successfully")
        
        # Test tenant health
        health_result = await mcp_composition_service.get_tenant_health(tenant_id)
        
        if not health_result.get("success", False):
            logger.error(f"❌ Tenant health check failed: {health_result}")
            return False
        
        logger.info(f"✅ Tenant health check passed: {health_result['status']}")
        
        # Test tenant disconnect
        disconnect_result = await mcp_composition_service.disconnect_tenant(tenant_id)
        
        if not disconnect_result.get("success", False):
            logger.error(f"❌ Tenant disconnect failed: {disconnect_result}")
            return False
        
        logger.info("✅ Tenant disconnected successfully")
        
        # Test business metrics
        metrics = mcp_composition_service.get_business_metrics()
        
        if metrics.get("active_tenants", 0) != 0:
            logger.error(f"❌ Expected 0 active tenants after disconnect, got {metrics['active_tenants']}")
            return False
        
        logger.info("✅ Business metrics updated correctly")
        
        logger.info("🎉 MCP Composition Service tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP composition service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all MCP refactoring tests."""
    logger.info("🚀 Starting MCP Refactoring Tests")
    
    # Test MCP Client Manager
    test1_passed = await test_mcp_refactoring()
    
    # Test MCP Composition Service
    test2_passed = await test_mcp_composition_service()
    
    if test1_passed and test2_passed:
        logger.info("🎉 All MCP refactoring tests passed!")
        return True
    else:
        logger.error("❌ Some MCP refactoring tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
