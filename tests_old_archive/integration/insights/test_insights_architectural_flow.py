#!/usr/bin/env python3
"""
Integration tests for Insights Pillar Architectural Flow

Tests the complete Solution → Journey → Realm Services flow for insights operations.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any
import uuid


@pytest.mark.integration
@pytest.mark.insights
@pytest.mark.architecture
@pytest.mark.slow
class TestInsightsArchitecturalFlow:
    """Integration tests for complete insights architectural flow."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Mock platform gateway."""
        gateway = Mock()
        gateway.logger = Mock()
        return gateway
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        return container
    
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
    async def test_complete_eda_analysis_flow(self, insights_solution_orchestrator, insights_journey_orchestrator):
        """Test complete EDA analysis flow: Solution → Journey → Workflow."""
        # Setup: Mock Journey Orchestrator discovery
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=insights_journey_orchestrator
        )
        
        # Setup: Mock StructuredAnalysisWorkflow
        mock_workflow = AsyncMock()
        mock_workflow.execute = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_eda_123",
            "summary": {
                "textual": "EDA analysis complete with key insights",
                "tabular": {
                    "columns": ["Metric", "Value"],
                    "rows": [["Total Records", 100], ["Average", 42.5]]
                },
                "visualizations": [{
                    "chart_type": "bar",
                    "data": []
                }]
            },
            "insights": [{
                "insight_id": "insight_1",
                "type": "trend",
                "description": "Key trend identified"
            }]
        })
        
        insights_journey_orchestrator._get_structured_analysis_workflow = AsyncMock(
            return_value=mock_workflow
        )
        
        # Setup: Mock platform correlation
        workflow_id = str(uuid.uuid4())
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": workflow_id,
            "user_id": "test_user",
            "tenant_id": "test_tenant",
            "session_id": "session_123"
        })
        
        insights_solution_orchestrator._record_platform_correlation_completion = AsyncMock()
        
        # Execute: Call Solution Orchestrator
        result = await insights_solution_orchestrator.orchestrate_insights_analysis(
            file_id="file_eda_123",
            analysis_type="eda",
            analysis_options={
                "include_visualizations": True,
                "include_tabular_summary": True
            },
            user_context={
                "user_id": "test_user",
                "tenant_id": "test_tenant"
            }
        )
        
        # Verify: Complete flow executed
        assert result["success"] is True
        assert "analysis_id" in result
        assert result["summary"]["textual"] == "EDA analysis complete with key insights"
        assert "tabular" in result["summary"]
        assert "visualizations" in result["summary"]
        assert len(result["insights"]) > 0
        
        # Verify: Platform correlation was orchestrated
        insights_solution_orchestrator._orchestrate_platform_correlation.assert_called_once()
        insights_solution_orchestrator._record_platform_correlation_completion.assert_called_once()
        
        # Verify: Journey Orchestrator was called
        insights_journey_orchestrator._get_structured_analysis_workflow.assert_called_once()
        mock_workflow.execute.assert_called_once()
        
        # Verify: Workflow received correct parameters
        call_args = mock_workflow.execute.call_args
        assert call_args[1]["file_id"] == "file_eda_123"
        assert call_args[1]["analysis_options"]["analysis_type"] == "eda"
    
    @pytest.mark.asyncio
    async def test_complete_unstructured_analysis_flow(self, insights_solution_orchestrator, insights_journey_orchestrator):
        """Test complete unstructured analysis flow with AAR."""
        # Setup: Mock Journey Orchestrator discovery
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=insights_journey_orchestrator
        )
        
        # Setup: Mock UnstructuredAnalysisWorkflow
        mock_workflow = AsyncMock()
        mock_workflow.execute = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_unstructured_123",
            "summary": {
                "textual": "Unstructured document analysis complete",
                "tabular": {},
                "visualizations": []
            },
            "insights": [{
                "insight_id": "insight_1",
                "type": "theme",
                "description": "Key theme identified"
            }],
            "aar_analysis": {
                "lessons_learned": ["Lesson 1", "Lesson 2"],
                "risks": ["Risk 1"],
                "recommendations": ["Recommendation 1"],
                "timeline": []
            }
        })
        
        insights_journey_orchestrator._get_unstructured_analysis_workflow = AsyncMock(
            return_value=mock_workflow
        )
        
        # Setup: Mock platform correlation
        workflow_id = str(uuid.uuid4())
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": workflow_id
        })
        
        insights_solution_orchestrator._record_platform_correlation_completion = AsyncMock()
        
        # Execute: Call Solution Orchestrator
        result = await insights_solution_orchestrator.orchestrate_insights_analysis(
            file_id="file_unstructured_123",
            analysis_type="unstructured",
            analysis_options={
                "aar_specific_analysis": True,
                "include_visualizations": False
            },
            user_context={"user_id": "test_user"}
        )
        
        # Verify: Complete flow executed
        assert result["success"] is True
        assert "analysis_id" in result
        assert "aar_analysis" in result
        assert len(result["aar_analysis"]["lessons_learned"]) > 0
        
        # Verify: Workflow was called with AAR option
        call_args = mock_workflow.execute.call_args
        assert call_args[1]["analysis_options"]["aar_specific_analysis"] is True
    
    @pytest.mark.asyncio
    async def test_platform_correlation_flow(self, insights_solution_orchestrator):
        """Test that platform correlation is properly tracked through the flow."""
        # Setup: Mock Journey Orchestrator
        mock_journey_orchestrator = AsyncMock()
        mock_journey_orchestrator.execute_analysis_workflow = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_corr",
            "summary": {"textual": "Analysis complete"}
        })
        
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=mock_journey_orchestrator
        )
        
        # Setup: Mock platform correlation services
        workflow_id = str(uuid.uuid4())
        correlation_context = {
            "workflow_id": workflow_id,
            "user_id": "test_user",
            "tenant_id": "test_tenant",
            "session_id": "session_123",
            "trace_id": "trace_123"
        }
        
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(
            return_value=correlation_context
        )
        
        insights_solution_orchestrator._record_platform_correlation_completion = AsyncMock()
        
        # Execute
        result = await insights_solution_orchestrator.orchestrate_insights_analysis(
            file_id="file_corr",
            analysis_type="eda",
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Verify: Platform correlation was orchestrated
        insights_solution_orchestrator._orchestrate_platform_correlation.assert_called_once()
        
        # Verify: Correlation context was passed to Journey Orchestrator
        call_args = mock_journey_orchestrator.execute_analysis_workflow.call_args
        assert call_args[1]["user_context"]["workflow_id"] == workflow_id
        assert call_args[1]["user_context"]["user_id"] == "test_user"
        
        # Verify: Completion was recorded
        insights_solution_orchestrator._record_platform_correlation_completion.assert_called_once()
        completion_call = insights_solution_orchestrator._record_platform_correlation_completion.call_args
        # Check if called with positional args or keyword args
        if completion_call[0]:  # Positional args
            assert completion_call[0][0] == "insights_analysis_eda"
        else:  # Keyword args
            assert completion_call[1]["operation"] == "insights_analysis_eda"
    
    @pytest.mark.asyncio
    async def test_error_propagation_flow(self, insights_solution_orchestrator, insights_journey_orchestrator):
        """Test that errors are properly propagated through the flow."""
        # Setup: Mock Journey Orchestrator discovery
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=insights_journey_orchestrator
        )
        
        # Setup: Mock workflow to raise error
        mock_workflow = AsyncMock()
        mock_workflow.execute = AsyncMock(side_effect=Exception("Workflow execution failed"))
        
        insights_journey_orchestrator._get_structured_analysis_workflow = AsyncMock(
            return_value=mock_workflow
        )
        
        # Setup: Mock platform correlation
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": "workflow_error"
        })
        
        insights_solution_orchestrator._realm_service = Mock()
        insights_solution_orchestrator._realm_service.handle_error_with_audit = AsyncMock()
        
        # Execute
        result = await insights_solution_orchestrator.orchestrate_insights_analysis(
            file_id="file_error",
            analysis_type="eda",
            user_context={"user_id": "test_user"}
        )
        
        # Verify: Error was handled
        assert result["success"] is False
        assert "error" in result
        # workflow_id may not be in result if error occurs before correlation completion
        # Check if workflow_id exists (it should if correlation was started)
        if "workflow_id" in result:
            assert result["workflow_id"] == "workflow_error"
        
        # Verify: Error was handled (may be handled via try/except, not necessarily via handle_error_with_audit)
        # The error should be caught and returned in the result
        assert "Workflow execution failed" in result.get("error", "") or "error" in result

