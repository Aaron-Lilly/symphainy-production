#!/usr/bin/env python3
"""
Layer 3: Experience Foundation Outputs Tests

Tests that validate Experience Foundation outputs are properly accessible.

WHAT: Validate outputs are accessible
HOW: Test that Experience Foundation exposes its SDK builders and capabilities correctly
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


class TestExperienceFoundationOutputs:
    """Test Experience Foundation outputs are accessible."""
    
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
            mock_platform_gateway = Mock()
            container.get_foundation_service = Mock(side_effect=lambda name: mock_platform_gateway if name == "PlatformInfrastructureGateway" else None)
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
    async def test_get_experience_sdk_returns_sdk_builders(self, experience_foundation):
        """Test that get_experience_sdk returns SDK builders."""
        await experience_foundation.initialize()
        
        sdk = experience_foundation.get_experience_sdk()
        
        assert sdk is not None
        assert "frontend_gateway_builder" in sdk
        assert "session_manager_builder" in sdk
        assert "user_experience_builder" in sdk
    
    @pytest.mark.asyncio
    async def test_get_service_capabilities_returns_capabilities(self, experience_foundation):
        """Test that get_service_capabilities returns capabilities."""
        await experience_foundation.initialize()
        
        capabilities = await experience_foundation.get_service_capabilities()
        
        assert capabilities is not None
        assert "service_name" in capabilities
        assert capabilities["service_name"] == "experience_foundation"
        assert "service_type" in capabilities
        assert capabilities["service_type"] == "foundation"
        assert "capabilities" in capabilities
        assert "sdk_components" in capabilities
        assert "created_instances" in capabilities
    
    @pytest.mark.asyncio
    async def test_health_check_returns_health_status(self, experience_foundation):
        """Test that health_check returns health status."""
        await experience_foundation.initialize()
        
        health = await experience_foundation.health_check()
        
        assert health is not None
        assert "status" in health
        assert health["status"] == "healthy"
        assert "service_name" in health
        assert health["service_name"] == "experience_foundation"
        assert "created_gateways" in health
        assert "created_session_managers" in health
        assert "created_user_experiences" in health
        assert "timestamp" in health
    
    @pytest.mark.asyncio
    async def test_coordinate_experience_returns_result(self, experience_foundation):
        """Test that coordinate_experience returns coordination result."""
        await experience_foundation.initialize()
        
        # Mock the SDK builder methods to avoid actual initialization
        with patch.object(experience_foundation, 'create_frontend_gateway', new_callable=AsyncMock) as mock_create:
            mock_gateway = Mock()
            mock_create.return_value = mock_gateway
            
            experience_request = {
                "realm_name": "test_realm",
                "experience_type": "frontend_gateway",
                "config": {}
            }
            
            result = await experience_foundation.coordinate_experience(experience_request)
            
            assert result is not None
            assert "success" in result
            assert result["success"] is True
            assert "experience_type" in result
            assert result["experience_type"] == "frontend_gateway"
            assert "realm_name" in result
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_coordinate_experience_handles_unknown_type(self, experience_foundation):
        """Test that coordinate_experience handles unknown experience type."""
        await experience_foundation.initialize()
        
        experience_request = {
            "realm_name": "test_realm",
            "experience_type": "unknown_type",
            "config": {}
        }
        
        result = await experience_foundation.coordinate_experience(experience_request)
        
        assert result is not None
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "supported_types" in result
    
    @pytest.mark.asyncio
    async def test_sdk_builders_are_accessible(self, experience_foundation):
        """Test that SDK builders are accessible."""
        await experience_foundation.initialize()
        
        assert experience_foundation.frontend_gateway_builder is not None
        assert experience_foundation.session_manager_builder is not None
        assert experience_foundation.user_experience_builder is not None
    
    @pytest.mark.asyncio
    async def test_create_methods_are_accessible(self, experience_foundation):
        """Test that create methods are accessible."""
        await experience_foundation.initialize()
        
        assert hasattr(experience_foundation, 'create_frontend_gateway')
        assert callable(experience_foundation.create_frontend_gateway)
        assert hasattr(experience_foundation, 'create_session_manager')
        assert callable(experience_foundation.create_session_manager)
        assert hasattr(experience_foundation, 'create_user_experience')
        assert callable(experience_foundation.create_user_experience)

