#!/usr/bin/env python3
"""
Content Processing Agent LLM Integration Test

Tests the refactored ContentProcessingAgent with real LLM calls to verify:
1. Agent initializes correctly with AgentBase utility methods
2. Agent can use LLM abstraction (if available)
3. Agent's utility methods work correctly
4. End-to-end agent functionality

This test does NOT require full backend startup - it creates minimal components.
"""

import pytest
import os
import sys
import asyncio
from typing import Dict, Any, Optional
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Skip if API keys are not available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_OPENAI_API_KEY")
if not OPENAI_API_KEY and os.path.exists("../../.env.secrets"):
    try:
        with open("../../.env.secrets", "r") as f:
            for line in f:
                if line.startswith("LLM_OPENAI_API_KEY="):
                    OPENAI_API_KEY = line.split("=", 1)[1].strip()
                    break
    except:
        pass

pytestmark = pytest.mark.integration


class TestContentProcessingAgentLLMIntegration:
    """Test ContentProcessingAgent with real LLM calls."""
    
    @pytest.fixture
    def minimal_di_container(self):
        """Create minimal DI container with real utilities."""
        from unittest.mock import MagicMock
        
        class MinimalDIContainer:
            def __init__(self):
                # Create real logger
                import logging
                self.logger = logging.getLogger("TestContentProcessingAgent")
                self.logger.setLevel(logging.INFO)
                
                # Mock utilities
                self.mock_config = MagicMock()
                self.mock_health = MagicMock()
                self.mock_telemetry = MagicMock()
                self.mock_security = MagicMock()
                self.mock_security.check_permissions = AsyncMock(return_value=True)
                self.mock_security.audit_log = AsyncMock()
            
            def get_logger(self, name):
                return self.logger
            
            def get_config(self):
                return self.mock_config
            
            def get_health(self):
                return self.mock_health
            
            def get_telemetry(self):
                return self.mock_telemetry
            
            def get_security(self):
                return self.mock_security
        
        return MinimalDIContainer()
    
    @pytest.fixture
    def llm_abstraction(self, minimal_di_container):
        """Create LLM abstraction with real API key."""
        if not OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
        
        from foundations.public_works_foundation.infrastructure_adapters.openai_adapter import OpenAIAdapter
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction
        
        openai_adapter = OpenAIAdapter(api_key=OPENAI_API_KEY)
        
        return LLMAbstraction(
            openai_adapter=openai_adapter,
            anthropic_adapter=None,
            provider="openai",
            di_container=minimal_di_container
        )
    
    @pytest.fixture
    def public_works_foundation(self, llm_abstraction):
        """Create mock Public Works Foundation with LLM abstraction."""
        mock_pwf = MagicMock()
        mock_pwf.get_llm_business_abstraction = MagicMock(return_value=llm_abstraction)
        mock_pwf.get_tenant_service = MagicMock(return_value=MagicMock())
        return mock_pwf
    
    @pytest.fixture
    def agentic_foundation(self, llm_abstraction):
        """Create mock Agentic Foundation with LLM abstraction."""
        mock_af = MagicMock()
        mock_af.get_llm_abstraction = AsyncMock(return_value=llm_abstraction)
        mock_af.di_container = MagicMock()
        return mock_af
    
    @pytest.fixture
    def agui_schema(self):
        """Create mock AGUI schema."""
        from unittest.mock import MagicMock
        schema = MagicMock()
        schema.schema_name = "content_processing_agent_schema"
        schema.components = []
        return schema
    
    @pytest.fixture
    def content_processing_agent(
        self,
        minimal_di_container,
        public_works_foundation,
        agentic_foundation,
        agui_schema
    ):
        """Create ContentProcessingAgent instance."""
        # Import directly from file to avoid __init__.py import issues
        import importlib.util
        agent_file_path = os.path.join(
            os.path.dirname(__file__),
            '../../../backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/agents/content_processing_agent.py'
        )
        agent_file_path = os.path.abspath(agent_file_path)
        
        spec = importlib.util.spec_from_file_location("content_processing_agent", agent_file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules['content_processing_agent'] = module
        spec.loader.exec_module(module)
        
        ContentProcessingAgent = module.ContentProcessingAgent
        from backend.business_enablement.protocols.business_specialist_agent_protocol import SpecialistCapability
        
        # Mock other required dependencies
        mock_mcp_client_manager = MagicMock()
        mock_policy_integration = MagicMock()
        mock_policy_integration.initialize = AsyncMock()
        mock_tool_composition = MagicMock()
        mock_agui_formatter = MagicMock()
        mock_curator_foundation = MagicMock()
        mock_curator_foundation.get_registered_services = AsyncMock(return_value={"services": {}})
        
        agent = ContentProcessingAgent(
            agent_name="TestContentProcessingAgent",
            business_domain="content",
            capabilities=["process_file", "optimize_content", "extract_data", "convert_format", "assess_quality", "batch_process"],
            required_roles=["content_steward"],
            agui_schema=agui_schema,
            foundation_services=minimal_di_container,
            agentic_foundation=agentic_foundation,
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mock_mcp_client_manager,
            policy_integration=mock_policy_integration,
            tool_composition=mock_tool_composition,
            agui_formatter=mock_agui_formatter,
            curator_foundation=mock_curator_foundation,
            specialist_capability=SpecialistCapability.CONTENT_PROCESSING
        )
        
        # Mock MCP server (for tool execution)
        mock_mcp_server = MagicMock()
        mock_mcp_server.execute_tool = AsyncMock(return_value={
            "success": True,
            "result": {"processed": True, "file_id": "test_file_123"}
        })
        agent.mcp_server = mock_mcp_server
        
        return agent
    
    @pytest.fixture
    def user_context(self):
        """Create user context."""
        from utilities import UserContext
        context = UserContext()
        context.user_id = "test_user_123"
        context.tenant_id = "test_tenant_123"
        context.roles = ["content_processor"]
        return context
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_agent_initializes_with_utility_methods(self, content_processing_agent):
        """Test that agent initializes and uses AgentBase utility methods."""
        # Mock the utility methods to verify they're called
        with pytest.mock.patch.object(content_processing_agent, 'log_operation_with_telemetry', new_callable=AsyncMock) as mock_log, \
             pytest.mock.patch.object(content_processing_agent, 'record_health_metric', new_callable=AsyncMock) as mock_health:
            
            result = await content_processing_agent.initialize()
            
            assert result is True, "Agent should initialize successfully"
            assert content_processing_agent.is_initialized, "Agent should be initialized"
            
            # Verify utility methods were called
            assert mock_log.called, "log_operation_with_telemetry should be called"
            assert mock_health.called, "record_health_metric should be called"
            
            # Check for specific log calls
            log_calls = [call[0][0] for call in mock_log.call_args_list]
            assert "initialize_start" in log_calls, "Should log initialize_start"
            assert "initialize_complete" in log_calls, "Should log initialize_complete"
            
            print("\n✅ Agent initialized successfully with utility methods")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_agent_executes_capability_with_utility_methods(self, content_processing_agent, user_context):
        """Test that agent executes capabilities and uses utility methods."""
        await content_processing_agent.initialize()
        
        # Mock utility methods to verify usage
        with pytest.mock.patch.object(content_processing_agent, 'log_operation_with_telemetry', new_callable=AsyncMock) as mock_log, \
             pytest.mock.patch.object(content_processing_agent, 'record_health_metric', new_callable=AsyncMock) as mock_health:
            
            result = await content_processing_agent.execute_business_capability(
                "process_file",
                {"file_id": "test_file_123"},
                user_context
            )
            
            assert result.get("success") is True, "Capability should execute successfully"
            
            # Verify utility methods were called
            assert mock_log.called, "log_operation_with_telemetry should be called"
            assert mock_health.called, "record_health_metric should be called"
            
            print(f"\n✅ Agent executed capability successfully")
            print(f"✅ Result: {result.get('message')}")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_agent_handles_errors_with_audit(self, content_processing_agent, user_context):
        """Test that agent handles errors using AgentBase handle_error_with_audit method."""
        await content_processing_agent.initialize()
        
        # Make MCP server fail
        content_processing_agent.mcp_server.execute_tool = AsyncMock(side_effect=Exception("Test error"))
        
        # Mock error handler to verify it's called
        with pytest.mock.patch.object(content_processing_agent, 'handle_error_with_audit', new_callable=AsyncMock) as mock_error_handler:
            result = await content_processing_agent.execute_business_capability(
                "process_file",
                {"file_id": "test_file_123"},
                user_context
            )
            
            assert result.get("success") is False, "Should fail when MCP server fails"
            assert mock_error_handler.called, "handle_error_with_audit should be called on error"
            
            print("\n✅ Agent correctly handled error with audit logging")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_agent_security_validation(self, content_processing_agent, user_context):
        """Test that agent performs security validation."""
        await content_processing_agent.initialize()
        
        # Make security check fail
        content_processing_agent.security.check_permissions = AsyncMock(return_value=False)
        
        with pytest.raises(PermissionError, match="Access denied"):
            await content_processing_agent.execute_business_capability(
                "process_file",
                {"file_id": "test_file_123"},
                user_context
            )
        
        print("\n✅ Agent correctly performs security validation")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_agent_tenant_validation(self, content_processing_agent, user_context):
        """Test that agent performs tenant validation."""
        await content_processing_agent.initialize()
        
        # Make tenant validation fail
        mock_tenant_service = MagicMock()
        mock_tenant_service.validate_tenant_access = AsyncMock(return_value=False)
        content_processing_agent.public_works_foundation.get_tenant_service = MagicMock(return_value=mock_tenant_service)
        
        with pytest.raises(PermissionError, match="Tenant access denied"):
            await content_processing_agent.execute_business_capability(
                "process_file",
                {"file_id": "test_file_123"},
                user_context
            )
        
        print("\n✅ Agent correctly performs tenant validation")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_agent_get_supported_capabilities(self, content_processing_agent, user_context):
        """Test that agent returns supported capabilities."""
        await content_processing_agent.initialize()
        
        capabilities = await content_processing_agent.get_supported_capabilities(user_context)
        
        assert isinstance(capabilities, list), "Capabilities should be a list"
        assert len(capabilities) > 0, "Agent should have capabilities"
        assert "process_file" in capabilities, "Should include process_file capability"
        
        print(f"\n✅ Agent returned capabilities: {capabilities}")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_agent_analyze_situation(self, content_processing_agent, user_context):
        """Test that agent can analyze situations."""
        await content_processing_agent.initialize()
        
        # Mock MCP server for situation analysis
        content_processing_agent.mcp_server.execute_tool = AsyncMock(return_value={
            "success": True,
            "result": {
                "analysis": "Content is well-structured",
                "recommendations": ["Process with standard pipeline"]
            }
        })
        
        result = await content_processing_agent.analyze_situation({
            "type": "content_analysis",
            "content_id": "test_content_123"
        }, user_context)
        
        assert result.get("success") is True, "Situation analysis should succeed"
        assert "analysis" in result, "Result should include analysis"
        
        print(f"\n✅ Agent analyzed situation successfully")
        print(f"✅ Analysis: {result.get('analysis')}")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_agent_process_file_autonomous(self, content_processing_agent, user_context):
        """Test that agent can autonomously process files."""
        await content_processing_agent.initialize()
        
        # Mock MCP server responses for autonomous processing
        async def mock_execute_tool(tool_name, params, user_ctx):
            if tool_name == "analyze_content_situation":
                return {
                    "success": True,
                    "result": {
                        "findings": {
                            "processing_complexity": "low",
                            "file_size": "5MB",
                            "quality_score": 0.9
                        }
                    }
                }
            elif tool_name == "process_file":
                return {
                    "success": True,
                    "result": {"processed": True, "file_id": params.get("file_id")}
                }
            elif tool_name == "assess_quality":
                return {
                    "success": True,
                    "result": {"quality_score": 0.9, "assessment": "high_quality"}
                }
            else:
                return {"success": False, "error": "Unknown tool"}
        
        content_processing_agent.mcp_server.execute_tool = AsyncMock(side_effect=mock_execute_tool)
        
        result = await content_processing_agent.process_file_autonomous(
            "test_file_123",
            user_context
        )
        
        assert result.get("success") is True, "Autonomous processing should succeed"
        assert "autonomous_decisions" in result, "Result should include autonomous decisions"
        assert "processing_result" in result, "Result should include processing result"
        
        print(f"\n✅ Agent autonomously processed file")
        print(f"✅ Autonomous decisions: {result.get('autonomous_decisions')}")
        print(f"✅ Processing result: {result.get('processing_result', {}).get('message', 'N/A')}")


if __name__ == "__main__":
    # Allow running directly
    pytest.main([__file__, "-v", "-s"])

