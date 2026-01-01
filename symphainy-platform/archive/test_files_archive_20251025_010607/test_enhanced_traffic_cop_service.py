#!/usr/bin/env python3
"""
Test Enhanced Traffic Cop Service

Comprehensive tests for the enhanced Traffic Cop service with advanced session management,
cross-dimensional capabilities, state management, and agent orchestration.
"""

import asyncio
import sys
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

# Import the enhanced Traffic Cop service classes directly
from services.traffic_cop.traffic_cop_service_enhanced import (
    TrafficCopService, StateScope, StatePriority, SessionStatus,
    CrossDimensionalSessionRequest, CrossDimensionalSessionResponse,
    SessionHealthMetrics
)
from interfaces import (
    SessionInitiationRequest, SessionInitiationResponse, SessionValidationResult
)
from utilities import UserContext


class MockPublicWorksFoundationService:
    """Mock Public Works Foundation Service for testing."""
    
    def __init__(self):
        self.utility_foundation = Mock()
        self.smart_city_abstractions = {}
        self._setup_mock_abstractions()
    
    def _setup_mock_abstractions(self):
        """Set up mock abstractions."""
        # Mock session initiation abstraction
        self.session_initiation_abstraction = Mock()
        self.session_initiation_abstraction.initiate_session = AsyncMock(return_value={
            "session_id": "test_session_123",
            "user_id": "test_user",
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        })
        self.session_initiation_abstraction.validate_session = AsyncMock(return_value={
            "valid": True,
            "user_id": "test_user",
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "metadata": {}
        })
        self.session_initiation_abstraction.terminate_session = AsyncMock(return_value={
            "status": "success",
            "message": "Session terminated"
        })
        self.session_initiation_abstraction.refresh_session = AsyncMock(return_value={
            "session_id": "test_session_123",
            "session_data": {"refreshed": True}
        })
        
        # Mock other abstractions
        self.authentication_abstraction = Mock()
        self.file_lifecycle_abstraction = Mock()
        self.health_monitoring_abstraction = Mock()
        self.health_monitoring_abstraction.record_metric = AsyncMock()
        self.orchestration_abstraction = Mock()
        
        # Mock advanced abstractions
        self.advanced_session_management_abstraction = Mock()
        self.advanced_session_management_abstraction.manage_cross_dimensional_sessions = AsyncMock(return_value={
            "session_id": "cross_dim_session_123",
            "dimensions": ["smart_city", "business"],
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "metadata": {}
        })
        self.advanced_session_management_abstraction.coordinate_agentic_sessions = AsyncMock(return_value={
            "coordination_id": "coord_123",
            "agentic_systems": ["agent1", "agent2"],
            "session_context": {"session_id": "test_session_123"},
            "status": "coordinated",
            "created_at": datetime.utcnow().isoformat()
        })
        
        self.advanced_state_management_abstraction = Mock()
        self.advanced_state_management_abstraction.manage_state = AsyncMock(return_value={
            "status": "success",
            "state_entry": {
                "key": "test_key",
                "value": "test_value",
                "scope": "local",
                "priority": 2,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": {"session_id": "test_session_123"}
            }
        })
    
    async def get_smart_city_abstractions(self, role: str) -> Dict[str, Any]:
        """Get Smart City abstractions for a role."""
        return {
            "session_initiation": {"abstraction": self.session_initiation_abstraction},
            "authentication": {"abstraction": self.authentication_abstraction},
            "file_lifecycle": {"abstraction": self.file_lifecycle_abstraction},
            "health_monitoring": {"abstraction": self.health_monitoring_abstraction},
            "orchestration": {"abstraction": self.orchestration_abstraction},
            "advanced_session_management": {"abstraction": self.advanced_session_management_abstraction},
            "advanced_state_management": {"abstraction": self.advanced_state_management_abstraction}
        }


class MockCuratorFoundationService:
    """Mock Curator Foundation Service for testing."""
    
    def __init__(self):
        self.capabilities = {}
    
    async def register_capability(self, service_name: str, capability: Dict[str, Any]) -> Dict[str, Any]:
        """Register a service capability."""
        self.capabilities[service_name] = capability
        return {"success": True, "message": f"Capability registered for {service_name}"}


async def test_enhanced_traffic_cop_initialization():
    """Test enhanced Traffic Cop service initialization."""
    print("🧪 Testing Enhanced Traffic Cop Service Initialization...")
    
    # Create mock services
    mock_public_works = MockPublicWorksFoundationService()
    mock_curator = MockCuratorFoundationService()
    
    # Create Traffic Cop service
    traffic_cop = TrafficCopService(mock_public_works, mock_curator)
    
    # Initialize service
    await traffic_cop.initialize()
    
    # Verify initialization
    assert traffic_cop.initialized, "Service should be initialized"
    assert traffic_cop.session_initiation_abstraction is not None, "Session initiation abstraction should be set"
    assert traffic_cop.advanced_session_management_abstraction is not None, "Advanced session management abstraction should be set"
    assert traffic_cop.advanced_state_management_abstraction is not None, "Advanced state management abstraction should be set"
    
    # Verify state machines are initialized
    assert "smart_city" in traffic_cop.session_state_machines, "Smart City state machine should be initialized"
    assert "business" in traffic_cop.session_state_machines, "Business state machine should be initialized"
    assert "agentic" in traffic_cop.session_state_machines, "Agentic state machine should be initialized"
    assert "experience" in traffic_cop.session_state_machines, "Experience state machine should be initialized"
    
    print("✅ Enhanced Traffic Cop Service initialization test passed!")


async def test_cross_dimensional_session_management():
    """Test cross-dimensional session management capabilities."""
    print("🧪 Testing Cross-Dimensional Session Management...")
    
    # Create mock services
    mock_public_works = MockPublicWorksFoundationService()
    mock_curator = MockCuratorFoundationService()
    
    # Create Traffic Cop service
    traffic_cop = TrafficCopService(mock_public_works, mock_curator)
    await traffic_cop.initialize()
    
    # Test cross-dimensional session creation
    request = CrossDimensionalSessionRequest(
        dimensions=["smart_city", "business", "agentic"],
        metadata={"test": "data"},
        user_id="test_user"
    )
    
    response = await traffic_cop.initiate_cross_dimensional_session(request)
    
    # Verify response
    assert response.session_id is not None, "Session ID should be generated"
    assert "smart_city" in response.dimensions, "Smart City dimension should be included"
    assert "business" in response.dimensions, "Business dimension should be included"
    assert "agentic" in response.dimensions, "Agentic dimension should be included"
    assert response.status == "created", "Session should be created"
    
    # Verify session is stored
    assert response.session_id in traffic_cop.cross_dimensional_sessions, "Session should be stored"
    
    # Verify state machines are updated
    for dimension in response.dimensions:
        if dimension in traffic_cop.session_state_machines:
            assert traffic_cop.session_state_machines[dimension]["current_state"] == "active", f"{dimension} state machine should be active"
    
    print("✅ Cross-dimensional session management test passed!")


async def test_advanced_state_management():
    """Test advanced state management capabilities."""
    print("🧪 Testing Advanced State Management...")
    
    # Create mock services
    mock_public_works = MockPublicWorksFoundationService()
    mock_curator = MockCuratorFoundationService()
    
    # Create Traffic Cop service
    traffic_cop = TrafficCopService(mock_public_works, mock_curator)
    await traffic_cop.initialize()
    
    # Test state management
    session_id = "test_session_123"
    state_key = "test_state"
    state_value = {"data": "test"}
    scope = StateScope.LOCAL
    priority = StatePriority.HIGH
    
    result = await traffic_cop.manage_session_state(
        session_id, state_key, state_value, scope, priority
    )
    
    # Verify result
    assert result["status"] == "success", "State management should succeed"
    assert "state_entry" in result, "State entry should be returned"
    
    # Verify health metrics are updated
    assert session_id in traffic_cop.session_health_metrics, "Health metrics should be tracked"
    assert traffic_cop.session_health_metrics[session_id].activity_count > 0, "Activity count should be incremented"
    
    print("✅ Advanced state management test passed!")


async def test_agent_orchestration_coordination():
    """Test agent orchestration coordination capabilities."""
    print("🧪 Testing Agent Orchestration Coordination...")
    
    # Create mock services
    mock_public_works = MockPublicWorksFoundationService()
    mock_curator = MockCuratorFoundationService()
    
    # Create Traffic Cop service
    traffic_cop = TrafficCopService(mock_public_works, mock_curator)
    await traffic_cop.initialize()
    
    # Test agent coordination
    agent_hierarchy = ["master_agent", "worker_agent_1", "worker_agent_2"]
    session_context = {
        "session_id": "test_session_123",
        "workflow_type": "data_processing",
        "priority": "high"
    }
    
    result = await traffic_cop.coordinate_agentic_session(agent_hierarchy, session_context)
    
    # Verify result
    assert "coordination_id" in result, "Coordination ID should be generated"
    assert result["agentic_systems"] == agent_hierarchy, "Agent hierarchy should be preserved"
    assert result["session_context"] == session_context, "Session context should be preserved"
    assert result["status"] == "coordinated", "Coordination should succeed"
    
    # Verify coordination is stored
    assert result["coordination_id"] in traffic_cop.agent_coordination_sessions, "Coordination should be stored"
    
    print("✅ Agent orchestration coordination test passed!")


async def test_session_health_metrics():
    """Test session health metrics capabilities."""
    print("🧪 Testing Session Health Metrics...")
    
    # Create mock services
    mock_public_works = MockPublicWorksFoundationService()
    mock_curator = MockCuratorFoundationService()
    
    # Create Traffic Cop service
    traffic_cop = TrafficCopService(mock_public_works, mock_curator)
    await traffic_cop.initialize()
    
    # Create a test session
    session_id = "test_session_123"
    traffic_cop.session_health_metrics[session_id] = SessionHealthMetrics(
        session_id=session_id,
        response_time=0.5,
        error_count=2,
        activity_count=10,
        last_activity=datetime.utcnow(),
        health_status="healthy"
    )
    
    # Add cross-dimensional session
    traffic_cop.cross_dimensional_sessions[session_id] = {
        "session_id": session_id,
        "dimensions": ["smart_city", "business"],
        "status": "active"
    }
    
    # Add agent coordination
    traffic_cop.agent_coordination_sessions["coord_123"] = {
        "coordination_id": "coord_123",
        "session_context": {"session_id": session_id},
        "status": "coordinated"
    }
    
    # Test health metrics retrieval
    result = await traffic_cop.get_session_health_metrics(session_id)
    
    # Verify result
    assert result["status"] == "success", "Health metrics request should succeed"
    assert "health_metrics" in result, "Health metrics should be returned"
    
    health_metrics = result["health_metrics"]
    assert health_metrics["session_id"] == session_id, "Session ID should match"
    assert health_metrics["response_time"] == 0.5, "Response time should be correct"
    assert health_metrics["error_count"] == 2, "Error count should be correct"
    assert health_metrics["activity_count"] == 10, "Activity count should be correct"
    assert health_metrics["health_status"] == "healthy", "Health status should be correct"
    assert health_metrics["cross_dimensional"] == True, "Should be cross-dimensional"
    assert "smart_city" in health_metrics["dimensions"], "Should include Smart City dimension"
    assert "business" in health_metrics["dimensions"], "Should include Business dimension"
    assert health_metrics["agent_coordination"] == True, "Should have agent coordination"
    assert health_metrics["coordination_count"] == 1, "Should have one coordination"
    
    print("✅ Session health metrics test passed!")


async def test_core_session_management():
    """Test core session management interface implementation."""
    print("🧪 Testing Core Session Management Interface...")
    
    # Create mock services
    mock_public_works = MockPublicWorksFoundationService()
    mock_curator = MockCuratorFoundationService()
    
    # Create Traffic Cop service
    traffic_cop = TrafficCopService(mock_public_works, mock_curator)
    await traffic_cop.initialize()
    
    # Test session initiation
    request = SessionInitiationRequest(
        user_id="test_user",
        session_metadata={"test": "data", "cross_dimensional": True},
        session_timeout=7200
    )
    
    response = await traffic_cop.initiate_session(request)
    
    # Verify response
    assert response.status == "success", "Session initiation should succeed"
    assert response.session_id is not None, "Session ID should be generated"
    assert response.session_data is not None, "Session data should be returned"
    assert "advanced capabilities" in response.message, "Should mention advanced capabilities"
    
    # Test session validation
    validation_result = await traffic_cop.validate_session(response.session_id)
    
    # Verify validation
    assert validation_result.valid == True, "Session should be valid"
    assert validation_result.session_id == response.session_id, "Session ID should match"
    assert validation_result.user_id == "test_user", "User ID should match"
    
    # Test session refresh
    refresh_response = await traffic_cop.refresh_session(response.session_id)
    
    # Verify refresh
    assert refresh_response.status == "success", "Session refresh should succeed"
    assert refresh_response.session_id == response.session_id, "Session ID should match"
    assert "advanced state management" in refresh_response.message, "Should mention advanced state management"
    
    # Test session termination
    termination_result = await traffic_cop.terminate_session(response.session_id)
    
    # Verify termination
    assert termination_result["status"] == "success", "Session termination should succeed"
    assert termination_result["session_id"] == response.session_id, "Session ID should match"
    assert "comprehensive cleanup" in termination_result["message"], "Should mention comprehensive cleanup"
    
    print("✅ Core session management interface test passed!")


async def test_service_info():
    """Test service information capabilities."""
    print("🧪 Testing Service Information...")
    
    # Create mock services
    mock_public_works = MockPublicWorksFoundationService()
    mock_curator = MockCuratorFoundationService()
    
    # Create Traffic Cop service
    traffic_cop = TrafficCopService(mock_public_works, mock_curator)
    await traffic_cop.initialize()
    
    # Test service info
    service_info = await traffic_cop.get_service_info()
    
    # Verify service info
    assert service_info["service_name"] == "traffic_cop", "Service name should be correct"
    assert service_info["version"] == "2.0.0", "Version should be correct"
    assert "Advanced session management" in service_info["description"], "Description should mention advanced capabilities"
    assert "Cross-dimensional session management" in service_info["capabilities"], "Should include cross-dimensional capabilities"
    assert "Advanced state management" in service_info["capabilities"], "Should include state management capabilities"
    assert "Agent orchestration integration" in service_info["capabilities"], "Should include agent orchestration"
    assert "/sessions/cross-dimensional/initiate" in service_info["endpoints"], "Should include cross-dimensional endpoints"
    assert "/sessions/state/manage" in service_info["endpoints"], "Should include state management endpoints"
    assert "/sessions/agentic/coordinate" in service_info["endpoints"], "Should include agent coordination endpoints"
    assert "/sessions/health/metrics" in service_info["endpoints"], "Should include health metrics endpoints"
    assert service_info["status"] == "operational", "Service should be operational"
    
    print("✅ Service information test passed!")


async def run_all_tests():
    """Run all enhanced Traffic Cop service tests."""
    print("🚀 Starting Enhanced Traffic Cop Service Tests...")
    print("=" * 60)
    
    try:
        await test_enhanced_traffic_cop_initialization()
        await test_cross_dimensional_session_management()
        await test_advanced_state_management()
        await test_agent_orchestration_coordination()
        await test_session_health_metrics()
        await test_core_session_management()
        await test_service_info()
        
        print("=" * 60)
        print("🎉 ALL ENHANCED TRAFFIC COP SERVICE TESTS PASSED!")
        print("✅ The enhanced Traffic Cop service is ready for production!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
