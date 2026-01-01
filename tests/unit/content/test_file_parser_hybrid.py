"""
Comprehensive unit tests for hybrid file parsing.

Tests:
- Hybrid parsing (structured + unstructured)
- 3 JSON file output (structured, unstructured, correlation map)
- Correlation map generation
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.content
@pytest.mark.hybrid_parsing
@pytest.mark.fast
class TestHybridParsing:
    """Test suite for hybrid file parsing."""
    
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
    def hybrid_parsing(self, mock_file_parser_service):
        """Create HybridParsing instance."""
        from backend.content.services.file_parser_service.modules.hybrid_parsing import HybridParsing
        return HybridParsing(mock_file_parser_service)
    
    @pytest.mark.asyncio
    async def test_parse_hybrid_file(self, hybrid_parsing, mock_file_parser_service):
        """Test parsing hybrid file (structured + unstructured)."""
        # Mock structured parsing result
        structured_result = {
            "success": True,
            "parsing_type": "structured",
            "data": {"tables": [{"id": 1, "name": "Table1"}]},
            "tables": [{"id": 1, "name": "Table1"}],
            "records": [{"id": 1, "value": "test"}],
            "metadata": {"page_count": 1, "table_count": 1}
        }
        
        # Mock unstructured parsing result
        unstructured_result = {
            "success": True,
            "parsing_type": "unstructured",
            "chunks": [
                {"text": "Chunk 1", "chunk_index": 0},
                {"text": "Chunk 2", "chunk_index": 1}
            ],
            "metadata": {"page_count": 1}
        }
        
        # Mock both parsing modules
        with patch.object(hybrid_parsing.service, 'utilities_module') as mock_utils:
            with patch('backend.content.services.file_parser_service.modules.hybrid_parsing.StructuredParsing') as mock_structured:
                with patch('backend.content.services.file_parser_service.modules.hybrid_parsing.UnstructuredParsing') as mock_unstructured:
                    mock_structured_instance = Mock()
                    mock_structured_instance.parse = AsyncMock(return_value=structured_result)
                    mock_structured.return_value = mock_structured_instance
                    
                    mock_unstructured_instance = Mock()
                    mock_unstructured_instance.parse = AsyncMock(return_value=unstructured_result)
                    mock_unstructured.return_value = mock_unstructured_instance
                    
                    result = await hybrid_parsing.parse(
                        file_data=b"test data",
                        file_type="excel_with_text",
                        filename="test.xlsx"
                    )
        
        assert result["success"] is True
        assert result["parsing_type"] == "hybrid"
        assert "parsed_files" in result
        assert "structured" in result["parsed_files"]
        assert "unstructured" in result["parsed_files"]
        assert "correlation_map" in result["parsed_files"]
    
    @pytest.mark.asyncio
    async def test_hybrid_parsing_structured_failure(self, hybrid_parsing, mock_file_parser_service):
        """Test hybrid parsing when structured parsing fails."""
        structured_result = {
            "success": False,
            "error": "Structured parsing failed"
        }
        
        with patch('backend.content.services.file_parser_service.modules.hybrid_parsing.StructuredParsing') as mock_structured:
            mock_structured_instance = Mock()
            mock_structured_instance.parse = AsyncMock(return_value=structured_result)
            mock_structured.return_value = mock_structured_instance
            
            result = await hybrid_parsing.parse(
                file_data=b"test data",
                file_type="excel_with_text",
                filename="test.xlsx"
            )
        
        assert result["success"] is False
        assert "Structured parsing failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_hybrid_parsing_unstructured_failure(self, hybrid_parsing, mock_file_parser_service):
        """Test hybrid parsing when unstructured parsing fails."""
        structured_result = {
            "success": True,
            "data": {"tables": []},
            "tables": [],
            "records": [],
            "metadata": {}
        }
        
        unstructured_result = {
            "success": False,
            "error": "Unstructured parsing failed"
        }
        
        with patch('backend.content.services.file_parser_service.modules.hybrid_parsing.StructuredParsing') as mock_structured:
            with patch('backend.content.services.file_parser_service.modules.hybrid_parsing.UnstructuredParsing') as mock_unstructured:
                mock_structured_instance = Mock()
                mock_structured_instance.parse = AsyncMock(return_value=structured_result)
                mock_structured.return_value = mock_structured_instance
                
                mock_unstructured_instance = Mock()
                mock_unstructured_instance.parse = AsyncMock(return_value=unstructured_result)
                mock_unstructured.return_value = mock_unstructured_instance
                
                result = await hybrid_parsing.parse(
                    file_data=b"test data",
                    file_type="excel_with_text",
                    filename="test.xlsx"
                )
        
        assert result["success"] is False
        assert "Unstructured parsing failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_correlation_map_generation(self, hybrid_parsing, mock_file_parser_service):
        """Test correlation map generation."""
        structured_result = {
            "success": True,
            "tables": [{"id": 1}, {"id": 2}],
            "records": [{"id": 1}, {"id": 2}],
            "metadata": {"page_count": 2}
        }
        
        unstructured_result = {
            "success": True,
            "chunks": [
                {"text": "Chunk 1", "chunk_index": 0},
                {"text": "Chunk 2", "chunk_index": 1},
                {"text": "Chunk 3", "chunk_index": 2}
            ],
            "metadata": {"page_count": 2}
        }
        
        correlation_map = await hybrid_parsing._create_correlation_map(
            structured_result=structured_result,
            unstructured_result=unstructured_result
        )
        
        assert "structured_to_unstructured" in correlation_map
        assert "unstructured_to_structured" in correlation_map
        assert "confidence_scores" in correlation_map
        assert "metadata_correlations" in correlation_map
        
        # Verify mappings exist
        assert len(correlation_map["structured_to_unstructured"]) > 0
        assert len(correlation_map["unstructured_to_structured"]) > 0
    
    @pytest.mark.asyncio
    async def test_correlation_map_empty_data(self, hybrid_parsing, mock_file_parser_service):
        """Test correlation map with empty data."""
        structured_result = {
            "success": True,
            "tables": [],
            "records": [],
            "metadata": {}
        }
        
        unstructured_result = {
            "success": True,
            "chunks": [],
            "metadata": {}
        }
        
        correlation_map = await hybrid_parsing._create_correlation_map(
            structured_result=structured_result,
            unstructured_result=unstructured_result
        )
        
        assert correlation_map is not None
        assert "structured_to_unstructured" in correlation_map
        assert "unstructured_to_structured" in correlation_map
    
    @pytest.mark.asyncio
    async def test_correlation_map_exception_handling(self, hybrid_parsing, mock_file_parser_service):
        """Test correlation map exception handling."""
        # Pass invalid data to trigger exception
        correlation_map = await hybrid_parsing._create_correlation_map(
            structured_result=None,
            unstructured_result=None
        )
        
        # Should return minimal correlation map with error
        assert correlation_map is not None
        assert "error" in correlation_map or len(correlation_map) > 0

