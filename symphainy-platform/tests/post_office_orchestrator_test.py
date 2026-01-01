#!/usr/bin/env python3
"""
Post Office Communication Orchestrator Test - Real Implementation Test

Tests the new Post Office Service as a Communication Orchestrator with actual platform implementations.
This test verifies that our orchestrator properly delegates to Communication Foundation.
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
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

# Import our new Post Office Service
from backend.smart_city.services.post_office.post_office_service import PostOfficeService

# Import Post Office interface
from backend.smart_city.interfaces.post_office_interface import (
    SendMessageRequest,
    RouteEventRequest,
    RegisterAgentRequest,
    GetMessagesRequest,
    GetMessageStatusRequest,
    MessagePriority,
    EventType,
    AgentStatus
)


class PostOfficeOrchestratorTest:
    """Test the Post Office Service as Communication Orchestrator."""
    
    def __init__(self):
        self.logger = logging.getLogger("PostOfficeOrchestratorTest")
        self.di_container = None
        self.post_office = None
        
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
            
            # Initialize Communication Foundation
            communication = CommunicationFoundationService(self.di_container)
            await communication.initialize_foundation()
            
            # Initialize Curator Foundation
            curator = CuratorFoundationService(self.di_container)
            await curator.initialize_foundation()
            
            # Register services in DI Container
            self.di_container.service_registry["CommunicationFoundationService"] = communication
            self.di_container.service_registry["CuratorFoundationService"] = curator
            
            self.logger.info("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup test environment: {e}")
            return False
    
    async def test_post_office_initialization(self):
        """Test Post Office Service initialization."""
        try:
            self.logger.info("🧪 Testing Post Office initialization...")
            
            # Create Post Office Service
            self.post_office = PostOfficeService(self.di_container)
            
            # Initialize Post Office
            success = await self.post_office.initialize()
            
            if success:
                self.logger.info("✅ Post Office initialization successful")
                return True
            else:
                self.logger.error("❌ Post Office initialization failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Post Office initialization test failed: {e}")
            return False
    
    async def test_agent_registration(self):
        """Test agent registration orchestration."""
        try:
            self.logger.info("🧪 Testing agent registration...")
            
            # Register a test agent
            register_request = RegisterAgentRequest(
                agent_id="test_agent_001",
                agent_name="Test Agent",
                agent_type="liaison",
                capabilities=["send_message", "receive_message"],
                endpoint="http://localhost:8000/agent",
                tenant_id="test_tenant"
            )
            
            response = await self.post_office.register_agent(register_request)
            
            if response.success and response.status == AgentStatus.ACTIVE:
                self.logger.info("✅ Agent registration successful")
                return True
            else:
                self.logger.error(f"❌ Agent registration failed: {response.error_message}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Agent registration test failed: {e}")
            return False
    
    async def test_message_orchestration(self):
        """Test message orchestration."""
        try:
            self.logger.info("🧪 Testing message orchestration...")
            
            # Send a test message
            send_request = SendMessageRequest(
                message_id="test_message_001",
                sender_id="test_agent_001",
                recipient_id="user_123",
                subject="Test Message",
                content="This is a test message",
                message_type="text",
                priority=MessagePriority.NORMAL,
                tenant_id="test_tenant"
            )
            
            response = await self.post_office.send_message(send_request)
            
            if response.success and response.status.value == "sent":
                self.logger.info("✅ Message orchestration successful")
                
                # Test message retrieval
                get_request = GetMessagesRequest(
                    recipient_id="user_123",
                    limit=10,
                    tenant_id="test_tenant"
                )
                
                get_response = await self.post_office.get_messages(get_request)
                
                if get_response.success and len(get_response.messages) > 0:
                    self.logger.info("✅ Message retrieval successful")
                    
                    # Test message status check
                    status_request = GetMessageStatusRequest(
                        message_id="test_message_001",
                        tenant_id="test_tenant"
                    )
                    
                    status_response = await self.post_office.get_message_status(status_request)
                    
                    if status_response.success:
                        self.logger.info("✅ Message status check successful")
                        return True
                    else:
                        self.logger.error(f"❌ Message status check failed: {status_response.error_message}")
                        return False
                else:
                    self.logger.error(f"❌ Message retrieval failed: {get_response.error_message}")
                    return False
            else:
                self.logger.error(f"❌ Message orchestration failed: {response.error_message}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Message orchestration test failed: {e}")
            return False
    
    async def test_event_orchestration(self):
        """Test event orchestration."""
        try:
            self.logger.info("🧪 Testing event orchestration...")
            
            # Route a test event
            route_request = RouteEventRequest(
                event_id="test_event_001",
                event_type=EventType.USER_ACTION,
                source="test_source",
                target="test_target",
                event_data={"action": "test_action", "data": "test_data"},
                priority=MessagePriority.NORMAL,
                tenant_id="test_tenant"
            )
            
            response = await self.post_office.route_event(route_request)
            
            if response.success and len(response.routing_results) > 0:
                self.logger.info("✅ Event orchestration successful")
                return True
            else:
                self.logger.error(f"❌ Event orchestration failed: {response.error_message}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Event orchestration test failed: {e}")
            return False
    
    async def test_health_check(self):
        """Test Post Office health check."""
        try:
            self.logger.info("🧪 Testing Post Office health check...")
            
            health_status = await self.post_office.health_check()
            
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
            
            capabilities = await self.post_office.get_service_capabilities()
            
            self.logger.info(f"Service Name: {capabilities['service_name']}")
            self.logger.info(f"Service Type: {capabilities['service_type']}")
            self.logger.info(f"Message Orchestration: {len(capabilities['capabilities']['message_orchestration'])}")
            self.logger.info(f"Event Orchestration: {len(capabilities['capabilities']['event_orchestration'])}")
            self.logger.info(f"Active Agents: {capabilities['capabilities']['active_agents']}")
            
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
            self.logger.info("🚀 Starting Post Office Communication Orchestrator tests...")
            
            # Setup
            if not await self.setup_test_environment():
                return False
            
            # Test Post Office initialization
            if not await self.test_post_office_initialization():
                return False
            
            # Test agent registration
            if not await self.test_agent_registration():
                return False
            
            # Test message orchestration
            if not await self.test_message_orchestration():
                return False
            
            # Test event orchestration
            if not await self.test_event_orchestration():
                return False
            
            # Test health check
            if not await self.test_health_check():
                return False
            
            # Test service capabilities
            if not await self.test_service_capabilities():
                return False
            
            self.logger.info("🎉 All tests passed! Post Office Communication Orchestrator is working correctly.")
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
    test_suite = PostOfficeOrchestratorTest()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🎉 SUCCESS: Post Office Communication Orchestrator test completed successfully!")
        print("✅ The orchestrator is working with real platform implementations.")
    else:
        print("\n❌ FAILURE: Post Office Communication Orchestrator test failed.")
        print("⚠️ Check the logs above for details.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())


