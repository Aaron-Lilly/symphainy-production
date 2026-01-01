"""
Test Business Outcomes Orchestrator - POC Proposal Output

CRITICAL TEST: Validates that POC proposal outputs are impressive and complete,
not generic boilerplate. This is essential for CTO demo readiness.

Tests:
- POC proposal contains all required sections
- POC proposal is impressive (not generic)
- POC proposal includes financial analysis
- POC proposal integrates pillar outputs
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.critical
class TestBusinessOutcomesPOCOutput:
    """Test Business Outcomes Orchestrator POC proposal output quality."""
    
    @pytest.fixture
    async def orchestrator(self, real_platform_gateway):
        """Create Business Outcomes Orchestrator."""
        # TODO: Initialize orchestrator with real dependencies
        orchestrator = BusinessOutcomesOrchestrator(
            service_name="test_business_outcomes_orchestrator",
            realm_name="business_enablement",
            platform_gateway=real_platform_gateway,
            di_container=None  # TODO: Get from fixture
        )
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_poc_proposal_contains_required_sections(self, orchestrator):
        """Test that POC proposal contains all required sections."""
        business_context = {
            "pillar_outputs": {
                "content": {
                    "files": [{"name": "mission_data.csv", "type": "csv"}]
                },
                "insights": {
                    "summary": "Analysis reveals key opportunities for improvement"
                },
                "operations": {
                    "coexistence_blueprint": {
                        "future_state": "Automated system"
                    }
                }
            },
            "proposal_options": {
                "poc_type": "hybrid",
                "budget_range": "medium",
                "timeline_preference": "90_days"
            }
        }
        
        result = await orchestrator.generate_poc_proposal(business_context)
        
        # Validate structure
        assert result["success"] is True, f"POC proposal generation failed: {result.get('error', 'Unknown error')}"
        assert "proposal" in result, "Proposal missing from result"
        
        proposal = result["proposal"]
        
        # Validate required sections
        assert "executive_summary" in proposal, "Executive summary missing"
        assert "business_case" in proposal, "Business case missing"
        assert "poc_scope" in proposal, "POC scope missing"
        assert "timeline" in proposal, "Timeline missing"
        assert "budget" in proposal, "Budget missing"
        assert "success_metrics" in proposal, "Success metrics missing"
        assert "financial_analysis" in proposal, "Financial analysis missing"
    
    @pytest.mark.asyncio
    async def test_poc_proposal_is_impressive_not_generic(self, orchestrator):
        """Test that POC proposal is impressive and not generic boilerplate."""
        business_context = {
            "pillar_outputs": {
                "content": {
                    "files": [{"name": "insurance_claims.csv", "type": "csv"}]
                },
                "insights": {
                    "summary": "Insurance underwriting analysis shows risk patterns"
                },
                "operations": {
                    "coexistence_blueprint": {
                        "future_state": "AI-enhanced underwriting system"
                    }
                }
            },
            "proposal_options": {
                "poc_type": "hybrid",
                "budget_range": "medium",
                "timeline_preference": "90_days"
            }
        }
        
        result = await orchestrator.generate_poc_proposal(business_context)
        
        assert result["success"] is True
        proposal = result["proposal"]
        
        # Validate impressiveness
        executive_summary = proposal.get("executive_summary", "")
        assert len(executive_summary) > 800, f"Executive summary too short ({len(executive_summary)} chars). Should be > 800 words for impressive output."
        
        business_case = proposal.get("business_case", "")
        assert len(business_case) > 500, f"Business case too short ({len(business_case)} chars). Should be > 500 words."
        
        # Check for context-specific content (not generic)
        summary_lower = executive_summary.lower()
        context_indicators = ["insurance", "underwriting", "risk", "specific", "custom", "tailored", "unique"]
        has_context = any(indicator in summary_lower for indicator in context_indicators)
        assert has_context, f"POC proposal appears generic. Summary: {executive_summary[:200]}..."
        
        # Check for low generic word count (too many "the" suggests generic text)
        generic_word_count = summary_lower.count("the")
        assert generic_word_count < 50, f"POC proposal appears too generic (high 'the' count: {generic_word_count})"
    
    @pytest.mark.asyncio
    async def test_poc_proposal_includes_financial_analysis(self, orchestrator):
        """Test that POC proposal includes comprehensive financial analysis."""
        business_context = {
            "pillar_outputs": {
                "content": {"files": []},
                "insights": {"summary": "Analysis complete"},
                "operations": {"coexistence_blueprint": {}}
            },
            "proposal_options": {
                "poc_type": "hybrid",
                "budget_range": "medium",
                "timeline_preference": "90_days"
            }
        }
        
        result = await orchestrator.generate_poc_proposal(business_context)
        
        assert result["success"] is True
        proposal = result["proposal"]
        
        # Validate financial analysis
        financial = proposal.get("financial_analysis", {})
        assert "roi" in financial, "ROI missing from financial analysis"
        assert "npv" in financial, "NPV missing from financial analysis"
        assert "irr" in financial, "IRR missing from financial analysis"
        
        # Validate financial values are reasonable
        roi = financial.get("roi")
        assert roi is not None, "ROI value is None"
        assert roi > 0, f"ROI should be positive, got {roi}"
        
        npv = financial.get("npv")
        assert npv is not None, "NPV value is None"
        
        irr = financial.get("irr")
        assert irr is not None, "IRR value is None"
        
        # Validate risk analysis
        assert "risk_analysis" in financial or "risk_assessment" in proposal, "Risk analysis missing"
    
    @pytest.mark.asyncio
    async def test_poc_proposal_integrates_pillar_outputs(self, orchestrator):
        """Test that POC proposal integrates outputs from all pillars."""
        business_context = {
            "pillar_outputs": {
                "content": {
                    "files": [
                        {"name": "legacy_data.csv", "type": "csv"},
                        {"name": "target_schema.json", "type": "json"}
                    ],
                    "summary": "Data migration files uploaded"
                },
                "insights": {
                    "summary": "Data quality analysis: 75% completeness, schema alignment needed",
                    "recommendations": ["Data cleansing required", "Schema transformation needed"]
                },
                "operations": {
                    "coexistence_blueprint": {
                        "current_state": "Legacy system",
                        "future_state": "Modernized platform",
                        "recommendations": ["Phased migration", "Parallel running"]
                    }
                }
            },
            "proposal_options": {
                "poc_type": "technical",
                "budget_range": "high",
                "timeline_preference": "180_days"
            }
        }
        
        result = await orchestrator.generate_poc_proposal(business_context)
        
        assert result["success"] is True
        proposal = result["proposal"]
        
        executive_summary = proposal.get("executive_summary", "").lower()
        business_case = proposal.get("business_case", "").lower()
        combined_text = executive_summary + " " + business_case
        
        # Check for pillar integration indicators
        # Content pillar
        assert any(word in combined_text for word in ["file", "data", "upload", "content", "migration"]) or                "content_summary" in proposal or "files" in proposal,                "POC proposal should reference content pillar outputs"
        
        # Insights pillar
        assert any(word in combined_text for word in ["insight", "analysis", "quality", "schema"]) or                "insights_summary" in proposal,                "POC proposal should reference insights pillar outputs"
        
        # Operations pillar
        assert any(word in combined_text for word in ["workflow", "process", "migration", "coexistence", "legacy"]) or                "coexistence_blueprint" in proposal,                "POC proposal should reference operations pillar outputs"
