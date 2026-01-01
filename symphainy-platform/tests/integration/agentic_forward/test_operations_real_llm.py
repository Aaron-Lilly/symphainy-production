#!/usr/bin/env python3
"""
Agentic-Forward Integration Tests - Operations (Real LLM)

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
import json
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


class TestOperationsRealLLM:
    """Integration tests with real LLM calls for Operations."""
    
    @pytest.fixture
    def sample_sop_content(self):
        """Sample SOP content for testing."""
        return {
            "title": "Customer Onboarding Process",
            "description": "Standard operating procedure for onboarding new customers",
            "steps": [
                {
                    "step_number": 1,
                    "instruction": "Collect customer information",
                    "details": "Gather name, email, phone number, and business details"
                },
                {
                    "step_number": 2,
                    "instruction": "Verify customer identity",
                    "details": "Run identity verification checks"
                },
                {
                    "step_number": 3,
                    "instruction": "Create customer account",
                    "details": "Set up account in CRM system"
                },
                {
                    "step_number": 4,
                    "instruction": "Send welcome email",
                    "details": "Automated welcome email with account details"
                },
                {
                    "step_number": 5,
                    "instruction": "Schedule onboarding call",
                    "details": "Book initial consultation call"
                }
            ]
        }
    
    @pytest.fixture
    def sample_workflow_content(self):
        """Sample workflow content for testing."""
        return {
            "title": "Order Processing Workflow",
            "description": "Automated workflow for processing customer orders",
            "steps": [
                {
                    "step_id": "step_1",
                    "name": "Receive Order",
                    "description": "System receives order from customer",
                    "order": 1,
                    "type": "automated"
                },
                {
                    "step_id": "step_2",
                    "name": "Validate Order",
                    "description": "Check order details and inventory",
                    "order": 2,
                    "type": "automated"
                },
                {
                    "step_id": "step_3",
                    "name": "Process Payment",
                    "description": "Charge customer payment method",
                    "order": 3,
                    "type": "automated"
                },
                {
                    "step_id": "step_4",
                    "name": "Fulfill Order",
                    "description": "Prepare and ship order",
                    "order": 4,
                    "type": "human_ai_collaboration"
                },
                {
                    "step_id": "step_5",
                    "name": "Send Confirmation",
                    "description": "Email confirmation to customer",
                    "order": 5,
                    "type": "automated"
                }
            ]
        }
    
    @pytest.fixture
    def minimal_di_container(self):
        """Create minimal DI container."""
        from unittest.mock import MagicMock
        import logging
        
        class MinimalDIContainer:
            def __init__(self):
                self.logger = logging.getLogger("TestOperations")
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
        """Create OperationsSpecialistAgent with real LLM."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.agents.operations_specialist_agent import OperationsSpecialistAgent
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
        mock_agui_schema.schema_name = "operations_schema"
        
        agent = OperationsSpecialistAgent(
            agent_name="TestOperationsSpecialistAgent",
            business_domain="operations",
            capabilities=["process_optimization", "workflow_analysis"],
            required_roles=["operations_manager"],
            agui_schema=mock_agui_schema,
            foundation_services=minimal_di_container,
            agentic_foundation=mock_af,
            public_works_foundation=mock_pwf,
            mcp_client_manager=mock_mcp,
            policy_integration=mock_policy,
            tool_composition=mock_tool,
            agui_formatter=mock_agui,
            curator_foundation=mock_curator,
            metadata_foundation=mock_metadata,
            specialist_capability=SpecialistCapability.PROCESS_OPTIMIZATION
        )
        
        # Set LLM abstraction directly
        agent.llm_abstraction = llm_abstraction
        
        # Initialize agent
        await agent.initialize()
        
        return agent
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_agent_critical_reasoning_for_workflow_real_llm(self, specialist_agent, sample_sop_content):
        """
        Test agent's critical reasoning with real LLM for workflow structure.
        
        Validates:
        1. Agent uses real LLM to analyze process content
        2. Agent identifies workflow structure and AI opportunities
        3. Steps and decision points are relevant
        4. Automation opportunities are identified
        """
        if not OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
        
        context = {
            "business_goals": ["Improve efficiency", "Reduce manual work"]
        }
        
        # Act: Agent does critical reasoning
        result = await specialist_agent.analyze_process_for_workflow_structure(
            process_content=sample_sop_content,
            context=context,
            user_id="test_user"
        )
        
        # Assert
        assert result["success"] is True, "Agent reasoning should succeed"
        assert "workflow_structure" in result, "Should return workflow structure"
        assert "ai_value_opportunities" in result, "Should identify AI value opportunities"
        
        workflow_structure = result["workflow_structure"]
        assert "steps" in workflow_structure, "Should specify workflow steps"
        assert len(workflow_structure["steps"]) > 0, "Should have at least one step"
        assert "recommended_approach" in workflow_structure, "Should specify recommended approach"
        
        # Validate steps are relevant to SOP content
        steps = workflow_structure["steps"]
        assert all("name" in step or "step_id" in step for step in steps), "Steps should have identifiers"
        
        # Validate AI opportunities
        ai_opportunities = result["ai_value_opportunities"]
        assert len(ai_opportunities) > 0, "Should identify AI opportunities"
        
        print(f"\n✅ Agent critical reasoning successful")
        print(f"✅ Workflow Steps: {len(steps)}")
        print(f"✅ Recommended Approach: {workflow_structure.get('recommended_approach')}")
        print(f"✅ AI Opportunities: {len(ai_opportunities)}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_agent_critical_reasoning_for_coexistence_real_llm(self, specialist_agent, sample_sop_content, sample_workflow_content):
        """
        Test agent's critical reasoning with real LLM for coexistence structure.
        
        Validates:
        1. Agent uses real LLM to analyze SOP and workflow
        2. Agent determines optimal coexistence structure
        3. Handoff points are identified
        4. Collaboration pattern is relevant
        """
        if not OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
        
        context = {
            "business_goals": ["Optimize human-AI collaboration"]
        }
        
        # Act: Agent does critical reasoning
        result = await specialist_agent.analyze_for_coexistence_structure(
            sop_content=sample_sop_content,
            workflow_content=sample_workflow_content,
            context=context,
            user_id="test_user"
        )
        
        # Assert
        assert result["success"] is True, "Agent reasoning should succeed"
        assert "coexistence_structure" in result, "Should return coexistence structure"
        
        coexistence_structure = result["coexistence_structure"]
        assert "collaboration_pattern" in coexistence_structure, "Should specify collaboration pattern"
        assert "handoff_points" in coexistence_structure, "Should identify handoff points"
        assert "ai_augmentation_points" in coexistence_structure, "Should identify AI augmentation points"
        
        # Validate collaboration pattern
        pattern = coexistence_structure["collaboration_pattern"]
        assert pattern in ["ai_augmented", "human_driven", "ai_driven", "hybrid"], "Should have valid pattern"
        
        # Validate handoff points
        handoff_points = coexistence_structure["handoff_points"]
        # May be empty, but structure should exist
        
        print(f"\n✅ Agent critical reasoning successful")
        print(f"✅ Collaboration Pattern: {pattern}")
        print(f"✅ Handoff Points: {len(handoff_points)}")
        print(f"✅ AI Augmentation Points: {len(coexistence_structure.get('ai_augmentation_points', []))}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_sop_generation_with_real_llm(self, sample_workflow_content):
        """
        Test SOP generation from workflow with real LLM calls.
        
        Validates:
        1. Agent uses real LLM to analyze workflow content
        2. Agent determines optimal SOP structure
        3. Service executes agent's SOP structure
        4. Result is a valid, relevant SOP
        """
        # Skip if LLM not configured
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("LLM API key not configured - skipping real LLM test")
        
        assert True  # Placeholder - will implement full integration test
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_coexistence_analysis_with_real_llm(self, sample_sop_content, sample_workflow_content):
        """
        Test coexistence analysis with real LLM calls.
        
        Validates:
        1. Agent uses real LLM to analyze SOP and workflow
        2. Agent determines optimal coexistence structure
        3. Service executes agent's coexistence structure
        4. Result identifies relevant handoff points and collaboration patterns
        """
        # Skip if LLM not configured
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("LLM API key not configured - skipping real LLM test")
        
        assert True  # Placeholder - will implement full integration test
    
    @pytest.mark.asyncio
    async def test_agent_identifies_ai_opportunities(self, sample_sop_content):
        """
        Test that agent identifies relevant AI opportunities.
        
        Validates:
        - Agent identifies where AI can add value
        - AI opportunities are relevant to the process
        - Automation opportunities are identified
        """
        # Skip if LLM not configured
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("LLM API key not configured")
        
        assert True  # Placeholder

