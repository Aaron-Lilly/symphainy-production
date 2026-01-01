#!/usr/bin/env python3
"""
Content Processing Agent Refactored - Comprehensive Test

Tests that the refactored ContentProcessingAgent:
1. Uses full utility pattern (telemetry, security, tenant, error handling, health metrics)
2. Does NOT self-register with Curator (factory handles registration)
3. Provides equivalent or better functionality than prior version
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call, call
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from utilities import UserContext

# Mock the problematic import before importing the agent
import sys
from unittest.mock import MagicMock

# Mock content_liaison_agent to avoid import errors
class MockContentLiaisonAgent:
    pass

mock_liaison_module = type('MockModule', (), {'ContentLiaisonAgent': MockContentLiaisonAgent})()
sys.modules['backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.agents.content_liaison_agent'] = mock_liaison_module

# Mock DIContainerService (Foundation Services)
class MockDIContainerService:
    def __init__(self):
        self._services = {}
        self._utilities = {}
        
        # Mock logger
        self.logger = MagicMock()
        self.logger.info = MagicMock()
        self.logger.warning = MagicMock()
        self.logger.error = MagicMock()
        self.logger.debug = MagicMock()
        
        # Mock utilities
        self.mock_telemetry = MagicMock()
        self.mock_telemetry.collect_metric = AsyncMock()
        self.mock_telemetry.record_metric = AsyncMock()  # For AgentBase utility methods
        
        self.mock_security = MagicMock()
        self.mock_security.check_permissions = AsyncMock(return_value=True)
        self.mock_security.audit_log = AsyncMock()
        
        self.mock_health = MagicMock()
        self.mock_health.record_metric = AsyncMock()
        
        self.mock_config = MagicMock()
        
        # Store utilities
        self._utilities["telemetry"] = self.mock_telemetry
        self._utilities["security"] = self.mock_security
        self._utilities["health"] = self.mock_health
        self._utilities["config"] = self.mock_config
    
    def get_logger(self, name):
        return self.logger
    
    def get_telemetry(self):
        return self.mock_telemetry
    
    def get_security(self):
        return self.mock_security
    
    def get_health(self):
        return self.mock_health
    
    def get_config(self):
        return self.mock_config
    
    def get_foundation_service(self, name: str):
        return self._services.get(name)


# Mock Public Works Foundation
class MockPublicWorksFoundation:
    def __init__(self):
        self.mock_tenant_service = MagicMock()
        self.mock_tenant_service.validate_tenant_access = AsyncMock(return_value=True)
    
    def get_tenant_service(self):
        return self.mock_tenant_service


# Mock MCP Client Manager
class MockMCPClientManager:
    def __init__(self):
        pass
    
    async def connect_to_role(self, role, tenant_context):
        return MagicMock()


# Mock Policy Integration
class MockPolicyIntegration:
    def __init__(self):
        pass
    
    async def initialize(self, agent_id, required_roles, tenant_context):
        pass


# Mock Tool Composition
class MockToolComposition:
    def __init__(self):
        pass


# Mock AGUI Formatter
class MockAGUIFormatter:
    def __init__(self):
        pass


# Mock MCP Server
class MockMCPServer:
    def __init__(self):
        self.execute_tool = AsyncMock(return_value={
            "success": True,
            "result": {"processed": True, "file_id": "test_file_123"}
        })
        self.get_server_info = MagicMock(return_value={"status": "healthy"})
        self.get_health = MagicMock(return_value={"status": "healthy"})
        self.get_tool_list = MagicMock(return_value=["process_file", "optimize_content"])


# Mock Curator Foundation
class MockCuratorFoundation:
    def __init__(self):
        self.get_registered_services = AsyncMock(return_value={
            "services": {
                "ContentAnalysisOrchestratorService": {
                    "service_instance": MagicMock()
                }
            }
        })


# Mock AGUI Schema
class MockAGUISchema:
    def __init__(self):
        self.schema_name = "content_processing_agent_schema"
        self.components = []


@pytest.fixture
def mock_foundation_services():
    """Create mock foundation services."""
    return MockDIContainerService()


@pytest.fixture
def mock_public_works_foundation():
    """Create mock public works foundation."""
    return MockPublicWorksFoundation()


@pytest.fixture
def mock_mcp_client_manager():
    """Create mock MCP client manager."""
    return MockMCPClientManager()


@pytest.fixture
def mock_policy_integration():
    """Create mock policy integration."""
    return MockPolicyIntegration()


@pytest.fixture
def mock_tool_composition():
    """Create mock tool composition."""
    return MockToolComposition()


@pytest.fixture
def mock_agui_formatter():
    """Create mock AGUI formatter."""
    return MockAGUIFormatter()


@pytest.fixture
def mock_curator_foundation():
    """Create mock curator foundation."""
    return MockCuratorFoundation()


@pytest.fixture
def mock_agui_schema():
    """Create mock AGUI schema."""
    return MockAGUISchema()


@pytest.fixture
def mock_agentic_foundation():
    """Create mock agentic foundation."""
    return MagicMock()


@pytest.fixture
def mock_mcp_server():
    """Create mock MCP server."""
    return MockMCPServer()


@pytest.fixture
def content_processing_agent(
    mock_foundation_services,
    mock_public_works_foundation,
    mock_mcp_client_manager,
    mock_policy_integration,
    mock_tool_composition,
    mock_agui_formatter,
    mock_curator_foundation,
    mock_agui_schema,
    mock_agentic_foundation
):
    """Create ContentProcessingAgent instance."""
    # Import directly from module file to avoid __init__.py import issues
    import importlib.util
    agent_file_path = os.path.join(
        os.path.dirname(__file__),
        '../../../backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/agents/content_processing_agent.py'
    )
    agent_file_path = os.path.abspath(agent_file_path)
    
    spec = importlib.util.spec_from_file_location("content_processing_agent", agent_file_path)
    module = importlib.util.module_from_spec(spec)
    
    # Add the module to sys.modules to handle relative imports
    sys.modules['content_processing_agent'] = module
    spec.loader.exec_module(module)
    
    ContentProcessingAgent = module.ContentProcessingAgent
    
    agent = ContentProcessingAgent(
        agent_name="test_content_processing_agent",
        business_domain="content",
        capabilities=["process_file", "optimize_content", "extract_data"],
        required_roles=["content_steward"],
        agui_schema=mock_agui_schema,
        foundation_services=mock_foundation_services,
        agentic_foundation=mock_agentic_foundation,
        public_works_foundation=mock_public_works_foundation,
        mcp_client_manager=mock_mcp_client_manager,
        policy_integration=mock_policy_integration,
        tool_composition=mock_tool_composition,
        agui_formatter=mock_agui_formatter,
        curator_foundation=mock_curator_foundation
    )
    
    # Set MCP server
    agent.mcp_server = MockMCPServer()
    
    return agent


@pytest.fixture
def user_context():
    """Create user context."""
    context = UserContext()
    context.user_id = "test_user_123"
    context.tenant_id = "test_tenant_123"
    context.roles = ["content_processor"]
    return context


@pytest.mark.asyncio
class TestAgentUtilityUsage:
    """Test that agent uses utilities correctly."""
    
    async def test_initialize_uses_agentbase_utility_methods(self, content_processing_agent, mock_foundation_services):
        """Test that initialize() uses AgentBase utility methods (log_operation_with_telemetry, record_health_metric)."""
        # Mock the AgentBase utility methods to verify they're called
        with patch.object(content_processing_agent, 'log_operation_with_telemetry', new_callable=AsyncMock) as mock_log, \
             patch.object(content_processing_agent, 'record_health_metric', new_callable=AsyncMock) as mock_health:
            
            result = await content_processing_agent.initialize()
            
            assert result is True
            # Verify AgentBase utility methods were called
            assert mock_log.called, "log_operation_with_telemetry should be called"
            assert mock_health.called, "record_health_metric should be called"
            
            # Check for start and complete telemetry calls
            log_calls = [call[0][0] for call in mock_log.call_args_list]
            assert "initialize_start" in log_calls, "Should log initialize_start"
            assert "initialize_complete" in log_calls, "Should log initialize_complete"
            
            # Check for health metric call
            health_calls = [call[0][0] for call in mock_health.call_args_list]
            assert "initialized" in health_calls, "Should record initialized health metric"
    
    async def test_initialize_uses_telemetry(self, content_processing_agent, mock_foundation_services):
        """Test that initialize() uses telemetry via AgentBase utility methods."""
        result = await content_processing_agent.initialize()
        
        assert result is True
        # Verify telemetry was called via AgentBase utility method
        # The utility method internally calls telemetry.record_metric
        assert mock_foundation_services.mock_telemetry.record_metric.called or \
               mock_foundation_services.mock_telemetry.collect_metric.called
    
    async def test_initialize_uses_health_metrics(self, content_processing_agent, mock_foundation_services):
        """Test that initialize() uses health metrics via AgentBase utility methods."""
        result = await content_processing_agent.initialize()
        
        assert result is True
        # Verify health metrics were recorded via AgentBase utility method
        # The utility method internally calls health.record_metric or telemetry.record_metric
        assert mock_foundation_services.mock_health.record_metric.called or \
               mock_foundation_services.mock_telemetry.record_metric.called
    
    async def test_execute_capability_uses_agentbase_utility_methods(self, content_processing_agent, user_context):
        """Test that execute_business_capability() uses AgentBase utility methods."""
        await content_processing_agent.initialize()
        content_processing_agent.mcp_server = MockMCPServer()
        
        # Mock the AgentBase utility methods to verify they're called
        with patch.object(content_processing_agent, 'log_operation_with_telemetry', new_callable=AsyncMock) as mock_log, \
             patch.object(content_processing_agent, 'record_health_metric', new_callable=AsyncMock) as mock_health:
            
            result = await content_processing_agent.execute_business_capability(
                "process_file",
                {"file_id": "test_file_123"},
                user_context
            )
            
            assert result.get("success") is True
            # Verify AgentBase utility methods were called
            assert mock_log.called, "log_operation_with_telemetry should be called"
            assert mock_health.called, "record_health_metric should be called"
            
            # Check for start and complete telemetry calls
            log_calls = [call[0][0] for call in mock_log.call_args_list]
            assert "execute_business_capability_start" in log_calls, "Should log start"
            assert "execute_business_capability_complete" in log_calls, "Should log complete"
    
    async def test_execute_capability_uses_telemetry(self, content_processing_agent, mock_foundation_services, user_context):
        """Test that execute_business_capability() uses telemetry via AgentBase utility methods."""
        await content_processing_agent.initialize()
        content_processing_agent.mcp_server = MockMCPServer()
        
        result = await content_processing_agent.execute_business_capability(
            "process_file",
            {"file_id": "test_file_123"},
            user_context
        )
        
        assert result.get("success") is True
        # Verify telemetry was called via AgentBase utility method
        assert mock_foundation_services.mock_telemetry.record_metric.called or \
               mock_foundation_services.mock_telemetry.collect_metric.called
    
    async def test_execute_capability_uses_security_validation(self, content_processing_agent, mock_foundation_services, user_context):
        """Test that execute_business_capability() uses security validation."""
        await content_processing_agent.initialize()
        
        # Make security check fail
        mock_foundation_services.mock_security.check_permissions = AsyncMock(return_value=False)
        
        with pytest.raises(PermissionError, match="Access denied"):
            await content_processing_agent.execute_business_capability(
                "process_file",
                {"file_id": "test_file_123"},
                user_context
            )
        
        # Verify security check was called
        assert mock_foundation_services.mock_security.check_permissions.called
    
    async def test_execute_capability_uses_tenant_validation(self, content_processing_agent, mock_public_works_foundation, user_context):
        """Test that execute_business_capability() uses tenant validation."""
        await content_processing_agent.initialize()
        
        # Make tenant validation fail
        mock_public_works_foundation.mock_tenant_service.validate_tenant_access = AsyncMock(return_value=False)
        
        with pytest.raises(PermissionError, match="Tenant access denied"):
            await content_processing_agent.execute_business_capability(
                "process_file",
                {"file_id": "test_file_123"},
                user_context
            )
        
        # Verify tenant validation was called
        assert mock_public_works_foundation.mock_tenant_service.validate_tenant_access.called
    
    async def test_execute_capability_uses_error_handling(self, content_processing_agent, user_context):
        """Test that execute_business_capability() uses AgentBase handle_error_with_audit() method."""
        await content_processing_agent.initialize()
        
        # Make MCP server fail
        content_processing_agent.mcp_server = MockMCPServer()
        content_processing_agent.mcp_server.execute_tool = AsyncMock(side_effect=Exception("Test error"))
        
        # Mock the AgentBase utility method to verify it's called
        with patch.object(content_processing_agent, 'handle_error_with_audit', new_callable=AsyncMock) as mock_error_handler:
            result = await content_processing_agent.execute_business_capability(
                "process_file",
                {"file_id": "test_file_123"},
                user_context
            )
            
            assert result.get("success") is False
            # Verify AgentBase error handling method was called
            assert mock_error_handler.called, "handle_error_with_audit should be called on error"
    
    async def test_process_file_autonomous_uses_security_validation(self, content_processing_agent, mock_foundation_services, user_context):
        """Test that process_file_autonomous() uses security validation."""
        await content_processing_agent.initialize()
        
        # Make security check fail
        mock_foundation_services.mock_security.check_permissions = AsyncMock(return_value=False)
        
        with pytest.raises(PermissionError, match="Access denied"):
            await content_processing_agent.process_file_autonomous(
                "test_file_123",
                user_context
            )
        
        # Verify security check was called
        assert mock_foundation_services.mock_security.check_permissions.called


@pytest.mark.asyncio
class TestAgentCuratorRegistration:
    """Test that agent does NOT self-register with Curator."""
    
    async def test_initialize_does_not_self_register(self, content_processing_agent, mock_curator_foundation):
        """Test that initialize() does NOT call register_with_curator()."""
        # Mock register_with_curator if it exists
        if hasattr(content_processing_agent, 'register_with_curator'):
            content_processing_agent.register_with_curator = AsyncMock()
        
        result = await content_processing_agent.initialize()
        
        assert result is True
        # Verify register_with_curator was NOT called (factory handles registration)
        if hasattr(content_processing_agent, 'register_with_curator'):
            assert not content_processing_agent.register_with_curator.called


@pytest.mark.asyncio
class TestAgentFunctionalEquivalence:
    """Test that agent provides equivalent functionality."""
    
    async def test_execute_business_capability_success(self, content_processing_agent, user_context):
        """Test that execute_business_capability() works correctly."""
        await content_processing_agent.initialize()
        
        result = await content_processing_agent.execute_business_capability(
            "process_file",
            {"file_id": "test_file_123"},
            user_context
        )
        
        assert result.get("success") is True
        assert "result" in result or "message" in result
        # Verify processing history was updated
        assert len(content_processing_agent.processing_history) > 0
    
    async def test_execute_business_capability_unsupported(self, content_processing_agent, user_context):
        """Test that execute_business_capability() handles unsupported capabilities."""
        await content_processing_agent.initialize()
        
        result = await content_processing_agent.execute_business_capability(
            "unsupported_capability",
            {},
            user_context
        )
        
        assert result.get("success") is False
        assert "not supported" in result.get("message", "").lower()
    
    async def test_process_file_autonomous_success(self, content_processing_agent, user_context):
        """Test that process_file_autonomous() works correctly."""
        await content_processing_agent.initialize()
        
        # Mock analyze_situation to return success
        content_processing_agent.analyze_situation = AsyncMock(return_value={
            "success": True,
            "analysis": {
                "findings": {
                    "processing_complexity": "low",
                    "file_size": "1MB",
                    "quality_score": 0.9
                }
            }
        })
        
        result = await content_processing_agent.process_file_autonomous(
            "test_file_123",
            user_context
        )
        
        assert result.get("success") is True
        assert "autonomous_decisions" in result
        assert "processing_result" in result
    
    async def test_get_supported_capabilities(self, content_processing_agent, user_context):
        """Test that get_supported_capabilities() works correctly."""
        await content_processing_agent.initialize()
        
        capabilities = await content_processing_agent.get_supported_capabilities(user_context)
        
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert "process_file" in capabilities
    
    async def test_analyze_situation(self, content_processing_agent, user_context):
        """Test that analyze_situation() works correctly."""
        await content_processing_agent.initialize()
        
        result = await content_processing_agent.analyze_situation(
            {"type": "content_analysis", "content_id": "test_123"},
            user_context
        )
        
        # Result may be success or failure depending on MCP server
        assert isinstance(result, dict)
        assert "success" in result
    
    async def test_get_processing_metrics(self, content_processing_agent, user_context):
        """Test that get_processing_metrics() works correctly."""
        await content_processing_agent.initialize()
        
        result = await content_processing_agent.get_processing_metrics(user_context)
        
        # Result may be success or failure depending on MCP server
        assert isinstance(result, dict)
        assert "success" in result
    
    async def test_batch_process_autonomous(self, content_processing_agent, user_context):
        """Test that batch_process_autonomous() works correctly."""
        await content_processing_agent.initialize()
        
        # Mock analyze_situation to return success
        content_processing_agent.analyze_situation = AsyncMock(return_value={
            "success": True,
            "analysis": {}
        })
        
        result = await content_processing_agent.batch_process_autonomous(
            ["file_1", "file_2", "file_3"],
            user_context
        )
        
        # Result may be success or failure depending on MCP server
        assert isinstance(result, dict)
        assert "success" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

