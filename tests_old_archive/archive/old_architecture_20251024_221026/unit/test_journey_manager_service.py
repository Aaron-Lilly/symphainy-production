#!/usr/bin/env python3
"""
Unit tests for Journey Manager Service

Tests the core functionality of the Journey Manager Service including:
- Service initialization
- Journey management
- Business outcome tracking
- Journey orchestration
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

from journey_solution.roles.journey_manager.journey_manager_service import JourneyManagerService
from symphainy_platform.foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext, JourneyType


class TestJourneyManagerService:
    """Test Journey Manager Service functionality."""

    @pytest.fixture
    def mock_di_container(self):
        """Create a mock DI container."""
        di_container = Mock(spec=DIContainerService)
        di_container.get_foundation_service.return_value = Mock()
        return di_container

    @pytest.fixture
    def journey_manager_service(self, mock_di_container):
        """Create a Journey Manager Service instance."""
        return JourneyManagerService(
            di_container=mock_di_container,
            journey_id="test_journey_123",
            business_outcome="data_analysis",
            journey_type=JourneyType.MVP
        )

    def test_journey_manager_service_initialization(self, journey_manager_service):
        """Test Journey Manager Service initializes correctly."""
        assert journey_manager_service is not None
        assert journey_manager_service.di_container is not None
        assert journey_manager_service.journey_id == "test_journey_123"
        assert journey_manager_service.business_outcome == "data_analysis"
        assert journey_manager_service.journey_type == JourneyType.MVP
        
        # Check that journey state is initialized
        assert isinstance(journey_manager_service.journey_state, dict)
        assert "status" in journey_manager_service.journey_state
        assert "created_at" in journey_manager_service.journey_state
        assert "business_outcome" in journey_manager_service.journey_state
        assert journey_manager_service.journey_state["business_outcome"] == "data_analysis"

    @pytest.mark.asyncio
    async def test_journey_manager_service_initialize(self, journey_manager_service):
        """Test Journey Manager Service initialization process."""
        # Mock the initialization methods
        journey_manager_service._initialize_journey_components = AsyncMock()
        journey_manager_service._initialize_business_outcome_tracking = AsyncMock()
        journey_manager_service._initialize_journey_orchestration = AsyncMock()
        
        # Initialize the service
        await journey_manager_service.initialize()
        
        # Verify all initialization methods were called
        journey_manager_service._initialize_journey_components.assert_called_once()
        journey_manager_service._initialize_business_outcome_tracking.assert_called_once()
        journey_manager_service._initialize_journey_orchestration.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_journey_components(self, journey_manager_service):
        """Test journey components initialization."""
        # Mock the DI container to return mock components
        mock_guide_agent = Mock()
        mock_experience_manager = Mock()
        mock_city_manager = Mock()
        mock_delivery_manager = Mock()
        
        journey_manager_service.di_container.get_foundation_service.side_effect = [
            mock_guide_agent,
            mock_experience_manager,
            mock_city_manager,
            mock_delivery_manager
        ]
        
        # Initialize components
        await journey_manager_service._initialize_journey_components()
        
        # Verify components were initialized
        assert journey_manager_service.guide_agent == mock_guide_agent
        assert journey_manager_service.experience_manager == mock_experience_manager
        assert journey_manager_service.city_manager == mock_city_manager
        assert journey_manager_service.delivery_manager == mock_delivery_manager

    @pytest.mark.asyncio
    async def test_initialize_business_outcome_tracking(self, journey_manager_service):
        """Test business outcome tracking initialization."""
        # Initialize tracking
        await journey_manager_service._initialize_business_outcome_tracking()
        
        # Verify tracking was initialized
        assert "business_outcome_tracking" in journey_manager_service.journey_state
        assert "metrics" in journey_manager_service.journey_state["business_outcome_tracking"]
        assert "milestones" in journey_manager_service.journey_state["business_outcome_tracking"]
        assert "progress" in journey_manager_service.journey_state["business_outcome_tracking"]

    @pytest.mark.asyncio
    async def test_initialize_journey_orchestration(self, journey_manager_service):
        """Test journey orchestration initialization."""
        # Initialize orchestration
        await journey_manager_service._initialize_journey_orchestration()
        
        # Verify orchestration was initialized
        assert "orchestration" in journey_manager_service.journey_state
        assert "current_step" in journey_manager_service.journey_state["orchestration"]
        assert "next_steps" in journey_manager_service.journey_state["orchestration"]
        assert "completed_steps" in journey_manager_service.journey_state["orchestration"]

    @pytest.mark.asyncio
    async def test_start_journey(self, journey_manager_service):
        """Test starting a journey."""
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Start journey
        result = await journey_manager_service.start_journey(user_context)
        
        # Verify journey was started
        assert "journey_id" in result
        assert "status" in result
        assert "started_at" in result
        assert result["journey_id"] == journey_manager_service.journey_id
        assert result["status"] == "started"
        
        # Verify journey state was updated
        assert journey_manager_service.journey_state["status"] == "started"
        assert "started_at" in journey_manager_service.journey_state

    @pytest.mark.asyncio
    async def test_progress_journey(self, journey_manager_service):
        """Test progressing a journey."""
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Mock journey step
        journey_step = {
            "step_id": "step_1",
            "name": "Data Collection",
            "description": "Collect and profile business data",
            "status": "in_progress"
        }
        
        # Progress journey
        result = await journey_manager_service.progress_journey(user_context, journey_step)
        
        # Verify journey was progressed
        assert "journey_id" in result
        assert "step_id" in result
        assert "status" in result
        assert result["journey_id"] == journey_manager_service.journey_id
        assert result["step_id"] == "step_1"
        assert result["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_complete_journey(self, journey_manager_service):
        """Test completing a journey."""
        # Mock user context
        user_context = Mock(spec=UserContext)
        user_context.user_id = "test_user"
        user_context.tenant_id = "test_tenant"
        
        # Complete journey
        result = await journey_manager_service.complete_journey(user_context)
        
        # Verify journey was completed
        assert "journey_id" in result
        assert "status" in result
        assert "completed_at" in result
        assert result["journey_id"] == journey_manager_service.journey_id
        assert result["status"] == "completed"
        
        # Verify journey state was updated
        assert journey_manager_service.journey_state["status"] == "completed"
        assert "completed_at" in journey_manager_service.journey_state

    @pytest.mark.asyncio
    async def test_get_journey_status(self, journey_manager_service):
        """Test getting journey status."""
        # Get journey status
        status = await journey_manager_service.get_journey_status()
        
        # Verify status
        assert "journey_id" in status
        assert "status" in status
        assert "business_outcome" in status
        assert "journey_type" in status
        assert "created_at" in status
        assert status["journey_id"] == journey_manager_service.journey_id
        assert status["business_outcome"] == "data_analysis"
        assert status["journey_type"] == JourneyType.MVP.value

    @pytest.mark.asyncio
    async def test_get_journey_progress(self, journey_manager_service):
        """Test getting journey progress."""
        # Get journey progress
        progress = await journey_manager_service.get_journey_progress()
        
        # Verify progress
        assert "overall_progress" in progress
        assert "current_step" in progress
        assert "completed_steps" in progress
        assert "remaining_steps" in progress
        assert "milestones" in progress

    @pytest.mark.asyncio
    async def test_journey_manager_service_health_check(self, journey_manager_service):
        """Test journey manager service health check."""
        # Mock the health check
        journey_manager_service._check_components = AsyncMock(return_value=True)
        journey_manager_service._check_journey_state = AsyncMock(return_value=True)
        journey_manager_service._check_business_outcome_tracking = AsyncMock(return_value=True)
        
        # Get health status
        health = await journey_manager_service.get_health_status()
        
        # Verify health status
        assert "status" in health
        assert "components" in health
        assert "journey_state" in health
        assert "business_outcome_tracking" in health
        assert "timestamp" in health

    def test_journey_manager_service_string_representation(self, journey_manager_service):
        """Test string representation of journey manager service."""
        # Test that the service has a meaningful string representation
        str_repr = str(journey_manager_service)
        assert "JourneyManagerService" in str_repr
        assert "journey" in str_repr.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
