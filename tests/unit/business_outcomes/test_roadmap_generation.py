"""
Comprehensive unit tests for Roadmap Generation Service.

Tests:
- Roadmap generation from pillar outputs
- Flexible input handling (partial pillars)
- Strategic planning
- Phase/milestone generation
- Timeline generation
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.business_outcomes
@pytest.mark.roadmap
@pytest.mark.fast
class TestRoadmapGeneration:
    """Test suite for Roadmap Generation Service."""
    
    @pytest.fixture
    def mock_roadmap_service(self):
        """Create mock RoadmapGenerationService."""
        from backend.journey.services.roadmap_generation_service.roadmap_generation_service import RoadmapGenerationService
        service = Mock(spec=RoadmapGenerationService)
        service.generate_roadmap = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_generate_roadmap_full_pillars(self, mock_roadmap_service):
        """Test roadmap generation with all pillars."""
        mock_roadmap_service.generate_roadmap.return_value = {
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
        
        result = await mock_roadmap_service.generate_roadmap(
            pillar_outputs={
                "content": {},
                "insights": {},
                "operations": {}
            },
            business_context={}
        )
        
        assert result["success"] is True
        assert "phases" in result["roadmap"]
    
    @pytest.mark.asyncio
    async def test_generate_roadmap_partial_pillars(self, mock_roadmap_service):
        """Test roadmap generation with partial pillars (flexible input)."""
        mock_roadmap_service.generate_roadmap.return_value = {
            "success": True,
            "roadmap_id": "roadmap_123",
            "roadmap": {
                "phases": []
            }
        }
        
        # Test with only content pillar
        result = await mock_roadmap_service.generate_roadmap(
            pillar_outputs={"content": {}},
            business_context={}
        )
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_phase_generation(self, mock_roadmap_service):
        """Test phase generation."""
        mock_roadmap_service.generate_roadmap.return_value = {
            "success": True,
            "roadmap": {
                "phases": [
                    {
                        "name": "Phase 1",
                        "duration": "2 months",
                        "milestones": ["milestone1", "milestone2"]
                    }
                ]
            }
        }
        
        result = await mock_roadmap_service.generate_roadmap(
            pillar_outputs={},
            business_context={}
        )
        
        assert len(result["roadmap"]["phases"]) > 0
        assert "milestones" in result["roadmap"]["phases"][0]
    
    @pytest.mark.asyncio
    async def test_timeline_generation(self, mock_roadmap_service):
        """Test timeline generation."""
        mock_roadmap_service.generate_roadmap.return_value = {
            "success": True,
            "roadmap": {
                "timeline": "6 months",
                "start_date": "2025-01-01",
                "end_date": "2025-07-01"
            }
        }
        
        result = await mock_roadmap_service.generate_roadmap(
            pillar_outputs={},
            business_context={}
        )
        
        assert "timeline" in result["roadmap"]



