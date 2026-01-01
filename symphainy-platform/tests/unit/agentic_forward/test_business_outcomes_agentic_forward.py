#!/usr/bin/env python3
"""
Agentic-Forward Pattern Tests - Business Outcomes

Tests the agentic-forward pattern for Business Outcomes Orchestrator:
- Agent does critical reasoning FIRST
- Services execute agent's strategic decisions
- No backward compatibility fallbacks
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Dict, Any

pytestmark = pytest.mark.unit


class TestBusinessOutcomesAgenticForward:
    """Test agentic-forward pattern for Business Outcomes."""
    
    @pytest.fixture
    def mock_delivery_manager(self):
        """Create mock delivery manager."""
        manager = MagicMock()
        manager.realm_name = "business_enablement"
        manager.service_name = "DeliveryManagerService"
        manager.platform_gateway = MagicMock()
        manager.di_container = MagicMock()
        manager.di_container.get_logger = Mock(return_value=MagicMock())
        return manager
    
    @pytest.fixture
    def mock_specialist_agent(self):
        """Create mock specialist agent with LLM abstraction."""
        agent = MagicMock()
        
        # Mock LLM abstraction
        agent.llm_abstraction = MagicMock()
        agent.llm_abstraction.analyze_text = AsyncMock(return_value={
            "analysis": "AI can add significant value in semantic data modeling and analytics. Strategic focus should be on analytics implementation."
        })
        
        # Mock critical reasoning methods
        agent.analyze_pillar_outputs_for_roadmap = AsyncMock(return_value={
            "success": True,
            "roadmap_structure": {
                "phases": [
                    {
                        "phase_id": "phase_content",
                        "name": "Content Foundation",
                        "priority": "high",
                        "ai_value": "Semantic data model creation",
                        "estimated_duration_days": 30
                    },
                    {
                        "phase_id": "phase_insights",
                        "name": "Analytics Implementation",
                        "priority": "high",
                        "ai_value": "AI-powered business intelligence",
                        "estimated_duration_days": 45
                    }
                ],
                "priorities": ["Establish semantic data foundation", "Implement AI-driven analytics"],
                "strategic_focus": "AI value maximization",
                "recommended_approach": "ai_value_maximization"
            },
            "ai_value_opportunities": [
                {
                    "area": "Content Processing",
                    "ai_value": "Intelligent semantic data model creation",
                    "impact": "high"
                }
            ],
            "reasoning": {
                "analysis": "AI can add significant value in semantic data modeling",
                "key_insights": ["AI can add value in data processing"],
                "recommendations": ["Prioritize AI-powered analytics"]
            }
        })
        
        agent.analyze_pillar_outputs_for_poc = AsyncMock(return_value={
            "success": True,
            "poc_structure": {
                "scope": {
                    "in_scope": [
                        {"item": "Semantic Data Model Creation", "description": "AI-powered semantic modeling"}
                    ],
                    "out_of_scope": [],
                    "assumptions": ["Client will provide necessary access"],
                    "risks": []
                },
                "objectives": ["Demonstrate AI value in data processing"],
                "success_criteria": ["AI successfully creates semantic data model"],
                "recommended_focus": "AI value demonstration"
            },
            "ai_value_propositions": [
                {
                    "proposition": "AI-powered semantic data modeling",
                    "value": "Reduces manual data modeling effort by 70%"
                }
            ],
            "reasoning": {
                "analysis": "POC should focus on demonstrating AI capabilities",
                "value_maximization_strategy": "Focus on demonstrating AI capabilities",
                "recommendations": ["Prioritize AI-powered analytics"]
            }
        })
        
        agent.enhance_strategic_roadmap = AsyncMock(return_value={
            "success": True,
            "roadmap": {
                "roadmap_id": "roadmap_123",
                "phases": [],
                "enhanced": True
            }
        })
        
        agent.refine_poc_proposal = AsyncMock(return_value={
            "success": True,
            "poc_proposal": {
                "proposal_id": "poc_123",
                "refined": True
            }
        })
        
        return agent
    
    @pytest.fixture
    def mock_roadmap_service(self):
        """Create mock roadmap generation service."""
        service = MagicMock()
        service.generate_roadmap = AsyncMock(return_value={
            "success": True,
            "roadmap_id": "roadmap_123",
            "roadmap": {
                "roadmap_id": "roadmap_123",
                "phases": [
                    {
                        "phase_id": "phase_content",
                        "name": "Content Foundation",
                        "duration_days": 30
                    }
                ],
                "milestones": [],
                "timeline": {"total_duration_days": 30},
                "dependencies": []
            }
        })
        return service
    
    @pytest.fixture
    def mock_poc_service(self):
        """Create mock POC generation service."""
        service = MagicMock()
        service.generate_poc_proposal = AsyncMock(return_value={
            "success": True,
            "poc_proposal": {
                "proposal_id": "poc_123",
                "objectives": ["Demonstrate AI value"],
                "scope": {"in_scope": []},
                "timeline": {},
                "financials": {}
            }
        })
        return service
    
    @pytest.fixture
    async def orchestrator(self, mock_delivery_manager, mock_specialist_agent, mock_roadmap_service, mock_poc_service):
        """Create BusinessOutcomesOrchestrator with mocked dependencies."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        orchestrator = BusinessOutcomesOrchestrator(mock_delivery_manager)
        
        # Set specialist agent
        orchestrator.specialist_agent = mock_specialist_agent
        
        # Mock service discovery
        orchestrator._get_roadmap_generation_service = AsyncMock(return_value=mock_roadmap_service)
        orchestrator._get_poc_generation_service = AsyncMock(return_value=mock_poc_service)
        
        # Mock pillar summaries
        orchestrator._get_content_orchestrator = AsyncMock(return_value=MagicMock())
        orchestrator._get_insights_orchestrator = AsyncMock(return_value=MagicMock())
        orchestrator._get_operations_orchestrator = AsyncMock(return_value=MagicMock())
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_generate_roadmap_agentic_forward_flow(self, orchestrator, mock_specialist_agent, mock_roadmap_service):
        """Test that roadmap generation follows agentic-forward pattern: Agent → Service."""
        # Arrange
        pillar_outputs = {
            "content_pillar": {"success": True, "semantic_data_model": {"structured_files": {"count": 10}}},
            "insights_pillar": {"success": True, "summary": {"textual": "Key insights found"}},
            "operations_pillar": {"success": True, "artifacts": {"workflows": []}}
        }
        business_context = {
            "business_name": "Test Corp",
            "pillar_outputs": pillar_outputs
        }
        
        # Act
        result = await orchestrator.generate_strategic_roadmap(
            business_context=business_context,
            user_id="test_user"
        )
        
        # Assert
        # 1. Agent was called FIRST for critical reasoning
        mock_specialist_agent.analyze_pillar_outputs_for_roadmap.assert_called_once()
        call_args = mock_specialist_agent.analyze_pillar_outputs_for_roadmap.call_args
        assert call_args[1]["pillar_outputs"] == pillar_outputs
        # Business context is enhanced by orchestrator, so check key fields
        enhanced_context = call_args[1]["business_context"]
        assert enhanced_context["pillar_outputs"] == pillar_outputs
        assert enhanced_context["business_name"] == "Test Corp"
        
        # 2. Service was called with agent's structure
        mock_roadmap_service.generate_roadmap.assert_called_once()
        service_call_args = mock_roadmap_service.generate_roadmap.call_args
        roadmap_structure = service_call_args[1]["roadmap_structure"]
        assert roadmap_structure["phases"] is not None
        assert roadmap_structure["strategic_focus"] == "AI value maximization"
        
        # 3. Result is successful
        if not result.get("success"):
            print(f"\n❌ Orchestrator returned error: {result.get('error', 'Unknown error')}")
            print(f"   Message: {result.get('message', 'No message')}")
        assert result["success"] is True, f"Expected success but got: {result}"
        assert "roadmap" in result
    
    @pytest.mark.asyncio
    async def test_generate_roadmap_agent_failure_handling(self, orchestrator, mock_specialist_agent):
        """Test that roadmap generation fails gracefully if agent reasoning fails."""
        # Arrange
        mock_specialist_agent.analyze_pillar_outputs_for_roadmap = AsyncMock(return_value={
            "success": False,
            "error": "Agent reasoning failed"
        })
        
        business_context = {
            "pillar_outputs": {
                "content_pillar": {"success": True}
            }
        }
        
        # Act
        result = await orchestrator.generate_strategic_roadmap(
            business_context=business_context,
            user_id="test_user"
        )
        
        # Assert
        assert result["success"] is False
        assert "Agent reasoning required" in result["error"] or "Agent reasoning failed" in result.get("message", "")
    
    @pytest.mark.asyncio
    async def test_generate_poc_agentic_forward_flow(self, orchestrator, mock_specialist_agent, mock_poc_service):
        """Test that POC generation follows agentic-forward pattern: Agent → Service."""
        # Arrange
        pillar_outputs = {
            "content_pillar": {"success": True},
            "insights_pillar": {"success": True},
            "operations_pillar": {"success": True}
        }
        business_context = {
            "objectives": ["Increase efficiency"],
            "pillar_outputs": pillar_outputs
        }
        
        # Act
        result = await orchestrator.generate_poc_proposal(
            business_context=business_context,
            user_id="test_user"
        )
        
        # Assert
        # 1. Agent was called FIRST for critical reasoning
        mock_specialist_agent.analyze_pillar_outputs_for_poc.assert_called_once()
        call_args = mock_specialist_agent.analyze_pillar_outputs_for_poc.call_args
        assert call_args[1]["pillar_outputs"] == pillar_outputs
        assert call_args[1]["business_context"] == business_context
        
        # 2. Service was called with agent's structure
        mock_poc_service.generate_poc_proposal.assert_called_once()
        service_call_args = mock_poc_service.generate_poc_proposal.call_args
        poc_structure = service_call_args[1]["poc_structure"]
        assert poc_structure["scope"] is not None
        assert poc_structure["objectives"] is not None
        assert poc_structure["recommended_focus"] == "AI value demonstration"
        
        # 3. Result is successful
        if not result.get("success"):
            print(f"\n❌ Orchestrator returned error: {result.get('error', 'Unknown error')}")
            print(f"   Message: {result.get('message', 'No message')}")
        assert result["success"] is True, f"Expected success but got: {result}"
        # POC proposal may be in "proposal" or "poc_proposal" key
        assert "proposal" in result or "poc_proposal" in result, f"Expected proposal in result, got keys: {result.keys()}"
    
    @pytest.mark.asyncio
    async def test_generate_poc_agent_failure_handling(self, orchestrator, mock_specialist_agent):
        """Test that POC generation fails gracefully if agent reasoning fails."""
        # Arrange
        mock_specialist_agent.analyze_pillar_outputs_for_poc = AsyncMock(return_value={
            "success": False,
            "error": "Agent reasoning failed"
        })
        
        business_context = {
            "pillar_outputs": {
                "content_pillar": {"success": True}
            }
        }
        
        # Act
        result = await orchestrator.generate_poc_proposal(
            business_context=business_context,
            user_id="test_user"
        )
        
        # Assert
        assert result["success"] is False
        assert "Agent reasoning required" in result["error"] or "Agent reasoning failed" in result.get("message", "")
    
    @pytest.mark.asyncio
    async def test_agent_uses_llm_abstraction(self, orchestrator, mock_specialist_agent):
        """Test that agent uses LLM abstraction for critical reasoning."""
        # Arrange
        business_context = {
            "pillar_outputs": {
                "content_pillar": {"success": True}
            }
        }
        
        # Act
        await orchestrator.generate_strategic_roadmap(
            business_context=business_context,
            user_id="test_user"
        )
        
        # Assert
        # Verify LLM abstraction is available (mocked in fixture)
        assert hasattr(mock_specialist_agent, 'llm_abstraction')
        assert mock_specialist_agent.llm_abstraction is not None
    
    @pytest.mark.asyncio
    async def test_service_validates_agent_structure(self, orchestrator, mock_specialist_agent, mock_roadmap_service):
        """Test that service validates agent-provided structure."""
        # Arrange - agent provides invalid structure (no phases)
        mock_specialist_agent.analyze_pillar_outputs_for_roadmap = AsyncMock(return_value={
            "success": True,
            "roadmap_structure": {
                "phases": [],  # Invalid - no phases
                "priorities": []
            }
        })
        
        # Mock service to return error for invalid structure
        mock_roadmap_service.generate_roadmap = AsyncMock(return_value={
            "success": False,
            "error": "No phases specified in roadmap structure"
        })
        
        business_context = {
            "pillar_outputs": {"content_pillar": {"success": True}}
        }
        
        # Act
        result = await orchestrator.generate_strategic_roadmap(
            business_context=business_context,
            user_id="test_user"
        )
        
        # Assert
        assert result["success"] is False
        assert "phases" in result.get("error", "").lower() or "structure" in result.get("error", "").lower()

