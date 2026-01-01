#!/usr/bin/env python3
"""
Data Analyzer Service Tests

Tests for DataAnalyzerService enabling service in isolation.
Verifies service works before orchestrators use it.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.enabling_services]

class TestDataAnalyzerService:
    """Test DataAnalyzerService functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        container.get_abstraction = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_smart_city_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    async def data_analyzer_service(self, mock_di_container, mock_platform_gateway):
        """Create DataAnalyzerService instance."""
        from backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service import DataAnalyzerService
        
        service = DataAnalyzerService(
            service_name="DataAnalyzerService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        service.librarian.search_knowledge = AsyncMock(return_value={"results": []})
        service.librarian.semantic_search = AsyncMock(return_value={"results": []})
        service.data_steward = Mock()
        service.content_steward = Mock()
        service.curator = Mock()
        service.curator.register_service = AsyncMock(return_value=True)
        service.curator.discover_service = AsyncMock(return_value=None)
        
        
        # Mock Content Steward for store_document
        mock_content_steward = Mock()
        mock_content_steward.process_upload = AsyncMock(return_value={
            "uuid": "test_file_uuid_123",
            "file_id": "test_file_uuid_123",
            "metadata": {}
        })
        # Mock get_content_steward_api to return Content Steward
        service.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
        
        # Mock Data Steward for validate_data_quality and track_data_lineage
        mock_data_steward = Mock()
        mock_data_steward.validate_data_quality = AsyncMock(return_value={"status": "passed"})
        mock_data_steward.track_lineage = AsyncMock(return_value=True)
        service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        
        return service
    
    @pytest.mark.asyncio
    async def test_service_initializes(self, mock_di_container, mock_platform_gateway):
        """Test service initializes correctly."""
        from backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service import DataAnalyzerService
        
        service = DataAnalyzerService(
            service_name="DataAnalyzerService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "DataAnalyzerService"
        assert service.realm_name == "business_enablement"
        assert hasattr(service, 'supported_analyses')
        assert len(service.supported_analyses) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_data_soa_api(self, data_analyzer_service):
        """Test analyze_data SOA API works."""
        # Mock retrieve_document
        data_analyzer_service.retrieve_document = AsyncMock(return_value={
            "data": {"key": "value"},
            "metadata": {}
        })
        data_analyzer_service.validate_data_quality = AsyncMock(return_value={"status": "passed"})
        
        result = await data_analyzer_service.analyze_data(
            data_id="test_data_123",
            analysis_type="descriptive"
        )
        
        assert isinstance(result, dict)
        assert "results" in result or "analysis_id" in result
    
    @pytest.mark.asyncio
    async def test_categorize_content_soa_api(self, data_analyzer_service):
        """Test categorize_content SOA API works."""
        result = await data_analyzer_service.categorize_content(
            file_id="test_file_123",
            parsed_data={"content": "sample text"}
        )
        
        assert isinstance(result, dict)
        assert "domain" in result
    
    @pytest.mark.asyncio
    async def test_assess_content_quality_soa_api(self, data_analyzer_service):
        """Test assess_content_quality SOA API works."""
        result = await data_analyzer_service.assess_content_quality(
            file_id="test_file_123",
            parsed_data={"content": "sample text"}
        )
        
        assert isinstance(result, dict)
        assert "data_quality_score" in result or "completeness" in result
    
    @pytest.mark.asyncio
    async def test_generate_semantic_summary_soa_api(self, data_analyzer_service):
        """Test generate_semantic_summary SOA API works."""
        result = await data_analyzer_service.generate_semantic_summary(
            file_id="test_file_123",
            parsed_data={"content": "sample text"}
        )
        
        assert isinstance(result, dict)
        assert "business_context" in result or "key_insights" in result
    
    @pytest.mark.asyncio
    async def test_detect_domain_soa_api(self, data_analyzer_service):
        """Test detect_domain SOA API works."""
        result = await data_analyzer_service.detect_domain(
            parsed_data={"content": "sample text"}
        )
        
        assert isinstance(result, dict)
        assert "domain" in result
    
    @pytest.mark.asyncio
    async def test_assess_complexity_soa_api(self, data_analyzer_service):
        """Test assess_complexity SOA API works."""
        result = await data_analyzer_service.assess_complexity(
            parsed_data={"content": "sample text"}
        )
        
        assert isinstance(result, dict)
        assert "complexity" in result
    
    @pytest.mark.asyncio
    async def test_analyze_data_handles_unsupported_type(self, data_analyzer_service):
        """Test analyze_data handles unsupported analysis type gracefully."""
        result = await data_analyzer_service.analyze_data(
            data_id="test_data_123",
            analysis_type="unsupported_type"
        )
        
        assert result["success"] is False
        assert "unsupported" in result.get("message", "").lower()

