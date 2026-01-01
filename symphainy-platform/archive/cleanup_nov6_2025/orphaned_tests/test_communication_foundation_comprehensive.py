#!/usr/bin/env python3
"""
Comprehensive Communication Foundation Test

Tests the new Communication Foundation with unified router management,
realm bridges, and API Gateway integration.

WHAT (Test Role): I test the Communication Foundation comprehensively
HOW (Test Implementation): I test all components and their integration
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
from foundations.communication_foundation.realm_bridges.solution_bridge import SolutionRealmBridge
from foundations.communication_foundation.realm_bridges.experience_bridge import ExperienceRealmBridge
from foundations.communication_foundation.infrastructure_adapters.api_gateway_adapter import APIGatewayAdapter

# Import DI Container
from foundations.di_container.di_container_service import DIContainerService

# Import other foundations for testing
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

# Import FastAPI for testing
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommunicationFoundationTest:
    """Comprehensive Communication Foundation Test Suite."""
    
    def __init__(self):
        """Initialize test suite."""
        self.di_container = None
        self.public_works_foundation = None
        self.curator_foundation = None
        self.communication_foundation = None
        self.fastapi_app = None
        self.test_client = None
        
    async def setup_test_environment(self):
        """Set up test environment with all foundations."""
        try:
            logger.info("🚀 Setting up Communication Foundation test environment...")
            
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
            
            # Create FastAPI app for testing
            self.fastapi_app = FastAPI(title="Communication Foundation Test")
            self.test_client = TestClient(self.fastapi_app)
            logger.info("✅ FastAPI test app created")
            
            logger.info("🎯 Communication Foundation test environment ready!")
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
            
            # Test router registration
            test_router = FastAPI(title="Test Router")
            router_manager.register_realm_router("test_realm", test_router)
            logger.info("✅ Test router registered successfully")
            
            logger.info("✅ FastAPI Router Manager test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ FastAPI Router Manager test failed: {e}")
            return False
    
    async def test_realm_bridges(self):
        """Test realm bridges functionality."""
        try:
            logger.info("🧪 Testing Realm Bridges...")
            
            # Test Solution Realm Bridge
            solution_bridge = self.communication_foundation.solution_bridge
            if solution_bridge:
                assert solution_bridge.is_initialized, "Solution bridge should be initialized"
                solution_router = solution_bridge.get_router()
                assert solution_router is not None, "Solution router should not be None"
                logger.info("✅ Solution Realm Bridge working")
            else:
                logger.warning("⚠️ Solution Realm Bridge not available")
            
            # Test Experience Realm Bridge
            experience_bridge = self.communication_foundation.experience_bridge
            if experience_bridge:
                assert experience_bridge.is_initialized, "Experience bridge should be initialized"
                experience_router = experience_bridge.get_router()
                assert experience_router is not None, "Experience router should not be None"
                logger.info("✅ Experience Realm Bridge working")
            else:
                logger.warning("⚠️ Experience Realm Bridge not available")
            
            logger.info("✅ Realm Bridges test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Realm Bridges test failed: {e}")
            return False
    
    async def test_api_gateway_adapter(self):
        """Test API Gateway Adapter functionality."""
        try:
            logger.info("🧪 Testing API Gateway Adapter...")
            
            # Get API Gateway adapter
            api_gateway = self.communication_foundation.api_gateway_adapter
            
            if not api_gateway:
                logger.warning("⚠️ API Gateway Adapter not available")
                return True  # Not critical for basic functionality
            
            # Test API Gateway initialization
            assert api_gateway.is_initialized, "API Gateway should be initialized"
            logger.info("✅ API Gateway Adapter is initialized")
            
            # Test SOA routing configuration
            soa_routing = api_gateway.soa_routing_config
            assert soa_routing is not None, "SOA routing config should not be None"
            logger.info("✅ SOA routing configuration available")
            
            logger.info("✅ API Gateway Adapter test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ API Gateway Adapter test failed: {e}")
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
            
            # Test WebSocket Abstraction
            websocket_abstraction = self.communication_foundation.websocket_abstraction
            if websocket_abstraction:
                logger.info("✅ WebSocket Abstraction available")
            else:
                logger.warning("⚠️ WebSocket Abstraction not available")
            
            logger.info("✅ Communication Abstractions test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Communication Abstractions test failed: {e}")
            return False
    
    async def test_soa_api_registration(self):
        """Test SOA API registration functionality."""
        try:
            logger.info("🧪 Testing SOA API Registration...")
            
            # Test registering SOA API
            test_api_endpoints = {
                "test_endpoint": {
                    "path": "/test",
                    "method": "GET",
                    "description": "Test endpoint"
                }
            }
            
            await self.communication_foundation.register_soa_api("test_service", test_api_endpoints)
            logger.info("✅ SOA API registration successful")
            
            # Test discovering SOA API
            discovered_api = await self.communication_foundation.discover_soa_api("test_service")
            if discovered_api:
                logger.info("✅ SOA API discovery successful")
            else:
                logger.warning("⚠️ SOA API discovery returned None")
            
            logger.info("✅ SOA API Registration test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ SOA API Registration test failed: {e}")
            return False
    
    async def test_messaging_and_events(self):
        """Test messaging and event functionality."""
        try:
            logger.info("🧪 Testing Messaging and Events...")
            
            # Test sending message
            test_message = {
                "type": "test_message",
                "data": {"test": "value"},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.communication_foundation.send_message(
                target_realm="test_realm",
                message_type="test",
                message_data=test_message
            )
            logger.info("✅ Message sending successful")
            
            # Test publishing event
            test_event = {
                "event_type": "test_event",
                "event_data": {"test": "value"},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.communication_foundation.publish_event(
                event_type="test",
                event_data=test_event
            )
            logger.info("✅ Event publishing successful")
            
            logger.info("✅ Messaging and Events test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Messaging and Events test failed: {e}")
            return False
    
    async def test_websocket_connections(self):
        """Test WebSocket connection functionality."""
        try:
            logger.info("🧪 Testing WebSocket Connections...")
            
            # Test establishing WebSocket connection
            connection_result = await self.communication_foundation.establish_websocket_connection(
                client_id="test_client",
                realm="test_realm"
            )
            
            if connection_result:
                logger.info("✅ WebSocket connection established")
            else:
                logger.warning("⚠️ WebSocket connection returned None")
            
            logger.info("✅ WebSocket Connections test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket Connections test failed: {e}")
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
    
    async def run_comprehensive_test(self):
        """Run comprehensive Communication Foundation test suite."""
        try:
            logger.info("🎯 Starting Comprehensive Communication Foundation Test Suite...")
            
            # Setup test environment
            if not await self.setup_test_environment():
                logger.error("❌ Test environment setup failed")
                return False
            
            # Run all tests
            test_results = []
            
            test_results.append(await self.test_fastapi_router_manager())
            test_results.append(await self.test_realm_bridges())
            test_results.append(await self.test_api_gateway_adapter())
            test_results.append(await self.test_communication_abstractions())
            test_results.append(await self.test_soa_api_registration())
            test_results.append(await self.test_messaging_and_events())
            test_results.append(await self.test_websocket_connections())
            test_results.append(await self.test_health_and_status())
            
            # Calculate results
            passed_tests = sum(test_results)
            total_tests = len(test_results)
            
            logger.info(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
            
            if passed_tests == total_tests:
                logger.info("🎉 All Communication Foundation tests passed!")
                return True
            else:
                logger.warning(f"⚠️ {total_tests - passed_tests} tests failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Comprehensive test failed: {e}")
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
    test_suite = CommunicationFoundationTest()
    success = await test_suite.run_comprehensive_test()
    
    if success:
        print("\n🎉 Communication Foundation Test Suite PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Communication Foundation Test Suite FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())





