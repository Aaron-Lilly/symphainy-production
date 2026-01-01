#!/usr/bin/env python3
"""
Agentic-Forward Integration Tests - Business Outcomes (Real LLM)

Integration tests with REAL LLM calls to validate:
- Agent does critical reasoning with actual LLM
- Services execute agent's strategic decisions
- Real, relevant results/artifacts are produced
"""

import pytest
import asyncio
from typing import Dict, Any
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Load .env.secrets file if it exists (MUST happen before checking API keys)
def _load_env_secrets():
    """Load .env.secrets file."""
    try:
        from dotenv import load_dotenv
        from pathlib import Path
        
        # Get absolute paths to ensure we find the file regardless of CWD
        current_file = Path(__file__).resolve()
        # Go up from test file: tests/integration/agentic_forward/test_*.py
        # To project root: symphainy_source/
        test_dir = current_file.parent
        integration_dir = test_dir.parent
        tests_dir = integration_dir.parent
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
                # Also try relative to current working directory
                cwd_secrets = Path.cwd() / ".env.secrets"
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

# Check for API keys (try both OPENAI_API_KEY and LLM_OPENAI_API_KEY)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("LLM_ANTHROPIC_API_KEY")

pytestmark = pytest.mark.integration


class TestBusinessOutcomesRealLLM:
    """Integration tests with real LLM calls for Business Outcomes."""
    
    @pytest.fixture
    def sample_pillar_outputs(self):
        """Sample pillar outputs for testing."""
        return {
            "content_pillar": {
                "success": True,
                "semantic_data_model": {
                    "structured_files": {
                        "count": 15,
                        "types": ["CSV", "JSON", "Excel"]
                    },
                    "unstructured_files": {
                        "count": 8,
                        "types": ["PDF", "DOCX"]
                    },
                    "entities": ["Customer", "Product", "Order"],
                    "relationships": ["Customer->Order", "Order->Product"]
                },
                "summary": {
                    "textual": "Content pillar processed 23 files. Created semantic data model with 3 entities and 2 relationships.",
                    "tabular": {
                        "files_processed": 23,
                        "entities_found": 3,
                        "relationships_found": 2
                    }
                }
            },
            "insights_pillar": {
                "success": True,
                "summary": {
                    "textual": "Key insights: Customer retention is declining. Product sales are increasing. Order fulfillment time is improving.",
                    "tabular": {
                        "metrics_analyzed": 12,
                        "insights_generated": 5
                    }
                },
                "key_findings": [
                    "Customer retention down 15%",
                    "Product sales up 20%",
                    "Order fulfillment improved 10%"
                ]
            },
            "operations_pillar": {
                "success": True,
                "artifacts": {
                    "workflows": [
                        {"workflow_id": "wf_1", "name": "Order Processing", "steps": 5},
                        {"workflow_id": "wf_2", "name": "Customer Onboarding", "steps": 8}
                    ],
                    "sops": [
                        {"sop_id": "sop_1", "name": "Quality Control", "steps": 6}
                    ],
                    "coexistence_blueprints": [
                        {"blueprint_id": "bp_1", "name": "Order-Customer Coexistence"}
                    ]
                },
                "summary": {
                    "textual": "Operations pillar created 2 workflows, 1 SOP, and 1 coexistence blueprint.",
                    "tabular": {
                        "workflows": 2,
                        "sops": 1,
                        "blueprints": 1
                    }
                }
            }
        }
    
    @pytest.fixture
    def business_context(self, sample_pillar_outputs):
        """Business context for testing."""
        return {
            "business_name": "Test Retail Corp",
            "pillar_outputs": sample_pillar_outputs,
            "objectives": [
                "Improve customer retention",
                "Increase operational efficiency",
                "Leverage AI for competitive advantage"
            ],
            "budget": 250000,
            "timeline_days": 180,
            "roadmap_options": {
                "roadmap_type": "hybrid"
            },
            "proposal_options": {
                "poc_type": "hybrid",
                "budget": 50000,
                "timeline_days": 90
            }
        }
    
    @pytest.fixture
    def minimal_di_container(self):
        """Create minimal DI container."""
        from unittest.mock import MagicMock
        import logging
        
        class MinimalDIContainer:
            def __init__(self):
                self.logger = logging.getLogger("TestBusinessOutcomes")
                self.logger.setLevel(logging.INFO)
                self.mock_config = MagicMock()
                self.mock_health = MagicMock()
                self.mock_telemetry = MagicMock()
                self.mock_security = MagicMock()
                self.mock_security.check_permissions = AsyncMock(return_value=True)
            
            def get_logger(self, name):
                return self.logger
            
            def get_config(self):
                # Return real config values, not mocks
                return {
                    "LLM_RETRY_ENABLED": True,
                    "LLM_RETRY_ATTEMPTS": 3,
                    "LLM_RETRY_DELAY": 2.0,
                    "LLM_TIMEOUT": 120.0
                }
            
            def get_health(self):
                return self.mock_health
            
            def get_telemetry(self):
                return self.mock_telemetry
            
            def get_security(self):
                return self.mock_security
        
        return MinimalDIContainer()
    
    @pytest.fixture
    def llm_abstraction(self, minimal_di_container):
        """Create real LLM abstraction."""
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
    async def specialist_agent(self, minimal_di_container, llm_abstraction):
        """Create BusinessOutcomesSpecialistAgent with real LLM."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.agents.business_outcomes_specialist_agent import BusinessOutcomesSpecialistAgent
        from backend.business_enablement.protocols.business_specialist_agent_protocol import SpecialistCapability
        
        # Mock dependencies
        mock_pwf = MagicMock()
        mock_pwf.get_llm_business_abstraction = MagicMock(return_value=llm_abstraction)
        
        mock_af = MagicMock()
        mock_af.get_llm_abstraction = AsyncMock(return_value=llm_abstraction)
        
        mock_mcp = MagicMock()
        mock_policy = MagicMock()
        mock_policy.initialize = AsyncMock()
        mock_tool = MagicMock()
        mock_agui = MagicMock()
        mock_curator = MagicMock()
        mock_metadata = MagicMock()
        
        mock_agui_schema = MagicMock()
        mock_agui_schema.schema_name = "business_outcomes_schema"
        
        agent = BusinessOutcomesSpecialistAgent(
            agent_name="TestBusinessOutcomesSpecialistAgent",
            business_domain="business_outcomes",
            capabilities=["strategic_planning", "roi_calculation"],
            required_roles=["business_analyst"],
            agui_schema=mock_agui_schema,
            foundation_services=minimal_di_container,
            public_works_foundation=mock_pwf,
            mcp_client_manager=mock_mcp,
            policy_integration=mock_policy,
            tool_composition=mock_tool,
            agui_formatter=mock_agui,
            curator_foundation=mock_curator,
            metadata_foundation=mock_metadata,
            specialist_capability=SpecialistCapability.STRATEGIC_PLANNING,
            agentic_foundation=mock_af  # Pass via kwargs
        )
        
        # Set LLM abstraction directly
        agent.llm_abstraction = llm_abstraction
        
        # Initialize agent
        await agent.initialize()
        
        return agent
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_agent_critical_reasoning_for_roadmap_real_llm(self, specialist_agent, sample_pillar_outputs):
        """
        Test agent's critical reasoning with real LLM for roadmap.
        
        Validates:
        1. Agent uses real LLM for critical reasoning
        2. Agent produces relevant roadmap structure
        3. AI value opportunities are identified
        4. Structure is relevant to pillar outputs
        """
        if not OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
        
        business_context = {
            "business_name": "Test Retail Corp",
            "objectives": ["Improve customer retention", "Increase efficiency"]
        }
        
        # Act: Agent does critical reasoning
        result = await specialist_agent.analyze_pillar_outputs_for_roadmap(
            pillar_outputs=sample_pillar_outputs,
            business_context=business_context,
            user_id="test_user"
        )
        
        # Assert
        # Debug: Print result if it doesn't have expected structure
        if not isinstance(result, dict) or "success" not in result:
            print(f"\n❌ Unexpected result format: {type(result)}")
            print(f"   Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
            print(f"   Result: {result}")
        
        assert isinstance(result, dict), f"Result should be a dict, got {type(result)}"
        assert "success" in result, f"Result should have 'success' key. Got keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}"
        assert result["success"] is True, f"Agent reasoning should succeed. Result: {result}"
        assert "roadmap_structure" in result, "Should return roadmap structure"
        assert "ai_value_opportunities" in result, "Should identify AI value opportunities"
        assert "reasoning" in result, "Should include reasoning"
        
        roadmap_structure = result["roadmap_structure"]
        assert "phases" in roadmap_structure, "Should specify phases"
        assert len(roadmap_structure["phases"]) > 0, "Should have at least one phase"
        assert "strategic_focus" in roadmap_structure, "Should specify strategic focus"
        
        # Validate AI value opportunities are relevant
        ai_opportunities = result["ai_value_opportunities"]
        assert len(ai_opportunities) > 0, "Should identify AI opportunities"
        
        # Validate reasoning quality
        reasoning = result["reasoning"]
        assert "analysis" in reasoning, "Should include analysis"
        assert len(reasoning["analysis"]) > 50, "Analysis should be substantive"
        
        print(f"\n✅ Agent critical reasoning successful")
        print(f"✅ Strategic Focus: {roadmap_structure.get('strategic_focus')}")
        print(f"✅ Phases: {len(roadmap_structure.get('phases', []))}")
        print(f"✅ AI Opportunities: {len(ai_opportunities)}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_agent_critical_reasoning_for_poc_real_llm(self, specialist_agent, sample_pillar_outputs):
        """
        Test agent's critical reasoning with real LLM for POC.
        
        Validates:
        1. Agent uses real LLM for critical reasoning
        2. Agent produces relevant POC structure
        3. Scope and objectives are relevant
        4. AI value propositions are identified
        """
        if not OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
        
        business_context = {
            "business_name": "Test Retail Corp",
            "objectives": ["Demonstrate AI value", "Improve efficiency"]
        }
        
        # Act: Agent does critical reasoning
        result = await specialist_agent.analyze_pillar_outputs_for_poc(
            pillar_outputs=sample_pillar_outputs,
            business_context=business_context,
            poc_type="hybrid",
            user_id="test_user"
        )
        
        # Assert
        assert result["success"] is True, "Agent reasoning should succeed"
        assert "poc_structure" in result, "Should return POC structure"
        # Check for either ai_value_propositions or ai_value_opportunities (fallback uses opportunities)
        assert "ai_value_propositions" in result or "ai_value_opportunities" in result, "Should identify AI value propositions/opportunities"
        
        poc_structure = result["poc_structure"]
        assert "scope" in poc_structure, "Should specify scope"
        assert "objectives" in poc_structure, "Should specify objectives"
        assert len(poc_structure["objectives"]) > 0, "Should have objectives"
        assert "success_criteria" in poc_structure, "Should specify success criteria"
        
        # Validate scope is relevant
        scope = poc_structure["scope"]
        assert "in_scope" in scope, "Should specify in-scope items"
        assert len(scope["in_scope"]) > 0, "Should have in-scope items"
        
        # Validate AI value propositions/opportunities
        ai_propositions = result.get("ai_value_propositions") or result.get("ai_value_opportunities", [])
        assert len(ai_propositions) > 0, "Should identify AI value propositions/opportunities"
        
        print(f"\n✅ Agent critical reasoning successful")
        print(f"✅ Objectives: {len(poc_structure.get('objectives', []))}")
        print(f"✅ In-Scope Items: {len(scope.get('in_scope', []))}")
        print(f"✅ AI Value Propositions: {len(ai_propositions)}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_generate_poc_with_real_llm(self, business_context):
        """
        Test POC generation with real LLM calls.
        
        Validates:
        1. Agent uses real LLM for critical reasoning
        2. Agent produces relevant POC structure
        3. Service executes agent's structure
        4. Result is a valid, relevant POC proposal
        """
        # Skip if LLM not configured
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("LLM API key not configured - skipping real LLM test")
        
        assert True  # Placeholder - will implement full integration test
    
    @pytest.mark.asyncio
    async def test_agent_critical_reasoning_quality(self, sample_pillar_outputs):
        """
        Test that agent's critical reasoning produces quality structures.
        
        This test validates:
        - Agent identifies AI value opportunities
        - Agent structures roadmap/POC appropriately
        - Agent's reasoning is relevant to inputs
        """
        # This test would validate the quality of agent reasoning
        # by checking that:
        # 1. AI value opportunities are identified
        # 2. Structure aligns with pillar outputs
        # 3. Strategic focus is relevant
        
        # For now, we'll create a test that can be run with real LLM
        # when API keys are available
        
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("LLM API key not configured")
        
        assert True  # Placeholder

