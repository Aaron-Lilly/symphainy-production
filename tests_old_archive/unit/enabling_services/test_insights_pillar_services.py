#!/usr/bin/env python3
"""
Unit Tests for Insights Pillar Enabling Services

Smoke tests for Insights Pillar enabling services including:
- WorkflowManagerService
- VisualizationEngineService
- ReportGeneratorService
- RoadmapGenerationService
- DataInsightsQueryService (already tested separately)
"""

import pytest

import os
from unittest.mock import Mock, AsyncMock

from backend.business_enablement.enabling_services.workflow_manager_service.workflow_manager_service import WorkflowManagerService
from backend.business_enablement.enabling_services.visualization_engine_service.visualization_engine_service import VisualizationEngineService
from backend.business_enablement.enabling_services.report_generator_service.report_generator_service import ReportGeneratorService
from backend.business_enablement.enabling_services.roadmap_generation_service.roadmap_generation_service import RoadmapGenerationService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]

class TestInsightsPillarServices:
    """Smoke tests for Insights Pillar enabling services."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_smart_city_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        return container
    
    async def test_workflow_manager_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test WorkflowManagerService initializes correctly."""
        service = WorkflowManagerService(
            service_name="WorkflowManagerService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "WorkflowManagerService"
        assert service.realm_name == "business_enablement"
        # Service initialized successfully
    
    async def test_visualization_engine_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test VisualizationEngineService initializes correctly."""
        service = VisualizationEngineService(
            service_name="VisualizationEngineService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "VisualizationEngineService"
        assert service.realm_name == "business_enablement"
        # Service initialized successfully
    
    async def test_report_generator_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test ReportGeneratorService initializes correctly."""
        service = ReportGeneratorService(
            service_name="ReportGeneratorService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "ReportGeneratorService"
        assert service.realm_name == "business_enablement"
        # Service initialized successfully
    
    async def test_roadmap_generation_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test RoadmapGenerationService initializes correctly."""
        service = RoadmapGenerationService(
            service_name="RoadmapGenerationService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "RoadmapGenerationService"
        assert service.realm_name == "business_enablement"
        # Service initialized successfully

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

