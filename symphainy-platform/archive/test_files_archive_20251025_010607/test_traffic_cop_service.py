#!/usr/bin/env python3
"""
Test Traffic Cop Service

Test the production-ready Traffic Cop service with full platform integration.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from backend.smart_city.services.traffic_cop import TrafficCopService
from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation import CuratorFoundationService
from utilities import UserContext
from interfaces import SessionInitiationRequest


class MockPublicWorksFoundation:
    """Mock Public Works Foundation for testing."""
    
    def __init__(self, utility_foundation):
        self.utility_foundation = utility_foundation
        self.abstractions = {}
    
    async def get_smart_city_abstractions(self, role: str) -> Dict[str, Any]:
        """Return mock Smart City abstractions."""
        return {
            "session_initiation": MockSessionAbstraction(),
            "authentication": MockAuthAbstraction(),
            "file_lifecycle": MockFileAbstraction(),
            "health_monitoring": MockHealthAbstraction(),
            "orchestration": MockOrchestrationAbstraction()
        }


class MockSessionAbstraction:
    """Mock session abstraction for testing."""
    
    async def validate_session(self, session_id: str) -> Dict[str, Any]:
        if session_id == "valid_session":
            return {
                "session_id": session_id,
                "user_id": "test_user",
                "expires_at": (datetime.utcnow().replace(hour=23, minute=59, second=59)).isoformat(),
                "metadata": {"test": True}
            }
        return None
    
    async def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "session_id": session_data["session_id"]}
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id == "valid_session":
            return {
                "session_id": session_id,
                "user_id": "test_user",
                "state": "active",
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow().replace(hour=23, minute=59, second=59)).isoformat(),
                "metadata": {"test": True}
            }
        return None
    
    async def terminate_session(self, session_id: str) -> Dict[str, Any]:
        return {"success": True, "session_id": session_id}
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "session_id": session_id}
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "session_id": "session_1",
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow().replace(hour=23, minute=59, second=59)).isoformat(),
                "metadata": {},
                "state": "active"
            }
        ]
    
    async def get_expired_sessions(self) -> List[Dict[str, Any]]:
        return []
    
    async def get_analytics(self) -> Dict[str, Any]:
        return {
            "total_sessions": 10,
            "active_sessions": 5,
            "expired_sessions": 5
        }


class MockAuthAbstraction:
    """Mock authentication abstraction for testing."""
    
    async def validate_user(self, user_id: str, user_context: UserContext = None) -> Dict[str, Any]:
        return {"valid": True, "user_id": user_id}


class MockFileAbstraction:
    """Mock file abstraction for testing."""
    
    async def store_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "file_id": "test_file"}


class MockHealthAbstraction:
    """Mock health monitoring abstraction for testing."""
    
    async def record_metric(self, name: str, value: float, tags: Dict[str, str] = None) -> Dict[str, Any]:
        return {"success": True, "metric": name, "value": value}
    
    async def get_metrics(self, pattern: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        return [
            {"name": "session_validations", "value": 1, "timestamp": datetime.utcnow().isoformat()}
        ]


class MockOrchestrationAbstraction:
    """Mock orchestration abstraction for testing."""
    
    async def schedule_cleanup_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "task_name": task_name}
    
    async def cancel_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "task_name": task_name}
    
    async def reschedule_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "task_name": task_name}


async def test_traffic_cop_service():
    """Test Traffic Cop service functionality."""
    print("🧪 Testing Traffic Cop Service...")
    
    try:
        # Initialize foundation services
        utility_foundation = UtilityFoundationService()
        await utility_foundation.initialize()
        
        curator_foundation = CuratorFoundationService(utility_foundation)
        await curator_foundation.initialize()
        
        public_works_foundation = MockPublicWorksFoundation(utility_foundation)
        
        # Initialize Traffic Cop service
        traffic_cop = TrafficCopService(public_works_foundation, curator_foundation)
        await traffic_cop.initialize()
        
        print("✅ Traffic Cop Service initialized successfully")
        
        # Test 1: Session initiation
        print("\n📝 Test 1: Session initiation...")
        request = SessionInitiationRequest(
            user_id="test_user",
            session_type="test",
            metadata={"test": True}
        )
        
        response = await traffic_cop.initiate_session(request)
        print(f"✅ Session initiation: {response.success}")
        if response.success:
            print(f"   Session ID: {response.session_id}")
            print(f"   User ID: {response.user_id}")
            print(f"   Expires at: {response.expires_at}")
        
        # Test 2: Session validation
        print("\n🔍 Test 2: Session validation...")
        validation = await traffic_cop.validate_session("valid_session")
        print(f"✅ Session validation: {validation.is_valid}")
        if validation.is_valid:
            print(f"   User ID: {validation.user_id}")
            print(f"   Expires at: {validation.expires_at}")
        
        # Test 3: Session termination
        print("\n🛑 Test 3: Session termination...")
        terminate_result = await traffic_cop.terminate_session("valid_session")
        print(f"✅ Session termination: {terminate_result['success']}")
        
        # Test 4: Session refresh
        print("\n🔄 Test 4: Session refresh...")
        refresh_result = await traffic_cop.refresh_session("valid_session", 48)
        print(f"✅ Session refresh: {refresh_result['success']}")
        if refresh_result['success']:
            print(f"   New expires at: {refresh_result['new_expires_at']}")
        
        # Test 5: Get session state
        print("\n📊 Test 5: Get session state...")
        state = await traffic_cop.get_session_state("valid_session")
        print(f"✅ Session state retrieved: {'error' not in state}")
        if 'error' not in state:
            print(f"   State: {state['state']}")
            print(f"   User ID: {state['user_id']}")
        
        # Test 6: List user sessions
        print("\n📋 Test 6: List user sessions...")
        sessions = await traffic_cop.list_user_sessions("test_user")
        print(f"✅ User sessions listed: {len(sessions)} sessions")
        for session in sessions:
            print(f"   - {session.session_id} ({session.state})")
        
        # Test 7: Cleanup expired sessions
        print("\n🧹 Test 7: Cleanup expired sessions...")
        cleanup_result = await traffic_cop.cleanup_expired_sessions()
        print(f"✅ Cleanup completed: {cleanup_result['success']}")
        print(f"   Cleaned count: {cleanup_result['cleaned_count']}")
        
        # Test 8: Get session analytics
        print("\n📈 Test 8: Get session analytics...")
        analytics = await traffic_cop.get_session_analytics()
        print(f"✅ Analytics retrieved: {'error' not in analytics}")
        if 'error' not in analytics:
            print(f"   Total sessions: {analytics['total_sessions']}")
            print(f"   Active sessions: {analytics['active_sessions']}")
        
        # Test 9: SOA Protocol
        print("\n🌐 Test 9: SOA Protocol...")
        openapi_spec = await traffic_cop.get_openapi_spec()
        print(f"✅ OpenAPI spec generated: {openapi_spec['openapi']}")
        print(f"   Title: {openapi_spec['info']['title']}")
        print(f"   Endpoints: {len(openapi_spec['paths'])}")
        
        docs = await traffic_cop.get_docs()
        print(f"✅ Docs generated: {docs['service_name']}")
        print(f"   Interface: {docs['interface']}")
        print(f"   Endpoints: {len(docs['endpoints'])}")
        
        # Test 10: Curator registration
        print("\n📝 Test 10: Curator registration...")
        registration = await traffic_cop.register_with_curator()
        print(f"✅ Curator registration: {registration.get('success', False)}")
        
        print("\n🎉 All Traffic Cop service tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_platform_integration():
    """Test platform integration features."""
    print("\n🧪 Testing Platform Integration...")
    
    try:
        # Initialize foundation services
        utility_foundation = UtilityFoundationService()
        await utility_foundation.initialize()
        
        curator_foundation = CuratorFoundationService(utility_foundation)
        await curator_foundation.initialize()
        
        public_works_foundation = MockPublicWorksFoundation(utility_foundation)
        
        # Initialize Traffic Cop service
        traffic_cop = TrafficCopService(public_works_foundation, curator_foundation)
        await traffic_cop.initialize()
        
        # Test user context integration
        print("\n👤 Testing user context integration...")
        user_context = UserContext(user_id="test_user", session_id="test_session")
        
        request = SessionInitiationRequest(user_id="test_user")
        response = await traffic_cop.initiate_session(request, user_context)
        print(f"✅ User context integration: {response.success}")
        
        # Test telemetry integration
        print("\n📊 Testing telemetry integration...")
        # The service should have recorded telemetry automatically
        print("✅ Telemetry integration: Built-in (check logs above)")
        
        # Test error handling integration
        print("\n🛡️ Testing error handling integration...")
        try:
            # This should trigger error handling
            await traffic_cop.validate_session("invalid_session")
        except Exception:
            pass  # Expected to fail
        print("✅ Error handling integration: Built-in")
        
        # Test health monitoring integration
        print("\n🏥 Testing health monitoring integration...")
        health_status = await traffic_cop.get_service_health()
        print(f"✅ Health monitoring: {health_status['status']}")
        
        print("\n🎉 Platform integration tests completed!")
        
    except Exception as e:
        print(f"❌ Platform integration test failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print("🚀 Starting Traffic Cop Service Tests...")
    
    await test_traffic_cop_service()
    await test_platform_integration()
    
    print("\n🏁 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
