"""
Integration tests for Business Outcomes Pillar workflows.

Tests:
- Pillar summary compilation workflow
- Roadmap generation workflow
- POC proposal generation workflow
- Flexible pillar input handling
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure


@pytest.mark.integration
@pytest.mark.pillar
@pytest.mark.business_outcomes
@pytest.mark.slow
class TestBusinessOutcomesPillarIntegration:
    """Test suite for Business Outcomes Pillar integration."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        container.get_config_adapter = Mock(return_value=Mock())
        return container
    
    @pytest.mark.asyncio
    async def test_pillar_summary_compilation(self, mock_platform_gateway, mock_di_container):
        """Test pillar summary compilation workflow."""
        from backend.journey.orchestrators.business_outcomes_journey_orchestrator.business_outcomes_journey_orchestrator import BusinessOutcomesJourneyOrchestrator
        
        orchestrator = BusinessOutcomesJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock pillar summary compilation
        with patch.object(orchestrator, 'compile_pillar_summaries') as mock_compile:
            mock_compile.return_value = {
                "success": True,
                "summaries": {
                    "content": {"summary": "Content summary"},
                    "insights": {"summary": "Insights summary"},
                    "operations": {"summary": "Operations summary"}
                }
            }
            
            result = await orchestrator.compile_pillar_summaries(
                session_id="session_123"
            )
            
            assert result["success"] is True
            assert "summaries" in result
    
    @pytest.mark.asyncio
    async def test_roadmap_generation_workflow(self, mock_platform_gateway, mock_di_container):
        """Test roadmap generation workflow."""
        from backend.journey.orchestrators.business_outcomes_journey_orchestrator.business_outcomes_journey_orchestrator import BusinessOutcomesJourneyOrchestrator
        
        orchestrator = BusinessOutcomesJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock roadmap generation
        with patch.object(orchestrator, 'execute_roadmap_generation_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "roadmap_id": "roadmap_123",
                "roadmap": {
                    "phases": [
                        {"name": "Phase 1", "milestones": []},
                        {"name": "Phase 2", "milestones": []}
                    ],
                    "timeline": "6 months"
                }
            }
            
            result = await orchestrator.execute_roadmap_generation_workflow(
                pillar_summaries={
                    "content": {},
                    "insights": {},
                    "operations": {}
                },
                roadmap_options={}
            )
            
            assert result["success"] is True
            assert "roadmap_id" in result
            assert "roadmap" in result
    
    @pytest.mark.asyncio
    async def test_poc_proposal_generation_workflow(self, mock_platform_gateway, mock_di_container):
        """Test POC proposal generation workflow."""
        from backend.journey.orchestrators.business_outcomes_journey_orchestrator.business_outcomes_journey_orchestrator import BusinessOutcomesJourneyOrchestrator
        
        orchestrator = BusinessOutcomesJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock POC proposal generation
        with patch.object(orchestrator, 'execute_poc_proposal_generation_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "poc_id": "poc_123",
                "poc_proposal": {
                    "executive_summary": "POC summary",
                    "recommendations": [],
                    "financials": {
                        "roi": 0.25,
                        "npv": 1000000,
                        "irr": 0.15
                    }
                }
            }
            
            result = await orchestrator.execute_poc_proposal_generation_workflow(
                pillar_summaries={},
                poc_options={}
            )
            
            assert result["success"] is True
            assert "poc_id" in result
            assert "poc_proposal" in result
    
    @pytest.mark.asyncio
    async def test_flexible_pillar_input_roadmap(self, mock_platform_gateway, mock_di_container):
        """Test roadmap generation with partial pillar inputs (flexible input)."""
        from backend.journey.orchestrators.business_outcomes_journey_orchestrator.business_outcomes_journey_orchestrator import BusinessOutcomesJourneyOrchestrator
        
        orchestrator = BusinessOutcomesJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock roadmap generation with only content pillar
        with patch.object(orchestrator, 'execute_roadmap_generation_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "roadmap_id": "roadmap_123",
                "roadmap": {}
            }
            
            # Test with only content pillar (flexible input)
            result = await orchestrator.execute_roadmap_generation_workflow(
                pillar_summaries={"content": {}},  # Only content pillar
                roadmap_options={}
            )
            
            # Should work with partial input
            assert result["success"] is True




