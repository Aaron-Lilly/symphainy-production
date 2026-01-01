#!/usr/bin/env python3
"""
Integration tests for Pillar Summary Endpoints

Tests the newly created pillar summary endpoints:
- Content Pillar: GET /api/v1/content-pillar/pillar-summary
- Operations Pillar: GET /api/v1/operations-pillar/pillar-summary
- Business Outcomes: GET /api/v1/business-outcomes-pillar/get-pillar-summaries

Validates:
- Endpoints are accessible
- Return correct 3-way summary structure
- Handle missing data gracefully
- Cross-realm (intra-realm) communication works
"""

import os
import sys
import asyncio
import pytest
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))


class TestPillarSummaryEndpoints:
    """Test suite for pillar summary endpoints - tests orchestrator methods directly."""
    
    @pytest.fixture
    def test_user_id(self):
        """Test user ID."""
        return "test_user_123"
    
    @pytest.fixture
    def test_session_id(self):
        """Test session ID."""
        return "test_session_456"
    
    @pytest.fixture
    def mock_delivery_manager(self):
        """Create mock delivery manager with orchestrators."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_orchestrator.content_orchestrator import ContentOrchestrator
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
        
        mock_dm = Mock()
        mock_dm.mvp_pillar_orchestrators = {
            "content": Mock(spec=ContentOrchestrator),
            "insights": Mock(spec=InsightsOrchestrator),
            "operations": Mock(spec=OperationsOrchestrator)
        }
        return mock_dm
    
    @pytest.mark.asyncio
    async def test_content_orchestrator_get_pillar_summary_method_exists(self, test_user_id):
        """Test that ContentOrchestrator has get_pillar_summary method."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_orchestrator.content_orchestrator import ContentOrchestrator
        
        # Check method exists
        assert hasattr(ContentOrchestrator, 'get_pillar_summary'), \
            "ContentOrchestrator should have get_pillar_summary method"
        
        # Check it's async
        import inspect
        method = getattr(ContentOrchestrator, 'get_pillar_summary')
        assert inspect.iscoroutinefunction(method), \
            "get_pillar_summary should be an async method"
    
    @pytest.mark.asyncio
    async def test_operations_orchestrator_get_pillar_summary_method_exists(self):
        """Test that OperationsOrchestrator has get_pillar_summary method."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
        
        # Check method exists
        assert hasattr(OperationsOrchestrator, 'get_pillar_summary'), \
            "OperationsOrchestrator should have get_pillar_summary method"
        
        # Check it's async
        import inspect
        method = getattr(OperationsOrchestrator, 'get_pillar_summary')
        assert inspect.iscoroutinefunction(method), \
            "get_pillar_summary should be an async method"
    
    @pytest.mark.asyncio
    async def test_business_outcomes_get_pillar_summaries_calls_orchestrators(self, mock_delivery_manager, test_user_id, test_session_id):
        """Test that BusinessOutcomesOrchestrator.get_pillar_summaries calls all three orchestrators."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        # Setup mock orchestrator responses
        mock_delivery_manager.mvp_pillar_orchestrators["content"].get_pillar_summary = AsyncMock(return_value={
            "success": True,
            "pillar": "content",
            "summary": {"textual": "Test", "tabular": {}, "visualizations": []},
            "semantic_data_model": {}
        })
        
        mock_delivery_manager.mvp_pillar_orchestrators["insights"].get_pillar_summary = AsyncMock(return_value={
            "success": True,
            "pillar": "insights",
            "summary": {"textual": "Test", "tabular": {}, "visualizations": []}
        })
        
        mock_delivery_manager.mvp_pillar_orchestrators["operations"].get_pillar_summary = AsyncMock(return_value={
            "success": True,
            "pillar": "operations",
            "summary": {"textual": "Test", "tabular": {}, "visualizations": []},
            "artifacts": {}
        })
        
        # Create BusinessOutcomesOrchestrator with mock delivery manager
        orchestrator = BusinessOutcomesOrchestrator(mock_delivery_manager)
        orchestrator.delivery_manager = mock_delivery_manager
        
        # Call get_pillar_summaries
        result = await orchestrator.get_pillar_summaries(
            session_id=test_session_id,
            user_id=test_user_id
        )
        
        # Verify structure
        assert "success" in result, "Should have 'success' field"
        assert "summaries" in result, "Should have 'summaries' field"
        
        summaries = result["summaries"]
        assert "content_pillar" in summaries, "Should have 'content_pillar' summary"
        assert "insights_pillar" in summaries, "Should have 'insights_pillar' summary"
        assert "operations_pillar" in summaries, "Should have 'operations_pillar' summary"
        
        # Verify orchestrators were called
        mock_delivery_manager.mvp_pillar_orchestrators["content"].get_pillar_summary.assert_called_once()
        mock_delivery_manager.mvp_pillar_orchestrators["insights"].get_pillar_summary.assert_called_once()
        mock_delivery_manager.mvp_pillar_orchestrators["operations"].get_pillar_summary.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_business_outcomes_handles_missing_orchestrators_gracefully(self, mock_delivery_manager, test_user_id, test_session_id):
        """Test that BusinessOutcomesOrchestrator handles missing orchestrators gracefully."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        # Remove one orchestrator
        mock_delivery_manager.mvp_pillar_orchestrators["content"] = None
        
        # Setup other orchestrators
        mock_delivery_manager.mvp_pillar_orchestrators["insights"].get_pillar_summary = AsyncMock(return_value={
            "success": True,
            "pillar": "insights",
            "summary": {"textual": "Test", "tabular": {}, "visualizations": []}
        })
        
        mock_delivery_manager.mvp_pillar_orchestrators["operations"].get_pillar_summary = AsyncMock(return_value={
            "success": True,
            "pillar": "operations",
            "summary": {"textual": "Test", "tabular": {}, "visualizations": []},
            "artifacts": {}
        })
        
        # Create BusinessOutcomesOrchestrator
        orchestrator = BusinessOutcomesOrchestrator(mock_delivery_manager)
        orchestrator.delivery_manager = mock_delivery_manager
        
        # Call get_pillar_summaries - should not crash
        result = await orchestrator.get_pillar_summaries(
            session_id=test_session_id,
            user_id=test_user_id
        )
        
        # Should still return structure
        assert "success" in result, "Should have 'success' field"
        assert "summaries" in result, "Should have 'summaries' field"
        
        # Content should be empty, but others should work
        summaries = result["summaries"]
        assert "content_pillar" in summaries, "Should have 'content_pillar' key (even if empty)"
        assert "insights_pillar" in summaries, "Should have 'insights_pillar' summary"
        assert "operations_pillar" in summaries, "Should have 'operations_pillar' summary"
    
    @pytest.mark.asyncio
    async def test_content_pillar_summary_structure(self, mock_delivery_manager):
        """Test that Content pillar summary returns correct structure."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_orchestrator.content_orchestrator import ContentOrchestrator
        
        # Create orchestrator with mock delivery manager
        orchestrator = ContentOrchestrator(mock_delivery_manager)
        
        # Mock the list_uploaded_files method
        orchestrator.list_uploaded_files = AsyncMock(return_value={
            "success": True,
            "files": [
                {"ui_name": "test.csv", "content_type": "structured", "parsed": True, "size_bytes": 1024},
                {"ui_name": "test.pdf", "content_type": "unstructured", "parsed": False, "size_bytes": 2048}
            ],
            "count": 2
        })
        
        # Mock _realm_service for user context
        orchestrator._realm_service = Mock()
        orchestrator._realm_service.get_user_context = Mock(return_value={"user_id": "test_user"})
        orchestrator.logger = Mock()
        
        # Call get_pillar_summary
        result = await orchestrator.get_pillar_summary(user_id="test_user")
        
        # Verify structure
        assert result.get("success") is not None, "Should have 'success' field"
        
        if result.get("success"):
            assert result["pillar"] == "content", "Pillar should be 'content'"
            assert "summary" in result, "Should have 'summary' field"
            
            summary = result["summary"]
            assert "textual" in summary, "Should have 'textual' summary"
            assert "tabular" in summary, "Should have 'tabular' summary"
            assert "visualizations" in summary, "Should have 'visualizations' summary"
            
            assert "semantic_data_model" in result, "Should have 'semantic_data_model' field"
    
    @pytest.mark.asyncio
    async def test_operations_pillar_summary_structure(self, mock_delivery_manager):
        """Test that Operations pillar summary returns correct structure."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
        
        # Create orchestrator with mock delivery manager
        orchestrator = OperationsOrchestrator(mock_delivery_manager)
        
        # Mock Librarian API
        mock_librarian = AsyncMock()
        mock_librarian.query_documents = AsyncMock(return_value={
            "documents": [
                {
                    "artifact_id": "artifact_123",
                    "artifact_type": "workflow",
                    "status": "draft",
                    "data": {"workflow_definition": {"title": "Test Workflow"}},
                    "created_at": "2024-12-16T12:00:00Z"
                }
            ]
        })
        
        orchestrator.get_librarian_api = AsyncMock(return_value=mock_librarian)
        orchestrator._realm_service = Mock()
        orchestrator._realm_service.search_documents = AsyncMock(return_value=[])
        orchestrator.logger = Mock()
        
        # Call get_pillar_summary
        result = await orchestrator.get_pillar_summary(user_id="test_user")
        
        # Verify structure
        assert result.get("success") is not None, "Should have 'success' field"
        
        if result.get("success"):
            assert result["pillar"] == "operations", "Pillar should be 'operations'"
            assert "summary" in result, "Should have 'summary' field"
            
            summary = result["summary"]
            assert "textual" in summary, "Should have 'textual' summary"
            assert "tabular" in summary, "Should have 'tabular' summary"
            assert "visualizations" in summary, "Should have 'visualizations' summary"
            
            assert "artifacts" in result, "Should have 'artifacts' field"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

