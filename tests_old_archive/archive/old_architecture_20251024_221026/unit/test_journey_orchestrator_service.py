#!/usr/bin/env python3
"""
Unit tests for Journey Orchestrator Service

Tests the core functionality of the Journey Orchestrator Service including:
- Service initialization
- Cross-dimensional manager injection
- Journey orchestration
- Business outcome management
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import uuid

# Add the project root to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from journey_solution.services.journey_orchestrator_service import JourneyOrchestratorService
from symphainy_platform.foundations.di_container.di_container_service import DIContainerService
from symphainy_platform.foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from utilities import UserContext, JourneyType


class TestJourneyOrchestratorService:
    """Test Journey Orchestrator Service functionality."""

    @pytest.fixture
    def mock_di_container(self):
        """Create a mock DI container."""
        di_container = Mock(spec=DIContainerService)
        di_container.get_foundation_service.return_value = Mock()
        return di_container

    @pytest.fixture
    def mock_public_works_foundation(self):
        """Create a mock Public Works Foundation."""
        return Mock(spec=PublicWorksFoundationService)

    @pytest.fixture
    def mock_curator_foundation(self):
        """Create a mock Curator Foundation."""
        return Mock(spec=CuratorFoundationService)

    @pytest.fixture
    def journey_orchestrator(self, mock_di_container, mock_public_works_foundation, mock_curator_foundation):
        """Create a Journey Orchestrator Service instance."""
        return JourneyOrchestratorService(
            di_container=mock_di_container,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )

    def test_journey_orchestrator_initialization(self, journey_orchestrator):
        """Test Journey Orchestrator Service initializes correctly."""
        assert journey_orchestrator is not None
        assert journey_orchestrator.di_container is not None
        assert journey_orchestrator.public_works_foundation is not None
        assert journey_orchestrator.curator_foundation is not None
        
        # Check that cross-dimensional managers are initially None
        assert journey_orchestrator.city_manager is None
        assert journey_orchestrator.delivery_manager is None
        assert journey_orchestrator.experience_manager is None
        
        # Check that journey/solution services are initially None
        assert journey_orchestrator.solution_architect is None
        assert journey_orchestrator.business_outcome_analyzer is None
        
        # Check that journey management structures are initialized
        assert isinstance(journey_orchestrator.active_journeys, dict)
        assert isinstance(journey_orchestrator.journey_templates, dict)
        assert isinstance(journey_orchestrator.business_outcome_catalog, dict)

    @pytest.mark.asyncio
    async def test_journey_orchestrator_initialize(self, journey_orchestrator):
        """Test Journey Orchestrator Service initialization process."""
        # Mock the injection methods
        journey_orchestrator._inject_cross_dimensional_managers = AsyncMock()
        journey_orchestrator._initialize_journey_solution_services = AsyncMock()
        journey_orchestrator._initialize_business_outcome_catalog = AsyncMock()
        journey_orchestrator._initialize_journey_templates = AsyncMock()
        
        # Initialize the service
        await journey_orchestrator.initialize()
        
        # Verify all initialization methods were called
        journey_orchestrator._inject_cross_dimensional_managers.assert_called_once()
        journey_orchestrator._initialize_journey_solution_services.assert_called_once()
        journey_orchestrator._initialize_business_outcome_catalog.assert_called_once()
        journey_orchestrator._initialize_journey_templates.assert_called_once()

    @pytest.mark.asyncio
    async def test_inject_cross_dimensional_managers(self, journey_orchestrator):
        """Test cross-dimensional manager injection."""
        # Mock the DI container to return mock managers
        mock_city_manager = Mock()
        mock_delivery_manager = Mock()
        mock_experience_manager = Mock()
        
        journey_orchestrator.di_container.get_foundation_service.side_effect = [
            mock_city_manager,
            mock_delivery_manager,
            mock_experience_manager
        ]
        
        # Inject managers
        await journey_orchestrator._inject_cross_dimensional_managers()
        
        # Verify managers were injected
        assert journey_orchestrator.city_manager == mock_city_manager
        assert journey_orchestrator.delivery_manager == mock_delivery_manager
        assert journey_orchestrator.experience_manager == mock_experience_manager
        
        # Verify DI container was called with correct service names
        expected_calls = [
            (("CityManagerService",),),
            (("DeliveryManagerService",),),
            (("ExperienceManagerService",),)
        ]
        journey_orchestrator.di_container.get_foundation_service.assert_has_calls(expected_calls)

    @pytest.mark.asyncio
    async def test_inject_cross_dimensional_managers_with_exception(self, journey_orchestrator):
        """Test cross-dimensional manager injection with exception handling."""
        # Mock DI container to raise exception
        journey_orchestrator.di_container.get_foundation_service.side_effect = Exception("Service not found")
        
        # Inject managers (should not raise exception)
        await journey_orchestrator._inject_cross_dimensional_managers()
        
        # Verify managers remain None
        assert journey_orchestrator.city_manager is None
        assert journey_orchestrator.delivery_manager is None
        assert journey_orchestrator.experience_manager is None

    @pytest.mark.asyncio
    async def test_initialize_journey_solution_services(self, journey_orchestrator):
        """Test journey/solution services initialization."""
        # Mock the DI container to return mock services
        mock_solution_architect = Mock()
        mock_business_outcome_analyzer = Mock()
        mock_journey_manager_factory = Mock()
        
        journey_orchestrator.di_container.get_foundation_service.side_effect = [
            mock_solution_architect,
            mock_business_outcome_analyzer,
            mock_journey_manager_factory
        ]
        
        # Initialize services
        await journey_orchestrator._initialize_journey_solution_services()
        
        # Verify services were initialized
        assert journey_orchestrator.solution_architect == mock_solution_architect
        assert journey_orchestrator.business_outcome_analyzer == mock_business_outcome_analyzer
        assert journey_orchestrator.journey_manager_factory == mock_journey_manager_factory

    @pytest.mark.asyncio
    async def test_initialize_business_outcome_catalog(self, journey_orchestrator):
        """Test business outcome catalog initialization."""
        # Initialize catalog
        await journey_orchestrator._initialize_business_outcome_catalog()
        
        # Verify catalog was initialized
        assert isinstance(journey_orchestrator.business_outcome_catalog, dict)
        assert len(journey_orchestrator.business_outcome_catalog) > 0
        
        # Check for expected business outcome categories
        expected_categories = [
            "data_analysis",
            "process_optimization", 
            "customer_insights",
            "operational_efficiency",
            "strategic_planning"
        ]
        
        for category in expected_categories:
            assert category in journey_orchestrator.business_outcome_catalog
            outcome = journey_orchestrator.business_outcome_catalog[category]
            assert "name" in outcome
            assert "description" in outcome
            assert "icon" in outcome
            assert "examples" in outcome

    @pytest.mark.asyncio
    async def test_initialize_journey_templates(self, journey_orchestrator):
        """Test journey templates initialization."""
        # Initialize templates
        await journey_orchestrator._initialize_journey_templates()
        
        # Verify templates were initialized
        assert isinstance(journey_orchestrator.journey_templates, dict)
        assert len(journey_orchestrator.journey_templates) > 0
        
        # Check for expected journey types
        expected_types = ["mvp", "enterprise", "custom"]
        
        for journey_type in expected_types:
            assert journey_type in journey_orchestrator.journey_templates
            template = journey_orchestrator.journey_templates[journey_type]
            assert "name" in template
            assert "description" in template
            assert "steps" in template
            assert "estimated_duration" in template

    @pytest.mark.asyncio
    async def test_create_business_outcome_journey(self, journey_orchestrator):
        """Test creating a business outcome journey."""
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Mock journey manager factory
        mock_journey_manager = Mock()
        journey_orchestrator.journey_manager_factory = Mock()
        journey_orchestrator.journey_manager_factory.create_journey_manager.return_value = mock_journey_manager
        
        # Create journey
        business_outcome = "data_analysis"
        journey_type = JourneyType.MVP
        
        result = await journey_orchestrator.create_business_outcome_journey(
            user_context, business_outcome, journey_type
        )
        
        # Verify journey was created
        assert "journey_id" in result
        assert "status" in result
        assert "business_outcome" in result
        assert result["business_outcome"] == business_outcome
        assert result["journey_type"] == journey_type.value
        
        # Verify journey manager was created
        journey_orchestrator.journey_manager_factory.create_journey_manager.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_journeys(self, journey_orchestrator):
        """Test getting active journeys."""
        # Add some mock active journeys
        journey_orchestrator.active_journeys = {
            "journey_1": {"user_id": "user1", "status": "active"},
            "journey_2": {"user_id": "user2", "status": "active"}
        }
        
        # Get active journeys
        active_journeys = await journey_orchestrator.get_active_journeys()
        
        # Verify active journeys
        assert len(active_journeys) == 2
        assert "journey_1" in active_journeys
        assert "journey_2" in active_journeys

    @pytest.mark.asyncio
    async def test_get_journey_templates(self, journey_orchestrator):
        """Test getting journey templates."""
        # Initialize templates first
        await journey_orchestrator._initialize_journey_templates()
        
        # Get templates
        templates = await journey_orchestrator.get_journey_templates()
        
        # Verify templates
        assert isinstance(templates, dict)
        assert len(templates) > 0
        assert "mvp" in templates
        assert "enterprise" in templates

    @pytest.mark.asyncio
    async def test_get_business_outcome_catalog(self, journey_orchestrator):
        """Test getting business outcome catalog."""
        # Initialize catalog first
        await journey_orchestrator._initialize_business_outcome_catalog()
        
        # Get catalog
        catalog = await journey_orchestrator.get_business_outcome_catalog()
        
        # Verify catalog
        assert isinstance(catalog, dict)
        assert len(catalog) > 0
        assert "data_analysis" in catalog
        assert "process_optimization" in catalog

    @pytest.mark.asyncio
    async def test_journey_orchestrator_health_check(self, journey_orchestrator):
        """Test journey orchestrator health check."""
        # Mock the health check
        journey_orchestrator._check_cross_dimensional_managers = AsyncMock(return_value=True)
        journey_orchestrator._check_journey_solution_services = AsyncMock(return_value=True)
        journey_orchestrator._check_active_journeys = AsyncMock(return_value=True)
        
        # Get health status
        health = await journey_orchestrator.get_health_status()
        
        # Verify health status
        assert "status" in health
        assert "cross_dimensional_managers" in health
        assert "journey_solution_services" in health
        assert "active_journeys" in health
        assert "timestamp" in health

    def test_journey_orchestrator_string_representation(self, journey_orchestrator):
        """Test string representation of journey orchestrator."""
        # Test that the service has a meaningful string representation
        str_repr = str(journey_orchestrator)
        assert "JourneyOrchestratorService" in str_repr
        assert "orchestration hub" in str_repr.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
