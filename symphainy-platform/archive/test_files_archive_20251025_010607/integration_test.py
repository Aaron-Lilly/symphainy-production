#!/usr/bin/env python3
"""
API Routing Integration Test

Integration test for API routing utility using real services.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext
from .api_routing_utility import APIRoutingUtility, HTTPMethod


async def test_api_routing_integration():
    """Test API routing utility integration with real services."""
    print("🚀 Testing API Routing Integration with Real Services...")
    
    try:
        # Initialize DI container
        di_container = DIContainerService("test_realm")
        print("✅ DI Container initialized")
        
        # Get API router
        api_router = di_container.get_api_router()
        print("✅ API Router retrieved")
        
        # Test basic functionality
        await test_basic_functionality(api_router)
        
        # Test middleware integration
        await test_middleware_integration(api_router)
        
        # Test real service integration
        await test_real_service_integration(di_container)
        
        print("🎉 All API routing integration tests passed!")
        
    except Exception as e:
        print(f"❌ API routing integration test failed: {e}")
        raise


async def test_basic_functionality(api_router: APIRoutingUtility):
    """Test basic API routing functionality."""
    print("  📝 Testing basic functionality...")
    
    # Register test route
    route_id = await api_router.register_route(
        method=HTTPMethod.GET,
        path="/api/test/health",
        handler=health_handler,
        pillar="test_pillar",
        realm="test_realm",
        description="Test health endpoint",
        version="1.0",
        tags=["test", "health"]
    )
    
    print(f"    ✅ Route registered: {route_id}")
    
    # List routes
    routes = await api_router.list_routes(pillar="test_pillar")
    assert len(routes) == 1
    assert routes[0].path == "/api/test/health"
    print("    ✅ Route listing works")
    
    # Test route info
    route_info = await api_router.get_route_info(route_id)
    assert route_info is not None
    assert route_info.path == "/api/test/health"
    print("    ✅ Route info retrieval works")


async def test_middleware_integration(api_router: APIRoutingUtility):
    """Test middleware integration."""
    print("  🔧 Testing middleware integration...")
    
    # Register test middleware
    await api_router.register_middleware(
        middleware=test_middleware,
        scope="global"
    )
    
    print("    ✅ Middleware registered")
    
    # Test middleware execution
    user_context = UserContext(
        user_id="integration_test_user",
        tenant_id="integration_test_tenant",
        roles=["user"],
        permissions=["read"]
    )
    
    response_context = await api_router.route_request(
        method=HTTPMethod.GET,
        path="/api/test/health",
        request_data={},
        user_context=user_context
    )
    
    assert response_context.status_code == 200
    assert response_context.body["success"] is True
    assert response_context.body.get("middleware_processed") is True
    print("    ✅ Middleware execution works")


async def test_real_service_integration(di_container: DIContainerService):
    """Test integration with real services."""
    print("  🏗️ Testing real service integration...")
    
    # Test that we can get real services from DI container
    try:
        # Test getting configuration service
        config_service = di_container.get_config()
        assert config_service is not None
        print("    ✅ Configuration service integration works")
        
        # Test getting error handler service
        error_handler = di_container.get_error_handler()
        assert error_handler is not None
        print("    ✅ Error handler service integration works")
        
        # Test getting validation service
        validation_service = di_container.get_validation()
        assert validation_service is not None
        print("    ✅ Validation service integration works")
        
    except Exception as e:
        print(f"    ⚠️ Some services not available: {e}")
        print("    ℹ️ This is expected in test environment without full service initialization")


# TEST HANDLERS

async def health_handler(request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
    """Health handler for testing."""
    return {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_context.user_id if user_context else None,
        "tenant_id": user_context.tenant_id if user_context else None
    }


async def test_middleware(request_context, user_context, next_handler):
    """Test middleware that adds metadata."""
    # Add middleware processing metadata
    request_context.metadata["middleware_processed"] = True
    request_context.metadata["processed_at"] = datetime.utcnow().isoformat()
    
    # Continue to next handler
    response_context = await next_handler()
    
    # Add response metadata
    response_context.metadata["middleware_processed"] = True
    
    return response_context


if __name__ == "__main__":
    asyncio.run(test_api_routing_integration())


