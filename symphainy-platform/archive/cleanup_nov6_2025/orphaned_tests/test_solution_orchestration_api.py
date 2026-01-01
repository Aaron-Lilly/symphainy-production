#!/usr/bin/env python3
"""
Test Solution Orchestration Hub Public API

This script tests the Solution Orchestration Hub public API endpoints
to ensure they work correctly with the existing API gateway and bridge.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8009"
SOLUTION_ORCHESTRATE_ENDPOINT = f"{API_BASE_URL}/api/v1/solution/orchestrate"
SOLUTION_CAPABILITIES_ENDPOINT = f"{API_BASE_URL}/api/v1/solution/orchestrate/capabilities"
SOLUTION_INITIATORS_ENDPOINT = f"{API_BASE_URL}/api/v1/solution/orchestrate/initiators"

# Test data
TEST_CASES = [
    {
        "name": "MVP Solution - AI Legacy Data Integration",
        "data": {
            "business_outcome": "AI-enabled legacy data integration for our mainframe systems",
            "solution_intent": "mvp",
            "user_context": {
                "user_id": "test_user_001",
                "tenant_id": "test_tenant",
                "session_id": "test_session_001"
            }
        }
    },
    {
        "name": "POC Solution - AI Marketing Campaigns",
        "data": {
            "business_outcome": "AI-enabled marketing campaigns for boats and marine equipment",
            "solution_intent": "poc",
            "user_context": {
                "user_id": "test_user_002",
                "tenant_id": "test_tenant",
                "session_id": "test_session_002"
            }
        }
    },
    {
        "name": "Demo Solution - AV Testing",
        "data": {
            "business_outcome": "AI-enabled autonomous vehicle testing capabilities",
            "solution_intent": "demo",
            "user_context": {
                "user_id": "test_user_003",
                "tenant_id": "test_tenant",
                "session_id": "test_session_003"
            }
        }
    }
]


class SolutionOrchestrationAPITester:
    """Test the Solution Orchestration Hub public API endpoints."""
    
    def __init__(self):
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def test_api_health(self) -> bool:
        """Test if the API is accessible."""
        try:
            async with self.session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    logger.info("✅ API Gateway is accessible")
                    return True
                else:
                    logger.error(f"❌ API Gateway returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to API Gateway: {e}")
            return False
    
    async def test_solution_orchestrate_endpoint(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test the solution orchestrate endpoint."""
        test_name = test_case["name"]
        test_data = test_case["data"]
        
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            async with self.session.post(
                SOLUTION_ORCHESTRATE_ENDPOINT,
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_data = await response.json()
                
                if response.status == 200:
                    logger.info(f"✅ {test_name} - Success")
                    logger.info(f"   Response: {json.dumps(response_data, indent=2)}")
                    return {
                        "test_name": test_name,
                        "success": True,
                        "status_code": response.status,
                        "response": response_data
                    }
                else:
                    logger.error(f"❌ {test_name} - Failed with status {response.status}")
                    logger.error(f"   Response: {json.dumps(response_data, indent=2)}")
                    return {
                        "test_name": test_name,
                        "success": False,
                        "status_code": response.status,
                        "response": response_data
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} - Exception: {e}")
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e)
            }
    
    async def test_solution_capabilities_endpoint(self) -> Dict[str, Any]:
        """Test the solution capabilities endpoint."""
        logger.info("🧪 Testing: Solution Capabilities Endpoint")
        
        try:
            async with self.session.get(SOLUTION_CAPABILITIES_ENDPOINT) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    logger.info("✅ Solution Capabilities - Success")
                    logger.info(f"   Response: {json.dumps(response_data, indent=2)}")
                    return {
                        "test_name": "Solution Capabilities",
                        "success": True,
                        "status_code": response.status,
                        "response": response_data
                    }
                else:
                    logger.error(f"❌ Solution Capabilities - Failed with status {response.status}")
                    return {
                        "test_name": "Solution Capabilities",
                        "success": False,
                        "status_code": response.status,
                        "response": response_data
                    }
                    
        except Exception as e:
            logger.error(f"❌ Solution Capabilities - Exception: {e}")
            return {
                "test_name": "Solution Capabilities",
                "success": False,
                "error": str(e)
            }
    
    async def test_solution_initiators_endpoint(self) -> Dict[str, Any]:
        """Test the solution initiators endpoint."""
        logger.info("🧪 Testing: Solution Initiators Endpoint")
        
        try:
            async with self.session.get(SOLUTION_INITIATORS_ENDPOINT) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    logger.info("✅ Solution Initiators - Success")
                    logger.info(f"   Response: {json.dumps(response_data, indent=2)}")
                    return {
                        "test_name": "Solution Initiators",
                        "success": True,
                        "status_code": response.status,
                        "response": response_data
                    }
                else:
                    logger.error(f"❌ Solution Initiators - Failed with status {response.status}")
                    return {
                        "test_name": "Solution Initiators",
                        "success": False,
                        "status_code": response.status,
                        "response": response_data
                    }
                    
        except Exception as e:
            logger.error(f"❌ Solution Initiators - Exception: {e}")
            return {
                "test_name": "Solution Initiators",
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests."""
        logger.info("🚀 Starting Solution Orchestration Hub API Tests")
        logger.info("=" * 60)
        
        # Test API health
        api_healthy = await self.test_api_health()
        if not api_healthy:
            logger.error("❌ API Gateway is not accessible. Please start the platform first.")
            return {
                "success": False,
                "message": "API Gateway not accessible",
                "tests": []
            }
        
        # Test solution orchestrate endpoints
        orchestrate_results = []
        for test_case in TEST_CASES:
            result = await self.test_solution_orchestrate_endpoint(test_case)
            orchestrate_results.append(result)
        
        # Test capabilities endpoint
        capabilities_result = await self.test_solution_capabilities_endpoint()
        
        # Test initiators endpoint
        initiators_result = await self.test_solution_initiators_endpoint()
        
        # Compile results
        all_results = orchestrate_results + [capabilities_result, initiators_result]
        successful_tests = sum(1 for result in all_results if result.get("success", False))
        total_tests = len(all_results)
        
        logger.info("=" * 60)
        logger.info(f"📊 Test Results: {successful_tests}/{total_tests} tests passed")
        
        if successful_tests == total_tests:
            logger.info("🎉 All tests passed! Solution Orchestration Hub API is working correctly.")
        else:
            logger.warning(f"⚠️  {total_tests - successful_tests} tests failed. Check the logs above for details.")
        
        return {
            "success": successful_tests == total_tests,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "test_results": all_results,
            "timestamp": datetime.utcnow().isoformat()
        }


async def main():
    """Main test function."""
    print("🧪 Solution Orchestration Hub API Test Suite")
    print("=" * 60)
    print("This test suite will verify that the Solution Orchestration Hub")
    print("public API endpoints are working correctly through the API Gateway.")
    print("=" * 60)
    
    async with SolutionOrchestrationAPITester() as tester:
        results = await tester.run_all_tests()
        
        # Print summary
        print("\n📋 Test Summary:")
        print(f"   Total Tests: {results['total_tests']}")
        print(f"   Successful: {results['successful_tests']}")
        print(f"   Failed: {results['failed_tests']}")
        print(f"   Success Rate: {(results['successful_tests']/results['total_tests']*100):.1f}%")
        
        if results['success']:
            print("\n🎉 All tests passed! The Solution Orchestration Hub API is working correctly.")
            print("\n✅ The API is ready for:")
            print("   - Frontend landing page integration (MVP)")
            print("   - External client integration (future extensibility)")
            print("   - Direct API calls bypassing landing page service")
        else:
            print(f"\n⚠️  {results['failed_tests']} tests failed. Please check the logs above for details.")
            print("\n🔧 Common issues:")
            print("   - Platform not started (run: python main.py)")
            print("   - API Gateway not accessible on port 8009")
            print("   - Solution Orchestration Hub service not initialized")
            print("   - DI Container not properly configured")
        
        return results


if __name__ == "__main__":
    asyncio.run(main())






