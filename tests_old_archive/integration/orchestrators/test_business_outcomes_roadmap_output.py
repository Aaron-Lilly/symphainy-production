"""
Test Business Outcomes Orchestrator - Roadmap Output

CRITICAL TEST: Validates that roadmap outputs are impressive and complete,
not generic boilerplate. This is essential for CTO demo readiness.

Tests:
- Roadmap contains all required sections
- Roadmap is impressive (not generic)
- Roadmap integrates pillar outputs
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
class TestBusinessOutcomesRoadmapOutput:
    """Test Business Outcomes Orchestrator roadmap output quality."""
    
    @pytest.fixture
    async def orchestrator(self, real_platform_gateway):
        """Create Business Outcomes Orchestrator."""
        # TODO: Initialize orchestrator with real dependencies
        # This will need DI container setup
        orchestrator = BusinessOutcomesOrchestrator(
            service_name="test_business_outcomes_orchestrator",
            realm_name="business_enablement",
            platform_gateway=real_platform_gateway,
            di_container=None  # TODO: Get from fixture
        )
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_roadmap_contains_required_sections(self, orchestrator):
        """Test that roadmap contains all required sections."""
        business_context = {
            "pillar_outputs": {
                "content": {
                    "files": [
                        {"name": "mission_plans.csv", "type": "csv", "size": 1024}
                    ]
                },
                "insights": {
                    "summary": "Safety patterns identified in mission data. Key findings include..."
                },
                "operations": {
                    "coexistence_blueprint": {
                        "future_state": "Automated safety monitoring system",
                        "recommendations": ["Implement real-time alerts", "Add predictive analytics"]
                    }
                }
            },
            "objectives": ["Improve safety", "Reduce incidents"],
            "timeline_days": 180,
            "budget": 500000,
            "roadmap_options": {
                "roadmap_type": "hybrid"
            }
        }
        
        result = await orchestrator.generate_strategic_roadmap(business_context)
        
        # Validate structure
        assert result["success"] is True, f"Roadmap generation failed: {result.get('error', 'Unknown error')}"
        assert "roadmap" in result, "Roadmap missing from result"
        
        roadmap = result["roadmap"]
        
        # Validate required sections
        assert "executive_summary" in roadmap, "Executive summary missing"
        assert "phases" in roadmap, "Phases missing"
        assert "timeline" in roadmap, "Timeline missing"
        assert "budget" in roadmap, "Budget missing"
        assert "visualization" in roadmap, "Visualization missing"
    
    @pytest.mark.asyncio
    async def test_roadmap_is_impressive_not_generic(self, orchestrator):
        """Test that roadmap is impressive and not generic boilerplate."""
        business_context = {
            "pillar_outputs": {
                "content": {
                    "files": [{"name": "defense_telemetry.bin", "type": "cobol"}]
                },
                "insights": {
                    "summary": "Defense T&E analysis reveals critical safety patterns"
                },
                "operations": {
                    "coexistence_blueprint": {
                        "future_state": "Automated defense testing system"
                    }
                }
            },
            "objectives": ["Improve defense testing", "Enhance safety protocols"],
            "timeline_days": 180,
            "budget": 1000000,
            "roadmap_options": {
                "roadmap_type": "hybrid"
            }
        }
        
        result = await orchestrator.generate_strategic_roadmap(business_context)
        
        assert result["success"] is True
        roadmap = result["roadmap"]
        
        # Validate impressiveness
        executive_summary = roadmap.get("executive_summary", "")
        assert len(executive_summary) > 500, f"Executive summary too short ({len(executive_summary)} chars). Should be > 500 words for impressive output."
        
        # Check for context-specific content (not generic)
        summary_lower = executive_summary.lower()
        context_indicators = ["defense", "testing", "safety", "mission", "telemetry", "specific", "custom", "tailored"]
        has_context = any(indicator in summary_lower for indicator in context_indicators)
        assert has_context, f"Roadmap appears generic. Summary: {executive_summary[:200]}..."
        
        # Validate phases are substantial
        phases = roadmap.get("phases", [])
        assert len(phases) >= 3, f"Too few phases ({len(phases)}). Should have at least 3 phases."
        
        # Validate each phase has content
        for phase in phases:
            assert "name" in phase, "Phase missing name"
            assert "milestones" in phase or "objectives" in phase, "Phase missing milestones/objectives"
    
    @pytest.mark.asyncio
    async def test_roadmap_integrates_pillar_outputs(self, orchestrator):
        """Test that roadmap integrates outputs from all pillars."""
        business_context = {
            "pillar_outputs": {
                "content": {
                    "files": [
                        {"name": "test_data.csv", "type": "csv"},
                        {"name": "analysis_results.xlsx", "type": "excel"}
                    ],
                    "summary": "Uploaded 2 files for analysis"
                },
                "insights": {
                    "summary": "Key insights: Data quality is 85%, trends show positive growth",
                    "recommendations": ["Improve data collection", "Enhance analytics"]
                },
                "operations": {
                    "coexistence_blueprint": {
                        "current_state": "Manual processes",
                        "future_state": "Automated workflows",
                        "recommendations": ["Implement automation", "Train staff"]
                    }
                }
            },
            "objectives": ["Improve efficiency", "Reduce costs"],
            "timeline_days": 90,
            "budget": 250000
        }
        
        result = await orchestrator.generate_strategic_roadmap(business_context)
        
        assert result["success"] is True
        roadmap = result["roadmap"]
        
        executive_summary = roadmap.get("executive_summary", "").lower()
        
        # Check for pillar integration indicators
        # Content pillar
        assert any(word in executive_summary for word in ["file", "data", "upload", "content"]) or                "content_summary" in roadmap or "files" in roadmap,                "Roadmap should reference content pillar outputs"
        
        # Insights pillar
        assert any(word in executive_summary for word in ["insight", "analysis", "trend", "quality"]) or                "insights_summary" in roadmap,                "Roadmap should reference insights pillar outputs"
        
        # Operations pillar
        assert any(word in executive_summary for word in ["workflow", "process", "automation", "coexistence"]) or                "coexistence_blueprint" in roadmap,                "Roadmap should reference operations pillar outputs"
