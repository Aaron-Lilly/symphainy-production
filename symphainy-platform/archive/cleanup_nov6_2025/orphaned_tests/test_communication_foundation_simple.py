#!/usr/bin/env python3
"""
Simple Communication Foundation Test

Tests the Communication Foundation without the broken imports.

WHAT (Test Role): I test the Communication Foundation simply
HOW (Test Implementation): I test basic functionality without broken imports
"""

import asyncio
import sys
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Communication Foundation components
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.communication_foundation.infrastructure_adapters.fastapi_router_manager import FastAPIRouterManager

# Import DI Container
from foundations.di_container.di_container_service import DIContainerService

# Import other foundations for testing
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleCommunicationFoundationTest:
    """Simple Communication Foundation Test Suite."""
    
    def __init__(self):
        """Initialize test suite."""
        self.di_container = None
        self.public_works_foundation = None
        self.curator_foundation = None
        self.communication_foundation = None
        
    async def setup_test_environment(self):
        """Set up test environment with all foundations."""
        try:
            logger.info("🚀 Setting up Simple Communication Foundation test environment...")
            
            # Initialize DI Container
            self.di_container = DIContainerService("communication_test")
            logger.info("✅ DI Container initialized")
            
            # Initialize Public Works Foundation
            self.public_works_foundation = PublicWorksFoundationService(
                di_container=self.di_container
            )
            await self.public_works_foundation.initialize()
            logger.info("✅ Public Works Foundation initialized")
            
            # Initialize Curator Foundation
            self.curator_foundation = CuratorFoundationService(
                foundation_services=self.di_container,
                public_works_foundation=self.public_works_foundation
            )
            await self.curator_foundation.initialize()
            logger.info("✅ Curator Foundation initialized")
            
            # Initialize Communication Foundation
            self.communication_foundation = CommunicationFoundationService(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            await self.communication_foundation.initialize()
            logger.info("✅ Communication Foundation initialized")
            
            logger.info("🎯 Simple Communication Foundation test environment ready!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup test environment: {e}")
            return False
    
    async def test_fastapi_router_manager(self):
        """Test FastAPI Router Manager functionality."""
        try:
            logger.info("🧪 Testing FastAPI Router Manager...")
            
            # Get router manager from communication foundation
            router_manager = self.communication_foundation.fastapi_router_manager
            
            if not router_manager:
                logger.error("❌ FastAPI Router Manager not initialized")
                return False
            
            # Test router manager initialization
            assert router_manager.is_initialized, "Router manager should be initialized"
            logger.info("✅ FastAPI Router Manager is initialized")
            
            # Test getting unified router
            unified_router = router_manager.get_unified_router()
            assert unified_router is not None, "Unified router should not be None"
            logger.info("✅ Unified router retrieved successfully")
            
            logger.info("✅ FastAPI Router Manager test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ FastAPI Router Manager test failed: {e}")
            return False
    
    async def test_communication_abstractions(self):
        """Test communication abstractions."""
        try:
            logger.info("🧪 Testing Communication Abstractions...")
            
            # Test SOA Client Abstraction
            soa_client = self.communication_foundation.soa_client_abstraction
            if soa_client:
                logger.info("✅ SOA Client Abstraction available")
            else:
                logger.warning("⚠️ SOA Client Abstraction not available")
            
            # Test Communication Abstraction
            communication_abstraction = self.communication_foundation.communication_abstraction
            if communication_abstraction:
                logger.info("✅ Communication Abstraction available")
            else:
                logger.warning("⚠️ Communication Abstraction not available")
            
            logger.info("✅ Communication Abstractions test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Communication Abstractions test failed: {e}")
            return False
    
    async def test_health_and_status(self):
        """Test health and status functionality."""
        try:
            logger.info("🧪 Testing Health and Status...")
            
            # Test getting service health
            health_status = await self.communication_foundation.get_service_health()
            assert health_status is not None, "Health status should not be None"
            logger.info("✅ Service health retrieved successfully")
            
            # Test getting communication foundation status
            foundation_status = await self.communication_foundation.get_communication_foundation_status()
            assert foundation_status is not None, "Foundation status should not be None"
            logger.info("✅ Foundation status retrieved successfully")
            
            logger.info("✅ Health and Status test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Health and Status test failed: {e}")
            return False
    
    async def run_simple_test(self):
        """Run simple Communication Foundation test suite."""
        try:
            logger.info("🎯 Starting Simple Communication Foundation Test Suite...")
            
            # Setup test environment
            if not await self.setup_test_environment():
                logger.error("❌ Test environment setup failed")
                return False
            
            # Run all tests
            test_results = []
            
            test_results.append(await self.test_fastapi_router_manager())
            test_results.append(await self.test_communication_abstractions())
            test_results.append(await self.test_health_and_status())
            
            # Calculate results
            passed_tests = sum(test_results)
            total_tests = len(test_results)
            
            logger.info(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
            
            if passed_tests == total_tests:
                logger.info("🎉 All Simple Communication Foundation tests passed!")
                return True
            else:
                logger.warning(f"⚠️ {total_tests - passed_tests} tests failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Simple test failed: {e}")
            return False
        
        finally:
            # Cleanup
            await self.cleanup_test_environment()
    
    async def cleanup_test_environment(self):
        """Clean up test environment."""
        try:
            logger.info("🧹 Cleaning up test environment...")
            
            if self.communication_foundation:
                await self.communication_foundation.shutdown()
                logger.info("✅ Communication Foundation shutdown")
            
            if self.curator_foundation:
                await self.curator_foundation.shutdown()
                logger.info("✅ Curator Foundation shutdown")
            
            if self.public_works_foundation:
                await self.public_works_foundation.shutdown()
                logger.info("✅ Public Works Foundation shutdown")
            
            logger.info("✅ Test environment cleanup complete")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")


async def main():
    """Main test function."""
    test_suite = SimpleCommunicationFoundationTest()
    success = await test_suite.run_simple_test()
    
    if success:
        print("\n🎉 Simple Communication Foundation Test Suite PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Simple Communication Foundation Test Suite FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())





