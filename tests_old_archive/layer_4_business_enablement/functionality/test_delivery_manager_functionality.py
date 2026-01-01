#!/usr/bin/env python3
"""
Delivery Manager Functionality Tests

Tests Delivery Manager core functionality:
- Pillar orchestration
- Cross-pillar coordination
- SOA API exposure
- MCP Tool exposure

Uses mock AI responses.
"""

# Path is configured in pytest.ini - no manipulation needed

import pytest

from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any

    # Fallback: calculate from this file's location
@pytest.mark.business_enablement
@pytest.mark.functional
class TestDeliveryManagerFunctionality:
    """Test Delivery Manager functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    def mock_content_analysis_orchestrator(self):
        """Create mock Content Analysis Orchestrator."""
        orchestrator = Mock()
        orchestrator.analyze_content = AsyncMock(return_value={"status": "success"})
        return orchestrator
    
    @pytest.fixture
    def mock_insights_orchestrator(self):
        """Create mock Insights Orchestrator."""
        orchestrator = Mock()
        orchestrator.generate_insights = AsyncMock(return_value={"status": "success"})
        return orchestrator
    
    @pytest.fixture
    async def delivery_manager_service(self, mock_di_container, mock_platform_gateway, mock_content_analysis_orchestrator, mock_insights_orchestrator):
        """Create Delivery Manager Service instance."""
        from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
        
        service = DeliveryManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Mock pillar orchestrators
        service.mvp_pillar_orchestrators = {
            "content_analysis": mock_content_analysis_orchestrator,
            "insights": mock_insights_orchestrator,
            "operations": Mock(),
            "business_outcomes": Mock()
        }
        
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_orchestrate_pillars(self, delivery_manager_service, mock_content_analysis_orchestrator):
        """Test pillar orchestration."""
        request = {
            "pillar": "content_analysis",
            "action": "analyze",
            "data": {"content": "test content"}
        }
        
        result = await delivery_manager_service.orchestrate_pillars(request)
        
        assert result is not None
        assert isinstance(result, dict)
        # Should indicate successful orchestration
        assert "status" in result or "result" in result
    
    @pytest.mark.asyncio
    async def test_orchestrate_pillars(self, delivery_manager_service):
        """Test pillar orchestration (Delivery Manager uses orchestrate_pillars, not coordinate_cross_pillar)."""
        business_context = {
            "pillar": "content_analysis",
            "action": "analyze",
            "data": {"content": "test content"}
        }
        
        # Mock the business_enablement_orchestration_module
        delivery_manager_service.business_enablement_orchestration_module = Mock()
        delivery_manager_service.business_enablement_orchestration_module.orchestrate_business_enablement = AsyncMock(
            return_value={"status": "success", "result": {}}
        )
        
        result = await delivery_manager_service.orchestrate_pillars(business_context)
        
        assert result is not None
        assert isinstance(result, dict)
        assert "status" in result or "result" in result
    
    @pytest.mark.asyncio
    async def test_has_soa_apis(self, delivery_manager_service):
        """Test that Delivery Manager exposes SOA APIs."""
        assert hasattr(delivery_manager_service, 'soa_apis')
        # Should have SOA APIs registered
        assert isinstance(delivery_manager_service.soa_apis, dict)
    
    @pytest.mark.asyncio
    async def test_has_mcp_tools(self, delivery_manager_service):
        """Test that Delivery Manager exposes MCP Tools."""
        assert hasattr(delivery_manager_service, 'mcp_tools')
        # Should have MCP Tools registered
        assert isinstance(delivery_manager_service.mcp_tools, dict)

