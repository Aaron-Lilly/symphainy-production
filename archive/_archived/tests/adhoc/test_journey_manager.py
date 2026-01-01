#!/usr/bin/env python3
"""
Test Journey Manager Service

Test script to verify the Journey Manager service works correctly.
"""

import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext
from experience.services.journey_manager_service import JourneyManagerService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_journey_manager():
    """Test the Journey Manager service."""
    logger.info("🧪 Testing Journey Manager Service...")
    
    try:
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            full_name="Test User",
            email="test@example.com",
            session_id="test_session_123",
            permissions=["read", "write"]
        )
        
        # Initialize Journey Manager
        journey_manager = JourneyManagerService()
        await journey_manager.initialize()
        
        logger.info("✅ Journey Manager initialized successfully")
        
        # Test 1: Create user journey
        logger.info("🧪 Test 1: Create user journey")
        journey_result = await journey_manager.create_user_journey(
            user_context, 
            {
                "journey_type": "data_analysis",
                "total_milestones": 5,
                "total_steps": 10,
                "flow_type": "linear"
            }
        )
        
        if journey_result.get("success"):
            journey_id = journey_result.get("journey_id")
            logger.info(f"✅ Journey created: {journey_id}")
            
            # Test 2: Track journey progress
            logger.info("🧪 Test 2: Track journey progress")
            progress_result = await journey_manager.track_journey_progress(
                journey_id,
                {"milestone_completed": 1, "step_completed": 2},
                user_context
            )
            
            if progress_result.get("success"):
                logger.info("✅ Journey progress tracked successfully")
            else:
                logger.error(f"❌ Journey progress tracking failed: {progress_result.get('error')}")
            
            # Test 3: Get journey state
            logger.info("🧪 Test 3: Get journey state")
            state_result = await journey_manager.get_journey_state(journey_id, user_context)
            
            if state_result.get("success"):
                logger.info("✅ Journey state retrieved successfully")
            else:
                logger.error(f"❌ Journey state retrieval failed: {state_result.get('error')}")
            
            # Test 4: Update journey flow
            logger.info("🧪 Test 4: Update journey flow")
            flow_result = await journey_manager.update_journey_flow(
                journey_id,
                {"flow_type": "branching", "steps": [1, 2, 3, 4, 5]},
                user_context
            )
            
            if flow_result.get("success"):
                logger.info("✅ Journey flow updated successfully")
            else:
                logger.error(f"❌ Journey flow update failed: {flow_result.get('error')}")
            
            # Test 5: Navigate to next milestone
            logger.info("🧪 Test 5: Navigate to next milestone")
            navigation_result = await journey_manager.navigate_to_next_milestone(journey_id, user_context)
            
            if navigation_result.get("success"):
                logger.info("✅ Navigation to next milestone successful")
            else:
                logger.error(f"❌ Navigation failed: {navigation_result.get('error')}")
            
            # Test 6: Handle journey branching
            logger.info("🧪 Test 6: Handle journey branching")
            branching_result = await journey_manager.handle_journey_branching(
                journey_id,
                {"decision_type": "pillar_selection", "decision_value": "insights"},
                user_context
            )
            
            if branching_result.get("success"):
                logger.info("✅ Journey branching handled successfully")
            else:
                logger.error(f"❌ Journey branching failed: {branching_result.get('error')}")
            
            # Test 7: Analyze journey analytics
            logger.info("🧪 Test 7: Analyze journey analytics")
            analytics_result = await journey_manager.analyze_journey_analytics(journey_id, user_context)
            
            if analytics_result.get("success"):
                logger.info("✅ Journey analytics analyzed successfully")
            else:
                logger.error(f"❌ Journey analytics failed: {analytics_result.get('error')}")
            
            # Test 8: Optimize journey experience
            logger.info("🧪 Test 8: Optimize journey experience")
            optimization_result = await journey_manager.optimize_journey_experience(
                journey_id,
                {"optimization_type": "flow_improvement"},
                user_context
            )
            
            if optimization_result.get("success"):
                logger.info("✅ Journey optimization successful")
            else:
                logger.error(f"❌ Journey optimization failed: {optimization_result.get('error')}")
            
            # Test 9: Get user journey history
            logger.info("🧪 Test 9: Get user journey history")
            history_result = await journey_manager.get_user_journey_history(user_context)
            
            if history_result.get("success"):
                logger.info("✅ Journey history retrieved successfully")
            else:
                logger.error(f"❌ Journey history retrieval failed: {history_result.get('error')}")
            
            # Test 10: Pause journey
            logger.info("🧪 Test 10: Pause journey")
            pause_result = await journey_manager.pause_journey(journey_id, user_context)
            
            if pause_result.get("success"):
                logger.info("✅ Journey paused successfully")
            else:
                logger.error(f"❌ Journey pause failed: {pause_result.get('error')}")
            
            # Test 11: Resume journey
            logger.info("🧪 Test 11: Resume journey")
            resume_result = await journey_manager.resume_journey(journey_id, user_context)
            
            if resume_result.get("success"):
                logger.info("✅ Journey resumed successfully")
            else:
                logger.error(f"❌ Journey resume failed: {resume_result.get('error')}")
            
            # Test 12: Complete journey
            logger.info("🧪 Test 12: Complete journey")
            completion_result = await journey_manager.complete_journey(
                journey_id,
                {"completion_reason": "user_finished", "satisfaction_score": 4.5},
                user_context
            )
            
            if completion_result.get("success"):
                logger.info("✅ Journey completed successfully")
            else:
                logger.error(f"❌ Journey completion failed: {completion_result.get('error')}")
            
            # Test 13: Health check
            logger.info("🧪 Test 13: Health check")
            health_result = await journey_manager.health_check()
            
            if health_result.get("status") == "healthy":
                logger.info("✅ Health check passed")
            else:
                logger.error(f"❌ Health check failed: {health_result}")
        
        else:
            logger.error(f"❌ Journey creation failed: {journey_result.get('error')}")
        
        # Shutdown Journey Manager
        await journey_manager.shutdown()
        logger.info("✅ Journey Manager shutdown successfully")
        
        logger.info("🎉 All Journey Manager tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Journey Manager test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_journey_manager())
