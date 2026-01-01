#!/usr/bin/env python3
"""
File Parser Service Tests

Tests for FileParserService enabling service in isolation.
Verifies service works before orchestrators use it.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.enabling_services]

class TestFileParserService:
    """Test FileParserService functionality."""
    
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
    async def file_parser_service(self, mock_di_container, mock_platform_gateway):
        """Create FileParserService instance."""
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        service.librarian.search_knowledge = AsyncMock(return_value={"results": []})
        service.content_steward = Mock()
        service.content_steward.retrieve_file = AsyncMock(return_value={
            "file_id": "test_file_123",
            "filename": "test.pdf",
            "data": b"test file content",
            "metadata": {"size": 100, "type": "application/pdf"}
        })
        service.data_steward = Mock()
        service.curator = Mock()
        service.curator.register_service = AsyncMock(return_value=True)
        service.curator.discover_service = AsyncMock(return_value=None)
        
        return service
    
    @pytest.mark.asyncio
    async def test_service_initializes(self, mock_di_container, mock_platform_gateway):
        """Test service initializes correctly."""
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "FileParserService"
        assert service.realm_name == "business_enablement"
        assert hasattr(service, 'supported_formats')
        assert len(service.supported_formats) > 0
    
    @pytest.mark.asyncio
    async def test_parse_file_soa_api(self, file_parser_service):
        """Test parse_file SOA API works."""
        result = await file_parser_service.parse_file(
            file_id="test_file_123",
            parse_options={}
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_detect_file_type_soa_api(self, file_parser_service):
        """Test detect_file_type SOA API works."""
        result = await file_parser_service.detect_file_type("test_file_123")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_extract_content_soa_api(self, file_parser_service):
        """Test extract_content SOA API works."""
        result = await file_parser_service.extract_content("test_file_123")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_extract_metadata_soa_api(self, file_parser_service):
        """Test extract_metadata SOA API works."""
        result = await file_parser_service.extract_metadata("test_file_123")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_get_supported_formats_soa_api(self, file_parser_service):
        """Test get_supported_formats SOA API works."""
        result = await file_parser_service.get_supported_formats()
        
        assert isinstance(result, dict)
        assert "formats" in result or "supported_formats" in result
        assert len(result.get("formats", result.get("supported_formats", []))) > 0
    
    @pytest.mark.asyncio
    async def test_parse_file_handles_missing_file(self, file_parser_service):
        """Test parse_file handles missing file gracefully."""
        file_parser_service.content_steward.retrieve_file = AsyncMock(return_value=None)
        
        result = await file_parser_service.parse_file("missing_file")
        
        assert result["success"] is False
        assert "not found" in result.get("message", "").lower()
    
    @pytest.mark.asyncio
    async def test_retrieve_document_uses_content_steward(self, file_parser_service):
        """Test retrieve_document uses Content Steward SOA API."""
        result = await file_parser_service.retrieve_document("test_file_123")
        
        assert result is not None
        file_parser_service.content_steward.retrieve_file.assert_called_once_with("test_file_123")

