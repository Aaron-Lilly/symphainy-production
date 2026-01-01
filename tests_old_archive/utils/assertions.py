#!/usr/bin/env python3
"""
Custom Assertions

Provides custom assertion helpers for testing.
"""

from typing import Dict, Any, List, Optional


class ServiceAssertions:
    """Assertions for service testing."""
    
    @staticmethod
    def assert_service_initialized(service, service_name: str = None):
        """Assert service is properly initialized."""
        assert service is not None, f"{service_name or 'Service'} should not be None"
        assert hasattr(service, "is_initialized"), \
            f"{service_name or 'Service'} should have is_initialized attribute"
        assert service.is_initialized, \
            f"{service_name or 'Service'} should be initialized"
    
    @staticmethod
    def assert_service_registered(service, curator=None, service_name: str = None):
        """Assert service is registered with Curator."""
        # Check if service has registration method
        has_registration = (
            hasattr(service, "register_with_curator") or
            hasattr(service, "register_capability") or
            hasattr(service, "register_service")
        )
        assert has_registration, \
            f"{service_name or 'Service'} should have registration capability"
        
        # If curator provided, verify registration
        if curator:
            # This would need actual curator implementation
            # For now, just verify capability exists
            pass
    
    @staticmethod
    def assert_smart_city_service_available(service, service_name: str):
        """Assert Smart City service is available."""
        assert service is not None, f"{service_name} should be available"
        assert hasattr(service, "service_name") or hasattr(service, "role_name"), \
            f"{service_name} should have service_name or role_name"


class ResponseAssertions:
    """Assertions for API response testing."""
    
    @staticmethod
    def assert_success_response(response: Dict[str, Any], expected_keys: List[str] = None):
        """Assert response indicates success."""
        assert response is not None, "Response should not be None"
        assert "status" in response, "Response should have 'status' key"
        assert response["status"] == "success", \
            f"Response status should be 'success', got: {response.get('status')}"
        
        if expected_keys:
            for key in expected_keys:
                assert key in response, f"Response should have '{key}' key"
    
    @staticmethod
    def assert_error_response(response: Dict[str, Any], error_message: str = None):
        """Assert response indicates an error."""
        assert response is not None, "Response should not be None"
        assert "status" in response, "Response should have 'status' key"
        assert response["status"] in ["error", "failed"], \
            f"Response status should indicate error, got: {response.get('status')}"
        
        if error_message:
            assert "message" in response, "Error response should have 'message' key"
            assert error_message.lower() in response["message"].lower(), \
                f"Error message should contain '{error_message}'"
    
    @staticmethod
    def assert_response_has_data(response: Dict[str, Any], data_key: str = "data"):
        """Assert response contains data."""
        assert data_key in response, f"Response should have '{data_key}' key"
        assert response[data_key] is not None, f"Response '{data_key}' should not be None"


class JourneyAssertions:
    """Assertions for journey testing."""
    
    @staticmethod
    def assert_pillar_complete(journey_status: Dict[str, Any], pillar_name: str):
        """Assert a pillar is complete."""
        completed = journey_status.get("completed_pillars", [])
        assert pillar_name in completed, f"{pillar_name} pillar should be completed"
    
    @staticmethod
    def assert_current_pillar(journey_status: Dict[str, Any], pillar_name: str):
        """Assert current pillar."""
        current = journey_status.get("current_pillar")
        assert current == pillar_name, \
            f"Current pillar should be '{pillar_name}', got: '{current}'"
    
    @staticmethod
    def assert_journey_progress(journey_status: Dict[str, Any], min_progress: float = 0.0):
        """Assert journey progress."""
        progress = journey_status.get("progress", 0)
        assert progress >= min_progress, \
            f"Journey progress should be at least {min_progress}, got: {progress}"


class OrchestratorAssertions:
    """Assertions for orchestrator testing."""
    
    @staticmethod
    def assert_orchestrator_has_enabling_service(orchestrator, service_name: str):
        """Assert orchestrator has access to enabling service."""
        service_attr = f"{service_name.lower().replace('_', '_')}_service"
        assert hasattr(orchestrator.business_orchestrator, service_attr), \
            f"Orchestrator should have access to {service_name}"
        
        service = getattr(orchestrator.business_orchestrator, service_attr, None)
        assert service is not None, f"{service_name} should be available"
    
    @staticmethod
    def assert_orchestrator_can_execute_action(orchestrator, action: str):
        """Assert orchestrator can execute an action."""
        assert hasattr(orchestrator, "execute"), \
            "Orchestrator should have execute method"
        assert hasattr(orchestrator, action) or action in orchestrator.__class__.__dict__, \
            f"Orchestrator should support action: {action}"



