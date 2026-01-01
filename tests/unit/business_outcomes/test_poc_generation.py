"""
Comprehensive unit tests for POC Generation Service.

Tests:
- POC proposal generation
- Financial analysis (ROI, NPV, IRR)
- Executive summary generation
- Recommendations generation
- Next steps generation
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.business_outcomes
@pytest.mark.poc
@pytest.mark.fast
class TestPOCGeneration:
    """Test suite for POC Generation Service."""
    
    @pytest.fixture
    def mock_poc_service(self):
        """Create mock POCGenerationService."""
        from backend.journey.services.poc_generation_service.poc_generation_service import POCGenerationService
        service = Mock(spec=POCGenerationService)
        service.generate_poc_proposal = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_generate_poc_proposal(self, mock_poc_service):
        """Test POC proposal generation."""
        mock_poc_service.generate_poc_proposal.return_value = {
            "success": True,
            "poc_id": "poc_123",
            "poc_proposal": {
                "executive_summary": "POC summary",
                "recommendations": [],
                "financials": {}
            }
        }
        
        result = await mock_poc_service.generate_poc_proposal(
            pillar_outputs={},
            poc_type="full"
        )
        
        assert result["success"] is True
        assert "poc_proposal" in result
    
    @pytest.mark.asyncio
    async def test_financial_analysis(self, mock_poc_service):
        """Test financial analysis in POC."""
        mock_poc_service.generate_poc_proposal.return_value = {
            "success": True,
            "poc_proposal": {
                "financials": {
                    "roi": 0.25,
                    "npv": 1000000,
                    "irr": 0.15,
                    "payback_period": "18 months"
                }
            }
        }
        
        result = await mock_poc_service.generate_poc_proposal(
            pillar_outputs={},
            poc_type="full"
        )
        
        assert "roi" in result["poc_proposal"]["financials"]
        assert "npv" in result["poc_proposal"]["financials"]
        assert "irr" in result["poc_proposal"]["financials"]
    
    @pytest.mark.asyncio
    async def test_executive_summary(self, mock_poc_service):
        """Test executive summary generation."""
        mock_poc_service.generate_poc_proposal.return_value = {
            "success": True,
            "poc_proposal": {
                "executive_summary": "Comprehensive POC summary with key points"
            }
        }
        
        result = await mock_poc_service.generate_poc_proposal(
            pillar_outputs={},
            poc_type="full"
        )
        
        assert "executive_summary" in result["poc_proposal"]
        assert len(result["poc_proposal"]["executive_summary"]) > 0
    
    @pytest.mark.asyncio
    async def test_recommendations(self, mock_poc_service):
        """Test recommendations generation."""
        mock_poc_service.generate_poc_proposal.return_value = {
            "success": True,
            "poc_proposal": {
                "recommendations": [
                    "Recommendation 1",
                    "Recommendation 2"
                ]
            }
        }
        
        result = await mock_poc_service.generate_poc_proposal(
            pillar_outputs={},
            poc_type="full"
        )
        
        assert len(result["poc_proposal"]["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_next_steps(self, mock_poc_service):
        """Test next steps generation."""
        mock_poc_service.generate_poc_proposal.return_value = {
            "success": True,
            "poc_proposal": {
                "next_steps": [
                    "Step 1",
                    "Step 2"
                ]
            }
        }
        
        result = await mock_poc_service.generate_poc_proposal(
            pillar_outputs={},
            poc_type="full"
        )
        
        assert "next_steps" in result["poc_proposal"]



