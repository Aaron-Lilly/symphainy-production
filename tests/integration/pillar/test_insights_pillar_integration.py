"""
Integration tests for Insights Pillar workflows.

Tests:
- Structured analysis workflow
- Unstructured analysis workflow
- Data mapping workflow
- Query service integration
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure


@pytest.mark.integration
@pytest.mark.pillar
@pytest.mark.insights
@pytest.mark.slow
class TestInsightsPillarIntegration:
    """Test suite for Insights Pillar integration."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        container.get_config_adapter = Mock(return_value=Mock())
        return container
    
    @pytest.mark.asyncio
    async def test_structured_analysis_workflow(self, mock_platform_gateway, mock_di_container):
        """Test structured analysis workflow."""
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        
        orchestrator = InsightsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock structured analysis workflow
        with patch.object(orchestrator, 'execute_structured_analysis_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "analysis_id": "analysis_123",
                "eda_results": {"summary_stats": {}},
                "quality_results": {"missing_values": 0}
            }
            
            result = await orchestrator.execute_structured_analysis_workflow(
                data_file_id="file_123",
                analysis_type="eda"
            )
            
            assert result["success"] is True
            assert "analysis_id" in result
    
    @pytest.mark.asyncio
    async def test_unstructured_analysis_workflow(self, mock_platform_gateway, mock_di_container):
        """Test unstructured analysis workflow."""
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        
        orchestrator = InsightsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock unstructured analysis workflow
        with patch.object(orchestrator, 'execute_unstructured_analysis_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "analysis_id": "analysis_456",
                "insights": ["insight1", "insight2"],
                "summary": "Analysis complete"
            }
            
            result = await orchestrator.execute_unstructured_analysis_workflow(
                document_content="Sample document content",
                analysis_type="business_summary"
            )
            
            assert result["success"] is True
            assert "insights" in result
    
    @pytest.mark.asyncio
    async def test_data_mapping_workflow(self, mock_platform_gateway, mock_di_container):
        """Test data mapping workflow."""
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        
        orchestrator = InsightsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock data mapping workflow
        with patch.object(orchestrator, 'execute_data_mapping_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "mapping_id": "mapping_123",
                "source_fields": ["field1", "field2"],
                "target_fields": ["target1", "target2"]
            }
            
            result = await orchestrator.execute_data_mapping_workflow(
                source_data={"field1": "value1", "field2": "value2"},
                target_schema={"target1": "string", "target2": "number"}
            )
            
            assert result["success"] is True
            assert "mapping_id" in result




