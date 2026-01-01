#!/usr/bin/env python3
"""
Comprehensive Test Suite for All Migrated MCP Servers

Tests:
1. Server instantiation with new base
2. Tool registration
3. Utility access
4. Abstract methods
5. Curator registration (if implemented)
"""

import os
import sys
import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Add the symphainy-platform directory to path
platform_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if platform_path not in sys.path:
    sys.path.insert(0, platform_path)

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock

# Import MCP servers
from backend.business_enablement.delivery_manager.mcp_server.delivery_manager_mcp_server import DeliveryManagerMCPServer
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.mcp_server.content_analysis_mcp_server import ContentAnalysisMCPServer
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.mcp_server.operations_mcp_server import OperationsMCPServer
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.mcp_server.insights_mcp_server import InsightsMCPServer
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.mcp_server.business_outcomes_mcp_server import BusinessOutcomesMCPServer
from backend.smart_city.mcp_server.smart_city_mcp_server import SmartCityMCPServer

# Import base class to verify inheritance
from bases.mcp_server.mcp_server_base import MCPServerBase


class TestMCPMigration:
    """Test suite for migrated MCP servers."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container with all required utilities."""
        container = Mock()
        
        # Mock utilities
        container.logger = Mock()
        container.logger.info = Mock()
        container.logger.error = Mock()
        container.logger.warning = Mock()
        container.logger.debug = Mock()
        
        container.config = Mock()
        container.health = Mock()
        container.telemetry = Mock()
        container.error_handler = Mock()
        container.tenant = Mock()
        container.validation = Mock()
        container.serialization = Mock()
        container.security = Mock()
        
        # Mock curator
        container.curator = Mock()
        container.get_curator = Mock(return_value=container.curator)
        
        # Mock service discovery
        container.get_service = Mock(return_value=None)
        
        return container
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator."""
        orchestrator = Mock()
        orchestrator.get_health_status = AsyncMock(return_value={"status": "healthy"})
        orchestrator.is_initialized = True
        return orchestrator
    
    @pytest.fixture
    def mock_delivery_manager(self):
        """Create mock delivery manager."""
        manager = Mock()
        manager.get_health_status = AsyncMock(return_value={"status": "healthy"})
        manager.is_initialized = True
        return manager
    
    # ============================================================================
    # TEST 1: Base Class Inheritance
    # ============================================================================
    
    def test_delivery_manager_inherits_new_base(self, mock_di_container, mock_delivery_manager):
        """Test that DeliveryManagerMCPServer inherits from new base."""
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        assert isinstance(server, MCPServerBase)
        assert hasattr(server, 'utilities')
        assert hasattr(server, 'tool_registry')
        assert hasattr(server, 'telemetry_emission')
        assert hasattr(server, 'health_monitoring')
    
    def test_content_analysis_inherits_new_base(self, mock_di_container, mock_orchestrator):
        """Test that ContentAnalysisMCPServer inherits from new base."""
        server = ContentAnalysisMCPServer(mock_orchestrator, mock_di_container)
        assert isinstance(server, MCPServerBase)
        assert hasattr(server, 'utilities')
        assert hasattr(server, 'tool_registry')
    
    def test_operations_inherits_new_base(self, mock_di_container, mock_orchestrator):
        """Test that OperationsMCPServer inherits from new base."""
        server = OperationsMCPServer(mock_orchestrator, mock_di_container)
        assert isinstance(server, MCPServerBase)
        assert hasattr(server, 'utilities')
        assert hasattr(server, 'tool_registry')
    
    def test_insights_inherits_new_base(self, mock_di_container, mock_orchestrator):
        """Test that InsightsMCPServer inherits from new base."""
        server = InsightsMCPServer(mock_orchestrator, mock_di_container)
        assert isinstance(server, MCPServerBase)
        assert hasattr(server, 'utilities')
        assert hasattr(server, 'tool_registry')
    
    def test_business_outcomes_inherits_new_base(self, mock_di_container, mock_orchestrator):
        """Test that BusinessOutcomesMCPServer inherits from new base."""
        server = BusinessOutcomesMCPServer(mock_orchestrator, mock_di_container)
        assert isinstance(server, MCPServerBase)
        assert hasattr(server, 'utilities')
        assert hasattr(server, 'tool_registry')
    
    def test_smart_city_inherits_new_base(self, mock_di_container):
        """Test that SmartCityMCPServer inherits from new base."""
        server = SmartCityMCPServer(mock_di_container)
        assert isinstance(server, MCPServerBase)
        assert hasattr(server, 'utilities')
        assert hasattr(server, 'tool_registry')
    
    # ============================================================================
    # TEST 2: Tool Registration
    # ============================================================================
    
    def test_delivery_manager_tool_registration(self, mock_di_container, mock_delivery_manager):
        """Test that DeliveryManagerMCPServer registers tools."""
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        tools = server.get_registered_tools()
        assert isinstance(tools, dict)
        assert len(tools) > 0
        # Check for expected tools
        tool_names = list(tools.keys())
        assert "coordinate_cross_realm" in tool_names or any("coordinate" in name for name in tool_names)
    
    def test_content_analysis_tool_registration(self, mock_di_container, mock_orchestrator):
        """Test that ContentAnalysisMCPServer registers tools."""
        server = ContentAnalysisMCPServer(mock_orchestrator, mock_di_container)
        tools = server.get_registered_tools()
        assert isinstance(tools, dict)
        assert len(tools) > 0
    
    def test_operations_tool_registration(self, mock_di_container, mock_orchestrator):
        """Test that OperationsMCPServer registers tools."""
        server = OperationsMCPServer(mock_orchestrator, mock_di_container)
        tools = server.get_registered_tools()
        assert isinstance(tools, dict)
        assert len(tools) > 0
    
    def test_insights_tool_registration(self, mock_di_container, mock_orchestrator):
        """Test that InsightsMCPServer registers tools."""
        server = InsightsMCPServer(mock_orchestrator, mock_di_container)
        tools = server.get_registered_tools()
        assert isinstance(tools, dict)
        assert len(tools) > 0
    
    def test_business_outcomes_tool_registration(self, mock_di_container, mock_orchestrator):
        """Test that BusinessOutcomesMCPServer registers tools."""
        server = BusinessOutcomesMCPServer(mock_orchestrator, mock_di_container)
        tools = server.get_registered_tools()
        assert isinstance(tools, dict)
        assert len(tools) > 0
    
    # ============================================================================
    # TEST 3: Abstract Methods
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_delivery_manager_abstract_methods(self, mock_di_container, mock_delivery_manager):
        """Test that DeliveryManagerMCPServer implements all abstract methods."""
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        # Test get_usage_guide
        usage_guide = server.get_usage_guide()
        assert isinstance(usage_guide, dict)
        assert "server_name" in usage_guide
        assert "tools" in usage_guide
        
        # Test get_tool_list
        tool_list = server.get_tool_list()
        assert isinstance(tool_list, list)
        assert len(tool_list) > 0
        
        # Test get_health_status
        health = await server.get_health_status()
        assert isinstance(health, dict)
        assert "server_name" in health
        assert "status" in health
        
        # Test get_version_info
        version_info = server.get_version_info()
        assert isinstance(version_info, dict)
        assert "server_name" in version_info
        assert "version" in version_info
    
    @pytest.mark.asyncio
    async def test_content_analysis_abstract_methods(self, mock_di_container, mock_orchestrator):
        """Test that ContentAnalysisMCPServer implements all abstract methods."""
        server = ContentAnalysisMCPServer(mock_orchestrator, mock_di_container)
        
        usage_guide = server.get_usage_guide()
        assert isinstance(usage_guide, dict)
        
        tool_list = server.get_tool_list()
        assert isinstance(tool_list, list)
        assert len(tool_list) > 0
        
        health = await server.get_health_status()
        assert isinstance(health, dict)
        
        version_info = server.get_version_info()
        assert isinstance(version_info, dict)
    
    @pytest.mark.asyncio
    async def test_operations_abstract_methods(self, mock_di_container, mock_orchestrator):
        """Test that OperationsMCPServer implements all abstract methods."""
        server = OperationsMCPServer(mock_orchestrator, mock_di_container)
        
        usage_guide = server.get_usage_guide()
        assert isinstance(usage_guide, dict)
        
        tool_list = server.get_tool_list()
        assert isinstance(tool_list, list)
        assert len(tool_list) > 0
        
        health = await server.get_health_status()
        assert isinstance(health, dict)
        
        version_info = server.get_version_info()
        assert isinstance(version_info, dict)
    
    @pytest.mark.asyncio
    async def test_insights_abstract_methods(self, mock_di_container, mock_orchestrator):
        """Test that InsightsMCPServer implements all abstract methods."""
        server = InsightsMCPServer(mock_orchestrator, mock_di_container)
        
        usage_guide = server.get_usage_guide()
        assert isinstance(usage_guide, dict)
        
        tool_list = server.get_tool_list()
        assert isinstance(tool_list, list)
        assert len(tool_list) > 0
        
        health = await server.get_health_status()
        assert isinstance(health, dict)
        
        version_info = server.get_version_info()
        assert isinstance(version_info, dict)
    
    @pytest.mark.asyncio
    async def test_business_outcomes_abstract_methods(self, mock_di_container, mock_orchestrator):
        """Test that BusinessOutcomesMCPServer implements all abstract methods."""
        server = BusinessOutcomesMCPServer(mock_orchestrator, mock_di_container)
        
        usage_guide = server.get_usage_guide()
        assert isinstance(usage_guide, dict)
        
        tool_list = server.get_tool_list()
        assert isinstance(tool_list, list)
        assert len(tool_list) > 0
        
        health = await server.get_health_status()
        assert isinstance(health, dict)
        
        version_info = server.get_version_info()
        assert isinstance(version_info, dict)
    
    @pytest.mark.asyncio
    async def test_smart_city_abstract_methods(self, mock_di_container):
        """Test that SmartCityMCPServer implements all abstract methods."""
        server = SmartCityMCPServer(mock_di_container)
        
        usage_guide = server.get_usage_guide()
        assert isinstance(usage_guide, dict)
        assert "server_type" in usage_guide
        assert usage_guide["server_type"] == "unified"
        
        tool_list = server.get_tool_list()
        assert isinstance(tool_list, list)
        
        health = await server.get_health_status()
        assert isinstance(health, dict)
        
        version_info = server.get_version_info()
        assert isinstance(version_info, dict)
    
    # ============================================================================
    # TEST 4: Utility Access
    # ============================================================================
    
    def test_delivery_manager_utility_access(self, mock_di_container, mock_delivery_manager):
        """Test that DeliveryManagerMCPServer can access utilities."""
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        assert hasattr(server, 'utilities')
        assert hasattr(server.utilities, 'logger')
        assert hasattr(server.utilities, 'config')
        assert hasattr(server.utilities, 'telemetry')
        assert hasattr(server.utilities, 'security')
        assert hasattr(server.utilities, 'error_handler')
        assert hasattr(server.utilities, 'tenant')
    
    def test_all_servers_utility_access(self, mock_di_container, mock_orchestrator):
        """Test that all servers can access utilities."""
        servers = [
            ContentAnalysisMCPServer(mock_orchestrator, mock_di_container),
            OperationsMCPServer(mock_orchestrator, mock_di_container),
            InsightsMCPServer(mock_orchestrator, mock_di_container),
            BusinessOutcomesMCPServer(mock_orchestrator, mock_di_container),
        ]
        
        for server in servers:
            assert hasattr(server, 'utilities')
            assert hasattr(server.utilities, 'logger')
            assert hasattr(server.utilities, 'telemetry')
    
    # ============================================================================
    # TEST 5: Curator Registration (Check if implemented)
    # ============================================================================
    
    def test_curator_registration_availability(self, mock_di_container, mock_delivery_manager):
        """Test if MCP servers have Curator registration capability."""
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        # Check if server has method to register with Curator
        # Note: This might not be implemented yet, so we're just checking
        has_curator_registration = (
            hasattr(server, 'register_with_curator') or
            hasattr(server, 'register_mcp_tools') or
            hasattr(server.tool_registry, 'register_with_curator')
        )
        
        # Log result (not a failure if not implemented)
        print(f"\n📋 Curator registration available: {has_curator_registration}")
        if not has_curator_registration:
            print("   ⚠️  Note: Curator registration may need to be added to MCP servers")
    
    # ============================================================================
    # TEST 6: Service Name Consistency
    # ============================================================================
    
    def test_service_name_consistency(self, mock_di_container, mock_delivery_manager, mock_orchestrator):
        """Test that service_name is set correctly."""
        servers = [
            (DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container), "delivery_manager_mcp"),
            (ContentAnalysisMCPServer(mock_orchestrator, mock_di_container), "content_analysis_mcp"),
            (OperationsMCPServer(mock_orchestrator, mock_di_container), "operations_mcp"),
            (InsightsMCPServer(mock_orchestrator, mock_di_container), "insights_mcp"),
            (BusinessOutcomesMCPServer(mock_orchestrator, mock_di_container), "business_outcomes_mcp"),
            (SmartCityMCPServer(mock_di_container), "smart_city_mcp"),
        ]
        
        for server, expected_name in servers:
            assert hasattr(server, 'service_name')
            assert server.service_name == expected_name, f"Expected {expected_name}, got {server.service_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

