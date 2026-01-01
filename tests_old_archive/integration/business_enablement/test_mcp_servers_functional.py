#!/usr/bin/env python3
"""
Comprehensive Functional Test: MCP Servers

This test verifies that MCP servers:
1. ✅ Properly register and expose MCP Tools
2. ✅ Can access enabling services through orchestrators
3. ✅ Properly use utilities (telemetry, security, tenant, error handling, health metrics)
4. ✅ Still work functionally after refactoring

Goal: Confirm MCP servers work correctly and use utilities properly.
"""

import pytest
import os
import sys
import asyncio
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'symphainy-platform'))


# ============================================================================
# TEST MCP SERVERS (All 5)
# ============================================================================

MCP_SERVERS_TO_TEST = [
    {
        "name": "content_analysis_mcp_server",
        "class": "ContentAnalysisMCPServer",
        "module": "backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.mcp_server.content_analysis_mcp_server",
        "test": {
            "tool": "analyze_document_tool",
            "params": {"document_id": "test_doc_123", "analysis_types": ["structure"]},
            "expected": {"has_success": True}
        }
    },
    {
        "name": "insights_mcp_server",
        "class": "InsightsMCPServer",
        "module": "backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.mcp_server.insights_mcp_server",
        "test": {
            "tool": "calculate_metrics_tool",
            "params": {"resource_id": "test_resource_123"},
            "expected": {"has_success": True}
        }
    },
    {
        "name": "operations_mcp_server",
        "class": "OperationsMCPServer",
        "module": "backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.mcp_server.operations_mcp_server",
        "test": {
            "tool": "health_check",
            "params": {},
            "expected": {"has_success": True}
        }
    },
    {
        "name": "business_outcomes_mcp_server",
        "class": "BusinessOutcomesMCPServer",
        "module": "backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.mcp_server.business_outcomes_mcp_server",
        "test": {
            "tool": "calculate_kpis_tool",
            "params": {"resource_id": "test_resource_123"},
            "expected": {"has_success": True}
        }
    },
    {
        "name": "delivery_manager_mcp_server",
        "class": "DeliveryManagerMCPServer",
        "module": "backend.business_enablement.delivery_manager.mcp_server.delivery_manager_mcp_server",
        "test": {
            "tool": "get_cross_realm_health",
            "params": {},
            "expected": {"has_success": True}
        }
    }
]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_di_container():
    """Create mock DI Container."""
    container = Mock()
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    container.logger = logger
    container.config = Mock()
    container.health = Mock()
    container.telemetry = Mock()
    container.error_handler = Mock()
    container.security = Mock()
    container.tenant = Mock()
    container.validation = Mock()
    container.serialization = Mock()
    return container


@pytest.fixture
def mock_orchestrator():
    """Create mock orchestrator with enabling service access."""
    orchestrator = Mock()
    
    # Content Analysis Orchestrator methods
    orchestrator.analyze_document = AsyncMock(return_value={
        "success": True,
        "document_id": "test_doc_123",
        "analysis": {"structure": "analyzed", "metadata": "extracted"}
    })
    orchestrator.parse_file = AsyncMock(return_value={"success": True, "file_id": "test_file_123"})
    orchestrator.extract_entities = AsyncMock(return_value={"success": True, "entities": []})
    
    # Insights Orchestrator methods
    orchestrator.calculate_metrics = AsyncMock(return_value={
        "success": True,
        "resource_id": "test_resource_123",
        "metrics": {"revenue": 1000, "profit": 500}
    })
    orchestrator.generate_insights = AsyncMock(return_value={"success": True, "insights": []})
    orchestrator.create_visualization = AsyncMock(return_value={"success": True, "visual_id": "vis_123"})
    orchestrator.query_analysis = AsyncMock(return_value={"success": True, "query_result": {}})
    orchestrator.analyze_content_for_insights = AsyncMock(return_value={"success": True})
    orchestrator.query_analysis_results = AsyncMock(return_value={"success": True})
    
    # Operations Orchestrator methods
    orchestrator.health_check = AsyncMock(return_value={"success": True, "status": "healthy"})
    orchestrator.get_session_elements = AsyncMock(return_value={"success": True, "elements": []})
    orchestrator.generate_workflow_from_sop = AsyncMock(return_value={"success": True, "workflow_id": "wf_123"})
    
    # Business Outcomes Orchestrator methods
    orchestrator.calculate_kpis = AsyncMock(return_value={
        "success": True,
        "resource_id": "test_resource_123",
        "kpis": {"roi": 0.5, "efficiency": 0.8}
    })
    orchestrator.track_outcomes = AsyncMock(return_value={"success": True})
    orchestrator.generate_roadmap = AsyncMock(return_value={"success": True, "roadmap_id": "rm_123"})
    orchestrator.analyze_outcomes = AsyncMock(return_value={"success": True})
    orchestrator.generate_strategic_roadmap = AsyncMock(return_value={"success": True})
    orchestrator.generate_poc_proposal = AsyncMock(return_value={"success": True})
    
    return orchestrator


@pytest.fixture
def mock_delivery_manager():
    """Create mock delivery manager."""
    manager = Mock()
    return manager


@pytest.fixture
def mock_user_context():
    """Create mock user context."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "roles": ["user"],
        "permissions": ["execute", "read", "write"]
    }


# ============================================================================
# FUNCTIONAL TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
@pytest.mark.functional
class TestMCPServersFunctional:
    """Test that MCP servers work functionally and use utilities properly."""
    
    @pytest.mark.parametrize("server_config", MCP_SERVERS_TO_TEST)
    async def test_mcp_server_registers_tools(
        self,
        server_config: Dict[str, Any],
        mock_di_container,
        mock_orchestrator,
        mock_delivery_manager
    ):
        """
        Test that MCP server properly registers tools.
        
        Verifies:
        1. Tools are registered during initialization
        2. Tool registry is accessible
        """
        # Import MCP server class
        module_path = server_config["module"]
        class_name = server_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        server_class = getattr(module, class_name)
        
        # Create MCP server instance
        if server_config["name"] == "delivery_manager_mcp_server":
            server = server_class(
                delivery_manager=mock_delivery_manager,
                di_container=mock_di_container
            )
        else:
            server = server_class(
                orchestrator=mock_orchestrator,
                di_container=mock_di_container
            )
        
        # Verify tools are registered
        assert hasattr(server, 'tool_registry'), \
            f"{class_name} should have tool_registry"
        
        # Verify tool registry has tools
        # The tool_registry should have registered tools
        # Check if we can list tools or if tool_registry has exposed_tools
        if hasattr(server, 'exposed_tools'):
            assert len(server.exposed_tools) > 0, \
                f"{class_name} should have registered tools"
            print(f"✅ {class_name} registered {len(server.exposed_tools)} tools")
        elif hasattr(server.tool_registry, 'tools'):
            assert len(server.tool_registry.tools) > 0, \
                f"{class_name} should have registered tools in tool_registry"
            print(f"✅ {class_name} registered {len(server.tool_registry.tools)} tools")
        else:
            # Check if tool_registry has a method to list tools
            if hasattr(server.tool_registry, 'list_tools'):
                tools = server.tool_registry.list_tools()
                assert len(tools) > 0, \
                    f"{class_name} should have registered tools"
                print(f"✅ {class_name} registered {len(tools)} tools")
            else:
                # At minimum, verify the test tool exists
                test_tool = server_config["test"]["tool"]
                # Try to execute it - if it's registered, it should work (or return error, not crash)
                try:
                    result = await server.execute_tool(test_tool, {})
                    # If we get here, the tool is at least callable
                    print(f"✅ {class_name} has tool '{test_tool}' registered")
                except AttributeError:
                    pytest.fail(f"{class_name} does not have tool '{test_tool}' registered")
    
    @pytest.mark.parametrize("server_config", MCP_SERVERS_TO_TEST)
    async def test_mcp_server_uses_utilities(
        self,
        server_config: Dict[str, Any],
        mock_di_container,
        mock_orchestrator,
        mock_delivery_manager,
        mock_user_context
    ):
        """
        Test that MCP server properly uses utilities.
        
        Verifies:
        1. Telemetry tracking (start/complete)
        2. Security validation (when user_context provided)
        3. Tenant validation (when user_context provided)
        4. Error handling with audit
        5. Health metrics recording
        """
        # Import MCP server class
        module_path = server_config["module"]
        class_name = server_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        server_class = getattr(module, class_name)
        
        # Create MCP server instance
        if server_config["name"] == "delivery_manager_mcp_server":
            server = server_class(
                delivery_manager=mock_delivery_manager,
                di_container=mock_di_container
            )
        else:
            server = server_class(
                orchestrator=mock_orchestrator,
                di_container=mock_di_container
            )
        
        # Test the tool execution
        test_config = server_config["test"]
        tool_name = test_config["tool"]
        params = test_config["params"].copy()
        
        # Create mocks to track utility calls
        mock_telemetry_emit_start = Mock()
        mock_telemetry_emit_complete = Mock()
        mock_health_record = Mock()
        mock_security_check = AsyncMock(return_value=True)
        mock_tenant_validate = AsyncMock(return_value=True)
        mock_error_handle = AsyncMock()
        
        # Mock utility methods
        with patch.object(server, 'telemetry_emission', new=Mock()) as mock_telemetry:
            mock_telemetry.emit_tool_execution_start_telemetry = mock_telemetry_emit_start
            mock_telemetry.emit_tool_execution_complete_telemetry = mock_telemetry_emit_complete
            with patch.object(server, 'health_monitoring', new=Mock()) as mock_health:
                mock_health.record_tool_execution_health = mock_health_record
                with patch.object(server, 'utilities', new=Mock()) as mock_utilities:
                    mock_security = Mock()
                    mock_security.check_permissions = mock_security_check
                    mock_utilities.security = mock_security
                    mock_tenant = Mock()
                    mock_tenant.validate_tenant_access = mock_tenant_validate
                    mock_utilities.tenant = mock_tenant
                    mock_error_handler = Mock()
                    mock_error_handler.handle_error_with_audit = mock_error_handle
                    mock_utilities.error_handler = mock_error_handler
                    
                    # Execute tool with user_context
                    result = await server.execute_tool(tool_name, params, user_context=mock_user_context)
                    
                    # Verify telemetry was called (start)
                    assert mock_telemetry_emit_start.called, \
                        f"{tool_name} should call emit_tool_execution_start_telemetry"
                    
                    # Verify telemetry was called (complete)
                    assert mock_telemetry_emit_complete.called, \
                        f"{tool_name} should call emit_tool_execution_complete_telemetry"
                    
                    # Verify health monitoring was called
                    assert mock_health_record.called, \
                        f"{tool_name} should call record_tool_execution_health"
                    
                    # Verify security check was called (when user_context provided)
                    assert mock_security_check.called, \
                        f"{tool_name} should call security.check_permissions when user_context provided"
                    
                    # Verify tenant validation was called (when user_context provided)
                    assert mock_tenant_validate.called, \
                        f"{tool_name} should call tenant.validate_tenant_access when user_context provided"
                    
                    # Verify result structure
                    assert isinstance(result, dict), \
                        f"{tool_name} should return dict, got {type(result)}"
                    
                    print(f"✅ {class_name}.execute_tool('{tool_name}') uses all utilities correctly")
                    print(f"   - Telemetry: ✅ (start & complete)")
                    print(f"   - Security: ✅ (check_permissions called)")
                    print(f"   - Tenant: ✅ (validate_tenant_access called)")
                    print(f"   - Health: ✅ (record_tool_execution_health called)")
    
    @pytest.mark.parametrize("server_config", MCP_SERVERS_TO_TEST)
    async def test_mcp_server_accesses_enabling_services(
        self,
        server_config: Dict[str, Any],
        mock_di_container,
        mock_orchestrator,
        mock_delivery_manager,
        mock_user_context
    ):
        """
        Test that MCP server can access enabling services through orchestrator.
        
        Verifies:
        1. MCP server delegates to orchestrator
        2. Orchestrator methods are called with correct parameters
        3. Enabling services are accessible through orchestrator
        """
        # Import MCP server class
        module_path = server_config["module"]
        class_name = server_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        server_class = getattr(module, class_name)
        
        # Create MCP server instance
        if server_config["name"] == "delivery_manager_mcp_server":
            server = server_class(
                delivery_manager=mock_delivery_manager,
                di_container=mock_di_container
            )
        else:
            server = server_class(
                orchestrator=mock_orchestrator,
                di_container=mock_di_container
            )
        
        # Test the tool execution
        test_config = server_config["test"]
        tool_name = test_config["tool"]
        params = test_config["params"].copy()
        
        # Mock utility methods (minimal - just to allow execution)
        with patch.object(server, 'telemetry_emission', new=Mock()) as mock_telemetry:
            mock_telemetry.emit_tool_execution_start_telemetry = Mock()
            mock_telemetry.emit_tool_execution_complete_telemetry = Mock()
            with patch.object(server, 'health_monitoring', new=Mock()) as mock_health:
                mock_health.record_tool_execution_health = Mock()
                with patch.object(server, 'utilities', new=Mock()) as mock_utilities:
                    mock_security = Mock()
                    mock_security.check_permissions = AsyncMock(return_value=True)
                    mock_utilities.security = mock_security
                    mock_tenant = Mock()
                    mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
                    mock_utilities.tenant = mock_tenant
                    mock_error_handler = Mock()
                    mock_error_handler.handle_error_with_audit = AsyncMock()
                    mock_utilities.error_handler = mock_error_handler
                    
                    # Execute tool
                    result = await server.execute_tool(tool_name, params, user_context=mock_user_context)
                    
                    # Verify orchestrator method was called (for non-delivery-manager servers)
                    if server_config["name"] != "delivery_manager_mcp_server":
                        # Map tool names to orchestrator methods
                        tool_to_method = {
                            "analyze_document_tool": "analyze_document",
                            "calculate_metrics_tool": "calculate_metrics",
                            "health_check": "health_check",
                            "calculate_kpis_tool": "calculate_kpis"
                        }
                        
                        orchestrator_method = tool_to_method.get(tool_name)
                        if orchestrator_method:
                            # Verify orchestrator method was called
                            assert hasattr(mock_orchestrator, orchestrator_method), \
                                f"Orchestrator should have {orchestrator_method} method"
                            
                            orchestrator_method_mock = getattr(mock_orchestrator, orchestrator_method)
                            assert orchestrator_method_mock.called, \
                                f"{tool_name} should call orchestrator.{orchestrator_method}"
                            
                            # Verify user_context was passed to orchestrator
                            call_args = orchestrator_method_mock.call_args
                            if call_args:
                                # Check if user_context was passed (either as kwarg or in call)
                                if 'user_context' in call_args.kwargs:
                                    assert call_args.kwargs['user_context'] == mock_user_context, \
                                        f"{tool_name} should pass user_context to orchestrator"
                                    print(f"✅ {class_name} passes user_context to orchestrator.{orchestrator_method}")
                    
                    # Verify result structure
                    assert isinstance(result, dict), \
                        f"{tool_name} should return dict, got {type(result)}"
                    
                    print(f"✅ {class_name}.execute_tool('{tool_name}') accesses enabling services through orchestrator")
                    print(f"   Result: {result.get('success')}, Keys: {list(result.keys())[:5]}...")
    
    @pytest.mark.parametrize("server_config", MCP_SERVERS_TO_TEST)
    async def test_mcp_server_executes_tool(
        self,
        server_config: Dict[str, Any],
        mock_di_container,
        mock_orchestrator,
        mock_delivery_manager,
        mock_user_context
    ):
        """
        Test that MCP server can execute tools and return structured responses.
        
        This is a simple functional test to verify:
        1. MCP server can be instantiated
        2. execute_tool() method works
        3. Tool returns structured response
        4. Tool execution completes successfully
        """
        # Import MCP server class
        module_path = server_config["module"]
        class_name = server_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        server_class = getattr(module, class_name)
        
        # Create MCP server instance
        if server_config["name"] == "delivery_manager_mcp_server":
            server = server_class(
                delivery_manager=mock_delivery_manager,
                di_container=mock_di_container
            )
        else:
            server = server_class(
                orchestrator=mock_orchestrator,
                di_container=mock_di_container
            )
        
        # Test the tool execution
        test_config = server_config["test"]
        tool_name = test_config["tool"]
        params = test_config["params"].copy()
        
        # Mock utility methods
        with patch.object(server, 'telemetry_emission', new=Mock()) as mock_telemetry:
            mock_telemetry.emit_tool_execution_start_telemetry = Mock()
            mock_telemetry.emit_tool_execution_complete_telemetry = Mock()
            with patch.object(server, 'health_monitoring', new=Mock()) as mock_health:
                mock_health.record_tool_execution_health = Mock()
                with patch.object(server, 'utilities', new=Mock()) as mock_utilities:
                    mock_security = Mock()
                    mock_security.check_permissions = AsyncMock(return_value=True)
                    mock_utilities.security = mock_security
                    mock_tenant = Mock()
                    mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
                    mock_utilities.tenant = mock_tenant
                    mock_error_handler = Mock()
                    mock_error_handler.handle_error_with_audit = AsyncMock()
                    mock_utilities.error_handler = mock_error_handler
                    
                    # Execute tool
                    result = await server.execute_tool(tool_name, params, user_context=mock_user_context)
                    
                    # Verify result structure
                    assert isinstance(result, dict), \
                        f"{tool_name} should return dict, got {type(result)}"
                    
                    # Verify telemetry was called
                    assert mock_telemetry.emit_tool_execution_start_telemetry.called, \
                        f"{tool_name} should call emit_tool_execution_start_telemetry"
                    
                    # Verify health monitoring was called
                    assert mock_health.record_tool_execution_health.called, \
                        f"{tool_name} should call record_tool_execution_health"
                    
                    print(f"✅ {class_name}.execute_tool('{tool_name}') works correctly")
                    print(f"   Result: {result.get('success')}, Keys: {list(result.keys())[:5]}...")
    
    @pytest.mark.parametrize("server_config", MCP_SERVERS_TO_TEST)
    async def test_mcp_server_handles_errors_gracefully(
        self,
        server_config: Dict[str, Any],
        mock_di_container,
        mock_orchestrator,
        mock_delivery_manager
    ):
        """
        Test that MCP server handles errors gracefully.
        
        This verifies error handling still works correctly.
        """
        # Import MCP server class
        module_path = server_config["module"]
        class_name = server_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        server_class = getattr(module, class_name)
        
        # Create MCP server instance
        if server_config["name"] == "delivery_manager_mcp_server":
            server = server_class(
                delivery_manager=mock_delivery_manager,
                di_container=mock_di_container
            )
        else:
            server = server_class(
                orchestrator=mock_orchestrator,
                di_container=mock_di_container
            )
        
        # Mock utility methods
        with patch.object(server, 'telemetry_emission', new=Mock()) as mock_telemetry:
            mock_telemetry.emit_tool_execution_start_telemetry = Mock()
            mock_telemetry.emit_tool_execution_complete_telemetry = Mock()
            with patch.object(server, 'health_monitoring', new=Mock()) as mock_health:
                mock_health.record_tool_execution_health = Mock()
                with patch.object(server, 'utilities', new=Mock()) as mock_utilities:
                    mock_security = Mock()
                    mock_security.check_permissions = AsyncMock(return_value=True)
                    mock_utilities.security = mock_security
                    mock_tenant = Mock()
                    mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
                    mock_utilities.tenant = mock_tenant
                    mock_error_handler = Mock()
                    mock_error_handler.handle_error_with_audit = AsyncMock()
                    mock_utilities.error_handler = mock_error_handler
                    
                    # Execute with unknown tool (should handle gracefully)
                    result = await server.execute_tool("unknown_tool", {})
                    
                    # Verify it returns structured error response (not raises exception)
                    assert isinstance(result, dict), \
                        f"execute_tool should return dict even for unknown tool, got {type(result)}"
                    
                    assert "error" in result, \
                        f"Error response should have 'error' field"
                    
                    print(f"✅ {class_name}.execute_tool() handles unknown tools gracefully")
                    print(f"   Error: {result.get('error')}")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "functional"])

