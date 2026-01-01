#!/usr/bin/env python3
"""
Test Request-Scoped User Context

This script tests that the new request-scoped user context pattern works correctly.
It simulates a request flow:
1. Set user context at entry point (like FrontendGatewayService.route_frontend_request)
2. Call service methods that should automatically have access to context
3. Verify context is accessible throughout the request lifecycle
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

from utilities.security_authorization.request_context import (
    set_request_user_context,
    get_request_user_context,
    get_user_id,
    get_tenant_id,
    get_permissions,
    clear_request_user_context
)


async def test_request_context_basic():
    """Test basic context setting and retrieval."""
    print("=" * 80)
    print("TEST 1: Basic Context Setting and Retrieval")
    print("=" * 80)
    
    # Set context
    test_context = {
        "user_id": "test-user-123",
        "tenant_id": "test-tenant-456",
        "permissions": ["read", "write", "admin"],
        "email": "test@example.com",
        "roles": ["owner"]
    }
    
    set_request_user_context(test_context)
    
    # Retrieve context
    retrieved = get_request_user_context()
    assert retrieved is not None, "Context should be set"
    assert retrieved["user_id"] == "test-user-123", "User ID should match"
    assert retrieved["tenant_id"] == "test-tenant-456", "Tenant ID should match"
    assert retrieved["permissions"] == ["read", "write", "admin"], "Permissions should match"
    
    # Test convenience methods
    assert get_user_id() == "test-user-123", "get_user_id() should work"
    assert get_tenant_id() == "test-tenant-456", "get_tenant_id() should work"
    assert get_permissions() == ["read", "write", "admin"], "get_permissions() should work"
    
    print("✅ Test 1 PASSED: Basic context operations work correctly")
    print()


async def test_request_context_nested_calls():
    """Test that context is accessible in nested function calls."""
    print("=" * 80)
    print("TEST 2: Context in Nested Function Calls")
    print("=" * 80)
    
    # Set context
    test_context = {
        "user_id": "nested-user",
        "tenant_id": "nested-tenant",
        "permissions": ["read", "write"]
    }
    set_request_user_context(test_context)
    
    # Simulate nested function calls
    async def level_1():
        ctx = get_request_user_context()
        assert ctx is not None, "Context should be available in level_1"
        return await level_2()
    
    async def level_2():
        ctx = get_request_user_context()
        assert ctx is not None, "Context should be available in level_2"
        return await level_3()
    
    async def level_3():
        ctx = get_request_user_context()
        assert ctx is not None, "Context should be available in level_3"
        assert ctx["user_id"] == "nested-user", "User ID should be accessible in level_3"
        return "success"
    
    result = await level_1()
    assert result == "success", "Nested calls should work"
    
    print("✅ Test 2 PASSED: Context is accessible in nested function calls")
    print()


async def test_request_context_clear():
    """Test that clearing context works."""
    print("=" * 80)
    print("TEST 3: Context Clearing")
    print("=" * 80)
    
    # Set context
    test_context = {"user_id": "clear-test-user"}
    set_request_user_context(test_context)
    
    # Verify it's set
    assert get_user_id() == "clear-test-user", "Context should be set"
    
    # Clear context
    clear_request_user_context()
    
    # Verify it's cleared
    assert get_request_user_context() is None, "Context should be cleared"
    assert get_user_id() is None, "get_user_id() should return None after clear"
    
    print("✅ Test 3 PASSED: Context clearing works correctly")
    print()


async def test_request_context_missing():
    """Test behavior when context is not set."""
    print("=" * 80)
    print("TEST 4: Missing Context Handling")
    print("=" * 80)
    
    # Clear any existing context
    clear_request_user_context()
    
    # Try to get context (should return None)
    ctx = get_request_user_context()
    assert ctx is None, "Context should be None when not set"
    
    # Convenience methods should return None or empty list
    assert get_user_id() is None, "get_user_id() should return None"
    assert get_tenant_id() is None, "get_tenant_id() should return None"
    assert get_permissions() == [], "get_permissions() should return empty list"
    
    print("✅ Test 4 PASSED: Missing context is handled gracefully")
    print()


async def test_request_context_update():
    """Test that context can be updated."""
    print("=" * 80)
    print("TEST 5: Context Updates")
    print("=" * 80)
    
    # Set initial context
    initial_context = {
        "user_id": "initial-user",
        "tenant_id": "initial-tenant",
        "permissions": ["read"]
    }
    set_request_user_context(initial_context)
    
    # Verify initial values
    assert get_user_id() == "initial-user", "Initial user ID should be set"
    
    # Update context
    updated_context = {
        "user_id": "updated-user",
        "tenant_id": "updated-tenant",
        "permissions": ["read", "write", "admin"]
    }
    set_request_user_context(updated_context)
    
    # Verify updated values
    assert get_user_id() == "updated-user", "User ID should be updated"
    assert get_tenant_id() == "updated-tenant", "Tenant ID should be updated"
    assert get_permissions() == ["read", "write", "admin"], "Permissions should be updated"
    
    print("✅ Test 5 PASSED: Context can be updated")
    print()


async def simulate_real_request_flow():
    """Simulate a real request flow like FrontendGatewayService -> ContentOrchestrator -> ContentSteward."""
    print("=" * 80)
    print("TEST 6: Simulated Real Request Flow")
    print("=" * 80)
    
    # Simulate FrontendGatewayService.route_frontend_request()
    async def route_frontend_request():
        # Build user context from headers/token (simulated)
        user_context = {
            "user_id": "real-user-789",
            "tenant_id": "real-tenant-789",
            "permissions": ["read", "write", "admin", "delete"],
            "email": "user@example.com",
            "roles": ["owner"],
            "session_id": "session-123",
            "workflow_id": "workflow-456"
        }
        
        # Set request context (this is what FrontendGatewayService does)
        set_request_user_context(user_context)
        print(f"✅ [route_frontend_request] Set user context: user_id={user_context['user_id']}")
        
        # Route to orchestrator
        return await content_orchestrator_process_file()
    
    # Simulate ContentOrchestrator.process_file()
    async def content_orchestrator_process_file():
        # Get context from request scope (no need to pass as parameter!)
        user_context = get_request_user_context()
        print(f"✅ [ContentOrchestrator.process_file] Retrieved context: user_id={user_context['user_id'] if user_context else None}")
        
        if not user_context:
            raise ValueError("No user context available")
        
        # Call ContentSteward (no need to pass user_context!)
        return await content_steward_store_parsed_file()
    
    # Simulate ContentSteward.store_parsed_file()
    async def content_steward_store_parsed_file():
        # Get context from request scope (no need to pass as parameter!)
        user_context = get_request_user_context()
        print(f"✅ [ContentSteward.store_parsed_file] Retrieved context: user_id={user_context['user_id'] if user_context else None}")
        
        if not user_context:
            raise ValueError("No user context available")
        
        # Verify permissions are accessible
        permissions = get_permissions()
        assert "write" in permissions, "Write permission should be available"
        
        return {
            "success": True,
            "parsed_file_id": "parsed-123",
            "user_id": get_user_id(),
            "tenant_id": get_tenant_id()
        }
    
    # Run the simulated flow
    result = await route_frontend_request()
    
    assert result["success"] is True, "Request flow should succeed"
    assert result["user_id"] == "real-user-789", "User ID should be preserved"
    assert result["tenant_id"] == "real-tenant-789", "Tenant ID should be preserved"
    
    print("✅ Test 6 PASSED: Real request flow works correctly")
    print(f"   Result: {result}")
    print()


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("REQUEST-SCOPED USER CONTEXT TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        await test_request_context_basic()
        await test_request_context_nested_calls()
        await test_request_context_clear()
        await test_request_context_missing()
        await test_request_context_update()
        await simulate_real_request_flow()
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nThe request-scoped user context pattern is working correctly.")
        print("You can now migrate services to use this pattern.")
        print()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up
        clear_request_user_context()


if __name__ == "__main__":
    asyncio.run(main())

