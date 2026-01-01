#!/usr/bin/env python3
"""
Delivery Manager Integration Test

Test the Delivery Manager cross-realm coordination functionality.
"""

import asyncio
import logging
from datetime import datetime

from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext
from config.environment_loader import EnvironmentLoader

# Import Delivery Manager
from backend.business_enablement.roles.delivery_manager.delivery_manager_service import DeliveryManagerService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_delivery_manager_integration():
    """Test Delivery Manager integration and functionality."""
    logger.info("🚀 Starting Delivery Manager Integration Test")
    
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
        
        # Initialize Delivery Manager Service
        logger.info("🚚 Initializing Delivery Manager Service...")
        delivery_manager = DeliveryManagerService(environment=environment)
        await delivery_manager.initialize()
        
        logger.info("✅ Delivery Manager Service initialized successfully")
        
        # Test 1: Coordinate Cross-Realm
        logger.info("🌐 Testing Cross-Realm Coordination...")
        coordination_response = await delivery_manager.coordinate_cross_realm(
            coordination_data={
                "realms": ["business_enablement", "smart_city", "experience"],
                "action": "workflow_coordination",
                "workflow_id": "test_workflow_123"
            },
            user_context=user_context
        )
        logger.info(f"✅ Cross-Realm Coordination Response: {coordination_response.get('success')}")
        logger.info(f"   Coordination ID: {coordination_response.get('coordination_id')}")
        logger.info(f"   Realms Involved: {coordination_response.get('realms_involved')}")
        
        # Test 2: Route to Realm
        logger.info("🔄 Testing Realm Routing...")
        routing_response = await delivery_manager.route_to_realm(
            target_realm="business_enablement",
            request_data={
                "action": "pillar_coordination",
                "pillar": "content",
                "request_type": "file_upload"
            },
            user_context=user_context
        )
        logger.info(f"✅ Realm Routing Response: {routing_response.get('success')}")
        logger.info(f"   Target Realm: {routing_response.get('target_realm')}")
        logger.info(f"   Routed: {routing_response.get('routed')}")
        
        # Test 3: Discover Realm Services
        logger.info("🔍 Testing Realm Service Discovery...")
        discovery_response = await delivery_manager.discover_realm_services(
            realm="smart_city",
            user_context=user_context
        )
        logger.info(f"✅ Realm Service Discovery Response: {discovery_response.get('success')}")
        logger.info(f"   Realm: {discovery_response.get('realm')}")
        logger.info(f"   Services: {discovery_response.get('services', [])}")
        
        # Test 4: Manage Cross-Realm State
        logger.info("📊 Testing Cross-Realm State Management...")
        state_response = await delivery_manager.manage_cross_realm_state(
            state_data={
                "state_type": "workflow_progress",
                "workflow_id": "test_workflow_123",
                "current_step": "content_processing",
                "realms": ["business_enablement", "smart_city"]
            },
            user_context=user_context
        )
        logger.info(f"✅ Cross-Realm State Management Response: {state_response.get('success')}")
        logger.info(f"   State Managed: {state_response.get('state_managed')}")
        
        # Test 5: Get Cross-Realm Health
        logger.info("❤️ Testing Cross-Realm Health Check...")
        health_response = await delivery_manager.get_cross_realm_health()
        logger.info(f"✅ Cross-Realm Health Response: {health_response.get('success')}")
        logger.info(f"   Overall Status: {health_response.get('overall_status')}")
        logger.info(f"   Realms: {health_response.get('realms', {})}")
        
        # Test 6: Health Check
        logger.info("❤️ Testing Delivery Manager Health Check...")
        delivery_health_response = await delivery_manager.health_check()
        logger.info(f"✅ Delivery Manager Health Response: {delivery_health_response.get('status')}")
        logger.info(f"   Capabilities: {delivery_health_response.get('capabilities')}")
        logger.info(f"   Dimension Clients: {delivery_health_response.get('dimension_clients')}")
        
        logger.info("🎉 All Delivery Manager tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Delivery Manager Integration Test failed: {e}")
        raise
    finally:
        # Shutdown Delivery Manager Service
        if 'delivery_manager' in locals() and delivery_manager.is_initialized:
            await delivery_manager.shutdown()
            logger.info("🛑 Delivery Manager Service shutdown successfully")


if __name__ == "__main__":
    asyncio.run(test_delivery_manager_integration())
