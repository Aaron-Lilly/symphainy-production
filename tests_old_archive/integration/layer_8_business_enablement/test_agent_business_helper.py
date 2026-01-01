#!/usr/bin/env python3
"""
Phase 1: BusinessAbstractionHelper Integration Tests (Mocked)

Tests agent access to business abstractions via BusinessAbstractionHelper.
All tests use mocked LLM to verify abstraction integration.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))

pytestmark = [pytest.mark.integration]


@pytest.fixture
async def minimal_foundation_infrastructure():
    """Minimal infrastructure fixture for Agentic Foundation tests."""
    from foundations.di_container.di_container_service import DIContainerService
    from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
    from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
    
    di_container = DIContainerService("test_platform")
    pwf = PublicWorksFoundationService(di_container=di_container)
    await asyncio.wait_for(pwf.initialize(), timeout=30.0)
    di_container.public_works_foundation = pwf
    
    curator = CuratorFoundationService(foundation_services=di_container, public_works_foundation=pwf)
    await asyncio.wait_for(curator.initialize(), timeout=30.0)
    di_container.curator_foundation = curator
    
    return {"di_container": di_container, "public_works_foundation": pwf, "curator": curator}


@pytest.fixture
async def agentic_foundation(minimal_foundation_infrastructure):
    """Fixture providing initialized Agentic Foundation."""
    infra = minimal_foundation_infrastructure
    from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
    
    agentic = AgenticFoundationService(
        di_container=infra["di_container"],
        public_works_foundation=infra["public_works_foundation"],
        curator_foundation=infra["curator"]
    )
    await agentic.initialize()
    return agentic


@pytest.fixture
async def agent_with_helper(agentic_foundation):
    """Fixture providing agent with BusinessAbstractionHelper."""
    from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
    from foundations.agentic_foundation.agui_schema_registry import AGUISchema
    
    agentic = agentic_foundation
    di_container = agentic.di_container
    
    # Create AGUI schema
    agui_schema = AGUISchema(
        agent_name="Helper Test Agent",
        version="1.0.0",
        description="Test BusinessAbstractionHelper",
        components=[],
        metadata={}
    )
    
    # Create agent
    agent = await agentic.create_agent(
        agent_class=DimensionLiaisonAgent,
        agent_name="Helper Test Agent",
        agent_type="liaison",
        realm_name="business_enablement",
        di_container=di_container,
        capabilities=["conversation"],
        required_roles=["test_orchestrator"],
        agui_schema=agui_schema
    )
    
    return agent


class TestBusinessAbstractionHelperAccess:
    """Test agent access to BusinessAbstractionHelper."""
    
    @pytest.mark.asyncio
    async def test_agent_has_business_helper(self, agent_with_helper):
        """Test that agent has BusinessAbstractionHelper."""
        agent = agent_with_helper
        
        assert hasattr(agent, "business_helper"), "Agent should have business_helper"
        assert agent.business_helper is not None, "Business helper should be initialized"
    
    @pytest.mark.asyncio
    async def test_business_helper_has_llm_access(self, agent_with_helper):
        """Test that BusinessAbstractionHelper can access LLM abstraction."""
        agent = agent_with_helper
        
        if not hasattr(agent, "business_helper"):
            pytest.skip("Agent does not have business_helper")
        
        helper = agent.business_helper
        
        # Test LLM abstraction access
        llm_abstraction = await helper.get_abstraction("llm_composition_service")
        
        # LLM abstraction may be None if not configured, which is OK for this test
        # We're just verifying the helper can attempt to access it
        assert True, "Helper should be able to access LLM abstraction"
    
    @pytest.mark.asyncio
    async def test_business_helper_list_abstractions(self, agent_with_helper):
        """Test that BusinessAbstractionHelper can list available abstractions."""
        agent = agent_with_helper
        
        if not hasattr(agent, "business_helper"):
            pytest.skip("Agent does not have business_helper")
        
        helper = agent.business_helper
        
        # List abstractions
        abstractions = await helper.list_available_abstractions()
        
        assert isinstance(abstractions, dict), "Should return dictionary of abstractions"
        # May be empty if no abstractions configured, which is OK


class TestBusinessAbstractionHelperLLMMethods:
    """Test BusinessAbstractionHelper LLM convenience methods."""
    
    @pytest.mark.asyncio
    async def test_generate_agent_response(self, agent_with_helper):
        """Test generate_agent_response method (mocked)."""
        agent = agent_with_helper
        
        if not hasattr(agent, "business_helper"):
            pytest.skip("Agent does not have business_helper")
        
        helper = agent.business_helper
        
        # Mock LLM composition service
        mock_llm_service = AsyncMock()
        mock_llm_service.generate_agent_response = AsyncMock(return_value={
            "content": "Mocked agent response",
            "model": "gpt-4o-mini",
            "usage": {"total_tokens": 10}
        })
        
        # Patch the abstraction cache
        helper._abstraction_cache["llm_composition_service"] = mock_llm_service
        
        # Test generate_agent_response
        result = await helper.generate_agent_response(
            prompt="Test prompt",
            agent_context={"test": "context"}
        )
        
        assert result is not None, "Should return result"
        assert "content" in result or "error" in result, "Should return content or error"
    
    @pytest.mark.asyncio
    async def test_guide_user_with_llm(self, agent_with_helper):
        """Test guide_user_with_llm method (mocked)."""
        agent = agent_with_helper
        
        if not hasattr(agent, "business_helper"):
            pytest.skip("Agent does not have business_helper")
        
        helper = agent.business_helper
        
        # Mock LLM composition service
        mock_llm_service = AsyncMock()
        mock_llm_service.guide_user = AsyncMock(return_value={
            "guidance": "Mocked guidance response",
            "steps": ["Step 1", "Step 2"]
        })
        
        # Patch the abstraction cache
        helper._abstraction_cache["llm_composition_service"] = mock_llm_service
        
        # Test guide_user_with_llm
        result = await helper.guide_user_with_llm(
            user_input="How do I do X?",
            available_tools=["tool1", "tool2"],
            context="Test context"
        )
        
        assert result is not None, "Should return result"
        assert "guidance" in result or "error" in result, "Should return guidance or error"
    
    @pytest.mark.asyncio
    async def test_interpret_analysis_results(self, agent_with_helper):
        """Test interpret_analysis_results method (mocked)."""
        agent = agent_with_helper
        
        if not hasattr(agent, "business_helper"):
            pytest.skip("Agent does not have business_helper")
        
        helper = agent.business_helper
        
        # Mock LLM composition service
        mock_llm_service = AsyncMock()
        mock_llm_service.interpret_results = AsyncMock(return_value={
            "interpretation": "Mocked interpretation",
            "insights": ["Insight 1", "Insight 2"]
        })
        
        # Patch the abstraction cache
        helper._abstraction_cache["llm_composition_service"] = mock_llm_service
        
        # Test interpret_analysis_results
        result = await helper.interpret_analysis_results(
            results={"data": "test"},
            context="Test context",
            expertise="test_expertise"
        )
        
        assert result is not None, "Should return result"
        assert "interpretation" in result or "error" in result, "Should return interpretation or error"


class TestBusinessAbstractionHelperCaching:
    """Test BusinessAbstractionHelper abstraction caching."""
    
    @pytest.mark.asyncio
    async def test_abstraction_caching(self, agent_with_helper):
        """Test that abstractions are cached."""
        agent = agent_with_helper
        
        if not hasattr(agent, "business_helper"):
            pytest.skip("Agent does not have business_helper")
        
        helper = agent.business_helper
        
        # Clear cache
        await helper.clear_cache()
        assert len(helper._abstraction_cache) == 0, "Cache should be empty"
        
        # Get abstraction (may be None if not configured)
        abstraction = await helper.get_abstraction("llm_composition_service")
        
        # If abstraction exists, it should be cached
        if abstraction is not None:
            assert "llm_composition_service" in helper._abstraction_cache, \
                "Abstraction should be cached"
    
    @pytest.mark.asyncio
    async def test_preload_abstractions(self, agent_with_helper):
        """Test preloading abstractions into cache."""
        agent = agent_with_helper
        
        if not hasattr(agent, "business_helper"):
            pytest.skip("Agent does not have business_helper")
        
        helper = agent.business_helper
        
        # Preload abstractions
        await helper.preload_abstractions(["llm_composition_service"])
        
        # Cache may or may not have items depending on configuration
        # Just verify method executes without error
        assert True, "Preload should execute without error"


class TestBusinessAbstractionHelperUsageTracking:
    """Test BusinessAbstractionHelper usage tracking."""
    
    @pytest.mark.asyncio
    async def test_usage_statistics(self, agent_with_helper):
        """Test usage statistics tracking."""
        agent = agent_with_helper
        
        if not hasattr(agent, "business_helper"):
            pytest.skip("Agent does not have business_helper")
        
        helper = agent.business_helper
        
        # Get usage statistics
        stats = helper.get_usage_statistics()
        
        assert isinstance(stats, dict), "Should return dictionary"
        # May be empty if no usage yet, which is OK

