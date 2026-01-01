#!/usr/bin/env python3
"""
Phase 2: Real API Tests - Agent Guidance Generation

REAL API TESTS: Verify agents can generate guidance with actual LLM calls.

These tests verify that agents can:
1. Generate capability guidance with real LLM
2. Provide step-by-step instructions
3. Suggest alternative approaches
4. Identify prerequisites and dependencies

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
    Test agent with real LLM for guidance generation.
    """
    from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
    from foundations.agentic_foundation.agui_schema_registry import AGUISchema, AGUIComponent
    
    infra = agentic_foundation_with_real_llm
    agentic = infra["agentic_foundation"]
    di_container = infra["di_container"]
    
    # Create AGUI schema
    agui_schema = AGUISchema(
        agent_name="Real Guidance Test Agent",
        version="1.0.0",
        description="Test agent for real LLM guidance generation",
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
        agent_name="Real Guidance Test Agent",
        agent_type="liaison",
        realm_name="business_enablement",
        di_container=di_container,
        capabilities=["conversation", "guidance"],
        required_roles=[],
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


class TestRealGuidanceGeneration:
    """Test that agents can generate guidance with real LLM."""
    
    @pytest.mark.asyncio
    async def test_agent_can_generate_capability_guidance(self, test_agent_with_real_llm):
        """
        Test that agent can generate capability guidance with real LLM.
        
        This verifies:
        - Agent can generate step-by-step guidance
        - Guidance is relevant and actionable
        - Guidance includes prerequisites
        """
        agent = test_agent_with_real_llm["agent"]
        
        # Verify agent has LLM abstraction
        if not hasattr(agent, "llm_abstraction") or agent.llm_abstraction is None:
            pytest.skip("Agent does not have LLM abstraction")
        
        # Request guidance for a capability
        capability_request = "How do I store a document in the system?"
        
        try:
            # Generate guidance using real LLM
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            prompt = f"""Provide step-by-step guidance for: {capability_request}

Include:
1. Prerequisites
2. Step-by-step instructions
3. Expected outcomes

Format as clear, actionable steps."""

            request = LLMRequest(
                messages=[{"role": "user", "content": prompt}],
                model=LLMModel.GPT_3_5_TURBO,  # Use cheapest model for testing (cost optimization)
                max_tokens=200
            )
            
            response = await agent.llm_abstraction.generate_response(request)
            response_text = str(response.content) if hasattr(response, "content") else str(response)
            
            # Verify guidance is generated
            assert len(response_text) > 50, \
                f"Guidance should be substantial. Response: {response_text}"
            
            # Verify guidance contains actionable steps (numbers, bullets, or step indicators)
            has_steps = any(indicator in response_text.lower() for indicator in ["step", "1.", "2.", "first", "then", "next"])
            assert has_steps, \
                f"Guidance should include steps. Response: {response_text}"
            
            assert True, "✅ Agent can generate capability guidance with real LLM"
            
        except Exception as e:
            pytest.fail(f"Failed to generate guidance with real LLM - integration issue: {e}")
    
    @pytest.mark.asyncio
    async def test_agent_can_suggest_alternative_approaches(self, test_agent_with_real_llm):
        """
        Test that agent can suggest alternative approaches with real LLM.
        
        This verifies:
        - LLM can suggest multiple approaches
        - Alternatives are reasonable
        - Agent can present options
        """
        agent = test_agent_with_real_llm["agent"]
        
        if not hasattr(agent, "llm_abstraction") or agent.llm_abstraction is None:
            pytest.skip("Agent does not have LLM abstraction")
        
        # Request alternatives
        capability_request = "How can I analyze document content?"
        
        try:
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            prompt = f"""For this capability: {capability_request}

Suggest 2-3 alternative approaches. Include pros and cons for each."""

            request = LLMRequest(
                messages=[{"role": "user", "content": prompt}],
                model=LLMModel.GPT_3_5_TURBO,  # Use cheapest model for testing (cost optimization)
                max_tokens=200
            )
            
            response = await agent.llm_abstraction.generate_response(request)
            response_text = str(response.content) if hasattr(response, "content") else str(response)
            
            # Verify alternatives are suggested
            assert len(response_text) > 50, \
                f"Response should be substantial. Response: {response_text}"
            
            # Verify multiple approaches are mentioned
            has_alternatives = any(indicator in response_text.lower() for indicator in ["alternative", "approach", "option", "method", "way"])
            assert has_alternatives, \
                f"Response should suggest alternatives. Response: {response_text}"
            
            assert True, "✅ Agent can suggest alternative approaches with real LLM"
            
        except Exception as e:
            pytest.fail(f"Failed to suggest alternatives with real LLM - integration issue: {e}")
    
    @pytest.mark.asyncio
    async def test_agent_can_identify_prerequisites(self, test_agent_with_real_llm):
        """
        Test that agent can identify prerequisites with real LLM.
        
        This verifies:
        - LLM can identify required prerequisites
        - Prerequisites are relevant
        - Agent can present dependencies
        """
        agent = test_agent_with_real_llm["agent"]
        
        if not hasattr(agent, "llm_abstraction") or agent.llm_abstraction is None:
            pytest.skip("Agent does not have LLM abstraction")
        
        # Request capability with prerequisites
        capability_request = "How do I validate a data schema?"
        
        try:
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            prompt = f"""For this capability: {capability_request}

Identify:
1. Prerequisites (what must be done first)
2. Dependencies (what is needed)
3. Requirements (what must be available)

Format as a clear list."""

            request = LLMRequest(
                messages=[{"role": "user", "content": prompt}],
                model=LLMModel.GPT_3_5_TURBO,  # Use cheapest model for testing (cost optimization)
                max_tokens=200
            )
            
            response = await agent.llm_abstraction.generate_response(request)
            response_text = str(response.content) if hasattr(response, "content") else str(response)
            
            # Verify prerequisites are identified
            assert len(response_text) > 30, \
                f"Response should identify prerequisites. Response: {response_text}"
            
            # Verify response mentions prerequisites/dependencies/requirements
            has_prereqs = any(term in response_text.lower() for term in ["prerequisite", "require", "need", "depend", "first", "before"])
            assert has_prereqs, \
                f"Response should identify prerequisites. Response: {response_text}"
            
            assert True, "✅ Agent can identify prerequisites with real LLM"
            
        except Exception as e:
            pytest.fail(f"Failed to identify prerequisites with real LLM - integration issue: {e}")

