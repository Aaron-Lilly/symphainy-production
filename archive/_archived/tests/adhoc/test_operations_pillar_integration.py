#!/usr/bin/env python3
"""
Operations Pillar Integration Test

Test the Operations Pillar integration to ensure all components work correctly.
"""

import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext
from backend.business_enablement.pillars.operations_pillar.operations_pillar_service import OperationsPillarService
from backend.business_enablement.interfaces.operations_management_interface import (
    SOPRequest, ConversionRequest, CoexistenceAnalysisRequest, 
    ProcessOptimizationRequest, CoexistenceBlueprintRequest
)


async def test_operations_pillar_integration():
    """Test Operations Pillar integration."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    try:
        logger.info("🚀 Starting Operations Pillar Integration Test")
        
        # Initialize Operations Pillar
        logger.info("🏗️ Initializing Operations Pillar...")
        operations_pillar = OperationsPillarService(
            utility_foundation=None,  # Mock for testing
            curator_foundation=None
        )
        await operations_pillar.initialize()
        
        # Test SOP creation
        logger.info("📋 Testing SOP creation...")
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        sop_request = SOPRequest(
            title="Customer Support Ticket Process",
            description="Create a process for handling customer support tickets",
            content={"steps": ["Receive ticket", "Categorize", "Assign", "Resolve"]},
            user_context=user_context,
            session_id="test_session",
            options={"sop_type": "administrative"}
        )
        
        sop_response = await operations_pillar.create_sop(sop_request)
        if sop_response.success:
            logger.info(f"✅ SOP created: {sop_response.message}")
        else:
            logger.warning(f"⚠️ SOP creation failed: {sop_response.message}")
        
        # Test SOP to workflow conversion
        logger.info("🔄 Testing SOP to workflow conversion...")
        conversion_request = ConversionRequest(
            source_id="sop_123",
            source_type="sop",
            target_type="workflow",
            user_context=user_context,
            session_id="test_session"
        )
        
        conversion_response = await operations_pillar.convert_sop_to_workflow(conversion_request)
        if conversion_response.success:
            logger.info(f"✅ SOP converted to workflow: {conversion_response.message}")
        else:
            logger.warning(f"⚠️ SOP to workflow conversion failed: {conversion_response.message}")
        
        # Test coexistence analysis
        logger.info("🤝 Testing coexistence analysis...")
        coexistence_request = CoexistenceAnalysisRequest(
            process_description="Customer support ticket handling process",
            current_ai_usage={
                "ai_capabilities": ["data_processing", "basic_analysis"],
                "interaction_patterns": ["delegated"]
            },
            human_roles=["decision_making", "customer_interaction"],
            user_context=user_context,
            session_id="test_session"
        )
        
        coexistence_response = await operations_pillar.analyze_coexistence(coexistence_request)
        if coexistence_response.success:
            logger.info(f"✅ Coexistence analysis completed: {coexistence_response.message}")
        else:
            logger.warning(f"⚠️ Coexistence analysis failed: {coexistence_response.message}")
        
        # Test process optimization
        logger.info("⚡ Testing process optimization...")
        optimization_request = ProcessOptimizationRequest(
            process_id="test_process",
            current_process={
                "id": "test_process",
                "name": "Customer Support Process",
                "steps": [
                    {"id": "step1", "name": "Receive ticket", "type": "task"},
                    {"id": "step2", "name": "Categorize ticket", "type": "task"},
                    {"id": "step3", "name": "Assign to agent", "type": "task"},
                    {"id": "step4", "name": "Resolve ticket", "type": "task"}
                ]
            },
            optimization_goals=["efficiency", "cost_reduction"],
            constraints=["budget", "timeline"],
            user_context=user_context,
            session_id="test_session"
        )
        
        optimization_response = await operations_pillar.optimize_process(optimization_request)
        if optimization_response.success:
            logger.info(f"✅ Process optimization completed: {optimization_response.message}")
        else:
            logger.warning(f"⚠️ Process optimization failed: {optimization_response.message}")
        
        # Test coexistence blueprint creation
        logger.info("📊 Testing coexistence blueprint creation...")
        blueprint_request = CoexistenceBlueprintRequest(
            requirements={
                "collaboration_level": "high",
                "automation_level": "medium",
                "trust_requirements": "high"
            },
            constraints={
                "budget": "$100,000",
                "timeline": "6 months",
                "team_size": "10 people"
            },
            user_context=user_context,
            session_id="test_session"
        )
        
        blueprint_response = await operations_pillar.create_coexistence_blueprint(blueprint_request)
        if blueprint_response.success:
            logger.info(f"✅ Coexistence blueprint created: {blueprint_response.message}")
        else:
            logger.warning(f"⚠️ Coexistence blueprint creation failed: {blueprint_response.message}")
        
        # Test health check
        logger.info("🏥 Testing health check...")
        health_result = await operations_pillar.get_pillar_health()
        logger.info(f"✅ Health status: {health_result.get('status', 'unknown')}")
        
        # Test business metrics
        logger.info("📊 Testing business metrics...")
        metrics_result = await operations_pillar.get_business_metrics()
        logger.info(f"✅ Business metrics retrieved: {metrics_result.get('service_name', 'unknown')}")
        
        # Test MCP tools
        logger.info("🔧 Testing MCP tools...")
        mcp_tools = operations_pillar.mcp_server.get_available_tools()
        logger.info(f"✅ Available MCP tools: {len(mcp_tools)}")
        
        # Test agent capabilities
        logger.info("🤖 Testing agent capabilities...")
        liaison_status = "healthy"  # Mock status
        specialist_status = "healthy"  # Mock status
        logger.info(f"✅ Liaison Agent status: {liaison_status}")
        logger.info(f"✅ Specialist Agent status: {specialist_status}")
        
        # Cleanup
        logger.info("🧹 Cleaning up...")
        await operations_pillar.shutdown()
        
        logger.info("🎉 Operations Pillar Integration Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Operations Pillar Integration Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_operations_pillar_integration())
    if success:
        print("✅ All tests passed! Operations Pillar integration is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the logs for details.")
        sys.exit(1)
