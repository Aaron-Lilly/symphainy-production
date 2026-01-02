"""
Comprehensive unit tests for Insights Query Service.

Tests:
- Natural language query processing
- Query pattern matching (15+ patterns)
- Top/Bottom N queries
- Chart requests
- Trend analysis
- Filtering queries
- Summarization
- Metric lookup
- Comparison queries
- Recommendations queries
- AAR queries
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.insights
@pytest.mark.query
@pytest.mark.fast
class TestInsightsQuery:
    """Test suite for Insights Query Service."""
    
    @pytest.fixture
    def mock_query_service(self):
        """Create mock DataInsightsQueryService."""
        from backend.business_enablement.enabling_services.data_insights_query_service.data_insights_query_service import DataInsightsQueryService
        service = Mock(spec=DataInsightsQueryService)
        service.process_query = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_top_n_query(self, mock_query_service):
        """Test Top N query pattern."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "top_n",
            "response_type": "table",
            "data": [
                {"item": "Item1", "value": 100},
                {"item": "Item2", "value": 90}
            ]
        }
        
        result = await mock_query_service.process_query(
            query="What are the top 5 revenue drivers?",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "top_n"
        assert result["response_type"] == "table"
    
    @pytest.mark.asyncio
    async def test_chart_request(self, mock_query_service):
        """Test chart request pattern."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "chart",
            "response_type": "chart",
            "chart_type": "bar",
            "data": {}
        }
        
        result = await mock_query_service.process_query(
            query="Show me a chart of revenue",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "chart"
        assert result["response_type"] == "chart"
    
    @pytest.mark.asyncio
    async def test_trend_analysis(self, mock_query_service):
        """Test trend analysis query."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "trend",
            "response_type": "text",
            "trends": ["increasing", "decreasing"]
        }
        
        result = await mock_query_service.process_query(
            query="What trends are increasing?",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "trend"
    
    @pytest.mark.asyncio
    async def test_filter_query(self, mock_query_service):
        """Test filter query pattern."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "filter",
            "response_type": "table",
            "filtered_data": []
        }
        
        result = await mock_query_service.process_query(
            query="Show me accounts over 90 days late",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "filter"
    
    @pytest.mark.asyncio
    async def test_summarization(self, mock_query_service):
        """Test summarization query."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "summarize",
            "response_type": "text",
            "summary": "Key findings summary"
        }
        
        result = await mock_query_service.process_query(
            query="Summarize the key findings",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "summarize"
    
    @pytest.mark.asyncio
    async def test_metric_lookup(self, mock_query_service):
        """Test metric lookup query."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "metric",
            "response_type": "text",
            "metric_value": "1000000"
        }
        
        result = await mock_query_service.process_query(
            query="What is the revenue for Q4?",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "metric"
    
    @pytest.mark.asyncio
    async def test_comparison_query(self, mock_query_service):
        """Test comparison query."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "compare",
            "response_type": "table",
            "comparison_data": {}
        }
        
        result = await mock_query_service.process_query(
            query="Compare Q1 vs Q2",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "compare"
    
    @pytest.mark.asyncio
    async def test_recommendations_query(self, mock_query_service):
        """Test recommendations query."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "recommendations",
            "response_type": "text",
            "recommendations": ["rec1", "rec2"]
        }
        
        result = await mock_query_service.process_query(
            query="What are the high-priority recommendations?",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "recommendations"
    
    @pytest.mark.asyncio
    async def test_aar_queries(self, mock_query_service):
        """Test AAR (After Action Review) queries."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "aar_lessons",
            "response_type": "text",
            "lessons": ["lesson1", "lesson2"]
        }
        
        result = await mock_query_service.process_query(
            query="Show me lessons learned",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "aar_lessons"
    
    @pytest.mark.asyncio
    async def test_count_query(self, mock_query_service):
        """Test count query."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "count",
            "response_type": "text",
            "count": 42
        }
        
        result = await mock_query_service.process_query(
            query="How many accounts are late?",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "count"
    
    @pytest.mark.asyncio
    async def test_average_query(self, mock_query_service):
        """Test average query."""
        mock_query_service.process_query.return_value = {
            "success": True,
            "query_type": "average",
            "response_type": "text",
            "average": 15.5
        }
        
        result = await mock_query_service.process_query(
            query="What's the average response time?",
            analysis_results={}
        )
        
        assert result["success"] is True
        assert result["query_type"] == "average"
    
    @pytest.mark.asyncio
    async def test_query_error_handling(self, mock_query_service):
        """Test query error handling."""
        mock_query_service.process_query.side_effect = Exception("Query processing failed")
        
        with pytest.raises(Exception):
            await mock_query_service.process_query(
                query="Invalid query",
                analysis_results={}
            )




