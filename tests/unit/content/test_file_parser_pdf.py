"""
Comprehensive unit tests for PDF file parsing (special focus).

Tests:
- PDF table extraction
- PDF text extraction
- PDF structured content (forms, invoices)
- PDF unstructured content (documents, articles)
- PDF hybrid content (both tables and text)
- PDF metadata extraction
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.content
@pytest.mark.pdf_parsing
@pytest.mark.fast
class TestPDFParsing:
    """Test suite for PDF file parsing with special focus."""
    
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
        """Create UnstructuredParsing instance (PDF uses unstructured parsing)."""
        from backend.content.services.file_parser_service.modules.unstructured_parsing import UnstructuredParsing
        return UnstructuredParsing(mock_file_parser_service)
    
    @pytest.fixture
    def sample_pdf_data(self):
        """Sample PDF file data."""
        return b"%PDF-1.4\n"
    
    @pytest.mark.asyncio
    async def test_parse_pdf_structured_content(self, unstructured_parsing, mock_file_parser_service, sample_pdf_data):
        """Test parsing PDF with structured content (forms, invoices)."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        # Structured content with tables
        mock_result.text_content = "Invoice\n\nTable:\nItem | Price\nWidget | $10.00"
        mock_result.structured_data = {
            "tables": [
                {
                    "rows": [
                        ["Item", "Price"],
                        ["Widget", "$10.00"]
                    ]
                }
            ]
        }
        mock_result.metadata = {"page_count": 1, "table_count": 1}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        parse_options = {"content_type": "structured"}
        
        result = await unstructured_parsing.parse(
            file_data=sample_pdf_data,
            file_type="pdf",
            filename="invoice.pdf",
            parse_options=parse_options
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "unstructured"
        assert result["file_type"] == "pdf"
        assert "chunks" in result
        assert "content" in result
    
    @pytest.mark.asyncio
    async def test_parse_pdf_unstructured_content(self, unstructured_parsing, mock_file_parser_service, sample_pdf_data):
        """Test parsing PDF with unstructured content (documents, articles)."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        # Unstructured content (article/document)
        article_text = """
        Introduction
        
        This is a comprehensive article about PDF processing.
        
        Main Content
        
        PDF files can contain various types of content including text, images, and tables.
        
        Conclusion
        
        Proper parsing requires understanding the content type.
        """
        mock_result.text_content = article_text
        mock_result.metadata = {"page_count": 3, "table_count": 0}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        parse_options = {"content_type": "unstructured"}
        
        result = await unstructured_parsing.parse(
            file_data=sample_pdf_data,
            file_type="pdf",
            filename="article.pdf",
            parse_options=parse_options
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "unstructured"
        assert "chunks" in result
        assert len(result["chunks"]) > 0
    
    @pytest.mark.asyncio
    async def test_parse_pdf_hybrid_content(self, unstructured_parsing, mock_file_parser_service, sample_pdf_data):
        """Test parsing PDF with hybrid content (both tables and text)."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        # Hybrid content (document with tables)
        hybrid_text = """
        Report Title
        
        This report contains both text and tables.
        
        Table 1:
        Column A | Column B
        Value 1  | Value 2
        
        Additional text content follows the table.
        """
        mock_result.text_content = hybrid_text
        mock_result.structured_data = {
            "tables": [
                {
                    "rows": [
                        ["Column A", "Column B"],
                        ["Value 1", "Value 2"]
                    ]
                }
            ]
        }
        mock_result.metadata = {"page_count": 2, "table_count": 1}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        parse_options = {"content_type": "hybrid"}
        
        result = await unstructured_parsing.parse(
            file_data=sample_pdf_data,
            file_type="pdf",
            filename="report.pdf",
            parse_options=parse_options
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "unstructured"
        assert "chunks" in result
        assert len(result["chunks"]) > 0
    
    @pytest.mark.asyncio
    async def test_parse_pdf_table_extraction(self, unstructured_parsing, mock_file_parser_service, sample_pdf_data):
        """Test PDF table extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = "Table content extracted"
        mock_result.structured_data = {
            "tables": [
                {
                    "rows": [
                        ["Header 1", "Header 2", "Header 3"],
                        ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
                        ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"]
                    ],
                    "columns": 3,
                    "rows": 3
                }
            ]
        }
        mock_result.metadata = {"page_count": 1, "table_count": 1}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=sample_pdf_data,
            file_type="pdf",
            filename="table.pdf",
            parse_options={"content_type": "structured"}
        )
        
        assert result["success"] is True
        # Verify table extraction (if abstraction provides structured_data)
        assert "content" in result
    
    @pytest.mark.asyncio
    async def test_parse_pdf_text_extraction(self, unstructured_parsing, mock_file_parser_service, sample_pdf_data):
        """Test PDF text extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        extracted_text = "This is extracted text from a PDF document.\n\nIt contains multiple paragraphs.\n\nEach paragraph is separated by blank lines."
        mock_result.text_content = extracted_text
        mock_result.metadata = {"page_count": 2, "table_count": 0}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=sample_pdf_data,
            file_type="pdf",
            filename="document.pdf",
            parse_options={"content_type": "unstructured"}
        )
        
        assert result["success"] is True
        assert "content" in result
        assert result["content"] == extracted_text
        assert len(result["chunks"]) > 0
    
    @pytest.mark.asyncio
    async def test_parse_pdf_metadata_extraction(self, unstructured_parsing, mock_file_parser_service, sample_pdf_data):
        """Test PDF metadata extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = "PDF content"
        mock_result.metadata = {
            "page_count": 5,
            "table_count": 2,
            "author": "Test Author",
            "title": "Test PDF",
            "creation_date": "2025-01-01"
        }
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
        assert "metadata" in result
        assert result["metadata"]["page_count"] == 5
        assert result["structure"]["page_count"] == 5
    
    @pytest.mark.asyncio
    async def test_parse_pdf_page_count(self, unstructured_parsing, mock_file_parser_service, sample_pdf_data):
        """Test PDF page count extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = "Multi-page PDF content"
        mock_result.metadata = {"page_count": 10, "table_count": 0}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=sample_pdf_data,
            file_type="pdf",
            filename="multipage.pdf"
        )
        
        assert result["success"] is True
        assert result["structure"]["page_count"] == 10
        assert result["metadata"]["page_count"] == 10
    
    @pytest.mark.asyncio
    async def test_parse_pdf_default_strategy(self, unstructured_parsing, mock_file_parser_service, sample_pdf_data):
        """Test PDF parsing with default strategy (hybrid)."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = "PDF content with both text and tables"
        mock_result.metadata = {"page_count": 1, "table_count": 1}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        # No content_type specified - should default to hybrid
        result = await unstructured_parsing.parse(
            file_data=sample_pdf_data,
            file_type="pdf",
            filename="default.pdf"
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "unstructured"
        assert "chunks" in result
    
    @pytest.mark.asyncio
    async def test_parse_pdf_invalid_file(self, unstructured_parsing, mock_file_parser_service):
        """Test parsing invalid PDF file."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Invalid PDF format"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=b"invalid pdf data",
            file_type="pdf",
            filename="invalid.pdf"
        )
        
        assert result["success"] is False
        assert "Invalid PDF format" in result["message"]
    
    @pytest.mark.asyncio
    async def test_parse_pdf_timeout(self, unstructured_parsing, mock_file_parser_service):
        """Test PDF parsing timeout."""
        mock_abstraction = AsyncMock()
        mock_abstraction.parse_file = AsyncMock(side_effect=asyncio.TimeoutError())
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        result = await unstructured_parsing.parse(
            file_data=b"%PDF-1.4\n",
            file_type="pdf",
            filename="timeout.pdf"
        )
        
        assert result["success"] is False
        assert result["error"] == "file_parsing_timeout"



