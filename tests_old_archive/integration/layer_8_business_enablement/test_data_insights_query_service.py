#!/usr/bin/env python3
"""
Functional tests for DataInsightsQueryService.

Tests natural language query processing capabilities.
"""

import pytest
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestDataInsightsQueryServiceFunctional:
    """Functional tests for DataInsightsQueryService."""
    
    @pytest.fixture(scope="function")
    async def data_insights_query_service(self, smart_city_infrastructure):
        """Create DataInsightsQueryService instance."""
        from backend.business_enablement.enabling_services.data_insights_query_service import DataInsightsQueryService
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        di_container = smart_city_infrastructure["di_container"]
        
        service = DataInsightsQueryService(
            service_name="DataInsightsQueryService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        initialized = await service.initialize()
        assert initialized, "DataInsightsQueryService should initialize successfully"
        
        return service
    
    @pytest.fixture(scope="function")
    def mock_user_context(self) -> Dict[str, Any]:
        """Create a mock user context."""
        return {
            "user_id": "test_user_123",
            "tenant_id": "test_tenant_123",
            "email": "test@example.com",
            "permissions": ["read", "write"]
        }
    
    @pytest.fixture(scope="function")
    def sample_cached_analysis(self) -> Dict[str, Any]:
        """Create a sample cached analysis response."""
        return {
            "analysis_id": "analysis_123",
            "summary": {
                "textual": "This analysis shows revenue trends over the past quarter. Revenue increased by 15% compared to the previous quarter."
            },
            "metrics": {
                "revenue": 1000000,
                "growth": 0.15,
                "period": "Q1 2024"
            },
            "insights": [
                {
                    "type": "trend",
                    "description": "Revenue is trending upward",
                    "confidence": 0.9
                }
            ],
            "data": [
                {"month": "January", "revenue": 800000},
                {"month": "February", "revenue": 900000},
                {"month": "March", "revenue": 1000000}
            ]
        }
    
    async def test_service_initialization(self, data_insights_query_service):
        """Test that DataInsightsQueryService initializes correctly."""
        assert data_insights_query_service is not None
        assert data_insights_query_service.is_initialized is True
        assert data_insights_query_service.librarian is not None
        assert data_insights_query_service.data_steward is not None
        
        logger.info("✅ DataInsightsQueryService initialized correctly")
    
    async def test_process_query_summarize(
        self,
        data_insights_query_service,
        sample_cached_analysis,
        mock_user_context
    ):
        """Test processing a summarize query."""
        result = await data_insights_query_service.process_query(
            query="Summarize the analysis",
            analysis_id=sample_cached_analysis["analysis_id"],
            cached_analysis=sample_cached_analysis,
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "query_id" in result
        assert "result" in result
        assert result.get("result", {}).get("type") in ["text", "table", "chart"]
        
        logger.info(f"✅ Query processed successfully: {result.get('query_id')}")
    
    async def test_process_query_top_n(
        self,
        data_insights_query_service,
        sample_cached_analysis,
        mock_user_context
    ):
        """Test processing a top N query."""
        result = await data_insights_query_service.process_query(
            query="Show me the top 3 months by revenue",
            analysis_id=sample_cached_analysis["analysis_id"],
            cached_analysis=sample_cached_analysis,
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "query_id" in result
        assert "result" in result
        assert "follow_up_suggestions" in result
        
        logger.info(f"✅ Top N query processed successfully: {result.get('query_id')}")
    
    async def test_process_query_chart(
        self,
        data_insights_query_service,
        sample_cached_analysis,
        mock_user_context
    ):
        """Test processing a chart query."""
        result = await data_insights_query_service.process_query(
            query="Show me a chart of revenue over time",
            analysis_id=sample_cached_analysis["analysis_id"],
            cached_analysis=sample_cached_analysis,
            query_type="chart",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "query_id" in result
        assert "result" in result
        
        logger.info(f"✅ Chart query processed successfully: {result.get('query_id')}")
    
    async def test_get_supported_patterns(
        self,
        data_insights_query_service,
        mock_user_context
    ):
        """Test getting supported query patterns."""
        result = await data_insights_query_service.get_supported_patterns(
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        # PatternMatcher.get_supported_patterns() should return pattern categories
        assert len(result) > 1  # Should have more than just "success"
        
        logger.info("✅ Supported patterns retrieved successfully")
    
    async def test_process_query_security_validation(
        self,
        data_insights_query_service,
        sample_cached_analysis
    ):
        """Test that query processing requires proper permissions."""
        # User context without permissions
        unauthorized_context = {
            "user_id": "unauthorized_user",
            "tenant_id": "test_tenant_123",
            "permissions": []  # No permissions
        }
        
        # This should raise PermissionError
        with pytest.raises(PermissionError):
            await data_insights_query_service.process_query(
                query="Summarize the analysis",
                analysis_id=sample_cached_analysis["analysis_id"],
                cached_analysis=sample_cached_analysis,
                user_context=unauthorized_context
            )
        
        logger.info("✅ Security validation tested")
    
    async def test_architecture_verification(self, data_insights_query_service, smart_city_infrastructure):
        """Verify the service follows the 5-layer architecture pattern."""
        # Verify it uses Platform Gateway for abstractions (if needed)
        assert data_insights_query_service.platform_gateway is not None
        
        # Verify it uses Smart City services via RealmServiceBase
        assert data_insights_query_service.librarian is not None
        assert data_insights_query_service.data_steward is not None
        
        logger.info("✅ Architecture verification passed (5-layer pattern)")




