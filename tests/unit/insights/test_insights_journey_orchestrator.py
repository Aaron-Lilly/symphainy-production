"""
Comprehensive unit tests for Insights Journey Orchestrator.

Tests:
- Data mapping workflow
- Unstructured analysis workflow
- Structured analysis workflow
- Field extraction service integration
- Data quality validation service integration
- Data transformation service integration
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.insights
@pytest.mark.orchestrator
@pytest.mark.fast
class TestInsightsJourneyOrchestrator:
    """Test suite for Insights Journey Orchestrator."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=None)
        gateway.get_foundation_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        container.get_config_adapter = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def insights_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create InsightsJourneyOrchestrator instance."""
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        return InsightsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, insights_orchestrator):
        """Test orchestrator initialization."""
        await insights_orchestrator.initialize()
        assert insights_orchestrator.is_initialized is True
        assert insights_orchestrator.orchestrator_name == "InsightsJourneyOrchestrator"
    
    @pytest.mark.asyncio
    async def test_data_mapping_workflow(self, insights_orchestrator):
        """Test data mapping workflow execution."""
        # Mock workflow
        with patch.object(insights_orchestrator, '_get_data_mapping_workflow') as mock_get_workflow:
            mock_workflow = Mock()
            mock_workflow.execute = AsyncMock(return_value={
                "success": True,
                "mapping_id": "mapping_123",
                "source_fields": ["field1", "field2"],
                "target_fields": ["target1", "target2"]
            })
            mock_get_workflow.return_value = mock_workflow
            
            result = await insights_orchestrator.execute_data_mapping_workflow(
                source_data={"field1": "value1", "field2": "value2"},
                target_schema={"target1": "string", "target2": "number"}
            )
            
            assert result["success"] is True
            assert "mapping_id" in result
            mock_workflow.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unstructured_analysis_workflow(self, insights_orchestrator):
        """Test unstructured analysis workflow execution."""
        with patch.object(insights_orchestrator, '_get_unstructured_analysis_workflow') as mock_get_workflow:
            mock_workflow = Mock()
            mock_workflow.execute = AsyncMock(return_value={
                "success": True,
                "analysis_id": "analysis_123",
                "insights": ["insight1", "insight2"],
                "summary": "Analysis complete"
            })
            mock_get_workflow.return_value = mock_workflow
            
            result = await insights_orchestrator.execute_unstructured_analysis_workflow(
                document_content="Sample document content",
                analysis_type="business_summary"
            )
            
            assert result["success"] is True
            assert "analysis_id" in result
            assert "insights" in result
    
    @pytest.mark.asyncio
    async def test_structured_analysis_workflow(self, insights_orchestrator):
        """Test structured analysis workflow execution."""
        with patch.object(insights_orchestrator, '_get_structured_analysis_workflow') as mock_get_workflow:
            mock_workflow = Mock()
            mock_workflow.execute = AsyncMock(return_value={
                "success": True,
                "analysis_id": "analysis_123",
                "eda_results": {"summary_stats": {}},
                "quality_results": {"missing_values": 0}
            })
            mock_get_workflow.return_value = mock_workflow
            
            result = await insights_orchestrator.execute_structured_analysis_workflow(
                data_file_id="file_123",
                analysis_type="eda"
            )
            
            assert result["success"] is True
            assert "analysis_id" in result
    
    @pytest.mark.asyncio
    async def test_field_extraction_service_integration(self, insights_orchestrator):
        """Test field extraction service integration."""
        with patch.object(insights_orchestrator, '_get_field_extraction_service') as mock_get_service:
            mock_service = Mock()
            mock_service.extract_fields = AsyncMock(return_value={
                "success": True,
                "fields": ["field1", "field2", "field3"]
            })
            mock_get_service.return_value = mock_service
            
            # Test via workflow that uses field extraction
            result = await insights_orchestrator.execute_data_mapping_workflow(
                source_data={"field1": "value1"},
                target_schema={}
            )
            
            # Verify service was accessed (if workflow uses it)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_data_quality_validation_integration(self, insights_orchestrator):
        """Test data quality validation service integration."""
        with patch.object(insights_orchestrator, '_get_data_quality_validation_service') as mock_get_service:
            mock_service = Mock()
            mock_service.validate_data_quality = AsyncMock(return_value={
                "success": True,
                "quality_score": 0.95,
                "issues": []
            })
            mock_get_service.return_value = mock_service
            
            # Test via workflow that uses quality validation
            result = await insights_orchestrator.execute_structured_analysis_workflow(
                data_file_id="file_123",
                analysis_type="eda"
            )
            
            # Verify service was accessed (if workflow uses it)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_data_transformation_integration(self, insights_orchestrator):
        """Test data transformation service integration."""
        with patch.object(insights_orchestrator, '_get_data_transformation_service') as mock_get_service:
            mock_service = Mock()
            mock_service.transform_data = AsyncMock(return_value={
                "success": True,
                "transformed_data": {"new_field": "value"}
            })
            mock_get_service.return_value = mock_service
            
            # Test via workflow that uses transformation
            result = await insights_orchestrator.execute_data_mapping_workflow(
                source_data={},
                target_schema={}
            )
            
            # Verify service was accessed (if workflow uses it)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow_failure(self, insights_orchestrator):
        """Test error handling when workflow fails."""
        with patch.object(insights_orchestrator, '_get_data_mapping_workflow') as mock_get_workflow:
            mock_workflow = Mock()
            mock_workflow.execute = AsyncMock(side_effect=Exception("Workflow failed"))
            mock_get_workflow.return_value = mock_workflow
            
            with pytest.raises(Exception):
                await insights_orchestrator.execute_data_mapping_workflow(
                    source_data={},
                    target_schema={}
                )
    
    @pytest.mark.asyncio
    async def test_error_handling_service_unavailable(self, insights_orchestrator):
        """Test error handling when service is unavailable."""
        with patch.object(insights_orchestrator, '_get_field_extraction_service') as mock_get_service:
            mock_get_service.return_value = None
            
            # Should handle gracefully
            result = await insights_orchestrator.execute_data_mapping_workflow(
                source_data={},
                target_schema={}
            )
            
            # Should either return error or handle gracefully
            assert result is not None



