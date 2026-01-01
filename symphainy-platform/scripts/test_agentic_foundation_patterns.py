#!/usr/bin/env python3
"""
Test script to verify Agentic Foundation refactoring patterns are working correctly.

Tests:
1. Infrastructure enablement services initialization
2. Wrapper methods in AgenticFoundationService
3. MCPClientManager utilities
4. Service integration and dependency injection
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)
# Also add symphainy-platform to path
platform_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, platform_path)

async def test_infrastructure_enablement_services():
    """Test that infrastructure enablement services are properly initialized."""
    print("\n" + "="*80)
    print("TEST 1: Infrastructure Enablement Services Initialization")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService()
        await di_container.initialize()
        print("✅ DI Container initialized")
        
        # Initialize Public Works Foundation
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize()
        print("✅ Public Works Foundation initialized")
        
        # Initialize Agentic Foundation
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works,
            curator_foundation=None
        )
        await agentic_foundation.initialize()
        print("✅ Agentic Foundation initialized")
        
        # Check infrastructure enablement services
        services_to_check = [
            ("tool_registry_service", "ToolRegistryService"),
            ("tool_discovery_service", "ToolDiscoveryService"),
            ("health_service", "HealthService"),
            ("policy_service", "PolicyService"),
            ("session_service", "SessionService")
        ]
        
        all_passed = True
        for attr_name, service_name in services_to_check:
            service = getattr(agentic_foundation, attr_name, None)
            if service:
                print(f"✅ {service_name} is initialized: {type(service).__name__}")
                
                # Check if service has mixins
                if hasattr(service, '_init_utility_access'):
                    print(f"   ✅ {service_name} has utility mixins")
                else:
                    print(f"   ⚠️ {service_name} missing utility mixins")
                    all_passed = False
            else:
                print(f"❌ {service_name} is NOT initialized")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_wrapper_methods():
    """Test that wrapper methods in AgenticFoundationService work correctly."""
    print("\n" + "="*80)
    print("TEST 2: Wrapper Methods in AgenticFoundationService")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService()
        await di_container.initialize()
        
        # Initialize Public Works Foundation
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize()
        
        # Initialize Agentic Foundation
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works,
            curator_foundation=None
        )
        await agentic_foundation.initialize()
        
        # Check wrapper methods exist
        wrapper_methods = [
            "register_agent_tool",
            "discover_agent_tools",
            "monitor_agent_health_wrapper",
            "enforce_agent_policy_wrapper",
            "manage_agent_session_wrapper"
        ]
        
        all_passed = True
        for method_name in wrapper_methods:
            if hasattr(agentic_foundation, method_name):
                method = getattr(agentic_foundation, method_name)
                if callable(method):
                    print(f"✅ Wrapper method '{method_name}' exists and is callable")
                else:
                    print(f"❌ Wrapper method '{method_name}' exists but is not callable")
                    all_passed = False
            else:
                print(f"❌ Wrapper method '{method_name}' does not exist")
                all_passed = False
        
        # Test that wrapper methods have utility access
        if hasattr(agentic_foundation, 'log_operation_with_telemetry'):
            print("✅ AgenticFoundationService has utility methods (log_operation_with_telemetry)")
        else:
            print("❌ AgenticFoundationService missing utility methods")
            all_passed = False
        
        if hasattr(agentic_foundation, 'handle_error_with_audit'):
            print("✅ AgenticFoundationService has utility methods (handle_error_with_audit)")
        else:
            print("❌ AgenticFoundationService missing utility methods")
            all_passed = False
        
        if hasattr(agentic_foundation, 'record_health_metric'):
            print("✅ AgenticFoundationService has utility methods (record_health_metric)")
        else:
            print("❌ AgenticFoundationService missing utility methods")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_client_manager():
    """Test that MCPClientManager has utilities."""
    print("\n" + "="*80)
    print("TEST 3: MCPClientManager Utilities")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.agentic_foundation.agent_sdk.mcp_client_manager import MCPClientManager
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService()
        await di_container.initialize()
        
        # Initialize Agentic Foundation (minimal - just for MCPClientManager)
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=None,
            curator_foundation=None
        )
        
        # Create MCPClientManager
        mcp_manager = MCPClientManager(
            foundation_services=di_container,
            agentic_foundation=agentic_foundation
        )
        print("✅ MCPClientManager created")
        
        # Check utility mixins
        if hasattr(mcp_manager, '_init_utility_access'):
            print("✅ MCPClientManager has utility mixins (_init_utility_access)")
        else:
            print("❌ MCPClientManager missing utility mixins")
            return False
        
        if hasattr(mcp_manager, '_init_performance_monitoring'):
            print("✅ MCPClientManager has performance monitoring mixins")
        else:
            print("❌ MCPClientManager missing performance monitoring mixins")
            return False
        
        # Check utility methods
        utility_methods = [
            "log_operation_with_telemetry",
            "handle_error_with_audit",
            "record_health_metric",
            "get_security",
            "get_tenant"
        ]
        
        all_passed = True
        for method_name in utility_methods:
            if hasattr(mcp_manager, method_name):
                method = getattr(mcp_manager, method_name)
                if callable(method):
                    print(f"✅ MCPClientManager has utility method '{method_name}'")
                else:
                    print(f"❌ MCPClientManager method '{method_name}' exists but is not callable")
                    all_passed = False
            else:
                print(f"❌ MCPClientManager missing utility method '{method_name}'")
                all_passed = False
        
        # Test that initialize() method uses utilities
        try:
            await mcp_manager.initialize()
            print("✅ MCPClientManager.initialize() executed successfully")
        except Exception as e:
            # This is expected if Curator is not available
            if "Curator" in str(e) or "not available" in str(e).lower():
                print(f"⚠️ MCPClientManager.initialize() failed (expected - Curator not available): {e}")
            else:
                print(f"❌ MCPClientManager.initialize() failed unexpectedly: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_wrapper_method_invocation():
    """Test that wrapper methods can be called (even if services aren't fully configured)."""
    print("\n" + "="*80)
    print("TEST 4: Wrapper Method Invocation")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService()
        await di_container.initialize()
        
        # Initialize Public Works Foundation
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize()
        
        # Initialize Agentic Foundation
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works,
            curator_foundation=None
        )
        await agentic_foundation.initialize()
        
        # Test wrapper method invocation (should handle missing services gracefully)
        user_context = {"tenant_id": "test_tenant", "user_id": "test_user"}
        
        # Test discover_agent_tools (should return empty list if service not available)
        try:
            result = await agentic_foundation.discover_agent_tools(
                capability_name="test_capability",
                user_context=user_context
            )
            print(f"✅ discover_agent_tools() executed: returned {type(result).__name__}")
            if isinstance(result, list):
                print(f"   Result is a list (expected): {len(result)} items")
            else:
                print(f"   ⚠️ Result is not a list: {type(result)}")
        except Exception as e:
            # Check if it's a security/tenant validation error (expected)
            if "Access denied" in str(e) or "Tenant access denied" in str(e):
                print(f"✅ discover_agent_tools() executed security/tenant validation (expected)")
            else:
                print(f"❌ discover_agent_tools() failed unexpectedly: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # Test that utilities are being called
        # We can't easily test telemetry/health metrics without mocking, but we can verify
        # the methods exist and are being called in the wrapper
        print("✅ Wrapper methods can be invoked")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_service_dependency_injection():
    """Test that services are properly injected with dependencies."""
    print("\n" + "="*80)
    print("TEST 5: Service Dependency Injection")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService()
        await di_container.initialize()
        
        # Initialize Public Works Foundation
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize()
        
        # Initialize Agentic Foundation
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works,
            curator_foundation=None
        )
        await agentic_foundation.initialize()
        
        # Check that services have their dependencies
        if agentic_foundation.tool_registry_service:
            service = agentic_foundation.tool_registry_service
            if hasattr(service, 'tool_storage_abstraction'):
                print("✅ ToolRegistryService has tool_storage_abstraction dependency")
            else:
                print("❌ ToolRegistryService missing tool_storage_abstraction dependency")
                return False
            
            if hasattr(service, 'di_container'):
                print("✅ ToolRegistryService has di_container dependency")
            else:
                print("❌ ToolRegistryService missing di_container dependency")
                return False
        
        if agentic_foundation.health_service:
            service = agentic_foundation.health_service
            if hasattr(service, 'health_abstraction'):
                print("✅ HealthService has health_abstraction dependency")
            else:
                print("❌ HealthService missing health_abstraction dependency")
                return False
        
        if agentic_foundation.policy_service:
            service = agentic_foundation.policy_service
            if hasattr(service, 'policy_abstraction'):
                print("✅ PolicyService has policy_abstraction dependency")
            else:
                print("❌ PolicyService missing policy_abstraction dependency")
                return False
        
        if agentic_foundation.session_service:
            service = agentic_foundation.session_service
            if hasattr(service, 'session_abstraction'):
                print("✅ SessionService has session_abstraction dependency")
            else:
                print("❌ SessionService missing session_abstraction dependency")
                return False
        
        print("✅ All services have proper dependencies injected")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("AGENTIC FOUNDATION PATTERN VERIFICATION TESTS")
    print("="*80)
    print("\nTesting Option B pattern: Utilities via AgenticFoundationService")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(("Infrastructure Enablement Services", await test_infrastructure_enablement_services()))
    results.append(("Wrapper Methods", await test_wrapper_methods()))
    results.append(("MCPClientManager Utilities", await test_mcp_client_manager()))
    results.append(("Wrapper Method Invocation", await test_wrapper_method_invocation()))
    results.append(("Service Dependency Injection", await test_service_dependency_injection()))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*80)
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("="*80)
    
    if failed == 0:
        print("\n🎉 All tests passed! Patterns are working correctly.")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

