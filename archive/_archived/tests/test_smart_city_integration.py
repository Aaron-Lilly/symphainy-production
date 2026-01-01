#!/usr/bin/env python3
"""
Comprehensive Smart City Roles Integration Test
Tests all Smart City roles with their associated infrastructure
"""

import asyncio
import logging
import sys
import os
import requests
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.smart_city.services.security_guard.security_guard_service import SecurityGuardService
from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
from backend.smart_city.services.post_office.post_office_service import PostOfficeService
from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
from backend.smart_city.services.librarian.librarian_service import LibrarianService
from backend.smart_city.services.conductor.conductor_service import ConductorService
from backend.smart_city.services.nurse.nurse_service import NurseService
from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
from foundations.utility_foundation.utilities.logging.logging_service import SmartCityLoggingService
from config.environment_loader import EnvironmentLoader

class SmartCityIntegrationTester:
    """Comprehensive tester for all Smart City roles and infrastructure."""
    
    def __init__(self):
        self.logger = SmartCityLoggingService("smart_city_tester")
        self.env_loader = EnvironmentLoader()
        self.results = {}
        self.platform_url = "http://localhost:8000"
        
    async def test_infrastructure_connectivity(self):
        """Test connectivity to all infrastructure services."""
        print("🔌 Testing Infrastructure Connectivity...")
        
        infrastructure_tests = {
            "Redis": self._test_redis_connection(),
            "ArangoDB": self._test_arangodb_connection(),
            "Meilisearch": self._test_meilisearch_connection(),
            "Platform API": self._test_platform_api()
        }
        
        for service, test_func in infrastructure_tests.items():
            try:
                result = await test_func
                self.results[f"infrastructure_{service.lower()}"] = result
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {service}: {result['message']}")
            except Exception as e:
                self.results[f"infrastructure_{service.lower()}"] = {"success": False, "error": str(e)}
                print(f"  ❌ {service}: Error - {e}")
    
    async def _test_redis_connection(self):
        """Test Redis connection."""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            return {"success": True, "message": "Connected successfully"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {e}"}
    
    async def _test_arangodb_connection(self):
        """Test ArangoDB connection."""
        try:
            import requests
            response = requests.get("http://localhost:8529/_api/version", timeout=5)
            if response.status_code == 200:
                return {"success": True, "message": "Connected successfully"}
            else:
                return {"success": False, "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {e}"}
    
    async def _test_meilisearch_connection(self):
        """Test Meilisearch connection."""
        try:
            import requests
            response = requests.get("http://localhost:7700/health", timeout=5)
            if response.status_code == 200:
                return {"success": True, "message": "Connected successfully"}
            else:
                return {"success": False, "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {e}"}
    
    async def _test_platform_api(self):
        """Test platform API connectivity."""
        try:
            response = requests.get(f"{self.platform_url}/health", timeout=5)
            if response.status_code == 200:
                return {"success": True, "message": "Platform API accessible"}
            else:
                return {"success": False, "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {e}"}
    
    async def test_smart_city_roles(self):
        """Test all Smart City roles individually."""
        print("\n🏛️ Testing Smart City Roles...")
        
        roles = [
            ("Security Guard", SecurityGuardService, {"utility_foundation": None, "curator_foundation": None}),
            ("Traffic Cop", TrafficCopService, {"utility_foundation": None, "public_works_foundation": None, "curator_foundation": None}),
            ("Post Office", PostOfficeService, {"utility_foundation": None, "public_works_foundation": None, "curator_foundation": None}),
            ("Data Steward", DataStewardService, {"utility_foundation": None, "curator_foundation": None}),
            ("Librarian", LibrarianService, {"utility_foundation": None, "curator_foundation": None}),
            ("Conductor", ConductorService, {"utility_foundation": None, "curator_foundation": None}),
            ("Nurse", NurseService, {"utility_foundation": None, "curator_foundation": None}),
            ("City Manager", CityManagerService, {"utility_foundation": None, "public_works_foundation": None})
        ]
        
        for role_name, service_class, constructor_args in roles:
            try:
                print(f"  🧪 Testing {role_name}...")
                result = await self._test_single_role(role_name, service_class, constructor_args)
                self.results[f"role_{role_name.lower().replace(' ', '_')}"] = result
                status = "✅" if result["success"] else "❌"
                print(f"    {status} {role_name}: {result['message']}")
            except Exception as e:
                self.results[f"role_{role_name.lower().replace(' ', '_')}"] = {"success": False, "error": str(e)}
                print(f"    ❌ {role_name}: Error - {e}")
    
    async def _test_single_role(self, role_name, service_class, constructor_args):
        """Test a single Smart City role."""
        try:
            # Create service instance
            service = service_class(**constructor_args)
            
            # Initialize service
            await service.initialize()
            
            # Test service health
            health = await service.get_service_health()
            
            if health.get("status") == "healthy":
                return {"success": True, "message": f"Healthy - {health.get('service', 'unknown')}"}
            else:
                return {"success": False, "message": f"Unhealthy - {health.get('status', 'unknown')}"}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to initialize: {e}"}
    
    async def test_cross_role_integration(self):
        """Test integration between Smart City roles."""
        print("\n🔗 Testing Cross-Role Integration...")
        
        try:
            # Test Security Guard -> Traffic Cop integration
            print("  🔐 Testing Security Guard -> Traffic Cop integration...")
            security_guard = SecurityGuardService(
                utility_foundation=None,
                curator_foundation=None
            )
            await security_guard.initialize()
            
            traffic_cop = TrafficCopService(
                utility_foundation=None,
                public_works_foundation=None,
                curator_foundation=None
            )
            await traffic_cop.initialize()
            
            # Test session creation and routing
            session_result = await traffic_cop.create_session(
                user_id="test_user",
                session_data={"test": "data"},
                priority="normal"
            )
            
            if session_result.get("success"):
                self.results["cross_role_integration"] = {"success": True, "message": "Cross-role integration working"}
                print("    ✅ Cross-role integration working")
            else:
                self.results["cross_role_integration"] = {"success": False, "message": "Cross-role integration failed"}
                print("    ❌ Cross-role integration failed")
                
        except Exception as e:
            self.results["cross_role_integration"] = {"success": False, "error": str(e)}
            print(f"    ❌ Cross-role integration error: {e}")
    
    async def test_platform_api_endpoints(self):
        """Test platform API endpoints."""
        print("\n🌐 Testing Platform API Endpoints...")
        
        endpoints = [
            "/health",
            "/services",
            "/api/content/health",
            "/api/insights/health",
            "/api/operations/health",
            "/api/business-outcomes/health"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.platform_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.results[f"api_{endpoint.replace('/', '_').replace('api_', '')}"] = {"success": True, "message": "OK"}
                    print(f"  ✅ {endpoint}: OK")
                else:
                    self.results[f"api_{endpoint.replace('/', '_').replace('api_', '')}"] = {"success": False, "message": f"HTTP {response.status_code}"}
                    print(f"  ❌ {endpoint}: HTTP {response.status_code}")
            except Exception as e:
                self.results[f"api_{endpoint.replace('/', '_').replace('api_', '')}"] = {"success": False, "error": str(e)}
                print(f"  ❌ {endpoint}: Error - {e}")
    
    def generate_report(self):
        """Generate a comprehensive test report."""
        print("\n📊 Test Report Summary")
        print("=" * 50)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if result.get("success", False))
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test_name, result in self.results.items():
                if not result.get("success", False):
                    error = result.get("error", result.get("message", "Unknown error"))
                    print(f"  - {test_name}: {error}")
        
        print(f"\n📅 Test completed at: {datetime.now().isoformat()}")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests/total_tests)*100,
            "results": self.results
        }

async def main():
    """Main test function."""
    print("🏛️ Smart City Roles Integration Test Suite")
    print("=" * 50)
    
    tester = SmartCityIntegrationTester()
    
    # Run all tests
    await tester.test_infrastructure_connectivity()
    await tester.test_smart_city_roles()
    await tester.test_cross_role_integration()
    await tester.test_platform_api_endpoints()
    
    # Generate report
    report = tester.generate_report()
    
    if report["failed_tests"] == 0:
        print("\n🎉 All tests passed! Smart City roles are fully operational!")
        return 0
    else:
        print(f"\n⚠️ {report['failed_tests']} tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
