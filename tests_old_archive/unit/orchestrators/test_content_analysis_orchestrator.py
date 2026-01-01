#!/usr/bin/env python3
"""
Content Analysis Orchestrator Tests

Tests for ContentAnalysisOrchestrator in isolation.
Verifies orchestrator composes services correctly.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.orchestrators]

class TestContentAnalysisOrchestrator:
    """Test ContentAnalysisOrchestrator functionality."""
    
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
        """Create ContentAnalysisOrchestrator instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(mock_delivery_manager)
        
        # Mock enabling services
        orchestrator._file_parser_service = Mock()
        orchestrator._file_parser_service.parse_file = AsyncMock(return_value={"success": True, "content": "parsed"})
        orchestrator._file_parser_service.detect_file_type = AsyncMock(return_value="pdf")
        
        # Mock MCP server
        orchestrator.mcp_server = Mock()
        orchestrator.mcp_server.execute_tool = AsyncMock(return_value={"success": True})
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrator_initializes(self, mock_delivery_manager):
        """Test orchestrator initializes correctly."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(mock_delivery_manager)
        
        assert orchestrator.service_name == "ContentAnalysisOrchestratorService"
        assert orchestrator.realm_name == "business_enablement"
        assert orchestrator.delivery_manager == mock_delivery_manager
    
    @pytest.mark.asyncio
    async def test_orchestrator_has_mcp_server(self, orchestrator):
        """Test orchestrator has MCP server initialized."""
        assert hasattr(orchestrator, 'mcp_server')
        assert orchestrator.mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_parse_file_composes_services(self, orchestrator):
        """Test parse_file composes enabling services."""
        result = await orchestrator.parse_file("test_file_123")
        
        assert isinstance(result, dict)
        # Verify orchestrator called enabling service
        if hasattr(orchestrator, '_file_parser_service') and orchestrator._file_parser_service:
            orchestrator._file_parser_service.parse_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_uploaded_files(self, orchestrator):
        """Test list_uploaded_files orchestrator method."""
        result = await orchestrator.list_uploaded_files(user_id="user_123")
        
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_get_file_details(self, orchestrator):
        """Test get_file_details orchestrator method."""
        result = await orchestrator.get_file_details(file_id="test_file_123", user_id="user_123")
        
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_process_documents(self, orchestrator):
        """Test process_documents orchestrator method."""
        result = await orchestrator.process_documents(
            file_ids=["file1", "file2"],
            user_id="user_123"
        )
        
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_convert_format(self, orchestrator):
        """Test convert_format orchestrator method."""
        result = await orchestrator.convert_format(
            file_id="test_file_123",
            target_format="parquet",
            user_id="user_123"
        )
        
        assert isinstance(result, dict)

