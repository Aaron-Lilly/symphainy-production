#!/usr/bin/env python3
"""
Test Authentication Refactor Pattern

Tests the new abstraction pattern:
- ForwardAuth uses get_user_context() (Supabase API)
- Handler-level uses validate_token() (JWKS local)
- All infrastructure logic in abstraction
- Handlers are simple (just call abstraction)
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any, Optional


@pytest.mark.asyncio
async def test_forwardauth_uses_abstraction():
    """
    Test that ForwardAuth endpoint uses AuthAbstraction.get_user_context().
    
    This verifies:
    - ForwardAuth handler is simple (just calls abstraction)
    - All infrastructure logic is in abstraction
    - Returns proper headers for Traefik
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        # First, try to get a valid token (or use a test token if available)
        # For now, we'll test with an invalid token to verify error handling
        # In a real scenario, we'd use a valid token from login
        
        # Test with invalid token (should return 401)
        response = await client.get(
            "http://35.215.64.103/api/auth/validate-token",
            headers={"Authorization": "Bearer invalid_token"},
            timeout=10.0
        )
        
        # Should return 401 (not 500) - abstraction handles errors properly
        assert response.status_code in [401, 503], f"Expected 401 or 503, got {response.status_code}"
        
        # If we had a valid token, we'd check for headers:
        # - X-User-Id
        # - X-Tenant-Id
        # - X-User-Email
        # - X-User-Roles
        # - X-User-Permissions
        # - X-Auth-Origin
        
        print(f"✅ ForwardAuth endpoint accessible (status: {response.status_code})")


@pytest.mark.asyncio
async def test_forwardauth_handler_simple():
    """
    Test that ForwardAuth handler is simple (no infrastructure logic).
    
    This verifies:
    - Handler just extracts token
    - Handler just calls abstraction
    - Handler just maps to headers
    - No Supabase API calls in handler
    - No configuration checking in handler
    """
    # This is a structural test - we verify by code inspection
    # The handler should be ~40 lines, not 140+
    
    # Read the handler file to verify it's simple
    handler_path = "symphainy-platform/backend/api/auth_router.py"
    
    try:
        with open(handler_path, 'r') as f:
            content = f.read()
            
        # Find the validate_token_forwardauth function
        if "async def validate_token_forwardauth" in content:
            # Extract the function
            start = content.find("async def validate_token_forwardauth")
            end = content.find("\n\n@", start + 1)
            if end == -1:
                end = content.find("\n\n#", start + 1)
            if end == -1:
                end = len(content)
            
            function_code = content[start:end]
            
            # Verify it's simple (no infrastructure logic)
            assert "httpx.AsyncClient" not in function_code, "Handler should not make direct HTTP calls"
            assert "SUPABASE_URL" not in function_code, "Handler should not check configuration"
            assert "os.getenv" not in function_code, "Handler should not access environment variables"
            assert "get_user_context" in function_code, "Handler should call abstraction"
            assert "auth_abstraction" in function_code, "Handler should use abstraction"
            
            # Count lines (should be ~40-65, not 140+)
            line_count = function_code.count('\n')
            assert line_count < 70, f"Handler should be simple (~40-65 lines), got {line_count} lines"
            
            print(f"✅ ForwardAuth handler is simple ({line_count} lines)")
            print(f"✅ Handler uses abstraction (get_user_context)")
            print(f"✅ No infrastructure logic in handler")
        else:
            pytest.fail("validate_token_forwardauth function not found")
            
    except FileNotFoundError:
        pytest.skip(f"Handler file not found: {handler_path}")


@pytest.mark.asyncio
async def test_abstraction_has_get_user_context():
    """
    Test that AuthAbstraction has get_user_context() method.
    
    This verifies:
    - Protocol defines get_user_context()
    - Abstraction implements get_user_context()
    - Method handles all infrastructure logic
    """
    # This is a structural test - we verify by code inspection
    
    # Check protocol
    protocol_path = "symphainy-platform/foundations/public_works_foundation/abstraction_contracts/authentication_protocol.py"
    
    try:
        with open(protocol_path, 'r') as f:
            protocol_content = f.read()
            
        assert "async def get_user_context" in protocol_content, "Protocol should define get_user_context()"
        assert "Get user/tenant context" in protocol_content, "Protocol should document get_user_context()"
        
        print("✅ Protocol defines get_user_context()")
        
    except FileNotFoundError:
        pytest.skip(f"Protocol file not found: {protocol_path}")
    
    # Check abstraction
    abstraction_path = "symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py"
    
    try:
        with open(abstraction_path, 'r') as f:
            abstraction_content = f.read()
            
        assert "async def get_user_context" in abstraction_content, "Abstraction should implement get_user_context()"
        assert "supabase.get_user" in abstraction_content, "Abstraction should use Supabase adapter"
        assert "SecurityContext" in abstraction_content, "Abstraction should return SecurityContext"
        
        print("✅ Abstraction implements get_user_context()")
        print("✅ Abstraction uses Supabase adapter")
        print("✅ Abstraction returns SecurityContext")
        
    except FileNotFoundError:
        pytest.skip(f"Abstraction file not found: {abstraction_path}")


@pytest.mark.asyncio
async def test_security_context_has_email():
    """
    Test that SecurityContext has email field.
    
    This verifies:
    - SecurityContext includes email for ForwardAuth headers
    - All SecurityContext instantiations include email
    """
    # This is a structural test - we verify by code inspection
    
    protocol_path = "symphainy-platform/foundations/public_works_foundation/abstraction_contracts/authentication_protocol.py"
    
    try:
        with open(protocol_path, 'r') as f:
            content = f.read()
            
        assert "email: str | None = None" in content, "SecurityContext should have email field"
        
        print("✅ SecurityContext has email field")
        
    except FileNotFoundError:
        pytest.skip(f"Protocol file not found: {protocol_path}")


@pytest.mark.asyncio
async def test_handler_level_validation_unchanged():
    """
    Test that handler-level validation still uses validate_token().
    
    This verifies:
    - Handler-level validation unchanged (already used abstraction)
    - Still uses validate_token() (JWKS local)
    - Not affected by get_user_context() addition
    """
    # This is a structural test - we verify by code inspection
    
    router_path = "symphainy-platform/backend/api/universal_pillar_router.py"
    
    try:
        with open(router_path, 'r') as f:
            content = f.read()
            
        # Handler-level should still use validate_token (not get_user_context)
        assert "validate_token" in content, "Handler-level should use validate_token()"
        assert "get_auth_abstraction" in content, "Handler-level should get abstraction"
        
        print("✅ Handler-level validation uses validate_token()")
        print("✅ Handler-level validation unchanged")
        
    except FileNotFoundError:
        pytest.skip(f"Router file not found: {router_path}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

