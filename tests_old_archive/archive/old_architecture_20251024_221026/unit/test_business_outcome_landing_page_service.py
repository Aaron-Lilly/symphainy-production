#!/usr/bin/env python3
"""
Unit tests for Business Outcome Landing Page Service

Tests the core functionality of the Business Outcome Landing Page Service including:
- Service initialization
- Dependency injection
- Business outcome template management
- Landing page rendering
- Journey creation
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

from journey_solution.services.business_outcome_landing_page_service import BusinessOutcomeLandingPageService
from symphainy_platform.foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext, JourneyType


class TestBusinessOutcomeLandingPageService:
    """Test Business Outcome Landing Page Service functionality."""

    @pytest.fixture
    def mock_di_container(self):
        """Create a mock DI container."""
        di_container = Mock(spec=DIContainerService)
        di_container.get_foundation_service.return_value = Mock()
        return di_container

    @pytest.fixture
    def business_outcome_landing_page_service(self, mock_di_container):
        """Create a Business Outcome Landing Page Service instance."""
        return BusinessOutcomeLandingPageService(di_container=mock_di_container)

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
    async def test_inject_dependencies(self, business_outcome_landing_page_service):
        """Test dependency injection."""
        # Mock the DI container to return mock services
        mock_guide_agent = Mock()
        mock_experience_manager = Mock()
        mock_frontend_integration = Mock()
        mock_journey_orchestrator = Mock()
        mock_journey_persistence = Mock()
        
        business_outcome_landing_page_service.di_container.get_foundation_service.side_effect = [
            mock_guide_agent,
            mock_experience_manager,
            mock_frontend_integration,
            mock_journey_orchestrator,
            mock_journey_persistence
        ]
        
        # Inject dependencies
        await business_outcome_landing_page_service._inject_dependencies()
        
        # Verify dependencies were injected
        assert business_outcome_landing_page_service.guide_agent == mock_guide_agent
        assert business_outcome_landing_page_service.experience_manager == mock_experience_manager
        assert business_outcome_landing_page_service.frontend_integration == mock_frontend_integration
        assert business_outcome_landing_page_service.journey_orchestrator == mock_journey_orchestrator
        assert business_outcome_landing_page_service.journey_persistence == mock_journey_persistence
        
        # Verify DI container was called with correct service names
        expected_calls = [
            (("GuideAgent",),),
            (("ExperienceManagerService",),),
            (("FrontendIntegrationService",),),
            (("JourneyOrchestratorService",),),
            (("JourneyPersistenceService",),)
        ]
        business_outcome_landing_page_service.di_container.get_foundation_service.assert_has_calls(expected_calls)

    @pytest.mark.asyncio
    async def test_inject_dependencies_with_exception(self, business_outcome_landing_page_service):
        """Test dependency injection with exception handling."""
        # Mock DI container to raise exception
        business_outcome_landing_page_service.di_container.get_foundation_service.side_effect = Exception("Service not found")
        
        # Inject dependencies (should not raise exception)
        await business_outcome_landing_page_service._inject_dependencies()
        
        # Verify dependencies remain None
        assert business_outcome_landing_page_service.guide_agent is None
        assert business_outcome_landing_page_service.experience_manager is None
        assert business_outcome_landing_page_service.frontend_integration is None
        assert business_outcome_landing_page_service.journey_orchestrator is None
        assert business_outcome_landing_page_service.journey_persistence is None

    @pytest.mark.asyncio
    async def test_initialize_landing_page_templates(self, business_outcome_landing_page_service):
        """Test landing page templates initialization."""
        # Initialize templates
        await business_outcome_landing_page_service._initialize_landing_page_templates()
        
        # Verify templates were enhanced with metadata
        templates = business_outcome_landing_page_service.business_outcome_templates
        
        for category, template in templates.items():
            # Check that metadata was added
            assert "metadata" in template
            assert "created_at" in template["metadata"]
            assert "version" in template["metadata"]
            assert "category" in template["metadata"]
            assert template["metadata"]["category"] == category

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
    async def test_render_landing_page(self, business_outcome_landing_page_service):
        """Test rendering the landing page."""
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Mock frontend integration
        mock_landing_page_data = {
            "title": "Business Outcome Landing Page",
            "templates": business_outcome_landing_page_service.business_outcome_templates,
            "user_context": user_context
        }
        business_outcome_landing_page_service.frontend_integration = Mock()
        business_outcome_landing_page_service.frontend_integration.render_landing_page = AsyncMock(return_value=mock_landing_page_data)
        
        # Render landing page
        result = await business_outcome_landing_page_service.render_landing_page(user_context)
        
        # Verify landing page was rendered
        assert "title" in result
        assert "templates" in result
        assert "user_context" in result
        assert result["templates"] == business_outcome_landing_page_service.business_outcome_templates
        
        # Verify frontend integration was called
        business_outcome_landing_page_service.frontend_integration.render_landing_page.assert_called_once_with(
            user_context, business_outcome_landing_page_service.business_outcome_templates
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

    @pytest.mark.asyncio
    async def test_business_outcome_landing_page_service_health_check(self, business_outcome_landing_page_service):
        """Test business outcome landing page service health check."""
        # Mock the health check
        business_outcome_landing_page_service._check_dependencies = AsyncMock(return_value=True)
        business_outcome_landing_page_service._check_templates = AsyncMock(return_value=True)
        
        # Get health status
        health = await business_outcome_landing_page_service.get_health_status()
        
        # Verify health status
        assert "status" in health
        assert "dependencies" in health
        assert "templates" in health
        assert "timestamp" in health

    def test_business_outcome_landing_page_service_string_representation(self, business_outcome_landing_page_service):
        """Test string representation of business outcome landing page service."""
        # Test that the service has a meaningful string representation
        str_repr = str(business_outcome_landing_page_service)
        assert "BusinessOutcomeLandingPageService" in str_repr
        assert "landing page" in str_repr.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
