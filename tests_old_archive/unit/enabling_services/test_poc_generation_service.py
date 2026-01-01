#!/usr/bin/env python3
"""
POC Generation Service Tests

Tests for POCGenerationService enabling service in isolation.
Verifies service works before orchestrators use it.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.enabling_services]

class TestPOCGenerationService:
    """Test POCGenerationService functionality."""
    
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
    async def poc_service(self, mock_di_container, mock_platform_gateway):
        """Create POCGenerationService instance."""
        from backend.business_enablement.enabling_services.poc_generation_service.poc_generation_service import POCGenerationService
        
        service = POCGenerationService(
            service_name="POCGenerationService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        service.librarian.store_document = AsyncMock(return_value={"document_id": "poc_123"})
        service.data_steward = Mock()
        service.curator = Mock()
        service.curator.register_service = AsyncMock(return_value=True)
        service.curator.discover_service = AsyncMock(return_value=None)
        
        return service
    
    @pytest.fixture
    def sample_pillar_outputs(self):
        """Create sample pillar outputs."""
        return {
            "content_pillar": {"files_parsed": 10},
            "insights_pillar": {"insights_generated": 5},
            "operations_pillar": {"sops_created": 3},
            "business_outcomes_pillar": {"roadmap_created": True}
        }
    
    @pytest.mark.asyncio
    async def test_service_initializes(self, mock_di_container, mock_platform_gateway):
        """Test service initializes correctly."""
        from backend.business_enablement.enabling_services.poc_generation_service.poc_generation_service import POCGenerationService
        
        service = POCGenerationService(
            service_name="POCGenerationService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "POCGenerationService"
        assert service.realm_name == "business_enablement"
        assert hasattr(service, 'poc_types')
        assert len(service.poc_types) > 0
    
    @pytest.mark.asyncio
    async def test_generate_poc_proposal_soa_api(self, poc_service, sample_pillar_outputs):
        """Test generate_poc_proposal SOA API works."""
        result = await poc_service.generate_poc_proposal(
            pillar_outputs=sample_pillar_outputs,
            poc_type="hybrid",
            options={}
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_generate_poc_roadmap_soa_api(self, poc_service, sample_pillar_outputs):
        """Test generate_poc_roadmap SOA API works."""
        result = await poc_service.generate_poc_roadmap(
            business_context={"pillar_outputs": sample_pillar_outputs},
            poc_type="hybrid"
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_analyze_poc_financials_soa_api(self, poc_service, sample_pillar_outputs):
        """Test analyze_poc_financials SOA API works."""
        result = await poc_service.analyze_poc_financials(
            business_context={"pillar_outputs": sample_pillar_outputs},
            poc_type="hybrid"
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_calculate_poc_metrics_soa_api(self, poc_service, sample_pillar_outputs):
        """Test calculate_poc_metrics SOA API works."""
        result = await poc_service.calculate_poc_metrics(
            business_context={"pillar_outputs": sample_pillar_outputs},
            poc_type="hybrid"
        )
        
        assert isinstance(result, dict)
        assert "success" in result

