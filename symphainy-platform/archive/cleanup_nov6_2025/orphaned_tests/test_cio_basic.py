#!/usr/bin/env python3
"""
Simple Test for Platform Infrastructure Gateway

Tests the core functionality without complex imports.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_platform_gateway_basic():
    """Test Platform Infrastructure Gateway basic functionality."""
    print("🧪 Testing Platform Infrastructure Gateway (Basic)...")
    
    try:
        # Test 1: Import Platform Gateway
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway, RealmCapability
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
        
        # Test 5: Test access validation
        # Smart City should have access to all abstractions
        assert gateway.validate_realm_access("smart_city", "session") == True
        assert gateway.validate_realm_access("smart_city", "llm") == True
        print("✅ Smart City access validation working")
        
        # Business Enablement should have limited access
        assert gateway.validate_realm_access("business_enablement", "content_metadata") == True
        assert gateway.validate_realm_access("business_enablement", "session") == False
        print("✅ Business Enablement access validation working")
        
        # Test 6: Test abstraction retrieval
        abstraction = gateway.get_abstraction("smart_city", "session")
        assert abstraction == "MockSessionAbstraction", f"Wrong abstraction: {abstraction}"
        print("✅ Abstraction retrieval working")
        
        # Test 7: Test access denial
        try:
            gateway.get_abstraction("business_enablement", "session")
            assert False, "Should have raised ValueError for denied access"
        except ValueError as e:
            assert "cannot access 'session'" in str(e)
            print("✅ Access denial working correctly")
        
        # Test 8: Test health check
        health = gateway.health_check()
        assert health["status"] == "healthy"
        print("✅ Health check working")
        
        print("🎉 Platform Gateway basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Platform Gateway test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_realm_context_basic():
    """Test RealmContext basic structure."""
    print("\n🧪 Testing RealmContext (Basic)...")
    
    try:
        # Test 1: Import RealmContext
        from platform_infrastructure.contexts.realm_context import RealmContext
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
        
        print("🎉 RealmContext basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ RealmContext test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run basic tests."""
    print("🚀 Testing CIO's Platform Architecture Implementation (Basic)")
    print("=" * 70)
    
    tests = [
        test_platform_gateway_basic,
        test_realm_context_basic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! CIO's architecture is working correctly.")
        print("\n✅ Key Achievements:")
        print("   • Platform Infrastructure Gateway with explicit realm mappings")
        print("   • RealmContext with realm_name and platform_gateway")
        print("   • Communication Foundation removed from RealmContext")
        print("   • Smart City SOA API access methods added")
        print("   • Access validation and governance working")
        return True
    else:
        print("❌ Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
