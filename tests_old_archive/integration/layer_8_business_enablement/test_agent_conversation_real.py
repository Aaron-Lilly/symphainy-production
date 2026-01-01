#!/usr/bin/env python3
"""
Phase 2: Real API Tests - Agent Conversation Processing

REAL API TESTS: Verify agents can process conversations with actual LLM calls.

These tests verify that agents can:
1. Process conversation requests with real LLM
2. Handle real LLM responses
3. Maintain conversation context
4. Generate appropriate responses

REQUIREMENTS:
- OPENAI_API_KEY or ANTHROPIC_API_KEY must be set
- Tests use real API calls (costs apply)
- Use cheapest models for testing (gpt-3.5-turbo for cost optimization)
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
    
    Uses smart_city_infrastructure fixture and ensures LLM abstraction is real.
    """
    infra = smart_city_infrastructure
    di_container = infra["di_container"]
    pwf = infra["public_works_foundation"]
    curator = infra["curator"]
    
    # Ensure Public Works Foundation has real LLM abstraction
    # If not configured, try to initialize it
    if not hasattr(pwf, "llm_abstraction") or pwf.llm_abstraction is None:
        # Try to get or create real LLM abstraction
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
            # Add Anthropic support if needed
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
    Test agent with real LLM (not mocked).
    """
    from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
    from foundations.agentic_foundation.agui_schema_registry import AGUISchema, AGUIComponent
    
    infra = agentic_foundation_with_real_llm
    agentic = infra["agentic_foundation"]
    di_container = infra["di_container"]
    
    # Create AGUI schema
    agui_schema = AGUISchema(
        agent_name="Real LLM Test Agent",
        version="1.0.0",
        description="Test agent for real LLM conversation testing",
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
    
    # Create agent
    agent = await agentic.create_agent(
        agent_class=DimensionLiaisonAgent,
        agent_name="Real LLM Test Agent",
        agent_type="liaison",
        realm_name="business_enablement",
        di_container=di_container,
        capabilities=["conversation", "tool_usage"],
        required_roles=[],
        agui_schema=agui_schema,
        dimension="business_enablement"
    )
    
    assert agent is not None, "Agent must be created"
    assert agent.is_initialized, "Agent must be initialized"
    
    # Verify agent has real LLM (not mocked)
    if hasattr(agent, "llm_abstraction"):
        assert agent.llm_abstraction is not None, "Agent must have LLM abstraction for real API tests"
    
    return {
        "agent": agent,
        "agentic_foundation": agentic,
        "infrastructure": infra
    }


class TestRealConversationProcessing:
    """Test that agents can process conversations with real LLM."""
    
    @pytest.mark.asyncio
    async def test_agent_can_process_simple_conversation(self, test_agent_with_real_llm):
        """
        Test that agent can process a simple conversation with real LLM.
        
        This verifies:
        - Agent can send messages to real LLM
        - Agent receives real LLM responses
        - Response is properly formatted
        """
        # Verify API key is available (reload secrets to ensure it's available)
        _load_env_secrets()
        openai_key = os.getenv("LLM_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not openai_key:
            # Debug: Check what's actually in the environment
            print(f"\n⚠️  DEBUG: API key check failed")
            print(f"   LLM_OPENAI_API_KEY: {os.getenv('LLM_OPENAI_API_KEY')}")
            print(f"   OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
            pytest.skip("No LLM API keys configured (LLM_OPENAI_API_KEY/OPENAI_API_KEY)")
        
        agent = test_agent_with_real_llm["agent"]
        
        # Verify agent has LLM abstraction (required for real API tests)
        assert hasattr(agent, "llm_abstraction"), \
            "Agent must have LLM abstraction for real API tests"
        assert agent.llm_abstraction is not None, \
            "Agent LLM abstraction must be initialized"
        
        # Simple test message
        test_message = "Hello, can you introduce yourself?"
        
        try:
            # Use direct LLM call via agent's LLM abstraction (this is the real API call)
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            request = LLMRequest(
                messages=[{"role": "user", "content": test_message}],
                model=LLMModel.GPT_3_5_TURBO,  # Use cheapest model for testing (cost optimization)
                max_tokens=100
            )
            
            # Debug: Check adapter before calling
            if hasattr(agent.llm_abstraction, "primary_adapter"):
                adapter = agent.llm_abstraction.primary_adapter
                print(f"\n🔍 Adapter check:")
                print(f"   Adapter type: {type(adapter)}")
                print(f"   Adapter has _client: {hasattr(adapter, '_client')}")
                if hasattr(adapter, "_client"):
                    print(f"   _client is None: {adapter._client is None}")
                if hasattr(adapter, "api_key"):
                    api_key_set = adapter.api_key is not None and len(adapter.api_key) > 0
                    print(f"   API key set: {api_key_set}")
                    if api_key_set:
                        print(f"   API key starts with: {adapter.api_key[:10]}...")
            
            # Make the actual API call
            print(f"\n🚀 Making real API call to OpenAI (model: gpt-3.5-turbo)...")
            response = await agent.llm_abstraction.generate_response(request)
            
            # Debug: Check raw adapter response if available
            print(f"\n🔍 Response check:")
            print(f"   Response type: {type(response)}")
            print(f"   Has content attr: {hasattr(response, 'content')}")
            if hasattr(response, "content"):
                print(f"   Content value: {repr(response.content[:200]) if response.content else '(empty)'}")
                print(f"   Content type: {type(response.content)}")
                print(f"   Content length: {len(response.content) if response.content else 0}")
            if hasattr(response, "usage"):
                print(f"   Usage: {response.usage}")
            if hasattr(response, "finish_reason"):
                print(f"   Finish reason: {response.finish_reason}")
            
            # Verify response is not None
            assert response is not None, "Agent should return a response"
            
            # Debug: Print response details
            print(f"\n📊 Response details:")
            print(f"   Type: {type(response)}")
            if hasattr(response, "content"):
                print(f"   Content: {response.content[:100] if response.content else '(empty)'}")
                print(f"   Content length: {len(response.content) if response.content else 0}")
            if hasattr(response, "model"):
                print(f"   Model: {response.model}")
            if hasattr(response, "finish_reason"):
                print(f"   Finish reason: {response.finish_reason}")
            
            # Verify response has content
            if hasattr(response, "content"):
                # Check if content is empty (might indicate API issue)
                if not response.content or len(response.content) == 0:
                    # Check finish_reason for clues
                    if hasattr(response, "finish_reason") and response.finish_reason:
                        print(f"   ⚠️  Empty content but finish_reason: {response.finish_reason}")
                    # This might be a real API issue - let's check if it's a parsing problem
                    pytest.fail(f"LLM response has empty content. This might indicate an API issue or parsing problem. Response: {response}")
                assert len(response.content) > 0, f"Response should have content. Response object: {response}"
            elif isinstance(response, dict):
                assert "content" in response or "message" in response or "text" in response, \
                    "Response should contain content/message/text"
            else:
                response_str = str(response)
                assert len(response_str) > 0, "Response should be convertible to non-empty string"
            
            assert True, "✅ Agent can process conversation with real LLM"
            
        except Exception as e:
            pytest.fail(f"Failed to process conversation with real LLM - integration issue: {e}")
    
    @pytest.mark.asyncio
    async def test_agent_can_maintain_conversation_context(self, test_agent_with_real_llm):
        """
        Test that agent can maintain conversation context across multiple turns.
        
        This verifies:
        - Agent remembers previous messages
        - Context is preserved in multi-turn conversations
        """
        agent = test_agent_with_real_llm["agent"]
        
        # First message
        message1 = "My name is Alice. What's your name?"
        
        # Second message (should reference first)
        message2 = "What did I just tell you my name was?"
        
        try:
            # Process first message
            if hasattr(agent, "process_conversation"):
                response1 = await agent.process_conversation(message=message1, context={})
            elif hasattr(agent, "llm_abstraction") and agent.llm_abstraction:
                from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
                
                request1 = LLMRequest(
                    messages=[{"role": "user", "content": message1}],
                    model=LLMModel.GPT_4O_MINI,
                    max_tokens=100
                )
                response1 = await agent.llm_abstraction.generate_response(request1)
            else:
                pytest.skip("Agent does not have conversation processing capability")
            
            # Process second message with context
            if hasattr(agent, "process_conversation"):
                # Agent should maintain context internally
                response2 = await agent.process_conversation(message=message2, context={})
            elif hasattr(agent, "llm_abstraction") and agent.llm_abstraction:
                # Manually maintain context
                from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
                
                # Build conversation history
                messages = [
                    {"role": "user", "content": message1},
                    {"role": "assistant", "content": str(response1.content) if hasattr(response1, "content") else str(response1)},
                    {"role": "user", "content": message2}
                ]
                
                request2 = LLMRequest(
                    messages=messages,
                    model=LLMModel.GPT_3_5_TURBO,  # Use cheapest model for testing
                    max_tokens=100
                )
                response2 = await agent.llm_abstraction.generate_response(request2)
            else:
                pytest.skip("Agent does not have conversation processing capability")
            
            # Verify second response references the name
            response2_text = str(response2.content) if hasattr(response2, "content") else str(response2)
            
            # LLM should remember "Alice" from first message
            assert "alice" in response2_text.lower() or "Alice" in response2_text, \
                f"Agent should remember context. Response: {response2_text}"
            
            assert True, "✅ Agent can maintain conversation context with real LLM"
            
        except Exception as e:
            pytest.fail(f"Failed to maintain conversation context with real LLM - integration issue: {e}")
    
    @pytest.mark.asyncio
    async def test_agent_response_quality(self, test_agent_with_real_llm):
        """
        Test that agent generates reasonable responses with real LLM.
        
        This verifies:
        - Response quality is acceptable
        - Responses are coherent
        - Responses are relevant to the query
        """
        agent = test_agent_with_real_llm["agent"]
        
        # Test with a specific query
        test_message = "What is the capital of France?"
        
        try:
            # Process conversation
            if hasattr(agent, "process_conversation"):
                response = await agent.process_conversation(message=test_message, context={})
            elif hasattr(agent, "llm_abstraction") and agent.llm_abstraction:
                from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
                
                request = LLMRequest(
                    messages=[{"role": "user", "content": test_message}],
                    model=LLMModel.GPT_3_5_TURBO,  # Use cheapest model for testing
                    max_tokens=100
                )
                response = await agent.llm_abstraction.generate_response(request)
            else:
                pytest.skip("Agent does not have conversation processing capability")
            
            # Extract response text
            response_text = str(response.content) if hasattr(response, "content") else str(response)
            response_text_lower = response_text.lower()
            
            # Verify response mentions Paris (capital of France)
            assert "paris" in response_text_lower, \
                f"Response should mention Paris. Response: {response_text}"
            
            # Verify response is not empty
            assert len(response_text) > 10, \
                f"Response should be substantial. Response: {response_text}"
            
            assert True, "✅ Agent generates quality responses with real LLM"
            
        except Exception as e:
            pytest.fail(f"Failed to verify response quality with real LLM - integration issue: {e}")

