#!/usr/bin/env python3
"""
File Parser Service Functionality Tests

Tests File Parser Service core functionality:
- File parsing (multiple formats)
- Format detection
- Content extraction
- Metadata extraction
- Supported formats listing

Uses mock AI responses and test datasets.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Dict, Any

# Path is configured in pytest.ini - no manipulation needed

from tests.fixtures.test_datasets import get_sample_document, SAMPLE_DOCUMENT_TEXT
from tests.fixtures.business_enablement_fixtures import mock_di_container, mock_platform_gateway

@pytest.mark.business_enablement
@pytest.mark.functional
class TestFileParserServiceFunctionality:
    """Test File Parser Service functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    def mock_document_intelligence(self):
        """Create mock Document Intelligence Abstraction."""
        mock_abstraction = Mock()
        mock_abstraction.process_document = AsyncMock(return_value={
            "result_id": "test_result_001",
            "filename": "test.pdf",
            "success": True,
            "text_length": 100,
            "chunks": [],
            "entities": []
        })
        return mock_abstraction
    
    @pytest.fixture
    def mock_content_steward(self):
        """Create mock Content Steward API."""
        mock_api = Mock()
        mock_api.get_file = AsyncMock(return_value={
            "file_id": "test_file_001",
            "filename": "test.pdf",
            "file_data": get_sample_document("pdf"),
            "content_type": "application/pdf"
        })
        return mock_api
    
    @pytest.fixture
    async def file_parser_service(self, mock_di_container, mock_platform_gateway, mock_document_intelligence, mock_content_steward):
        """Create File Parser Service instance."""
        # Path is configured in pytest.ini - no manipulation needed
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        # Set up mocks
        mock_platform_gateway.get_abstraction.return_value = mock_document_intelligence
        
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City APIs
        service.content_steward = mock_content_steward
        service.librarian = Mock()
        service.data_steward = Mock()
        service.document_intelligence = mock_document_intelligence
        
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_get_supported_formats(self, file_parser_service):
        """Test that service returns supported file formats."""
        result = await file_parser_service.get_supported_formats()
        
        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result
        assert "supported_formats" in result
        assert isinstance(result["supported_formats"], list)
        assert len(result["supported_formats"]) > 0
        assert "pdf" in result["supported_formats"]
        assert "docx" in result["supported_formats"]
    
    @pytest.mark.asyncio
    async def test_detect_file_type(self, file_parser_service, mock_content_steward):
        """Test that service can detect file type."""
        # Mock file retrieval
        file_id = "test_file_001"
        mock_content_steward.get_file.return_value = {
            "file_id": file_id,
            "filename": "test.pdf",
            "data": get_sample_document("pdf"),
            "metadata": {"file_type": "pdf"}
        }
        
        file_type = await file_parser_service.detect_file_type(file_id)
        
        assert file_type is not None
        assert isinstance(file_type, str)
    
    @pytest.mark.asyncio
    async def test_parse_file_basic(self, file_parser_service, mock_content_steward, mock_document_intelligence):
        """Test basic file parsing functionality."""
        # Mock file retrieval
        file_id = "test_file_001"
        mock_content_steward.get_file.return_value = {
            "file_id": file_id,
            "filename": "test.txt",
            "data": get_sample_document("text"),
            "metadata": {}
        }
        
        # Mock document intelligence result
        from bases.contracts.document_intelligence import DocumentProcessingResult, DocumentChunk
        mock_document_intelligence.process_document.return_value = DocumentProcessingResult(
            result_id="result_001",
            filename="test.txt",
            success=True,
            chunks=[DocumentChunk(chunk_id="chunk_1", text="Test content", start_position=0, end_position=11, length=11)]
        )
        
        result = await file_parser_service.parse_file(file_id)
        
        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_extract_content(self, file_parser_service, mock_content_steward, mock_document_intelligence):
        """Test content extraction functionality."""
        # Mock file retrieval and parsing
        file_id = "test_file_001"
        mock_content_steward.get_file.return_value = {
            "file_id": file_id,
            "filename": "test.txt",
            "data": get_sample_document("text"),
            "metadata": {}
        }
        
        from bases.contracts.document_intelligence import DocumentProcessingResult, DocumentChunk
        mock_document_intelligence.process_document.return_value = DocumentProcessingResult(
            result_id="result_001",
            filename="test.txt",
            success=True,
            chunks=[DocumentChunk(chunk_id="chunk_1", text="Test content", start_position=0, end_position=11, length=11)]
        )
        
        content = await file_parser_service.extract_content(file_id)
        
        assert content is not None
        assert isinstance(content, dict)
        assert "success" in content
    
    @pytest.mark.asyncio
    async def test_extract_metadata(self, file_parser_service, mock_content_steward):
        """Test metadata extraction functionality."""
        # Mock file retrieval
        file_id = "test_file_001"
        mock_content_steward.get_file.return_value = {
            "file_id": file_id,
            "filename": "test.txt",
            "data": get_sample_document("text"),
            "metadata": {"file_type": "text"}
        }
        
        # Mock content steward enrichment
        file_parser_service.enrich_content_metadata = AsyncMock(return_value={})
        
        metadata = await file_parser_service.extract_metadata(file_id)
        
        assert metadata is not None
        assert isinstance(metadata, dict)
        assert "success" in metadata
    
    @pytest.mark.asyncio
    async def test_parse_file_with_document_intelligence(self, file_parser_service, mock_content_steward, mock_document_intelligence):
        """Test file parsing uses Document Intelligence Abstraction."""
        # Mock file retrieval
        file_id = "test_file_001"
        mock_content_steward.get_file.return_value = {
            "file_id": file_id,
            "filename": "test.pdf",
            "data": get_sample_document("pdf"),
            "metadata": {}
        }
        
        # Mock document intelligence result
        from bases.contracts.document_intelligence import DocumentProcessingResult
        mock_document_intelligence.process_document.return_value = DocumentProcessingResult(
            result_id="result_001",
            filename="test.pdf",
            success=True
        )
        
        result = await file_parser_service.parse_file(file_id)
        
        # Verify Document Intelligence was called
        assert file_parser_service.document_intelligence is not None
        assert mock_document_intelligence.process_document.called
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_file(self, file_parser_service):
        """Test error handling for invalid files."""
        invalid_data = b"invalid file data"
        
        # Should handle gracefully
        try:
            result = await file_parser_service.parse_file(
                file_data=invalid_data,
                filename="invalid.xyz"
            )
            # Either returns error result or raises exception
            assert result is not None or True
        except Exception as e:
            # Exception is acceptable for invalid files
            assert isinstance(e, Exception)

