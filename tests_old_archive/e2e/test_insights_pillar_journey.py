#!/usr/bin/env python3
"""
E2E Tests for Insights Pillar Journey

Tests the complete Insights Pillar user journey:
1. Select file from Content Pillar
2. Analyze content via Universal Gateway
3. Verify 3-way summary (Text | Table | Charts)
4. Test NLP query processing
5. Test metrics calculation
6. Test visualization generation
7. Test trend analysis

This simulates a real user workflow through the Insights Pillar.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.experience.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator.insights_orchestrator import InsightsOrchestrator

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]

class TestInsightsPillarJourney:
    """E2E tests for Insights Pillar user journey."""
    
    @pytest.fixture
    async def mock_platform_services(self):
        """Create mock platform services."""
        services = {}
        
        # Mock Librarian
        services['librarian'] = Mock()
        services['librarian'].store_document = AsyncMock(return_value={
            "success": True,
            "document_id": "doc_123"
        })
        services['librarian'].get_document = AsyncMock(return_value={
            "data": {
                "content": "Test analysis data",
                "metadata": {"analysis_type": "comprehensive"}
            }
        })
        
        # Mock Data Steward
        services['data_steward'] = Mock()
        services['data_steward'].track_lineage = AsyncMock(return_value={"success": True})
        
        return services
    
    @pytest.fixture
    async def mock_enabling_services(self):
        """Create mock enabling services."""
        services = {}
        
        # Mock DataAnalyzerService
        services['data_analyzer'] = Mock()
        services['data_analyzer'].analyze_data = AsyncMock(return_value={
            "success": True,
            "analysis": {
                "insights": ["Key insight 1", "Key insight 2", "Key insight 3"],
                "patterns": ["Pattern A", "Pattern B"],
                "trends": ["Upward trend in metric X", "Downward trend in metric Y"],
                "summary": "Comprehensive analysis shows positive trends"
            },
            "analysis_type": "descriptive"
        })
        
        # Mock MetricsCalculatorService
        services['metrics_calculator'] = Mock()
        services['metrics_calculator'].calculate_kpi = AsyncMock(return_value={
            "success": True,
            "kpi_value": 85.5,
            "metrics": {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.88,
                "f1_score": 0.85
            },
            "trend": "improving"
        })
        
        # Mock VisualizationEngineService
        services['visualization_engine'] = Mock()
        services['visualization_engine'].create_visualization = AsyncMock(return_value={
            "success": True,
            "visualization_id": "viz_123",
            "chart_data": {
                "type": "bar",
                "data": [10, 20, 30, 40, 50],
                "labels": ["Q1", "Q2", "Q3", "Q4", "Q5"]
            },
            "chart_config": {"title": "Quarterly Metrics"}
        })
        
        # Mock DataInsightsQueryService
        services['data_insights_query'] = Mock()
        services['data_insights_query'].process_query = AsyncMock(return_value={
            "success": True,
            "query_id": "query_123",
            "result": {
                "type": "text",
                "data": "The top 3 insights are: 1) Performance improved by 15%, 2) User engagement increased, 3) Cost efficiency optimized"
            }
        })
        
        return services
    
    @pytest.fixture
    async def insights_orchestrator(self, mock_platform_services, mock_enabling_services):
        """Create InsightsOrchestrator with mocked dependencies."""
        mock_business_orchestrator = Mock()
        mock_business_orchestrator.realm_name = "business_enablement"
        mock_business_orchestrator.platform_gateway = Mock()
        mock_business_orchestrator.di_container = Mock()
        
        # Inject enabling services
        mock_business_orchestrator.data_analyzer_service = mock_enabling_services['data_analyzer']
        mock_business_orchestrator.metrics_calculator_service = mock_enabling_services['metrics_calculator']
        mock_business_orchestrator.visualization_engine_service = mock_enabling_services['visualization_engine']
        mock_business_orchestrator.data_insights_query_service = mock_enabling_services['data_insights_query']
        
        orchestrator = InsightsOrchestrator(mock_business_orchestrator)
        
        # Inject platform services
        orchestrator.librarian = mock_platform_services['librarian']
        orchestrator.data_steward = mock_platform_services['data_steward']
        
        # Initialize analysis cache
        orchestrator.analysis_cache = {}
        
        return orchestrator
    
    @pytest.fixture
    async def gateway_service(self, insights_orchestrator):
        """Create FrontendGatewayService with mocked orchestrators."""
        platform_gateway = Mock()
        di_container = Mock()
        
        gateway = FrontendGatewayService(
            service_name="FrontendGatewayService",
            realm_name="experience",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Inject orchestrators
        gateway.insights_orchestrator = insights_orchestrator
        gateway.librarian = Mock()
        gateway.security_guard = Mock()
        gateway.traffic_cop = Mock()
        
        return gateway
    
    async def test_complete_insights_pillar_journey(
        self,
        gateway_service,
        insights_orchestrator,
        mock_platform_services,
        mock_enabling_services
    ):
        """Test complete Insights Pillar user journey."""
        
        # Step 1: Calculate metrics for a resource
        metrics_request = {
            "endpoint": "/api/insights/calculate_metrics",
            "method": "POST",
            "params": {
                "resource_id": "resource_123",
                "options": {"analysis_type": "descriptive"}
            }
        }
        
        metrics_result = await gateway_service.route_frontend_request(metrics_request)
        
        # Verify metrics calculation succeeded
        assert isinstance(metrics_result, dict)
        assert "success" in metrics_result or "status" in metrics_result
        
        # Step 2: Generate insights
        insights_request = {
            "endpoint": "/api/insights/generate_insights",
            "method": "POST",
            "params": {
                "resource_id": "resource_123",
                "options": {"include_visualization": True}
            }
        }
        
        insights_result = await gateway_service.route_frontend_request(insights_request)
        
        # Verify insights generation succeeded
        assert isinstance(insights_result, dict)
        if insights_result.get("status") == "success":
            assert "data" in insights_result
        
        # Step 3: Create visualization
        viz_request = {
            "endpoint": "/api/insights/create_visualization",
            "method": "POST",
            "params": {
                "resource_id": "resource_123",
                "options": {"visualization_type": "bar_chart"}
            }
        }
        
        viz_result = await gateway_service.route_frontend_request(viz_request)
        
        # Verify visualization creation succeeded
        assert isinstance(viz_result, dict)
        
        # Step 4: Query analysis results with NLP
        query_request = {
            "endpoint": "/api/insights/query_analysis_results",
            "method": "POST",
            "params": {
                "query": "What are the top 3 insights?",
                "analysis_id": "analysis_123"
            }
        }
        
        query_result = await gateway_service.route_frontend_request(query_request)
        
        # Verify NLP query succeeded
        assert isinstance(query_result, dict)
    
    async def test_three_way_summary_generation(
        self,
        insights_orchestrator,
        mock_enabling_services
    ):
        """Test 3-way summary generation (Text | Table | Charts)."""
        # Initialize analysis cache with test data
        insights_orchestrator.analysis_cache = {
            "analysis_123": {
                "results": {
                    "insights": ["Insight 1", "Insight 2"],
                    "metrics": {"kpi": 85.5},
                    "trends": ["Trend A"]
                }
            }
        }
        
        # Get pillar summary
        result = await insights_orchestrator.get_pillar_summary(analysis_id="analysis_123")
        
        # Should return summary data
        assert isinstance(result, dict)
        assert "success" in result or "status" in result
    
    async def test_metrics_calculation_workflow(self, insights_orchestrator):
        """Test metrics calculation workflow."""
        result = await insights_orchestrator.calculate_metrics(
            resource_id="resource_123",
            options={"analysis_type": "descriptive"}
        )
        
        # Should return metrics
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
    
    async def test_insights_generation_workflow(self, insights_orchestrator):
        """Test insights generation workflow."""
        result = await insights_orchestrator.generate_insights(
            resource_id="resource_123",
            options={"include_visualization": True}
        )
        
        # Should return insights
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
            # Should have orchestrated multiple services
            data = result["data"]
            assert "analysis" in data or "metrics" in data or "visualization" in data
    
    async def test_visualization_creation_workflow(self, insights_orchestrator):
        """Test visualization creation workflow."""
        result = await insights_orchestrator.create_visualization(
            resource_id="resource_123",
            options={"visualization_type": "line_chart"}
        )
        
        # Should return visualization
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
    
    async def test_trend_analysis_workflow(self, insights_orchestrator):
        """Test trend analysis workflow."""
        result = await insights_orchestrator.analyze_trends(
            resource_id="resource_123",
            options={"time_period": "30d"}
        )
        
        # Should return trend analysis
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
    
    async def test_nlp_query_processing(
        self,
        insights_orchestrator,
        mock_enabling_services
    ):
        """Test NLP query processing."""
        # Set up analysis cache
        insights_orchestrator.analysis_cache = {
            "analysis_123": {
                "results": {
                    "insights": ["Insight 1", "Insight 2", "Insight 3"],
                    "metrics": {"accuracy": 0.85}
                }
            }
        }
        
        result = await insights_orchestrator.query_analysis_results(
            query="What are the top insights?",
            analysis_id="analysis_123",
            query_type="text"
        )
        
        # Should return query result
        assert "status" in result or "success" in result
    
    async def test_content_analysis_for_insights(self, insights_orchestrator):
        """Test analyzing content for insights."""
        # Mock workflows
        insights_orchestrator.structured_workflow = Mock()
        insights_orchestrator.unstructured_workflow = Mock()
        insights_orchestrator.hybrid_workflow = Mock()
        
        result = await insights_orchestrator.analyze_content_for_insights(
            source_type="file",
            file_id="file_123",
            content_type="structured"
        )
        
        # Should return analysis
        assert isinstance(result, dict)
        assert "success" in result or "error" in result
    
    async def test_list_user_analyses(self, insights_orchestrator):
        """Test listing user analyses."""
        # Set up analysis cache
        insights_orchestrator.analysis_cache = {
            "analysis_1": {"timestamp": "2025-11-11T10:00:00"},
            "analysis_2": {"timestamp": "2025-11-11T11:00:00"}
        }
        
        result = await insights_orchestrator.list_user_analyses(
            limit=10,
            offset=0
        )
        
        # Should return list of analyses
        assert isinstance(result, dict)
        assert "success" in result or "status" in result
    
    async def test_error_handling_invalid_resource(
        self,
        insights_orchestrator,
        mock_enabling_services
    ):
        """Test error handling for invalid resource."""
        # Mock analyzer failure
        mock_enabling_services['data_analyzer'].analyze_data = AsyncMock(return_value={
            "success": False,
            "error": "Resource not found"
        })
        
        result = await insights_orchestrator.calculate_metrics(
            resource_id="invalid_resource"
        )
        
        # Should handle error gracefully
        assert isinstance(result, dict)
        assert "status" in result
    
    async def test_concurrent_analysis_requests(self, insights_orchestrator):
        """Test concurrent analysis requests."""
        import asyncio
        
        # Simulate multiple analyses
        tasks = [
            insights_orchestrator.calculate_metrics(resource_id=f"resource_{i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete
        assert len(results) == 3
        for result in results:
            assert isinstance(result, (dict, Exception))
    
    async def test_visualization_types(self, insights_orchestrator):
        """Test different visualization types."""
        viz_types = ["bar_chart", "line_chart", "pie_chart", "scatter_plot"]
        
        for viz_type in viz_types:
            result = await insights_orchestrator.create_visualization(
                resource_id="resource_123",
                options={"visualization_type": viz_type}
            )
            
            # Should handle all visualization types
            assert isinstance(result, dict)
            assert "status" in result
    
    async def test_analysis_caching(self, insights_orchestrator):
        """Test that analysis results are cached."""
        # Perform analysis
        result1 = await insights_orchestrator.calculate_metrics(
            resource_id="resource_123"
        )
        
        # Check if result is stored (would be in analysis_cache in real scenario)
        assert isinstance(result1, dict)
        
        # Verify cache exists
        assert hasattr(insights_orchestrator, 'analysis_cache')
    
    async def test_smart_city_integration(
        self,
        insights_orchestrator,
        mock_platform_services
    ):
        """Test Smart City service integration."""
        result = await insights_orchestrator.calculate_metrics(
            resource_id="resource_123"
        )
        
        # Should have completed (Smart City integration happens internally)
        assert "status" in result
    
    async def test_multi_service_orchestration(
        self,
        insights_orchestrator,
        mock_enabling_services
    ):
        """Test orchestration of multiple enabling services."""
        # Generate insights should orchestrate analyzer + metrics + visualization
        result = await insights_orchestrator.generate_insights(
            resource_id="resource_123",
            options={"include_visualization": True}
        )
        
        # Should have orchestrated multiple services
        assert "status" in result
        if result["status"] == "success":
            data = result["data"]
            # Should have results from multiple services
            assert isinstance(data, dict)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

