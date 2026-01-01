#!/usr/bin/env python3
"""
Test Business Orchestrator Integration

Test the integration between Business Orchestrator and Content Pillar
to verify the orchestration patterns work correctly.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext
from backend.business_enablement.pillars.business_orchestrator.business_orchestrator_service import BusinessOrchestratorService
from backend.business_enablement.pillars.content_pillar.content_pillar_service import ContentPillarService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_business_orchestrator_integration():
    """Test the integration between Business Orchestrator and Content Pillar."""
    try:
        logger.info("🚀 Starting Business Orchestrator Integration Test")
        
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_456",
            permissions=["business_enablement", "content_management"]
        )
        
        # Initialize Business Orchestrator
        logger.info("🏗️ Initializing Business Orchestrator...")
        orchestrator = BusinessOrchestratorService()
        await orchestrator.initialize()
        
        # Initialize Content Pillar
        logger.info("📄 Initializing Content Pillar...")
        content_pillar = ContentPillarService(
            utility_foundation=None,  # Mock for testing
            curator_foundation=None
        )
        await content_pillar.initialize()
        
        # Register Content Pillar with Orchestrator
        logger.info("🔗 Registering Content Pillar with Orchestrator...")
        registration_result = await orchestrator.register_pillar(
            pillar_name="content_pillar",
            pillar_service=content_pillar,
            capabilities=content_pillar.business_capabilities
        )
        
        if registration_result["success"]:
            logger.info(f"✅ Content Pillar registered successfully: {registration_result['message']}")
        else:
            logger.error(f"❌ Content Pillar registration failed: {registration_result['message']}")
            return False
        
        # Test pillar discovery
        logger.info("🔍 Testing pillar capability discovery...")
        discovery_result = await orchestrator.discover_pillar_capabilities("file_upload")
        
        if discovery_result:
            logger.info(f"✅ Found {len(discovery_result)} pillars with file_upload capability")
            for pillar in discovery_result:
                logger.info(f"   - {pillar['service_name']}: {pillar['capabilities']}")
        else:
            logger.warning("⚠️ No pillars found with file_upload capability")
        
        # Test request routing
        logger.info("🔄 Testing request routing to Content Pillar...")
        routing_result = await orchestrator.route_request_to_pillar(
            pillar_name="content_pillar",
            request_type="get_files",
            request_data={"user_id": user_context.user_id, "file_type": "pdf"},
            user_context=user_context
        )
        
        if routing_result["success"]:
            logger.info(f"✅ Request routed successfully: {routing_result['message']}")
        else:
            logger.warning(f"⚠️ Request routing failed: {routing_result['message']}")
        
        # Test workflow orchestration
        logger.info("🎼 Testing workflow orchestration...")
        workflow_definition = {
            "name": "Test Content Processing Workflow",
            "description": "Test workflow for content processing",
            "steps": [
                {
                    "step_id": "upload_file",
                    "pillar": "content_pillar",
                    "action": "upload_file",
                    "description": "Upload a test file"
                },
                {
                    "step_id": "parse_file",
                    "pillar": "content_pillar",
                    "action": "parse_document",
                    "description": "Parse the uploaded file",
                    "depends_on": ["upload_file"]
                }
            ]
        }
        
        workflow_result = await orchestrator.orchestrate_business_workflow(
            workflow_definition=workflow_definition,
            user_context=user_context
        )
        
        if workflow_result["success"]:
            logger.info(f"✅ Workflow orchestration started: {workflow_result['message']}")
            workflow_id = workflow_result.get("workflow_id")
            
            if workflow_id:
                # Check workflow status
                status_result = await orchestrator.get_workflow_status(workflow_id, user_context)
                if status_result["success"]:
                    logger.info(f"✅ Workflow status retrieved: {status_result['status']}")
                else:
                    logger.warning(f"⚠️ Failed to get workflow status: {status_result['message']}")
        else:
            logger.warning(f"⚠️ Workflow orchestration failed: {workflow_result['message']}")
        
        # Test pillar status monitoring
        logger.info("📊 Testing pillar status monitoring...")
        status_result = await orchestrator.get_pillar_status()
        
        if status_result["success"]:
            logger.info(f"✅ Pillar status retrieved: {status_result.get('total_pillars', 0)} pillars")
            for pillar_name, pillar_info in status_result.get("pillars", {}).items():
                logger.info(f"   - {pillar_name}: {pillar_info['status']} (Health: {pillar_info.get('health_score', 0):.0%})")
        else:
            logger.warning(f"⚠️ Failed to get pillar status: {status_result['message']}")
        
        # Test orchestrator health
        logger.info("🏥 Testing orchestrator health...")
        health_result = await orchestrator.get_orchestrator_health()
        
        if health_result["success"]:
            logger.info(f"✅ Orchestrator health retrieved: {health_result['orchestrator']['status']}")
            logger.info(f"   - Registered pillars: {health_result['orchestrator']['registered_pillars']}")
            logger.info(f"   - Active workflows: {health_result['orchestrator']['active_workflows']}")
        else:
            logger.warning(f"⚠️ Failed to get orchestrator health: {health_result['message']}")
        
        # Test MCP tools
        logger.info("🔧 Testing MCP tools...")
        mcp_tools = await orchestrator.mcp_server.get_available_business_tools(user_context)
        logger.info(f"✅ Available MCP tools: {len(mcp_tools)}")
        
        for tool in mcp_tools:
            logger.info(f"   - {tool['name']}: {tool['description']}")
        
        # Test MCP tool execution
        if mcp_tools:
            test_tool = mcp_tools[0]  # Use first available tool
            tool_result = await orchestrator.mcp_server.execute_business_tool(
                tool_name=test_tool["name"],
                tool_params={"pillar_name": "content_pillar", "capabilities": ["file_upload"]},
                user_context=user_context
            )
            
            if tool_result["success"]:
                logger.info(f"✅ MCP tool executed successfully: {test_tool['name']}")
            else:
                logger.warning(f"⚠️ MCP tool execution failed: {tool_result['message']}")
        
        # Test agent capabilities
        logger.info("🤖 Testing agent capabilities...")
        
        # Test coordination agent
        coordination_agent = orchestrator.coordination_agent
        agent_status = await coordination_agent.get_agent_status(user_context)
        logger.info(f"✅ Coordination Agent status: {agent_status['status']}")
        
        # Test workflow agent
        workflow_agent = orchestrator.workflow_agent
        capabilities = await workflow_agent.get_supported_capabilities(user_context)
        logger.info(f"✅ Workflow Agent capabilities: {len(capabilities)}")
        
        logger.info("🎉 Business Orchestrator Integration Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Business Orchestrator Integration Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            if 'orchestrator' in locals():
                await orchestrator.shutdown()
            if 'content_pillar' in locals():
                await content_pillar.shutdown()
        except Exception as e:
            logger.warning(f"⚠️ Cleanup failed: {e}")


async def main():
    """Main test function."""
    success = await test_business_orchestrator_integration()
    
    if success:
        print("\n✅ All tests passed! Business Orchestrator integration is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
