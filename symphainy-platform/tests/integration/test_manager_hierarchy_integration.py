#!/usr/bin/env python3
"""
Manager Hierarchy Integration Tests

Tests for top-down manager flow, service registration, and MCP tool accessibility.

This test suite verifies:
1. Manager initialization and infrastructure connections
2. Top-down orchestration flow (Solution → Journey → Experience → Delivery)
3. Service registration with Curator
4. SOA API exposure
5. MCP Tool registration
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock


class MockDIContainer:
    """Mock DI Container for testing."""
    
    def __init__(self):
        self.services = {}
        self.foundation_services = {}
        self.utilities = {
            "logger": Mock(),
            "config": Mock(),
            "health": Mock(),
            "telemetry": Mock(),
            "security": Mock(),
            "authorization": Mock()
        }
    
    def register_service(self, service_name: str, service_instance: Any):
        """Register a service."""
        self.services[service_name] = service_instance
    
    def get_service(self, service_name: str):
        """Get a service."""
        return self.services.get(service_name)
    
    def get_foundation_service(self, service_name: str):
        """Get a foundation service."""
        return self.foundation_services.get(service_name)
    
    def register_foundation_service(self, service_name: str, service_instance: Any):
        """Register a foundation service."""
        self.foundation_services[service_name] = service_instance
    
    def get_utility(self, utility_name: str):
        """Get a utility."""
        return self.utilities.get(utility_name)
    
    def get_logger(self, name: str):
        """Get a logger."""
        return self.utilities["logger"]
    
    def get_abstraction(self, abstraction_name: str):
        """Get an abstraction."""
        return None


class MockCurator:
    """Mock Curator Foundation Service for testing."""
    
    def __init__(self):
        self.registered_services = {}
        self.service_capabilities = {}
    
    async def register_service(self, service: Any, capability: Dict[str, Any]):
        """Register a service with capabilities."""
        service_name = capability.get("service_name", service.service_name)
        self.registered_services[service_name] = service
        self.service_capabilities[service_name] = capability
    
    def is_service_registered(self, service_name: str) -> bool:
        """Check if a service is registered."""
        return service_name in self.registered_services
    
    def get_service_capabilities(self, service_name: str) -> Dict[str, Any]:
        """Get service capabilities."""
        return self.service_capabilities.get(service_name, {})


class MockPublicWorksFoundation:
    """Mock Public Works Foundation for testing."""
    
    def __init__(self):
        # Create mock abstractions
        self.abstractions = {
            "session": Mock(),
            "state_management": Mock(),
            "messaging": Mock(),
            "analytics": Mock(),
            "health": Mock(),
            "telemetry": Mock()
        }
    
    def get_session_abstraction(self):
        """Get session abstraction."""
        return self.abstractions["session"]
    
    def get_state_management_abstraction(self):
        """Get state management abstraction."""
        return self.abstractions["state_management"]
    
    def get_messaging_abstraction(self):
        """Get messaging abstraction."""
        return self.abstractions["messaging"]
    
    def get_analytics_abstraction(self):
        """Get analytics abstraction."""
        return self.abstractions["analytics"]
    
    def get_health_abstraction(self):
        """Get health abstraction."""
        return self.abstractions["health"]
    
    def get_telemetry_abstraction(self):
        """Get telemetry abstraction."""
        return self.abstractions["telemetry"]


@pytest.fixture
def mock_di_container():
    """Create a mock DI container."""
    container = MockDIContainer()
    
    # Register foundation services
    mock_public_works = MockPublicWorksFoundation()
    mock_curator = MockCurator()
    
    container.register_foundation_service("PublicWorksFoundationService", mock_public_works)
    container.register_foundation_service("CuratorFoundationService", mock_curator)
    
    return container


@pytest.mark.asyncio
async def test_manager_imports_available():
    """Test that all managers can be imported."""
    try:
        from solution.services.solution_manager.solution_manager_service import SolutionManagerService
        from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
        from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
        from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import DeliveryManagerService
        assert True, "All managers imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import managers: {e}")


@pytest.mark.asyncio
async def test_manager_initialization(mock_di_container):
    """Test that all managers initialize successfully."""
    from solution.services.solution_manager.solution_manager_service import SolutionManagerService
    from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
    from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
    from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    # Create managers
    delivery_manager = DeliveryManagerService(mock_di_container)
    experience_manager = ExperienceManagerService(mock_di_container)
    journey_manager = JourneyManagerService(mock_di_container)
    solution_manager = SolutionManagerService(mock_di_container)
    
    # Register managers with DI container
    mock_di_container.register_foundation_service("DeliveryManagerService", delivery_manager)
    mock_di_container.register_foundation_service("ExperienceManagerService", experience_manager)
    mock_di_container.register_foundation_service("JourneyManagerService", journey_manager)
    mock_di_container.register_foundation_service("SolutionManagerService", solution_manager)
    
    # Initialize managers
    delivery_result = await delivery_manager.initialize()
    experience_result = await experience_manager.initialize()
    journey_result = await journey_manager.initialize()
    solution_result = await solution_manager.initialize()
    
    assert delivery_result, "Delivery Manager should initialize successfully"
    assert experience_result, "Experience Manager should initialize successfully"
    assert journey_result, "Journey Manager should initialize successfully"
    assert solution_result, "Solution Manager should initialize successfully"
    
    # Verify initialization status
    assert delivery_manager.is_initialized, "Delivery Manager should be initialized"
    assert experience_manager.is_initialized, "Experience Manager should be initialized"
    assert journey_manager.is_initialized, "Journey Manager should be initialized"
    assert solution_manager.is_initialized, "Solution Manager should be initialized"


@pytest.mark.asyncio
async def test_manager_infrastructure_connections(mock_di_container):
    """Test that all managers have infrastructure connections."""
    from solution.services.solution_manager.solution_manager_service import SolutionManagerService
    from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
    from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
    from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    # Create and initialize managers
    delivery_manager = DeliveryManagerService(mock_di_container)
    experience_manager = ExperienceManagerService(mock_di_container)
    journey_manager = JourneyManagerService(mock_di_container)
    solution_manager = SolutionManagerService(mock_di_container)
    
    # Register managers
    mock_di_container.register_foundation_service("DeliveryManagerService", delivery_manager)
    mock_di_container.register_foundation_service("ExperienceManagerService", experience_manager)
    mock_di_container.register_foundation_service("JourneyManagerService", journey_manager)
    mock_di_container.register_foundation_service("SolutionManagerService", solution_manager)
    
    # Initialize
    await delivery_manager.initialize()
    await experience_manager.initialize()
    await journey_manager.initialize()
    await solution_manager.initialize()
    
    # Verify infrastructure connections
    assert delivery_manager.is_infrastructure_connected, "Delivery Manager should have infrastructure connected"
    assert experience_manager.is_infrastructure_connected, "Experience Manager should have infrastructure connected"
    assert journey_manager.is_infrastructure_connected, "Journey Manager should have infrastructure connected"
    assert solution_manager.is_infrastructure_connected, "Solution Manager should have infrastructure connected"


@pytest.mark.asyncio
async def test_top_down_flow_solution_to_journey(mock_di_container):
    """Test Solution Manager → Journey Manager flow."""
    from solution.services.solution_manager.solution_manager_service import SolutionManagerService
    from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
    
    # Create managers
    journey_manager = JourneyManagerService(mock_di_container)
    solution_manager = SolutionManagerService(mock_di_container)
    
    # Register managers
    mock_di_container.register_foundation_service("JourneyManagerService", journey_manager)
    mock_di_container.register_foundation_service("SolutionManagerService", solution_manager)
    
    # Initialize
    await journey_manager.initialize()
    await solution_manager.initialize()
    
    # Test orchestration
    journey_context = {"journey_type": "standard", "requirements": {}}
    result = await solution_manager.orchestrate_journey(journey_context)
    
    assert result["success"], "Solution Manager should successfully orchestrate journey"


@pytest.mark.asyncio
async def test_top_down_flow_journey_to_experience(mock_di_container):
    """Test Journey Manager → Experience Manager flow."""
    from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
    from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
    
    # Create managers
    experience_manager = ExperienceManagerService(mock_di_container)
    journey_manager = JourneyManagerService(mock_di_container)
    
    # Register managers
    mock_di_container.register_foundation_service("ExperienceManagerService", experience_manager)
    mock_di_container.register_foundation_service("JourneyManagerService", journey_manager)
    
    # Initialize
    await experience_manager.initialize()
    await journey_manager.initialize()
    
    # Test orchestration
    experience_context = {"experience_type": "web", "user_context": {}}
    result = await journey_manager.orchestrate_experience(experience_context)
    
    assert result["success"], "Journey Manager should successfully orchestrate experience"


@pytest.mark.asyncio
async def test_top_down_flow_experience_to_delivery(mock_di_container):
    """Test Experience Manager → Delivery Manager flow."""
    from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
    from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    # Create managers
    delivery_manager = DeliveryManagerService(mock_di_container)
    experience_manager = ExperienceManagerService(mock_di_container)
    
    # Register managers
    mock_di_container.register_foundation_service("DeliveryManagerService", delivery_manager)
    mock_di_container.register_foundation_service("ExperienceManagerService", experience_manager)
    
    # Initialize
    await delivery_manager.initialize()
    await experience_manager.initialize()
    
    # Test orchestration
    delivery_context = {"capability_type": "test", "context": {}}
    result = await experience_manager.orchestrate_delivery(delivery_context)
    
    assert result["success"], "Experience Manager should successfully orchestrate delivery"


@pytest.mark.asyncio
async def test_top_down_flow_delivery_to_business_enablement(mock_di_container):
    """Test Delivery Manager → Business Enablement orchestration."""
    from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    # Create manager
    delivery_manager = DeliveryManagerService(mock_di_container)
    
    # Register manager
    mock_di_container.register_foundation_service("DeliveryManagerService", delivery_manager)
    
    # Initialize
    await delivery_manager.initialize()
    
    # Test orchestration
    business_context = {"pillars": ["content", "insights", "operations", "business_outcomes"]}
    result = await delivery_manager.orchestrate_business_enablement(business_context)
    
    assert result["success"], "Delivery Manager should successfully orchestrate business enablement"


@pytest.mark.asyncio
async def test_soa_apis_exposed(mock_di_container):
    """Test that all managers expose SOA APIs."""
    from solution.services.solution_manager.solution_manager_service import SolutionManagerService
    from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
    from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
    from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    # Create and initialize managers
    delivery_manager = DeliveryManagerService(mock_di_container)
    experience_manager = ExperienceManagerService(mock_di_container)
    journey_manager = JourneyManagerService(mock_di_container)
    solution_manager = SolutionManagerService(mock_di_container)
    
    # Initialize
    await delivery_manager.initialize()
    await experience_manager.initialize()
    await journey_manager.initialize()
    await solution_manager.initialize()
    
    # Verify SOA APIs
    assert len(solution_manager.soa_apis) > 0, "Solution Manager should expose SOA APIs"
    assert len(journey_manager.soa_apis) > 0, "Journey Manager should expose SOA APIs"
    assert len(experience_manager.soa_apis) > 0, "Experience Manager should expose SOA APIs"
    assert len(delivery_manager.soa_apis) > 0, "Delivery Manager should expose SOA APIs"


@pytest.mark.asyncio
async def test_mcp_tools_registered(mock_di_container):
    """Test that all managers have MCP tools registered."""
    from solution.services.solution_manager.solution_manager_service import SolutionManagerService
    from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
    from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
    from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    # Create and initialize managers
    delivery_manager = DeliveryManagerService(mock_di_container)
    experience_manager = ExperienceManagerService(mock_di_container)
    journey_manager = JourneyManagerService(mock_di_container)
    solution_manager = SolutionManagerService(mock_di_container)
    
    # Initialize
    await delivery_manager.initialize()
    await experience_manager.initialize()
    await journey_manager.initialize()
    await solution_manager.initialize()
    
    # Verify MCP Tools
    assert len(solution_manager.mcp_tools) > 0, "Solution Manager should have MCP tools"
    assert len(journey_manager.mcp_tools) > 0, "Journey Manager should have MCP tools"
    assert len(experience_manager.mcp_tools) > 0, "Experience Manager should have MCP tools"
    assert len(delivery_manager.mcp_tools) > 0, "Delivery Manager should have MCP tools"


@pytest.mark.asyncio
async def test_curator_service_registration(mock_di_container):
    """Test that all managers are registered with Curator."""
    from solution.services.solution_manager.solution_manager_service import SolutionManagerService
    from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
    from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
    from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    # Create and initialize managers
    delivery_manager = DeliveryManagerService(mock_di_container)
    experience_manager = ExperienceManagerService(mock_di_container)
    journey_manager = JourneyManagerService(mock_di_container)
    solution_manager = SolutionManagerService(mock_di_container)
    
    # Initialize (which should register with Curator)
    await delivery_manager.initialize()
    await experience_manager.initialize()
    await journey_manager.initialize()
    await solution_manager.initialize()
    
    # Get Curator and verify registration
    curator = mock_di_container.get_foundation_service("CuratorFoundationService")
    
    assert curator.is_service_registered("SolutionManagerService"), "Solution Manager should be registered"
    assert curator.is_service_registered("JourneyManagerService"), "Journey Manager should be registered"
    assert curator.is_service_registered("ExperienceManagerService"), "Experience Manager should be registered"
    assert curator.is_service_registered("DeliveryManagerService"), "Delivery Manager should be registered"


@pytest.mark.asyncio
async def test_manager_health_checks(mock_di_container):
    """Test that all managers have health checks."""
    from solution.services.solution_manager.solution_manager_service import SolutionManagerService
    from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
    from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
    from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    # Create and initialize managers
    delivery_manager = DeliveryManagerService(mock_di_container)
    experience_manager = ExperienceManagerService(mock_di_container)
    journey_manager = JourneyManagerService(mock_di_container)
    solution_manager = SolutionManagerService(mock_di_container)
    
    # Initialize
    await delivery_manager.initialize()
    await experience_manager.initialize()
    await journey_manager.initialize()
    await solution_manager.initialize()
    
    # Check health
    solution_health = await solution_manager.health_check()
    journey_health = await journey_manager.health_check()
    experience_health = await experience_manager.health_check()
    delivery_health = await delivery_manager.health_check()
    
    assert solution_health["status"] == "healthy", "Solution Manager should be healthy"
    assert journey_health["status"] == "healthy", "Journey Manager should be healthy"
    assert experience_health["status"] == "healthy", "Experience Manager should be healthy"
    assert delivery_health["status"] == "healthy", "Delivery Manager should be healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
