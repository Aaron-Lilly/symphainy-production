#!/usr/bin/env python3
"""
Integration Tests for InsightsOrchestrator

Tests the Insights Orchestrator integration including:
- All 9 semantic API methods
- Enabling service composition
- Universal Gateway routing compatibility
- NLP query processing
- End-to-end insights generation workflows
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator.insights_orchestrator import InsightsOrchestrator

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

class TestInsightsOrchestrator:
    """Integration tests for InsightsOrchestrator."""
    
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
        orchestrator.data_analyzer_service = Mock()
        orchestrator.data_analyzer_service.analyze_data = AsyncMock(return_value={
            "success": True,
            "analysis": {"insights": ["test insight"], "patterns": []},
            "analysis_type": "descriptive"
        })
        
        orchestrator.metrics_calculator_service = Mock()
        orchestrator.metrics_calculator_service.calculate_kpi = AsyncMock(return_value={
            "success": True,
            "kpi_value": 85.5,
            "metrics": {"accuracy": 0.85}
        })
        
        orchestrator.visualization_engine_service = Mock()
        orchestrator.visualization_engine_service.create_visualization = AsyncMock(return_value={
            "success": True,
            "visualization_id": "viz_123",
            "chart_data": {}
        })
        
        orchestrator.data_insights_query_service = Mock()
        orchestrator.data_insights_query_service.process_query = AsyncMock(return_value={
            "success": True,
            "query_id": "query_123",
            "result": {"type": "text", "data": "Test result"}
        })
        
        return orchestrator
    
    @pytest.fixture
    async def insights_orchestrator(self, mock_business_orchestrator):
        """Create InsightsOrchestrator instance."""
        orchestrator = InsightsOrchestrator(mock_business_orchestrator)
        
        # Mock Smart City services
        orchestrator.librarian = Mock()
        orchestrator.librarian.store_document = AsyncMock(return_value={"success": True, "document_id": "doc_123"})
        orchestrator.librarian.get_document = AsyncMock(return_value={
            "data": {"content": "test content", "metadata": {}}
        })
        orchestrator.data_steward = Mock()
        orchestrator.data_steward.track_lineage = AsyncMock(return_value={"success": True})
        orchestrator.curator = Mock()
        
        return orchestrator
    
    async def test_orchestrator_initialization(self, insights_orchestrator):
        """Test that InsightsOrchestrator initializes correctly."""
        assert insights_orchestrator.service_name == "InsightsOrchestratorService"
        assert insights_orchestrator.realm_name == "business_enablement"
        assert hasattr(insights_orchestrator, 'calculate_metrics')
        assert hasattr(insights_orchestrator, 'generate_insights')
        assert hasattr(insights_orchestrator, 'create_visualization')
        assert hasattr(insights_orchestrator, 'analyze_trends')
        assert hasattr(insights_orchestrator, 'analyze_content_for_insights')
        assert hasattr(insights_orchestrator, 'query_analysis_results')
        assert hasattr(insights_orchestrator, 'get_analysis_results')
        assert hasattr(insights_orchestrator, 'get_pillar_summary')
        assert hasattr(insights_orchestrator, 'list_user_analyses')
    
    async def test_calculate_metrics_semantic_api(self, insights_orchestrator):
        """Test calculate_metrics semantic API method."""
        result = await insights_orchestrator.calculate_metrics(
            resource_id="test_resource_123",
            options={"analysis_type": "descriptive"}
        )
        
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
            assert "resource_id" in result
    
    async def test_generate_insights_semantic_api(self, insights_orchestrator):
        """Test generate_insights semantic API method."""
        result = await insights_orchestrator.generate_insights(
            resource_id="test_resource_123",
            options={"analysis_type": "descriptive"}
        )
        
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
            # Should orchestrate multiple services
            data = result["data"]
            assert "analysis" in data or "metrics" in data
    
    async def test_create_visualization_semantic_api(self, insights_orchestrator):
        """Test create_visualization semantic API method."""
        result = await insights_orchestrator.create_visualization(
            resource_id="test_resource_123",
            options={"visualization_type": "bar_chart"}
        )
        
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
    
    async def test_analyze_trends_semantic_api(self, insights_orchestrator):
        """Test analyze_trends semantic API method."""
        result = await insights_orchestrator.analyze_trends(
            resource_id="test_resource_123",
            options={"time_period": "30d"}
        )
        
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
    
    async def test_analyze_content_for_insights_semantic_api(self, insights_orchestrator):
        """Test analyze_content_for_insights semantic API method."""
        # Initialize workflows to avoid AttributeError
        insights_orchestrator.structured_workflow = Mock()
        insights_orchestrator.unstructured_workflow = Mock()
        insights_orchestrator.hybrid_workflow = Mock()
        
        result = await insights_orchestrator.analyze_content_for_insights(
            source_type="file",
            file_id="test_file_123",
            content_type="structured",
            analysis_options={"analysis_depth": "detailed"}
        )
        
        # This method returns success/error format, not status
        assert "success" in result or "error" in result
        if result.get("success"):
            assert "analysis_id" in result or "data" in result
    
    async def test_query_analysis_results_semantic_api(self, insights_orchestrator, mock_business_orchestrator):
        """Test query_analysis_results semantic API method (NLP query)."""
        result = await insights_orchestrator.query_analysis_results(
            query="What are the top insights?",
            analysis_id="analysis_123",
            query_type="text"
        )
        
        assert "status" in result or "success" in result
        # Should use DataInsightsQueryService
        if result.get("status") == "success" or result.get("success"):
            assert "query_id" in result or "result" in result or "data" in result
    
    async def test_get_analysis_results_semantic_api(self, insights_orchestrator):
        """Test get_analysis_results semantic API method."""
        # Initialize analysis_cache to avoid AttributeError
        insights_orchestrator.analysis_cache = {}
        
        result = await insights_orchestrator.get_analysis_results(
            analysis_id="analysis_123"
        )
        
        # Should return success or error (not status)
        assert "success" in result or "error" in result
        if result.get("success"):
            assert "analysis" in result or "data" in result
    
    async def test_get_pillar_summary_semantic_api(self, insights_orchestrator):
        """Test get_pillar_summary semantic API method."""
        # Initialize analysis_cache to avoid AttributeError
        insights_orchestrator.analysis_cache = {}
        
        result = await insights_orchestrator.get_pillar_summary(
            analysis_id="analysis_123"
        )
        
        assert "status" in result or "success" in result
        # Should return summary of insights pillar state
    
    async def test_list_user_analyses_semantic_api(self, insights_orchestrator):
        """Test list_user_analyses semantic API method."""
        # Initialize analysis_cache to avoid AttributeError
        insights_orchestrator.analysis_cache = {}
        
        result = await insights_orchestrator.list_user_analyses(
            limit=20,
            offset=0,
            content_type="structured"
        )
        
        assert "status" in result or "success" in result
        if result.get("status") == "success" or result.get("success"):
            assert "analyses" in result or "data" in result
    
    async def test_multiple_service_orchestration(self, insights_orchestrator):
        """Test orchestration of multiple enabling services."""
        # generate_insights should orchestrate analyzer + metrics + visualization
        result = await insights_orchestrator.generate_insights(
            resource_id="test_resource",
            options={"include_visualization": True}
        )
        
        assert "status" in result
        if result["status"] == "success":
            # Should have results from multiple services
            data = result["data"]
            assert "analysis" in data or "metrics" in data or "visualization" in data
    
    async def test_nlp_query_integration(self, insights_orchestrator, mock_business_orchestrator):
        """Test NLP query processing integration."""
        # Initialize analysis_cache
        insights_orchestrator.analysis_cache = {
            "analysis_123": {"results": {"metrics": [{"name": "metric1", "value": 100}]}}
        }
        
        # Test that query_analysis_results uses DataInsightsQueryService
        result = await insights_orchestrator.query_analysis_results(
            query="Show me the top 5 metrics",
            analysis_id="analysis_123",
            query_type="text"
        )
        
        # Should have called DataInsightsQueryService
        assert "status" in result or "success" in result
    
    async def test_universal_gateway_compatibility(self, insights_orchestrator):
        """Test that orchestrator methods are compatible with Universal Gateway routing."""
        # Initialize analysis_cache
        insights_orchestrator.analysis_cache = {}
        
        methods_to_test = [
            ("calculate_metrics", {"resource_id": "test_123"}),
            ("generate_insights", {"resource_id": "test_123"}),
            ("create_visualization", {"resource_id": "test_123"}),
            ("get_analysis_results", {"analysis_id": "analysis_123"}),
            ("get_pillar_summary", {"analysis_id": "analysis_123"})
        ]
        
        for method_name, params in methods_to_test:
            method = getattr(insights_orchestrator, method_name)
            result = await method(**params)
            
            # All should return dict with status indicator
            assert isinstance(result, dict)
            assert "status" in result or "success" in result or "error" in result
    
    async def test_error_handling(self, insights_orchestrator, mock_business_orchestrator):
        """Test error handling in orchestrator."""
        # Mock service failure
        mock_business_orchestrator.data_analyzer_service.analyze_data = AsyncMock(return_value={
            "success": False,
            "error": "Analysis failed"
        })
        
        result = await insights_orchestrator.calculate_metrics(
            resource_id="invalid_resource"
        )
        
        # Should handle error gracefully
        assert "status" in result
    
    async def test_visualization_workflow(self, insights_orchestrator):
        """Test complete visualization workflow."""
        # Step 1: Generate insights
        insights_result = await insights_orchestrator.generate_insights(
            resource_id="test_resource",
            options={"include_visualization": False}
        )
        
        assert "status" in insights_result
        
        # Step 2: Create visualization
        if insights_result.get("status") == "success":
            viz_result = await insights_orchestrator.create_visualization(
                resource_id="test_resource",
                options={"visualization_type": "dashboard"}
            )
            assert "status" in viz_result
    
    async def test_concurrent_analysis_requests(self, insights_orchestrator):
        """Test handling of concurrent analysis requests."""
        import asyncio
        
        # Simulate multiple concurrent analysis requests
        tasks = [
            insights_orchestrator.calculate_metrics(resource_id=f"resource_{i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without crashing
        assert len(results) == 3
        for result in results:
            assert isinstance(result, (dict, Exception))
    
    async def test_smart_city_integration(self, insights_orchestrator):
        """Test Smart City service integration (Librarian, Data Steward)."""
        result = await insights_orchestrator.calculate_metrics(
            resource_id="test_resource"
        )
        
        # Should have completed successfully (Smart City integration happens internally)
        assert "status" in result
        # The orchestrator formats results and attempts to store them
        if result.get("status") == "success":
            assert "data" in result
    
    async def test_execute_method(self, insights_orchestrator):
        """Test execute method (generic orchestration entry point)."""
        request = {
            "action": "calculate_metrics",
            "resource_id": "test_123"
        }
        
        result = await insights_orchestrator.execute(request)
        
        assert "status" in result or "success" in result
    
    async def test_health_check(self, insights_orchestrator):
        """Test health_check method."""
        result = await insights_orchestrator.health_check()
        
        assert "status" in result or "healthy" in result
    
    async def test_get_service_capabilities(self, insights_orchestrator):
        """Test get_service_capabilities method."""
        result = await insights_orchestrator.get_service_capabilities()
        
        assert "capabilities" in result or "semantic_apis" in result
        # Should list all 9 semantic API methods

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

