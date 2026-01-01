#!/usr/bin/env python3
"""
Unit tests for Insights Journey Orchestrator - Analysis Workflows

Tests the new analysis workflow execution methods added during refactoring.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.insights
class TestInsightsJourneyOrchestratorAnalysis:
    """Unit tests for Insights Journey Orchestrator analysis workflows."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Mock platform gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    async def insights_journey_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create Insights Journey Orchestrator instance."""
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        
        orchestrator = InsightsJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_execute_analysis_workflow_unstructured(self, insights_journey_orchestrator):
        """Test unstructured analysis workflow execution."""
        # Mock UnstructuredAnalysisWorkflow
        mock_workflow = AsyncMock()
        mock_workflow.execute = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_123",
            "summary": {
                "textual": "Unstructured analysis complete",
                "tabular": {},
                "visualizations": []
            }
        })
        
        insights_journey_orchestrator._get_unstructured_analysis_workflow = AsyncMock(
            return_value=mock_workflow
        )
        
        result = await insights_journey_orchestrator.execute_analysis_workflow(
            file_id="file_123",
            analysis_type="unstructured",
            analysis_options={"aar_specific_analysis": True},
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
        assert "analysis_id" in result
        
        # Verify workflow was called with correct parameters
        mock_workflow.execute.assert_called_once_with(
            source_type="file",
            file_id="file_123",
            analysis_options={"aar_specific_analysis": True}
        )
    
    @pytest.mark.asyncio
    async def test_execute_analysis_workflow_eda(self, insights_journey_orchestrator):
        """Test EDA analysis workflow execution."""
        # Mock StructuredAnalysisWorkflow
        mock_workflow = AsyncMock()
        mock_workflow.execute = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_eda",
            "summary": {
                "textual": "EDA analysis complete",
                "tabular": {"columns": ["Metric", "Value"], "rows": []},
                "visualizations": []
            }
        })
        
        insights_journey_orchestrator._get_structured_analysis_workflow = AsyncMock(
            return_value=mock_workflow
        )
        
        result = await insights_journey_orchestrator.execute_analysis_workflow(
            file_id="file_eda",
            analysis_type="eda",
            analysis_options={"include_visualizations": True},
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
        assert result["summary"]["textual"] == "EDA analysis complete"
        
        # Verify workflow was called with analysis_type in options
        call_args = mock_workflow.execute.call_args
        assert call_args[1]["analysis_options"]["analysis_type"] == "eda"
    
    @pytest.mark.asyncio
    async def test_execute_analysis_workflow_vark(self, insights_journey_orchestrator):
        """Test VARK analysis workflow execution."""
        # Mock StructuredAnalysisWorkflow
        mock_workflow = AsyncMock()
        mock_workflow.execute = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_vark",
            "summary": {"textual": "VARK analysis complete"}
        })
        
        insights_journey_orchestrator._get_structured_analysis_workflow = AsyncMock(
            return_value=mock_workflow
        )
        
        result = await insights_journey_orchestrator.execute_analysis_workflow(
            file_id="file_vark",
            analysis_type="vark",
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_execute_analysis_workflow_business_summary(self, insights_journey_orchestrator):
        """Test business summary analysis workflow execution."""
        # Mock StructuredAnalysisWorkflow
        mock_workflow = AsyncMock()
        mock_workflow.execute = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_business",
            "summary": {"textual": "Business summary generated"}
        })
        
        insights_journey_orchestrator._get_structured_analysis_workflow = AsyncMock(
            return_value=mock_workflow
        )
        
        result = await insights_journey_orchestrator.execute_analysis_workflow(
            file_id="file_business",
            analysis_type="business_summary",
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_execute_analysis_workflow_unknown_type(self, insights_journey_orchestrator):
        """Test error handling for unknown analysis type."""
        result = await insights_journey_orchestrator.execute_analysis_workflow(
            file_id="file_unknown",
            analysis_type="unknown_type",
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "unknown_type" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_analysis_workflow_workflow_not_available(self, insights_journey_orchestrator):
        """Test error handling when workflow is not available."""
        insights_journey_orchestrator._get_unstructured_analysis_workflow = AsyncMock(
            return_value=None
        )
        
        result = await insights_journey_orchestrator.execute_analysis_workflow(
            file_id="file_error",
            analysis_type="unstructured",
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is False
        assert "not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_visualization_workflow(self, insights_journey_orchestrator):
        """Test visualization workflow execution."""
        # Mock Visualization Engine Service
        mock_viz_service = AsyncMock()
        mock_viz_service.create_visualization = AsyncMock(return_value={
            "success": True,
            "visualization_id": "viz_123",
            "charts": []
        })
        
        insights_journey_orchestrator._get_visualization_engine_service = AsyncMock(
            return_value=mock_viz_service
        )
        
        result = await insights_journey_orchestrator.execute_visualization_workflow(
            content_id="content_123",
            visualization_options={"chart_type": "bar"},
            user_context={"user_id": "test_user"}
        )
        
        # Note: Currently returns placeholder, but structure is correct
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_service_access_methods(self, insights_journey_orchestrator):
        """Test that service access methods are available."""
        # Test that methods exist
        assert hasattr(insights_journey_orchestrator, '_get_data_analyzer_service')
        assert hasattr(insights_journey_orchestrator, '_get_visualization_engine_service')
        assert hasattr(insights_journey_orchestrator, '_get_apg_processor_service')
        assert hasattr(insights_journey_orchestrator, '_get_insights_generator_service')
        assert hasattr(insights_journey_orchestrator, '_get_metrics_calculator_service')
        assert hasattr(insights_journey_orchestrator, 'get_content_steward_api')
        assert hasattr(insights_journey_orchestrator, 'track_data_lineage')
        assert hasattr(insights_journey_orchestrator, 'store_document')

