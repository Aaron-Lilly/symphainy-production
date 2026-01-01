#!/usr/bin/env python3
"""
MCP Architecture Test

Tests the refactored MCP architecture without requiring full foundation initialization.
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

async def test_mcp_architecture():
    """Test the refactored MCP architecture."""
    try:
        logger.info("🧪 Testing MCP Architecture Refactoring")
        
        # Test 1: Import MCP Protocol
        logger.info("📋 Test 1: Import MCP Protocol")
        
        from foundations.public_works_foundation.abstraction_contracts.mcp_protocol import MCPProtocol
        
        logger.info("✅ MCP Protocol imported successfully")
        
        # Test 2: Import MCP Adapter
        logger.info("📋 Test 2: Import MCP Adapter")
        
        from foundations.public_works_foundation.infrastructure_adapters.mcp_adapter import MCPAdapter
        
        # Create MCP adapter
        mcp_adapter = MCPAdapter()
        logger.info("✅ MCP Adapter created successfully")
        
        # Test 3: Import MCP Abstraction
        logger.info("📋 Test 3: Import MCP Abstraction")
        
        from foundations.public_works_foundation.infrastructure_abstractions.mcp_abstraction import MCPAbstraction
        
        # Create MCP abstraction
        mcp_abstraction = MCPAbstraction(mcp_adapter)
        logger.info("✅ MCP Abstraction created successfully")
        
        # Test 4: Import MCP Composition Service
        logger.info("📋 Test 4: Import MCP Composition Service")
        
        from foundations.public_works_foundation.composition_services.mcp_composition_service import MCPCompositionService
        
        # Create MCP composition service
        mcp_composition_service = MCPCompositionService(mcp_abstraction)
        logger.info("✅ MCP Composition Service created successfully")
        
        # Test 5: Import MCP Client Manager (Business Service)
        logger.info("📋 Test 5: Import MCP Client Manager (Business Service)")
        
        from foundations.agentic_foundation.business_services.mcp_client_manager import MCPClientManager
        
        # Create MCP Client Manager
        mcp_client_manager = MCPClientManager(mcp_adapter)
        logger.info("✅ MCP Client Manager created successfully")
        
        # Test 6: Verify Architecture
        logger.info("📋 Test 6: Verify Architecture")
        
        # Test MCP adapter health
        adapter_health = mcp_adapter.get_adapter_health()
        if adapter_health.get("adapter_name") != "MCPAdapter":
            logger.error("❌ MCP Adapter not properly identified")
            return False
        
        logger.info("✅ MCP Adapter architecture verified")
        
        # Test MCP abstraction health
        abstraction_health = mcp_abstraction.get_abstraction_health()
        if abstraction_health.get("abstraction_name") != "MCPAbstraction":
            logger.error("❌ MCP Abstraction not properly identified")
            return False
        
        logger.info("✅ MCP Abstraction architecture verified")
        
        # Test MCP composition service health
        composition_health = mcp_composition_service.get_composition_health()
        if composition_health.get("service_name") != "MCPCompositionService":
            logger.error("❌ MCP Composition Service not properly identified")
            return False
        
        logger.info("✅ MCP Composition Service architecture verified")
        
        # Test MCP Client Manager health
        manager_health = mcp_client_manager.get_manager_health()
        if manager_health.get("service_type") != "business_service":
            logger.error("❌ MCP Client Manager not properly identified as business service")
            return False
        
        if manager_health.get("realm") != "agentic":
            logger.error("❌ MCP Client Manager not properly identified as agentic realm")
            return False
        
        logger.info("✅ MCP Client Manager architecture verified")
        
        # Test 7: Basic Functionality
        logger.info("📋 Test 7: Basic Functionality")
        
        # Test tenant context
        tenant_context = {
            "tenant_id": "test_tenant_123",
            "user_id": "test_user_456"
        }
        
        await mcp_client_manager.set_tenant_context(tenant_context)
        logger.info("✅ Tenant context set successfully")
        
        # Test manager health after tenant context
        manager_health = mcp_client_manager.get_manager_health()
        if manager_health.get("tenant_context") != tenant_context:
            logger.error("❌ Tenant context not properly stored")
            return False
        
        logger.info("✅ Tenant context functionality verified")
        
        logger.info("🎉 MCP Architecture refactoring test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP architecture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run MCP architecture test."""
    logger.info("🚀 Starting MCP Architecture Test")
    
    success = await test_mcp_architecture()
    
    if success:
        logger.info("🎉 MCP architecture test passed!")
        return True
    else:
        logger.error("❌ MCP architecture test failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


