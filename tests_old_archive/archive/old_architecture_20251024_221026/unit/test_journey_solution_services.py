#!/usr/bin/env python3
"""
Unit tests for Journey Solution Services

Tests the core functionality of the Journey Solution services including:
- Journey Orchestrator Service
- Business Outcome Landing Page Service
- Business Outcome Analyzer Service
- Solution Architect Service
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../symphainy-platform')))

from journey_solution.services.journey_orchestrator_service import JourneyOrchestratorService
from journey_solution.services.business_outcome_landing_page_service import BusinessOutcomeLandingPageService
from journey_solution.services.business_outcome_analyzer_service import BusinessOutcomeAnalyzerService
from journey_solution.services.solution_architect_service import SolutionArchitectService
from symphainy_platform.foundations.di_container.di_container_service import DIContainerService
from symphainy_platform.foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from utilities import UserContext
from symphainy_platform.journey_solution.services.journey_persistence_service import JourneyType


class TestJourneySolutionServices:
    """Test Journey Solution Services functionality."""

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

    @pytest.fixture
    def business_outcome_landing_page_service(self, mock_di_container):
        """Create a Business Outcome Landing Page Service instance."""
        return BusinessOutcomeLandingPageService(di_container=mock_di_container)

    @pytest.fixture
    def business_outcome_analyzer_service(self, mock_di_container):
        """Create a Business Outcome Analyzer Service instance."""
        return BusinessOutcomeAnalyzerService(di_container=mock_di_container)

    @pytest.fixture
    def solution_architect_service(self, mock_di_container):
        """Create a Solution Architect Service instance."""
        return SolutionArchitectService(di_container=mock_di_container)

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

    def test_business_outcome_landing_page_service_initialization(self, business_outcome_landing_page_service):
        """Test Business Outcome Landing Page Service initializes correctly."""
        assert business_outcome_landing_page_service is not None
        assert business_outcome_landing_page_service.di_container is not None
        
        # Check that dependencies are initially None
        assert business_outcome_landing_page_service.guide_agent is None
        assert business_outcome_landing_page_service.experience_manager is None
        assert business_outcome_landing_page_service.frontend_integration is None
        assert business_outcome_landing_page_service.journey_orchestrator is None
        assert business_outcome_landing_page_service.journey_persistence is None
        
        # Check that business outcome templates are initialized
        assert isinstance(business_outcome_landing_page_service.business_outcome_templates, dict)
        assert len(business_outcome_landing_page_service.business_outcome_templates) > 0

    def test_business_outcome_analyzer_service_initialization(self, business_outcome_analyzer_service):
        """Test Business Outcome Analyzer Service initializes correctly."""
        assert business_outcome_analyzer_service is not None
        assert business_outcome_analyzer_service.di_container is not None
        
        # Check that dependencies are initially None
        assert business_outcome_analyzer_service.guide_agent is None
        assert business_outcome_analyzer_service.experience_manager is None
        assert business_outcome_analyzer_service.journey_orchestrator is None
        
        # Check that business outcome analysis structures are initialized
        assert isinstance(business_outcome_analyzer_service.business_outcome_analysis, dict)
        assert isinstance(business_outcome_analyzer_service.analysis_templates, dict)
        assert isinstance(business_outcome_analyzer_service.analysis_results, dict)

    def test_solution_architect_service_initialization(self, solution_architect_service):
        """Test Solution Architect Service initializes correctly."""
        assert solution_architect_service is not None
        assert solution_architect_service.di_container is not None
        
        # Check that dependencies are initially None
        assert solution_architect_service.guide_agent is None
        assert solution_architect_service.experience_manager is None
        assert solution_architect_service.journey_orchestrator is None
        
        # Check that solution architecture structures are initialized
        assert isinstance(solution_architect_service.solution_architectures, dict)
        assert isinstance(solution_architect_service.architecture_templates, dict)
        assert isinstance(solution_architect_service.architecture_results, dict)

    def test_business_outcome_templates_initialization(self, business_outcome_landing_page_service):
        """Test business outcome templates are properly initialized."""
        templates = business_outcome_landing_page_service.business_outcome_templates
        
        # Check for expected business outcome categories
        expected_categories = [
            "data_analysis",
            "process_optimization",
            "customer_insights", 
            "operational_efficiency",
            "strategic_planning"
        ]
        
        for category in expected_categories:
            assert category in templates
            template = templates[category]
            
            # Check template structure
            assert "name" in template
            assert "description" in template
            assert "icon" in template
            assert "examples" in template
            assert "guide_agent_prompt" in template
            
            # Check template content
            assert isinstance(template["name"], str)
            assert isinstance(template["description"], str)
            assert isinstance(template["icon"], str)
            assert isinstance(template["examples"], list)
            assert isinstance(template["guide_agent_prompt"], str)
            
            # Check examples are not empty
            assert len(template["examples"]) > 0

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
    async def test_business_outcome_landing_page_service_initialize(self, business_outcome_landing_page_service):
        """Test Business Outcome Landing Page Service initialization process."""
        # Mock the injection methods
        business_outcome_landing_page_service._inject_dependencies = AsyncMock()
        business_outcome_landing_page_service._initialize_landing_page_templates = AsyncMock()
        
        # Initialize the service
        await business_outcome_landing_page_service.initialize()
        
        # Verify all initialization methods were called
        business_outcome_landing_page_service._inject_dependencies.assert_called_once()
        business_outcome_landing_page_service._initialize_landing_page_templates.assert_called_once()

    @pytest.mark.asyncio
    async def test_business_outcome_analyzer_service_initialize(self, business_outcome_analyzer_service):
        """Test Business Outcome Analyzer Service initialization process."""
        # Mock the injection methods
        business_outcome_analyzer_service._inject_dependencies = AsyncMock()
        business_outcome_analyzer_service._initialize_analysis_templates = AsyncMock()
        
        # Initialize the service
        await business_outcome_analyzer_service.initialize()
        
        # Verify all initialization methods were called
        business_outcome_analyzer_service._inject_dependencies.assert_called_once()
        business_outcome_analyzer_service._initialize_analysis_templates.assert_called_once()

    @pytest.mark.asyncio
    async def test_solution_architect_service_initialize(self, solution_architect_service):
        """Test Solution Architect Service initialization process."""
        # Mock the injection methods
        solution_architect_service._inject_dependencies = AsyncMock()
        solution_architect_service._initialize_architecture_templates = AsyncMock()
        
        # Initialize the service
        await solution_architect_service.initialize()
        
        # Verify all initialization methods were called
        solution_architect_service._inject_dependencies.assert_called_once()
        solution_architect_service._initialize_architecture_templates.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_business_outcome_journey(self, business_outcome_landing_page_service):
        """Test creating a business outcome journey."""
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Mock journey orchestrator
        mock_journey_result = {
            "journey_id": "test_journey_123",
            "status": "created",
            "business_outcome": "data_analysis"
        }
        business_outcome_landing_page_service.journey_orchestrator = Mock()
        business_outcome_landing_page_service.journey_orchestrator.create_business_outcome_journey = AsyncMock(return_value=mock_journey_result)
        
        # Create journey
        business_outcome = "data_analysis"
        journey_type = JourneyType.MVP
        
        result = await business_outcome_landing_page_service.create_business_outcome_journey(
            user_context, business_outcome, journey_type
        )
        
        # Verify journey was created
        assert "journey_id" in result
        assert "status" in result
        assert "business_outcome" in result
        assert result["business_outcome"] == business_outcome
        assert result["journey_type"] == journey_type.value
        
        # Verify journey orchestrator was called
        business_outcome_landing_page_service.journey_orchestrator.create_business_outcome_journey.assert_called_once_with(
            user_context, business_outcome, journey_type
        )

    @pytest.mark.asyncio
    async def test_get_business_outcome_templates(self, business_outcome_landing_page_service):
        """Test getting business outcome templates."""
        # Get templates
        templates = await business_outcome_landing_page_service.get_business_outcome_templates()
        
        # Verify templates
        assert isinstance(templates, dict)
        assert len(templates) > 0
        assert templates == business_outcome_landing_page_service.business_outcome_templates

    @pytest.mark.asyncio
    async def test_get_business_outcome_template_by_category(self, business_outcome_landing_page_service):
        """Test getting a specific business outcome template."""
        # Get specific template
        template = await business_outcome_landing_page_service.get_business_outcome_template("data_analysis")
        
        # Verify template
        assert template is not None
        assert "name" in template
        assert "description" in template
        assert "icon" in template
        assert "examples" in template
        assert "guide_agent_prompt" in template

    @pytest.mark.asyncio
    async def test_get_business_outcome_template_by_category_not_found(self, business_outcome_landing_page_service):
        """Test getting a non-existent business outcome template."""
        # Get non-existent template
        template = await business_outcome_landing_page_service.get_business_outcome_template("non_existent")
        
        # Verify template is None
        assert template is None

    def test_journey_solution_services_string_representation(self, journey_orchestrator, business_outcome_landing_page_service, business_outcome_analyzer_service, solution_architect_service):
        """Test string representation of journey solution services."""
        # Test that the services have meaningful string representations
        orchestrator_str = str(journey_orchestrator)
        landing_page_str = str(business_outcome_landing_page_service)
        analyzer_str = str(business_outcome_analyzer_service)
        architect_str = str(solution_architect_service)
        
        assert "JourneyOrchestratorService" in orchestrator_str
        assert "BusinessOutcomeLandingPageService" in landing_page_str
        assert "BusinessOutcomeAnalyzerService" in analyzer_str
        assert "SolutionArchitectService" in architect_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
