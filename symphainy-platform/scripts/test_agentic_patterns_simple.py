#!/usr/bin/env python3
"""
Simplified test script to verify Agentic Foundation refactoring patterns.

Tests focus on:
1. Code structure and method existence (static analysis)
2. MCPClientManager utilities (can test without full initialization)
3. Wrapper method signatures
"""

import sys
import os
import ast
import inspect
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
platform_path = Path(__file__).parent.parent
sys.path.insert(0, str(platform_path))


def test_mcp_client_manager_structure():
    """Test MCPClientManager has utility mixins and methods."""
    print("\n" + "="*80)
    print("TEST 1: MCPClientManager Structure")
    print("="*80)
    
    try:
        # Read the file and parse AST
        mcp_file = platform_path / "foundations/agentic_foundation/agent_sdk/mcp_client_manager.py"
        with open(mcp_file, 'r') as f:
            content = f.read()
        
        # Check for mixin imports
        if "UtilityAccessMixin" in content and "PerformanceMonitoringMixin" in content:
            print("✅ MCPClientManager imports utility mixins")
        else:
            print("❌ MCPClientManager missing utility mixin imports")
            return False
        
        # Check for mixin initialization
        if "_init_utility_access" in content and "_init_performance_monitoring" in content:
            print("✅ MCPClientManager initializes utility mixins")
        else:
            print("❌ MCPClientManager missing utility mixin initialization")
            return False
        
        # Check for utility methods in key methods
        methods_to_check = [
            ("initialize", ["log_operation_with_telemetry", "handle_error_with_audit", "record_health_metric"]),
            ("execute_role_tool", ["log_operation_with_telemetry", "handle_error_with_audit", "record_health_metric"]),
            ("connect_to_role", ["log_operation_with_telemetry", "handle_error_with_audit", "record_health_metric"]),
            ("disconnect_from_role", ["log_operation_with_telemetry", "handle_error_with_audit", "record_health_metric"]),
        ]
        
        all_passed = True
        for method_name, utilities in methods_to_check:
            # Find method in content
            method_pattern = f"async def {method_name}("
            if method_pattern in content:
                # Get method content
                start_idx = content.find(method_pattern)
                # Find the end of the method (next def or class)
                end_idx = len(content)
                for pattern in ["\n    async def ", "\n    def ", "\nclass ", "\n\n#"]:
                    next_idx = content.find(pattern, start_idx + 1)
                    if next_idx != -1 and next_idx < end_idx:
                        end_idx = next_idx
                
                method_content = content[start_idx:end_idx]
                
                # Check for utilities
                found_all = True
                for utility in utilities:
                    if utility in method_content:
                        print(f"   ✅ {method_name}() uses {utility}")
                    else:
                        print(f"   ❌ {method_name}() missing {utility}")
                        found_all = False
                        all_passed = False
                
                if found_all:
                    print(f"✅ {method_name}() has all utilities")
            else:
                print(f"❌ Method {method_name}() not found")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wrapper_methods_structure():
    """Test that wrapper methods exist in AgenticFoundationService."""
    print("\n" + "="*80)
    print("TEST 2: Wrapper Methods Structure")
    print("="*80)
    
    try:
        # Read the file
        agentic_file = platform_path / "foundations/agentic_foundation/agentic_foundation_service.py"
        with open(agentic_file, 'r') as f:
            content = f.read()
        
        # Check for wrapper methods
        wrapper_methods = [
            "register_agent_tool",
            "discover_agent_tools",
            "monitor_agent_health_wrapper",
            "enforce_agent_policy_wrapper",
            "manage_agent_session_wrapper"
        ]
        
        all_passed = True
        for method_name in wrapper_methods:
            method_pattern = f"async def {method_name}("
            if method_pattern in content:
                print(f"✅ Wrapper method '{method_name}' exists")
                
                # Check it has utilities
                start_idx = content.find(method_pattern)
                end_idx = len(content)
                for pattern in ["\n    async def ", "\n    def ", "\nclass ", "\n\n#"]:
                    next_idx = content.find(pattern, start_idx + 1)
                    if next_idx != -1 and next_idx < end_idx:
                        end_idx = next_idx
                
                method_content = content[start_idx:end_idx]
                
                # Check for utilities
                if "log_operation_with_telemetry" in method_content:
                    print(f"   ✅ {method_name}() uses telemetry")
                else:
                    print(f"   ❌ {method_name}() missing telemetry")
                    all_passed = False
                
                if "handle_error_with_audit" in method_content:
                    print(f"   ✅ {method_name}() uses error handling")
                else:
                    print(f"   ❌ {method_name}() missing error handling")
                    all_passed = False
                
                if "record_health_metric" in method_content:
                    print(f"   ✅ {method_name}() uses health metrics")
                else:
                    print(f"   ❌ {method_name}() missing health metrics")
                    all_passed = False
                
                # Check for security/tenant validation
                if "check_permissions" in method_content or "validate_tenant_access" in method_content:
                    print(f"   ✅ {method_name}() has security/tenant validation")
                else:
                    print(f"   ⚠️ {method_name}() may be missing security/tenant validation (check manually)")
            else:
                print(f"❌ Wrapper method '{method_name}' does not exist")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_infrastructure_enablement_integration():
    """Test that infrastructure enablement services are integrated."""
    print("\n" + "="*80)
    print("TEST 3: Infrastructure Enablement Services Integration")
    print("="*80)
    
    try:
        # Read the file
        agentic_file = platform_path / "foundations/agentic_foundation/agentic_foundation_service.py"
        with open(agentic_file, 'r') as f:
            content = f.read()
        
        # Check for service imports
        services = [
            "ToolRegistryService",
            "ToolDiscoveryService",
            "HealthService",
            "PolicyService",
            "SessionService"
        ]
        
        all_passed = True
        for service_name in services:
            if f"from foundations.agentic_foundation.infrastructure_enablement.{service_name.lower().replace('service', '')}" in content or service_name in content:
                print(f"✅ {service_name} is imported")
            else:
                print(f"❌ {service_name} not imported")
                all_passed = False
        
        # Check for service properties
        service_properties = [
            "tool_registry_service",
            "tool_discovery_service",
            "health_service",
            "policy_service",
            "session_service"
        ]
        
        for prop_name in service_properties:
            if f"self.{prop_name}" in content:
                print(f"✅ {prop_name} property exists")
            else:
                print(f"❌ {prop_name} property missing")
                all_passed = False
        
        # Check for initialization method
        if "_initialize_infrastructure_enablement_services" in content:
            print("✅ _initialize_infrastructure_enablement_services() method exists")
        else:
            print("❌ _initialize_infrastructure_enablement_services() method missing")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_policy_session_mixins():
    """Test that PolicyService and SessionService have mixins."""
    print("\n" + "="*80)
    print("TEST 4: PolicyService and SessionService Mixins")
    print("="*80)
    
    try:
        services = [
            ("policy_service.py", "PolicyService"),
            ("session_service.py", "SessionService")
        ]
        
        all_passed = True
        for filename, service_name in services:
            service_file = platform_path / f"foundations/agentic_foundation/infrastructure_enablement/{filename}"
            if not service_file.exists():
                print(f"❌ {service_name} file not found: {service_file}")
                all_passed = False
                continue
            
            with open(service_file, 'r') as f:
                content = f.read()
            
            # Check for mixin imports
            if "UtilityAccessMixin" in content and "PerformanceMonitoringMixin" in content:
                print(f"✅ {service_name} imports utility mixins")
            else:
                print(f"❌ {service_name} missing utility mixin imports")
                all_passed = False
            
            # Check for mixin initialization
            if "_init_utility_access" in content and "_init_performance_monitoring" in content:
                print(f"✅ {service_name} initializes utility mixins")
            else:
                print(f"❌ {service_name} missing utility mixin initialization")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("AGENTIC FOUNDATION PATTERN VERIFICATION TESTS (Static Analysis)")
    print("="*80)
    print("\nTesting Option B pattern: Utilities via AgenticFoundationService")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(("MCPClientManager Structure", test_mcp_client_manager_structure()))
    results.append(("Wrapper Methods Structure", test_wrapper_methods_structure()))
    results.append(("Infrastructure Enablement Integration", test_infrastructure_enablement_integration()))
    results.append(("Policy/Session Service Mixins", test_policy_session_mixins()))
    
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
        print("\n🎉 All tests passed! Patterns are correctly implemented.")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)





