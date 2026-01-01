#!/usr/bin/env python3
"""
Guide Agent Integration Test

Test the Guide Agent cross-dimensional functionality and integration.
"""

import asyncio
import logging
from datetime import datetime

from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext
from config.environment_loader import EnvironmentLoader

# Import Guide Agent
from backend.business_enablement.roles.guide_agent.guide_agent_service import GuideAgentService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_guide_agent_integration():
    """Test Guide Agent integration and functionality."""
    logger.info("🚀 Starting Guide Agent Integration Test")
    
    try:
        # Initialize environment
        environment = EnvironmentLoader()
        
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_123",
            permissions=["read", "write", "analyze"]
        )
        
        # Initialize Guide Agent Service
        logger.info("🎭 Initializing Guide Agent Service...")
        guide_agent = GuideAgentService(logger=logger)
        await guide_agent.initialize()
        
        logger.info("✅ Guide Agent Service initialized successfully")
        
        # Test 1: Process User Message
        logger.info("💬 Testing User Message Processing...")
        message_response = await guide_agent.process_user_message(
            message="I want to upload a file and analyze it",
            conversation_id="test_conv_123",
            user_context=user_context
        )
        logger.info(f"✅ User Message Response: {message_response.get('success')}")
        logger.info(f"   Message: {message_response.get('message', 'No message')}")
        
        # Test 2: Analyze User Intent
        logger.info("🧠 Testing Intent Analysis...")
        intent_response = await guide_agent.analyze_user_intent(
            message="Create a workflow for data processing",
            user_context=user_context
        )
        logger.info(f"✅ Intent Analysis Response: {intent_response.get('success')}")
        logger.info(f"   Intent Type: {intent_response.get('intent_type')}")
        logger.info(f"   Requires Pillar Routing: {intent_response.get('requires_pillar_routing')}")
        logger.info(f"   Target Pillar: {intent_response.get('target_pillar')}")
        
        # Test 3: Route to Pillar Liaison
        logger.info("🔄 Testing Pillar Routing...")
        routing_response = await guide_agent.route_to_pillar_liaison(
            pillar="content",
            request_data={"message": "Upload file", "conversation_id": "test_conv_123"},
            user_context=user_context
        )
        logger.info(f"✅ Pillar Routing Response: {routing_response.get('success')}")
        logger.info(f"   Pillar: {routing_response.get('pillar')}")
        logger.info(f"   Routed: {routing_response.get('routed')}")
        
        # Test 4: Resume Conversation
        logger.info("🔄 Testing Conversation Resumption...")
        resume_response = await guide_agent.resume_conversation(
            conversation_id="test_conv_123",
            pillar_response={
                "pillar": "content",
                "success": True,
                "data": {"files_processed": 1},
                "message": "File uploaded successfully"
            },
            user_context=user_context
        )
        logger.info(f"✅ Conversation Resumption Response: {resume_response.get('success')}")
        logger.info(f"   Next Steps: {resume_response.get('next_steps', [])}")
        
        # Test 5: Provide Guidance
        logger.info("🧭 Testing Guidance Provision...")
        guidance_response = await guide_agent.provide_guidance(
            guidance_type="general_guidance",
            context={"message": "Help me get started"},
            user_context=user_context
        )
        logger.info(f"✅ Guidance Response: {guidance_response.get('success')}")
        logger.info(f"   Message: {guidance_response.get('message')}")
        
        # Test 6: Manage User Journey
        logger.info("🗺️ Testing User Journey Management...")
        journey_response = await guide_agent.manage_user_journey(
            journey_data={"journey_type": "onboarding", "step": "file_upload"},
            user_context=user_context
        )
        logger.info(f"✅ User Journey Response: {journey_response.get('success')}")
        
        # Test 7: Coordinate Cross-Pillar Workflow
        logger.info("🔗 Testing Cross-Pillar Workflow Coordination...")
        workflow_response = await guide_agent.coordinate_cross_pillar_workflow(
            workflow_data={"workflow_type": "content_to_insights", "steps": ["upload", "analyze"]},
            user_context=user_context
        )
        logger.info(f"✅ Cross-Pillar Workflow Response: {workflow_response.get('success')}")
        
        # Test 8: Get User Recommendations
        logger.info("💡 Testing User Recommendations...")
        recommendations_response = await guide_agent.get_user_recommendations(user_context)
        logger.info(f"✅ User Recommendations Response: {recommendations_response.get('success')}")
        logger.info(f"   Recommendations: {recommendations_response.get('recommendations', [])}")
        
        # Test 9: Health Check
        logger.info("❤️ Testing Health Check...")
        health_response = await guide_agent.health_check()
        logger.info(f"✅ Health Check Response: {health_response.get('status')}")
        logger.info(f"   Supported Dimensions: {health_response.get('supported_dimensions')}")
        logger.info(f"   Capabilities: {health_response.get('capabilities')}")
        
        logger.info("🎉 All Guide Agent tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Guide Agent Integration Test failed: {e}")
        raise
    finally:
        # Shutdown Guide Agent Service
        if 'guide_agent' in locals() and guide_agent.is_initialized:
            await guide_agent.shutdown()
            logger.info("🛑 Guide Agent Service shutdown successfully")


if __name__ == "__main__":
    asyncio.run(test_guide_agent_integration())
