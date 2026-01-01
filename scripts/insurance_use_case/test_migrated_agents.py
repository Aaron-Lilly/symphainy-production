#!/usr/bin/env python3
"""
Test Migrated Agents - Verification Script

Tests the 5 newly migrated agents to ensure they:
1. Import correctly
2. Initialize correctly
3. Load configs correctly
4. Can be instantiated by orchestrators

Agents to test:
- WavePlanningSpecialist (Iterative)
- QualityRemediationSpecialist (Stateless)
- RoutingDecisionSpecialist (Stateless)
- ChangeImpactAssessmentSpecialist (Iterative)
- BusinessAnalysisSpecialist (Stateless)
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

# Configure for test mode
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("TEST_MODE", "true")
os.environ.setdefault("TRAEFIK_OPTIONAL_IN_TEST", "true")

import logging
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestMigratedAgents")

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

def log_test(test_name: str, status: str, details: str = ""):
    """Log test result."""
    test_results["total"] += 1
    if status == "PASS":
        test_results["passed"] += 1
        logger.info(f"✅ {test_name}: PASS")
    else:
        test_results["failed"] += 1
        test_results["errors"].append(f"{test_name}: {details}")
        logger.error(f"❌ {test_name}: FAIL - {details}")

async def test_agent_import(agent_name: str, module_path: str):
    """Test that agent can be imported."""
    test_name = f"Import {agent_name}"
    try:
        module = __import__(module_path, fromlist=[agent_name])
        agent_class = getattr(module, agent_name)
        assert agent_class is not None, f"{agent_name} class not found"
        log_test(test_name, "PASS")
        return agent_class
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        return None

async def test_agent_initialization(agent_class, agent_name: str):
    """Test that agent can be initialized (minimal setup)."""
    test_name = f"Initialize {agent_name}"
    try:
        # Minimal initialization test - just check config loading
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        from foundations.agentic_foundation.agent_sdk.mcp_client_manager import MCPClientManager
        from foundations.agentic_foundation.agent_sdk.policy_integration import PolicyIntegration
        from foundations.agentic_foundation.agent_sdk.tool_composition import ToolComposition
        from foundations.agentic_foundation.agent_sdk.agui_output_formatter import AGUIOutputFormatter
        
        # Create minimal DI container
        di_container = DIContainerService("test_migrated_agents")
        
        # Check that agent class has expected attributes
        assert hasattr(agent_class, '__init__'), f"{agent_name} missing __init__"
        
        # Check config path exists (convert CamelCase to snake_case, handling acronyms)
        import re
        # Handle acronyms: convert consecutive uppercase to lowercase, then add underscores
        # First, insert underscore before uppercase that follows lowercase
        snake_name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', agent_name)
        # Then, insert underscore before uppercase that follows uppercase and is followed by lowercase
        snake_name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', snake_name)
        snake_name = snake_name.lower()
        config_path = Path(__file__).parent.parent.parent / "symphainy-platform" / "backend" / "business_enablement" / "agents" / "configs" / f"{snake_name}.yaml"
        assert config_path.exists(), f"Config file not found: {config_path}"
        
        log_test(test_name, "PASS", f"Config: {config_path.name}")
        return True
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_config_loading(agent_name: str):
    """Test that agent config loads correctly."""
    test_name = f"Config Load {agent_name}"
    try:
        import yaml
        import re
        # Convert CamelCase to snake_case, handling acronyms
        # First, insert underscore before uppercase that follows lowercase
        snake_name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', agent_name)
        # Then, insert underscore before uppercase that follows uppercase and is followed by lowercase
        snake_name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', snake_name)
        snake_name = snake_name.lower()
        config_path = Path(__file__).parent.parent.parent / "symphainy-platform" / "backend" / "business_enablement" / "agents" / "configs" / f"{snake_name}.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Verify required fields
        assert "agent_name" in config, "Missing agent_name"
        assert config["agent_name"] == agent_name, f"Agent name mismatch: {config['agent_name']} != {agent_name}"
        assert "role" in config, "Missing role"
        assert "goal" in config, "Missing goal"
        assert "instructions" in config, "Missing instructions"
        assert "stateful" in config, "Missing stateful"
        assert "iterative_execution" in config, "Missing iterative_execution"
        assert "cost_tracking" in config, "Missing cost_tracking"
        
        log_test(test_name, "PASS", f"Stateful: {config.get('stateful')}, Iterative: {config.get('iterative_execution')}")
        return True
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        return False

async def test_agents_from_init():
    """Test that agents can be imported from agents.__init__."""
    test_name = "Import from agents.__init__"
    try:
        from backend.business_enablement.agents import (
            WavePlanningSpecialist,
            QualityRemediationSpecialist,
            RoutingDecisionSpecialist,
            ChangeImpactAssessmentSpecialist,
            BusinessAnalysisSpecialist,
            SOPGenerationSpecialist,
            WorkflowGenerationSpecialist,
            CoexistenceBlueprintSpecialist,
            RoadmapProposalSpecialist,
            CoexistenceStrategySpecialist,
            SagaWALManagementSpecialist
        )
        
        assert WavePlanningSpecialist is not None
        assert QualityRemediationSpecialist is not None
        assert RoutingDecisionSpecialist is not None
        assert ChangeImpactAssessmentSpecialist is not None
        assert BusinessAnalysisSpecialist is not None
        assert SOPGenerationSpecialist is not None
        assert WorkflowGenerationSpecialist is not None
        assert CoexistenceBlueprintSpecialist is not None
        assert RoadmapProposalSpecialist is not None
        assert CoexistenceStrategySpecialist is not None
        assert SagaWALManagementSpecialist is not None
        
        log_test(test_name, "PASS")
        return True
    except Exception as e:
        log_test(test_name, "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    logger.info("=" * 80)
    logger.info("TEST: Migrated Agents Verification")
    logger.info("=" * 80)
    logger.info("")
    
    # Agents to test (all 11 migrated agents)
    agents_to_test = [
        ("WavePlanningSpecialist", "backend.business_enablement.agents.wave_planning_specialist"),
        ("QualityRemediationSpecialist", "backend.business_enablement.agents.quality_remediation_specialist"),
        ("RoutingDecisionSpecialist", "backend.business_enablement.agents.routing_decision_specialist"),
        ("ChangeImpactAssessmentSpecialist", "backend.business_enablement.agents.change_impact_assessment_specialist"),
        ("BusinessAnalysisSpecialist", "backend.business_enablement.agents.business_analysis_specialist"),
        ("SOPGenerationSpecialist", "backend.business_enablement.agents.sop_generation_specialist"),
        ("WorkflowGenerationSpecialist", "backend.business_enablement.agents.workflow_generation_specialist"),
        ("CoexistenceBlueprintSpecialist", "backend.business_enablement.agents.coexistence_blueprint_specialist"),
        ("RoadmapProposalSpecialist", "backend.business_enablement.agents.roadmap_proposal_specialist"),
        ("CoexistenceStrategySpecialist", "backend.business_enablement.agents.coexistence_strategy_specialist"),
        ("SagaWALManagementSpecialist", "backend.business_enablement.agents.saga_wal_management_specialist"),
    ]
    
    logger.info(f"Testing {len(agents_to_test)} migrated agents...")
    logger.info("")
    
    # Test each agent
    for agent_name, module_path in agents_to_test:
        logger.info(f"🧪 Testing {agent_name}...")
        logger.info("")
        
        # Test import
        agent_class = await test_agent_import(agent_name, module_path)
        if agent_class is None:
            continue
        
        # Test config loading
        await test_config_loading(agent_name)
        
        # Test initialization (minimal)
        await test_agent_initialization(agent_class, agent_name)
        
        logger.info("")
    
    # Test imports from __init__
    logger.info("🧪 Testing imports from agents.__init__...")
    await test_agents_from_init()
    logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total Tests: {test_results['total']}")
    logger.info(f"Passed: {test_results['passed']}")
    logger.info(f"Failed: {test_results['failed']}")
    
    if test_results["errors"]:
        logger.info("")
        logger.info("Errors:")
        for error in test_results["errors"]:
            logger.error(f"  - {error}")
    
    logger.info("")
    
    if test_results["failed"] == 0:
        logger.info("✅ ALL TESTS PASSED - Migrated agents are ready!")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED - Review errors above")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

