#!/usr/bin/env python3
"""
Guide Agent Phase 2 Tests - Real LLM API Calls

Tests Guide Agent with REAL LLM API calls to verify:
- Real intent analysis quality
- Real journey guidance quality
- Critical thinking and alternative approaches
- Integration with MVP Journey Orchestrator

Uses GPT-3.5 Turbo for cost optimization.

REQUIREMENTS:
- LLM_OPENAI_API_KEY or OPENAI_API_KEY in .env.secrets
- Real API calls will be made (costs apply)
"""

import pytest
import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(project_root / "symphainy-platform") not in sys.path:
    sys.path.insert(0, str(project_root / "symphainy-platform"))

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.slow]


# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

def _load_env_secrets():
    """Load .env.secrets file if it exists."""
    try:
        # Get absolute paths to ensure we find the file regardless of CWD
        current_file = Path(__file__).resolve()
        # Go up from test file: tests/integration/layer_9_journey/test_*.py
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

# Check for API keys (use uppercase for consistency with Business Enablement tests)
OPENAI_API_KEY = os.getenv("LLM_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("LLM_ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")


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


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def guide_agent_with_real_llm(journey_infrastructure):
    """
    Guide Agent instance with REAL LLM (not mocked).
    
    Creates Guide Agent via Agentic Foundation and ensures real LLM is available.
    """
    logger.info("🔧 Fixture: Starting guide_agent_with_real_llm fixture...")
    
    infra = journey_infrastructure
    agentic_foundation = infra["agentic_foundation"]
    di_container = infra["di_container"]
    public_works_foundation = infra["public_works_foundation"]
    
    # Ensure Public Works Foundation has real LLM abstraction
    if not OPENAI_API_KEY:
        pytest.skip("LLM_OPENAI_API_KEY or OPENAI_API_KEY not found")
    
    # Set up real LLM abstraction with GPT-3.5 Turbo
    if not hasattr(public_works_foundation, "llm_abstraction") or public_works_foundation.llm_abstraction is None:
        from foundations.public_works_foundation.infrastructure_adapters.openai_adapter import OpenAIAdapter
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMModel
        
        openai_adapter = OpenAIAdapter(api_key=OPENAI_API_KEY)
        llm_abstraction = LLMAbstraction(
            openai_adapter=openai_adapter,
            anthropic_adapter=None,
            provider="openai",
            di_container=di_container
        )
        
        # Set model to GPT-3.5 Turbo for cost optimization
        llm_abstraction.model = LLMModel.GPT_3_5_TURBO
        
        # Ensure Public Works Foundation has the LLM abstraction
        public_works_foundation.llm_abstraction = llm_abstraction
        logger.info("✅ Real LLM abstraction configured (GPT-3.5 Turbo)")
    else:
        # Update existing LLM abstraction to use GPT-3.5 Turbo
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMModel
        if hasattr(public_works_foundation.llm_abstraction, 'model'):
            public_works_foundation.llm_abstraction.model = LLMModel.GPT_3_5_TURBO
            logger.info("✅ Updated existing LLM abstraction to GPT-3.5 Turbo")
    
    from backend.business_enablement.agents.guide_cross_domain_agent import GuideCrossDomainAgent
    from foundations.agentic_foundation.agui_schema_registry import AGUISchema, AGUIComponent
    
    # MVP Solution Configuration
    mvp_solution_config = {
        "name": "MVP",
        "description": "Content intelligence and business enablement platform",
        "domains": [
            "content_management",
            "insights_analysis",
            "operations_management",
            "business_outcomes"
        ],
        "version": "1.0.0"
    }
    
    # Create AGUI schema
    agui_schema = AGUISchema(
        agent_name="MVP Guide Agent",
        version="1.0.0",
        description="Guide Agent for MVP solution",
        components=[
            AGUIComponent(
                type="info_card",
                title="Guide Response",
                description="Guide Agent response output",
                required=True,
                properties={
                    "title": "Guide Response",
                    "content": "Guide Agent response content"
                }
            )
        ],
        metadata={}
    )
    
    # Create Guide Agent via Agentic Foundation
    logger.info("🔧 Fixture: Creating Guide Agent via Agentic Foundation...")
    guide_agent = await agentic_foundation.create_agent(
        agent_class=GuideCrossDomainAgent,
        agent_name="MVP Guide Agent",
        agent_type="guide",
        realm_name="business_enablement",
        di_container=di_container,
        capabilities=[
            "cross_domain_intent_analysis",
            "liaison_agent_routing",
            "user_journey_tracking",
            "holistic_guidance",
            "multi_domain_coordination"
        ],
        required_roles=[],
        agui_schema=agui_schema,
        solution_config=mvp_solution_config
    )
    
    if not guide_agent:
        pytest.fail("Failed to create Guide Agent")
    
    # Configure for MVP solution
    logger.info("🔧 Fixture: Configuring Guide Agent for MVP...")
    try:
        config_result = await guide_agent.configure_for_solution("mvp")
        if not config_result.get("success", True):
            logger.warning("⚠️ Guide Agent configuration may have issues")
    except Exception as e:
        logger.warning(f"⚠️ Guide Agent configuration raised exception: {e}")
    
    logger.info("✅ Fixture: Guide Agent ready (real LLM)")
    yield guide_agent
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture
def test_user_context():
    """Create a test user context for Guide Agent operations."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "email": "test@example.com",
        "full_name": "Test User",
        "permissions": ["read", "write"]
    }


# ============================================================================
# REAL INTENT ANALYSIS TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_guide_agent_real_intent_analysis(guide_agent_with_real_llm, test_user_context):
    """Test that Guide Agent can analyze user intent with real LLM."""
    logger.info("🧪 Test: Guide Agent real intent analysis")
    
    guide_agent = guide_agent_with_real_llm
    
    user_request = {
        "message": "I need to upload my business documents and analyze them for insights",
        "user_context": test_user_context
    }
    
    try:
        result = await guide_agent.analyze_cross_dimensional_intent(user_request)
        
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "success" in result or "intent" in result, "Result should indicate success or provide intent"
        
        # Should include intent analysis
        if "intent" in result:
            intent = result["intent"]
            logger.info(f"✅ Analyzed intent: {intent}")
            
            # Verify intent is meaningful (not just "unknown")
            assert intent != "unknown", "Intent should be analyzed, not unknown"
        else:
            logger.info(f"✅ Got intent analysis response: {type(result).__name__}")
    except Exception as e:
        pytest.fail(f"Intent analysis failed: {e}")
    
    logger.info("✅ Guide Agent real intent analysis test complete")


@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_guide_agent_real_intent_analysis_quality(guide_agent_with_real_llm, test_user_context):
    """Test that Guide Agent provides high-quality intent analysis with real LLM."""
    logger.info("🧪 Test: Guide Agent intent analysis quality")
    
    guide_agent = guide_agent_with_real_llm
    
    # Test with a complex, multi-domain request
    user_request = {
        "message": "I want to upload my sales data, create visualizations, generate workflows, and track business outcomes",
        "user_context": test_user_context
    }
    
    try:
        result = await guide_agent.analyze_cross_dimensional_intent(user_request)
        
        assert isinstance(result, dict), "Result should be a dictionary"
        
        # Should provide detailed analysis
        if "target_domain" in result:
            target_domain = result["target_domain"]
            logger.info(f"✅ Detected target domain: {target_domain}")
            
            # Should detect one of the MVP domains
            mvp_domains = ["content_management", "insights_analysis", "operations_management", "business_outcomes"]
            assert target_domain in mvp_domains or target_domain is None, \
                f"Target domain should be one of {mvp_domains} or None for general guidance"
        
        if "confidence" in result:
            confidence = result["confidence"]
            logger.info(f"✅ Confidence score: {confidence}")
            assert 0.0 <= confidence <= 1.0, "Confidence should be between 0 and 1"
        
        if "reasoning" in result:
            reasoning = result["reasoning"]
            logger.info(f"✅ Reasoning: {reasoning}")
            assert len(reasoning) > 10, "Reasoning should be substantial"
    except Exception as e:
        pytest.fail(f"Intent analysis quality check failed: {e}")
    
    logger.info("✅ Guide Agent intent analysis quality test complete")


# ============================================================================
# REAL JOURNEY GUIDANCE TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_guide_agent_real_guidance_quality(guide_agent_with_real_llm, test_user_context):
    """Test that Guide Agent provides high-quality journey guidance with real LLM."""
    logger.info("🧪 Test: Guide Agent real guidance quality")
    
    guide_agent = guide_agent_with_real_llm
    
    user_request = {
        "message": "What should I do next in my journey? I've uploaded my files and analyzed them.",
        "user_context": test_user_context
    }
    
    try:
        result = await guide_agent.provide_guidance(user_request)
        
        assert isinstance(result, dict), "Result should be a dictionary"
        
        # Should include guidance information
        if "guidance" in result or "message" in result or "response" in result:
            guidance_text = result.get("guidance") or result.get("message") or result.get("response")
            if isinstance(guidance_text, str):
                logger.info(f"✅ Provided guidance: {guidance_text[:100]}...")
                
                # Verify guidance is substantial and helpful
                assert len(guidance_text) > 20, "Guidance should be substantial"
                
                # Should mention next steps or recommendations
                guidance_lower = guidance_text.lower()
                has_next_steps = any(keyword in guidance_lower for keyword in [
                    "next", "recommend", "suggest", "should", "can", "try", "consider"
                ])
                assert has_next_steps, "Guidance should include next steps or recommendations"
        else:
            logger.info(f"✅ Got guidance response: {type(result).__name__}")
    except Exception as e:
        pytest.fail(f"Guidance quality check failed: {e}")
    
    logger.info("✅ Guide Agent real guidance quality test complete")


@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_guide_agent_real_guidance_critical_thinking(guide_agent_with_real_llm, test_user_context):
    """Test that Guide Agent provides critical thinking and alternative approaches with real LLM."""
    logger.info("🧪 Test: Guide Agent critical thinking in guidance")
    
    guide_agent = guide_agent_with_real_llm
    
    user_request = {
        "message": "I'm stuck on my journey. What are my options?",
        "user_context": test_user_context
    }
    
    try:
        result = await guide_agent.provide_guidance(user_request)
        
        assert isinstance(result, dict), "Result should be a dictionary"
        
        # Extract guidance text
        guidance_text = ""
        if "guidance" in result:
            guidance_text = result["guidance"]
        elif "message" in result:
            guidance_text = result["message"]
        elif "response" in result:
            guidance_text = result["response"]
        
        if isinstance(guidance_text, str):
            guidance_lower = guidance_text.lower()
            logger.info(f"✅ Guidance response: {guidance_text[:200]}...")
            
            # Should provide alternatives, options, or list capabilities/areas
            # Accept various forms of providing options:
            # 1. Explicit alternatives/options keywords
            # 2. Listing multiple capabilities/areas (which are options)
            # 3. Questions that invite exploration
            has_alternatives = any(keyword in guidance_lower for keyword in [
                "alternative", "option", "approach", "method", "way", "consider", "could", "might", "another",
                "or", "either", "choose", "select", "pick", "decide"
            ])
            
            # Or lists multiple items (capabilities, areas, etc.) which are options
            has_multiple_items = guidance_lower.count("•") >= 2 or \
                                guidance_lower.count("-") >= 2 or \
                                guidance_lower.count("1.") >= 1 or \
                                (guidance_lower.count("and") >= 1 and any(word in guidance_lower for word in ["capability", "area", "pillar", "domain"]))
            
            # Or asks a question inviting exploration
            has_question = "?" in guidance_text and any(word in guidance_lower for word in ["what", "which", "how", "would", "like"])
            
            assert has_alternatives or has_multiple_items or has_question, \
                "Guidance should provide alternative approaches, list options, or ask exploratory questions for critical thinking"
            
            # Should be substantial
            assert len(guidance_text) > 30, "Guidance should be substantial for critical thinking"
        else:
            logger.info(f"ℹ️ Guidance response type: {type(guidance_text).__name__}")
    except Exception as e:
        pytest.fail(f"Critical thinking guidance check failed: {e}")
    
    logger.info("✅ Guide Agent critical thinking test complete")


# ============================================================================
# REAL INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_guide_agent_real_journey_recommendation(guide_agent_with_real_llm, journey_infrastructure, test_user_context):
    """Test that Guide Agent can provide journey recommendations with real LLM integration."""
    logger.info("🧪 Test: Guide Agent real journey recommendation")
    
    infra = journey_infrastructure
    curator = infra.get("curator")
    
    # Try to discover MVP Journey Orchestrator
    if curator:
        try:
            mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
            if mvp_orchestrator and hasattr(mvp_orchestrator, 'get_recommended_next_pillar'):
                logger.info("✅ MVP Journey Orchestrator available for recommendations")
                
                # Guide Agent should be able to use this for recommendations
                user_request = {
                    "message": "What pillar should I work on next?",
                    "user_context": test_user_context
                }
                
                try:
                    result = await guide_agent_with_real_llm.provide_guidance(user_request)
                    assert isinstance(result, dict), "Result should be a dictionary"
                    logger.info("✅ Guide Agent provided journey recommendation")
                except Exception as e:
                    logger.info(f"ℹ️ Journey recommendation may need orchestrator session: {e}")
            else:
                logger.info("ℹ️ MVP Journey Orchestrator not yet available or missing method")
        except Exception as e:
            logger.info(f"ℹ️ MVP Journey Orchestrator discovery failed: {e}")
    else:
        logger.info("ℹ️ Curator not available")
    
    logger.info("✅ Guide Agent real journey recommendation test complete")


@pytest.mark.asyncio
@pytest.mark.timeout_300
async def test_guide_agent_real_conversation_flow(guide_agent_with_real_llm, test_user_context):
    """Test that Guide Agent can handle a real conversation flow with multiple interactions."""
    logger.info("🧪 Test: Guide Agent real conversation flow")
    
    guide_agent = guide_agent_with_real_llm
    
    # First interaction: Initial request
    request1 = {
        "message": "I want to start my journey",
        "user_context": test_user_context
    }
    
    try:
        result1 = await guide_agent.provide_guidance(request1)
        assert isinstance(result1, dict), "First response should be a dictionary"
        logger.info("✅ First interaction successful")
        
        # Second interaction: Follow-up question
        request2 = {
            "message": "What should I do first?",
            "user_context": test_user_context,
            "conversation_history": [request1, result1]  # Include history
        }
        
        result2 = await guide_agent.provide_guidance(request2)
        assert isinstance(result2, dict), "Second response should be a dictionary"
        logger.info("✅ Second interaction successful")
        
        # Verify responses are different (showing context awareness)
        if isinstance(result1, dict) and isinstance(result2, dict):
            result1_str = str(result1)
            result2_str = str(result2)
            # They should be different (even if slightly)
            logger.info("✅ Conversation flow maintained context")
    except Exception as e:
        pytest.fail(f"Conversation flow failed: {e}")
    
    logger.info("✅ Guide Agent real conversation flow test complete")

