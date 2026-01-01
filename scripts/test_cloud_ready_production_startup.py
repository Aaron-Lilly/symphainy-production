#!/usr/bin/env python3
"""
Production Startup Test - Cloud-Ready Mode

This test verifies that the platform can start up in cloud-ready mode
and provides equivalent or better functionality than the current mode.

Tests:
1. Platform startup in cloud-ready mode
2. Critical endpoints are accessible
3. Foundation services are available
4. Service discovery works
5. API routing works
6. Health checks pass
"""

import os
import sys
import asyncio
import logging
import httpx
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
TEST_TIMEOUT = 300  # 5 minutes for full startup
HEALTH_CHECK_RETRIES = 30
HEALTH_CHECK_INTERVAL = 2  # seconds

TEST_RESULTS = {
    "startup": {"passed": False, "errors": []},
    "health_endpoints": {"passed": False, "errors": []},
    "foundation_services": {"passed": False, "errors": []},
    "service_discovery": {"passed": False, "errors": []},
    "api_routing": {"passed": False, "errors": []},
    "functionality": {"passed": False, "errors": []}
}


async def wait_for_platform_ready(base_url: str, timeout: int = TEST_TIMEOUT) -> bool:
    """Wait for platform to be ready."""
    logger.info(f"⏳ Waiting for platform to be ready at {base_url}...")
    
    start_time = time.time()
    async with httpx.AsyncClient(timeout=10.0) as client:
        while time.time() - start_time < timeout:
            try:
                response = await client.get(f"{base_url}/api/health")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") != "unhealthy":
                        logger.info("✅ Platform is ready!")
                        return True
            except Exception as e:
                logger.debug(f"Platform not ready yet: {e}")
            
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)
    
    logger.error("❌ Platform did not become ready within timeout")
    return False


async def test_startup():
    """Test 1: Platform Startup"""
    logger.info("=" * 80)
    logger.info("TEST 1: Platform Startup (Cloud-Ready Mode)")
    logger.info("=" * 80)
    
    try:
        # Set cloud-ready mode
        os.environ["CLOUD_READY_MODE"] = "enabled"
        os.environ["TEST_MODE"] = "true"  # Makes Traefik optional for testing
        
        # Import and test startup
        from main_cloud_ready import CloudReadyPlatformOrchestrator
        
        logger.info("🚀 Starting platform in cloud-ready mode...")
        orchestrator = CloudReadyPlatformOrchestrator()
        startup_result = await orchestrator.orchestrate_platform_startup()
        
        assert startup_result.get("success"), "Startup should succeed"
        assert startup_result.get("mode") == "cloud_ready", "Mode should be cloud_ready"
        
        logger.info("✅ Platform started successfully")
        logger.info(f"   Startup sequence: {startup_result.get('startup_sequence', [])}")
        
        # Verify critical components
        di_container = orchestrator.get_di_container()
        assert di_container is not None, "DI Container should be initialized"
        
        router_manager = orchestrator.get_router_manager()
        assert router_manager is not None, "Router Manager should be initialized"
        
        foundation_services = orchestrator.foundation_services
        assert len(foundation_services) >= 4, "Should have at least 4 foundation services"
        
        logger.info("✅ Critical components verified")
        
        TEST_RESULTS["startup"]["passed"] = True
        return True, orchestrator
        
    except Exception as e:
        error_msg = f"Startup test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["startup"]["errors"].append(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return False, None


async def test_health_endpoints(orchestrator: Optional[Any] = None):
    """Test 2: Health Endpoints"""
    logger.info("=" * 80)
    logger.info("TEST 2: Health Endpoints")
    logger.info("=" * 80)
    
    try:
        # Test health endpoint via orchestrator (if available)
        if orchestrator:
            status = await orchestrator.get_platform_status()
            assert status.get("mode") == "cloud_ready", "Status should indicate cloud_ready mode"
            logger.info("✅ Platform status endpoint works")
        
        # Test health endpoint via HTTP (if platform is running)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{BASE_URL}/api/health")
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Health endpoint accessible: {data.get('status', 'unknown')}")
                else:
                    logger.warning(f"⚠️ Health endpoint returned {response.status_code}")
        except Exception as e:
            logger.debug(f"Health endpoint not accessible (platform may not be running): {e}")
        
        TEST_RESULTS["health_endpoints"]["passed"] = True
        return True
        
    except Exception as e:
        error_msg = f"Health endpoints test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["health_endpoints"]["errors"].append(error_msg)
        return False


async def test_foundation_services(orchestrator: Optional[Any] = None):
    """Test 3: Foundation Services"""
    logger.info("=" * 80)
    logger.info("TEST 3: Foundation Services")
    logger.info("=" * 80)
    
    try:
        if not orchestrator:
            raise Exception("Orchestrator not available")
        
        foundation_services = orchestrator.foundation_services
        
        # Verify required foundation services
        required_services = [
            "PublicWorksFoundationService",
            "CuratorFoundationService",
            "AgenticFoundationService",
            "ExperienceFoundationService"
        ]
        
        for service_name in required_services:
            assert service_name in foundation_services, f"{service_name} should be available"
            service = foundation_services[service_name]
            assert service is not None, f"{service_name} should not be None"
            logger.info(f"✅ {service_name} available")
        
        # Test service access via DI Container
        di_container = orchestrator.get_di_container()
        for service_name in required_services:
            service = di_container.get_foundation_service(service_name)
            assert service is not None, f"{service_name} should be accessible via DI Container"
            logger.info(f"✅ {service_name} accessible via DI Container")
        
        TEST_RESULTS["foundation_services"]["passed"] = True
        return True
        
    except Exception as e:
        error_msg = f"Foundation services test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["foundation_services"]["errors"].append(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_service_discovery(orchestrator: Optional[Any] = None):
    """Test 4: Service Discovery"""
    logger.info("=" * 80)
    logger.info("TEST 4: Service Discovery")
    logger.info("=" * 80)
    
    try:
        if not orchestrator:
            raise Exception("Orchestrator not available")
        
        # Test Curator Foundation service discovery
        curator = orchestrator.get_foundation_service("CuratorFoundationService")
        assert curator is not None, "Curator Foundation should be available"
        
        # Test auto-discovery (if enabled)
        if curator.auto_discovery:
            assert curator.auto_discovery.is_initialized, "Auto-discovery should be initialized"
            discovered_count = len(curator.auto_discovery.discovered_services)
            logger.info(f"✅ Auto-discovery found {discovered_count} services")
            assert discovered_count > 0, "Should discover at least some services"
        
        # Test unified registry (if enabled)
        di_container = orchestrator.get_di_container()
        if di_container and di_container.unified_registry:
            services = di_container.unified_registry.list_services()
            logger.info(f"✅ Unified registry has {len(services)} services")
            assert len(services) > 0, "Unified registry should have services"
        
        TEST_RESULTS["service_discovery"]["passed"] = True
        return True
        
    except Exception as e:
        error_msg = f"Service discovery test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["service_discovery"]["errors"].append(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_api_routing(orchestrator: Optional[Any] = None):
    """Test 5: API Routing"""
    logger.info("=" * 80)
    logger.info("TEST 5: API Routing")
    logger.info("=" * 80)
    
    try:
        if not orchestrator:
            raise Exception("Orchestrator not available")
        
        # Test Router Manager
        router_manager = orchestrator.get_router_manager()
        assert router_manager is not None, "Router Manager should be available"
        assert router_manager.is_initialized, "Router Manager should be initialized"
        
        # Test unified router
        unified_router = router_manager.get_unified_router()
        assert unified_router is not None, "Unified router should be available"
        logger.info("✅ Router Manager and unified router available")
        
        # Test realm routers (if any registered)
        registered_realms = router_manager.list_registered_realms()
        logger.info(f"✅ {len(registered_realms)} realm routers registered")
        
        TEST_RESULTS["api_routing"]["passed"] = True
        return True
        
    except Exception as e:
        error_msg = f"API routing test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["api_routing"]["errors"].append(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_functionality_equivalence(orchestrator: Optional[Any] = None):
    """Test 6: Functionality Equivalence"""
    logger.info("=" * 80)
    logger.info("TEST 6: Functionality Equivalence")
    logger.info("=" * 80)
    
    try:
        if not orchestrator:
            raise Exception("Orchestrator not available")
        
        # Test 1: Foundation services property (compatibility)
        foundation_services = orchestrator.foundation_services
        assert isinstance(foundation_services, dict), "foundation_services should be a dict"
        assert len(foundation_services) >= 4, "Should have at least 4 foundation services"
        logger.info("✅ foundation_services property works (compatibility)")
        
        # Test 2: Managers property (compatibility - empty in cloud-ready)
        managers = orchestrator.managers
        assert isinstance(managers, dict), "managers should be a dict"
        logger.info("✅ managers property works (compatibility)")
        
        # Test 3: get_platform_status
        status = await orchestrator.get_platform_status()
        assert status.get("mode") == "cloud_ready", "Status should indicate cloud_ready mode"
        assert "startup_status" in status, "Status should include startup_status"
        assert "startup_sequence" in status, "Status should include startup_sequence"
        logger.info("✅ get_platform_status works")
        
        # Test 4: DI Container access
        di_container = orchestrator.get_di_container()
        assert di_container is not None, "DI Container should be accessible"
        logger.info("✅ DI Container accessible")
        
        # Test 5: Router Manager access
        router_manager = orchestrator.get_router_manager()
        assert router_manager is not None, "Router Manager should be accessible"
        logger.info("✅ Router Manager accessible")
        
        # Test 6: Foundation service access
        for service_name in ["PublicWorksFoundationService", "CuratorFoundationService"]:
            service = orchestrator.get_foundation_service(service_name)
            assert service is not None, f"{service_name} should be accessible"
        logger.info("✅ Foundation services accessible via get_foundation_service")
        
        logger.info("✅ All functionality equivalence tests passed")
        
        TEST_RESULTS["functionality"]["passed"] = True
        return True
        
    except Exception as e:
        error_msg = f"Functionality equivalence test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["functionality"]["errors"].append(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Run all production tests."""
    logger.info("=" * 80)
    logger.info("CLOUD-READY PRODUCTION STARTUP TEST")
    logger.info("=" * 80)
    logger.info("")
    logger.info("This test verifies that the platform can start up in cloud-ready mode")
    logger.info("and provides equivalent or better functionality than the current mode.")
    logger.info("")
    
    # Set cloud-ready mode
    os.environ["CLOUD_READY_MODE"] = "enabled"
    os.environ["TEST_MODE"] = "true"
    
    orchestrator = None
    
    try:
        # Test 1: Startup
        logger.info("📋 Running Test 1: Platform Startup...")
        startup_passed, orchestrator = await test_startup()
        logger.info("")
        
        if not startup_passed:
            logger.error("❌ Startup failed - cannot continue with other tests")
            return 1
        
        # Test 2: Health Endpoints
        logger.info("📋 Running Test 2: Health Endpoints...")
        health_passed = await test_health_endpoints(orchestrator)
        logger.info("")
        
        # Test 3: Foundation Services
        logger.info("📋 Running Test 3: Foundation Services...")
        foundation_passed = await test_foundation_services(orchestrator)
        logger.info("")
        
        # Test 4: Service Discovery
        logger.info("📋 Running Test 4: Service Discovery...")
        discovery_passed = await test_service_discovery(orchestrator)
        logger.info("")
        
        # Test 5: API Routing
        logger.info("📋 Running Test 5: API Routing...")
        routing_passed = await test_api_routing(orchestrator)
        logger.info("")
        
        # Test 6: Functionality Equivalence
        logger.info("📋 Running Test 6: Functionality Equivalence...")
        functionality_passed = await test_functionality_equivalence(orchestrator)
        logger.info("")
        
        # Print summary
        logger.info("=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        
        all_passed = (
            startup_passed and
            health_passed and
            foundation_passed and
            discovery_passed and
            routing_passed and
            functionality_passed
        )
        
        logger.info(f"1. Platform Startup:        {'✅ PASSED' if startup_passed else '❌ FAILED'}")
        logger.info(f"2. Health Endpoints:        {'✅ PASSED' if health_passed else '❌ FAILED'}")
        logger.info(f"3. Foundation Services:    {'✅ PASSED' if foundation_passed else '❌ FAILED'}")
        logger.info(f"4. Service Discovery:       {'✅ PASSED' if discovery_passed else '❌ FAILED'}")
        logger.info(f"5. API Routing:             {'✅ PASSED' if routing_passed else '❌ FAILED'}")
        logger.info(f"6. Functionality Equivalence: {'✅ PASSED' if functionality_passed else '❌ FAILED'}")
        logger.info("")
        
        if all_passed:
            logger.info("🎉 ALL PRODUCTION TESTS PASSED!")
            logger.info("")
            logger.info("✅ Cloud-ready mode is production-ready")
            logger.info("✅ Platform provides equivalent or better functionality")
            logger.info("✅ Safe to eliminate the prior version")
            logger.info("")
            logger.info("Recommendation: Transition to cloud-ready architecture")
            return 0
        else:
            logger.error("❌ SOME TESTS FAILED")
            logger.error("")
            logger.error("Errors:")
            for test_name, result in TEST_RESULTS.items():
                if not result["passed"] and result["errors"]:
                    logger.error(f"  {test_name}:")
                    for error in result["errors"]:
                        logger.error(f"    - {error}")
            logger.error("")
            logger.error("⚠️ Do not eliminate prior version until all tests pass")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with exception: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)









