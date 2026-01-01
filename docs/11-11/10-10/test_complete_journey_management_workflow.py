#!/usr/bin/env python3
"""
Complete Journey Management Workflow Test

This test validates the complete journey management workflow from business outcome
landing page through journey persistence to frontend integration.

TEST SCOPE:
- Journey persistence service
- Business outcome landing page service
- Experience layer integration
- Frontend component integration
- End-to-end workflow validation
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add the platform directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "symphainy-platform"))

# Mock UserContext for testing
class UserContext:
    def __init__(self, tenant_id: str, user_id: str, session_id: str):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.session_id = session_id
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from journey_solution.services.journey_persistence_service import JourneyPersistenceService, JourneyType, JourneyStatus
from journey_solution.services.business_outcome_landing_page_service import BusinessOutcomeLandingPageService
from experience.services.business_outcome_experience_service import BusinessOutcomeExperienceService


class MockDIContainerService(DIContainerService):
    """Mock DI Container Service for testing."""
    
    def __init__(self, service_name: str):
        super().__init__(service_name)
        self.config = MockUnifiedConfigurationManager()
        self.public_works_foundation = MockPublicWorksFoundationService()
        self.curator_foundation = MockCuratorFoundationService()
    
    def get_service(self, service_name: str):
        """Get a service by name."""
        if service_name == "JourneyPersistenceService":
            return MockJourneyPersistenceService()
        elif service_name == "BusinessOutcomeLandingPageService":
            return MockBusinessOutcomeLandingPageService()
        elif service_name == "ExperienceManagerService":
            return MockExperienceManagerService()
        elif service_name == "FrontendIntegrationService":
            return MockFrontendIntegrationService()
        elif service_name == "JourneyManagerService":
            return MockJourneyManagerService()
        elif service_name == "JourneyOrchestratorService":
            return MockJourneyOrchestratorService()
        elif service_name == "GuideAgent":
            return MockGuideAgent()
        else:
            return None
    
    def get_public_works_foundation(self):
        """Get public works foundation."""
        return self.public_works_foundation
    
    def get_curator_foundation(self):
        """Get curator foundation."""
        return self.curator_foundation


class MockUnifiedConfigurationManager:
    """Mock Unified Configuration Manager."""
    
    def get(self, key: str, default: Any = None) -> Any:
        if key == "MULTI_TENANT_ENABLED":
            return True
        return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        return self.get(key, default)


class MockPublicWorksFoundationService:
    """Mock Public Works Foundation Service."""
    
    def __init__(self):
        self.llm_abstraction = MockLLMAbstraction()


class MockCuratorFoundationService:
    """Mock Curator Foundation Service."""
    
    def __init__(self):
        self.services = {}


class MockLLMAbstraction:
    """Mock LLM Abstraction."""
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        return f"Mock LLM response for: {prompt}"
    
    async def analyze_text(self, text: str, **kwargs) -> Dict[str, Any]:
        return {"analysis": f"Mock analysis for: {text}"}


class MockJourneyPersistenceService:
    """Mock Journey Persistence Service."""
    
    def __init__(self):
        self.journeys = {}
        self.journey_history = {}
    
    async def create_journey(self, user_context: UserContext, business_outcome: str, 
                           journey_type: JourneyType = JourneyType.MVP, 
                           journey_data: Dict[str, Any] = None) -> Any:
        """Create a journey."""
        journey_id = f"journey_{len(self.journeys) + 1}"
        journey_context = MockJourneyContext(
            journey_id=journey_id,
            tenant_id=user_context.tenant_id,
            user_id=user_context.user_id,
            session_id=user_context.session_id,
            journey_type=journey_type,
            business_outcome=business_outcome,
            journey_data=journey_data or {}
        )
        self.journeys[journey_id] = journey_context
        return journey_context
    
    async def get_journey(self, journey_id: str) -> Any:
        """Get a journey."""
        return self.journeys.get(journey_id)
    
    async def update_journey(self, journey_id: str, updates: Dict[str, Any]) -> Any:
        """Update a journey."""
        if journey_id in self.journeys:
            journey = self.journeys[journey_id]
            for key, value in updates.items():
                if hasattr(journey, key):
                    setattr(journey, key, value)
                else:
                    journey.journey_data[key] = value
            return journey
        return None
    
    async def get_journey_template(self, journey_type: JourneyType) -> Dict[str, Any]:
        """Get journey template."""
        return {
            "name": f"{journey_type.value} Journey",
            "steps": ["business_outcome_analysis", "data_requirement_assessment", "platform_routing"]
        }


class MockBusinessOutcomeLandingPageService:
    """Mock Business Outcome Landing Page Service."""
    
    def __init__(self):
        self.guide_agent = MockGuideAgent()
        self.journey_persistence = MockJourneyPersistenceService()
    
    async def render_landing_page(self, user_context: UserContext) -> Dict[str, Any]:
        """Render landing page."""
        return {
            "title": "What business outcome would you like to achieve?",
            "subtitle": "Tell our Guide Agent what you'd like to accomplish",
            "available_outcomes": [
                {"id": "data_analysis", "name": "Data Analysis & Insights"},
                {"id": "process_optimization", "name": "Process Optimization"},
                {"id": "strategic_planning", "name": "Strategic Planning"}
            ]
        }
    
    async def create_business_outcome_journey(self, user_context: UserContext, 
                                            business_outcome: str,
                                            journey_type: str = "mvp") -> Dict[str, Any]:
        """Create business outcome journey."""
        journey_context = await self.journey_persistence.create_journey(
            user_context=user_context,
            business_outcome=business_outcome,
            journey_type=JourneyType.MVP
        )
        
        return {
            "success": True,
            "journey_id": journey_context.journey_id,
            "business_outcome": business_outcome,
            "journey_type": journey_type,
            "status": "created",
            "current_step": "business_outcome_analysis",
            "guide_agent_prompt": f"I can help you with {business_outcome}. What would you like to accomplish?",
            "next_steps": ["data_requirement_assessment", "platform_routing"]
        }


class MockExperienceManagerService:
    """Mock Experience Manager Service."""
    
    def __init__(self):
        self.services = {}
    
    async def register_experience_service(self, service_name: str, service_instance: Any):
        """Register experience service."""
        self.services[service_name] = service_instance


class MockFrontendIntegrationService:
    """Mock Frontend Integration Service."""
    
    def __init__(self):
        self.components = {}


class MockJourneyManagerService:
    """Mock Journey Manager Service."""
    
    def __init__(self):
        self.journeys = {}


class MockJourneyOrchestratorService:
    """Mock Journey Orchestrator Service."""
    
    def __init__(self):
        self.orchestrations = {}


class MockGuideAgent:
    """Mock Guide Agent."""
    
    def __init__(self):
        self.conversations = {}
    
    async def initialize_journey_guidance(self, journey_context: Any, user_context: UserContext, 
                                        business_outcome: str):
        """Initialize journey guidance."""
        pass


class MockJourneyContext:
    """Mock Journey Context."""
    
    def __init__(self, journey_id: str, tenant_id: str, user_id: str, session_id: str,
                 journey_type: JourneyType, business_outcome: str, journey_data: Dict[str, Any]):
        self.journey_id = journey_id
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.session_id = session_id
        self.journey_type = journey_type
        self.business_outcome = business_outcome
        self.journey_data = journey_data
        self.status = JourneyStatus.CREATED
        self.current_step = "business_outcome_analysis"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


async def test_journey_persistence_service():
    """Test journey persistence service."""
    print("🧪 Testing Journey Persistence Service...")
    
    try:
        # Initialize service
        di_container = MockDIContainerService("test_service")
        public_works = MockPublicWorksFoundationService()
        journey_persistence = JourneyPersistenceService(di_container, public_works)
        
        # Test initialization
        await journey_persistence.initialize()
        print("✅ Journey Persistence Service initialized")
        
        # Test journey creation
        user_context = UserContext(
            tenant_id="test_tenant",
            user_id="test_user",
            session_id="test_session"
        )
        
        journey_context = await journey_persistence.create_journey(
            user_context=user_context,
            business_outcome="Data Analysis & Insights",
            journey_type=JourneyType.MVP
        )
        
        print(f"✅ Journey created: {journey_context.journey_id}")
        
        # Test journey retrieval
        retrieved_journey = await journey_persistence.get_journey(journey_context.journey_id)
        assert retrieved_journey is not None
        print("✅ Journey retrieval successful")
        
        # Test journey update
        updated_journey = await journey_persistence.update_journey(
            journey_context.journey_id,
            {"current_step": "data_requirement_assessment"}
        )
        assert updated_journey is not None
        print("✅ Journey update successful")
        
        # Test journey stats
        stats = await journey_persistence.get_journey_stats()
        assert stats["total_active_journeys"] > 0
        print("✅ Journey stats successful")
        
        print("🎉 Journey Persistence Service test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Journey Persistence Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_business_outcome_landing_page_service():
    """Test business outcome landing page service."""
    print("🧪 Testing Business Outcome Landing Page Service...")
    
    try:
        # Initialize service
        di_container = MockDIContainerService("test_service")
        landing_page_service = BusinessOutcomeLandingPageService(di_container)
        
        # Test initialization
        await landing_page_service.initialize()
        print("✅ Business Outcome Landing Page Service initialized")
        
        # Test landing page rendering
        user_context = UserContext(
            tenant_id="test_tenant",
            user_id="test_user",
            session_id="test_session"
        )
        
        landing_page_content = await landing_page_service.render_landing_page(user_context)
        assert landing_page_content is not None
        print("✅ Landing page rendering successful")
        
        # Test journey creation
        journey_response = await landing_page_service.create_business_outcome_journey(
            user_context=user_context,
            business_outcome="Data Analysis & Insights"
        )
        
        assert journey_response["success"] is True
        assert journey_response["journey_id"] is not None
        print("✅ Journey creation successful")
        
        print("🎉 Business Outcome Landing Page Service test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Business Outcome Landing Page Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_business_outcome_experience_service():
    """Test business outcome experience service."""
    print("🧪 Testing Business Outcome Experience Service...")
    
    try:
        # Initialize service
        di_container = MockDIContainerService("test_service")
        public_works = MockPublicWorksFoundationService()
        experience_service = BusinessOutcomeExperienceService(di_container, public_works)
        
        # Test initialization
        await experience_service.initialize()
        print("✅ Business Outcome Experience Service initialized")
        
        # Test landing page rendering
        user_context = UserContext(
            tenant_id="test_tenant",
            user_id="test_user",
            session_id="test_session"
        )
        
        landing_page_response = await experience_service.render_business_outcome_landing_page(user_context)
        assert landing_page_response["success"] is True
        print("✅ Landing page rendering successful")
        
        # Test journey creation
        journey_response = await experience_service.create_business_outcome_journey(
            user_context=user_context,
            business_outcome="Data Analysis & Insights"
        )
        
        assert journey_response["success"] is True
        assert journey_response["journey_id"] is not None
        print("✅ Journey creation successful")
        
        # Test Guide Agent experience
        guide_agent_response = await experience_service.start_guide_agent_experience(
            user_context=user_context,
            journey_id=journey_response["journey_id"]
        )
        
        assert guide_agent_response["success"] is True
        print("✅ Guide Agent experience successful")
        
        # Test pillar routing
        routing_response = await experience_service.handle_pillar_routing(
            user_context=user_context,
            pillar="content",
            journey_id=journey_response["journey_id"]
        )
        
        assert routing_response["success"] is True
        print("✅ Pillar routing successful")
        
        print("🎉 Business Outcome Experience Service test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Business Outcome Experience Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_complete_workflow():
    """Test complete journey management workflow."""
    print("🧪 Testing Complete Journey Management Workflow...")
    
    try:
        # Initialize all services
        di_container = MockDIContainerService("test_service")
        public_works = MockPublicWorksFoundationService()
        
        # Initialize journey persistence
        journey_persistence = JourneyPersistenceService(di_container, public_works)
        await journey_persistence.initialize()
        
        # Initialize business outcome landing page
        landing_page_service = BusinessOutcomeLandingPageService(di_container)
        await landing_page_service.initialize()
        
        # Initialize experience service
        experience_service = BusinessOutcomeExperienceService(di_container, public_works)
        await experience_service.initialize()
        
        print("✅ All services initialized")
        
        # Test complete workflow
        user_context = UserContext(
            tenant_id="test_tenant",
            user_id="test_user",
            session_id="test_session"
        )
        
        # Step 1: Render landing page
        landing_page_response = await experience_service.render_business_outcome_landing_page(user_context)
        assert landing_page_response["success"] is True
        print("✅ Step 1: Landing page rendered")
        
        # Step 2: Create journey
        journey_response = await experience_service.create_business_outcome_journey(
            user_context=user_context,
            business_outcome="Data Analysis & Insights"
        )
        assert journey_response["success"] is True
        print("✅ Step 2: Journey created")
        
        # Step 3: Start Guide Agent experience
        guide_agent_response = await experience_service.start_guide_agent_experience(
            user_context=user_context,
            journey_id=journey_response["journey_id"]
        )
        assert guide_agent_response["success"] is True
        print("✅ Step 3: Guide Agent experience started")
        
        # Step 4: Handle pillar routing
        routing_response = await experience_service.handle_pillar_routing(
            user_context=user_context,
            pillar="content",
            journey_id=journey_response["journey_id"]
        )
        assert routing_response["success"] is True
        print("✅ Step 4: Pillar routing completed")
        
        # Step 5: Verify journey persistence
        journey_context = await journey_persistence.get_journey(journey_response["journey_id"])
        assert journey_context is not None
        assert journey_context.business_outcome == "Data Analysis & Insights"
        print("✅ Step 5: Journey persistence verified")
        
        print("🎉 Complete Journey Management Workflow test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Complete Journey Management Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🚀 Testing Complete Journey Management Workflow")
    print("=" * 60)
    
    # Run individual service tests
    persistence_test = await test_journey_persistence_service()
    landing_page_test = await test_business_outcome_landing_page_service()
    experience_test = await test_business_outcome_experience_service()
    
    # Run complete workflow test
    workflow_test = await test_complete_workflow()
    
    print("\n" + "=" * 60)
    print("🎯 Test Results:")
    
    total_tests = 4
    passed_tests = 0
    
    if persistence_test:
        passed_tests += 1
        print("✅ Journey Persistence Service: PASSED")
    else:
        print("❌ Journey Persistence Service: FAILED")
    
    if landing_page_test:
        passed_tests += 1
        print("✅ Business Outcome Landing Page Service: PASSED")
    else:
        print("❌ Business Outcome Landing Page Service: FAILED")
    
    if experience_test:
        passed_tests += 1
        print("✅ Business Outcome Experience Service: PASSED")
    else:
        print("❌ Business Outcome Experience Service: FAILED")
    
    if workflow_test:
        passed_tests += 1
        print("✅ Complete Journey Management Workflow: PASSED")
    else:
        print("❌ Complete Journey Management Workflow: FAILED")
    
    print(f"\n🎯 Overall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Journey Management System is working correctly!")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    asyncio.run(main())
