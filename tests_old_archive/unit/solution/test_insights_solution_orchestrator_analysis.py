#!/usr/bin/env python3
"""
Unit tests for Insights Solution Orchestrator - Analysis Operations

Tests the new analysis orchestration methods added during refactoring.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.insights
class TestInsightsSolutionOrchestratorAnalysis:
    """Unit tests for Insights Solution Orchestrator analysis methods."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Mock platform gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    async def insights_solution_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create Insights Solution Orchestrator instance."""
        from backend.solution.services.insights_solution_orchestrator_service.insights_solution_orchestrator_service import InsightsSolutionOrchestratorService
        
        orchestrator = InsightsSolutionOrchestratorService(
            service_name="InsightsSolutionOrchestratorService",
            realm_name="solution",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock platform correlation services
        orchestrator.security_guard = AsyncMock()
        orchestrator.traffic_cop = AsyncMock()
        orchestrator.conductor = AsyncMock()
        orchestrator.post_office = AsyncMock()
        orchestrator.nurse = AsyncMock()
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrate_insights_analysis_eda(self, insights_solution_orchestrator):
        """Test EDA analysis orchestration."""
        # Mock Insights Journey Orchestrator
        mock_journey_orchestrator = AsyncMock()
        mock_journey_orchestrator.execute_analysis_workflow = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_123",
            "summary": {
                "textual": "EDA analysis complete",
                "tabular": {"columns": ["Metric", "Value"], "rows": []},
                "visualizations": []
            }
        })
        
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=mock_journey_orchestrator
        )
        
        # Mock platform correlation
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": "workflow_123",
            "user_id": "test_user",
            "session_id": "session_123"
        })
        
        insights_solution_orchestrator._record_platform_correlation_completion = AsyncMock()
        
        result = await insights_solution_orchestrator.orchestrate_insights_analysis(
            file_id="file_123",
            analysis_type="eda",
            analysis_options={"include_visualizations": True},
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        assert result["success"] is True
        assert "analysis_id" in result
        assert result["summary"]["textual"] == "EDA analysis complete"
        
        # Verify platform correlation was called
        insights_solution_orchestrator._orchestrate_platform_correlation.assert_called_once()
        insights_solution_orchestrator._record_platform_correlation_completion.assert_called_once()
        
        # Verify Journey Orchestrator was called
        mock_journey_orchestrator.execute_analysis_workflow.assert_called_once_with(
            file_id="file_123",
            analysis_type="eda",
            analysis_options={"include_visualizations": True},
            user_context={"workflow_id": "workflow_123", "user_id": "test_user", "session_id": "session_123"}
        )
    
    @pytest.mark.asyncio
    async def test_orchestrate_insights_analysis_unstructured(self, insights_solution_orchestrator):
        """Test unstructured analysis orchestration."""
        # Mock Insights Journey Orchestrator
        mock_journey_orchestrator = AsyncMock()
        mock_journey_orchestrator.execute_analysis_workflow = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_456",
            "summary": {
                "textual": "Unstructured analysis complete",
                "tabular": {},
                "visualizations": []
            },
            "aar_analysis": {
                "lessons_learned": [],
                "risks": [],
                "recommendations": []
            }
        })
        
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=mock_journey_orchestrator
        )
        
        # Mock platform correlation
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": "workflow_456"
        })
        
        insights_solution_orchestrator._record_platform_correlation_completion = AsyncMock()
        
        result = await insights_solution_orchestrator.orchestrate_insights_analysis(
            file_id="file_456",
            analysis_type="unstructured",
            analysis_options={"aar_specific_analysis": True},
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
        assert "analysis_id" in result
        assert "aar_analysis" in result
        
        # Verify Journey Orchestrator was called with correct type
        mock_journey_orchestrator.execute_analysis_workflow.assert_called_once_with(
            file_id="file_456",
            analysis_type="unstructured",
            analysis_options={"aar_specific_analysis": True},
            user_context={"workflow_id": "workflow_456"}  # user_id is not passed through in user_context
        )
    
    @pytest.mark.asyncio
    async def test_orchestrate_insights_analysis_business_summary(self, insights_solution_orchestrator):
        """Test business summary analysis orchestration."""
        # Mock Insights Journey Orchestrator
        mock_journey_orchestrator = AsyncMock()
        mock_journey_orchestrator.execute_analysis_workflow = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_789",
            "summary": {
                "textual": "Business summary generated"
            }
        })
        
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=mock_journey_orchestrator
        )
        
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": "workflow_789"
        })
        
        insights_solution_orchestrator._record_platform_correlation_completion = AsyncMock()
        
        result = await insights_solution_orchestrator.orchestrate_insights_analysis(
            file_id="file_789",
            analysis_type="business_summary",
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
        assert result["summary"]["textual"] == "Business summary generated"
    
    @pytest.mark.asyncio
    async def test_orchestrate_insights_analysis_vark(self, insights_solution_orchestrator):
        """Test VARK analysis orchestration."""
        # Mock Insights Journey Orchestrator
        mock_journey_orchestrator = AsyncMock()
        mock_journey_orchestrator.execute_analysis_workflow = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_vark",
            "summary": {
                "textual": "VARK analysis complete"
            }
        })
        
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=mock_journey_orchestrator
        )
        
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": "workflow_vark"
        })
        
        insights_solution_orchestrator._record_platform_correlation_completion = AsyncMock()
        
        result = await insights_solution_orchestrator.orchestrate_insights_analysis(
            file_id="file_vark",
            analysis_type="vark",
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
        assert result["summary"]["textual"] == "VARK analysis complete"
    
    @pytest.mark.asyncio
    async def test_orchestrate_insights_analysis_error_handling(self, insights_solution_orchestrator):
        """Test error handling in analysis orchestration."""
        # Mock Journey Orchestrator discovery failure
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=None
        )
        
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": "workflow_error"
        })
        
        result = await insights_solution_orchestrator.orchestrate_insights_analysis(
            file_id="file_error",
            analysis_type="eda",
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "workflow_id" in result
    
    @pytest.mark.asyncio
    async def test_orchestrate_insights_visualization(self, insights_solution_orchestrator):
        """Test visualization orchestration."""
        # Mock Insights Journey Orchestrator
        mock_journey_orchestrator = AsyncMock()
        mock_journey_orchestrator.execute_visualization_workflow = AsyncMock(return_value={
            "success": True,
            "visualization_id": "viz_123",
            "visualization_data": {
                "charts": [{"type": "bar", "data": []}]
            }
        })
        
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=mock_journey_orchestrator
        )
        
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": "workflow_viz"
        })
        
        insights_solution_orchestrator._record_platform_correlation_completion = AsyncMock()
        
        result = await insights_solution_orchestrator.orchestrate_insights_visualization(
            content_id="content_123",
            visualization_options={"chart_type": "bar"},
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
        assert "visualization_id" in result
        assert "visualization_data" in result
        
        # Verify Journey Orchestrator was called
        mock_journey_orchestrator.execute_visualization_workflow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_request_analyze(self, insights_solution_orchestrator):
        """Test handle_request routing for analyze endpoint."""
        # Mock orchestrate_insights_analysis
        insights_solution_orchestrator.orchestrate_insights_analysis = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_123"
        })
        
        result = await insights_solution_orchestrator.handle_request(
            method="POST",
            path="analyze",
            params={
                "file_id": "file_123",
                "analysis_type": "eda",
                "analysis_options": {}
            },
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
        insights_solution_orchestrator.orchestrate_insights_analysis.assert_called_once_with(
            file_id="file_123",
            analysis_type="eda",
            analysis_options={},
            user_context={"user_id": "test_user"}
        )
    
    @pytest.mark.asyncio
    async def test_handle_request_mapping(self, insights_solution_orchestrator):
        """Test handle_request routing for mapping endpoint."""
        # Mock orchestrate_insights_mapping
        insights_solution_orchestrator.orchestrate_insights_mapping = AsyncMock(return_value={
            "success": True,
            "mapping_id": "mapping_123"
        })
        
        result = await insights_solution_orchestrator.handle_request(
            method="POST",
            path="mapping",
            params={
                "source_file_id": "source_123",
                "target_file_id": "target_456",
                "mapping_options": {}
            },
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is True
        insights_solution_orchestrator.orchestrate_insights_mapping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_request_route_not_found(self, insights_solution_orchestrator):
        """Test handle_request for unknown route."""
        result = await insights_solution_orchestrator.handle_request(
            method="POST",
            path="unknown",
            params={},
            user_context={}
        )
        
        assert result["success"] is False
        assert result["error"] == "Route not found"

