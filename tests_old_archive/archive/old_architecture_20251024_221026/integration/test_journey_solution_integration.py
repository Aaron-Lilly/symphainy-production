#!/usr/bin/env python3
"""
Integration tests for Journey Solution

Tests the integration between Journey Solution components including:
- Journey Orchestrator Service integration
- Business Outcome Landing Page Service integration
- Journey Manager Service integration
- End-to-end journey creation and management
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
from journey_solution.services.business_outcome_landing_page_service import BusinessOutcomeLandingPageService
from journey_solution.roles.journey_manager.journey_manager_service import JourneyManagerService
from symphainy_platform.foundations.di_container.di_container_service import DIContainerService
from symphainy_platform.foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from utilities import UserContext, JourneyType


class TestJourneySolutionIntegration:
    """Test Journey Solution integration functionality."""

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
    def journey_manager_service(self, mock_di_container):
        """Create a Journey Manager Service instance."""
        return JourneyManagerService(
            di_container=mock_di_container,
            journey_id="test_journey_123",
            business_outcome="data_analysis",
            journey_type=JourneyType.MVP
        )

    @pytest.mark.asyncio
    async def test_journey_solution_end_to_end_flow(self, journey_orchestrator, business_outcome_landing_page_service, journey_manager_service):
        """Test end-to-end journey solution flow."""
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Mock journey orchestrator to return journey manager
        mock_journey_manager = Mock()
        mock_journey_manager.journey_id = "test_journey_123"
        mock_journey_manager.business_outcome = "data_analysis"
        mock_journey_manager.journey_type = JourneyType.MVP
        
        journey_orchestrator.journey_manager_factory = Mock()
        journey_orchestrator.journey_manager_factory.create_journey_manager.return_value = mock_journey_manager
        
        # Mock journey manager methods
        mock_journey_manager.start_journey = AsyncMock(return_value={
            "journey_id": "test_journey_123",
            "status": "started",
            "started_at": datetime.now().isoformat()
        })
        
        mock_journey_manager.progress_journey = AsyncMock(return_value={
            "journey_id": "test_journey_123",
            "step_id": "step_1",
            "status": "in_progress"
        })
        
        mock_journey_manager.complete_journey = AsyncMock(return_value={
            "journey_id": "test_journey_123",
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        })
        
        # Mock business outcome landing page service
        business_outcome_landing_page_service.journey_orchestrator = journey_orchestrator
        
        # Test end-to-end flow
        # 1. Create business outcome journey
        journey_result = await business_outcome_landing_page_service.create_business_outcome_journey(
            user_context, "data_analysis", JourneyType.MVP
        )
        
        # Verify journey was created
        assert "journey_id" in journey_result
        assert journey_result["business_outcome"] == "data_analysis"
        assert journey_result["journey_type"] == JourneyType.MVP.value
        
        # 2. Start journey
        start_result = await mock_journey_manager.start_journey(user_context)
        assert start_result["status"] == "started"
        
        # 3. Progress journey
        progress_result = await mock_journey_manager.progress_journey(user_context, {
            "step_id": "step_1",
            "name": "Data Collection",
            "description": "Collect and profile business data",
            "status": "in_progress"
        })
        assert progress_result["status"] == "in_progress"
        
        # 4. Complete journey
        complete_result = await mock_journey_manager.complete_journey(user_context)
        assert complete_result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_journey_orchestrator_business_outcome_catalog_integration(self, journey_orchestrator):
        """Test journey orchestrator business outcome catalog integration."""
        # Initialize journey orchestrator
        await journey_orchestrator.initialize()
        
        # Get business outcome catalog
        catalog = await journey_orchestrator.get_business_outcome_catalog()
        
        # Verify catalog structure
        assert isinstance(catalog, dict)
        assert len(catalog) > 0
        
        # Check for expected business outcome categories
        expected_categories = [
            "data_analysis",
            "process_optimization",
            "customer_insights",
            "operational_efficiency",
            "strategic_planning"
        ]
        
        for category in expected_categories:
            assert category in catalog
            outcome = catalog[category]
            assert "name" in outcome
            assert "description" in outcome
            assert "icon" in outcome
            assert "examples" in outcome

    @pytest.mark.asyncio
    async def test_business_outcome_landing_page_service_integration(self, business_outcome_landing_page_service):
        """Test business outcome landing page service integration."""
        # Initialize business outcome landing page service
        await business_outcome_landing_page_service.initialize()
        
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Test getting business outcome templates
        templates = await business_outcome_landing_page_service.get_business_outcome_templates()
        assert isinstance(templates, dict)
        assert len(templates) > 0
        
        # Test getting specific template
        template = await business_outcome_landing_page_service.get_business_outcome_template("data_analysis")
        assert template is not None
        assert "name" in template
        assert "description" in template
        assert "icon" in template
        assert "examples" in template
        assert "guide_agent_prompt" in template

    @pytest.mark.asyncio
    async def test_journey_manager_service_integration(self, journey_manager_service):
        """Test journey manager service integration."""
        # Initialize journey manager service
        await journey_manager_service.initialize()
        
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Test journey lifecycle
        # 1. Start journey
        start_result = await journey_manager_service.start_journey(user_context)
        assert start_result["status"] == "started"
        
        # 2. Get journey status
        status = await journey_manager_service.get_journey_status()
        assert status["status"] == "started"
        assert status["business_outcome"] == "data_analysis"
        assert status["journey_type"] == JourneyType.MVP.value
        
        # 3. Get journey progress
        progress = await journey_manager_service.get_journey_progress()
        assert "overall_progress" in progress
        assert "current_step" in progress
        assert "completed_steps" in progress
        assert "remaining_steps" in progress
        
        # 4. Complete journey
        complete_result = await journey_manager_service.complete_journey(user_context)
        assert complete_result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_journey_solution_health_integration(self, journey_orchestrator, business_outcome_landing_page_service, journey_manager_service):
        """Test journey solution health integration."""
        # Initialize all services
        await journey_orchestrator.initialize()
        await business_outcome_landing_page_service.initialize()
        await journey_manager_service.initialize()
        
        # Test health checks for all services
        orchestrator_health = await journey_orchestrator.get_health_status()
        landing_page_health = await business_outcome_landing_page_service.get_health_status()
        journey_manager_health = await journey_manager_service.get_health_status()
        
        # Verify health statuses
        assert "status" in orchestrator_health
        assert "status" in landing_page_health
        assert "status" in journey_manager_health
        
        # Verify health timestamps
        assert "timestamp" in orchestrator_health
        assert "timestamp" in landing_page_health
        assert "timestamp" in journey_manager_health

    @pytest.mark.asyncio
    async def test_journey_solution_error_handling(self, journey_orchestrator, business_outcome_landing_page_service):
        """Test journey solution error handling."""
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Test error handling in journey orchestrator
        # Mock DI container to raise exception
        journey_orchestrator.di_container.get_foundation_service.side_effect = Exception("Service not found")
        
        # Initialize should handle exceptions gracefully
        await journey_orchestrator.initialize()
        
        # Test error handling in business outcome landing page service
        # Mock DI container to raise exception
        business_outcome_landing_page_service.di_container.get_foundation_service.side_effect = Exception("Service not found")
        
        # Initialize should handle exceptions gracefully
        await business_outcome_landing_page_service.initialize()

    @pytest.mark.asyncio
    async def test_journey_solution_performance(self, journey_orchestrator, business_outcome_landing_page_service, journey_manager_service):
        """Test journey solution performance."""
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Test performance of multiple operations
        start_time = datetime.now()
        
        # Initialize all services
        await journey_orchestrator.initialize()
        await business_outcome_landing_page_service.initialize()
        await journey_manager_service.initialize()
        
        # Test multiple journey operations
        for i in range(10):
            # Create journey
            journey_result = await business_outcome_landing_page_service.create_business_outcome_journey(
                user_context, "data_analysis", JourneyType.MVP
            )
            assert "journey_id" in journey_result
            
            # Start journey
            start_result = await journey_manager_service.start_journey(user_context)
            assert start_result["status"] == "started"
            
            # Complete journey
            complete_result = await journey_manager_service.complete_journey(user_context)
            assert complete_result["status"] == "completed"
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Verify performance (should complete within reasonable time)
        assert duration < 5.0  # Should complete within 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
