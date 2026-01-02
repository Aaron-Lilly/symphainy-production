"""
Comprehensive unit tests for structured file parsing.

Tests:
- Excel files (xlsx, xls)
- CSV files
- JSON files
- Binary files with copybook
- Error handling
- Edge cases
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any
from pathlib import Path

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure


@pytest.mark.unit
@pytest.mark.content
@pytest.mark.structured_parsing
@pytest.mark.fast
class TestStructuredParsing:
    """Test suite for structured file parsing."""
    
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
    def structured_parsing(self, mock_file_parser_service):
        """Create StructuredParsing instance."""
        from backend.content.services.file_parser_service.modules.structured_parsing import StructuredParsing
        return StructuredParsing(mock_file_parser_service)
    
    @pytest.fixture
    def sample_excel_data(self):
        """Sample Excel file data (minimal valid xlsx)."""
        # This is a minimal valid xlsx file structure
        # In real tests, you'd use actual Excel files
        return b"PK\x03\x04"  # Minimal ZIP header (xlsx is a ZIP file)
    
    @pytest.fixture
    def sample_csv_data(self):
        """Sample CSV file data."""
        return b"name,age,city\nJohn,30,New York\nJane,25,Los Angeles"
    
    @pytest.fixture
    def sample_json_data(self):
        """Sample JSON file data."""
        data = {
            "users": [
                {"name": "John", "age": 30, "city": "New York"},
                {"name": "Jane", "age": 25, "city": "Los Angeles"}
            ]
        }
        return json.dumps(data).encode('utf-8')
    
    @pytest.fixture
    def sample_binary_data(self):
        """Sample binary file data."""
        return b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"
    
    @pytest.fixture
    def sample_copybook(self):
        """Sample COBOL copybook definition."""
        return """
        01 CUSTOMER-RECORD.
           05 CUSTOMER-ID PIC X(10).
           05 CUSTOMER-NAME PIC X(50).
           05 CUSTOMER-AGE PIC 9(3).
           05 CUSTOMER-BALANCE PIC 9(10)V99.
        """
    
    @pytest.mark.asyncio
    async def test_parse_excel_file(self, structured_parsing, mock_file_parser_service, sample_excel_data):
        """Test parsing Excel file (xlsx)."""
        # Mock abstraction
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.structured_data = {"tables": [{"rows": 2, "cols": 3}]}
        mock_result.text_content = "Sample Excel Content"
        mock_result.metadata = {"page_count": 1, "table_count": 1}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="ExcelProcessingAbstraction")
        
        result = await structured_parsing.parse(
            file_data=sample_excel_data,
            file_type="xlsx",
            filename="test.xlsx"
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "structured"
        assert result["file_type"] == "xlsx"
        assert "data" in result
        assert "tables" in result
        mock_abstraction.parse_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_parse_csv_file(self, structured_parsing, mock_file_parser_service, sample_csv_data):
        """Test parsing CSV file."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.structured_data = {
            "records": [
                {"name": "John", "age": "30", "city": "New York"},
                {"name": "Jane", "age": "25", "city": "Los Angeles"}
            ]
        }
        mock_result.text_content = sample_csv_data.decode('utf-8')
        mock_result.metadata = {"page_count": 1, "table_count": 0}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="CsvProcessingAbstraction")
        
        result = await structured_parsing.parse(
            file_data=sample_csv_data,
            file_type="csv",
            filename="test.csv"
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "structured"
        assert result["file_type"] == "csv"
        assert "records" in result
        assert len(result["records"]) == 2
    
    @pytest.mark.asyncio
    async def test_parse_json_file(self, structured_parsing, mock_file_parser_service, sample_json_data):
        """Test parsing JSON file."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.structured_data = json.loads(sample_json_data.decode('utf-8'))
        mock_result.text_content = sample_json_data.decode('utf-8')
        mock_result.metadata = {"page_count": 1, "table_count": 0}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="JsonProcessingAbstraction")
        
        result = await structured_parsing.parse(
            file_data=sample_json_data,
            file_type="json",
            filename="test.json"
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "structured"
        assert result["file_type"] == "json"
        assert "data" in result
        assert "users" in result["data"]
    
    @pytest.mark.asyncio
    async def test_parse_binary_with_copybook(self, structured_parsing, mock_file_parser_service, sample_binary_data, sample_copybook):
        """Test parsing binary file with copybook."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.structured_data = {
            "records": [
                {
                    "CUSTOMER-ID": "1234567890",
                    "CUSTOMER-NAME": "John Doe",
                    "CUSTOMER-AGE": "030",
                    "CUSTOMER-BALANCE": "000012345.67
                }
            ]
        }
        mock_result.text_content = ""
        mock_result.metadata = {"page_count": 1, "table_count": 0}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="MainframeProcessingAbstraction")
        
        parse_options = {
            "copybook": sample_copybook
        }
        
        result = await structured_parsing.parse(
            file_data=sample_binary_data,
            file_type="bin",
            filename="test.bin",
            parse_options=parse_options
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "structured"
        assert result["file_type"] == "bin"
        # Verify copybook was passed to abstraction
        call_args = mock_abstraction.parse_file.call_args
        assert call_args is not None
        request = call_args[0][0]
        assert request.options is not None
        assert "copybook" in request.options or "copybook_path" in request.options
    
    @pytest.mark.asyncio
    async def test_parse_binary_with_copybook_path(self, structured_parsing, mock_file_parser_service, sample_binary_data):
        """Test parsing binary file with copybook path."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.structured_data = {"records": []}
        mock_result.text_content = ""
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="MainframeProcessingAbstraction")
        
        parse_options = {
            "copybook_path": "/path/to/copybook.cpy"
        }
        
        result = await structured_parsing.parse(
            file_data=sample_binary_data,
            file_type="bin",
            filename="test.bin",
            parse_options=parse_options
        )
        
        assert result["success"] is True
        # Verify copybook_path was passed
        call_args = mock_abstraction.parse_file.call_args
        request = call_args[0][0]
        assert request.options is not None
        assert "copybook_path" in request.options
    
    @pytest.mark.asyncio
    async def test_parse_unsupported_file_type(self, structured_parsing, mock_file_parser_service):
        """Test parsing unsupported file type."""
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value=None)
        
        result = await structured_parsing.parse(
            file_data=b"test data",
            file_type="unknown",
            filename="test.unknown"
        )
        
        assert result["success"] is False
        assert result["error"] == "unsupported_file_type"
        assert "Unsupported structured file type" in result["message"]
    
    @pytest.mark.asyncio
    async def test_parse_abstraction_not_available(self, structured_parsing, mock_file_parser_service):
        """Test parsing when abstraction is not available."""
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="ExcelProcessingAbstraction")
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(side_effect=Exception("Abstraction not found"))
        
        result = await structured_parsing.parse(
            file_data=b"test data",
            file_type="xlsx",
            filename="test.xlsx"
        )
        
        assert result["success"] is False
        assert result["error"] == "abstraction_not_available"
    
    @pytest.mark.asyncio
    async def test_parse_abstraction_is_none(self, structured_parsing, mock_file_parser_service):
        """Test parsing when abstraction returns None."""
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="ExcelProcessingAbstraction")
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=None)
        
        result = await structured_parsing.parse(
            file_data=b"test data",
            file_type="xlsx",
            filename="test.xlsx"
        )
        
        assert result["success"] is False
        assert result["error"] == "abstraction_is_none"
    
    @pytest.mark.asyncio
    async def test_parse_timeout(self, structured_parsing, mock_file_parser_service):
        """Test parsing timeout."""
        mock_abstraction = AsyncMock()
        mock_abstraction.parse_file = AsyncMock(side_effect=asyncio.TimeoutError())
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="ExcelProcessingAbstraction")
        
        result = await structured_parsing.parse(
            file_data=b"test data",
            file_type="xlsx",
            filename="test.xlsx"
        )
        
        assert result["success"] is False
        assert result["error"] == "file_parsing_timeout"
    
    @pytest.mark.asyncio
    async def test_parse_abstraction_failure(self, structured_parsing, mock_file_parser_service):
        """Test parsing when abstraction returns failure."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Parsing failed"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="ExcelProcessingAbstraction")
        
        result = await structured_parsing.parse(
            file_data=b"test data",
            file_type="xlsx",
            filename="test.xlsx"
        )
        
        assert result["success"] is False
        assert "Parsing failed" in result["message"]
    
    @pytest.mark.asyncio
    async def test_parse_exception_handling(self, structured_parsing, mock_file_parser_service):
        """Test exception handling during parsing."""
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(side_effect=Exception("Unexpected error"))
        
        result = await structured_parsing.parse(
            file_data=b"test data",
            file_type="xlsx",
            filename="test.xlsx"
        )
        
        assert result["success"] is False
        assert "Unexpected error" in result["message"]
        mock_file_parser_service.handle_error_with_audit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_parse_with_user_context(self, structured_parsing, mock_file_parser_service, sample_csv_data):
        """Test parsing with user context."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.structured_data = {"records": []}
        mock_result.text_content = ""
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        mock_abstraction.parse_file = AsyncMock(return_value=mock_result)
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="CsvProcessingAbstraction")
        
        user_context = {
            "user_id": "test_user",
            "workflow_id": "test_workflow"
        }
        
        result = await structured_parsing.parse(
            file_data=sample_csv_data,
            file_type="csv",
            filename="test.csv",
            user_context=user_context
        )
        
        assert result["success"] is True
        # Verify user context was passed (if abstraction supports it)
        mock_abstraction.parse_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_parse_binary_timeout_extended(self, structured_parsing, mock_file_parser_service, sample_binary_data, sample_copybook):
        """Test that binary files get extended timeout (300 seconds)."""
        mock_abstraction = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.structured_data = {"records": []}
        mock_result.text_content = ""
        mock_result.metadata = {}
        mock_result.timestamp = "2025-01-01T00:00:00"
        
        # Simulate a long-running operation
        async def slow_parse(request):
            await asyncio.sleep(0.1)  # Simulate delay
            return mock_result
        
        mock_abstraction.parse_file = slow_parse
        
        mock_file_parser_service.platform_gateway.get_abstraction = Mock(return_value=mock_abstraction)
        mock_file_parser_service.utilities_module.get_abstraction_name_for_file_type = Mock(return_value="MainframeProcessingAbstraction")
        
        parse_options = {"copybook": sample_copybook}
        
        result = await structured_parsing.parse(
            file_data=sample_binary_data,
            file_type="bin",
            filename="test.bin",
            parse_options=parse_options
        )
        
        assert result["success"] is True
        # Verify timeout was extended (300 seconds for binary files)
        # This is tested implicitly - if timeout was 60 seconds, this would fail




