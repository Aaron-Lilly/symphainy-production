#!/usr/bin/env python3
"""
E2E tests for Insights Pillar Architectural Flow

Tests the complete end-to-end flow including API endpoints and frontend integration.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any
import json


@pytest.mark.e2e
@pytest.mark.insights
@pytest.mark.architecture
@pytest.mark.slow
class TestInsightsArchitecturalE2E:
    """E2E tests for complete insights architectural flow."""
    
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
    async def frontend_gateway_service(self, mock_platform_gateway, mock_di_container):
        """Create Frontend Gateway Service instance."""
        from foundations.experience_foundation.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
        
        gateway = FrontendGatewayService(
            service_name="FrontendGatewayService",
            realm_name="experience",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        return gateway
    
    @pytest.mark.asyncio
    async def test_api_endpoint_analyze_eda(self, frontend_gateway_service):
        """Test API endpoint /api/v1/insights-solution/analyze for EDA."""
        # Setup: Mock Insights Solution Orchestrator
        mock_solution_orchestrator = AsyncMock()
        mock_solution_orchestrator.handle_request = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_eda_api",
            "summary": {
                "textual": "EDA analysis complete via API",
                "tabular": {"columns": [], "rows": []},
                "visualizations": []
            },
            "workflow_id": "workflow_api"
        })
        
        # Mock orchestrator discovery
        with patch.object(frontend_gateway_service, '_get_orchestrator_for_pillar', new_callable=AsyncMock) as mock_get_orch:
            mock_get_orch.return_value = mock_solution_orchestrator
            
            # Execute: Simulate API request
            request = {
                "endpoint": "/api/v1/insights-solution/analyze",
                "method": "POST",
                "params": {
                    "file_id": "file_api_123",
                    "analysis_type": "eda",
                    "analysis_options": {
                        "include_visualizations": True
                    }
                },
                "user_context": {
                    "user_id": "test_user",
                    "tenant_id": "test_tenant"
                },
                "headers": {},
                "query_params": {}
            }
            
            result = await frontend_gateway_service.route_frontend_request(request)
            
            # Verify: Request was routed correctly
            assert result.get("success") is not False
            if result.get("success"):
                assert "analysis_id" in result
            
            # Verify: Solution Orchestrator was called
            mock_solution_orchestrator.handle_request.assert_called_once()
            call_args = mock_solution_orchestrator.handle_request.call_args
            assert call_args[1]["path"] == "analyze"
            assert call_args[1]["method"] == "POST"
            assert call_args[1]["params"]["file_id"] == "file_api_123"
    
    @pytest.mark.asyncio
    async def test_api_endpoint_analyze_unstructured(self, frontend_gateway_service):
        """Test API endpoint /api/v1/insights-solution/analyze for unstructured."""
        # Setup: Mock Insights Solution Orchestrator
        mock_solution_orchestrator = AsyncMock()
        mock_solution_orchestrator.handle_request = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_unstructured_api",
            "summary": {
                "textual": "Unstructured analysis complete via API"
            },
            "aar_analysis": {
                "lessons_learned": [],
                "risks": [],
                "recommendations": []
            }
        })
        
        with patch.object(frontend_gateway_service, '_get_orchestrator_for_pillar', new_callable=AsyncMock) as mock_get_orch:
            mock_get_orch.return_value = mock_solution_orchestrator
            
            # Execute
            request = {
                "endpoint": "/api/v1/insights-solution/analyze",
                "method": "POST",
                "params": {
                    "file_id": "file_unstructured_api",
                    "analysis_type": "unstructured",
                    "analysis_options": {
                        "aar_specific_analysis": True
                    }
                },
                "user_context": {"user_id": "test_user"},
                "headers": {},
                "query_params": {}
            }
            
            result = await frontend_gateway_service.route_frontend_request(request)
            
            # Verify
            assert result.get("success") is not False
            if result.get("success"):
                assert "analysis_id" in result
                assert "aar_analysis" in result
    
    @pytest.mark.asyncio
    async def test_api_endpoint_mapping(self, frontend_gateway_service):
        """Test API endpoint /api/v1/insights-solution/mapping."""
        # Setup: Mock Insights Solution Orchestrator
        mock_solution_orchestrator = AsyncMock()
        mock_solution_orchestrator.handle_request = AsyncMock(return_value={
            "success": True,
            "mapping_id": "mapping_api_123",
            "mapping_type": "unstructured_to_structured",
            "output_file_id": "output_file_api"
        })
        
        with patch.object(frontend_gateway_service, '_get_orchestrator_for_pillar', new_callable=AsyncMock) as mock_get_orch:
            mock_get_orch.return_value = mock_solution_orchestrator
            
            # Execute
            request = {
                "endpoint": "/api/v1/insights-solution/mapping",
                "method": "POST",
                "params": {
                    "source_file_id": "source_api",
                    "target_file_id": "target_api",
                    "mapping_options": {}
                },
                "user_context": {"user_id": "test_user"},
                "headers": {},
                "query_params": {}
            }
            
            result = await frontend_gateway_service.route_frontend_request(request)
            
            # Verify
            assert result.get("success") is not False
            if result.get("success"):
                assert "mapping_id" in result
                assert "output_file_id" in result
    
    @pytest.mark.asyncio
    async def test_legacy_endpoints_rejected(self, frontend_gateway_service):
        """Test that old /api/v1/insights-pillar endpoints are properly rejected."""
        # Execute: Try to use old endpoint
        request = {
            "endpoint": "/api/v1/insights-pillar/analyze-content-for-insights",
            "method": "POST",
            "params": {
                "file_id": "file_old",
                "content_type": "structured"
            },
            "user_context": {"user_id": "test_user"},
            "headers": {},
            "query_params": {}
        }
        
        result = await frontend_gateway_service.route_frontend_request(request)
        
        # Verify: Request was rejected (orchestrator not found)
        assert result.get("success") is False or "not available" in str(result.get("error", "")).lower() or "not found" in str(result.get("error", "")).lower()
    
    @pytest.mark.asyncio
    async def test_workflow_id_propagation(self, frontend_gateway_service):
        """Test that workflow_id is properly propagated through the flow."""
        # Setup: Mock Insights Solution Orchestrator
        mock_solution_orchestrator = AsyncMock()
        mock_solution_orchestrator.handle_request = AsyncMock(return_value={
            "success": True,
            "analysis_id": "analysis_workflow",
            "workflow_id": "workflow_propagated"
        })
        
        with patch.object(frontend_gateway_service, '_get_orchestrator_for_pillar', new_callable=AsyncMock) as mock_get_orch:
            mock_get_orch.return_value = mock_solution_orchestrator
            
            # Execute: Request with workflow_id in header
            request = {
                "endpoint": "/api/v1/insights-solution/analyze",
                "method": "POST",
                "params": {
                    "file_id": "file_workflow",
                    "analysis_type": "eda"
                },
                "user_context": {"user_id": "test_user"},
                "headers": {
                    "X-Workflow-Id": "workflow_from_header"
                },
                "query_params": {}
            }
            
            result = await frontend_gateway_service.route_frontend_request(request)
            
            # Verify: workflow_id was extracted and passed
            call_args = mock_solution_orchestrator.handle_request.call_args
            user_context = call_args[1]["user_context"]
            assert "workflow_id" in user_context

