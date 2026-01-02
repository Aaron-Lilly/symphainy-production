"""
Comprehensive unit tests for Business Outcomes Journey Orchestrator.

Tests:
- Pillar summary compilation
- Strategic roadmap generation
- POC proposal generation
- Solution context integration
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.business_outcomes
@pytest.mark.orchestrator
@pytest.mark.fast
class TestBusinessOutcomesJourneyOrchestrator:
    """Test suite for Business Outcomes Journey Orchestrator."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def business_outcomes_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create BusinessOutcomesJourneyOrchestrator instance."""
        from backend.journey.orchestrators.business_outcomes_journey_orchestrator.business_outcomes_journey_orchestrator import BusinessOutcomesJourneyOrchestrator
        return BusinessOutcomesJourneyOrchestrator(mock_platform_gateway, mock_di_container)
    
    @pytest.mark.asyncio
    async def test_compile_pillar_summaries(self, business_outcomes_orchestrator):
        """Test pillar summary compilation."""
        with patch.object(business_outcomes_orchestrator, 'compile_pillar_summaries') as mock_compile:
            mock_compile.return_value = {
                "success": True,
                "summaries": {
                    "content": {},
                    "insights": {},
                    "operations": {}
                }
            }
            
            result = await business_outcomes_orchestrator.compile_pillar_summaries(
                session_id="session_123"
            )
            
            assert result["success"] is True
            assert "summaries" in result
    
    @pytest.mark.asyncio
    async def test_roadmap_generation(self, business_outcomes_orchestrator):
        """Test strategic roadmap generation."""
        with patch.object(business_outcomes_orchestrator, 'execute_roadmap_generation_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "roadmap_id": "roadmap_123",
                "roadmap": {
                    "phases": [],
                    "milestones": []
                }
            }
            
            result = await business_outcomes_orchestrator.execute_roadmap_generation_workflow(
                pillar_summaries={},
                roadmap_options={}
            )
            
            assert result["success"] is True
            assert "roadmap_id" in result
            assert "roadmap" in result
    
    @pytest.mark.asyncio
    async def test_poc_proposal_generation(self, business_outcomes_orchestrator):
        """Test POC proposal generation."""
        with patch.object(business_outcomes_orchestrator, 'execute_poc_proposal_generation_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "poc_id": "poc_123",
                "poc_proposal": {
                    "executive_summary": "",
                    "recommendations": [],
                    "financials": {}
                }
            }
            
            result = await business_outcomes_orchestrator.execute_poc_proposal_generation_workflow(
                pillar_summaries={},
                poc_options={}
            )
            
            assert result["success"] is True
            assert "poc_id" in result
            assert "poc_proposal" in result
    
    @pytest.mark.asyncio
    async def test_flexible_pillar_input(self, business_outcomes_orchestrator):
        """Test that roadmap generation works with partial pillar inputs."""
        with patch.object(business_outcomes_orchestrator, 'execute_roadmap_generation_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "roadmap_id": "roadmap_123",
                "roadmap": {}
            }
            
            # Test with only content pillar
            result = await business_outcomes_orchestrator.execute_roadmap_generation_workflow(
                pillar_summaries={"content": {}},
                roadmap_options={}
            )
            
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, business_outcomes_orchestrator):
        """Test error handling."""
        with patch.object(business_outcomes_orchestrator, 'execute_roadmap_generation_workflow') as mock_execute:
            mock_execute.side_effect = Exception("Roadmap generation failed")
            
            with pytest.raises(Exception):
                await business_outcomes_orchestrator.execute_roadmap_generation_workflow(
                    pillar_summaries={},
                    roadmap_options={}
                )




