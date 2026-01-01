#!/usr/bin/env python3
"""
Test Frontend Integration Service

Tests the Frontend Integration service functionality.
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the service
from experience.services.frontend_integration_service import frontend_integration_service
from experience.interfaces.frontend_integration_interface import APIEndpoint, RequestMethod, DataFormat
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext


async def test_frontend_integration():
    """Test the Frontend Integration service."""
    logger.info("🧪 Testing Frontend Integration Service...")
    
    try:
        # Initialize the service
        await frontend_integration_service.initialize()
        logger.info("✅ Frontend Integration initialized successfully")
        
        # Create test user context
        user_context = UserContext(
            user_id="test_user_123",
            full_name="Test User",
            email="test@example.com",
            session_id="test_session_123",
            permissions=["read", "write"]
        )
        
        # Test 1: Create authenticated headers
        logger.info("🧪 Test 1: Create authenticated headers")
        headers = await frontend_integration_service.create_authenticated_headers(
            user_context, session_token="test_session_token"
        )
        logger.info(f"✅ Headers created: {list(headers.keys())}")
        
        # Test 2: Route API request
        logger.info("🧪 Test 2: Route API request")
        response = await frontend_integration_service.route_api_request(
            endpoint=APIEndpoint.HEALTH_CHECK,
            method=RequestMethod.GET,
            user_context=user_context,
            session_token="test_session_token"
        )
        logger.info(f"✅ API request routed: {response.get('success', False)}")
        
        # Test 3: Transform request data
        logger.info("🧪 Test 3: Transform request data")
        test_data = {"test": "data", "value": 123}
        transformed = await frontend_integration_service.transform_request_data(
            test_data, DataFormat.JSON, DataFormat.JSON
        )
        logger.info(f"✅ Data transformed: {transformed == test_data}")
        
        # Test 4: Transform response data
        logger.info("🧪 Test 4: Transform response data")
        response_data = {"success": True, "data": test_data}
        transformed_response = await frontend_integration_service.transform_response_data(
            response_data, DataFormat.JSON, DataFormat.JSON
        )
        logger.info(f"✅ Response transformed: {transformed_response == response_data}")
        
        # Test 5: Validate request
        logger.info("🧪 Test 5: Validate request")
        validation = await frontend_integration_service.validate_request(
            endpoint=APIEndpoint.CONTENT_UPLOAD,
            method=RequestMethod.POST,
            data=test_data
        )
        logger.info(f"✅ Request validated: {validation.get('valid', False)}")
        
        # Test 6: Handle API error
        logger.info("🧪 Test 6: Handle API error")
        try:
            raise Exception("Test error for error handling")
        except Exception as e:
            error_response = await frontend_integration_service.handle_api_error(
                e, APIEndpoint.CONTENT_UPLOAD, user_context, 
                response_text="Test error response", status_code=500
            )
            logger.info(f"✅ Error handled: {error_response.get('success', False) == False}")
        
        # Test 7: Get API documentation
        logger.info("🧪 Test 7: Get API documentation")
        docs = await frontend_integration_service.get_api_documentation()
        logger.info(f"✅ Documentation retrieved: {len(docs.get('endpoints', {}))} endpoints")
        
        # Test 8: Register webhook
        logger.info("🧪 Test 8: Register webhook")
        webhook_result = await frontend_integration_service.register_webhook(
            endpoint=APIEndpoint.CONTENT_UPLOAD,
            webhook_url="https://example.com/webhook",
            events=["upload_completed", "upload_failed"]
        )
        logger.info(f"✅ Webhook registered: {webhook_result.get('success', False)}")
        
        # Test 9: Unregister webhook
        logger.info("🧪 Test 9: Unregister webhook")
        if webhook_result.get('success'):
            webhook_id = webhook_result.get('webhook_id')
            unregister_result = await frontend_integration_service.unregister_webhook(webhook_id)
            logger.info(f"✅ Webhook unregistered: {unregister_result.get('success', False)}")
        
        # Test 10: Health check
        logger.info("🧪 Test 10: Health check")
        health = await frontend_integration_service.get_service_health()
        logger.info(f"✅ Health check: {health.get('status', 'unknown')}")
        
        logger.info("🎉 All Frontend Integration tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        raise
    finally:
        # Shutdown the service
        await frontend_integration_service.shutdown()
        logger.info("✅ Frontend Integration shutdown successfully")


if __name__ == "__main__":
    asyncio.run(test_frontend_integration())
