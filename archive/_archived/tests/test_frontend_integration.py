#!/usr/bin/env python3
"""
Frontend Integration Test
Tests the connection between frontend and backend services.
"""

import asyncio
import httpx
import pytest
from typing import Dict, Any


class FrontendIntegrationTest:
    """Test frontend-backend integration."""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_backend_health(self) -> bool:
        """Test backend health endpoint."""
        try:
            response = await self.client.get(f"{self.backend_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend Health: {data['status']}")
                return True
            else:
                print(f"❌ Backend Health Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend Health Error: {e}")
            return False
    
    async def test_frontend_availability(self) -> bool:
        """Test frontend availability."""
        try:
            response = await self.client.get(self.frontend_url)
            if response.status_code == 200:
                print("✅ Frontend Available")
                return True
            else:
                print(f"❌ Frontend Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend Error: {e}")
            return False
    
    async def test_backend_api_endpoints(self) -> bool:
        """Test key backend API endpoints."""
        endpoints = [
            "/health",
            "/services",
            "/docs"
        ]
        
        results = []
        for endpoint in endpoints:
            try:
                response = await self.client.get(f"{self.backend_url}{endpoint}")
                if response.status_code == 200:
                    print(f"✅ {endpoint}: OK")
                    results.append(True)
                else:
                    print(f"❌ {endpoint}: {response.status_code}")
                    results.append(False)
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
                results.append(False)
        
        return all(results)
    
    async def test_business_pillars_health(self) -> bool:
        """Test business pillars health."""
        try:
            response = await self.client.get(f"{self.backend_url}/health")
            if response.status_code == 200:
                data = response.json()
                services = data.get("services", {})
                
                healthy_services = []
                for service_name, service_data in services.items():
                    if isinstance(service_data, dict) and service_data.get("status") == "healthy":
                        healthy_services.append(service_name)
                        print(f"✅ {service_name}: Healthy")
                    else:
                        print(f"⚠️ {service_name}: {service_data.get('status', 'Unknown')}")
                
                print(f"📊 Healthy Services: {len(healthy_services)}/{len(services)}")
                return len(healthy_services) > 0
            else:
                print(f"❌ Health Check Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health Check Error: {e}")
            return False
    
    async def test_cross_dimension_integration(self) -> bool:
        """Test cross-dimension integration."""
        try:
            # Test if we can access the Experience Dimension through the backend
            response = await self.client.get(f"{self.backend_url}/services")
            if response.status_code == 200:
                print("✅ Cross-Dimension Integration: Backend accessible")
                return True
            else:
                print(f"❌ Cross-Dimension Integration Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cross-Dimension Integration Error: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests."""
        print("🚀 Starting Frontend Integration Tests")
        print("=" * 50)
        
        tests = {
            "backend_health": await self.test_backend_health(),
            "frontend_availability": await self.test_frontend_availability(),
            "backend_api_endpoints": await self.test_backend_api_endpoints(),
            "business_pillars_health": await self.test_business_pillars_health(),
            "cross_dimension_integration": await self.test_cross_dimension_integration()
        }
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print("=" * 50)
        
        passed = 0
        total = len(tests)
        
        for test_name, result in tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All integration tests passed!")
        else:
            print("⚠️ Some tests failed - check the logs above")
        
        return tests
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main test runner."""
    test_suite = FrontendIntegrationTest()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Return exit code based on results
        if all(results.values()):
            return 0
        else:
            return 1
            
    finally:
        await test_suite.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)