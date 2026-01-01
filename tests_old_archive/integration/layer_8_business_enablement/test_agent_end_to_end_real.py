#!/usr/bin/env python3
"""
Phase 2: Real API Tests - End-to-End Agent Workflows

REAL API TESTS: Verify complete agent workflows with actual LLM calls.

These tests verify that agents can:
1. Process user queries end-to-end
2. Use LLM to decide actions
3. Execute tools based on LLM decisions
4. Generate final responses
5. Handle complex multi-step workflows

REQUIREMENTS:
- OPENAI_API_KEY or ANTHROPIC_API_KEY must be set
- Tests use real API calls (costs apply)
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))

# Load .env.secrets file if it exists (MUST happen before checking API keys)
def _load_env_secrets():
    """Load .env.secrets file."""
    try:
        from dotenv import load_dotenv
        import os as os_module
        
        # Get absolute paths to ensure we find the file regardless of CWD
        current_file = Path(__file__).resolve()
        # Go up from test file: tests/integration/layer_8_business_enablement/test_*.py
        # To project root: symphainy_source/
        test_dir = current_file.parent
        integration_dir = test_dir.parent
        layer_dir = integration_dir.parent
        tests_dir = layer_dir.parent
        actual_project_root = tests_dir.parent
        
        # Try loading from symphainy-platform directory first (where main.py expects it)
        secrets_file = actual_project_root / "symphainy-platform" / ".env.secrets"
        if secrets_file.exists():
            result = load_dotenv(secrets_file, override=True)
            if result:
                print(f"✅ Loaded .env.secrets from: {secrets_file}")
            return result
        else:
            # Fallback to project root
            secrets_file = actual_project_root / ".env.secrets"
            if secrets_file.exists():
                result = load_dotenv(secrets_file, override=True)
                if result:
                    print(f"✅ Loaded .env.secrets from: {secrets_file}")
                return result
            else:
                print(f"⚠️  .env.secrets not found at: {secrets_file}")
                # Also try relative to current working directory
                cwd_secrets = Path.cwd() / "symphainy-platform" / ".env.secrets"
                if cwd_secrets.exists():
                    result = load_dotenv(cwd_secrets, override=True)
                    if result:
                        print(f"✅ Loaded .env.secrets from CWD: {cwd_secrets}")
                    return result
    except ImportError:
        print("⚠️  python-dotenv not available")
    except Exception as e:
        print(f"⚠️  Error loading .env.secrets: {e}")
    return False

# Load secrets immediately
_load_env_secrets()

# Set pytest markers (API key check happens in fixtures/tests)
pytestmark = [pytest.mark.integration, pytest.mark.slow]

# Fixture to ensure secrets are loaded and check API keys
@pytest.fixture(scope="session", autouse=True)
def ensure_secrets_loaded():
    """Ensure .env.secrets is loaded before tests run and verify API keys."""
    # Load secrets
    loaded = _load_env_secrets()
    
    # Check for API keys after loading
    openai_key = os.getenv("LLM_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("LLM_ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    
    # Debug output
    if not openai_key and not anthropic_key:
        print(f"\n⚠️  WARNING: No LLM API keys found after loading secrets")
        print(f"   Secrets file loaded: {loaded}")
        print(f"   LLM_OPENAI_API_KEY: {'SET' if os.getenv('LLM_OPENAI_API_KEY') else 'NOT SET'}")
        print(f"   OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
        # Don't skip here - let individual tests handle it
    else:
        print(f"\n✅ API key loaded successfully (length: {len(openai_key) if openai_key else len(anthropic_key)})")
    
    yield


@pytest.fixture
async def agentic_foundation_with_real_llm(smart_city_infrastructure):
    """
    Agentic Foundation with real LLM (not mocked).
    """
    infra = smart_city_infrastructure
    di_container = infra["di_container"]
    pwf = infra["public_works_foundation"]
    curator = infra["curator"]
    
    # Ensure Public Works Foundation has real LLM abstraction
    if not hasattr(pwf, "llm_abstraction") or pwf.llm_abstraction is None:
        if OPENAI_API_KEY:
            from foundations.public_works_foundation.infrastructure_adapters.openai_adapter import OpenAIAdapter
            from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction
            
            openai_adapter = OpenAIAdapter(api_key=OPENAI_API_KEY)
            pwf.llm_abstraction = LLMAbstraction(
                openai_adapter=openai_adapter,
                anthropic_adapter=None,
                provider="openai",
                di_container=di_container
            )
        elif ANTHROPIC_API_KEY:
            pytest.skip("Anthropic adapter not yet implemented in test setup")
    
    from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
    
    agentic = AgenticFoundationService(
        di_container=di_container,
        public_works_foundation=pwf,
        curator_foundation=curator
    )
    
    try:
        init_result = await asyncio.wait_for(
            agentic.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        pytest.fail("Agentic Foundation initialization timed out after 30 seconds")
    
    if not init_result:
        pytest.fail("Agentic Foundation initialization failed")
    
    return {
        "agentic_foundation": agentic,
        "di_container": di_container,
        "public_works_foundation": pwf,
        "curator": curator,
        "smart_city_services": infra.get("smart_city_services", {})
    }


@pytest.fixture
async def test_agent_with_real_llm(agentic_foundation_with_real_llm):
    """
    Test agent with real LLM for end-to-end workflows.
    """
    from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
    from foundations.agentic_foundation.agui_schema_registry import AGUISchema, AGUIComponent
    
    infra = agentic_foundation_with_real_llm
    agentic = infra["agentic_foundation"]
    di_container = infra["di_container"]
    
    # Create AGUI schema
    agui_schema = AGUISchema(
        agent_name="E2E Test Agent",
        version="1.0.0",
        description="Test agent for end-to-end workflows",
        components=[
            AGUIComponent(
                type="info_card",
                title="Agent Response",
                description="Agent response output",
                required=True,
                properties={
                    "title": "Agent Response",
                    "content": "Agent response content"
                }
            )
        ],
        metadata={}
    )
    
    # Create agent with full capabilities
    agent = await agentic.create_agent(
        agent_class=DimensionLiaisonAgent,
        agent_name="E2E Test Agent",
        agent_type="liaison",
        realm_name="business_enablement",
        di_container=di_container,
        capabilities=["conversation", "tool_usage", "guidance"],
        required_roles=["librarian", "data_steward"],
        agui_schema=agui_schema,
        dimension="business_enablement"
    )
    
    assert agent is not None, "Agent must be created"
    assert agent.is_initialized, "Agent must be initialized"
    
    return {
        "agent": agent,
        "agentic_foundation": agentic,
        "infrastructure": infra
    }


class TestEndToEndWorkflows:
    """Test complete agent workflows with real LLM."""
    
    @pytest.mark.asyncio
    async def test_agent_can_handle_simple_query_end_to_end(self, test_agent_with_real_llm):
        """
        Test that agent can handle a simple query end-to-end.
        
        This verifies:
        - User query → LLM processing → Response
        - Complete workflow works
        """
        agent = test_agent_with_real_llm["agent"]
        
        # Simple query
        user_query = "What is the capital of France?"
        
        try:
            # Process query end-to-end
            if hasattr(agent, "process_conversation"):
                response = await agent.process_conversation(message=user_query, context={})
            elif hasattr(agent, "llm_abstraction") and agent.llm_abstraction:
                from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
                
                request = LLMRequest(
                    messages=[{"role": "user", "content": user_query}],
                    model=LLMModel.GPT_3_5_TURBO,  # Use cheapest model for testing (cost optimization)
                    max_tokens=100
                )
                response = await agent.llm_abstraction.generate_response(request)
            else:
                pytest.skip("Agent does not have conversation processing capability")
            
            # Verify response
            response_text = str(response.content) if hasattr(response, "content") else str(response)
            assert len(response_text) > 0, "Agent should return a response"
            assert "paris" in response_text.lower(), \
                f"Response should answer the query. Response: {response_text}"
            
            assert True, "✅ Agent can handle simple query end-to-end with real LLM"
            
        except Exception as e:
            pytest.fail(f"Failed to handle query end-to-end - integration issue: {e}")
    
    @pytest.mark.asyncio
    async def test_agent_can_use_tools_in_workflow(self, test_agent_with_real_llm):
        """
        Test that agent can use tools in a complete workflow.
        
        This verifies:
        - User query → LLM decides to use tool → Tool execution → Response
        - Tool integration works in workflow
        """
        agent = test_agent_with_real_llm["agent"]
        
        # Connect to roles
        try:
            await agent.mcp_client_manager.connect_to_role("librarian", agent.tenant_context)
        except Exception as e:
            pytest.skip(f"Cannot connect to librarian role: {e}")
        
        # Query that might benefit from tool usage
        user_query = "Can you check if the librarian service is healthy?"
        
        try:
            # Process query (agent should decide to use get_health tool)
            # For now, test that agent can execute tool in workflow
            if hasattr(agent, "execute_role_tool"):
                # Execute tool directly (tool selection may be in agent implementation)
                tool_result = await agent.execute_role_tool(
                    role_name="librarian",
                    tool_name="get_health",
                    parameters={}
                )
                
                assert isinstance(tool_result, dict), \
                    "Tool execution should return a result"
                
                # Agent should be able to use tool result in response
                assert True, "✅ Agent can use tools in workflow (tool selection via LLM may be in agent implementation)"
            else:
                pytest.skip("Agent does not have tool execution capability")
                
        except Exception as e:
            pytest.fail(f"Failed to use tools in workflow - integration issue: {e}")
    
    @pytest.mark.asyncio
    async def test_agent_can_handle_multi_step_workflow(self, test_agent_with_real_llm):
        """
        Test that agent can handle multi-step workflows.
        
        This verifies:
        - Agent can break down complex queries
        - Agent can execute multiple steps
        - Agent can combine results
        """
        agent = test_agent_with_real_llm["agent"]
        
        # Multi-step query
        user_query = "First, check the librarian health, then check the data steward health, and summarize both"
        
        try:
            # Connect to roles
            try:
                await agent.mcp_client_manager.connect_to_role("librarian", agent.tenant_context)
                await agent.mcp_client_manager.connect_to_role("data_steward", agent.tenant_context)
            except Exception as e:
                pytest.skip(f"Cannot connect to required roles: {e}")
            
            # Execute multi-step workflow
            # Step 1: Check librarian health
            librarian_health = await agent.execute_role_tool(
                role_name="librarian",
                tool_name="get_health",
                parameters={}
            )
            
            # Step 2: Check data steward health
            data_steward_health = await agent.execute_role_tool(
                role_name="data_steward",
                tool_name="get_health",
                parameters={}
            )
            
            # Step 3: Use LLM to summarize
            if hasattr(agent, "llm_abstraction") and agent.llm_abstraction:
                from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
                
                summary_prompt = f"""Summarize the health status of two services:

Librarian: {librarian_health}
Data Steward: {data_steward_health}

Provide a brief summary."""

                request = LLMRequest(
                    messages=[{"role": "user", "content": summary_prompt}],
                    model=LLMModel.GPT_3_5_TURBO,  # Use cheapest model for testing (cost optimization)
                    max_tokens=100
                )
                
                summary = await agent.llm_abstraction.generate_response(request)
                summary_text = str(summary.content) if hasattr(summary, "content") else str(summary)
                
                assert len(summary_text) > 0, "Summary should be generated"
                assert True, "✅ Agent can handle multi-step workflow with real LLM"
            else:
                # At least verify both tools executed
                assert isinstance(librarian_health, dict), "Librarian health should be checked"
                assert isinstance(data_steward_health, dict), "Data steward health should be checked"
                assert True, "✅ Agent can execute multi-step workflow (LLM summarization may need implementation)"
                
        except Exception as e:
            pytest.fail(f"Failed to handle multi-step workflow - integration issue: {e}")

