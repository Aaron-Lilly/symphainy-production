#!/usr/bin/env python3
"""
Simple MCP Refactoring Test

Tests the refactored MCP Client Manager as a business service.
"""

import asyncio
import sys
import os
import logging

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_refactoring():
    """Test the refactored MCP Client Manager."""
    try:
        logger.info("🧪 Testing MCP Refactoring - Agentic Realm Business Service")
        
        # Test 1: Import MCP infrastructure
        logger.info("📋 Test 1: Import MCP Infrastructure")
        
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        # Initialize Public Works Foundation
        public_works = PublicWorksFoundationService()
        foundation_initialized = await public_works.initialize_foundation()
        
        if not foundation_initialized:
            logger.error("❌ Failed to initialize Public Works Foundation")
            return False
        
        logger.info("✅ Public Works Foundation initialized")
        
        # Test 2: Get MCP infrastructure
        logger.info("📋 Test 2: Get MCP Infrastructure")
        
        mcp_abstraction = public_works.get_mcp_abstraction()
        mcp_composition_service = public_works.get_mcp_composition_service()
        
        if not mcp_abstraction:
            logger.error("❌ MCP abstraction not available")
            return False
        
        if not mcp_composition_service:
            logger.error("❌ MCP composition service not available")
            return False
        
        logger.info("✅ MCP infrastructure available")
        
        # Test 3: Import MCP Client Manager
        logger.info("📋 Test 3: Import MCP Client Manager")
        
        from foundations.agentic_foundation.business_services.mcp_client_manager import MCPClientManager
        
        # Create MCP Client Manager
        mcp_client_manager = MCPClientManager(mcp_abstraction)
        
        logger.info("✅ MCP Client Manager created")
        
        # Test 4: Basic functionality
        logger.info("📋 Test 4: Basic Functionality")
        
        # Test tenant context
        tenant_context = {
            "tenant_id": "test_tenant_123",
            "user_id": "test_user_456"
        }
        
        await mcp_client_manager.set_tenant_context(tenant_context)
        logger.info("✅ Tenant context set")
        
        # Test manager health
        manager_health = mcp_client_manager.get_manager_health()
        
        if manager_health.get("service_type") != "business_service":
            logger.error("❌ MCP Client Manager is not properly identified as business service")
            return False
        
        if manager_health.get("realm") != "agentic":
            logger.error("❌ MCP Client Manager is not properly identified as agentic realm")
            return False
        
        logger.info("✅ Architecture verification passed")
        
        logger.info("🎉 MCP refactoring test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP refactoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run MCP refactoring test."""
    logger.info("🚀 Starting MCP Refactoring Test")
    
    success = await test_mcp_refactoring()
    
    if success:
        logger.info("🎉 MCP refactoring test passed!")
        return True
    else:
        logger.error("❌ MCP refactoring test failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
