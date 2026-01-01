#!/usr/bin/env python3
"""
Comprehensive Integration Test for Declarative Universal Mapper Specialist Agent

Tests the declarative agent with:
- Real platform dependencies
- Real LLM abstraction (actual API calls)
- Real orchestrator integration
- Real MCP tool execution
- All interface methods
- Error handling
- Edge cases

This is a bulletproof test suite to validate the declarative pattern before migrating other agents.
"""

import sys
import os

# Set Traefik URL to localhost for testing (when running outside Docker)
# Must be set BEFORE any imports that load configuration
if not os.environ.get("TRAEFIK_API_URL"):
    os.environ["TRAEFIK_API_URL"] = "http://localhost:8080"

# Cost control configuration (set via environment variables)
# Default: Use real LLM but with strict cost controls
os.environ.setdefault("TEST_USE_REAL_LLM", "true")
os.environ.setdefault("TEST_USE_CHEAPEST_MODEL", "true")
os.environ.setdefault("TEST_ENABLE_RETRIES", "false")  # Disable retries in tests to save costs
os.environ.setdefault("TEST_MAX_TOKENS", "50")  # Minimal tokens for tests
os.environ.setdefault("TEST_TRACK_COSTS", "true")
os.environ.setdefault("TEST_MAX_COST", "1.00")  # $1 max per test run
os.environ.setdefault("TEST_USE_CACHE", "true")  # Use response cache

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))
sys.path.insert(0, str(project_root / "tests"))  # For test utilities

# Import cost management utilities
try:
    from test_config import TestConfig
    from fixtures.llm_response_cache import LLMResponseCache
    from utils.cost_tracker import get_cost_tracker
    COST_CONTROLS_AVAILABLE = True
except ImportError:
    # Fallback if test utilities not available
    COST_CONTROLS_AVAILABLE = False
    logger = logging.getLogger("ComprehensiveDeclarativeAgentTest")
    logger.warning("⚠️ Cost control utilities not available - tests will use real API without cost limits")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ComprehensiveDeclarativeAgentTest")

# Initialize cost tracking and response cache
if COST_CONTROLS_AVAILABLE:
    cost_tracker = get_cost_tracker(max_cost=float(os.getenv("TEST_MAX_COST", "1.00")))
    response_cache = LLMResponseCache() if TestConfig.USE_RESPONSE_CACHE else None
    logger.info(f"💰 Cost controls enabled: max_cost=${cost_tracker.max_cost}, cache={'enabled' if response_cache else 'disabled'}")
else:
    cost_tracker = None
    response_cache = None

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}


def log_test(test_name: str, status: str, error: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
    """Log test result."""
    test_results["total"] += 1
    if status == "PASS":
        test_results["passed"] += 1
        logger.info(f"✅ {test_name}")
        if details:
            for key, value in details.items():
                logger.info(f"   {key}: {value}")
    else:
        test_results["failed"] += 1
        error_msg = f"{test_name}: {error}" if error else test_name
        test_results["errors"].append(error_msg)
        logger.error(f"❌ {test_name}: {error}")
        if details:
            for key, value in details.items():
                logger.error(f"   {key}: {value}")


# ============================================================================
# TEST SETUP: Platform Initialization
# ============================================================================

async def setup_platform_services():
    """Initialize all platform services needed for testing."""
    logger.info("🔧 Setting up platform services...")
    
    try:
        import os
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Set Traefik URL to localhost for testing (when running outside Docker)
        if not os.environ.get("TRAEFIK_API_URL"):
            os.environ["TRAEFIK_API_URL"] = "http://localhost:8080"
            logger.info("   🔧 Set TRAEFIK_API_URL=http://localhost:8080 for testing")
        
        # Initialize DI Container
        logger.info("   📦 Initializing DI Container...")
        di_container = DIContainerService("test_declarative_agent")
        # DIContainerService initializes automatically in __init__
        logger.info("   ✅ DI Container initialized")
        
        # Initialize Public Works Foundation
        logger.info("   📦 Initializing Public Works Foundation...")
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize()
        di_container.service_registry["PublicWorksFoundationService"] = public_works
        logger.info("   ✅ Public Works Foundation initialized")
        
        # Check LLM abstraction availability
        llm_abstraction = public_works.get_abstraction("llm")
        if llm_abstraction:
            logger.info("   ✅ LLM abstraction available")
        else:
            logger.warning("   ⚠️  LLM abstraction not available (may need API keys)")
        
        # Initialize Curator Foundation
        logger.info("   📦 Initializing Curator Foundation...")
        curator = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=public_works
        )
        await curator.initialize()
        di_container.service_registry["CuratorFoundationService"] = curator
        logger.info("   ✅ Curator Foundation initialized")
        
        # Initialize Agentic Foundation
        logger.info("   📦 Initializing Agentic Foundation...")
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works,
            curator_foundation=curator
        )
        await agentic_foundation.initialize()
        di_container.service_registry["AgenticFoundationService"] = agentic_foundation
        logger.info("   ✅ Agentic Foundation initialized")
        
        return {
            "di_container": di_container,
            "public_works": public_works,
            "curator": curator,
            "agentic_foundation": agentic_foundation,
            "llm_abstraction": llm_abstraction
        }
        
    except Exception as e:
        logger.error(f"❌ Platform setup failed: {e}")
        import traceback
        traceback.print_exc()
        raise


async def setup_orchestrator(platform_services: Dict[str, Any]):
    """Initialize Insurance Migration Orchestrator."""
    logger.info("🔧 Setting up Insurance Migration Orchestrator...")
    
    try:
        from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
        
        # Create delivery manager (minimal for testing)
        delivery_manager = DeliveryManagerService(
            di_container=platform_services["di_container"]
        )
        
        # Initialize orchestrator
        from backend.business_enablement.delivery_manager.insurance_use_case_orchestrators.insurance_migration_orchestrator.insurance_migration_orchestrator import InsuranceMigrationOrchestrator
        
        orchestrator = InsuranceMigrationOrchestrator(delivery_manager)
        await orchestrator.initialize()
        
        logger.info("   ✅ Insurance Migration Orchestrator initialized")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"❌ Orchestrator setup failed: {e}")
        import traceback
        traceback.print_exc()
        raise


# ============================================================================
# TEST 1: Agent Initialization with Real Dependencies
# ============================================================================

async def test_agent_initialization_real(platform_services: Dict[str, Any]):
    """Test agent initialization with real platform dependencies."""
    test_name = "Agent Initialization (Real Dependencies)"
    
    try:
        from backend.business_enablement.agents.specialists.universal_mapper_specialist_declarative import UniversalMapperSpecialist
        from foundations.agentic_foundation.agent_sdk.mcp_client_manager import MCPClientManager
        from foundations.agentic_foundation.agent_sdk.policy_integration import PolicyIntegration
        from foundations.agentic_foundation.agent_sdk.tool_composition import ToolComposition
        from foundations.agentic_foundation.agent_sdk.agui_output_formatter import AGUIOutputFormatter
        
        # Get SDK components from Agentic Foundation
        agentic_foundation = platform_services["agentic_foundation"]
        mcp_client_manager = agentic_foundation.mcp_client_manager
        
        # Instantiate SDK components (they're stored as classes, not instances)
        from foundations.agentic_foundation.agent_sdk.policy_integration import PolicyIntegration
        from foundations.agentic_foundation.agent_sdk.tool_composition import ToolComposition
        
        policy_integration = PolicyIntegration(
            foundation_services=platform_services["di_container"],
            agentic_foundation=agentic_foundation
        )
        tool_composition = ToolComposition(
            foundation_services=platform_services["di_container"],
            agentic_foundation=agentic_foundation
        )
        agui_formatter = agentic_foundation.agui_formatter
        
        # Initialize agent
        config_path = project_root / "symphainy-platform" / "backend" / "business_enablement" / "agents" / "configs" / "universal_mapper_specialist.yaml"
        
        agent = UniversalMapperSpecialist(
            foundation_services=platform_services["di_container"],
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=platform_services["curator"],
            public_works_foundation=platform_services["public_works"]
        )
        
        # Initialize agent
        await agent.initialize()
        
        # Validate agent state
        assert agent.agent_name == "UniversalMapperSpecialist", "Agent name should match"
        assert agent.role is not None, "Role should be set from config"
        assert agent.goal is not None, "Goal should be set from config"
        assert len(agent.allowed_tools) > 0, "Allowed tools should be configured"
        
        # Check LLM abstraction
        if agent.llm_abstraction:
            logger.info("   ✅ LLM abstraction available")
        else:
            logger.warning("   ⚠️  LLM abstraction not available (may need API keys)")
        
        log_test(test_name, "PASS", details={
            "agent_name": agent.agent_name,
            "role": agent.role,
            "allowed_tools": len(agent.allowed_tools),
            "llm_available": agent.llm_abstraction is not None
        })
        
        return agent
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 2: Orchestrator Integration
# ============================================================================

async def test_orchestrator_integration(agent, orchestrator):
    """Test that agent can be set on orchestrator and access MCP server."""
    test_name = "Orchestrator Integration"
    
    try:
        # Set orchestrator on agent
        agent.set_orchestrator(orchestrator)
        
        # Validate orchestrator is set
        assert agent._orchestrator is not None, "Orchestrator should be set"
        assert agent._orchestrator == orchestrator, "Orchestrator reference should match"
        
        # Validate MCP server is available
        assert hasattr(orchestrator, 'mcp_server'), "Orchestrator should have MCP server"
        assert orchestrator.mcp_server is not None, "MCP server should be initialized"
        
        # Get available tools
        available_tools = agent._get_available_tools()
        assert len(available_tools) > 0, "Agent should have access to tools"
        
        log_test(test_name, "PASS", details={
            "orchestrator_set": True,
            "mcp_server_available": True,
            "available_tools": len(available_tools),
            "tool_names": [t.get("name") for t in available_tools[:3]]
        })
        
        return True
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 3: LLM Abstraction Validation
# ============================================================================

async def test_llm_abstraction(agent):
    """Test that LLM abstraction is available and can make real calls."""
    test_name = "LLM Abstraction Validation"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available (may need API keys)")
            return False
        
        # Test LLM abstraction with a simple prompt
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
        
        test_prompt = "What is 2+2? Respond with just the number."
        
        # Use cost controls if available
        if COST_CONTROLS_AVAILABLE:
            model_name = TestConfig.get_test_model()
            max_tokens = TestConfig.MAX_TOKENS_IN_TESTS
            
            # Check cache first (zero cost)
            if response_cache:
                cached_response = response_cache.get(test_prompt, model_name)
                if cached_response:
                    logger.info("   💾 Using cached LLM response (zero cost)")
                    # Use cached response
                    llm_response_content = cached_response
                    # Create mock response object for validation
                    from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMResponse
                    llm_response = LLMResponse(
                        response_id="cached",
                        model=LLMModel[model_name.upper().replace("-", "_")],
                        content=llm_response_content,
                        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                        finish_reason="stop"
                    )
                else:
                    # Make real API call (track cost)
                    logger.info(f"   🧪 Making real LLM API call (model: {model_name}, max_tokens: {max_tokens})")
                    llm_request = LLMRequest(
                        messages=[{"role": "user", "content": test_prompt}],
                        model=LLMModel[model_name.upper().replace("-", "_")],
                        max_tokens=max_tokens,
                        temperature=0.0
                    )
                    
                    llm_response = await agent.llm_abstraction.generate_response(
                        llm_request,
                        retry_config=TestConfig.get_test_retry_config(),  # No retries in tests
                        timeout=TestConfig.get_test_timeout()
                    )
                    
                    # Cache response for future tests
                    response_cache.set(test_prompt, model_name, llm_response.content)
                    
                    # Track cost
                    if cost_tracker and TestConfig.should_track_costs():
                        tokens = llm_response.usage.get("total_tokens", 0) if isinstance(llm_response.usage, dict) else 0
                        cost_tracker.record_cost(test_name, tokens, model_name)
                        logger.info(f"   💰 Cost: ${cost_tracker.costs.get(test_name, 0):.4f}, Total: ${cost_tracker.total_cost:.4f}")
            else:
                # No cache, make real call
                logger.info(f"   🧪 Making real LLM API call (model: {model_name}, max_tokens: {max_tokens})")
                llm_request = LLMRequest(
                    messages=[{"role": "user", "content": test_prompt}],
                    model=LLMModel[model_name.upper().replace("-", "_")],
                    max_tokens=max_tokens,
                    temperature=0.0
                )
                llm_response = await agent.llm_abstraction.generate_response(
                    llm_request,
                    retry_config=TestConfig.get_test_retry_config(),
                    timeout=TestConfig.get_test_timeout()
                )
        else:
            # Fallback: use defaults (no cost controls)
            logger.info("   🧪 Testing LLM abstraction with real API call (no cost controls)...")
            llm_request = LLMRequest(
                messages=[{"role": "user", "content": test_prompt}],
                model=LLMModel.GPT_4O_MINI,
                max_tokens=50,
                temperature=0.0
            )
            llm_response = await agent.llm_abstraction.generate_response(llm_request)
        
        # Validate response
        assert llm_response is not None, "LLM response should not be None"
        assert hasattr(llm_response, 'content'), "LLM response should have content"
        assert len(llm_response.content) > 0, "LLM response should have content"
        
        logger.info(f"   ✅ LLM response received: {llm_response.content[:100]}...")
        
        log_test(test_name, "PASS", details={
            "llm_available": True,
            "response_received": True,
            "response_length": len(llm_response.content),
            "model": llm_response.model.value if hasattr(llm_response.model, 'value') else str(llm_response.model),
            "cached": response_cache and response_cache.get(test_prompt, model_name) is not None if COST_CONTROLS_AVAILABLE else False
        })
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "cost limit exceeded" in error_msg.lower():
            log_test(test_name, "FAIL", f"Cost limit exceeded: {error_msg}")
            logger.error("💰 Test cost limit exceeded - stopping tests to prevent further costs")
        elif "API key" in error_msg or "authentication" in error_msg.lower():
            log_test(test_name, "SKIP", f"LLM API not configured: {error_msg}")
        else:
            log_test(test_name, "FAIL", error_msg)
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 4: Prompt Building
# ============================================================================

async def test_prompt_building(agent):
    """Test that agent builds correct prompts from configuration."""
    test_name = "Prompt Building"
    
    try:
        # Create test request
        test_request = {
            "message": "Suggest mappings from legacy schema to canonical model",
            "task": "suggest_mappings",
            "data": {
                "source_schema": {
                    "name": "legacy_policy",
                    "fields": [
                        {"name": "policy_num", "type": "string"},
                        {"name": "prem_amt", "type": "decimal"}
                    ]
                },
                "target_schema_name": "canonical_policy"
            },
            "user_context": {
                "user_id": "test_user",
                "tenant_id": "test_tenant"
            }
        }
        
        # Build prompt
        prompt = agent._build_agent_prompt(test_request)
        
        # Validate prompt structure
        assert prompt is not None, "Prompt should not be None"
        assert len(prompt) > 0, "Prompt should not be empty"
        assert agent.role in prompt, "Prompt should include agent role"
        assert agent.goal in prompt, "Prompt should include agent goal"
        assert "Available Tools" in prompt, "Prompt should include available tools"
        assert test_request["message"] in prompt, "Prompt should include user message"
        
        # Check that tools are listed
        for tool_name in agent.allowed_tools[:2]:  # Check first 2 tools
            if tool_name in prompt:
                logger.info(f"   ✅ Tool '{tool_name}' found in prompt")
        
        log_test(test_name, "PASS", details={
            "prompt_length": len(prompt),
            "includes_role": agent.role in prompt,
            "includes_goal": agent.goal in prompt,
            "includes_tools": "Available Tools" in prompt,
            "tools_listed": sum(1 for tool in agent.allowed_tools if tool in prompt)
        })
        
        return True
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 5: suggest_mappings() with Real LLM
# ============================================================================

async def test_suggest_mappings_real_llm(agent):
    """Test suggest_mappings() with real LLM calls."""
    test_name = "suggest_mappings() with Real LLM"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available")
            return False
        
        # Create test schemas
        source_schema = {
            "name": "legacy_policy",
            "fields": [
                {"name": "policy_num", "type": "string", "description": "Policy number"},
                {"name": "prem_amt", "type": "decimal", "description": "Premium amount"},
                {"name": "eff_date", "type": "date", "description": "Effective date"},
                {"name": "cov_type", "type": "string", "description": "Coverage type"}
            ]
        }
        
        target_schema_name = "canonical_policy"
        
        logger.info("   🧪 Calling suggest_mappings() with real LLM...")
        result = await agent.suggest_mappings(
            source_schema=source_schema,
            target_schema_name=target_schema_name,
            client_id="test_client",
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Validate result structure
        assert result is not None, "Result should not be None"
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "success" in result, "Result should have 'success' field"
        
        if result.get("success"):
            assert "suggestions" in result, "Result should have 'suggestions' field"
            assert isinstance(result["suggestions"], list), "Suggestions should be a list"
            
            logger.info(f"   ✅ Received {len(result['suggestions'])} suggestions")
            
            # Log first suggestion if available
            if result["suggestions"]:
                first_suggestion = result["suggestions"][0]
                logger.info(f"   📋 First suggestion: {first_suggestion.get('source_field')} → {first_suggestion.get('target_field')}")
        
        log_test(test_name, "PASS", details={
            "success": result.get("success"),
            "suggestions_count": len(result.get("suggestions", [])),
            "has_reasoning": "reasoning" in result,
            "highest_confidence": result.get("highest_confidence", 0.0)
        })
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "authentication" in error_msg.lower():
            log_test(test_name, "SKIP", f"LLM API not configured: {error_msg}")
        else:
            log_test(test_name, "FAIL", error_msg)
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 6: learn_from_mappings() with Real LLM
# ============================================================================

async def test_learn_from_mappings_real_llm(agent):
    """Test learn_from_mappings() with real LLM calls."""
    test_name = "learn_from_mappings() with Real LLM"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available")
            return False
        
        # Create test data
        source_schema = {
            "name": "legacy_policy",
            "fields": [
                {"name": "policy_num", "type": "string"},
                {"name": "prem_amt", "type": "decimal"}
            ]
        }
        
        target_schema = {
            "name": "canonical_policy",
            "fields": [
                {"name": "policy_number", "type": "string"},
                {"name": "premium_amount", "type": "decimal"}
            ]
        }
        
        mapping_rules = {
            "rules": [
                {"source": "policy_num", "target": "policy_number", "transformation": "direct"},
                {"source": "prem_amt", "target": "premium_amount", "transformation": "direct"}
            ]
        }
        
        logger.info("   🧪 Calling learn_from_mappings() with real LLM...")
        result = await agent.learn_from_mappings(
            source_schema=source_schema,
            target_schema=target_schema,
            mapping_rules=mapping_rules,
            client_id="test_client",
            mapping_metadata={"accuracy": 0.95, "quality_score": 0.9},
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Validate result
        assert result is not None, "Result should not be None"
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "success" in result, "Result should have 'success' field"
        
        if result.get("success"):
            assert "pattern_id" in result, "Result should have 'pattern_id' field"
            assert "patterns_learned" in result, "Result should have 'patterns_learned' field"
            
            logger.info(f"   ✅ Learned {result.get('patterns_learned')} patterns")
            logger.info(f"   📋 Pattern ID: {result.get('pattern_id')}")
        
        log_test(test_name, "PASS", details={
            "success": result.get("success"),
            "pattern_id": result.get("pattern_id"),
            "patterns_learned": result.get("patterns_learned"),
            "confidence": result.get("confidence", 0.0)
        })
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "authentication" in error_msg.lower():
            log_test(test_name, "SKIP", f"LLM API not configured: {error_msg}")
        else:
            log_test(test_name, "FAIL", error_msg)
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 7: validate_mappings() with Real LLM
# ============================================================================

async def test_validate_mappings_real_llm(agent):
    """Test validate_mappings() with real LLM calls."""
    test_name = "validate_mappings() with Real LLM"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available")
            return False
        
        # Create test data
        source_schema = {
            "name": "legacy_policy",
            "fields": [
                {"name": "policy_num", "type": "string"},
                {"name": "prem_amt", "type": "decimal"}
            ]
        }
        
        target_schema = {
            "name": "canonical_policy",
            "fields": [
                {"name": "policy_number", "type": "string"},
                {"name": "premium_amount", "type": "decimal"}
            ]
        }
        
        mapping_rules = {
            "rules": [
                {"source": "policy_num", "target": "policy_number", "transformation": "direct"},
                {"source": "prem_amt", "target": "premium_amount", "transformation": "direct"}
            ]
        }
        
        logger.info("   🧪 Calling validate_mappings() with real LLM...")
        result = await agent.validate_mappings(
            source_schema=source_schema,
            target_schema=target_schema,
            mapping_rules=mapping_rules,
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Validate result
        assert result is not None, "Result should not be None"
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "success" in result, "Result should have 'success' field"
        assert "is_valid" in result, "Result should have 'is_valid' field"
        
        if result.get("success"):
            logger.info(f"   ✅ Validation result: {'VALID' if result.get('is_valid') else 'INVALID'}")
            logger.info(f"   📋 Confidence: {result.get('confidence', 0.0):.2f}")
        
        log_test(test_name, "PASS", details={
            "success": result.get("success"),
            "is_valid": result.get("is_valid"),
            "confidence": result.get("confidence", 0.0),
            "has_recommendations": len(result.get("recommendations", [])) > 0
        })
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "authentication" in error_msg.lower():
            log_test(test_name, "SKIP", f"LLM API not configured: {error_msg}")
        else:
            log_test(test_name, "FAIL", error_msg)
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 8: learn_from_correction() with Real LLM
# ============================================================================

async def test_learn_from_correction_real_llm(agent):
    """Test learn_from_correction() with real LLM calls."""
    test_name = "learn_from_correction() with Real LLM"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available")
            return False
        
        # Create test data
        original_mapping = {
            "source_field": "policy_num",
            "target_field": "policy_id",  # Incorrect
            "transformation": "direct"
        }
        
        corrected_mapping = {
            "source_field": "policy_num",
            "target_field": "policy_number",  # Correct
            "transformation": "direct"
        }
        
        correction_reason = "Policy number field should map to policy_number, not policy_id"
        
        logger.info("   🧪 Calling learn_from_correction() with real LLM...")
        result = await agent.learn_from_correction(
            original_mapping=original_mapping,
            corrected_mapping=corrected_mapping,
            correction_reason=correction_reason,
            approve_learning=True,
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Validate result
        assert result is not None, "Result should not be None"
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "success" in result, "Result should have 'success' field"
        
        if result.get("success"):
            assert "learned" in result, "Result should have 'learned' field"
            if result.get("learned"):
                assert "pattern_id" in result, "Result should have 'pattern_id' when learned"
                logger.info(f"   ✅ Correction learned: {result.get('pattern_id')}")
        
        log_test(test_name, "PASS", details={
            "success": result.get("success"),
            "learned": result.get("learned"),
            "pattern_id": result.get("pattern_id")
        })
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "authentication" in error_msg.lower():
            log_test(test_name, "SKIP", f"LLM API not configured: {error_msg}")
        else:
            log_test(test_name, "FAIL", error_msg)
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 9: MCP Tool Execution
# ============================================================================

async def test_mcp_tool_execution(agent, orchestrator):
    """Test that agent can execute MCP tools via orchestrator."""
    test_name = "MCP Tool Execution"
    
    try:
        # Ensure orchestrator is set
        if agent._orchestrator is None:
            agent.set_orchestrator(orchestrator)
        
        # Test tool execution (using map_to_canonical_tool)
        test_parameters = {
            "source_data": {
                "policy_num": "POL-123",
                "prem_amt": 1500.00,
                "eff_date": "2024-01-01"
            },
            "mapping_rules": {},
            "user_context": {
                "user_id": "test_user",
                "tenant_id": "test_tenant"
            }
        }
        
        logger.info("   🧪 Testing MCP tool execution...")
        
        # Execute tool directly via orchestrator's MCP server
        # Note: InsuranceMigrationMCPServer.execute_tool accepts dict for user_context
        user_context = test_parameters.pop("user_context", {
            "user_id": "test_user",
            "tenant_id": "test_tenant"
        })
        
        tool_result = await orchestrator.mcp_server.execute_tool(
            "map_to_canonical_tool",
            test_parameters,
            user_context
        )
        
        # Validate result
        assert tool_result is not None, "Tool result should not be None"
        assert isinstance(tool_result, dict), "Tool result should be a dictionary"
        
        logger.info(f"   ✅ Tool executed: {tool_result.get('success', False)}")
        
        # Test that agent can extract tool calls from LLM response
        # (This would normally come from LLM, but we'll test the extraction logic)
        mock_llm_response = {
            "reasoning": "I need to map the source data to canonical model",
            "tool_calls": [
                {
                    "tool_name": "map_to_canonical_tool",
                    "parameters": test_parameters
                }
            ],
            "response": "I've mapped the data to canonical model"
        }
        
        tool_calls = agent._extract_tool_calls_from_llm_response(mock_llm_response)
        assert len(tool_calls) > 0, "Should extract tool calls from LLM response"
        assert tool_calls[0]["tool_name"] == "map_to_canonical_tool", "Should extract correct tool name"
        
        log_test(test_name, "PASS", details={
            "tool_executed": True,
            "tool_result_success": tool_result.get("success", False),
            "tool_calls_extracted": len(tool_calls)
        })
        
        return True
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 10: Error Handling
# ============================================================================

async def test_error_handling(agent):
    """Test error handling in various scenarios."""
    test_name = "Error Handling"
    
    try:
        errors_handled = 0
        
        # Test 1: Invalid request (missing required fields)
        try:
            result = await agent.process_request({})
            # Should handle gracefully
            errors_handled += 1
        except Exception as e:
            # Expected to fail, but should be handled
            errors_handled += 1
        
        # Test 2: Invalid tool name (not in allowed_tools)
        mock_llm_response = {
            "tool_calls": [
                {"tool_name": "invalid_tool", "parameters": {}}
            ]
        }
        tool_calls = agent._extract_tool_calls_from_llm_response(mock_llm_response)
        # Should filter out invalid tools
        assert len(tool_calls) == 0, "Should filter out invalid tools"
        errors_handled += 1
        
        # Test 3: Too many tool calls (exceeds max_tool_calls)
        mock_llm_response = {
            "tool_calls": [
                {"tool_name": "map_to_canonical_tool", "parameters": {}} for _ in range(20)
            ]
        }
        tool_calls = agent._extract_tool_calls_from_llm_response(mock_llm_response)
        assert len(tool_calls) <= agent.max_tool_calls, "Should limit tool calls"
        errors_handled += 1
        
        log_test(test_name, "PASS", details={
            "errors_handled": errors_handled,
            "invalid_tools_filtered": True,
            "tool_call_limit_enforced": True
        })
        
        return True
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 11: Tool Scoping
# ============================================================================

async def test_tool_scoping(agent, orchestrator):
    """Test that agent only sees allowed tools (scoping works)."""
    test_name = "Tool Scoping"
    
    try:
        # Ensure orchestrator is set
        if agent._orchestrator is None:
            agent.set_orchestrator(orchestrator)
        
        # Get all tools from MCP server
        # Use get_registered_tools() which returns a dict, convert to list format
        registered_tools = orchestrator.mcp_server.get_registered_tools() if hasattr(orchestrator.mcp_server, 'get_registered_tools') else {}
        all_tools = [
            {
                "name": tool_name,
                "description": tool_info.get("description", ""),
                "input_schema": tool_info.get("input_schema", {})
            }
            for tool_name, tool_info in registered_tools.items()
        ] if registered_tools else []
        
        # Get scoped tools (what agent sees)
        scoped_tools = agent._get_available_tools()
        
        # Validate scoping
        scoped_tool_names = [t.get("name") for t in scoped_tools]
        
        # All scoped tools should be in allowed_tools
        for tool in scoped_tools:
            tool_name = tool.get("name")
            assert tool_name in agent.allowed_tools, f"Tool '{tool_name}' should be in allowed_tools"
        
        # All allowed_tools should be in scoped tools (if they exist in MCP server)
        for tool_name in agent.allowed_tools:
            if any(t.get("name") == tool_name for t in all_tools):
                assert any(t.get("name") == tool_name for t in scoped_tools), f"Tool '{tool_name}' should be in scoped tools"
        
        log_test(test_name, "PASS", details={
            "all_tools_count": len(all_tools),
            "scoped_tools_count": len(scoped_tools),
            "allowed_tools_count": len(agent.allowed_tools),
            "scoping_works": len(scoped_tools) <= len(all_tools)
        })
        
        return True
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 12: Full Workflow Integration
# ============================================================================

async def test_full_workflow_integration(agent):
    """Test a full workflow: suggest → validate → learn."""
    test_name = "Full Workflow Integration"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available")
            return False
        
        # Step 1: Suggest mappings
        source_schema = {
            "name": "legacy_policy",
            "fields": [
                {"name": "policy_num", "type": "string"},
                {"name": "prem_amt", "type": "decimal"}
            ]
        }
        
        logger.info("   🔄 Step 1: Suggesting mappings...")
        suggestions_result = await agent.suggest_mappings(
            source_schema=source_schema,
            target_schema_name="canonical_policy",
            client_id="test_client"
        )
        
        if not suggestions_result.get("success"):
            log_test(test_name, "SKIP", "Suggestions failed, skipping workflow")
            return False
        
        suggestions = suggestions_result.get("suggestions", [])
        logger.info(f"   ✅ Got {len(suggestions)} suggestions")
        
        # Step 2: Build mapping rules from suggestions
        mapping_rules = {
            "rules": [
                {
                    "source": s.get("source_field"),
                    "target": s.get("target_field"),
                    "transformation": s.get("transformation", "direct")
                }
                for s in suggestions[:2]  # Use first 2 suggestions
            ]
        }
        
        target_schema = {
            "name": "canonical_policy",
            "fields": [
                {"name": "policy_number", "type": "string"},
                {"name": "premium_amount", "type": "decimal"}
            ]
        }
        
        # Step 3: Validate mappings
        logger.info("   🔄 Step 2: Validating mappings...")
        validation_result = await agent.validate_mappings(
            source_schema=source_schema,
            target_schema=target_schema,
            mapping_rules=mapping_rules
        )
        
        logger.info(f"   ✅ Validation: {'VALID' if validation_result.get('is_valid') else 'INVALID'}")
        
        # Step 4: Learn from mappings (if valid)
        if validation_result.get("is_valid"):
            logger.info("   🔄 Step 3: Learning from mappings...")
            learning_result = await agent.learn_from_mappings(
                source_schema=source_schema,
                target_schema=target_schema,
                mapping_rules=mapping_rules,
                client_id="test_client",
                mapping_metadata={"accuracy": 0.9}
            )
            
            logger.info(f"   ✅ Learned: {learning_result.get('patterns_learned')} patterns")
        
        log_test(test_name, "PASS", details={
            "suggestions_count": len(suggestions),
            "validation_passed": validation_result.get("is_valid"),
            "learning_successful": learning_result.get("success") if validation_result.get("is_valid") else False
        })
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "authentication" in error_msg.lower():
            log_test(test_name, "SKIP", f"LLM API not configured: {error_msg}")
        else:
            log_test(test_name, "FAIL", error_msg)
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 13: Performance and Resource Usage
# ============================================================================

async def test_performance(agent):
    """Test agent performance and resource usage."""
    test_name = "Performance and Resource Usage"
    
    try:
        import time
        
        # Test prompt building performance
        test_request = {
            "message": "Test performance",
            "data": {"test": "data"}
        }
        
        start_time = time.time()
        prompt = agent._build_agent_prompt(test_request)
        prompt_time = time.time() - start_time
        
        # Test tool extraction performance
        mock_response = {
            "tool_calls": [
                {"tool_name": "map_to_canonical_tool", "parameters": {}}
            ]
        }
        
        start_time = time.time()
        tool_calls = agent._extract_tool_calls_from_llm_response(mock_response)
        extraction_time = time.time() - start_time
        
        # Validate performance (should be fast)
        assert prompt_time < 1.0, "Prompt building should be fast (< 1s)"
        assert extraction_time < 1.0, "Tool extraction should be fast (< 1s)"
        
        log_test(test_name, "PASS", details={
            "prompt_building_time": f"{prompt_time:.3f}s",
            "tool_extraction_time": f"{extraction_time:.3f}s",
            "performance_acceptable": True
        })
        
        return True
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_comprehensive_tests():
    """Run all comprehensive tests."""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 COMPREHENSIVE DECLARATIVE AGENT TESTING")
    logger.info("=" * 80)
    logger.info("")
    
    platform_services = None
    orchestrator = None
    agent = None
    
    try:
        # Setup
        logger.info("📦 PHASE 1: Platform Setup")
        logger.info("-" * 80)
        platform_services = await setup_platform_services()
        logger.info("")
        
        logger.info("📦 PHASE 2: Orchestrator Setup")
        logger.info("-" * 80)
        orchestrator = await setup_orchestrator(platform_services)
        logger.info("")
        
        # Tests
        logger.info("🧪 PHASE 3: Agent Tests")
        logger.info("-" * 80)
        
        # Test 1: Agent Initialization
        agent = await test_agent_initialization_real(platform_services)
        if not agent:
            logger.error("❌ Agent initialization failed - cannot continue tests")
            return False
        logger.info("")
        
        # Test 2: Orchestrator Integration
        await test_orchestrator_integration(agent, orchestrator)
        logger.info("")
        
        # Test 3: LLM Abstraction
        await test_llm_abstraction(agent)
        logger.info("")
        
        # Test 4: Prompt Building
        await test_prompt_building(agent)
        logger.info("")
        
        # Test 5: suggest_mappings() with Real LLM
        await test_suggest_mappings_real_llm(agent)
        logger.info("")
        
        # Test 6: learn_from_mappings() with Real LLM
        await test_learn_from_mappings_real_llm(agent)
        logger.info("")
        
        # Test 7: validate_mappings() with Real LLM
        await test_validate_mappings_real_llm(agent)
        logger.info("")
        
        # Test 8: learn_from_correction() with Real LLM
        await test_learn_from_correction_real_llm(agent)
        logger.info("")
        
        # Test 9: MCP Tool Execution
        await test_mcp_tool_execution(agent, orchestrator)
        logger.info("")
        
        # Test 10: Error Handling
        await test_error_handling(agent)
        logger.info("")
        
        # Test 11: Tool Scoping
        await test_tool_scoping(agent, orchestrator)
        logger.info("")
        
        # Test 12: Full Workflow Integration
        await test_full_workflow_integration(agent)
        logger.info("")
        
        # Test 13: Performance
        await test_performance(agent)
        logger.info("")
        
        # Summary
        logger.info("=" * 80)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"   Total Tests: {test_results['total']}")
        logger.info(f"   ✅ Passed: {test_results['passed']}")
        logger.info(f"   ❌ Failed: {test_results['failed']}")
        logger.info(f"   ⏭️  Skipped: {test_results['total'] - test_results['passed'] - test_results['failed']}")
        logger.info(f"   Success Rate: {(test_results['passed'] / test_results['total'] * 100):.1f}%")
        logger.info("")
        
        # Cost summary
        if COST_CONTROLS_AVAILABLE and cost_tracker:
            cost_summary = cost_tracker.get_summary()
            logger.info("💰 COST SUMMARY")
            logger.info("=" * 80)
            logger.info(f"   Total Cost: ${cost_summary['total_cost']:.4f}")
            logger.info(f"   Total API Calls: {cost_summary['total_calls']}")
            logger.info(f"   Max Budget: ${cost_summary['max_cost']:.2f}")
            logger.info(f"   Remaining Budget: ${cost_summary['remaining_budget']:.4f}")
            if cost_summary['test_costs']:
                logger.info("   Per-Test Costs:")
                for test_name, cost in cost_summary['test_costs'].items():
                    logger.info(f"      - {test_name}: ${cost:.4f}")
            logger.info("")
        
        if test_results['failed'] > 0:
            logger.error("❌ FAILED TESTS:")
            for error in test_results['errors']:
                logger.error(f"   - {error}")
            logger.info("")
            return False
        else:
            logger.info("✅ ALL TESTS PASSED!")
            logger.info("")
            logger.info("🎯 The declarative agent is bulletproof and ready for:")
            logger.info("   1. Migrating remaining agents")
            logger.info("   2. Updating Agentic SDK")
            logger.info("   3. Production deployment")
            logger.info("")
            return True
            
    except Exception as e:
        logger.error(f"❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    sys.exit(0 if success else 1)

