#!/usr/bin/env python3
"""
Phase 1: Agentic Foundation Tests (Mocked)

Tests Agentic Foundation initialization, agent factory, and core capabilities.
All tests use mocked LLM to verify foundation and code structure.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))

pytestmark = [pytest.mark.integration]


@pytest.fixture
async def minimal_foundation_infrastructure():
    """
    Minimal infrastructure fixture for Agentic Foundation tests.
    
    Only initializes Public Works Foundation and Curator Foundation.
    Does not require Smart City services.
    """
    from foundations.di_container.di_container_service import DIContainerService
    from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
    from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
    
    # 1. Initialize DI Container
    di_container = DIContainerService("test_platform")
    
    # 2. Initialize Public Works Foundation
    pwf = PublicWorksFoundationService(di_container=di_container)
    
    try:
        pwf_result = await asyncio.wait_for(
            pwf.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        pytest.fail("Public Works Foundation initialization timed out after 30 seconds")
    
    if not pwf_result:
        pytest.fail("Public Works Foundation initialization failed")
    
    di_container.public_works_foundation = pwf
    
    # 3. Initialize Curator Foundation
    curator = CuratorFoundationService(
        foundation_services=di_container,
        public_works_foundation=pwf
    )
    
    try:
        curator_result = await asyncio.wait_for(
            curator.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        pytest.fail("Curator Foundation initialization timed out after 30 seconds")
    
    if not curator_result:
        pytest.fail("Curator Foundation initialization failed")
    
    di_container.curator_foundation = curator
    
    return {
        "di_container": di_container,
        "public_works_foundation": pwf,
        "curator": curator
    }


class TestAgenticFoundationInitialization:
    """Test Agentic Foundation service initialization."""
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_initializes(self, minimal_foundation_infrastructure):
        """Test that Agentic Foundation initializes correctly."""
        infra = minimal_foundation_infrastructure
        di_container = infra["di_container"]
        pwf = infra["public_works_foundation"]
        curator = infra["curator"]
        
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Initialize Agentic Foundation
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
        
        assert init_result is True, "Agentic Foundation should initialize successfully"
        assert agentic.is_initialized, "Agentic Foundation should be marked as initialized"
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_has_required_components(self, minimal_foundation_infrastructure):
        """Test that Agentic Foundation has all required components."""
        infra = minimal_foundation_infrastructure
        di_container = infra["di_container"]
        pwf = infra["public_works_foundation"]
        curator = infra["curator"]
        
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        agentic = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=pwf,
            curator_foundation=curator
        )
        await agentic.initialize()
        
        # Check required components
        assert hasattr(agentic, "agent_base"), "Should have AgentBase class"
        assert hasattr(agentic, "policy_integration"), "Should have PolicyIntegration"
        assert hasattr(agentic, "tool_composition"), "Should have ToolComposition"
        assert hasattr(agentic, "business_abstraction_helper"), "Should have BusinessAbstractionHelper"
        
        # Check agent types
        assert hasattr(agentic, "dimension_liaison_agent"), "Should have DimensionLiaisonAgent"
        assert hasattr(agentic, "dimension_specialist_agent"), "Should have DimensionSpecialistAgent"
        assert hasattr(agentic, "lightweight_llm_agent"), "Should have LightweightLLMAgent"
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_has_agent_factory(self, minimal_foundation_infrastructure):
        """Test that Agentic Foundation has agent factory method."""
        infra = minimal_foundation_infrastructure
        di_container = infra["di_container"]
        pwf = infra["public_works_foundation"]
        curator = infra["curator"]
        
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        agentic = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=pwf,
            curator_foundation=curator
        )
        await agentic.initialize()
        
        # Check factory method
        assert hasattr(agentic, "create_agent"), "Should have create_agent factory method"
        assert callable(agentic.create_agent), "create_agent should be callable"
        
        # Check agent tracking
        assert hasattr(agentic, "_agents"), "Should track created agents"
        assert isinstance(agentic._agents, dict), "Agent registry should be a dictionary"
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_integrates_with_public_works(self, minimal_foundation_infrastructure):
        """Test that Agentic Foundation integrates with Public Works Foundation."""
        infra = minimal_foundation_infrastructure
        di_container = infra["di_container"]
        pwf = infra["public_works_foundation"]
        curator = infra["curator"]
        
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        agentic = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=pwf,
            curator_foundation=curator
        )
        await agentic.initialize()
        
        # Check Public Works Foundation reference
        assert agentic.public_works_foundation is not None, "Should have Public Works Foundation reference"
        assert agentic.public_works_foundation == pwf, "Should use the same Public Works Foundation instance"
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_integrates_with_curator(self, minimal_foundation_infrastructure):
        """Test that Agentic Foundation integrates with Curator Foundation."""
        infra = minimal_foundation_infrastructure
        di_container = infra["di_container"]
        pwf = infra["public_works_foundation"]
        curator = infra["curator"]
        
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        agentic = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=pwf,
            curator_foundation=curator
        )
        await agentic.initialize()
        
        # Check Curator Foundation reference
        assert agentic.curator_foundation is not None, "Should have Curator Foundation reference"
        assert agentic.curator_foundation == curator, "Should use the same Curator Foundation instance"
        
        # Check agent registration method
        assert hasattr(agentic, "_register_agent_with_curator"), \
            "Should have method to register agents with Curator"


class TestAgenticFoundationHealth:
    """Test Agentic Foundation health and monitoring."""
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_health_check(self, minimal_foundation_infrastructure):
        """Test Agentic Foundation health check."""
        infra = minimal_foundation_infrastructure
        di_container = infra["di_container"]
        pwf = infra["public_works_foundation"]
        curator = infra["curator"]
        
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        agentic = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=pwf,
            curator_foundation=curator
        )
        await agentic.initialize()
        
        # Check health check method exists (may not be implemented yet)
        if hasattr(agentic, "health_check"):
            try:
                health = await agentic.health_check()
                # Health check may return None if not fully implemented
                if health is not None:
                    assert isinstance(health, dict), "Health check should return dictionary"
            except NotImplementedError:
                pytest.skip("health_check not fully implemented")
            except Exception as e:
                # Health check may fail if dependencies not available
                if "not available" in str(e).lower():
                    pytest.skip(f"Health check dependencies not available: {e}")
                else:
                    raise
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_agent_registry(self, minimal_foundation_infrastructure):
        """Test Agentic Foundation agent registry."""
        infra = minimal_foundation_infrastructure
        di_container = infra["di_container"]
        pwf = infra["public_works_foundation"]
        curator = infra["curator"]
        
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        agentic = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=pwf,
            curator_foundation=curator
        )
        await agentic.initialize()
        
        # Check agent registry
        assert hasattr(agentic, "_agents"), "Should have agent registry"
        assert isinstance(agentic._agents, dict), "Agent registry should be a dictionary"
        
        # Initially empty (agents created on demand)
        assert len(agentic._agents) == 0, "Agent registry should start empty"

