#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
Tests the API connectivity between frontend and backend.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TIMEOUT = 10

def test_backend_api_endpoints() -> bool:
    """Test all backend API endpoints that the frontend needs."""
    print("🧪 Testing Backend API Endpoints...")
    
    endpoints = [
        # Content Pillar
        ("GET", "/api/content/health"),
        ("POST", "/api/content/upload"),
        ("GET", "/api/content/files"),
        
        # Insights Pillar
        ("GET", "/api/insights/health"),
        ("POST", "/api/insights/analyze"),
        ("GET", "/api/insights/insights"),
        
        # Operations Pillar
        ("GET", "/api/operations/health"),
        ("POST", "/api/operations/sop-builder"),
        ("POST", "/api/operations/workflow-builder"),
        
        # Business Outcomes Pillar
        ("GET", "/api/business-outcomes/health"),
        ("POST", "/api/business-outcomes/strategic-planning"),
        ("GET", "/api/business-outcomes/metrics"),
        
        # Cross-Pillar Integration
        ("GET", "/api/orchestrator/health"),
        ("POST", "/api/orchestrator/coordinate"),
        ("GET", "/api/delivery/health"),
        ("POST", "/api/delivery/coordinate"),
        
        # Experience Dimension
        ("GET", "/api/experience/health"),
        ("POST", "/api/experience/session"),
        ("GET", "/api/journey/health"),
        ("POST", "/api/journey/track"),
        ("GET", "/api/frontend/health"),
        ("POST", "/api/frontend/route"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for method, endpoint in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=TIMEOUT)
            else:  # POST
                response = requests.post(f"{BACKEND_URL}{endpoint}", timeout=TIMEOUT)
            
            if response.status_code in [200, 405]:  # 405 is expected for POST without data
                print(f"   ✅ {method} {endpoint} - OK")
                success_count += 1
            else:
                print(f"   ❌ {method} {endpoint} - {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {method} {endpoint} - Error: {e}")
    
    print(f"   📊 Backend API: {success_count}/{total_count} endpoints working")
    return success_count == total_count

def test_frontend_availability() -> bool:
    """Test if frontend is accessible."""
    print("🧪 Testing Frontend Availability...")
    
    try:
        response = requests.get(f"{FRONTEND_URL}", timeout=TIMEOUT)
        if response.status_code == 200:
            print("   ✅ Frontend main page accessible")
            return True
        else:
            print(f"   ❌ Frontend main page returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend not accessible: {e}")
        return False

def test_frontend_pillar_routes() -> bool:
    """Test if frontend pillar routes are accessible."""
    print("🧪 Testing Frontend Pillar Routes...")
    
    routes = [
        "/pillars/content",
        "/pillars/insight", 
        "/pillars/operation",
        "/pillars/business-outcomes"
    ]
    
    success_count = 0
    total_count = len(routes)
    
    for route in routes:
        try:
            response = requests.get(f"{FRONTEND_URL}{route}", timeout=TIMEOUT)
            if response.status_code == 200:
                print(f"   ✅ {route} - OK")
                success_count += 1
            else:
                print(f"   ❌ {route} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route} - Error: {e}")
    
    print(f"   📊 Frontend Routes: {success_count}/{total_count} routes working")
    return success_count == total_count

def test_cors_configuration() -> bool:
    """Test CORS configuration between frontend and backend."""
    print("🧪 Testing CORS Configuration...")
    
    try:
        # Test preflight request
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(f"{BACKEND_URL}/api/content/upload", headers=headers, timeout=TIMEOUT)
        
        if response.status_code in [200, 204]:
            print("   ✅ CORS preflight request successful")
            return True
        else:
            print(f"   ❌ CORS preflight request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
        return False

def test_api_response_format() -> bool:
    """Test that API responses are in the expected format."""
    print("🧪 Testing API Response Format...")
    
    try:
        # Test a simple GET endpoint
        response = requests.get(f"{BACKEND_URL}/api/content/health", timeout=TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if response has expected structure
        if isinstance(data, dict) and 'status' in data:
            print("   ✅ API response format is valid")
            return True
        else:
            print(f"   ❌ API response format unexpected: {data}")
            return False
            
    except Exception as e:
        print(f"   ❌ API response format test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Starting Frontend-Backend Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Backend API Endpoints", test_backend_api_endpoints),
        ("Frontend Availability", test_frontend_availability),
        ("Frontend Pillar Routes", test_frontend_pillar_routes),
        ("CORS Configuration", test_cors_configuration),
        ("API Response Format", test_api_response_format),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Integration Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Frontend and backend are ready for E2E testing.")
        return True
    else:
        print("⚠️ Some integration tests failed. Issues need to be resolved before E2E testing.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
