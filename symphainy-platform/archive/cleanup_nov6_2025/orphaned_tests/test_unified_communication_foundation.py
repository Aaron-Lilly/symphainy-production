#!/usr/bin/env python3
"""
Test Unified Communication Foundation

This script tests the unified Communication Foundation with consolidated
realm bridges and router management.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedCommunicationFoundationTester:
    """Test the unified Communication Foundation."""
    
    def __init__(self):
        self.test_results = []
    
    async def test_communication_foundation_initialization(self) -> Dict[str, Any]:
        """Test Communication Foundation initialization."""
        logger.info("🧪 Testing: Communication Foundation Initialization")
        
        try:
            # Import Communication Foundation
            from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            
            # Create mock dependencies
            di_container = DIContainerService("test_communication")
            public_works_foundation = PublicWorksFoundationService(di_container)
            curator_foundation = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=public_works_foundation
            )
            
            # Initialize Communication Foundation
            communication_foundation = CommunicationFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation,
                curator_foundation=curator_foundation
            )
            
            # Test initialization
            await communication_foundation.initialize()
            
            # Test unified router
            unified_router = await communication_foundation.get_unified_router()
            
            logger.info("✅ Communication Foundation initialization successful")
            logger.info(f"   Unified router type: {type(unified_router)}")
            
            return {
                "test_name": "Communication Foundation Initialization",
                "success": True,
                "unified_router_available": unified_router is not None,
                "router_type": str(type(unified_router))
            }
            
        except Exception as e:
            logger.error(f"❌ Communication Foundation initialization failed: {e}")
            return {
                "test_name": "Communication Foundation Initialization",
                "success": False,
                "error": str(e)
            }
    
    async def test_realm_bridges(self) -> Dict[str, Any]:
        """Test realm bridges within Communication Foundation."""
        logger.info("🧪 Testing: Realm Bridges")
        
        try:
            # Import realm bridges
            from foundations.communication_foundation.realm_bridges.solution_bridge import SolutionRealmBridge
            from foundations.communication_foundation.realm_bridges.experience_bridge import ExperienceRealmBridge
            
            # Test Solution Bridge
            solution_bridge = SolutionRealmBridge(
                di_container=None,  # Mock
                public_works_foundation=None,  # Mock
                curator_foundation=None  # Mock
            )
            
            # Test Experience Bridge
            experience_bridge = ExperienceRealmBridge(
                di_container=None,  # Mock
                public_works_foundation=None,  # Mock
                curator_foundation=None  # Mock
            )
            
            logger.info("✅ Realm bridges created successfully")
            logger.info(f"   Solution Bridge type: {type(solution_bridge)}")
            logger.info(f"   Experience Bridge type: {type(experience_bridge)}")
            
            return {
                "test_name": "Realm Bridges",
                "success": True,
                "solution_bridge_available": solution_bridge is not None,
                "experience_bridge_available": experience_bridge is not None
            }
            
        except Exception as e:
            logger.error(f"❌ Realm bridges test failed: {e}")
            return {
                "test_name": "Realm Bridges",
                "success": False,
                "error": str(e)
            }
    
    async def test_fastapi_router_manager(self) -> Dict[str, Any]:
        """Test FastAPI Router Manager."""
        logger.info("🧪 Testing: FastAPI Router Manager")
        
        try:
            # Import FastAPI Router Manager
            from foundations.communication_foundation.infrastructure_adapters.fastapi_router_manager import FastAPIRouterManager
            
            # Create router manager
            router_manager = FastAPIRouterManager()
            
            # Test initialization
            await router_manager.initialize()
            
            # Test unified router
            unified_router = router_manager.get_unified_router()
            
            # Test router stats
            stats = await router_manager.get_router_stats()
            
            logger.info("✅ FastAPI Router Manager test successful")
            logger.info(f"   Unified router type: {type(unified_router)}")
            logger.info(f"   Router stats: {stats}")
            
            return {
                "test_name": "FastAPI Router Manager",
                "success": True,
                "unified_router_available": unified_router is not None,
                "router_stats": stats
            }
            
        except Exception as e:
            logger.error(f"❌ FastAPI Router Manager test failed: {e}")
            return {
                "test_name": "FastAPI Router Manager",
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Communication Foundation tests."""
        logger.info("🚀 Starting Unified Communication Foundation Tests")
        logger.info("=" * 60)
        
        # Run all tests
        test_results = []
        
        # Test 1: Communication Foundation Initialization
        result1 = await self.test_communication_foundation_initialization()
        test_results.append(result1)
        
        # Test 2: Realm Bridges
        result2 = await self.test_realm_bridges()
        test_results.append(result2)
        
        # Test 3: FastAPI Router Manager
        result3 = await self.test_fastapi_router_manager()
        test_results.append(result3)
        
        # Compile results
        successful_tests = sum(1 for result in test_results if result.get("success", False))
        total_tests = len(test_results)
        
        logger.info("=" * 60)
        logger.info(f"📊 Test Results: {successful_tests}/{total_tests} tests passed")
        
        if successful_tests == total_tests:
            logger.info("🎉 All tests passed! Unified Communication Foundation is working correctly.")
        else:
            logger.warning(f"⚠️  {total_tests - successful_tests} tests failed. Check the logs above for details.")
        
        return {
            "success": successful_tests == total_tests,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "test_results": test_results,
            "timestamp": datetime.utcnow().isoformat()
        }


async def main():
    """Main test function."""
    print("🧪 Unified Communication Foundation Test Suite")
    print("=" * 60)
    print("This test suite verifies that the unified Communication Foundation")
    print("with consolidated realm bridges and router management works correctly.")
    print("=" * 60)
    
    tester = UnifiedCommunicationFoundationTester()
    results = await tester.run_all_tests()
    
    # Print summary
    print("\n📋 Test Summary:")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Successful: {results['successful_tests']}")
    print(f"   Failed: {results['failed_tests']}")
    print(f"   Success Rate: {(results['successful_tests']/results['total_tests']*100):.1f}%")
    
    if results['success']:
        print("\n🎉 All tests passed! The unified Communication Foundation is working correctly.")
        print("\n✅ Benefits achieved:")
        print("   - Single communication layer for all realms")
        print("   - Unified router management")
        print("   - Consolidated realm bridges")
        print("   - Simplified startup process")
        print("   - Holistic communication testing")
    else:
        print(f"\n⚠️  {results['failed_tests']} tests failed. Please check the logs above for details.")
        print("\n🔧 Common issues:")
        print("   - Missing dependencies")
        print("   - Import errors")
        print("   - Initialization failures")
        print("   - Router management issues")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())






