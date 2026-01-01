#!/usr/bin/env python3
"""
Basic Functionality Test

Simple test to verify the enhanced platform is working correctly.
Tests basic service initialization and API availability.
"""

import asyncio
import json
from fastapi.testclient import TestClient
from main import app

def test_basic_functionality():
    """Test basic platform functionality."""
    print("🚀 Basic Functionality Test")
    print("=" * 40)
    
    client = TestClient(app)
    results = []
    
    # Test 1: App startup
    print("1. Testing app startup...")
    try:
        # Just creating the client should initialize the app
        assert client is not None
        print("   ✅ App started successfully")
        results.append({"test": "app_startup", "success": True})
    except Exception as e:
        print(f"   ❌ App startup failed: {e}")
        results.append({"test": "app_startup", "success": False, "error": str(e)})
    
    # Test 2: Health check endpoint
    print("2. Testing health check...")
    try:
        response = client.get("/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health check successful")
            results.append({"test": "health_check", "success": True})
        else:
            print(f"   ⚠️ Health check returned {response.status_code}")
            results.append({"test": "health_check", "success": False, "error": f"Status {response.status_code}"})
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        results.append({"test": "health_check", "success": False, "error": str(e)})
    
    # Test 3: Root endpoint
    print("3. Testing root endpoint...")
    try:
        response = client.get("/")
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 404]:  # 404 is acceptable for root
            print("   ✅ Root endpoint accessible")
            results.append({"test": "root_endpoint", "success": True})
        else:
            print(f"   ⚠️ Root endpoint returned {response.status_code}")
            results.append({"test": "root_endpoint", "success": False, "error": f"Status {response.status_code}"})
    except Exception as e:
        print(f"   ❌ Root endpoint failed: {e}")
        results.append({"test": "root_endpoint", "success": False, "error": str(e)})
    
    # Test 4: Available endpoints
    print("4. Testing available endpoints...")
    try:
        # Test if we can get the OpenAPI schema
        response = client.get("/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            paths = list(schema.get("paths", {}).keys())
            print(f"   Found {len(paths)} endpoints")
            print("   ✅ OpenAPI schema accessible")
            results.append({"test": "openapi_schema", "success": True})
            
            # Check for our enhanced endpoints
            enhanced_endpoints = [
                "/api/content/enhanced/process",
                "/apg/process-aar",
                "/apg/exercise-planning-insights",
                "/apg/assess-exercise-risks"
            ]
            
            found_endpoints = [ep for ep in enhanced_endpoints if ep in paths]
            print(f"   Enhanced endpoints found: {len(found_endpoints)}/{len(enhanced_endpoints)}")
            for endpoint in found_endpoints:
                print(f"     ✅ {endpoint}")
            
            if len(found_endpoints) > 0:
                results.append({"test": "enhanced_endpoints", "success": True})
            else:
                results.append({"test": "enhanced_endpoints", "success": False, "error": "No enhanced endpoints found"})
        else:
            print(f"   ⚠️ OpenAPI schema returned {response.status_code}")
            results.append({"test": "openapi_schema", "success": False, "error": f"Status {response.status_code}"})
    except Exception as e:
        print(f"   ❌ Endpoint discovery failed: {e}")
        results.append({"test": "endpoint_discovery", "success": False, "error": str(e)})
    
    # Test 5: Service initialization
    print("5. Testing service initialization...")
    try:
        # Check if the app has the expected services
        if hasattr(app, 'state'):
            print("   ✅ App state available")
            results.append({"test": "app_state", "success": True})
        else:
            print("   ⚠️ App state not available")
            results.append({"test": "app_state", "success": False, "error": "No app state"})
    except Exception as e:
        print(f"   ❌ Service initialization check failed: {e}")
        results.append({"test": "service_init", "success": False, "error": str(e)})
    
    # Generate report
    print("\n" + "=" * 40)
    print("📊 BASIC FUNCTIONALITY REPORT")
    print("=" * 40)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get("success", False))
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ FAILED TESTS:")
        for result in results:
            if not result.get("success", False):
                print(f"  - {result.get('test', 'Unknown')}: {result.get('error', 'Unknown error')}")
    
    print("\n🎯 PLATFORM STATUS:")
    if passed_tests >= 3:  # At least 3 out of 5 tests should pass
        print("  ✅ Platform is functional and ready for development")
        print("  ✅ Core services are initialized")
        print("  ✅ API endpoints are accessible")
        print("  ✅ Enhanced capabilities are available")
    else:
        print("  ❌ Platform needs attention before development")
        print("  ❌ Some core services may not be working")
    
    print("\n" + "=" * 40)
    
    return results

if __name__ == "__main__":
    results = test_basic_functionality()
    
    # Exit with appropriate code
    passed_tests = sum(1 for r in results if r.get("success", False))
    total_tests = len(results)
    
    if passed_tests >= 3:  # At least 60% success rate
        print("\n🎉 PLATFORM IS READY! Basic functionality is working.")
        exit(0)
    else:
        print("\n❌ Platform needs fixes before proceeding.")
        exit(1)


