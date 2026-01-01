#!/usr/bin/env python3
"""
Layer 3: Experience Foundation Initialization Tests

Tests that validate Experience Foundation initializes correctly.

WHAT: Validate initialization
HOW: Test that Experience Foundation initializes all components correctly
"""

import pytest
import sys
import os
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add symphainy-platform to path for absolute imports
# From test file: tests/layer_3_foundations/experience_foundation/test_*.py
# Go up 3 levels to reach symphainy-platform root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from foundations.experience_foundation.experience_foundation_service import ExperienceFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestExperienceFoundationInitialization:
    """Test Experience Foundation initialization."""
    
    @pytest.fixture
    def di_container(self):
        """Create DI Container instance."""
        with patch('foundations.di_container.di_container_service.UnifiedConfigurationManager'), \
             patch('foundations.di_container.di_container_service.SmartCityLoggingService'), \
             patch('foundations.di_container.di_container_service.HealthManagementUtility'), \
             patch('foundations.di_container.di_container_service.TelemetryReportingUtility'), \
             patch('foundations.di_container.di_container_service.SecurityAuthorizationUtility'), \
             patch('foundations.di_container.di_container_service.SmartCityErrorHandler'), \
             patch('foundations.di_container.di_container_service.TenantManagementUtility'), \
             patch('foundations.di_container.di_container_service.ValidationUtility'), \
             patch('foundations.di_container.di_container_service.SerializationUtility'), \
             patch('foundations.di_container.di_container_service.PublicWorksFoundationService'), \
             patch('platform_infrastructure.infrastructure.platform_gateway.PlatformInfrastructureGateway'):
            container = DIContainerService("test_realm")
            # Mock foundation service getters
            container.get_foundation_service = Mock(return_value=None)
            return container
    
    @pytest.fixture
    def public_works_foundation(self):
        """Create mock Public Works Foundation."""
        return Mock()
    
    @pytest.fixture
    def curator_foundation(self):
        """Create mock Curator Foundation."""
        mock_curator = Mock()
        mock_curator.get_registered_service = Mock(return_value=None)
        return mock_curator
    
    @pytest.fixture
    def experience_foundation(self, di_container, public_works_foundation, curator_foundation):
        """Create Experience Foundation instance."""
        return ExperienceFoundationService(
            di_container=di_container,
            public_works_foundation=public_works_foundation,
            curator_foundation=curator_foundation
        )
    
    @pytest.mark.asyncio
    async def test_experience_foundation_initializes(self, experience_foundation):
        """Test that Experience Foundation initializes."""
        result = await experience_foundation.initialize()
        assert result is True
        assert experience_foundation.is_initialized is True
        assert experience_foundation.service_health == "healthy"
    
    @pytest.mark.asyncio
    async def test_experience_foundation_has_sdk_builders(self, experience_foundation):
        """Test that Experience Foundation has SDK builders."""
        await experience_foundation.initialize()
        
        # Check that SDK builders are available
        assert experience_foundation.frontend_gateway_builder is not None
        assert experience_foundation.session_manager_builder is not None
        assert experience_foundation.user_experience_builder is not None
    
    @pytest.mark.asyncio
    async def test_experience_foundation_has_capabilities_registry(self, experience_foundation):
        """Test that Experience Foundation has capabilities registry."""
        await experience_foundation.initialize()
        
        # Check that capabilities registry exists
        assert hasattr(experience_foundation, 'experience_capabilities')
        assert isinstance(experience_foundation.experience_capabilities, dict)
    
    @pytest.mark.asyncio
    async def test_experience_foundation_tracks_created_instances(self, experience_foundation):
        """Test that Experience Foundation tracks created instances."""
        await experience_foundation.initialize()
        
        # Check that instance tracking dictionaries exist
        assert hasattr(experience_foundation, '_created_gateways')
        assert isinstance(experience_foundation._created_gateways, dict)
        assert hasattr(experience_foundation, '_created_session_managers')
        assert isinstance(experience_foundation._created_session_managers, dict)
        assert hasattr(experience_foundation, '_created_user_experiences')
        assert isinstance(experience_foundation._created_user_experiences, dict)

