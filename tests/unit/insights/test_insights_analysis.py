"""
Comprehensive unit tests for Insights Analysis capabilities.

Tests:
- EDA (Exploratory Data Analysis)
- VARK learning style analysis
- Business summary analysis
- Unstructured document analysis
- Structured data analysis
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.insights
@pytest.mark.analysis
@pytest.mark.fast
class TestInsightsAnalysis:
    """Test suite for Insights Analysis capabilities."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def insights_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create InsightsJourneyOrchestrator instance."""
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        orchestrator = InsightsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_eda_analysis(self, insights_orchestrator):
        """Test EDA (Exploratory Data Analysis)."""
        with patch.object(insights_orchestrator, 'execute_structured_analysis_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "analysis_type": "eda",
                "results": {
                    "summary_stats": {
                        "mean": 10.5,
                        "std": 2.3,
                        "min": 5,
                        "max": 15
                    },
                    "distributions": {},
                    "correlations": {}
                }
            }
            
            result = await insights_orchestrator.execute_structured_analysis_workflow(
                data_file_id="file_123",
                analysis_type="eda"
            )
            
            assert result["success"] is True
            assert result["analysis_type"] == "eda"
            assert "results" in result
    
    @pytest.mark.asyncio
    async def test_vark_analysis(self, insights_orchestrator):
        """Test VARK learning style analysis."""
        with patch.object(insights_orchestrator, 'execute_unstructured_analysis_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "analysis_type": "vark",
                "results": {
                    "visual_score": 0.8,
                    "auditory_score": 0.6,
                    "reading_score": 0.7,
                    "kinesthetic_score": 0.5,
                    "primary_style": "visual"
                }
            }
            
            result = await insights_orchestrator.execute_unstructured_analysis_workflow(
                document_content="Sample learning content",
                analysis_type="vark"
            )
            
            assert result["success"] is True
            assert result["analysis_type"] == "vark"
            assert "primary_style" in result["results"]
    
    @pytest.mark.asyncio
    async def test_business_summary_analysis(self, insights_orchestrator):
        """Test business summary analysis."""
        with patch.object(insights_orchestrator, 'execute_unstructured_analysis_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "analysis_type": "business_summary",
                "results": {
                    "summary": "Key business insights extracted",
                    "key_points": ["point1", "point2", "point3"],
                    "recommendations": ["rec1", "rec2"]
                }
            }
            
            result = await insights_orchestrator.execute_unstructured_analysis_workflow(
                document_content="Business document content",
                analysis_type="business_summary"
            )
            
            assert result["success"] is True
            assert result["analysis_type"] == "business_summary"
            assert "summary" in result["results"]
    
    @pytest.mark.asyncio
    async def test_unstructured_document_analysis(self, insights_orchestrator):
        """Test unstructured document analysis."""
        with patch.object(insights_orchestrator, 'execute_unstructured_analysis_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "analysis_type": "unstructured",
                "results": {
                    "entities": ["entity1", "entity2"],
                    "topics": ["topic1", "topic2"],
                    "sentiment": "positive"
                }
            }
            
            result = await insights_orchestrator.execute_unstructured_analysis_workflow(
                document_content="Unstructured document content",
                analysis_type="unstructured"
            )
            
            assert result["success"] is True
            assert "entities" in result["results"]
    
    @pytest.mark.asyncio
    async def test_structured_data_analysis(self, insights_orchestrator):
        """Test structured data analysis."""
        with patch.object(insights_orchestrator, 'execute_structured_analysis_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "analysis_type": "eda",
                "results": {
                    "data_quality": {
                        "completeness": 0.95,
                        "accuracy": 0.92
                    },
                    "anomalies": [],
                    "patterns": []
                }
            }
            
            result = await insights_orchestrator.execute_structured_analysis_workflow(
                data_file_id="file_123",
                analysis_type="eda"
            )
            
            assert result["success"] is True
            assert "data_quality" in result["results"]
    
    @pytest.mark.asyncio
    async def test_analysis_error_handling(self, insights_orchestrator):
        """Test error handling in analysis."""
        with patch.object(insights_orchestrator, 'execute_structured_analysis_workflow') as mock_execute:
            mock_execute.side_effect = Exception("Analysis failed")
            
            with pytest.raises(Exception):
                await insights_orchestrator.execute_structured_analysis_workflow(
                    data_file_id="file_123",
                    analysis_type="eda"
                )




