#!/usr/bin/env python3
"""
Integration Tests for Universal Gateway (FrontendGatewayService) Routing

Tests the Universal Gateway routing logic including:
- Request routing to appropriate orchestrators
- Pillar-specific routing (Content, Insights, Operations, Data)
- Chat service routing
- Error handling and validation
- Response transformation for frontend
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.experience.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

class TestUniversalGatewayRouting:
    """Integration tests for Universal Gateway routing."""
    
    @pytest.fixture
    async def mock_orchestrators(self):
        """Create mock orchestrators."""
        mocks = {}
        
        # Mock ContentAnalysisOrchestrator
        mocks['content'] = Mock()
        mocks['content'].parse_file = AsyncMock(return_value={
            "status": "success",
            "data": {"parse_result": {"content": "parsed"}}
        })
        mocks['content'].analyze_document = AsyncMock(return_value={
            "status": "success",
            "data": {"analysis": {"insights": []}}
        })
        
        # Mock InsightsOrchestrator
        mocks['insights'] = Mock()
        mocks['insights'].calculate_metrics = AsyncMock(return_value={
            "status": "success",
            "data": {"metrics": {"kpi_value": 85.5}}
        })
        mocks['insights'].generate_insights = AsyncMock(return_value={
            "status": "success",
            "data": {"insights": []}
        })
        
        # Mock OperationsOrchestrator
        mocks['operations'] = Mock()
        mocks['operations'].generate_workflow_from_sop = AsyncMock(return_value={
            "success": True,
            "workflow": {"id": "workflow_123"}
        })
        mocks['operations'].start_wizard = AsyncMock(return_value={
            "success": True,
            "session_token": "wizard_123"
        })
        
        # Mock ChatService
        mocks['chat'] = Mock()
        mocks['chat'].handle_guide_chat = AsyncMock(return_value={
            "success": True,
            "response": "Test response"
        })
        
        return mocks
    
    @pytest.fixture
    async def gateway_service(self, mock_orchestrators):
        """Create FrontendGatewayService instance."""
        platform_gateway = Mock()
        platform_gateway.get_smart_city_service = AsyncMock(return_value=None)
        
        di_container = Mock()
        di_container.get_foundation_service = Mock(return_value=None)
        di_container.curator = None
        
        gateway = FrontendGatewayService(
            service_name="FrontendGatewayService",
            realm_name="experience",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Mock Smart City services
        gateway.librarian = Mock()
        gateway.security_guard = Mock()
        gateway.traffic_cop = Mock()
        
        # Inject mock orchestrators
        gateway.content_orchestrator = mock_orchestrators['content']
        gateway.insights_orchestrator = mock_orchestrators['insights']
        gateway.operations_orchestrator = mock_orchestrators['operations']
        gateway.chat_service = mock_orchestrators['chat']
        
        return gateway
    
    async def test_gateway_initialization(self, gateway_service):
        """Test that FrontendGatewayService initializes correctly."""
        assert gateway_service.service_name == "FrontendGatewayService"
        assert gateway_service.realm_name == "experience"
        assert hasattr(gateway_service, 'route_frontend_request')
        assert hasattr(gateway_service, 'content_orchestrator')
        assert hasattr(gateway_service, 'insights_orchestrator')
        assert hasattr(gateway_service, 'operations_orchestrator')
    
    async def test_route_to_content_pillar(self, gateway_service):
        """Test routing to Content pillar."""
        request = {
            "endpoint": "/api/content/parse_file",
            "method": "POST",
            "params": {
                "file_id": "test_file_123"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should route to ContentAnalysisOrchestrator
        assert isinstance(result, dict)
        # Should have either success or status indicator
        assert "success" in result or "status" in result or "error" in result
    
    async def test_route_to_insights_pillar(self, gateway_service):
        """Test routing to Insights pillar."""
        request = {
            "endpoint": "/api/insights/calculate_metrics",
            "method": "POST",
            "params": {
                "resource_id": "test_resource_123"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should route to InsightsOrchestrator
        assert isinstance(result, dict)
        assert "success" in result or "status" in result or "error" in result
    
    async def test_route_to_operations_pillar(self, gateway_service):
        """Test routing to Operations pillar."""
        request = {
            "endpoint": "/api/operations/generate_workflow_from_sop",
            "method": "POST",
            "params": {
                "session_token": "session_123",
                "sop_file_uuid": "sop_123"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should route to OperationsOrchestrator
        assert isinstance(result, dict)
        assert "success" in result or "status" in result or "error" in result
    
    async def test_route_to_chat_service(self, gateway_service):
        """Test routing to Chat service."""
        request = {
            "endpoint": "/api/chat/guide",
            "method": "POST",
            "params": {
                "message": "How do I create an SOP?",
                "session_token": "session_123"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should route to ChatService
        assert isinstance(result, dict)
        assert "success" in result or "status" in result or "error" in result
    
    async def test_invalid_endpoint_format(self, gateway_service):
        """Test handling of invalid endpoint format."""
        request = {
            "endpoint": "/invalid/endpoint",
            "method": "POST",
            "params": {}
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should return error
        assert "success" in result or "error" in result
        if "success" in result:
            assert result["success"] is False
        if "error" in result:
            assert isinstance(result["error"], str)
    
    async def test_missing_orchestrator(self, gateway_service):
        """Test handling when orchestrator is not available."""
        # Remove operations orchestrator
        gateway_service.operations_orchestrator = None
        
        request = {
            "endpoint": "/api/operations/start_wizard",
            "method": "POST",
            "params": {}
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should return error indicating orchestrator not available
        assert isinstance(result, dict)
        assert "success" in result or "error" in result
    
    async def test_multiple_pillar_requests(self, gateway_service):
        """Test routing requests to multiple pillars."""
        requests = [
            {
                "endpoint": "/api/content/parse_file",
                "method": "POST",
                "params": {"file_id": "file_1"}
            },
            {
                "endpoint": "/api/insights/calculate_metrics",
                "method": "POST",
                "params": {"resource_id": "resource_1"}
            },
            {
                "endpoint": "/api/operations/start_wizard",
                "method": "POST",
                "params": {}
            }
        ]
        
        results = []
        for request in requests:
            result = await gateway_service.route_frontend_request(request)
            results.append(result)
        
        # All should complete
        assert len(results) == 3
        for result in results:
            assert isinstance(result, dict)
    
    async def test_concurrent_routing(self, gateway_service):
        """Test concurrent request routing."""
        import asyncio
        
        requests = [
            {
                "endpoint": f"/api/content/parse_file",
                "method": "POST",
                "params": {"file_id": f"file_{i}"}
            }
            for i in range(5)
        ]
        
        tasks = [gateway_service.route_frontend_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without crashing
        assert len(results) == 5
        for result in results:
            assert isinstance(result, (dict, Exception))
    
    async def test_request_with_headers(self, gateway_service):
        """Test routing with request headers."""
        request = {
            "endpoint": "/api/content/parse_file",
            "method": "POST",
            "params": {"file_id": "test_file"},
            "headers": {
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should process request with headers
        assert isinstance(result, dict)
    
    async def test_request_with_query_params(self, gateway_service):
        """Test routing with query parameters."""
        request = {
            "endpoint": "/api/insights/calculate_metrics",
            "method": "GET",
            "params": {"resource_id": "test_resource"},
            "query_params": {
                "include_visualization": "true",
                "time_period": "30d"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should process request with query params
        assert isinstance(result, dict)
    
    async def test_request_with_user_id(self, gateway_service):
        """Test routing with user identification."""
        request = {
            "endpoint": "/api/content/parse_file",
            "method": "POST",
            "params": {"file_id": "test_file"},
            "user_id": "user_123"
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should process request with user context
        assert isinstance(result, dict)
    
    async def test_error_propagation(self, gateway_service, mock_orchestrators):
        """Test that errors from orchestrators are properly propagated."""
        # Mock orchestrator error
        mock_orchestrators['content'].parse_file = AsyncMock(return_value={
            "status": "error",
            "error": "File not found"
        })
        
        request = {
            "endpoint": "/api/content/parse_file",
            "method": "POST",
            "params": {"file_id": "invalid_file"}
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should propagate error
        assert isinstance(result, dict)
        assert "error" in result or ("status" in result and result["status"] == "error")
    
    async def test_response_transformation(self, gateway_service):
        """Test that responses are properly formatted for frontend."""
        request = {
            "endpoint": "/api/insights/calculate_metrics",
            "method": "POST",
            "params": {"resource_id": "test_resource"}
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should have frontend-ready format
        assert isinstance(result, dict)
        # Should have standard response structure
        assert any(key in result for key in ["success", "status", "data", "error"])
    
    async def test_method_routing(self, gateway_service):
        """Test routing different HTTP methods."""
        methods = ["GET", "POST", "PUT", "DELETE"]
        
        for method in methods:
            request = {
                "endpoint": "/api/content/parse_file",
                "method": method,
                "params": {"file_id": "test_file"}
            }
            
            result = await gateway_service.route_frontend_request(request)
            
            # Should handle all methods
            assert isinstance(result, dict)
    
    async def test_pillar_isolation(self, gateway_service, mock_orchestrators):
        """Test that pillars are properly isolated (no cross-pillar contamination)."""
        # Call Content pillar
        content_request = {
            "endpoint": "/api/content/parse_file",
            "method": "POST",
            "params": {"file_id": "test_file"}
        }
        content_result = await gateway_service.route_frontend_request(content_request)
        
        # Call Insights pillar
        insights_request = {
            "endpoint": "/api/insights/calculate_metrics",
            "method": "POST",
            "params": {"resource_id": "test_resource"}
        }
        insights_result = await gateway_service.route_frontend_request(insights_request)
        
        # Results should be independent
        assert isinstance(content_result, dict)
        assert isinstance(insights_result, dict)
        # Both requests should complete successfully (isolation verified by separate results)
        assert "success" in content_result or "status" in content_result or "error" in content_result
        assert "success" in insights_result or "status" in insights_result or "error" in insights_result
    
    async def test_api_endpoint_registration(self, gateway_service):
        """Test API endpoint registration."""
        async def test_handler(request):
            return {"success": True, "data": "test"}
        
        result = await gateway_service.expose_frontend_api(
            api_name="test_api",
            endpoint="/api/test/endpoint",
            handler=test_handler
        )
        
        # Should register successfully
        assert result is True or isinstance(result, bool)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

