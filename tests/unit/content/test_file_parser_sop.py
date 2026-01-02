"""
Comprehensive unit tests for SOP file parsing.

Tests:
- SOP document parsing (docx, pdf, txt)
- Section extraction
- Step/procedure extraction
- Role/responsibility extraction
- Dependency extraction
- Timeline/sequence extraction
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.content
@pytest.mark.sop_parsing
@pytest.mark.fast
class TestSOPParsing:
    """Test suite for SOP file parsing."""
    
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
    def sop_parsing(self, mock_file_parser_service):
        """Create SOPParsing instance."""
        from backend.content.services.file_parser_service.modules.sop_parsing import SOPParsing
        return SOPParsing(mock_file_parser_service)
    
    @pytest.fixture
    def sample_sop_text(self):
        """Sample SOP text content."""
        return """
TITLE: Customer Onboarding Procedure

SECTION 1: Initial Contact
Step 1: Receive customer inquiry
Step 2: Verify customer information
Role: Sales Representative
Responsibility: Initial customer contact

SECTION 2: Documentation
Step 1: Collect required documents
Step 2: Validate document completeness
Role: Documentation Specialist
Dependency: Section 1 completion

SECTION 3: Account Setup
Step 1: Create customer account
Step 2: Configure account settings
Step 3: Send welcome email
Timeline: Complete within 24 hours
Role: Account Administrator
"""
    
    @pytest.fixture
    def sample_pdf_data(self):
        """Sample PDF file data."""
        return b"%PDF-1.4\n"
    
    @pytest.fixture
    def sample_docx_data(self):
        """Sample DOCX file data."""
        return b"PK\x03\x04"
    
    @pytest.mark.asyncio
    async def test_parse_sop_docx(self, sop_parsing, mock_file_parser_service, sample_docx_data, sample_sop_text):
        """Test parsing SOP DOCX file."""
        # Mock abstraction for text extraction
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_sop_text
        mock_result.metadata = {"page_count": 3}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="WordProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=sample_docx_data,
            file_type="docx",
            filename="test_sop.docx",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "sop"
        assert result["file_type"] == "docx"
        assert "structure" in result
        assert "sections" in result["structure"]
    
    @pytest.mark.asyncio
    async def test_parse_sop_pdf(self, sop_parsing, mock_file_parser_service, sample_pdf_data, sample_sop_text):
        """Test parsing SOP PDF file."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_sop_text
        mock_result.metadata = {"page_count": 2}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="PdfProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=sample_pdf_data,
            file_type="pdf",
            filename="test_sop.pdf",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "sop"
        assert result["file_type"] == "pdf"
        assert "structure" in result
    
    @pytest.mark.asyncio
    async def test_parse_sop_txt(self, sop_parsing, mock_file_parser_service, sample_sop_text):
        """Test parsing SOP text file."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_sop_text
        mock_result.metadata = {"page_count": 1}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=sample_sop_text.encode('utf-8'),
            file_type="txt",
            filename="test_sop.txt",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "sop"
        assert result["file_type"] == "txt"
        assert "structure" in result
    
    @pytest.mark.asyncio
    async def test_sop_section_extraction(self, sop_parsing, mock_file_parser_service, sample_sop_text):
        """Test SOP section extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_sop_text
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=sample_sop_text.encode('utf-8'),
            file_type="txt",
            filename="test_sop.txt",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        structure = result["structure"]
        assert "sections" in structure
        assert len(structure["sections"]) > 0
        
        # Verify sections have headings
        for section in structure["sections"]:
            assert "heading" in section or "title" in section
    
    @pytest.mark.asyncio
    async def test_sop_step_extraction(self, sop_parsing, mock_file_parser_service, sample_sop_text):
        """Test SOP step/procedure extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_sop_text
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=sample_sop_text.encode('utf-8'),
            file_type="txt",
            filename="test_sop.txt",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        structure = result["structure"]
        
        # Verify steps are extracted
        steps_found = False
        for section in structure.get("sections", []):
            if "steps" in section or "procedures" in section:
                steps_found = True
                break
        assert steps_found or "steps" in structure or "procedures" in structure
    
    @pytest.mark.asyncio
    async def test_sop_role_extraction(self, sop_parsing, mock_file_parser_service, sample_sop_text):
        """Test SOP role/responsibility extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_sop_text
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=sample_sop_text.encode('utf-8'),
            file_type="txt",
            filename="test_sop.txt",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        structure = result["structure"]
        
        # Verify roles are extracted
        roles_found = False
        for section in structure.get("sections", []):
            if "roles" in section or "responsibilities" in section:
                roles_found = True
                break
        assert roles_found or "roles" in structure
    
    @pytest.mark.asyncio
    async def test_sop_dependency_extraction(self, sop_parsing, mock_file_parser_service, sample_sop_text):
        """Test SOP dependency extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_sop_text
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=sample_sop_text.encode('utf-8'),
            file_type="txt",
            filename="test_sop.txt",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        structure = result["structure"]
        
        # Verify dependencies are extracted (if present in text)
        # Dependencies may be in sections or at structure level
        assert "dependencies" in structure or any("dependencies" in section for section in structure.get("sections", []))
    
    @pytest.mark.asyncio
    async def test_sop_timeline_extraction(self, sop_parsing, mock_file_parser_service, sample_sop_text):
        """Test SOP timeline/sequence extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_sop_text
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=sample_sop_text.encode('utf-8'),
            file_type="txt",
            filename="test_sop.txt",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        structure = result["structure"]
        
        # Verify timeline/sequence is extracted
        assert "timeline" in structure or "sequence" in structure or any("timeline" in section for section in structure.get("sections", []))
    
    @pytest.mark.asyncio
    async def test_parse_unsupported_sop_type(self, sop_parsing, mock_file_parser_service):
        """Test parsing unsupported SOP file type."""
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value=None)
        
        result = await sop_parsing.parse(
            file_data=b"test data",
            file_type="unknown",
            filename="test.unknown",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is False
        assert result["error"] == "unsupported_file_type"
    
    @pytest.mark.asyncio
    async def test_sop_title_extraction(self, sop_parsing, mock_file_parser_service, sample_sop_text):
        """Test SOP title extraction."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = sample_sop_text
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=sample_sop_text.encode('utf-8'),
            file_type="txt",
            filename="test_sop.txt",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        structure = result["structure"]
        
        # Verify title is extracted
        assert "title" in structure or "name" in structure
    
    @pytest.mark.asyncio
    async def test_sop_empty_file(self, sop_parsing, mock_file_parser_service):
        """Test parsing empty SOP file."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.text_content = ""
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="TextProcessingAbstraction")
        
        result = await sop_parsing.parse(
            file_data=b"",
            file_type="txt",
            filename="test_sop.txt",
            parse_options={"is_sop": True}
        )
        
        assert result["success"] is True
        # Should handle empty file gracefully
        assert "structure" in result




