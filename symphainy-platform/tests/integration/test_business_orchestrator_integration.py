#!/usr/bin/env python3
"""
Integration Test for Business Orchestrator with MVP Orchestrators

Tests that Business Orchestrator can discover and initialize orchestrators,
and that orchestrators can access enabling services.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any

# Import Business Orchestrator
from backend.business_enablement.business_orchestrator.business_orchestrator_service import BusinessOrchestratorService


class MockDIContainer:
    """Mock DI Container for testing."""
    
    def __init__(self):
        self.services = {}
        self.foundation_services = {}
        self.utilities = {}
        self.abstractions = {}
    
    def get_service(self, name: str):
        return self.services.get(name)
    
    def get_foundation_service(self, name: str):
        return self.foundation_services.get(name)
    
    def get_abstraction(self, name: str):
        if name not in self.abstractions:
            self.abstractions[name] = Mock()
        return self.abstractions.get(name)
    
    def get_utility(self, name: str):
        if name not in self.utilities:
            self.utilities[name] = Mock()
        return self.utilities.get(name)


class MockPlatformGateway:
    """Mock Platform Gateway for testing."""
    
    def get_abstraction(self, name: str):
        return Mock()
    
    def validate_access(self, realm_name: str, abstraction_name: str):
        return True


class MockCurator:
    """Mock Curator for Smart City service discovery."""
    
    def __init__(self):
        self.registered_services = {}
    
    async def get_registered_services(self):
        return {
            "services": {
                "Librarian": {
                    "realm": "smart_city",
                    "service_type": "smart_city_service",
                    "service_instance": Mock()
                },
                "DataSteward": {
                    "realm": "smart_city",
                    "service_type": "smart_city_service",
                    "service_instance": Mock()
                },
                "Conductor": {
                    "realm": "smart_city",
                    "service_type": "smart_city_service",
                    "service_instance": Mock()
                }
            }
        }
    
    async def register_service(self, **kwargs):
        return True


@pytest.mark.asyncio
async def test_business_orchestrator_discovers_orchestrators():
    """Test Business Orchestrator can discover and initialize orchestrators."""
    try:
        # Create mocks
        di_container = MockDIContainer()
        platform_gateway = MockPlatformGateway()
        curator = MockCurator()
        di_container.foundation_services["CuratorFoundationService"] = curator
        
        # Create Business Orchestrator
        business_orchestrator = BusinessOrchestratorService(
            service_name="BusinessOrchestratorService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Mock enabling services discovery
        business_orchestrator._discover_enabling_services = AsyncMock(return_value=None)
        
        # Mock register_with_curator
        business_orchestrator.register_with_curator = AsyncMock(return_value=True)
        
        # Mock Smart City service discovery methods
        business_orchestrator.get_curator = Mock(return_value=curator)
        
        # Initialize Business Orchestrator
        result = await business_orchestrator.initialize()
        
        assert result is True, "Business Orchestrator should initialize successfully"
        
        # Check that orchestrators were initialized
        assert "insights" in business_orchestrator.mvp_orchestrators, "Insights Orchestrator should be initialized"
        assert "operations" in business_orchestrator.mvp_orchestrators, "Operations Orchestrator should be initialized"
        
        print("✅ Business Orchestrator discovered orchestrators successfully")
        print(f"   Discovered {len(business_orchestrator.mvp_orchestrators)} orchestrators")
        
    except Exception as e:
        pytest.fail(f"Business Orchestrator discovery failed: {e}")


@pytest.mark.asyncio
async def test_business_orchestrator_routes_to_orchestrators():
    """Test Business Orchestrator can route requests to orchestrators."""
    try:
        # Create mocks
        di_container = MockDIContainer()
        platform_gateway = MockPlatformGateway()
        curator = MockCurator()
        di_container.foundation_services["CuratorFoundationService"] = curator
        
        # Create Business Orchestrator
        business_orchestrator = BusinessOrchestratorService(
            service_name="BusinessOrchestratorService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Mock initialization
        business_orchestrator._discover_enabling_services = AsyncMock(return_value=None)
        business_orchestrator.register_with_curator = AsyncMock(return_value=True)
        business_orchestrator.get_curator = Mock(return_value=curator)
        
        await business_orchestrator.initialize()
        
        # Mock orchestrator execute methods
        insights_orchestrator = business_orchestrator.mvp_orchestrators.get("insights")
        if insights_orchestrator:
            insights_orchestrator.execute = AsyncMock(return_value={"status": "success", "data": "test"})
        
        operations_orchestrator = business_orchestrator.mvp_orchestrators.get("operations")
        if operations_orchestrator:
            operations_orchestrator.execute = AsyncMock(return_value={"status": "success", "data": "test"})
        
        # Test routing to Insights Orchestrator
        result = await business_orchestrator.execute_use_case(
            use_case="insights",
            request={"action": "calculate_metrics", "params": {"resource_id": "test"}}
        )
        
        assert result.get("status") == "success", "Should route to Insights Orchestrator successfully"
        
        # Test routing to Operations Orchestrator
        result = await business_orchestrator.execute_use_case(
            use_case="operations",
            request={"action": "optimize_process", "params": {"resource_id": "test"}}
        )
        
        assert result.get("status") == "success", "Should route to Operations Orchestrator successfully"
        
        print("✅ Business Orchestrator routing test passed")
        
    except Exception as e:
        pytest.fail(f"Business Orchestrator routing failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




