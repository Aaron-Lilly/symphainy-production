#!/usr/bin/env python3
"""
Integration tests for Data Mash and Query Insights functionality (Phase 4)

Tests the complete flow for:
- Data mash orchestration (DataSolutionOrchestrator)
- Query insights across data types (InsightsSolutionOrchestrator)
- End-to-end data mash queries
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any
import uuid


@pytest.mark.integration
@pytest.mark.insights
@pytest.mark.data_mash
@pytest.mark.slow
class TestDataMashQueryIntegration:
    """Integration tests for data mash and query insights functionality."""
    
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
    async def data_solution_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create Data Solution Orchestrator instance."""
        from backend.solution.services.data_solution_orchestrator_service.data_solution_orchestrator_service import DataSolutionOrchestratorService
        
        orchestrator = DataSolutionOrchestratorService(
            service_name="DataSolutionOrchestratorService",
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
        
        # Mock platform correlation methods
        orchestrator._orchestrate_platform_correlation = AsyncMock(
            return_value={"workflow_id": "workflow_mash_123", "user_id": "test_user"}
        )
        orchestrator._record_platform_correlation_completion = AsyncMock()
        
        return orchestrator
    
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
        
        # Mock platform correlation methods
        orchestrator._orchestrate_platform_correlation = AsyncMock(
            return_value={"workflow_id": "workflow_query_456", "user_id": "test_user"}
        )
        orchestrator._record_platform_correlation_completion = AsyncMock()
        
        return orchestrator
    
    @pytest.fixture
    async def insights_journey_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create Insights Journey Orchestrator instance."""
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        
        orchestrator = InsightsJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock realm service
        orchestrator._realm_service = Mock()
        orchestrator._realm_service.handle_error_with_audit = AsyncMock()
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrate_data_mash_basic(self, data_solution_orchestrator):
        """Test basic data mash orchestration."""
        # Setup: Mock journey orchestrators
        mock_content_journey = AsyncMock()
        mock_content_journey.handle_content_upload = AsyncMock(return_value={
            "success": True,
            "file_id": "file_123"
        })
        
        data_solution_orchestrator.content_journey_orchestrator = mock_content_journey
        
        # Mock Insights Solution Orchestrator discovery
        mock_insights_orchestrator = AsyncMock()
        mock_insights_orchestrator.query_insights = AsyncMock(return_value={
            "success": True,
            "insights": {
                "mappings": [],
                "analyses": []
            }
        })
        data_solution_orchestrator._discover_insights_solution_orchestrator = AsyncMock(
            return_value=mock_insights_orchestrator
        )
        
        # Execute
        result = await data_solution_orchestrator.orchestrate_data_mash(
            client_data_query={"file_ids": ["file_123"]},
            semantic_data_query=None,
            platform_data_query=None,
            insights_query={"mapping_needed": True},
            user_context={"user_id": "test_user"}
        )
        
        # Verify
        assert result["success"] is True
        assert "correlation" in result
        assert "workflow_id" in result["correlation"]
        assert "client_data" in result or "insights" in result
        
        # Verify platform correlation was called
        data_solution_orchestrator._orchestrate_platform_correlation.assert_called_once()
        data_solution_orchestrator._record_platform_correlation_completion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_insights_basic(self, insights_solution_orchestrator, insights_journey_orchestrator):
        """Test basic query insights functionality."""
        # Setup: Mock Journey Orchestrator discovery
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=insights_journey_orchestrator
        )
        
        # Mock query_insights_with_data_mash
        insights_journey_orchestrator.query_insights_with_data_mash = AsyncMock(return_value={
            "success": True,
            "insights": {
                "mappings": [{
                    "file_id": "file_123",
                    "status": "mapping_needed"
                }],
                "analyses": []
            },
            "workflow_ids": ["workflow_123"],
            "file_ids": ["file_123"],
            "content_ids": []
        })
        
        # Execute
        result = await insights_solution_orchestrator.query_insights(
            insights_query={
                "mapping_needed": True,
                "file_ids": ["file_123"]
            },
            user_context={"user_id": "test_user"}
        )
        
        # Verify
        assert result["success"] is True
        assert "insights" in result
        assert "mappings" in result["insights"]
        assert len(result["insights"]["mappings"]) > 0
        
        # Verify platform correlation was called
        insights_solution_orchestrator._orchestrate_platform_correlation.assert_called_once()
        insights_solution_orchestrator._record_platform_correlation_completion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_insights_with_client_data(self, insights_journey_orchestrator):
        """Test query insights with client data composition."""
        # Setup: Mock Content Steward
        mock_content_steward = AsyncMock()
        mock_content_steward.get_file = AsyncMock(return_value={
            "file_id": "file_123",
            "filename": "test_file.csv",
            "file_type": "csv",
            "size_bytes": 1024,
            "metadata": {
                "ui_name": "test_file.csv",
                "file_type": "csv",
                "mime_type": "text/csv",
                "parsed": True,
                "parsed_file_id": "parsed_123",
                "parse_result": {
                    "status": "success",
                    "record_count": 100,
                    "schema": {
                        "fields": ["col1", "col2"]
                    }
                }
            }
        })
        
        insights_journey_orchestrator.get_content_steward_api = AsyncMock(
            return_value=mock_content_steward
        )
        
        # Execute
        result = await insights_journey_orchestrator.query_insights_with_data_mash(
            insights_query={
                "file_ids": ["file_123"],
                "mapping_needed": True
            },
            user_context={"user_id": "test_user"}
        )
        
        # Verify
        assert result["success"] is True
        assert "client_data" in result
        assert len(result["client_data"]) == 1
        assert result["client_data"][0]["file_id"] == "file_123"
        assert result["client_data"][0]["parsed"] is True
        assert "parse_summary" in result["client_data"][0]
        
        # Verify insights include mapping needed status
        assert "insights" in result
        assert "mappings" in result["insights"]
        assert len(result["insights"]["mappings"]) > 0
        assert result["insights"]["mappings"][0]["file_id"] == "file_123"
        assert result["insights"]["mappings"][0]["status"] == "mapping_needed"
    
    @pytest.mark.asyncio
    async def test_query_insights_with_quality_issues(self, insights_journey_orchestrator):
        """Test query insights detecting quality issues."""
        # Setup: Mock Content Steward with quality issues
        mock_content_steward = AsyncMock()
        mock_content_steward.get_file = AsyncMock(return_value={
            "file_id": "file_456",
            "filename": "test_file_with_issues.csv",
            "metadata": {
                "ui_name": "test_file_with_issues.csv",
                "parsed": True,
                "parse_result": {
                    "status": "success",
                    "quality_issues": [
                        {
                            "type": "missing_values",
                            "field": "col1",
                            "count": 5
                        }
                    ]
                }
            }
        })
        
        insights_journey_orchestrator.get_content_steward_api = AsyncMock(
            return_value=mock_content_steward
        )
        
        # Execute
        result = await insights_journey_orchestrator.query_insights_with_data_mash(
            insights_query={
                "file_ids": ["file_456"],
                "quality_issues": True
            },
            user_context={"user_id": "test_user"}
        )
        
        # Verify
        assert result["success"] is True
        assert "insights" in result
        assert "analyses" in result["insights"]
        assert len(result["insights"]["analyses"]) > 0
        assert result["insights"]["analyses"][0]["file_id"] == "file_456"
        assert "quality_issues" in result["insights"]["analyses"][0]
    
    @pytest.mark.asyncio
    async def test_data_mash_api_endpoint(self, data_solution_orchestrator):
        """Test data mash API endpoint via handle_request."""
        # Setup: Mock journey orchestrators
        mock_content_journey = AsyncMock()
        data_solution_orchestrator.content_journey_orchestrator = mock_content_journey
        
        # Mock Insights Solution Orchestrator
        mock_insights_orchestrator = AsyncMock()
        mock_insights_orchestrator.query_insights = AsyncMock(return_value={
            "success": True,
            "insights": {"mappings": []}
        })
        data_solution_orchestrator._discover_insights_solution_orchestrator = AsyncMock(
            return_value=mock_insights_orchestrator
        )
        
        # Execute via handle_request
        result = await data_solution_orchestrator.handle_request(
            method="POST",
            path="mash",
            params={
                "client_data_query": {"file_ids": ["file_123"]},
                "insights_query": {"mapping_needed": True}
            },
            user_context={"user_id": "test_user"}
        )
        
        # Verify
        assert result["success"] is True
        assert "correlation" in result
        assert "workflow_id" in result["correlation"]
    
    @pytest.mark.asyncio
    async def test_query_insights_api_endpoint(self, insights_solution_orchestrator, insights_journey_orchestrator):
        """Test query insights API endpoint via handle_request."""
        # Setup: Mock Journey Orchestrator discovery
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=insights_journey_orchestrator
        )
        
        # Mock query_insights_with_data_mash
        insights_journey_orchestrator.query_insights_with_data_mash = AsyncMock(return_value={
            "success": True,
            "insights": {"mappings": []}
        })
        
        # Execute via handle_request
        result = await insights_solution_orchestrator.handle_request(
            method="POST",
            path="query",
            params={
                "insights_query": {
                    "mapping_needed": True,
                    "file_ids": ["file_123"]
                }
            },
            user_context={"user_id": "test_user"}
        )
        
        # Verify
        assert result["success"] is True
        assert "insights" in result
    
    @pytest.mark.asyncio
    async def test_data_mash_correlation_ids(self, data_solution_orchestrator):
        """Test that data mash correctly extracts correlation IDs."""
        # Setup: Mock journey orchestrators with correlation IDs
        mock_content_journey = AsyncMock()
        data_solution_orchestrator.content_journey_orchestrator = mock_content_journey
        
        # Mock Insights Solution Orchestrator with correlation IDs
        mock_insights_orchestrator = AsyncMock()
        mock_insights_orchestrator.query_insights = AsyncMock(return_value={
            "success": True,
            "workflow_id": "workflow_insights_789",
            "file_ids": ["file_123", "file_456"],
            "content_ids": ["content_789"],
            "insights": {"mappings": []}
        })
        data_solution_orchestrator._discover_insights_solution_orchestrator = AsyncMock(
            return_value=mock_insights_orchestrator
        )
        
        # Execute
        result = await data_solution_orchestrator.orchestrate_data_mash(
            client_data_query={"file_ids": ["file_123"]},
            insights_query={"mapping_needed": True},
            user_context={"user_id": "test_user", "workflow_id": "workflow_main_123"}
        )
        
        # Verify correlation IDs are extracted
        assert result["success"] is True
        assert "correlation" in result
        correlation = result["correlation"]
        assert "workflow_ids" in correlation
        assert "file_ids" in correlation
        assert "content_ids" in correlation
        
        # Verify workflow_ids include insights workflow (main workflow is in correlation_context, not extracted from user_context)
        assert "workflow_insights_789" in correlation["workflow_ids"]
        # Note: workflow_main_123 is in correlation_context but may not be extracted if it's the same as the mash workflow_id
        
        # Verify file_ids are extracted
        assert "file_123" in correlation["file_ids"]
        assert "file_456" in correlation["file_ids"]
    
    @pytest.mark.asyncio
    async def test_query_insights_error_handling(self, insights_journey_orchestrator):
        """Test error handling in query insights."""
        # Setup: Mock Content Steward to raise error
        insights_journey_orchestrator.get_content_steward_api = AsyncMock(
            side_effect=Exception("Content Steward unavailable")
        )
        
        # Execute
        result = await insights_journey_orchestrator.query_insights_with_data_mash(
            insights_query={"file_ids": ["file_123"]},
            user_context={"user_id": "test_user"}
        )
        
        # Verify error is handled gracefully
        assert result["success"] is False
        assert "error" in result
        
        # Verify error audit was called
        insights_journey_orchestrator._realm_service.handle_error_with_audit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_data_mash_empty_queries(self, data_solution_orchestrator):
        """Test data mash with empty queries."""
        # Setup: Mock journey orchestrators
        mock_content_journey = AsyncMock()
        data_solution_orchestrator.content_journey_orchestrator = mock_content_journey
        
        mock_insights_orchestrator = AsyncMock()
        mock_insights_orchestrator.query_insights = AsyncMock(return_value={
            "success": True,
            "insights": {}
        })
        data_solution_orchestrator._discover_insights_solution_orchestrator = AsyncMock(
            return_value=mock_insights_orchestrator
        )
        
        # Execute with all None queries
        result = await data_solution_orchestrator.orchestrate_data_mash(
            client_data_query=None,
            semantic_data_query=None,
            platform_data_query=None,
            insights_query=None,
            user_context={"user_id": "test_user"}
        )
        
        # Verify it still succeeds (empty queries are valid)
        assert result["success"] is True
        assert "correlation" in result
        assert "workflow_id" in result["correlation"]

