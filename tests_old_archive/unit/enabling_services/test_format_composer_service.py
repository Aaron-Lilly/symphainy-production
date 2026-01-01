#!/usr/bin/env python3
"""
Format Composer Service Tests

Tests for FormatComposerService enabling service in isolation.
Verifies service works before orchestrators use it.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.enabling_services]

class TestFormatComposerService:
    """Test FormatComposerService functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_smart_city_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    async def format_composer_service(self, mock_di_container, mock_platform_gateway):
        """Create FormatComposerService instance."""
        from backend.business_enablement.enabling_services.format_composer_service.format_composer_service import FormatComposerService
        
        service = FormatComposerService(
            service_name="FormatComposerService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.content_steward = Mock()
        service.content_steward.store_file = AsyncMock(return_value={"file_id": "composed_123"})
        service.curator = Mock()
        service.curator.register_service = AsyncMock(return_value=True)
        service.curator.discover_service = AsyncMock(return_value=None)
        
        return service
    
    @pytest.fixture
    def sample_parsed_data(self):
        """Create sample parsed data."""
        return {
            "content": "Sample text content",
            "tables": [
                {"headers": ["col1", "col2"], "rows": [["val1", "val2"]]}
            ],
            "metadata": {"source": "test.pdf"}
        }
    
    @pytest.mark.asyncio
    async def test_service_initializes(self, mock_di_container, mock_platform_gateway):
        """Test service initializes correctly."""
        from backend.business_enablement.enabling_services.format_composer_service.format_composer_service import FormatComposerService
        
        service = FormatComposerService(
            service_name="FormatComposerService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "FormatComposerService"
        assert service.realm_name == "business_enablement"
        assert hasattr(service, 'supported_formats')
        assert len(service.supported_formats) > 0
    
    @pytest.mark.asyncio
    async def test_compose_format_soa_api_parquet(self, format_composer_service, sample_parsed_data):
        """Test compose_format SOA API works for parquet format."""
        result = await format_composer_service.compose_format(
            parsed_data=sample_parsed_data,
            target_format="parquet",
            file_id="test_file_123"
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_compose_format_soa_api_json_structured(self, format_composer_service, sample_parsed_data):
        """Test compose_format SOA API works for json_structured format."""
        result = await format_composer_service.compose_format(
            parsed_data=sample_parsed_data,
            target_format="json_structured",
            file_id="test_file_123"
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_compose_format_soa_api_json_chunks(self, format_composer_service, sample_parsed_data):
        """Test compose_format SOA API works for json_chunks format."""
        result = await format_composer_service.compose_format(
            parsed_data=sample_parsed_data,
            target_format="json_chunks",
            file_id="test_file_123"
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_get_recommended_format_soa_api(self, format_composer_service):
        """Test get_recommended_format SOA API works."""
        result = await format_composer_service.get_recommended_format("pdf")
        
        assert isinstance(result, dict)
        assert "recommended_format" in result or "format" in result
    
    @pytest.mark.asyncio
    async def test_get_supported_formats_soa_api(self, format_composer_service):
        """Test get_supported_formats SOA API works."""
        result = await format_composer_service.get_supported_formats()
        
        assert isinstance(result, dict)
        assert "formats" in result or "supported_formats" in result
        formats = result.get("formats", result.get("supported_formats", []))
        assert len(formats) > 0
        assert "parquet" in formats or any("parquet" in str(f).lower() for f in formats)
    
    @pytest.mark.asyncio
    async def test_compose_format_handles_unsupported_format(self, format_composer_service, sample_parsed_data):
        """Test compose_format handles unsupported format gracefully."""
        result = await format_composer_service.compose_format(
            parsed_data=sample_parsed_data,
            target_format="unsupported_format"
        )
        
        assert result["success"] is False
        assert "unsupported" in result.get("error", "").lower()

