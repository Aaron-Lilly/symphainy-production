#!/usr/bin/env python3
"""
Business Outcomes Orchestrator Tests

Tests for BusinessOutcomesOrchestrator in isolation.
Verifies orchestrator composes services correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.orchestrators]

class TestBusinessOutcomesOrchestrator:
    """Test BusinessOutcomesOrchestrator functionality."""
    
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
        """Create BusinessOutcomesOrchestrator instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        orchestrator = BusinessOutcomesOrchestrator(mock_delivery_manager)
        
        # Mock enabling services
        orchestrator._roadmap_generation_service = Mock()
        orchestrator._roadmap_generation_service.generate_roadmap = AsyncMock(return_value={"success": True})
        orchestrator._poc_generation_service = Mock()
        orchestrator._poc_generation_service.generate_poc_proposal = AsyncMock(return_value={"success": True})
        
        # Mock MCP server
        orchestrator.mcp_server = Mock()
        orchestrator.mcp_server.execute_tool = AsyncMock(return_value={"success": True})
        
        # Mock specialist agent
        orchestrator.specialist_agent = Mock()
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrator_initializes(self, mock_delivery_manager):
        """Test orchestrator initializes correctly."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        orchestrator = BusinessOutcomesOrchestrator(mock_delivery_manager)
        
        assert orchestrator.service_name == "BusinessOutcomesOrchestratorService"
        assert orchestrator.realm_name == "business_enablement"
        assert orchestrator.delivery_manager == mock_delivery_manager
    
    @pytest.mark.asyncio
    async def test_orchestrator_has_mcp_server(self, orchestrator):
        """Test orchestrator has MCP server initialized."""
        assert hasattr(orchestrator, 'mcp_server')
        assert orchestrator.mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_generate_strategic_roadmap_composes_services(self, orchestrator):
        """Test generate_strategic_roadmap composes enabling services."""
        result = await orchestrator.generate_strategic_roadmap(business_context={"objectives": ["obj1"], "timeline": 180}
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_generate_poc_proposal_composes_services(self, orchestrator):
        """Test generate_poc_proposal composes enabling services."""
        result = await orchestrator.generate_poc_proposal(business_context={"content": {}, "insights": {}}
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_create_comprehensive_strategic_plan(self, orchestrator):
        """Test create_comprehensive_strategic_plan orchestrator method."""
        result = await orchestrator.create_comprehensive_strategic_plan(
            business_context={"business_context": {}}
        )
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_track_strategic_progress(self, orchestrator):
        """Test track_strategic_progress orchestrator method."""
        result = await orchestrator.track_strategic_progress(goals=[{"id": "goal_1", "status": "in_progress"}], performance_data={})
        
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_analyze_strategic_trends(self, orchestrator):
        """Test analyze_strategic_trends orchestrator method."""
        result = await orchestrator.analyze_strategic_trends(market_data={})
        
        assert isinstance(result, dict)
        assert "success" in result

