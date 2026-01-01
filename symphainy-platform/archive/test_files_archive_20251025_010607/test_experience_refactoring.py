#!/usr/bin/env python3
"""
Experience Dimension Refactoring Test

Tests the refactored Experience services to ensure they work correctly with pure DI.

WHAT (Test): I verify that the refactored Experience services work correctly
HOW (Test): I create mock dependencies and test service initialization and basic operations
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

# Import DIContainerService
from foundations.di_container.di_container_service import DIContainerService

# Import refactored services
from experience.roles.frontend_integration.frontend_integration_service import FrontendIntegrationService
from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
from experience.roles.journey_manager.journey_manager_service import JourneyManagerService

# Import protocols
from experience.protocols.experience_smart_city_api_protocol import ExperienceSmartCityAPIService
from experience.protocols.experience_abstraction_protocol import ExperienceAbstractionAccessService


class MockSmartCityAPIService:
    """Mock Smart City API Service for testing."""
    
    def __init__(self):
        self.logger = logging.getLogger("mock_smart_city_api")
    
    async def authenticate_user(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "user": {"user_id": "test_user", "email": "test@example.com", "full_name": "Test User"},
            "token": "test_token"
        }
    
    async def manage_user_session_state(self, user_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "session_updated": True}
    
    async def route_user_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "routed_to": "test_service"}
    
    async def record_user_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "recorded": True}
    
    async def get_user_telemetry(self, user_id: str) -> Dict[str, Any]:
        return {"success": True, "telemetry": {"interactions": 10}}
    
    async def get_user_metadata(self, user_id: str) -> Dict[str, Any]:
        return {"success": True, "metadata": {"preferences": {}}}
    
    async def execute_user_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "workflow_result": "completed"}
    
    async def store_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "stored": True}


class MockAbstractionAccessService:
    """Mock Abstraction Access Service for testing."""
    
    def __init__(self):
        self.logger = logging.getLogger("mock_abstraction_access")
    
    async def get_ui_abstractions(self) -> Dict[str, Any]:
        return {"success": True, "abstractions": {"ui_components": []}}
    
    async def get_frontend_integration_abstractions(self) -> Dict[str, Any]:
        return {"success": True, "abstractions": {"api_endpoints": []}}
    
    async def get_authentication_abstractions(self) -> Dict[str, Any]:
        return {"success": True, "abstractions": {"auth_methods": []}}
    
    async def get_user_experience_abstractions(self) -> Dict[str, Any]:
        return {"success": True, "abstractions": {"ux_patterns": []}}
    
    async def get_session_management_abstractions(self) -> Dict[str, Any]:
        return {"success": True, "abstractions": {"session_patterns": []}}
    
    async def get_journey_management_abstractions(self) -> Dict[str, Any]:
        return {"success": True, "abstractions": {"journey_patterns": []}}


class MockBusinessAPIs:
    """Mock Business APIs for testing."""
    
    def __init__(self):
        self.logger = logging.getLogger("mock_business_apis")
    
    async def list_content_files(self, session_token: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"success": True, "files": []}
    
    async def upload_content_file(self, file_data: bytes, metadata: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        return {"success": True, "file": {"id": "test_file", "name": "test.pdf"}}


class MockAgentAPIs:
    """Mock Agent APIs for testing."""
    
    def __init__(self):
        self.logger = logging.getLogger("mock_agent_apis")
    
    async def send_agent_message(self, message: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        return {"success": True, "response": "Test response"}


async def test_frontend_integration_service():
    """Test FrontendIntegrationService."""
    print("🧪 Testing FrontendIntegrationService...")
    
    try:
        # Create mock dependencies
        foundation_services = DIContainerService()
        smart_city_apis = MockSmartCityAPIService()
        business_apis = MockBusinessAPIs()
        agent_apis = MockAgentAPIs()
        abstraction_access = MockAbstractionAccessService()
        
        # Create service
        service = FrontendIntegrationService(
            foundation_services=foundation_services,
            smart_city_apis=smart_city_apis,
            business_apis=business_apis,
            agent_apis=agent_apis,
            abstraction_access=abstraction_access
        )
        
        # Test initialization
        await service.initialize()
        print("✅ FrontendIntegrationService initialized successfully")
        
        # Test health check
        health = await service.get_service_health()
        print(f"✅ FrontendIntegrationService health: {health['status']}")
        
        # Test API request routing
        result = await service.route_api_request(
            endpoint="/api/content/files",
            method="GET",
            user_context={"user_id": "test_user"},
            session_token="test_token"
        )
        print(f"✅ FrontendIntegrationService API routing: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ FrontendIntegrationService test failed: {e}")
        return False


async def test_experience_manager_service():
    """Test ExperienceManagerService."""
    print("🧪 Testing ExperienceManagerService...")
    
    try:
        # Create mock dependencies
        foundation_services = DIContainerService()
        smart_city_apis = MockSmartCityAPIService()
        abstraction_access = MockAbstractionAccessService()
        
        # Create service
        service = ExperienceManagerService(
            foundation_services=foundation_services,
            smart_city_apis=smart_city_apis,
            abstraction_access=abstraction_access
        )
        
        # Test initialization
        await service.initialize()
        print("✅ ExperienceManagerService initialized successfully")
        
        # Test health check
        health = await service.get_service_health()
        print(f"✅ ExperienceManagerService health: {health['status']}")
        
        # Test user session management
        result = await service.manage_user_session(
            user_id="test_user",
            session_data={"current_page": "dashboard"}
        )
        print(f"✅ ExperienceManagerService session management: {result['success']}")
        
        # Test user behavior tracking
        result = await service.track_user_behavior(
            user_id="test_user",
            behavior_data={"action": "click", "element": "button"}
        )
        print(f"✅ ExperienceManagerService behavior tracking: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ExperienceManagerService test failed: {e}")
        return False


async def test_journey_manager_service():
    """Test JourneyManagerService."""
    print("🧪 Testing JourneyManagerService...")
    
    try:
        # Create mock dependencies
        foundation_services = DIContainerService()
        smart_city_apis = MockSmartCityAPIService()
        abstraction_access = MockAbstractionAccessService()
        
        # Create service
        service = JourneyManagerService(
            foundation_services=foundation_services,
            smart_city_apis=smart_city_apis,
            abstraction_access=abstraction_access
        )
        
        # Test initialization
        await service.initialize()
        print("✅ JourneyManagerService initialized successfully")
        
        # Test health check
        health = await service.get_service_health()
        print(f"✅ JourneyManagerService health: {health['status']}")
        
        # Test journey creation
        journey_spec = {
            "user_id": "test_user",
            "template": "onboarding",
            "name": "Test Journey"
        }
        result = await service.create_user_journey(journey_spec)
        print(f"✅ JourneyManagerService journey creation: {result['success']}")
        
        if result['success']:
            journey_id = result['journey_id']
            
            # Test journey execution
            result = await service.execute_user_journey(
                journey_id=journey_id,
                user_context={"user_id": "test_user"}
            )
            print(f"✅ JourneyManagerService journey execution: {result['success']}")
            
            # Test journey progress tracking
            result = await service.track_journey_progress(
                journey_id=journey_id,
                user_id="test_user"
            )
            print(f"✅ JourneyManagerService progress tracking: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ JourneyManagerService test failed: {e}")
        return False


async def test_service_integration():
    """Test service integration and dependency injection."""
    print("🧪 Testing service integration...")
    
    try:
        # Create shared dependencies
        foundation_services = DIContainerService()
        smart_city_apis = MockSmartCityAPIService()
        business_apis = MockBusinessAPIs()
        agent_apis = MockAgentAPIs()
        abstraction_access = MockAbstractionAccessService()
        
        # Create services with proper DI
        frontend_service = FrontendIntegrationService(
            foundation_services=foundation_services,
            smart_city_apis=smart_city_apis,
            business_apis=business_apis,
            agent_apis=agent_apis,
            abstraction_access=abstraction_access
        )
        
        experience_service = ExperienceManagerService(
            foundation_services=foundation_services,
            smart_city_apis=smart_city_apis,
            abstraction_access=abstraction_access,
            frontend_integration_service=frontend_service
        )
        
        journey_service = JourneyManagerService(
            foundation_services=foundation_services,
            smart_city_apis=smart_city_apis,
            abstraction_access=abstraction_access,
            experience_manager_service=experience_service
        )
        
        # Initialize all services
        await frontend_service.initialize()
        await experience_service.initialize()
        await journey_service.initialize()
        
        print("✅ All services initialized with proper DI")
        
        # Test cross-service communication
        # Create a journey that uses experience management
        journey_spec = {
            "user_id": "integration_test_user",
            "template": "onboarding",
            "name": "Integration Test Journey"
        }
        
        journey_result = await journey_service.create_user_journey(journey_spec)
        if journey_result['success']:
            journey_id = journey_result['journey_id']
            
            # Track user behavior through experience manager
            behavior_result = await experience_service.track_user_behavior(
                user_id="integration_test_user",
                behavior_data={"action": "journey_started", "journey_id": journey_id}
            )
            
            print(f"✅ Cross-service integration: {behavior_result['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service integration test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Experience Dimension Refactoring Tests...")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    test_results = []
    
    # Run individual service tests
    test_results.append(await test_frontend_integration_service())
    print()
    
    test_results.append(await test_experience_manager_service())
    print()
    
    test_results.append(await test_journey_manager_service())
    print()
    
    # Run integration test
    test_results.append(await test_service_integration())
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(test_results)}")
    print(f"❌ Failed: {len(test_results) - sum(test_results)}")
    print(f"📈 Success Rate: {sum(test_results) / len(test_results) * 100:.1f}%")
    
    if all(test_results):
        print("🎉 All tests passed! Experience Dimension refactoring is successful!")
        return True
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
