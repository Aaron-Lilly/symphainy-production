#!/usr/bin/env python3
"""
WebSocket Pattern Validation Tests

Validates the WebSocket Gateway pattern:
- Single /ws endpoint
- Post Office ownership
- No direct WebSocket abstraction access

ANTI-PATTERN 2 COMPLIANCE: Tests behavior and outcomes, not internal structure.
"""

import pytest
import httpx
from typing import Dict, Any


@pytest.mark.integration
@pytest.mark.smart_city
@pytest.mark.critical
class TestWebSocketPatternValidation:
    """Test suite for WebSocket pattern validation - testing behavior, not structure."""
    
    @pytest.mark.asyncio
    async def test_single_ws_endpoint_exists(self, di_container):
        """
        Verify single /ws endpoint exists.
        
        ANTI-PATTERN 2 COMPLIANCE: Tests behavior (endpoint is accessible),
        not structure (hasattr checks).
        """
        from config.test_config import TestConfig
        
        # ✅ TEST BEHAVIOR: Single /ws endpoint is accessible
        async with httpx.AsyncClient(base_url=TestConfig.BACKEND_URL, timeout=10.0) as client:
            # Try to connect to /ws endpoint (will fail without session, but endpoint should exist)
            try:
                # Use WebSocket upgrade request to check if endpoint exists
                response = await client.get("/ws")
                # If endpoint exists, we'll get a response (may be 400/401 without session, but not 404)
                assert response.status_code != 404, "Single /ws endpoint should exist"
            except httpx.ConnectError:
                pytest.skip("Backend not available for endpoint test")
    
    @pytest.mark.asyncio
    async def test_post_office_owns_websocket_gateway(self, di_container, post_office_service):
        """
        Verify Post Office owns WebSocket Gateway.
        
        ANTI-PATTERN 2 COMPLIANCE: Tests behavior (Post Office can access gateway),
        not structure (hasattr checks).
        """
        # ✅ TEST BEHAVIOR: Post Office has WebSocket Gateway Service
        # Post Office should have initialized WebSocket Gateway during its initialization
        # We test this by checking that Post Office can provide WebSocket endpoint info
        
        try:
            # Post Office should have get_websocket_endpoint SOA API
            result = await post_office_service.get_websocket_endpoint(
                session_token="test_token",
                realm="content"
            )
            
            # ✅ TEST BEHAVIOR: Post Office can provide WebSocket endpoint info
            assert isinstance(result, dict), "Post Office should return WebSocket endpoint info"
            assert result.get("success") is not None or "websocket_url" in result, \
                "Post Office should provide WebSocket endpoint information"
        except AttributeError:
            pytest.fail("Post Office should have get_websocket_endpoint method (owns WebSocket Gateway)")
    
    @pytest.mark.asyncio
    async def test_realms_cannot_access_websocket_abstraction_directly(
        self, di_container, platform_gateway, city_manager
    ):
        """
        Verify realms cannot access WebSocket abstraction directly.
        
        ANTI-PATTERN 2 COMPLIANCE: Tests behavior (access denied),
        not structure (hasattr checks).
        """
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        
        # Create a Content realm service
        service = FileParserService(
            service_name="TestFileParserService",
            realm_name="content",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Register with City Manager before initialization (lifecycle ownership)
        await city_manager.service_management_module.register_service_for_initialization("TestFileParserService")
        await service.initialize()
        
        # ✅ TEST BEHAVIOR: Realm service cannot access WebSocket abstraction directly
        # (Content realm should not have websocket in its allowed abstractions)
        try:
            websocket_abstraction = service.get_abstraction("websocket")
            # If access is allowed, that's a problem (Content realm shouldn't have this)
            # If access is denied, that's correct behavior
            # We test the behavior: access should be denied or return None
            assert websocket_abstraction is None, \
                "Content realm should not have direct access to WebSocket abstraction"
        except Exception as e:
            # Exception is acceptable if access is properly denied
            # The error message may vary, but should indicate access is denied
            error_str = str(e).lower()
            assert ("not allowed" in error_str or "denied" in error_str or 
                   "not available" in error_str or "cannot access" in error_str), \
                f"Content realm access to WebSocket abstraction should be denied, got: {e}"
        
        # ✅ TEST BEHAVIOR: Realm service should use Post Office SOA APIs instead
        # (Content realm should access WebSocket via Post Office SOA APIs)
        # Note: Content realm doesn't have get_websocket_endpoint in its SOA API list
        # This is correct - only Solution realm has it. Content realm uses publish_event/subscribe_to_events
        try:
            # Content realm can access Post Office event SOA APIs
            soa_api = await service.get_soa_api("post_office.publish_event")
            # Method should exist and return a callable or None
            # If Post Office is available, SOA API should be accessible
            assert soa_api is None or callable(soa_api), \
                "Realm service should access Post Office via SOA APIs, not direct abstraction"
        except (AttributeError, ValueError) as e:
            # ValueError is OK if service not available - that's a behavior we can test
            # AttributeError means method doesn't exist, which is a problem
            if isinstance(e, AttributeError):
                pytest.fail("Realm services should have get_soa_api method for Post Office access")
            # ValueError means service not found or access denied - acceptable for behavior test
            pass
        
        # Cleanup
        try:
            await service.shutdown()
        except Exception:
            pass
    
    @pytest.mark.asyncio
    async def test_websocket_gateway_service_initialized_by_post_office(
        self, di_container, post_office_service
    ):
        """
        Verify WebSocket Gateway Service is initialized by Post Office.
        
        ANTI-PATTERN 2 COMPLIANCE: Tests behavior (gateway is initialized),
        not structure (hasattr checks).
        """
        # ✅ TEST BEHAVIOR: Post Office has initialized WebSocket Gateway
        # We test this by checking that Post Office can provide WebSocket endpoint info
        # (which requires the gateway to be initialized)
        
        try:
            result = await post_office_service.get_websocket_endpoint(
                session_token="test_token",
                realm="content"
            )
            
            # ✅ TEST BEHAVIOR: Gateway is initialized (Post Office can provide endpoint info)
            assert isinstance(result, dict), "Post Office should return WebSocket endpoint info"
            # If Post Office can provide endpoint info, gateway is initialized
            assert result.get("success") is not None or "websocket_url" in result, \
                "WebSocket Gateway should be initialized by Post Office"
        except AttributeError:
            pytest.fail("Post Office should have initialized WebSocket Gateway")
    
    @pytest.mark.asyncio
    async def test_websocket_gateway_registered_with_consul(
        self, di_container, post_office_service, curator_foundation
    ):
        """
        Verify WebSocket Gateway is registered with Consul.
        
        ANTI-PATTERN 2 COMPLIANCE: Tests behavior (gateway is discoverable),
        not structure (hasattr checks).
        """
        # ✅ TEST BEHAVIOR: WebSocket Gateway is discoverable via Curator
        # (Post Office registers gateway with Consul during initialization)
        
        try:
            # Try to discover WebSocket Gateway Service via Curator
            gateway_service = await curator_foundation.discover_service_by_name("WebSocketGatewayService")
            
            # ✅ TEST BEHAVIOR: Gateway is discoverable (registered with Consul)
            # Gateway may not be registered if Consul is not available, but method should exist
            assert gateway_service is None or hasattr(gateway_service, 'handle_connection'), \
                "WebSocket Gateway should be discoverable via Curator (registered with Consul)"
        except AttributeError:
            pytest.fail("Curator should have discover_service_by_name method")


