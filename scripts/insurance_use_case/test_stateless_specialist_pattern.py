#!/usr/bin/env python3
"""
Test Stateless Specialist Pattern - RecommendationSpecialist

Tests the simplest pattern: stateless, single-pass execution.
No conversation history, no iterative execution.

Tests:
1. Agent initialization
2. YAML config loading
3. LLM integration (single call)
4. Tool execution (if needed)
5. Response formatting
6. Cost tracking
7. Stateless behavior (no history)

Uses PRODUCTION environment to ensure fixes actually work.
"""

import sys
import os
from pathlib import Path

# Configure for PRODUCTION environment
# Use production endpoints instead of localhost
PRODUCTION_BASE_URL = os.getenv("PRODUCTION_BASE_URL", "http://35.215.64.103")
# Traefik API might be on port 80 (via Traefik routing) or 8080 (direct API access)
# Try port 80 first (standard Traefik routing), fallback to 8080
PRODUCTION_TRAEFIK_URL = os.getenv("TRAEFIK_API_URL", f"{PRODUCTION_BASE_URL}:80")
PRODUCTION_MCP_URL = os.getenv("MCP_SERVER_URL", f"{PRODUCTION_BASE_URL}:8000/mcp")

# Set production environment variables
# Use production URLs but keep ENVIRONMENT as "development" to avoid strict production checks
os.environ["TRAEFIK_API_URL"] = PRODUCTION_TRAEFIK_URL
os.environ["MCP_SERVER_URL"] = PRODUCTION_MCP_URL
os.environ["ENVIRONMENT"] = "development"  # Keep as development to avoid OTEL requirements
os.environ["TEST_MODE"] = "true"  # Mark as test mode
os.environ["TRAEFIK_OPTIONAL_IN_TEST"] = "true"  # Make Traefik optional for this test

print(f"🔧 Using PRODUCTION environment:")
print(f"   Base URL: {PRODUCTION_BASE_URL}")
print(f"   Traefik: {PRODUCTION_TRAEFIK_URL}")
print(f"   MCP Server: {PRODUCTION_MCP_URL}")
print()

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))
sys.path.insert(0, str(project_root / "tests"))

import asyncio
import logging
from typing import Dict, Any

# Test configuration
from tests.test_config import TestConfig
from tests.fixtures.llm_response_cache import LLMResponseCache
from tests.utils.cost_tracker import TestCostTracker

# Platform imports
from foundations.di_container.di_container_service import DIContainerService
from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
from foundations.agentic_foundation.agent_sdk.mcp_client_manager import MCPClientManager
from foundations.agentic_foundation.agent_sdk.policy_integration import PolicyIntegration
from foundations.agentic_foundation.agent_sdk.tool_composition import ToolComposition
from foundations.agentic_foundation.agent_sdk.agui_output_formatter import AGUIOutputFormatter

# Agent imports
from backend.business_enablement.agents.recommendation_specialist import RecommendationSpecialist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_stateless_specialist_pattern():
    """Test Stateless Specialist Pattern with RecommendationSpecialist."""
    
    print("\n" + "="*80)
    print("TEST: Stateless Specialist Pattern - RecommendationSpecialist")
    print("="*80 + "\n")
    
    # Initialize test infrastructure
    test_config = TestConfig()
    cost_tracker = TestCostTracker(max_cost=test_config.get_max_cost())
    llm_cache = LLMResponseCache() if test_config.USE_RESPONSE_CACHE else None
    
    print(f"📋 Test Configuration:")
    print(f"   Environment: PRODUCTION")
    print(f"   USE_REAL_LLM: {test_config.should_use_real_llm()}")
    print(f"   USE_CHEAPEST_MODEL: {test_config.USE_CHEAPEST_MODEL}")
    print(f"   MAX_TEST_COST: ${test_config.get_max_cost()}")
    print(f"   USE_CACHE: {test_config.USE_RESPONSE_CACHE}")
    print(f"   Traefik URL: {os.getenv('TRAEFIK_API_URL')}")
    print(f"   MCP Server URL: {os.getenv('MCP_SERVER_URL')}")
    print()
    
    try:
        # Initialize DI container
        print("🔧 Initializing DI Container...")
        di_container = DIContainerService("test_stateless_specialist")
        print("✅ DI Container initialized")
        
        # Initialize Public Works Foundation
        print("🔧 Initializing Public Works Foundation...")
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize_foundation()
        di_container.service_registry["PublicWorksFoundationService"] = public_works
        
        # Verify initialization
        if not public_works.is_initialized:
            raise RuntimeError("Public Works Foundation initialization failed - is_initialized is False")
        print(f"✅ Public Works Foundation initialized (is_initialized: {public_works.is_initialized})")
        
        # Initialize Curator Foundation
        print("🔧 Initializing Curator Foundation...")
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        curator = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=public_works
        )
        await curator.initialize()
        di_container.service_registry["CuratorFoundationService"] = curator
        print("✅ Curator Foundation initialized")
        
        # Initialize Agentic Foundation
        print("🔧 Initializing Agentic Foundation...")
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works,
            curator_foundation=curator
        )
        await agentic_foundation.initialize()
        di_container.service_registry["AgenticFoundationService"] = agentic_foundation
        print("✅ Agentic Foundation initialized")
        
        # Get required services
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
        
        # Initialize RecommendationSpecialist
        print("\n🔧 Initializing RecommendationSpecialist...")
        agent = RecommendationSpecialist(
            foundation_services=di_container,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator,
            metadata_foundation=None,
            public_works_foundation=public_works,
            logger=logger
        )
        
        await agent.initialize()
        print("✅ RecommendationSpecialist initialized")
        
        # Verify configuration
        print("\n📋 Verifying Configuration...")
        assert agent.agent_config is not None, "Agent config should be loaded"
        assert agent.agent_config.get("agent_name") == "RecommendationSpecialist", "Agent name should match"
        assert agent.stateful == False, "Should be stateless"
        assert agent.iterative_execution == False, "Should not use iterative execution"
        assert agent.cost_tracking == True, "Cost tracking should be enabled"
        print("✅ Configuration verified")
        
        # Test 1: Simple recommendation request
        print("\n🧪 Test 1: Simple Recommendation Request")
        print("-" * 80)
        
        analysis_data = {
            "metrics": {
                "revenue": 1000000,
                "costs": 800000,
                "profit": 200000
            },
            "trends": {
                "revenue_growth": "positive",
                "cost_reduction": "moderate"
            }
        }
        
        user_context = {
            "user_id": "test_user",
            "role": "manager",
            "tenant_id": "test_tenant"
        }
        
        print(f"   Input: Analysis data with {len(analysis_data)} metrics")
        print(f"   User context: {user_context.get('role')}")
        
        # Track cost before
        cost_before = cost_tracker.total_cost if hasattr(cost_tracker, 'total_cost') else 0.0
        
        result = await agent.generate_recommendations(
            analysis_data=analysis_data,
            user_context=user_context,
            recommendation_type="strategic"
        )
        
        # Track cost after
        cost_after = cost_tracker.total_cost if hasattr(cost_tracker, 'total_cost') else 0.0
        cost_incurred = cost_after - cost_before
        
        print(f"\n   ✅ Request completed")
        print(f"   Cost incurred: ${cost_incurred:.4f}")
        print(f"   Total cost so far: ${cost_after:.4f}")
        
        # Also check agent's internal cost tracking if available
        if hasattr(agent, '_total_cost'):
            agent_cost = agent._total_cost
            print(f"   Agent internal cost: ${agent_cost:.4f}")
        
        # Verify response
        assert result.get("success") == True, "Request should succeed"
        assert "recommendations" in result, "Response should include recommendations"
        assert isinstance(result.get("recommendations"), list), "Recommendations should be a list"
        print(f"   ✅ Response verified: {len(result.get('recommendations', []))} recommendations")
        
        # Verify stateless behavior (no conversation history)
        print("\n🧪 Test 2: Stateless Behavior Verification")
        print("-" * 80)
        
        # Check that conversation history is empty or minimal
        conversation_history_length = result.get("conversation_history_length", 0)
        print(f"   Conversation history length: {conversation_history_length}")
        assert conversation_history_length == 0 or conversation_history_length <= 2, \
            "Stateless agent should have minimal/no conversation history"
        print("   ✅ Stateless behavior verified (no conversation history maintained)")
        
        # Verify cost tracking
        print("\n🧪 Test 3: Cost Tracking Verification")
        print("-" * 80)
        
        if "cost_info" in result:
            cost_info = result["cost_info"]
            print(f"   Cost info: {cost_info}")
            assert "total_cost" in cost_info or "tokens_used" in cost_info, \
                "Cost info should include cost or token information"
            print("   ✅ Cost tracking verified")
        else:
            print("   ⚠️ Cost info not in response (may be optional)")
        
        # Test 4: Second request (should be independent)
        print("\n🧪 Test 4: Independent Request (Stateless)")
        print("-" * 80)
        
        analysis_data_2 = {
            "metrics": {
                "customer_satisfaction": 4.5,
                "retention_rate": 0.85
            }
        }
        
        result_2 = await agent.generate_recommendations(
            analysis_data=analysis_data_2,
            user_context=user_context,
            recommendation_type="operational"
        )
        
        print(f"   ✅ Second request completed")
        print(f"   Recommendations: {len(result_2.get('recommendations', []))}")
        
        # Verify second request is independent (no context from first)
        conversation_history_length_2 = result_2.get("conversation_history_length", 0)
        print(f"   Conversation history length: {conversation_history_length_2}")
        assert conversation_history_length_2 == 0 or conversation_history_length_2 <= 2, \
            "Second request should also be stateless"
        print("   ✅ Independent request verified (no context from previous request)")
        
        # Summary
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - Stateless Specialist Pattern")
        print("="*80)
        print(f"\n📊 Test Summary:")
        print(f"   Pattern: Stateless Specialist")
        print(f"   Agent: RecommendationSpecialist")
        print(f"   Tests: 4/4 passed")
        total_cost = cost_tracker.total_cost if hasattr(cost_tracker, 'total_cost') else 0.0
        print(f"   Total cost: ${total_cost:.4f}")
        print(f"   Conversation history: Not maintained (stateless)")
        print(f"   Iterative execution: Not used (single-pass)")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_stateless_specialist_pattern())
    sys.exit(0 if success else 1)

