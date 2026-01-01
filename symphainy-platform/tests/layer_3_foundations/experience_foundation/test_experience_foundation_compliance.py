#!/usr/bin/env python3
"""
Layer 3: Experience Foundation Compliance Tests

Tests that validate Experience Foundation complies with architectural patterns.

WHAT: Validate architectural compliance
HOW: Test that Experience Foundation uses DI Container, utilities, and Public Works Foundation properly
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add symphainy-platform to path for absolute imports
# From test file: tests/layer_3_foundations/experience_foundation/test_*.py
# Go up 3 levels to reach symphainy-platform root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from foundations.experience_foundation.experience_foundation_service import ExperienceFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestExperienceFoundationCompliance:
    """Test Experience Foundation architectural compliance."""
    
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
            return DIContainerService("test_realm")
    
    @pytest.fixture
    def public_works_foundation(self):
        """Create mock Public Works Foundation."""
        return Mock()
    
    @pytest.fixture
    def curator_foundation(self):
        """Create mock Curator Foundation."""
        return Mock()
    
    @pytest.fixture
    def experience_foundation(self, di_container, public_works_foundation, curator_foundation):
        """Create Experience Foundation instance."""
        return ExperienceFoundationService(
            di_container=di_container,
            public_works_foundation=public_works_foundation,
            curator_foundation=curator_foundation
        )
    
    def test_experience_foundation_uses_di_container(self, experience_foundation, di_container):
        """Test that Experience Foundation uses DI Container."""
        assert experience_foundation.di_container is not None
        assert experience_foundation.di_container == di_container
    
    def test_experience_foundation_uses_utilities(self, experience_foundation):
        """Test that Experience Foundation uses utilities via DI Container."""
        # Check that utility access methods exist
        assert hasattr(experience_foundation, 'get_utility')
        assert callable(experience_foundation.get_utility)
        assert hasattr(experience_foundation, 'logger')
        assert experience_foundation.logger is not None
    
    def test_experience_foundation_extends_foundation_service_base(self, experience_foundation):
        """Test that Experience Foundation extends FoundationServiceBase."""
        from bases.foundation_service_base import FoundationServiceBase
        assert isinstance(experience_foundation, FoundationServiceBase)
    
    def test_experience_foundation_has_required_attributes(self, experience_foundation):
        """Test that Experience Foundation has required attributes."""
        assert hasattr(experience_foundation, 'service_name')
        assert experience_foundation.service_name == "experience_foundation"
        assert hasattr(experience_foundation, 'di_container')
        assert hasattr(experience_foundation, 'public_works_foundation')
        assert hasattr(experience_foundation, 'curator_foundation')
    
    def test_experience_foundation_has_sdk_builders(self, experience_foundation):
        """Test that Experience Foundation has SDK builders."""
        assert hasattr(experience_foundation, 'frontend_gateway_builder')
        assert hasattr(experience_foundation, 'session_manager_builder')
        assert hasattr(experience_foundation, 'user_experience_builder')
    
    def test_experience_foundation_has_sdk_methods(self, experience_foundation):
        """Test that Experience Foundation has SDK methods."""
        assert hasattr(experience_foundation, 'create_frontend_gateway')
        assert callable(experience_foundation.create_frontend_gateway)
        assert hasattr(experience_foundation, 'create_session_manager')
        assert callable(experience_foundation.create_session_manager)
        assert hasattr(experience_foundation, 'create_user_experience')
        assert callable(experience_foundation.create_user_experience)
        assert hasattr(experience_foundation, 'get_experience_sdk')
        assert callable(experience_foundation.get_experience_sdk)
    
    def test_experience_foundation_has_coordinate_method(self, experience_foundation):
        """Test that Experience Foundation has coordinate_experience method."""
        assert hasattr(experience_foundation, 'coordinate_experience')
        assert callable(experience_foundation.coordinate_experience)
    
    def test_experience_foundation_has_health_methods(self, experience_foundation):
        """Test that Experience Foundation has health check methods."""
        assert hasattr(experience_foundation, 'health_check')
        assert callable(experience_foundation.health_check)
        assert hasattr(experience_foundation, 'get_service_capabilities')
        assert callable(experience_foundation.get_service_capabilities)

