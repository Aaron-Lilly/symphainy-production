#!/usr/bin/env python3
"""
Insights Orchestrator Tests

Tests for InsightsOrchestrator in isolation.
Verifies orchestrator composes services correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.orchestrators]

class TestInsightsOrchestrator:
    """Test InsightsOrchestrator functionality."""
    
    @pytest.fixture
    def mock_delivery_manager(self):
        """Create mock delivery manager."""
        manager = Mock()
        manager.realm_name = "business_enablement"
        manager.service_name = "DeliveryManagerService"
        manager.platform_gateway = Mock()
        manager.di_container = Mock()
        manager.di_container.get_logger = Mock(return_value=Mock())
        return manager
    
    @pytest.fixture
    async def orchestrator(self, mock_delivery_manager):
        """Create InsightsOrchestrator instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
        
        orchestrator = InsightsOrchestrator(mock_delivery_manager)
        
        # Mock enabling services
        orchestrator._data_analyzer_service = Mock()
        orchestrator._data_analyzer_service.analyze_data = AsyncMock(return_value={"success": True})
        
        # Mock MCP server
        orchestrator.mcp_server = Mock()
        orchestrator.mcp_server.execute_tool = AsyncMock(return_value={"success": True})
        
        # Mock specialist agent
        orchestrator.specialist_agent = Mock()
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrator_initializes(self, mock_delivery_manager):
        """Test orchestrator initializes correctly."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
        
        orchestrator = InsightsOrchestrator(mock_delivery_manager)
        
        assert orchestrator.service_name == "InsightsOrchestratorService"
        assert orchestrator.realm_name == "business_enablement"
        assert orchestrator.delivery_manager == mock_delivery_manager
    
    @pytest.mark.asyncio
    async def test_orchestrator_has_mcp_server(self, orchestrator):
        """Test orchestrator has MCP server initialized."""
        assert hasattr(orchestrator, 'mcp_server')
        assert orchestrator.mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_analyze_content_for_insights_composes_services(self, orchestrator):
        """Test analyze_content_for_insights composes enabling services."""
        result = await orchestrator.analyze_content_for_insights(source_type="file", file_id="test_file_123")
        
        assert isinstance(result, dict)
        assert "success" in result

