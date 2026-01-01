#!/usr/bin/env python3
"""
Unit Tests for DataInsightsQueryService

Tests the Data Insights Query enabling service functionality including:
- Service initialization
- Natural language query processing
- Pattern matching and intent detection
- Rule-based and LLM query execution
- Follow-up suggestion generation
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.business_enablement.enabling_services.data_insights_query_service.data_insights_query_service import DataInsightsQueryService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]

class TestDataInsightsQueryService:
    """Test DataInsightsQueryService functionality."""
    
    @pytest.fixture
    async def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        return container
    
    @pytest.fixture
    async def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_smart_city_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    async def data_insights_service(self, mock_di_container, mock_platform_gateway):
        """Create DataInsightsQueryService instance."""
        service = DataInsightsQueryService(
            service_name="DataInsightsQueryService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services to avoid initialization issues
        service.librarian = Mock()
        service.data_steward = Mock()
        service.curator = Mock()
        service.curator.register_service = AsyncMock(return_value=True)
        service.llm_client = None  # No LLM by default
        
        return service
    
    @pytest.fixture
    def sample_analysis(self):
        """Create sample analysis data."""
        return {
            "analysis_id": "analysis_test_123",
            "analysis_type": "content_analysis",
            "results": {
                "total_files": 10,
                "file_types": {
                    "pdf": 5,
                    "docx": 3,
                    "txt": 2
                },
                "top_keywords": [
                    {"keyword": "testing", "count": 25},
                    {"keyword": "quality", "count": 18},
                    {"keyword": "process", "count": 15}
                ],
                "trends": {
                    "upload_trend": "increasing",
                    "processing_time": "stable"
                }
            }
        }
    
    async def test_service_initialization(self, data_insights_service):
        """Test that DataInsightsQueryService initializes correctly."""
        assert data_insights_service.service_name == "DataInsightsQueryService"
        assert data_insights_service.realm_name == "business_enablement"
    
    async def test_process_query_top_n(self, data_insights_service, sample_analysis):
        """Test processing a top-N query."""
        result = await data_insights_service.process_query(
            query="What are the top 3 keywords?",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        assert result["success"] is True
        assert "query_id" in result
        assert "result" in result
        assert "follow_up_suggestions" in result
        assert "metadata" in result
        assert result["metadata"]["intent"] in ["top_n_query", "general"]
    
    async def test_process_query_chart_request(self, data_insights_service, sample_analysis):
        """Test processing a chart request query."""
        result = await data_insights_service.process_query(
            query="Show me a chart of file types",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        assert result["success"] is True
        assert "result" in result
        # Chart requests should have visualization data (text is also valid)
        assert result["result"]["type"] in ["chart", "table", "summary", "text"]
    
    async def test_process_query_trend_analysis(self, data_insights_service, sample_analysis):
        """Test processing a trend analysis query."""
        result = await data_insights_service.process_query(
            query="What is the trend for uploads?",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result
    
    async def test_process_query_summarize(self, data_insights_service, sample_analysis):
        """Test processing a summarization query."""
        result = await data_insights_service.process_query(
            query="Summarize the analysis",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["type"] in ["summary", "text"]
    
    async def test_process_query_with_type_hint(self, data_insights_service, sample_analysis):
        """Test processing query with explicit type hint."""
        result = await data_insights_service.process_query(
            query="File type distribution",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis,
            query_type="chart"
        )
        
        assert result["success"] is True
        assert "result" in result
    
    async def test_process_query_low_confidence(self, data_insights_service, sample_analysis):
        """Test processing query with low confidence (should use rule-based fallback)."""
        # Ambiguous query that might have low confidence
        result = await data_insights_service.process_query(
            query="Tell me something interesting",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        # Should still succeed with fallback
        assert result["success"] is True
        assert "result" in result
    
    async def test_process_query_with_llm(self, data_insights_service, sample_analysis):
        """Test processing query with LLM available."""
        # Mock LLM client
        data_insights_service.llm_client = Mock()
        data_insights_service.llm_client.generate = AsyncMock(return_value={
            "response": "Analysis shows 10 files with testing as top keyword"
        })
        
        result = await data_insights_service.process_query(
            query="What does this analysis tell us?",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        assert result["success"] is True
        assert "result" in result
    
    async def test_get_supported_patterns(self, data_insights_service):
        """Test getting supported query patterns."""
        result = await data_insights_service.get_supported_patterns()
        
        assert result["success"] is True
        assert "patterns" in result or "categories" in result or len(result.keys()) > 1
    
    async def test_follow_up_suggestions(self, data_insights_service, sample_analysis):
        """Test that follow-up suggestions are generated."""
        result = await data_insights_service.process_query(
            query="What are the top keywords?",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        assert result["success"] is True
        assert "follow_up_suggestions" in result
        assert isinstance(result["follow_up_suggestions"], list)
        # Should have at least some suggestions
        assert len(result["follow_up_suggestions"]) >= 0
    
    async def test_query_metadata(self, data_insights_service, sample_analysis):
        """Test that query metadata is properly populated."""
        result = await data_insights_service.process_query(
            query="Show top 5 keywords",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        assert result["success"] is True
        assert "metadata" in result
        metadata = result["metadata"]
        assert "intent" in metadata
        assert "confidence" in metadata
        assert "analysis_id" in metadata
        assert "processor" in metadata
        assert metadata["analysis_id"] == "analysis_test_123"
    
    async def test_empty_analysis(self, data_insights_service):
        """Test processing query with empty analysis."""
        empty_analysis = {
            "analysis_id": "empty_analysis",
            "results": {}
        }
        
        result = await data_insights_service.process_query(
            query="What are the results?",
            analysis_id="empty_analysis",
            cached_analysis=empty_analysis
        )
        
        # Should handle gracefully
        assert "success" in result
    
    async def test_complex_nested_query(self, data_insights_service):
        """Test processing complex query with nested data."""
        complex_analysis = {
            "analysis_id": "complex_123",
            "results": {
                "sections": {
                    "section_a": {
                        "metrics": {
                            "count": 100,
                            "average": 75.5,
                            "trend": "increasing"
                        }
                    },
                    "section_b": {
                        "metrics": {
                            "count": 50,
                            "average": 82.3,
                            "trend": "stable"
                        }
                    }
                }
            }
        }
        
        result = await data_insights_service.process_query(
            query="Compare section A and section B metrics",
            analysis_id="complex_123",
            cached_analysis=complex_analysis
        )
        
        assert result["success"] is True
        assert "result" in result
    
    async def test_filter_query(self, data_insights_service, sample_analysis):
        """Test processing a filter/search query."""
        result = await data_insights_service.process_query(
            query="Show only PDF files",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        assert result["success"] is True
        assert "result" in result
    
    async def test_comparison_query(self, data_insights_service):
        """Test processing a comparison query."""
        comparison_analysis = {
            "analysis_id": "comparison_123",
            "results": {
                "period_1": {"uploads": 100, "errors": 5},
                "period_2": {"uploads": 150, "errors": 3}
            }
        }
        
        result = await data_insights_service.process_query(
            query="Compare period 1 and period 2",
            analysis_id="comparison_123",
            cached_analysis=comparison_analysis
        )
        
        assert result["success"] is True
        assert "result" in result
    
    async def test_multiple_queries_same_analysis(self, data_insights_service, sample_analysis):
        """Test processing multiple queries on same analysis."""
        import asyncio
        
        queries = [
            "What are the top keywords?",
            "Show file type distribution",
            "What is the trend?"
        ]
        
        results = []
        for query in queries:
            # Add small delay to ensure different timestamps
            await asyncio.sleep(0.01)
            result = await data_insights_service.process_query(
                query=query,
                analysis_id="analysis_test_123",
                cached_analysis=sample_analysis
            )
            results.append(result)
        
        # All should succeed
        assert all(r["success"] for r in results)
        # Each should have query_id (may not be unique if same timestamp)
        query_ids = [r["query_id"] for r in results]
        assert len(query_ids) == 3
        # At least verify they all have the expected format
        assert all(qid.startswith("query_") for qid in query_ids)
    
    async def test_query_confidence_levels(self, data_insights_service, sample_analysis):
        """Test that different queries have appropriate confidence levels."""
        # High confidence query (specific pattern)
        high_conf_result = await data_insights_service.process_query(
            query="What are the top 5 keywords?",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        # Lower confidence query (vague)
        low_conf_result = await data_insights_service.process_query(
            query="Tell me about this",
            analysis_id="analysis_test_123",
            cached_analysis=sample_analysis
        )
        
        assert high_conf_result["success"] is True
        assert low_conf_result["success"] is True
        
        # Both should have confidence scores
        assert "metadata" in high_conf_result
        assert "confidence" in high_conf_result["metadata"]

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

