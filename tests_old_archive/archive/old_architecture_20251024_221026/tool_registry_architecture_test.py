#!/usr/bin/env python3
"""
Tool Registry Architecture Test

Tests the refactored Tool Registry following the 5-layer pattern with
Curator Foundation integration for distributed tool discovery.
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

async def test_tool_registry_architecture():
    """Test the refactored Tool Registry architecture."""
    try:
        logger.info("🧪 Testing Tool Registry Architecture - 5-Layer Pattern with Curator Integration")
        
        # Test 1: Import Tool Storage Infrastructure
        logger.info("📋 Test 1: Import Tool Storage Infrastructure")
        
        from foundations.public_works_foundation.abstraction_contracts.tool_storage_protocol import (
            ToolStorageProtocol, ToolDefinition
        )
        from foundations.public_works_foundation.infrastructure_adapters.arangodb_tool_storage_adapter import ArangoDBToolStorageAdapter
        from foundations.public_works_foundation.infrastructure_abstractions.tool_storage_abstraction import ToolStorageAbstraction
        
        logger.info("✅ Tool storage infrastructure imported successfully")
        
        # Test 2: Create Tool Storage Infrastructure
        logger.info("📋 Test 2: Create Tool Storage Infrastructure")
        
        # Create tool storage adapter
        tool_storage_adapter = ArangoDBToolStorageAdapter()
        
        # Create tool storage abstraction
        tool_storage_abstraction = ToolStorageAbstraction(tool_storage_adapter)
        
        logger.info("✅ Tool storage infrastructure created successfully")
        
        # Test 3: Import Tool Business Services
        logger.info("📋 Test 3: Import Tool Business Services")
        
        from foundations.agentic_foundation.business_services.tool_registry_service import ToolRegistryService
        from foundations.agentic_foundation.business_services.tool_discovery_service import ToolDiscoveryService
        
        logger.info("✅ Tool business services imported successfully")
        
        # Test 4: Create Tool Business Services
        logger.info("📋 Test 4: Create Tool Business Services")
        
        # Create tool registry service
        tool_registry_service = ToolRegistryService(tool_storage_abstraction)
        
        # Create tool discovery service
        tool_discovery_service = ToolDiscoveryService(tool_registry_service)
        
        logger.info("✅ Tool business services created successfully")
        
        # Test 5: Test Tool Registration
        logger.info("📋 Test 5: Test Tool Registration")
        
        # Create test tool definition
        test_tool = ToolDefinition(
            name="test_analysis_tool",
            version="1.0.0",
            description="Test analysis tool for architecture validation",
            parameters={
                "input_data": {"type": "string", "required": True},
                "analysis_type": {"type": "string", "required": True}
            },
            returns={"result": {"type": "object"}},
            tags=["analysis", "test", "validation"],
            realm="agentic",
            pillar="agentic",
            owner_agent="test_agent"
        )
        
        # Register tool
        register_result = await tool_registry_service.register_tool(
            tool_definition=test_tool,
            agent_id="test_agent",
            tenant_context={"realm": "agentic", "pillar": "agentic"}
        )
        
        if not register_result.get("success", False):
            logger.error(f"❌ Tool registration failed: {register_result}")
            return False
        
        logger.info("✅ Tool registration test passed")
        
        # Test 6: Test Tool Discovery
        logger.info("📋 Test 6: Test Tool Discovery")
        
        # Discover tools by capability
        discovered_tools = await tool_discovery_service.discover_tools_by_capability(
            capability_name="analysis",
            realm="agentic",
            tenant_context={"realm": "agentic", "pillar": "agentic"}
        )
        
        if len(discovered_tools) == 0:
            logger.error("❌ No tools discovered")
            return False
        
        logger.info(f"✅ Discovered {len(discovered_tools)} tools")
        
        # Test 7: Test Tool Retrieval
        logger.info("📋 Test 7: Test Tool Retrieval")
        
        # Get specific tool
        retrieved_tool = await tool_registry_service.get_tool(
            tool_name="test_analysis_tool",
            version="1.0.0",
            agent_id="test_agent"
        )
        
        if not retrieved_tool:
            logger.error("❌ Failed to retrieve tool")
            return False
        
        if retrieved_tool.name != "test_analysis_tool":
            logger.error("❌ Retrieved tool name mismatch")
            return False
        
        logger.info("✅ Tool retrieval test passed")
        
        # Test 8: Test Tool Discovery by Tags
        logger.info("📋 Test 8: Test Tool Discovery by Tags")
        
        # Discover tools by tags
        tagged_tools = await tool_discovery_service.discover_tools_by_tags(
            tags=["analysis", "test"],
            realm="agentic",
            tenant_context={"realm": "agentic", "pillar": "agentic"}
        )
        
        if len(tagged_tools) == 0:
            logger.error("❌ No tools discovered by tags")
            return False
        
        logger.info(f"✅ Discovered {len(tagged_tools)} tools by tags")
        
        # Test 9: Test Tool Discovery by Agent
        logger.info("📋 Test 9: Test Tool Discovery by Agent")
        
        # Discover tools by agent
        agent_tools = await tool_discovery_service.discover_tools_by_agent(
            agent_id="test_agent",
            tenant_context={"realm": "agentic", "pillar": "agentic"}
        )
        
        if len(agent_tools) == 0:
            logger.error("❌ No tools discovered for agent")
            return False
        
        logger.info(f"✅ Discovered {len(agent_tools)} tools for agent")
        
        # Test 10: Test Business Metrics
        logger.info("📋 Test 10: Test Business Metrics")
        
        # Check registry metrics
        registry_metrics = tool_registry_service.get_business_metrics()
        
        if registry_metrics.get("total_tools_registered", 0) == 0:
            logger.error("❌ Registry metrics not updated")
            return False
        
        # Check discovery metrics
        discovery_metrics = tool_discovery_service.get_business_metrics()
        
        if discovery_metrics.get("total_discovery_requests", 0) == 0:
            logger.error("❌ Discovery metrics not updated")
            return False
        
        logger.info("✅ Business metrics test passed")
        
        # Test 11: Test Architecture Verification
        logger.info("📋 Test 11: Test Architecture Verification")
        
        # Verify registry health
        registry_health = tool_registry_service.get_registry_health()
        
        if registry_health.get("service_type") != "business_service":
            logger.error("❌ Tool Registry not properly identified as business service")
            return False
        
        if registry_health.get("realm") != "agentic":
            logger.error("❌ Tool Registry not properly identified as agentic realm")
            return False
        
        # Verify discovery health
        discovery_health = tool_discovery_service.get_discovery_health()
        
        if discovery_health.get("service_type") != "business_service":
            logger.error("❌ Tool Discovery not properly identified as business service")
            return False
        
        if discovery_health.get("realm") != "agentic":
            logger.error("❌ Tool Discovery not properly identified as agentic realm")
            return False
        
        logger.info("✅ Architecture verification passed")
        
        # Test 12: Test Curator Integration Readiness
        logger.info("📋 Test 12: Test Curator Integration Readiness")
        
        # Test discovery with Curator Foundation (should work even if not available)
        all_tools = await tool_discovery_service.discover_available_tools(
            tenant_context={"realm": "agentic", "pillar": "agentic"}
        )
        
        if not isinstance(all_tools, dict):
            logger.error("❌ Available tools discovery failed")
            return False
        
        if "by_realm" not in all_tools or "by_pillar" not in all_tools:
            logger.error("❌ Available tools organization failed")
            return False
        
        logger.info("✅ Curator integration readiness test passed")
        
        logger.info("🎉 Tool Registry architecture test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool Registry architecture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run Tool Registry architecture test."""
    logger.info("🚀 Starting Tool Registry Architecture Test")
    
    success = await test_tool_registry_architecture()
    
    if success:
        logger.info("🎉 Tool Registry architecture test passed!")
        return True
    else:
        logger.error("❌ Tool Registry architecture test failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


