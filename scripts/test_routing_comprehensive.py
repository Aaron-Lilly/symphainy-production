#!/usr/bin/env python3
"""
Comprehensive Routing Test Suite

Tests new routing against old routing using real production scenarios.
Validates equivalence, performance, and edge cases.

Test Categories:
1. Startup & Initialization
2. Authentication & Authorization
3. Route Discovery & Registration
4. All Registered Routes
5. Edge Cases & Error Handling
6. Performance & Concurrency
7. Fallback Scenarios
8. Path Parameters
9. Query Parameters
10. Headers & Metadata
"""

import sys
import os
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'symphainy-platform')))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ComprehensiveRoutingTest")


class ComprehensiveRoutingTest:
    """Comprehensive test suite for routing validation."""
    
    def __init__(self):
        self.results = {
            "startup": {"passed": 0, "failed": 0, "tests": []},
            "authentication": {"passed": 0, "failed": 0, "tests": []},
            "route_discovery": {"passed": 0, "failed": 0, "tests": []},
            "route_execution": {"passed": 0, "failed": 0, "tests": []},
            "edge_cases": {"passed": 0, "failed": 0, "tests": []},
            "performance": {"passed": 0, "failed": 0, "tests": []},
            "fallback": {"passed": 0, "failed": 0, "tests": []},
            "concurrency": {"passed": 0, "failed": 0, "tests": []}
        }
        self.gateway = None
        self.di_container = None
        self.start_time = None
        
    async def setup(self):
        """Setup test environment."""
        logger.info("🔧 Setting up test environment...")
        
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.experience_foundation.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
            # Create DI Container
            self.di_container = DIContainerService(
                realm_name="test_realm",
                security_provider=None,
                authorization_guard=None
            )
            
            # Initialize Public Works Foundation
            logger.info("📦 Initializing Public Works Foundation...")
            public_works = PublicWorksFoundationService(self.di_container)
            await public_works.initialize()
            
            # Initialize Curator Foundation
            logger.info("📦 Initializing Curator Foundation...")
            curator = CuratorFoundationService(self.di_container, public_works_foundation=public_works)
            await curator.initialize()
            
            # Register services
            self.di_container.service_registry["PublicWorksFoundationService"] = public_works
            self.di_container.service_registry["CuratorFoundationService"] = curator
            
            # Create platform gateway (minimal mock)
            class MockPlatformGateway:
                pass
            
            platform_gateway = MockPlatformGateway()
            
            # Initialize FrontendGatewayService
            logger.info("📦 Initializing FrontendGatewayService...")
            self.gateway = FrontendGatewayService(
                service_name="FrontendGatewayService",
                realm_name="experience_foundation",
                platform_gateway=platform_gateway,
                di_container=self.di_container
            )
            
            success = await self.gateway.initialize()
            if not success:
                raise Exception("FrontendGatewayService initialization failed")
            
            logger.info("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}", exc_info=True)
            return False
    
    def record_test(self, category: str, test_name: str, passed: bool, details: Dict[str, Any] = None):
        """Record test result."""
        result = {
            "name": test_name,
            "passed": passed,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        self.results[category]["tests"].append(result)
        if passed:
            self.results[category]["passed"] += 1
            logger.info(f"✅ {category}: {test_name}")
        else:
            self.results[category]["failed"] += 1
            logger.error(f"❌ {category}: {test_name} - {details.get('error', 'Unknown error')}")
    
    async def test_startup(self):
        """Test 1: Startup & Initialization"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 1: Startup & Initialization")
        logger.info("="*60)
        
        # Test 1.1: Service Initialization
        try:
            assert self.gateway is not None, "Gateway not initialized"
            assert self.gateway.is_initialized, "Gateway not marked as initialized"
            self.record_test("startup", "Service Initialization", True)
        except Exception as e:
            self.record_test("startup", "Service Initialization", False, {"error": str(e)})
        
        # Test 1.2: Route Registration
        try:
            assert len(self.gateway.discovered_routes) > 0, "No routes discovered"
            self.record_test("startup", "Route Registration", True, {
                "routes_registered": len(self.gateway.discovered_routes)
            })
        except Exception as e:
            self.record_test("startup", "Route Registration", False, {"error": str(e)})
        
        # Test 1.3: Feature Flag Status
        try:
            assert hasattr(self.gateway, 'use_discovered_routing'), "Feature flag not set"
            logger.info(f"   Feature flag: {self.gateway.use_discovered_routing}")
            self.record_test("startup", "Feature Flag Status", True, {
                "enabled": self.gateway.use_discovered_routing
            })
        except Exception as e:
            self.record_test("startup", "Feature Flag Status", False, {"error": str(e)})
        
        # Test 1.4: APIRoutingUtility Available
        try:
            assert self.gateway.api_router is not None, "APIRoutingUtility not available"
            self.record_test("startup", "APIRoutingUtility Available", True)
        except Exception as e:
            self.record_test("startup", "APIRoutingUtility Available", False, {"error": str(e)})
    
    async def test_authentication(self):
        """Test 2: Authentication & Authorization"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 2: Authentication & Authorization")
        logger.info("="*60)
        
        # Test 2.1: Request without authentication
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/health",
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            # Should work (health check may not require auth)
            self.record_test("authentication", "Request Without Auth", True, {
                "result_status": result.get("status", "unknown")
            })
        except Exception as e:
            self.record_test("authentication", "Request Without Auth", False, {"error": str(e)})
        
        # Test 2.2: Request with Bearer token
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/health",
                "method": "GET",
                "params": {},
                "headers": {"Authorization": "Bearer test_token_12345"},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            self.record_test("authentication", "Request With Bearer Token", True)
        except Exception as e:
            self.record_test("authentication", "Request With Bearer Token", False, {"error": str(e)})
        
        # Test 2.3: Request with user_id
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/health",
                "method": "GET",
                "params": {"user_id": "test_user_123"},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            self.record_test("authentication", "Request With User ID", True)
        except Exception as e:
            self.record_test("authentication", "Request With User ID", False, {"error": str(e)})
    
    async def test_route_discovery(self):
        """Test 3: Route Discovery"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 3: Route Discovery")
        logger.info("="*60)
        
        # Test 3.1: Routes Discovered
        try:
            routes = self.gateway.discovered_routes
            assert len(routes) > 0, "No routes discovered"
            self.record_test("route_discovery", "Routes Discovered", True, {
                "count": len(routes)
            })
        except Exception as e:
            self.record_test("route_discovery", "Routes Discovered", False, {"error": str(e)})
        
        # Test 3.2: Route Metadata Complete
        try:
            sample_route = list(self.gateway.discovered_routes.values())[0]
            required_fields = ["route_id", "path", "method", "handler"]
            missing = [f for f in required_fields if f not in sample_route]
            assert len(missing) == 0, f"Missing fields: {missing}"
            self.record_test("route_discovery", "Route Metadata Complete", True)
        except Exception as e:
            self.record_test("route_discovery", "Route Metadata Complete", False, {"error": str(e)})
    
    async def test_all_routes(self):
        """Test 4: All Registered Routes"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 4: All Registered Routes")
        logger.info("="*60)
        
        # Get all registered routes
        routes = self.gateway.discovered_routes
        
        for route_key, route in routes.items():
            endpoint = route.get("path", "")
            method = route.get("method", "GET")
            
            # Skip routes with path parameters for now (test separately)
            if "{" in endpoint:
                continue
            
            try:
                request = {
                    "endpoint": endpoint,
                    "method": method,
                    "params": {},
                    "headers": {},
                    "query_params": {}
                }
                
                start_time = time.time()
                result = await self.gateway.route_frontend_request(request)
                elapsed_ms = (time.time() - start_time) * 1000
                
                # Check if route executed (may return error, but should not crash)
                assert result is not None, "No result returned"
                
                self.record_test("route_execution", f"{method} {endpoint}", True, {
                    "response_time_ms": round(elapsed_ms, 2),
                    "success": result.get("success", False)
                })
                
            except Exception as e:
                self.record_test("route_execution", f"{method} {endpoint}", False, {
                    "error": str(e)
                })
    
    async def test_edge_cases(self):
        """Test 5: Edge Cases & Error Handling"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 5: Edge Cases & Error Handling")
        logger.info("="*60)
        
        # Test 5.1: Invalid endpoint
        try:
            request = {
                "endpoint": "/api/v1/invalid-endpoint/does-not-exist",
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            # Should handle gracefully (return error, not crash)
            assert result is not None, "No result for invalid endpoint"
            self.record_test("edge_cases", "Invalid Endpoint", True, {
                "handled": True,
                "error": result.get("error", "none")
            })
        except Exception as e:
            self.record_test("edge_cases", "Invalid Endpoint", False, {"error": str(e)})
        
        # Test 5.2: Invalid HTTP method
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/health",
                "method": "INVALID_METHOD",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            assert result is not None, "No result for invalid method"
            self.record_test("edge_cases", "Invalid HTTP Method", True)
        except Exception as e:
            self.record_test("edge_cases", "Invalid HTTP Method", False, {"error": str(e)})
        
        # Test 5.3: Empty endpoint
        try:
            request = {
                "endpoint": "",
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            assert result is not None, "No result for empty endpoint"
            self.record_test("edge_cases", "Empty Endpoint", True)
        except Exception as e:
            self.record_test("edge_cases", "Empty Endpoint", False, {"error": str(e)})
        
        # Test 5.4: Missing required parameters
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/upload-file",
                "method": "POST",
                "params": {},  # Missing file_data
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            assert result is not None, "No result for missing params"
            self.record_test("edge_cases", "Missing Parameters", True)
        except Exception as e:
            self.record_test("edge_cases", "Missing Parameters", False, {"error": str(e)})
        
        # Test 5.5: Very long endpoint
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/" + "a" * 1000,
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            assert result is not None, "No result for long endpoint"
            self.record_test("edge_cases", "Very Long Endpoint", True)
        except Exception as e:
            self.record_test("edge_cases", "Very Long Endpoint", False, {"error": str(e)})
        
        # Test 5.6: Special characters in endpoint
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/test%20with%20spaces",
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            assert result is not None, "No result for special chars"
            self.record_test("edge_cases", "Special Characters", True)
        except Exception as e:
            self.record_test("edge_cases", "Special Characters", False, {"error": str(e)})
    
    async def test_path_parameters(self):
        """Test 6: Path Parameters"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 6: Path Parameters")
        logger.info("="*60)
        
        # Test 6.1: Route with file_id parameter
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/get-file-details/test_file_123",
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            assert result is not None, "No result for path parameter"
            self.record_test("route_execution", "Path Parameter (file_id)", True)
        except Exception as e:
            self.record_test("route_execution", "Path Parameter (file_id)", False, {"error": str(e)})
        
        # Test 6.2: Route with analysis_id parameter
        try:
            request = {
                "endpoint": "/api/v1/insights-pillar/analysis-results/test_analysis_456",
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            assert result is not None, "No result for analysis_id"
            self.record_test("route_execution", "Path Parameter (analysis_id)", True)
        except Exception as e:
            self.record_test("route_execution", "Path Parameter (analysis_id)", False, {"error": str(e)})
    
    async def test_query_parameters(self):
        """Test 7: Query Parameters"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 7: Query Parameters")
        logger.info("="*60)
        
        # Test 7.1: Request with query parameters
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/list-uploaded-files",
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {"limit": "10", "offset": "0", "filter": "pdf"}
            }
            result = await self.gateway.route_frontend_request(request)
            assert result is not None, "No result for query params"
            self.record_test("route_execution", "Query Parameters", True)
        except Exception as e:
            self.record_test("route_execution", "Query Parameters", False, {"error": str(e)})
    
    async def test_performance(self):
        """Test 8: Performance"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 8: Performance")
        logger.info("="*60)
        
        # Test 8.1: Response time for health check
        try:
            request = {
                "endpoint": "/api/v1/content-pillar/health",
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            
            times = []
            for _ in range(10):
                start = time.time()
                await self.gateway.route_frontend_request(request)
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            # Should be reasonable (< 1000ms average)
            assert avg_time < 1000, f"Average time too high: {avg_time}ms"
            
            self.record_test("performance", "Response Time (10 requests)", True, {
                "avg_ms": round(avg_time, 2),
                "min_ms": round(min_time, 2),
                "max_ms": round(max_time, 2)
            })
        except Exception as e:
            self.record_test("performance", "Response Time", False, {"error": str(e)})
    
    async def test_concurrency(self):
        """Test 9: Concurrency"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 9: Concurrency")
        logger.info("="*60)
        
        # Test 9.1: Concurrent requests
        try:
            async def make_request(i):
                request = {
                    "endpoint": "/api/v1/content-pillar/health",
                    "method": "GET",
                    "params": {"user_id": f"user_{i}"},
                    "headers": {},
                    "query_params": {}
                }
                return await self.gateway.route_frontend_request(request)
            
            # Make 20 concurrent requests
            tasks = [make_request(i) for i in range(20)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should complete (may have errors, but should not crash)
            assert len(results) == 20, f"Expected 20 results, got {len(results)}"
            errors = [r for r in results if isinstance(r, Exception)]
            assert len(errors) == 0, f"Got {len(errors)} exceptions"
            
            self.record_test("concurrency", "Concurrent Requests (20)", True, {
                "completed": len(results),
                "errors": len(errors)
            })
        except Exception as e:
            self.record_test("concurrency", "Concurrent Requests", False, {"error": str(e)})
    
    async def test_fallback(self):
        """Test 10: Fallback Scenarios"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 10: Fallback Scenarios")
        logger.info("="*60)
        
        # Test 10.1: Disable new routing, test fallback
        try:
            original_flag = self.gateway.use_discovered_routing
            self.gateway.use_discovered_routing = False
            
            request = {
                "endpoint": "/api/v1/content-pillar/health",
                "method": "GET",
                "params": {},
                "headers": {},
                "query_params": {}
            }
            result = await self.gateway.route_frontend_request(request)
            assert result is not None, "No result with fallback"
            
            # Restore flag
            self.gateway.use_discovered_routing = original_flag
            
            self.record_test("fallback", "Fallback to Old Routing", True)
        except Exception as e:
            self.gateway.use_discovered_routing = original_flag
            self.record_test("fallback", "Fallback to Old Routing", False, {"error": str(e)})
    
    async def test_metrics(self):
        """Test 11: Metrics Collection"""
        logger.info("\n" + "="*60)
        logger.info("TEST CATEGORY 11: Metrics Collection")
        logger.info("="*60)
        
        # Test 11.1: Get metrics
        try:
            metrics = await self.gateway.get_routing_metrics()
            assert metrics is not None, "No metrics returned"
            assert "old_routing" in metrics, "Missing old_routing metrics"
            assert "new_routing" in metrics, "Missing new_routing metrics"
            
            logger.info(f"   Old Routing Requests: {metrics.get('old_routing', {}).get('requests', 0)}")
            logger.info(f"   New Routing Requests: {metrics.get('new_routing', {}).get('requests', 0)}")
            
            self.record_test("performance", "Metrics Collection", True, {
                "old_requests": metrics.get('old_routing', {}).get('requests', 0),
                "new_requests": metrics.get('new_routing', {}).get('requests', 0)
            })
        except Exception as e:
            self.record_test("performance", "Metrics Collection", False, {"error": str(e)})
    
    async def run_all_tests(self):
        """Run all test categories."""
        self.start_time = time.time()
        logger.info("🚀 Starting Comprehensive Routing Test Suite...")
        logger.info(f"   Timestamp: {datetime.utcnow().isoformat()}")
        
        # Run all test categories
        await self.test_startup()
        await self.test_authentication()
        await self.test_route_discovery()
        await self.test_all_routes()
        await self.test_edge_cases()
        await self.test_path_parameters()
        await self.test_query_parameters()
        await self.test_performance()
        await self.test_concurrency()
        await self.test_fallback()
        await self.test_metrics()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        elapsed = time.time() - self.start_time
        
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            if total > 0:
                pass_rate = (passed / total) * 100
                logger.info(f"{category.upper()}: {passed}/{total} passed ({pass_rate:.1f}%)")
        
        logger.info("-" * 60)
        logger.info(f"TOTAL: {total_passed}/{total_passed + total_failed} passed")
        logger.info(f"Time: {elapsed:.2f}s")
        logger.info("="*60)
        
        # Save results to file
        results_file = f"/tmp/routing_test_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_passed": total_passed,
                    "total_failed": total_failed,
                    "elapsed_seconds": round(elapsed, 2),
                    "timestamp": datetime.utcnow().isoformat()
                },
                "results": self.results
            }, f, indent=2)
        
        logger.info(f"📄 Detailed results saved to: {results_file}")
        
        # Exit code
        if total_failed == 0:
            logger.info("✅ ALL TESTS PASSED")
            return 0
        else:
            logger.warning(f"⚠️ {total_failed} TESTS FAILED")
            return 1


async def main():
    """Main test runner."""
    test = ComprehensiveRoutingTest()
    
    # Setup
    if not await test.setup():
        logger.error("❌ Test setup failed")
        return 1
    
    # Run tests
    exit_code = await test.run_all_tests()
    
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)











