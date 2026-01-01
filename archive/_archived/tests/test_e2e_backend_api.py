#!/usr/bin/env python3
"""
E2E Backend API Test
Tests all backend API endpoints to ensure they're working properly.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000"
TIMEOUT = 10

def test_health_endpoint() -> bool:
    """Test the main health endpoint."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Health endpoint working")
        print(f"   Status: {data.get('status')}")
        print(f"   Platform running: {data.get('platform_running')}")
        
        services = data.get('services', {})
        healthy_services = sum(1 for s in services.values() if s.get('status') == 'healthy')
        total_services = len(services)
        print(f"   Healthy services: {healthy_services}/{total_services}")
        
        return True
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_services_endpoint() -> bool:
    """Test the services endpoint."""
    try:
        response = requests.get(f"{BACKEND_URL}/services", timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Services endpoint working")
        print(f"   Total services: {len(data.get('services', {}))}")
        
        return True
    except Exception as e:
        print(f"❌ Services endpoint failed: {e}")
        return False

def test_content_pillar_api() -> bool:
    """Test Content Pillar API endpoints."""
    try:
        # Test health
        response = requests.get(f"{BACKEND_URL}/api/content/health", timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Content Pillar health endpoint working")
        
        # Test file upload endpoint (should return method not allowed for GET)
        response = requests.get(f"{BACKEND_URL}/api/content/upload", timeout=TIMEOUT)
        if response.status_code == 405:  # Method not allowed is expected
            print("✅ Content Pillar upload endpoint exists (GET not allowed as expected)")
        else:
            print(f"⚠️ Content Pillar upload endpoint unexpected response: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Content Pillar API failed: {e}")
        return False

def test_insights_pillar_api() -> bool:
    """Test Insights Pillar API endpoints."""
    try:
        # Test health
        response = requests.get(f"{BACKEND_URL}/api/insights/health", timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Insights Pillar health endpoint working")
        
        # Test insights endpoint
        response = requests.get(f"{BACKEND_URL}/api/insights/insights", timeout=TIMEOUT)
        if response.status_code in [200, 405]:  # 405 is expected for GET without data
            print("✅ Insights Pillar insights endpoint exists")
        else:
            print(f"⚠️ Insights Pillar insights endpoint unexpected response: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Insights Pillar API failed: {e}")
        return False

def test_operations_pillar_api() -> bool:
    """Test Operations Pillar API endpoints."""
    try:
        # Test health
        response = requests.get(f"{BACKEND_URL}/api/operations/health", timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Operations Pillar health endpoint working")
        
        # Test SOP builder endpoint
        response = requests.get(f"{BACKEND_URL}/api/operations/sop-builder", timeout=TIMEOUT)
        if response.status_code in [200, 405]:  # 405 is expected for GET without data
            print("✅ Operations Pillar SOP builder endpoint exists")
        else:
            print(f"⚠️ Operations Pillar SOP builder endpoint unexpected response: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Operations Pillar API failed: {e}")
        return False

def test_business_outcomes_pillar_api() -> bool:
    """Test Business Outcomes Pillar API endpoints."""
    try:
        # Test health
        response = requests.get(f"{BACKEND_URL}/api/business-outcomes/health", timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Business Outcomes Pillar health endpoint working")
        
        # Test strategic planning endpoint
        response = requests.get(f"{BACKEND_URL}/api/business-outcomes/strategic-planning", timeout=TIMEOUT)
        if response.status_code in [200, 405]:  # 405 is expected for GET without data
            print("✅ Business Outcomes Pillar strategic planning endpoint exists")
        else:
            print(f"⚠️ Business Outcomes Pillar strategic planning endpoint unexpected response: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Business Outcomes Pillar API failed: {e}")
        return False

def test_experience_dimension_api() -> bool:
    """Test Experience Dimension API endpoints."""
    try:
        # Test health
        response = requests.get(f"{BACKEND_URL}/api/experience/health", timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Experience Manager health endpoint working")
        
        # Test journey manager health
        response = requests.get(f"{BACKEND_URL}/api/journey/health", timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Journey Manager health endpoint working")
        
        # Test frontend integration health
        response = requests.get(f"{BACKEND_URL}/api/frontend/health", timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Frontend Integration health endpoint working")
        
        return True
    except Exception as e:
        print(f"❌ Experience Dimension API failed: {e}")
        return False

def test_cross_pillar_integration() -> bool:
    """Test cross-pillar integration endpoints."""
    try:
        # Test business orchestrator
        response = requests.get(f"{BACKEND_URL}/api/orchestrator/health", timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Business Orchestrator health endpoint working")
        
        # Test delivery manager
        response = requests.get(f"{BACKEND_URL}/api/delivery/health", timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Delivery Manager health endpoint working")
        
        return True
    except Exception as e:
        print(f"❌ Cross-pillar integration failed: {e}")
        return False

def run_comprehensive_e2e_test():
    """Run comprehensive E2E tests."""
    print("🚀 Starting Comprehensive E2E Backend API Tests")
    print("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Services Endpoint", test_services_endpoint),
        ("Content Pillar API", test_content_pillar_api),
        ("Insights Pillar API", test_insights_pillar_api),
        ("Operations Pillar API", test_operations_pillar_api),
        ("Business Outcomes Pillar API", test_business_outcomes_pillar_api),
        ("Experience Dimension API", test_experience_dimension_api),
        ("Cross-Pillar Integration", test_cross_pillar_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 E2E Test Results Summary:")
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
        print("🎉 All E2E tests passed! Backend is ready for frontend integration.")
        return True
    else:
        print("⚠️ Some E2E tests failed. Backend needs attention before frontend integration.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_e2e_test()
    exit(0 if success else 1)


