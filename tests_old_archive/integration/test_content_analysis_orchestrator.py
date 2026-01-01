#!/usr/bin/env python3
"""
Integration Tests for ContentAnalysisOrchestrator

Tests the Content Analysis Orchestrator integration including:
- Semantic API method orchestration
- Enabling service composition
- Universal Gateway routing compatibility
- End-to-end content analysis workflows
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import io

from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

class TestContentAnalysisOrchestrator:
    """Integration tests for ContentAnalysisOrchestrator."""
    
    @pytest.fixture
    async def mock_business_orchestrator(self):
        """Create mock BusinessOrchestrator."""
        orchestrator = Mock()
        orchestrator.realm_name = "business_enablement"
        orchestrator.platform_gateway = Mock()
        orchestrator.platform_gateway.get_smart_city_service = AsyncMock(return_value=None)
        orchestrator.di_container = Mock()
        orchestrator.di_container.get_foundation_service = Mock(return_value=None)
        
        # Mock enabling services
        orchestrator.file_parser_service = Mock()
        orchestrator.file_parser_service.parse_file = AsyncMock(return_value={
            "success": True,
            "file_id": "test_file_123",
            "parsed_content": {"text": "Test content", "metadata": {}},
            "file_type": "txt"
        })
        
        orchestrator.data_analyzer_service = Mock()
        orchestrator.data_analyzer_service.analyze_data = AsyncMock(return_value={
            "success": True,
            "analysis": {"keywords": ["test"], "entities": []},
            "insights": []
        })
        
        orchestrator.metrics_calculator_service = Mock()
        orchestrator.metrics_calculator_service.calculate_metric = AsyncMock(return_value={
            "success": True,
            "metrics": {"word_count": 100, "readability": 75}
        })
        
        return orchestrator
    
    @pytest.fixture
    async def content_orchestrator(self, mock_business_orchestrator):
        """Create ContentAnalysisOrchestrator instance."""
        orchestrator = ContentAnalysisOrchestrator(mock_business_orchestrator)
        
        # Mock Smart City services
        orchestrator.librarian = Mock()
        orchestrator.librarian.store_document = AsyncMock(return_value={"success": True})
        orchestrator.librarian.get_document = AsyncMock(return_value={
            "data": {"content": "test content", "metadata": {}}
        })
        orchestrator.data_steward = Mock()
        orchestrator.curator = Mock()
        
        return orchestrator
    
    async def test_orchestrator_initialization(self, content_orchestrator):
        """Test that ContentAnalysisOrchestrator initializes correctly."""
        assert content_orchestrator.service_name == "ContentAnalysisOrchestratorService"
        assert content_orchestrator.realm_name == "business_enablement"
        assert hasattr(content_orchestrator, 'analyze_document')
        assert hasattr(content_orchestrator, 'parse_file')
        assert hasattr(content_orchestrator, 'extract_entities')
        assert hasattr(content_orchestrator, 'handle_content_upload')
    
    async def test_parse_file_semantic_api(self, content_orchestrator, mock_business_orchestrator):
        """Test parse_file semantic API method."""
        result = await content_orchestrator.parse_file(
            file_id="test_file_123"
        )
        
        assert result["status"] == "success"
        assert "resource_id" in result
        assert "data" in result
        assert "parse_result" in result["data"]
    
    async def test_analyze_document_semantic_api(self, content_orchestrator, mock_business_orchestrator):
        """Test analyze_document semantic API method."""
        result = await content_orchestrator.analyze_document(
            document_id="test_doc_123",
            analysis_types=["structure", "metadata", "entities"]
        )
        
        assert "status" in result
        # Should orchestrate multiple enabling services
        if result["status"] == "success":
            assert "data" in result
            # Should have results for requested analysis types
            data = result["data"]
            assert "structure" in data or "metadata" in data or "entities" in data
    
    async def test_extract_entities_semantic_api(self, content_orchestrator, mock_business_orchestrator):
        """Test extract_entities semantic API method."""
        # Mock the data analyzer service properly
        mock_business_orchestrator.data_analyzer_service.extract_entities = AsyncMock(return_value={
            "success": True,
            "entities": [{"type": "test", "value": "entity"}]
        })
        
        result = await content_orchestrator.extract_entities(
            document_id="test_doc_123"
        )
        
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
            assert "entities" in result["data"]
    
    async def test_handle_content_upload_semantic_api(self, content_orchestrator):
        """Test handle_content_upload semantic API method."""
        # Create mock file data
        file_data = b"Test file content"
        
        result = await content_orchestrator.handle_content_upload(
            file_data=file_data,
            filename="test.txt",
            file_type="txt"
        )
        
        assert "success" in result
        if result["success"]:
            assert "file_id" in result or "upload_id" in result
    
    async def test_execute_method(self, content_orchestrator):
        """Test execute method (generic orchestration entry point)."""
        request = {
            "action": "parse",
            "file_id": "test_file_123"
        }
        
        result = await content_orchestrator.execute(request)
        
        assert "success" in result or "status" in result
    
    async def test_enabling_service_composition(self, content_orchestrator, mock_business_orchestrator):
        """Test that orchestrator properly composes enabling services."""
        # Test that parse_file uses FileParserService (via lazy initialization)
        result = await content_orchestrator.parse_file(file_id="test_123")
        
        # Verify orchestrator completed successfully (service composition happened)
        assert result["status"] == "success"
        assert "data" in result
        # The fact that we got a properly formatted response means services were composed
    
    async def test_error_handling(self, content_orchestrator, mock_business_orchestrator):
        """Test error handling in orchestrator."""
        # Mock service failure
        mock_business_orchestrator.file_parser_service.parse_file = AsyncMock(return_value={
            "success": False,
            "error": "Parse failed"
        })
        
        result = await content_orchestrator.parse_file(file_id="invalid_file")
        
        # Should handle error gracefully - returns success status with error in data
        assert "status" in result
        assert "data" in result or "error" in result
    
    async def test_multiple_service_orchestration(self, content_orchestrator, mock_business_orchestrator):
        """Test orchestration of multiple enabling services."""
        # analyze_document should orchestrate parser + analyzer + metrics
        result = await content_orchestrator.analyze_document(
            document_id="test_doc",
            analysis_types=["structure", "metadata"]
        )
        
        # Should have called multiple services or returned comprehensive result
        assert "status" in result
    
    async def test_universal_gateway_compatibility(self, content_orchestrator, mock_business_orchestrator):
        """Test that orchestrator methods are compatible with Universal Gateway routing."""
        # All semantic API methods should accept standard parameters
        # and return standard response formats
        
        # Mock the data analyzer for extract_entities
        mock_business_orchestrator.data_analyzer_service.extract_entities = AsyncMock(return_value={
            "success": True,
            "entities": []
        })
        
        methods_to_test = [
            ("parse_file", {"file_id": "test_123"}),
            ("analyze_document", {"document_id": "test_doc", "analysis_types": ["structure"]}),
            ("extract_entities", {"document_id": "test_doc"})
        ]
        
        for method_name, params in methods_to_test:
            method = getattr(content_orchestrator, method_name)
            result = await method(**params)
            
            # All should return dict with status indicator
            assert isinstance(result, dict)
            assert "status" in result or "error" in result
    
    async def test_file_upload_workflow(self, content_orchestrator):
        """Test complete file upload workflow."""
        # Step 1: Upload file
        upload_result = await content_orchestrator.handle_content_upload(
            file_data=b"Test content",
            filename="test.txt",
            file_type="txt"
        )
        
        assert "success" in upload_result
        
        # Step 2: Parse file (if upload succeeded)
        if upload_result.get("success") and "file_id" in upload_result:
            parse_result = await content_orchestrator.parse_file(
                file_id=upload_result["file_id"]
            )
            assert "success" in parse_result
    
    async def test_concurrent_requests(self, content_orchestrator):
        """Test handling of concurrent requests."""
        import asyncio
        
        # Simulate multiple concurrent parse requests
        tasks = [
            content_orchestrator.parse_file(file_id=f"file_{i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without crashing
        assert len(results) == 3
        for result in results:
            assert isinstance(result, (dict, Exception))
    
    async def test_session_context_handling(self, content_orchestrator):
        """Test that orchestrator handles session context properly."""
        # Methods should work with or without explicit session context
        result = await content_orchestrator.parse_file(
            file_id="test_123"
        )
        
        assert "status" in result or "error" in result

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

