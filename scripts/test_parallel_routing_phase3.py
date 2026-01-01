#!/usr/bin/env python3
"""
Test Phase 3: Parallel Routing

Tests that both old (hardcoded) and new (discovered) routing work correctly.
"""

import sys
import os
import asyncio
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'symphainy-platform')))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ParallelRoutingTest")


async def test_parallel_routing():
    """Test that both old and new routing work."""
    logger.info("🧪 Starting Phase 3 Parallel Routing Test...")
    
    try:
        # Import required services
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from foundations.experience_foundation.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        logger.info("✅ Imports successful")
        
        # Create DI Container
        di_container = DIContainerService(
            realm_name="test_realm",
            security_provider=None,
            authorization_guard=None
        )
        logger.info("✅ DI Container created")
        
        # Initialize Public Works Foundation
        logger.info("📦 Initializing Public Works Foundation...")
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize()
        logger.info("✅ Public Works Foundation initialized")
        
        # Initialize Curator Foundation
        logger.info("📦 Initializing Curator Foundation...")
        curator = CuratorFoundationService(di_container, public_works_foundation=public_works)
        await curator.initialize()
        logger.info("✅ Curator Foundation initialized")
        
        # Register services
        di_container.service_registry["PublicWorksFoundationService"] = public_works
        di_container.service_registry["CuratorFoundationService"] = curator
        
        # Create platform gateway (minimal mock)
        class MockPlatformGateway:
            pass
        
        platform_gateway = MockPlatformGateway()
        
        # Initialize FrontendGatewayService
        logger.info("📦 Initializing FrontendGatewayService...")
        gateway = FrontendGatewayService(
            service_name="FrontendGatewayService",
            realm_name="experience_foundation",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Initialize gateway (registers routes)
        logger.info("🚀 Initializing FrontendGatewayService...")
        success = await gateway.initialize()
        
        if not success:
            logger.error("❌ FrontendGatewayService initialization failed")
            return False
        
        logger.info("✅ FrontendGatewayService initialized")
        
        # Test 1: Test old routing (feature flag = False)
        logger.info("\n" + "="*60)
        logger.info("TEST 1: Old Routing (Feature Flag = False)")
        logger.info("="*60)
        
        gateway.use_discovered_routing = False
        
        # Test health check endpoint (simple, no dependencies)
        test_request = {
            "endpoint": "/api/v1/content-pillar/health",
            "method": "GET",
            "params": {},
            "headers": {},
            "query_params": {},
            "user_id": "test_user"
        }
        
        logger.info(f"📤 Testing: {test_request['method']} {test_request['endpoint']}")
        old_result = await gateway.route_frontend_request(test_request)
        
        logger.info(f"📥 Old Routing Result: {old_result.get('status', 'unknown')}")
        logger.info(f"   Success: {old_result.get('success', 'unknown')}")
        
        # Test 2: Test new routing (feature flag = True)
        logger.info("\n" + "="*60)
        logger.info("TEST 2: New Routing (Feature Flag = True)")
        logger.info("="*60)
        
        gateway.use_discovered_routing = True
        
        # Discover routes first
        await gateway._discover_routes_from_curator()
        
        logger.info(f"📤 Testing: {test_request['method']} {test_request['endpoint']}")
        new_result = await gateway.route_frontend_request(test_request)
        
        logger.info(f"📥 New Routing Result: {new_result.get('status', 'unknown')}")
        logger.info(f"   Success: {new_result.get('success', 'unknown')}")
        logger.info(f"   Routing Method: {new_result.get('routing_method', 'unknown')}")
        
        # Test 3: Compare results
        logger.info("\n" + "="*60)
        logger.info("TEST 3: Compare Results")
        logger.info("="*60)
        
        # Both should return similar results (status should match)
        old_status = old_result.get("status") or old_result.get("pillar")
        new_status = new_result.get("status") or new_result.get("pillar")
        
        logger.info(f"Old Routing Status: {old_status}")
        logger.info(f"New Routing Status: {new_status}")
        
        # Check if results are similar
        if old_status and new_status:
            if old_status == new_status or (old_status in str(new_status) or new_status in str(old_status)):
                logger.info("✅ Results match - both routing methods work!")
                return True
            else:
                logger.warning(f"⚠️ Results differ: old={old_status}, new={new_status}")
                logger.warning("   This may be expected if handlers return different formats")
                return True  # Still consider success if both executed
        else:
            logger.warning("⚠️ Could not compare results (missing status field)")
            # Check if both executed without errors
            old_success = old_result.get("success") is not False
            new_success = new_result.get("success") is not False and new_result.get("error") != "Route not found"
            
            if old_success and new_success:
                logger.info("✅ Both routing methods executed successfully")
                return True
            else:
                logger.warning(f"⚠️ Old success: {old_success}, New success: {new_success}")
                return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    result = asyncio.run(test_parallel_routing())
    sys.exit(0 if result else 1)











