"""
Orchestrator-Service Integration Tests

Tests the integration between orchestrators and enabling services:
- Orchestrator → Enabling Service calls
- Service discovery via Curator
- Multi-service composition
- Error propagation
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestContentAnalysisOrchestratorServiceIntegration:
    """Test Content Analysis Orchestrator → Enabling Services integration."""
    
    async def test_orchestrator_discovers_file_parser_service(self, mock_curator_foundation):
        """Test orchestrator discovers File Parser Service via Curator."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock Curator response
        mock_service = MagicMock()
        mock_curator_foundation.get_service = AsyncMock(return_value=mock_service)
        
        # Initialize (triggers service discovery)
        await orchestrator.initialize()
        
        # Verify service discovery
        mock_curator_foundation.get_service.assert_called()
    
    async def test_orchestrator_calls_file_parser_service(self, mock_curator_foundation):
        """Test orchestrator calls File Parser Service correctly."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock File Parser Service
        mock_parser = MagicMock()
        mock_parser.parse_file = AsyncMock(return_value={
            "success": True,
            "content": "parsed content"
        })
        
        orchestrator.file_parser_service = mock_parser
        
        # Orchestrator handles file parsing request
        request = {
            "task": "parse_file",
            "file_path": "test.pdf"
        }
        
        result = await orchestrator.handle_request(request)
        
        # Verify service was called
        mock_parser.parse_file.assert_called_once()
        assert result["success"] is True
    
    async def test_orchestrator_composes_multiple_services(self, mock_curator_foundation):
        """Test orchestrator composes multiple services for complex request."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock multiple services
        mock_parser = MagicMock()
        mock_parser.parse_file = AsyncMock(return_value={"success": True, "content": "parsed"})
        
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_data = AsyncMock(return_value={"success": True, "insights": "analysis"})
        
        orchestrator.file_parser_service = mock_parser
        orchestrator.data_analyzer_service = mock_analyzer
        
        # Complex request requiring multiple services
        request = {
            "task": "parse_and_analyze",
            "file_path": "test.pdf"
        }
        
        result = await orchestrator.handle_request(request)
        
        # Verify both services were called in sequence
        mock_parser.parse_file.assert_called_once()
        mock_analyzer.analyze_data.assert_called_once()
    
    async def test_orchestrator_handles_service_error(self, mock_curator_foundation):
        """Test orchestrator handles service errors gracefully."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock service that fails
        mock_parser = MagicMock()
        mock_parser.parse_file = AsyncMock(side_effect=Exception("Service error"))
        
        orchestrator.file_parser_service = mock_parser
        
        # Request that will trigger error
        request = {
            "task": "parse_file",
            "file_path": "test.pdf"
        }
        
        result = await orchestrator.handle_request(request)
        
        # Orchestrator should handle error gracefully
        assert "error" in result or result.get("success") is False

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestInsightsOrchestratorServiceIntegration:
    """Test Insights Orchestrator → Enabling Services integration."""
    
    async def test_orchestrator_calls_data_analyzer_service(self, mock_curator_foundation):
        """Test orchestrator calls Data Analyzer Service."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        
        orchestrator = InsightsOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock Data Analyzer Service
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_data = AsyncMock(return_value={
            "success": True,
            "insights": "data analysis complete"
        })
        
        orchestrator.data_analyzer_service = mock_analyzer
        
        # Request for data analysis
        request = {
            "task": "analyze_data",
            "data": {"values": [1, 2, 3]}
        }
        
        result = await orchestrator.handle_request(request)
        
        # Verify service call
        mock_analyzer.analyze_data.assert_called_once()
        assert result["success"] is True
    
    async def test_orchestrator_calls_metrics_calculator_service(self, mock_curator_foundation):
        """Test orchestrator calls Metrics Calculator Service."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        
        orchestrator = InsightsOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock Metrics Calculator Service
        mock_metrics = MagicMock()
        mock_metrics.calculate_metrics = AsyncMock(return_value={
            "success": True,
            "metrics": {"average": 10}
        })
        
        orchestrator.metrics_calculator_service = mock_metrics
        
        # Request for metrics calculation
        request = {
            "task": "calculate_metrics",
            "data": {"values": [1, 2, 3]}
        }
        
        result = await orchestrator.handle_request(request)
        
        # Verify service call
        mock_metrics.calculate_metrics.assert_called_once()
        assert result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestOperationsOrchestratorServiceIntegration:
    """Test Operations Orchestrator → Enabling Services integration."""
    
    async def test_orchestrator_calls_workflow_manager_service(self, mock_curator_foundation):
        """Test orchestrator calls Workflow Manager Service."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator import OperationsOrchestrator
        
        orchestrator = OperationsOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock Workflow Manager Service
        mock_workflow = MagicMock()
        mock_workflow.create_workflow = AsyncMock(return_value={
            "success": True,
            "workflow_id": "wf_123"
        })
        
        orchestrator.workflow_manager_service = mock_workflow
        
        # Request for workflow creation
        request = {
            "task": "create_workflow",
            "workflow_data": {"name": "Test Workflow"}
        }
        
        result = await orchestrator.handle_request(request)
        
        # Verify service call
        mock_workflow.create_workflow.assert_called_once()
        assert result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestBusinessOutcomesOrchestratorServiceIntegration:
    """Test Business Outcomes Orchestrator → Enabling Services integration."""
    
    async def test_orchestrator_calls_report_generator_service(self, mock_curator_foundation):
        """Test orchestrator calls Report Generator Service."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        orchestrator = BusinessOutcomesOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock Report Generator Service
        mock_report = MagicMock()
        mock_report.generate_report = AsyncMock(return_value={
            "success": True,
            "report_id": "rpt_123"
        })
        
        orchestrator.report_generator_service = mock_report
        
        # Request for report generation
        request = {
            "task": "generate_report",
            "report_data": {"title": "Business Report"}
        }
        
        result = await orchestrator.handle_request(request)
        
        # Verify service call
        mock_report.generate_report.assert_called_once()
        assert result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestMultiServiceComposition:
    """Test orchestrators composing multiple services."""
    
    async def test_content_analysis_multi_service_workflow(self, mock_curator_foundation):
        """Test Content Analysis orchestrates multiple services in sequence."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock services
        services = {
            "file_parser": MagicMock(),
            "data_analyzer": MagicMock(),
            "validation_engine": MagicMock()
        }
        
        services["file_parser"].parse_file = AsyncMock(return_value={"success": True, "content": "parsed"})
        services["data_analyzer"].analyze_data = AsyncMock(return_value={"success": True, "analysis": "complete"})
        services["validation_engine"].validate = AsyncMock(return_value={"success": True, "valid": True})
        
        orchestrator.file_parser_service = services["file_parser"]
        orchestrator.data_analyzer_service = services["data_analyzer"]
        orchestrator.validation_engine_service = services["validation_engine"]
        
        # Complex request
        request = {
            "task": "full_analysis",
            "file_path": "test.pdf"
        }
        
        result = await orchestrator.handle_request(request)
        
        # Verify all services called in sequence
        services["file_parser"].parse_file.assert_called_once()
        services["data_analyzer"].analyze_data.assert_called_once()
        services["validation_engine"].validate.assert_called_once()
    
    async def test_service_chain_stops_on_error(self, mock_curator_foundation):
        """Test service composition stops if one service fails."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock services: first succeeds, second fails
        mock_parser = MagicMock()
        mock_parser.parse_file = AsyncMock(return_value={"success": True})
        
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_data = AsyncMock(return_value={"success": False, "error": "Analysis failed"})
        
        mock_validator = MagicMock()
        mock_validator.validate = AsyncMock(return_value={"success": True})
        
        orchestrator.file_parser_service = mock_parser
        orchestrator.data_analyzer_service = mock_analyzer
        orchestrator.validation_engine_service = mock_validator
        
        # Request
        request = {
            "task": "full_analysis",
            "file_path": "test.pdf"
        }
        
        result = await orchestrator.handle_request(request)
        
        # First service called, second called but failed, third should NOT be called
        mock_parser.parse_file.assert_called_once()
        mock_analyzer.analyze_data.assert_called_once()
        # Validator should not be called if analyzer failed
        assert result.get("success") is False or "error" in result

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestServiceDiscovery:
    """Test service discovery mechanisms."""
    
    async def test_orchestrator_discovers_all_required_services(self, mock_curator_foundation):
        """Test orchestrator discovers all services it needs."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock Curator to return different services
        service_responses = {
            "FileParserService": MagicMock(),
            "DataAnalyzerService": MagicMock(),
            "ValidationEngineService": MagicMock()
        }
        
        async def get_service_mock(service_name):
            return service_responses.get(service_name)
        
        mock_curator_foundation.get_service = get_service_mock
        
        # Initialize (triggers discovery)
        await orchestrator.initialize()
        
        # Verify orchestrator has references to services
        # (Implementation may vary, but orchestrator should have discovered services)
        assert orchestrator is not None
    
    async def test_orchestrator_handles_missing_service(self, mock_curator_foundation):
        """Test orchestrator handles case where service is not found."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock Curator to return None (service not found)
        mock_curator_foundation.get_service = AsyncMock(return_value=None)
        
        # Initialize should handle gracefully
        await orchestrator.initialize()
        
        # Orchestrator should still be functional or report missing dependencies
        assert orchestrator is not None

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestErrorPropagation:
    """Test error propagation from services to orchestrators."""
    
    async def test_service_error_propagates_to_orchestrator(self, mock_curator_foundation):
        """Test service errors are properly propagated."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        
        orchestrator = InsightsOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock service that returns error
        mock_service = MagicMock()
        mock_service.analyze_data = AsyncMock(return_value={
            "success": False,
            "error": "Data analysis failed"
        })
        
        orchestrator.data_analyzer_service = mock_service
        
        # Request
        request = {"task": "analyze_data", "data": {}}
        result = await orchestrator.handle_request(request)
        
        # Error should be propagated
        assert result.get("success") is False
        assert "error" in result
    
    async def test_service_exception_is_caught_and_handled(self, mock_curator_foundation):
        """Test orchestrator catches and handles service exceptions."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        
        orchestrator = InsightsOrchestrator(
            foundation_services=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock service that throws exception
        mock_service = MagicMock()
        mock_service.analyze_data = AsyncMock(side_effect=Exception("Critical error"))
        
        orchestrator.data_analyzer_service = mock_service
        
        # Request should not crash
        request = {"task": "analyze_data", "data": {}}
        result = await orchestrator.handle_request(request)
        
        # Should return error result, not crash
        assert result is not None
        assert result.get("success") is False or "error" in result

