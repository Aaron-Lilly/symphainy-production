"""
Comprehensive unit tests for unstructured file parsing.

Tests:
- PDF files
- Word documents (docx)
- Text files
- Chunking logic
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.content
@pytest.mark.unstructured_parsing
@pytest.mark.fast
class TestUnstructuredParsing:
    """Test suite for unstructured file parsing."""
    
    @pytest.fixture
    def mock_file_parser_service(self):
        """Create mock FileParserService."""
        service = Mock()
        service.logger = Mock()
        service.platform_gateway = Mock()
        service.realm_name = "business_enablement"
        service.utilities_module = Mock()
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        return service
    
    @pytest.fixture
    def unstructured_parsing(self, mock_file_parser_service):
        """Create UnstructuredParsing instance."""
        from backend.content.services.file_parser_service.modules.unstructured_parsing import UnstructuredParsing
        return UnstructuredParsing(mock_file_parser_service)
    
    @pytest.fixture
    def sample_pdf_data(self):
        """Sample PDF file data (minimal valid PDF)."""
        # Minimal valid PDF header
        return b"%PDF-1.4\n"
    
    @pytest.fixture
    def sample_text_data(self):
        """Sample text file data."""
        return b"This is a sample text file.\n\nIt has multiple paragraphs.\n\nEach paragraph is separated by blank lines."
    
    @pytest.fixture
    def sample_docx_data(self):
        """Sample DOCX file data (minimal valid docx)."""
        # DOCX is a ZIP file, so minimal ZIP header
        return b"PK\x03\x04"
    
    @pytest.mark.asyncio
    async def test_parse_pdf_file(self, unstructured_parsing, mock_file_parser_service, sample_pdf_data):
        """Test parsing PDF file."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = "This is PDF content.\n\nIt has multiple paragraphs.\n\nWith text extraction."
        mock_result.metadata = {"page_count": 3, "table_count": 0}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=sample_pdf_data,
            file_type="pdf",
            filename="test.pdf"
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "unstructured"
        assert result["file_type"] == "pdf"
        assert "chunks" in result
        assert "content" in result
        assert len(result["chunks"]) > 0
        assert result["structure"]["chunk_count"] == len(result["chunks"])
    
    @pytest.mark.asyncio
    async def test_parse_text_file(self, unstructured_parsing, mock_file_parser_service, sample_text_data):
        """Test parsing text file."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_text_data.decode('utf-8')
        mock_result.metadata = {"page_count": 1, "table_count": 0}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=sample_text_data,
            file_type="txt",
            filename="test.txt"
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "unstructured"
        assert result["file_type"] == "txt"
        assert "chunks" in result
        assert len(result["chunks"]) > 0
    
    @pytest.mark.asyncio
    async def test_parse_docx_file(self, unstructured_parsing, mock_file_parser_service, sample_docx_data):
        """Test parsing DOCX file."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = "This is Word document content.\n\nWith multiple paragraphs.\n\nAnd sections."
        mock_result.metadata = {"page_count": 2, "table_count": 0}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="WordProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=sample_docx_data,
            file_type="docx",
            filename="test.docx"
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "unstructured"
        assert result["file_type"] == "docx"
        assert "chunks" in result
    
    @pytest.mark.asyncio
    async def test_chunking_with_custom_size(self, unstructured_parsing, mock_file_parser_service, sample_text_data):
        """Test chunking with custom chunk size."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        # Create long text content
        long_text = "This is a very long text. " * 100
        mock_result.success = True
        mock_result.text_content = long_text
        mock_result.metadata = {"page_count": 1}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        parse_options = {"chunk_size": 500}  # Custom chunk size
        
        result = await unstructured_parsing.parse(
            file_data=sample_text_data,
            file_type="txt",
            filename="test.txt",
            parse_options=parse_options
        )
        
        assert result["success"] is True
        assert "chunks" in result
        # Verify chunks are approximately the right size
        for chunk in result["chunks"]:
            assert chunk["char_count"] <= 500 * 1.5  # Allow some flexibility
    
    @pytest.mark.asyncio
    async def test_chunking_empty_text(self, unstructured_parsing, mock_file_parser_service):
        """Test chunking with empty text."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = ""
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=b"",
            file_type="txt",
            filename="test.txt"
        )
        
        assert result["success"] is True
        assert result["chunks"] == []
        assert result["structure"]["chunk_count"] == 0
    
    @pytest.mark.asyncio
    async def test_chunking_paragraph_splitting(self, unstructured_parsing, mock_file_parser_service):
        """Test that chunking splits by paragraphs correctly."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        # Text with clear paragraph breaks
        text_with_paragraphs = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        mock_result.success = True
        mock_result.text_content = text_with_paragraphs
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=text_with_paragraphs.encode('utf-8'),
            file_type="txt",
            filename="test.txt"
        )
        
        assert result["success"] is True
        assert len(result["chunks"]) > 0
        # Verify chunks contain paragraph content
        all_text = " ".join([chunk["text"] for chunk in result["chunks"]])
        assert "Paragraph one" in all_text
        assert "Paragraph two" in all_text
    
    @pytest.mark.asyncio
    async def test_parse_unsupported_file_type(self, unstructured_parsing, mock_file_parser_service):
        """Test parsing unsupported file type."""
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value=None)
        
        result = await unstructured_parsing.parse(
            file_data=b"test data",
            file_type="unknown",
            filename="test.unknown"
        )
        
        assert result["success"] is False
        assert result["error"] == "unsupported_file_type"
    
    @pytest.mark.asyncio
    async def test_parse_timeout(self, unstructured_parsing, mock_file_parser_service):
        """Test parsing timeout."""
        mock_abstraction = AsyncMock()
        mock_abstraction.parse_file = AsyncMock(side_effect=asyncio.TimeoutError())
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=b"test data",
            file_type="pdf",
            filename="test.pdf"
        )
        
        assert result["success"] is False
        assert result["error"] == "file_parsing_timeout"
    
    @pytest.mark.asyncio
    async def test_parse_abstraction_failure(self, unstructured_parsing, mock_file_parser_service):
        """Test parsing when abstraction returns failure."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "PDF parsing failed"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=b"test data",
            file_type="pdf",
            filename="test.pdf"
        )
        
        assert result["success"] is False
        assert "PDF parsing failed" in result["message"]




