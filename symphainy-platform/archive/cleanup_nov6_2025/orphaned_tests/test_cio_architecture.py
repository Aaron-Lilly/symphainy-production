#!/usr/bin/env python3
"""
Test Platform Infrastructure Gateway Implementation

Tests the new Platform Gateway with explicit realm abstraction mappings
and validates the CIO's architectural plan.
"""

import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_platform_gateway():
    """Test Platform Infrastructure Gateway functionality."""
    print("🧪 Testing Platform Infrastructure Gateway...")
    
    try:
        # Test 1: Import Platform Gateway
        from platform.infrastructure.platform_gateway import PlatformInfrastructureGateway, RealmCapability
        print("✅ Platform Gateway import successful")
        
        # Test 2: Create mock Public Works Foundation
        class MockPublicWorksFoundation:
            def get_abstraction(self, name: str):
                return f"Mock{name.title()}Abstraction"
        
        mock_public_works = MockPublicWorksFoundation()
        
        # Test 3: Initialize Platform Gateway
        gateway = PlatformInfrastructureGateway(mock_public_works)
        print("✅ Platform Gateway initialization successful")
        
        # Test 4: Test realm mappings
        realms = gateway.list_all_realms()
        print(f"✅ Available realms: {realms}")
        
        expected_realms = ["smart_city", "business_enablement", "experience", "solution", "journey"]
        for realm in expected_realms:
            assert realm in realms, f"Missing realm: {realm}"
        print("✅ All expected realms present")
        
        # Test 5: Test realm capabilities
        smart_city_caps = gateway.get_realm_capabilities("smart_city")
        assert smart_city_caps is not None, "Smart City capabilities not found"
        assert smart_city_caps.byoi_support == True, "Smart City should support BYOI"
        print("✅ Smart City capabilities correct")
        
        # Test 6: Test access validation
        # Smart City should have access to all abstractions
        assert gateway.validate_realm_access("smart_city", "session") == True
        assert gateway.validate_realm_access("smart_city", "llm") == True
        print("✅ Smart City access validation working")
        
        # Business Enablement should have limited access
        assert gateway.validate_realm_access("business_enablement", "content_metadata") == True
        assert gateway.validate_realm_access("business_enablement", "session") == False
        print("✅ Business Enablement access validation working")
        
        # Test 7: Test abstraction retrieval
        abstraction = gateway.get_abstraction("smart_city", "session")
        assert abstraction == "MockSessionAbstraction", f"Wrong abstraction: {abstraction}"
        print("✅ Abstraction retrieval working")
        
        # Test 8: Test access denial
        try:
            gateway.get_abstraction("business_enablement", "session")
            assert False, "Should have raised ValueError for denied access"
        except ValueError as e:
            assert "cannot access 'session'" in str(e)
            print("✅ Access denial working correctly")
        
        # Test 9: Test health check
        health = gateway.health_check()
        assert health["status"] == "healthy"
        print("✅ Health check working")
        
        # Test 10: Test metrics
        metrics = gateway.get_access_metrics()
        assert metrics["total_requests"] > 0
        print("✅ Metrics tracking working")
        
        print("🎉 All Platform Gateway tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Platform Gateway test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_realm_context():
    """Test RealmContext refactoring."""
    print("\n🧪 Testing RealmContext refactoring...")
    
    try:
        # Test 1: Import RealmContext
        from platform.contexts.realm_context import RealmContext
        print("✅ RealmContext import successful")
        
        # Test 2: Check that communication field is removed
        import inspect
        sig = inspect.signature(RealmContext.__init__)
        params = list(sig.parameters.keys())
        
        # Should have realm_name and platform_gateway, not communication
        assert "realm_name" in params, "Missing realm_name parameter"
        assert "platform_gateway" in params, "Missing platform_gateway parameter"
        assert "communication" not in params, "Communication field should be removed"
        print("✅ RealmContext parameters correct")
        
        # Test 3: Check new methods exist
        methods = [method for method in dir(RealmContext) if not method.startswith('_')]
        
        expected_methods = [
            "get_abstraction", "get_all_abstractions", "validate_abstraction_access",
            "get_smart_city_api", "get_post_office_api", "get_traffic_cop_api",
            "send_message", "route_event", "route_request", "start_workflow"
        ]
        
        for method in expected_methods:
            assert method in methods, f"Missing method: {method}"
        print("✅ RealmContext methods correct")
        
        print("🎉 All RealmContext tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ RealmContext test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_di_container_integration():
    """Test DI Container integration with Platform Gateway."""
    print("\n🧪 Testing DI Container integration...")
    
    try:
        # Test 1: Import DI Container
        from foundations.di_container.di_container_service import DIContainerService
        print("✅ DI Container import successful")
        
        # Test 2: Check Platform Gateway getter exists
        methods = [method for method in dir(DIContainerService) if not method.startswith('_')]
        assert "get_platform_gateway" in methods, "Missing get_platform_gateway method"
        print("✅ DI Container Platform Gateway getter exists")
        
        print("🎉 All DI Container integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ DI Container integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 Testing CIO's Platform Architecture Implementation")
    print("=" * 60)
    
    tests = [
        test_platform_gateway,
        test_realm_context,
        test_di_container_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CIO's architecture is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
