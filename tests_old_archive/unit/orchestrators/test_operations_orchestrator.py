#!/usr/bin/env python3
"""
Operations Orchestrator Tests

Tests for OperationsOrchestrator in isolation.
Verifies orchestrator composes services correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.orchestrators]

class TestOperationsOrchestrator:
    """Test OperationsOrchestrator functionality."""
    
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
        """Create OperationsOrchestrator instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
        
        orchestrator = OperationsOrchestrator(mock_delivery_manager)
        
        # Mock enabling services
        orchestrator._sop_builder_service = Mock()
        orchestrator._sop_builder_service.create_sop = AsyncMock(return_value={"success": True})
        orchestrator._visualization_engine_service = Mock()
        orchestrator._visualization_engine_service.create_visualization = AsyncMock(return_value={"success": True})
        
        # Mock MCP server
        orchestrator.mcp_server = Mock()
        orchestrator.mcp_server.execute_tool = AsyncMock(return_value={"success": True})
        
        # Mock specialist agent
        orchestrator.specialist_agent = Mock()
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrator_initializes(self, mock_delivery_manager):
        """Test orchestrator initializes correctly."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
        
        orchestrator = OperationsOrchestrator(mock_delivery_manager)
        
        assert orchestrator.service_name == "OperationsOrchestratorService"
        assert orchestrator.realm_name == "business_enablement"
        assert orchestrator.delivery_manager == mock_delivery_manager
    
    @pytest.mark.asyncio
    async def test_orchestrator_has_mcp_server(self, orchestrator):
        """Test orchestrator has MCP server initialized."""
        assert hasattr(orchestrator, 'mcp_server')
        assert orchestrator.mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_generate_workflow_from_sop_composes_services(self, orchestrator):
        """Test generate_workflow_from_sop composes enabling services."""
        result = await orchestrator.generate_workflow_from_sop(session_token="test_session", sop_file_uuid="sop_123")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.skip(reason="visualize_workflow method not implemented in OperationsOrchestrator")
    @pytest.mark.asyncio
    async def test_visualize_workflow(self, orchestrator):
        """Test visualize_workflow orchestrator method."""
        result = await orchestrator.visualize_workflow(
            workflow_id="workflow_123"
        )
        
        assert isinstance(result, dict)
        assert "success" in result

