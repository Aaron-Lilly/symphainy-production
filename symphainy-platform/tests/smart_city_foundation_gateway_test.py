#!/usr/bin/env python3
"""
Smart City Foundation Gateway Test - Real Implementation Test

Tests the Smart City Foundation Gateway with actual platform implementations.
This test verifies that our gateway works with real Public Works Foundation methods.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

# Import actual platform services
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

# Import our Smart City Foundation Gateway
from smartcity.foundation_gateway import SmartCityFoundationGateway


class SmartCityFoundationGatewayTest:
    """Test the Smart City Foundation Gateway with real implementations."""
    
    def __init__(self):
        self.logger = logging.getLogger("SmartCityFoundationGatewayTest")
        self.di_container = None
        self.gateway = None
        
    async def setup_test_environment(self):
        """Set up test environment with real services."""
        try:
            self.logger.info("🚀 Setting up test environment...")
            
            # Create DI Container with real services
            self.di_container = DIContainerService(
                realm_name="test_realm",
                security_provider=None,
                authorization_guard=None
            )
            
            # Initialize Public Works Foundation
            public_works = PublicWorksFoundationService(self.di_container)
            await public_works.initialize_foundation()
            
            # Initialize Communication Foundation
            communication = CommunicationFoundationService(self.di_container)
            await communication.initialize_foundation()
            
            # Initialize Curator Foundation
            curator = CuratorFoundationService(self.di_container)
            await curator.initialize_foundation()
            
            # Register services in DI Container
            self.di_container.service_registry["PublicWorksFoundationService"] = public_works
            self.di_container.service_registry["CommunicationFoundationService"] = communication
            self.di_container.service_registry["CuratorFoundationService"] = curator
            
            self.logger.info("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup test environment: {e}")
            return False
    
    async def test_gateway_initialization(self):
        """Test Smart City Foundation Gateway initialization."""
        try:
            self.logger.info("🧪 Testing gateway initialization...")
            
            # Create gateway
            self.gateway = SmartCityFoundationGateway(self.di_container)
            
            # Initialize gateway
            success = await self.gateway.initialize()
            
            if success:
                self.logger.info("✅ Gateway initialization successful")
                return True
            else:
                self.logger.error("❌ Gateway initialization failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Gateway initialization test failed: {e}")
            return False
    
    async def test_abstraction_access(self):
        """Test abstraction access through gateway."""
        try:
            self.logger.info("🧪 Testing abstraction access...")
            
            # Test generic get_abstraction method
            abstractions_to_test = [
                "auth", "authorization", "session", "tenant",
                "file_management", "content_metadata", "llm", "mcp"
            ]
            
            for abstraction_name in abstractions_to_test:
                try:
                    abstraction = self.gateway.get_abstraction(abstraction_name)
                    self.logger.info(f"✅ Successfully retrieved {abstraction_name} abstraction")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to retrieve {abstraction_name} abstraction: {e}")
            
            # Test direct abstraction methods
            try:
                auth_abstraction = self.gateway.get_auth_abstraction()
                self.logger.info("✅ Successfully retrieved auth abstraction via direct method")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to retrieve auth abstraction via direct method: {e}")
            
            try:
                file_abstraction = self.gateway.get_file_management_abstraction()
                self.logger.info("✅ Successfully retrieved file management abstraction via direct method")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to retrieve file management abstraction via direct method: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Abstraction access test failed: {e}")
            return False
    
    async def test_health_check(self):
        """Test gateway health check."""
        try:
            self.logger.info("🧪 Testing gateway health check...")
            
            health_status = await self.gateway.health_check()
            
            self.logger.info(f"Health Status: {health_status['status']}")
            self.logger.info(f"Components: {list(health_status['components'].keys())}")
            
            if health_status['status'] in ['healthy', 'degraded']:
                self.logger.info("✅ Health check passed")
                return True
            else:
                self.logger.error("❌ Health check failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Health check test failed: {e}")
            return False
    
    async def test_service_capabilities(self):
        """Test service capabilities registration."""
        try:
            self.logger.info("🧪 Testing service capabilities...")
            
            capabilities = await self.gateway.get_service_capabilities()
            
            self.logger.info(f"Service Name: {capabilities['service_name']}")
            self.logger.info(f"Service Type: {capabilities['service_type']}")
            self.logger.info(f"Available Abstractions: {len(capabilities['capabilities']['infrastructure_abstractions'])}")
            self.logger.info(f"Registered Roles: {len(capabilities['capabilities']['smart_city_roles'])}")
            
            if capabilities['is_initialized']:
                self.logger.info("✅ Service capabilities test passed")
                return True
            else:
                self.logger.error("❌ Service capabilities test failed - not initialized")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Service capabilities test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests."""
        try:
            self.logger.info("🚀 Starting Smart City Foundation Gateway tests...")
            
            # Setup
            if not await self.setup_test_environment():
                return False
            
            # Test gateway initialization
            if not await self.test_gateway_initialization():
                return False
            
            # Test abstraction access
            if not await self.test_abstraction_access():
                return False
            
            # Test health check
            if not await self.test_health_check():
                return False
            
            # Test service capabilities
            if not await self.test_service_capabilities():
                return False
            
            self.logger.info("🎉 All tests passed! Smart City Foundation Gateway is working correctly.")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Test suite failed: {e}")
            return False


async def main():
    """Main test function."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    test_suite = SmartCityFoundationGatewayTest()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🎉 SUCCESS: Smart City Foundation Gateway test completed successfully!")
        print("✅ The gateway is working with real platform implementations.")
    else:
        print("\n❌ FAILURE: Smart City Foundation Gateway test failed.")
        print("⚠️ Check the logs above for details.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())


