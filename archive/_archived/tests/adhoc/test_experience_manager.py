#!/usr/bin/env python3
"""
Test Experience Manager Service

Test script to verify the Experience Manager service works correctly.
"""

import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext
from experience.services.experience_manager_service import ExperienceManagerService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_experience_manager():
    """Test the Experience Manager service."""
    logger.info("🧪 Testing Experience Manager Service...")
    
    try:
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            full_name="Test User",
            email="test@example.com",
            session_id="test_session_123",
            permissions=["read", "write"]
        )
        
        # Initialize Experience Manager
        experience_manager = ExperienceManagerService()
        await experience_manager.initialize()
        
        logger.info("✅ Experience Manager initialized successfully")
        
        # Test 1: Initialize experience session
        logger.info("🧪 Test 1: Initialize experience session")
        session_result = await experience_manager.initialize_experience_session(
            user_context, 
            {"preferences": {"theme": "dark", "language": "en"}}
        )
        
        if session_result.get("success"):
            session_id = session_result.get("session_id")
            logger.info(f"✅ Session created: {session_id}")
            
            # Test 2: Manage UI state
            logger.info("🧪 Test 2: Manage UI state")
            ui_state_result = await experience_manager.manage_user_interface_state(
                session_id,
                {"current_pillar": "content", "ui_components": {"file_upload": "active"}},
                user_context
            )
            
            if ui_state_result.get("success"):
                logger.info("✅ UI state managed successfully")
            else:
                logger.error(f"❌ UI state management failed: {ui_state_result.get('error')}")
            
            # Test 3: Get session state
            logger.info("🧪 Test 3: Get session state")
            session_state_result = await experience_manager.get_session_state(session_id, user_context)
            
            if session_state_result.get("success"):
                logger.info("✅ Session state retrieved successfully")
            else:
                logger.error(f"❌ Session state retrieval failed: {session_state_result.get('error')}")
            
            # Test 4: Route pillar request
            logger.info("🧪 Test 4: Route pillar request")
            pillar_route_result = await experience_manager.route_pillar_request(
                "content",
                {"endpoint": "/content/upload", "method": "POST", "payload": {"file": "test.csv"}},
                user_context
            )
            
            if pillar_route_result.get("success"):
                logger.info("✅ Pillar request routed successfully")
            else:
                logger.error(f"❌ Pillar request routing failed: {pillar_route_result.get('error')}")
            
            # Test 5: Get available pillars
            logger.info("🧪 Test 5: Get available pillars")
            pillars_result = await experience_manager.get_available_pillars(user_context)
            
            if pillars_result.get("success"):
                available_pillars = pillars_result.get("available_pillars", {})
                logger.info(f"✅ Available pillars: {list(available_pillars.keys())}")
            else:
                logger.error(f"❌ Get available pillars failed: {pillars_result.get('error')}")
            
            # Test 6: Health check
            logger.info("🧪 Test 6: Health check")
            health_result = await experience_manager.health_check()
            
            if health_result.get("status") == "healthy":
                logger.info("✅ Health check passed")
            else:
                logger.error(f"❌ Health check failed: {health_result}")
            
            # Test 7: Terminate session
            logger.info("🧪 Test 7: Terminate session")
            terminate_result = await experience_manager.terminate_experience_session(session_id, user_context)
            
            if terminate_result.get("success"):
                logger.info("✅ Session terminated successfully")
            else:
                logger.error(f"❌ Session termination failed: {terminate_result.get('error')}")
        
        else:
            logger.error(f"❌ Session creation failed: {session_result.get('error')}")
        
        # Shutdown Experience Manager
        await experience_manager.shutdown()
        logger.info("✅ Experience Manager shutdown successfully")
        
        logger.info("🎉 All Experience Manager tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Experience Manager test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_experience_manager())
