#!/usr/bin/env python3
"""
Test MCP Servers Curator Registration

Tests that MCP servers properly register their tools with Curator.
"""

import os
import sys
import asyncio
from typing import Dict, Any
from datetime import datetime
from unittest.mock import Mock, AsyncMock, MagicMock

# Add the symphainy-platform directory to path
platform_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if platform_path not in sys.path:
    sys.path.insert(0, platform_path)

import pytest

# Import MCP servers
from backend.business_enablement.delivery_manager.mcp_server.delivery_manager_mcp_server import DeliveryManagerMCPServer
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.mcp_server.content_analysis_mcp_server import ContentAnalysisMCPServer
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.mcp_server.operations_mcp_server import OperationsMCPServer
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.mcp_server.insights_mcp_server import InsightsMCPServer
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.mcp_server.business_outcomes_mcp_server import BusinessOutcomesMCPServer
from backend.smart_city.mcp_server.smart_city_mcp_server import SmartCityMCPServer

# Import base class
from bases.mcp_server.mcp_server_base import MCPServerBase


class TestMCPCuratorRegistration:
    """Test suite for MCP server Curator registration."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container with Curator."""
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
        
        # Mock Curator
        container.curator = Mock()
        container.get_curator = Mock(return_value=container.curator)
        
        # Mock service discovery
        container.get_service = Mock(return_value=None)
        
        return container
    
    @pytest.fixture
    def mock_curator(self):
        """Create mock Curator with register_domain_capability."""
        curator = Mock()
        curator.register_domain_capability = AsyncMock(return_value=True)
        return curator
    
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
    # TEST 1: Registration Method Exists
    # ============================================================================
    
    def test_mcp_base_has_curator_registration(self, mock_di_container, mock_delivery_manager):
        """Test that MCPServerBase has register_with_curator method."""
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        assert hasattr(server, 'register_with_curator')
        assert hasattr(server, 'get_curator')
        assert hasattr(server, '_get_realm')
        assert callable(server.register_with_curator)
    
    # ============================================================================
    # TEST 2: Curator Access
    # ============================================================================
    
    def test_get_curator_returns_curator(self, mock_di_container, mock_delivery_manager, mock_curator):
        """Test that get_curator() returns Curator from DI container."""
        mock_di_container.get_curator = Mock(return_value=mock_curator)
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        curator = server.get_curator()
        assert curator is not None
        assert curator == mock_curator
    
    def test_get_curator_handles_missing_curator(self, mock_di_container, mock_delivery_manager):
        """Test that get_curator() handles missing Curator gracefully."""
        mock_di_container.get_curator = Mock(return_value=None)
        mock_di_container.curator = None
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        curator = server.get_curator()
        assert curator is None
    
    # ============================================================================
    # TEST 3: Realm Detection
    # ============================================================================
    
    def test_realm_detection_business_enablement(self, mock_di_container, mock_orchestrator):
        """Test that Business Enablement servers detect correct realm."""
        servers = [
            (ContentAnalysisMCPServer(mock_orchestrator, mock_di_container), "business_enablement"),
            (OperationsMCPServer(mock_orchestrator, mock_di_container), "business_enablement"),
            (InsightsMCPServer(mock_orchestrator, mock_di_container), "business_enablement"),
            (BusinessOutcomesMCPServer(mock_orchestrator, mock_di_container), "business_enablement"),
        ]
        
        for server, expected_realm in servers:
            realm = server._get_realm()
            assert realm == expected_realm, f"{server.service_name} should be {expected_realm}, got {realm}"
    
    def test_realm_detection_smart_city(self, mock_di_container):
        """Test that Smart City server detects correct realm."""
        server = SmartCityMCPServer(mock_di_container)
        realm = server._get_realm()
        assert realm == "smart_city"
    
    def test_realm_detection_delivery_manager(self, mock_di_container, mock_delivery_manager):
        """Test that Delivery Manager detects correct realm."""
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        realm = server._get_realm()
        assert realm == "business_enablement"
    
    # ============================================================================
    # TEST 4: Tool Registration with Curator
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_register_with_curator_registers_tools(self, mock_di_container, mock_delivery_manager, mock_curator):
        """Test that register_with_curator() registers all tools."""
        mock_di_container.get_curator = Mock(return_value=mock_curator)
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        # Get tool count
        tools = server.get_registered_tools()
        tool_count = len(tools)
        
        assert tool_count > 0, "Server should have registered tools"
        
        # Register with Curator
        result = await server.register_with_curator()
        
        # Verify registration was called
        assert mock_curator.register_domain_capability.called, "register_domain_capability should be called"
        
        # Verify it was called for each tool
        call_count = mock_curator.register_domain_capability.call_count
        assert call_count == tool_count, f"Should register {tool_count} tools, but called {call_count} times"
        
        # Verify result
        assert result is True, "Registration should return True on success"
    
    @pytest.mark.asyncio
    async def test_register_with_curator_capability_structure(self, mock_di_container, mock_delivery_manager, mock_curator):
        """Test that registered capabilities have correct structure."""
        mock_di_container.get_curator = Mock(return_value=mock_curator)
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        # Register with Curator
        await server.register_with_curator()
        
        # Get all calls
        calls = mock_curator.register_domain_capability.call_args_list
        
        assert len(calls) > 0, "Should have registered at least one capability"
        
        # Check first call structure
        first_call = calls[0]
        capability = first_call[0][0]  # First positional argument
        user_context = first_call[0][1] if len(first_call[0]) > 1 else None
        
        # Verify capability structure
        assert hasattr(capability, 'capability_name')
        assert hasattr(capability, 'service_name')
        assert hasattr(capability, 'protocol_name')
        assert hasattr(capability, 'description')
        assert hasattr(capability, 'realm')
        assert hasattr(capability, 'contracts')
        assert hasattr(capability, 'version')
        
        # Verify contracts structure
        assert 'mcp_tool' in capability.contracts
        mcp_tool_contract = capability.contracts['mcp_tool']
        assert 'tool_name' in mcp_tool_contract
        assert 'tool_definition' in mcp_tool_contract
        assert 'metadata' in mcp_tool_contract
        
        # Verify tool_definition structure
        tool_def = mcp_tool_contract['tool_definition']
        assert 'name' in tool_def
        assert 'description' in tool_def
        assert 'input_schema' in tool_def
    
    @pytest.mark.asyncio
    async def test_register_with_curator_all_servers(self, mock_di_container, mock_orchestrator, mock_delivery_manager, mock_curator):
        """Test that all MCP servers can register with Curator."""
        mock_di_container.get_curator = Mock(return_value=mock_curator)
        
        servers = [
            DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container),
            ContentAnalysisMCPServer(mock_orchestrator, mock_di_container),
            OperationsMCPServer(mock_orchestrator, mock_di_container),
            InsightsMCPServer(mock_orchestrator, mock_di_container),
            BusinessOutcomesMCPServer(mock_orchestrator, mock_di_container),
        ]
        
        for server in servers:
            # Reset mock for each server
            mock_curator.register_domain_capability.reset_mock()
            
            # Register
            result = await server.register_with_curator()
            
            # Verify registration was attempted
            assert mock_curator.register_domain_capability.called, f"{server.service_name} should register tools"
            assert result is True, f"{server.service_name} registration should succeed"
            
            # Verify realm is correct
            realm = server._get_realm()
            calls = mock_curator.register_domain_capability.call_args_list
            for call in calls:
                capability = call[0][0]
                assert capability.realm == realm, f"Capability realm should match server realm: {realm}"
    
    # ============================================================================
    # TEST 5: Registration Handles Errors Gracefully
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_register_with_curator_handles_missing_curator(self, mock_di_container, mock_delivery_manager):
        """Test that registration handles missing Curator gracefully."""
        mock_di_container.get_curator = Mock(return_value=None)
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        # Should not raise exception
        result = await server.register_with_curator()
        
        # Should return False when Curator unavailable
        assert result is False
    
    @pytest.mark.asyncio
    async def test_register_with_curator_handles_registration_failure(self, mock_di_container, mock_delivery_manager, mock_curator):
        """Test that registration handles individual tool registration failures."""
        mock_di_container.get_curator = Mock(return_value=mock_curator)
        
        # Make some registrations fail
        call_count = 0
        def side_effect(capability, user_context=None):
            nonlocal call_count
            call_count += 1
            # Fail first call, succeed rest
            return call_count > 1
        
        mock_curator.register_domain_capability = AsyncMock(side_effect=side_effect)
        
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        # Should not raise exception
        result = await server.register_with_curator()
        
        # Should return True if at least one tool registered
        tools = server.get_registered_tools()
        if len(tools) > 1:
            assert result is True, "Should return True if at least one tool registered"
    
    @pytest.mark.asyncio
    async def test_register_with_curator_handles_exceptions(self, mock_di_container, mock_delivery_manager, mock_curator):
        """Test that registration handles exceptions gracefully."""
        mock_di_container.get_curator = Mock(return_value=mock_curator)
        mock_curator.register_domain_capability = AsyncMock(side_effect=Exception("Test error"))
        
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        # Should not raise exception
        result = await server.register_with_curator()
        
        # Should return False on error
        assert result is False
    
    # ============================================================================
    # TEST 6: Registration in start_server
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_start_server_calls_curator_registration(self, mock_di_container, mock_delivery_manager, mock_curator):
        """Test that start_server() calls register_with_curator()."""
        mock_di_container.get_curator = Mock(return_value=mock_curator)
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        # Mock register_with_curator to track calls
        server.register_with_curator = AsyncMock(return_value=True)
        
        # Start server
        result = await server.start_server()
        
        # Verify registration was called
        assert server.register_with_curator.called, "start_server() should call register_with_curator()"
        assert result is True
    
    # ============================================================================
    # TEST 7: Protocol Name Generation
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_protocol_name_generation(self, mock_di_container, mock_delivery_manager, mock_curator):
        """Test that protocol names are generated correctly."""
        mock_di_container.get_curator = Mock(return_value=mock_curator)
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        await server.register_with_curator()
        
        # Check protocol names in registered capabilities
        calls = mock_curator.register_domain_capability.call_args_list
        for call in calls:
            capability = call[0][0]
            # Protocol name should end with "Protocol"
            assert capability.protocol_name.endswith("Protocol"), f"Protocol name should end with 'Protocol': {capability.protocol_name}"
            # Should be based on service name
            assert server.service_name.replace('_', '').lower() in capability.protocol_name.lower(), \
                f"Protocol name should be based on service name: {capability.protocol_name}"
    
    # ============================================================================
    # TEST 8: Tool Definition Structure
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_tool_definition_includes_all_fields(self, mock_di_container, mock_delivery_manager, mock_curator):
        """Test that tool definitions include all required fields."""
        mock_di_container.get_curator = Mock(return_value=mock_curator)
        server = DeliveryManagerMCPServer(mock_delivery_manager, mock_di_container)
        
        await server.register_with_curator()
        
        # Check tool definition structure
        calls = mock_curator.register_domain_capability.call_args_list
        for call in calls:
            capability = call[0][0]
            tool_def = capability.contracts['mcp_tool']['tool_definition']
            
            # Required fields
            assert 'name' in tool_def
            assert 'description' in tool_def
            assert 'input_schema' in tool_def
            
            # Optional but expected fields
            assert 'tags' in tool_def
            assert 'requires_tenant' in tool_def


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])





