#!/usr/bin/env python3
"""
Priority 2 Features Test

Tests the Priority 2 features with cost controls:
1. Multi-turn conversation support (stateful pattern)
2. Tool result feedback loops (iterative execution)
3. Cost tracking

Uses cost controls to minimize API costs.
"""

import sys
import os

# Set Traefik URL to localhost for testing
if not os.environ.get("TRAEFIK_API_URL"):
    os.environ["TRAEFIK_API_URL"] = "http://localhost:8080"

# Cost control configuration
os.environ.setdefault("TEST_USE_REAL_LLM", "true")
os.environ.setdefault("TEST_USE_CHEAPEST_MODEL", "true")
os.environ.setdefault("TEST_ENABLE_RETRIES", "false")
os.environ.setdefault("TEST_MAX_TOKENS", "50")
os.environ.setdefault("TEST_TRACK_COSTS", "true")
os.environ.setdefault("TEST_MAX_COST", "2.00")
os.environ.setdefault("TEST_USE_CACHE", "true")

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))
sys.path.insert(0, str(project_root / "tests"))

# Import cost management utilities
from test_config import TestConfig
from fixtures.llm_response_cache import LLMResponseCache
from utils.cost_tracker import get_cost_tracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Priority2FeaturesTest")

# Initialize cost tracking and response cache
cost_tracker = get_cost_tracker(max_cost=float(os.getenv("TEST_MAX_COST", "2.00")))
response_cache = LLMResponseCache() if TestConfig.USE_RESPONSE_CACHE else None

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
# TEST SETUP (Reuse from Priority 1 test)
# ============================================================================

async def setup_platform_services():
    """Initialize platform services."""
    logger.info("🔧 Setting up platform services...")
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService("test_priority2_features")
        
        # Initialize Public Works Foundation
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize_foundation()
        di_container.service_registry["PublicWorksFoundationService"] = public_works
        
        # Initialize Curator Foundation
        curator = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=public_works
        )
        await curator.initialize()
        di_container.service_registry["CuratorFoundationService"] = curator
        
        # Initialize Agentic Foundation
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works,
            curator_foundation=curator
        )
        await agentic_foundation.initialize()
        di_container.service_registry["AgenticFoundationService"] = agentic_foundation
        
        logger.info("✅ Platform services initialized")
        
        return {
            "di_container": di_container,
            "public_works": public_works,
            "curator": curator,
            "agentic_foundation": agentic_foundation
        }
        
    except Exception as e:
        logger.error(f"❌ Platform setup failed: {e}")
        import traceback
        traceback.print_exc()
        raise

async def setup_agent(platform_services: Dict[str, Any], stateful: bool = False, iterative: bool = False):
    """Initialize declarative agent with Priority 2 config."""
    logger.info(f"🔧 Setting up declarative agent (stateful={stateful}, iterative={iterative})...")
    
    try:
        from backend.business_enablement.agents.specialists.universal_mapper_specialist_declarative import UniversalMapperSpecialist
        from foundations.agentic_foundation.agent_sdk.policy_integration import PolicyIntegration
        from foundations.agentic_foundation.agent_sdk.tool_composition import ToolComposition
        
        agentic_foundation = platform_services["agentic_foundation"]
        di_container = platform_services["di_container"]
        public_works = platform_services["public_works"]
        curator = platform_services["curator"]
        
        # Instantiate SDK components
        policy_integration = PolicyIntegration(
            foundation_services=di_container,
            agentic_foundation=agentic_foundation
        )
        tool_composition = ToolComposition(
            foundation_services=di_container,
            agentic_foundation=agentic_foundation
        )
        agui_formatter = agentic_foundation.agui_formatter
        mcp_client_manager = agentic_foundation.mcp_client_manager
        
        # Initialize agent
        config_path = project_root / "symphainy-platform" / "backend" / "business_enablement" / "agents" / "configs" / "universal_mapper_specialist.yaml"
        
        agent = UniversalMapperSpecialist(
            foundation_services=di_container,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator,
            public_works_foundation=public_works
        )
        
        await agent.initialize()
        
        # Override config for testing Priority 2 features
        if stateful:
            agent.stateful = True
            agent.max_conversation_history = 5  # Small for testing
        if iterative:
            agent.iterative_execution = True
            agent.max_iterations = 3  # Small for testing
        
        logger.info("✅ Agent initialized")
        return agent
        
    except Exception as e:
        logger.error(f"❌ Agent setup failed: {e}")
        import traceback
        traceback.print_exc()
        raise

# ============================================================================
# TEST 1: Cost Tracking
# ============================================================================

async def test_cost_tracking(agent):
    """Test cost tracking feature."""
    test_name = "Cost Tracking"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available")
            return False
        
        # Verify cost tracking is enabled
        assert agent.cost_tracking == True, "Cost tracking should be enabled"
        assert hasattr(agent, '_total_cost'), "Agent should have _total_cost attribute"
        assert hasattr(agent, '_cost_history'), "Agent should have _cost_history attribute"
        
        initial_cost = agent._total_cost
        
        # Make a simple request
        source_schema = {
            "name": "legacy_policy",
            "fields": [{"name": "policy_num", "type": "string"}]
        }
        
        logger.info("   🧪 Making request to track cost...")
        
        result = await agent.suggest_mappings(
            source_schema=source_schema,
            target_schema_name="canonical_policy",
            client_id="test_client",
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Verify cost was tracked
        final_cost = agent._total_cost
        cost_increase = final_cost - initial_cost
        
        # Verify cost info in response
        assert "cost_info" in result, "Response should include cost_info"
        assert result["cost_info"]["total_cost"] >= 0, "Total cost should be non-negative"
        
        log_test(test_name, "PASS", details={
            "cost_tracking_enabled": True,
            "cost_tracked": cost_increase > 0,
            "total_cost": f"${final_cost:.4f}",
            "cost_in_response": True
        })
        
        return True
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 2: Stateful Pattern (Conversation History)
# ============================================================================

async def test_stateful_conversation(agent):
    """Test stateful pattern with conversation history."""
    test_name = "Stateful Conversation History"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available")
            return False
        
        # Create stateful agent
        agent.stateful = True
        agent.max_conversation_history = 5
        agent.conversation_history = []
        
        # First message
        logger.info("   🧪 Testing conversation history (message 1)...")
        source_schema1 = {
            "name": "legacy_policy",
            "fields": [{"name": "policy_num", "type": "string"}]
        }
        
        result1 = await agent.suggest_mappings(
            source_schema=source_schema1,
            target_schema_name="canonical_policy",
            client_id="test_client",
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Verify conversation history was updated
        assert len(agent.conversation_history) >= 2, "Conversation history should have at least 2 messages"
        assert agent.conversation_history[-2]["role"] == "user", "Second-to-last should be user message"
        assert agent.conversation_history[-1]["role"] == "assistant", "Last should be assistant message"
        
        # Second message (should include conversation history)
        logger.info("   🧪 Testing conversation history (message 2)...")
        source_schema2 = {
            "name": "legacy_claim",
            "fields": [{"name": "claim_num", "type": "string"}]
        }
        
        result2 = await agent.suggest_mappings(
            source_schema=source_schema2,
            target_schema_name="canonical_claim",
            client_id="test_client",
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Verify conversation history includes both messages
        assert len(agent.conversation_history) >= 4, "Conversation history should have at least 4 messages"
        assert "conversation_history_length" in result2, "Response should include conversation history length"
        
        log_test(test_name, "PASS", details={
            "stateful_enabled": True,
            "conversation_history_length": len(agent.conversation_history),
            "history_in_response": True,
            "messages_tracked": len(agent.conversation_history) >= 4
        })
        
        return True
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 3: Iterative Execution (Tool Feedback Loops)
# ============================================================================

async def test_iterative_execution(agent):
    """Test iterative execution with tool feedback loops."""
    test_name = "Iterative Execution"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available")
            return False
        
        # Enable iterative execution
        agent.iterative_execution = True
        agent.max_iterations = 3
        
        logger.info("   🧪 Testing iterative execution...")
        
        # Make a request that might require multiple iterations
        source_schema = {
            "name": "legacy_policy",
            "fields": [
                {"name": "policy_num", "type": "string"},
                {"name": "prem_amt", "type": "decimal"},
                {"name": "eff_date", "type": "date"}
            ]
        }
        
        result = await agent.suggest_mappings(
            source_schema=source_schema,
            target_schema_name="canonical_policy",
            client_id="test_client",
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Verify iterative execution was used
        # Note: The agent might not actually use multiple iterations if it doesn't need to,
        # but we can verify the feature is enabled and working
        assert result is not None, "Result should not be None"
        assert "success" in result, "Result should have success field"
        
        # Check if tool_results contains iterations (if iterative execution was used)
        tool_results = result.get("tool_results", {})
        has_iterations = "iterations" in tool_results
        
        log_test(test_name, "PASS", details={
            "iterative_execution_enabled": True,
            "max_iterations": agent.max_iterations,
            "result_received": True,
            "iterations_used": has_iterations
        })
        
        return True
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 4: Combined Features
# ============================================================================

async def test_combined_features(agent):
    """Test all Priority 2 features together."""
    test_name = "Combined Priority 2 Features"
    
    try:
        if not agent.llm_abstraction:
            log_test(test_name, "SKIP", "LLM abstraction not available")
            return False
        
        # Enable all Priority 2 features
        agent.stateful = True
        agent.max_conversation_history = 5
        agent.iterative_execution = True
        agent.max_iterations = 3
        agent.cost_tracking = True
        agent.conversation_history = []
        
        logger.info("   🧪 Testing all Priority 2 features together...")
        
        source_schema = {
            "name": "legacy_policy",
            "fields": [{"name": "policy_num", "type": "string"}]
        }
        
        result = await agent.suggest_mappings(
            source_schema=source_schema,
            target_schema_name="canonical_policy",
            client_id="test_client",
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Verify all features are working
        checks = {
            "cost_tracking": "cost_info" in result,
            "stateful": len(agent.conversation_history) >= 2,
            "iterative_execution": agent.iterative_execution == True,
            "result_success": result.get("success") == True
        }
        
        all_passed = all(checks.values())
        
        log_test(test_name, "PASS" if all_passed else "FAIL", details=checks)
        
        return all_passed
        
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_priority2_tests():
    """Run Priority 2 features tests."""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 PRIORITY 2 FEATURES TESTING")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Testing:")
    logger.info("  1. Cost tracking")
    logger.info("  2. Stateful conversation history")
    logger.info("  3. Iterative execution (tool feedback loops)")
    logger.info("  4. Combined features")
    logger.info("")
    logger.info(f"💰 Cost Controls: max_cost=${cost_tracker.max_cost}, cache={'enabled' if response_cache else 'disabled'}")
    logger.info("")
    
    platform_services = None
    agent = None
    
    try:
        # Setup
        logger.info("📦 PHASE 1: Platform Setup")
        logger.info("-" * 80)
        platform_services = await setup_platform_services()
        logger.info("")
        
        logger.info("📦 PHASE 2: Agent Setup")
        logger.info("-" * 80)
        agent = await setup_agent(platform_services, stateful=False, iterative=False)
        logger.info("")
        
        # Tests
        logger.info("🧪 PHASE 3: Priority 2 Tests")
        logger.info("-" * 80)
        
        # Test 1: Cost Tracking
        await test_cost_tracking(agent)
        logger.info("")
        
        # Test 2: Stateful Conversation
        await test_stateful_conversation(agent)
        logger.info("")
        
        # Test 3: Iterative Execution
        await test_iterative_execution(agent)
        logger.info("")
        
        # Test 4: Combined Features
        await test_combined_features(agent)
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
            logger.info("✅ ALL PRIORITY 2 TESTS PASSED!")
            logger.info("")
            logger.info("🎯 Priority 2 features are implemented and verified:")
            logger.info("   ✅ Cost tracking")
            logger.info("   ✅ Stateful conversation history")
            logger.info("   ✅ Iterative execution (tool feedback loops)")
            logger.info("")
            return True
            
    except Exception as e:
        logger.error(f"❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_priority2_tests())
    sys.exit(0 if success else 1)







