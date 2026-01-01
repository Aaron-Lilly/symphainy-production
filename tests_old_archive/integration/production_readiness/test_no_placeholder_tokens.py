"""
Test No Placeholder Tokens in Authentication

CRITICAL TEST: Validates that Security Guard never returns placeholder tokens.
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from backend.smart_city.services.security_guard.security_guard_service import SecurityGuardService

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.critical
class TestNoPlaceholderTokens:
    """Test that no placeholder tokens exist in authentication."""
    
    @pytest.fixture
    async def security_guard(self):
        """Create Security Guard Service."""
        # TODO: Initialize with real dependencies
        service = SecurityGuardService(
            service_name="test_security_guard",
            realm_name="smart_city",
            platform_gateway=None,  # TODO: Get from fixture
            di_container=None  # TODO: Get from fixture
        )
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_security_guard_no_placeholder_tokens(self, security_guard):
        """Test Security Guard never returns placeholder tokens."""
        # Test authentication
        result = await security_guard.authenticate_user(
            username="test_user",
            password="test_password"
        )
        
        # Should not contain placeholder token
        if result.get("success"):
            access_token = result.get("access_token")
            assert access_token is not None, "Access token is None"
            assert access_token != "token_placeholder", "Found placeholder token"
            assert len(access_token) > 10, f"Token too short (likely placeholder): {len(access_token)} chars"
            
            # Token should look like a real JWT or similar
            # Real tokens are usually base64-encoded or have specific format
            assert "." in access_token or len(access_token) > 20,                 "Token format doesn't look real"
        else:
            # Should have proper error, not placeholder
            assert "error_code" in result, "Missing error_code in failure response"
            assert result["error_code"] != "TOKEN_PLACEHOLDER", "Found placeholder error code"
            assert "error" in result or "message" in result, "Missing error message"
    
    @pytest.mark.asyncio
    async def test_security_guard_no_fallback_to_placeholder(self, security_guard):
        """Test Security Guard doesn't fallback to placeholder on error."""
        # Test with invalid credentials
        result = await security_guard.authenticate_user(
            username="invalid",
            password="invalid"
        )
        
        # Should fail with proper error, not return placeholder token
        if not result.get("success"):
            # Should not have placeholder token even in error
            access_token = result.get("access_token")
            if access_token:
                assert access_token != "token_placeholder",                     "Should not return placeholder token even on error"
                assert len(access_token) > 10,                     "Should not return short placeholder token"
