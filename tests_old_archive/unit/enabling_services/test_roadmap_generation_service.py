#!/usr/bin/env python3
"""
Roadmap Generation Service Tests

Tests for RoadmapGenerationService enabling service in isolation.
Verifies service works before orchestrators use it.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.enabling_services]

class TestRoadmapGenerationService:
    """Test RoadmapGenerationService functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        container.get_infrastructure_abstraction = Mock(return_value=None)
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_smart_city_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    async def roadmap_service(self, mock_di_container, mock_platform_gateway):
        """Create RoadmapGenerationService instance."""
        from backend.business_enablement.enabling_services.roadmap_generation_service.roadmap_generation_service import RoadmapGenerationService
        
        service = RoadmapGenerationService(
            service_name="RoadmapGenerationService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        service.librarian.store_document = AsyncMock(return_value={"document_id": "roadmap_123"})
        service.data_steward = Mock()
        service.curator = Mock()
        service.curator.register_service = AsyncMock(return_value=True)
        service.curator.discover_service = AsyncMock(return_value=None)
        
        return service
    
    @pytest.fixture
    def sample_business_context(self):
        """Create sample business context."""
        return {
            "objectives": ["Objective 1", "Objective 2"],
            "timeline": 180,
            "budget": 500000,
            "roadmap_type": "hybrid"
        }
    
    @pytest.mark.asyncio
    async def test_service_initializes(self, mock_di_container, mock_platform_gateway):
        """Test service initializes correctly."""
        from backend.business_enablement.enabling_services.roadmap_generation_service.roadmap_generation_service import RoadmapGenerationService
        
        service = RoadmapGenerationService(
            service_name="RoadmapGenerationService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "RoadmapGenerationService"
        assert service.realm_name == "business_enablement"
        assert hasattr(service, 'roadmap_types')
        assert len(service.roadmap_types) > 0
    
    @pytest.mark.asyncio
    async def test_generate_roadmap_soa_api(self, roadmap_service, sample_business_context):
        """Test generate_roadmap SOA API works."""
        result = await roadmap_service.generate_roadmap(
            business_context=sample_business_context,
            options={}
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_create_comprehensive_strategic_plan_soa_api(self, roadmap_service, sample_business_context):
        """Test create_comprehensive_strategic_plan SOA API works."""
        result = await roadmap_service.create_comprehensive_strategic_plan(
            business_context={"business_context": sample_business_context}
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_track_strategic_progress_soa_api(self, roadmap_service):
        """Test track_strategic_progress SOA API works."""
        result = await roadmap_service.track_strategic_progress(goals=[{"id": "goal_1", "status": "in_progress", "milestones_completed": 2, "total_milestones": 5}], performance_data={})
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_analyze_strategic_trends_soa_api(self, roadmap_service):
        """Test analyze_strategic_trends SOA API works."""
        result = await roadmap_service.analyze_strategic_trends(market_data={"roadmap_ids": ["roadmap_123", "roadmap_456"]
        })
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_get_roadmap_soa_api(self, roadmap_service):
        """Test get_roadmap SOA API works."""
        result = await roadmap_service.get_roadmap("roadmap_123")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_visualize_roadmap_soa_api(self, roadmap_service):
        """Test visualize_roadmap SOA API works."""
        result = await roadmap_service.visualize_roadmap("roadmap_123")
        
        assert isinstance(result, dict)
        assert "success" in result

