"""
Roadmap & Proposal Specialist - Unit Tests

Tests for AI-powered roadmap and proposal generation specialist agent.
Tests multi-pillar synthesis, strategic roadmap creation, and POC proposal generation.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.unit
@pytest.mark.agentic
@pytest.mark.asyncio
class TestRoadmapProposalSpecialist:
    """Test suite for RoadmapProposalSpecialist."""
    
    async def test_initialization(self, roadmap_proposal_specialist_fixture):
        """Test specialist initializes correctly."""
        specialist = roadmap_proposal_specialist_fixture
        
        assert specialist is not None
        assert specialist.capability_name == "roadmap_proposal_generation"
        assert "multi_pillar_synthesis" in specialist.ai_enhancements
        assert specialist.enabling_service_name == "ReportGeneratorService"
    
    async def test_get_agent_capabilities(self, roadmap_proposal_specialist_fixture):
        """Test specialist reports correct capabilities."""
        specialist = roadmap_proposal_specialist_fixture
        
        capabilities = specialist.get_agent_capabilities()
        
        assert "roadmap_proposal_generation" in capabilities
        assert "multi_pillar_synthesis" in capabilities
        assert "strategic_roadmap_creation" in capabilities
    
    async def test_generate_comprehensive_proposal(self, roadmap_proposal_specialist_fixture,
                                                   sample_pillar_summaries):
        """Test main MVP use case: generate comprehensive proposal."""
        specialist = roadmap_proposal_specialist_fixture
        
        user_context = {
            "user_id": "test_user",
            "organization": "test_org"
        }
        
        result = await specialist.generate_comprehensive_proposal(
            pillar_summaries=sample_pillar_summaries,
            user_context=user_context
        )
        
        assert result["success"] is True
        assert result["capability"] == "roadmap_proposal_generation"
        assert "result" in result
    
    async def test_ai_enhancement_with_synthesis(self, roadmap_proposal_specialist_fixture):
        """Test AI enhancement synthesizes multi-pillar insights."""
        specialist = roadmap_proposal_specialist_fixture
        
        service_result = {"report": "test"}
        request = {
            "data": {
                "content_summary": {},
                "insights_summary": {},
                "operations_summary": {},
                "outcomes_summary": {}
            },
            "user_context": {}
        }
        context_analysis = {}
        
        enhanced = await specialist._enhance_with_ai(
            service_result, request, context_analysis
        )
        
        assert "executive_summary" in enhanced
        assert "strategic_analysis" in enhanced
        assert "implementation_roadmap" in enhanced
        assert "poc_proposal" in enhanced
        assert "risk_assessment" in enhanced
        assert "expected_outcomes" in enhanced
    
    async def test_multi_pillar_synthesis(self, roadmap_proposal_specialist_fixture,
                                         sample_pillar_summaries):
        """Test specialist synthesizes insights from all pillars."""
        specialist = roadmap_proposal_specialist_fixture
        
        synthesis = specialist._synthesize_pillar_insights(sample_pillar_summaries)
        
        assert "key_themes" in synthesis
        assert "cross_pillar_opportunities" in synthesis
        assert "strategic_priorities" in synthesis
        assert "integration_points" in synthesis
    
    async def test_executive_summary_generation(self, roadmap_proposal_specialist_fixture,
                                               sample_pillar_summaries):
        """Test specialist generates executive summary."""
        specialist = roadmap_proposal_specialist_fixture
        
        summary = specialist._generate_executive_summary(sample_pillar_summaries)
        
        assert "overview" in summary
        assert "key_findings" in summary
        assert "recommendations" in summary
        assert "next_steps" in summary
    
    async def test_strategic_analysis_generation(self, roadmap_proposal_specialist_fixture,
                                                sample_pillar_summaries):
        """Test specialist generates strategic analysis."""
        specialist = roadmap_proposal_specialist_fixture
        
        analysis = specialist._generate_strategic_analysis(sample_pillar_summaries)
        
        assert "current_state" in analysis
        assert "opportunities" in analysis
        assert "challenges" in analysis
        assert "strategic_direction" in analysis
    
    async def test_implementation_roadmap_creation(self, roadmap_proposal_specialist_fixture,
                                                  sample_pillar_summaries):
        """Test specialist creates implementation roadmap."""
        specialist = roadmap_proposal_specialist_fixture
        
        roadmap = specialist._create_implementation_roadmap(sample_pillar_summaries)
        
        assert "timeline" in roadmap
        assert "phases" in roadmap
        assert "milestones" in roadmap
        assert "dependencies" in roadmap
        assert isinstance(roadmap["phases"], list)
        assert len(roadmap["phases"]) > 0
    
    async def test_poc_proposal_generation(self, roadmap_proposal_specialist_fixture,
                                          sample_pillar_summaries):
        """Test specialist generates POC proposal."""
        specialist = roadmap_proposal_specialist_fixture
        
        poc = specialist._generate_poc_proposal(sample_pillar_summaries)
        
        assert "objectives" in poc
        assert "scope" in poc
        assert "success_criteria" in poc
        assert "timeline" in poc
        assert "resource_requirements" in poc
        assert "expected_outcomes" in poc
    
    async def test_risk_assessment(self, roadmap_proposal_specialist_fixture,
                                  sample_pillar_summaries):
        """Test specialist assesses risks."""
        specialist = roadmap_proposal_specialist_fixture
        
        risks = specialist._assess_risks(sample_pillar_summaries)
        
        assert "identified_risks" in risks
        assert "mitigation_strategies" in risks
        assert isinstance(risks["identified_risks"], list)
        assert len(risks["identified_risks"]) > 0
        assert all("risk" in r for r in risks["identified_risks"])
        assert all("severity" in r for r in risks["identified_risks"])
        assert all("likelihood" in r for r in risks["identified_risks"])
    
    async def test_expected_outcomes_projection(self, roadmap_proposal_specialist_fixture,
                                               sample_pillar_summaries):
        """Test specialist projects expected outcomes."""
        specialist = roadmap_proposal_specialist_fixture
        
        outcomes = specialist._project_expected_outcomes(sample_pillar_summaries)
        
        assert "short_term" in outcomes
        assert "medium_term" in outcomes
        assert "long_term" in outcomes
        assert all(isinstance(outcomes[k], list) for k in ["short_term", "medium_term", "long_term"])
    
    async def test_cross_pillar_opportunity_identification(self, roadmap_proposal_specialist_fixture,
                                                          sample_pillar_summaries):
        """Test specialist identifies cross-pillar opportunities."""
        specialist = roadmap_proposal_specialist_fixture
        
        opportunities = specialist._identify_cross_pillar_opportunities(sample_pillar_summaries)
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        assert all("opportunity" in opp for opp in opportunities)
        assert all("pillars_involved" in opp for opp in opportunities)
        assert all("expected_impact" in opp for opp in opportunities)
    
    async def test_strategic_priority_ranking(self, roadmap_proposal_specialist_fixture,
                                             sample_pillar_summaries):
        """Test specialist ranks strategic priorities."""
        specialist = roadmap_proposal_specialist_fixture
        
        priorities = specialist._rank_strategic_priorities(sample_pillar_summaries)
        
        assert isinstance(priorities, list)
        assert len(priorities) > 0
        assert all("priority" in p for p in priorities)
        assert all("rank" in p for p in priorities)
        assert all("justification" in p for p in priorities)
        # Verify priorities are ranked in order
        ranks = [p["rank"] for p in priorities]
        assert ranks == sorted(ranks)
    
    async def test_integration_point_mapping(self, roadmap_proposal_specialist_fixture,
                                            sample_pillar_summaries):
        """Test specialist maps integration points."""
        specialist = roadmap_proposal_specialist_fixture
        
        integration_points = specialist._map_integration_points(sample_pillar_summaries)
        
        assert isinstance(integration_points, list)
        assert len(integration_points) > 0
        assert all("from_pillar" in ip for ip in integration_points)
        assert all("to_pillar" in ip for ip in integration_points)
        assert all("integration_type" in ip for ip in integration_points)
    
    async def test_execute_capability_success(self, roadmap_proposal_specialist_fixture,
                                             sample_pillar_summaries):
        """Test full capability execution succeeds."""
        specialist = roadmap_proposal_specialist_fixture
        
        request = {
            "task": "generate_proposal",
            "data": sample_pillar_summaries,
            "user_context": {
                "organization": "test_org",
                "industry": "technology"
            },
            "parameters": {
                "include_poc": True,
                "include_roadmap": True
            }
        }
        
        result = await specialist.execute_capability(request)
        
        assert result["success"] is True
        assert result["capability"] == "roadmap_proposal_generation"
        assert "result" in result
    
    async def test_execute_capability_error_handling(self, roadmap_proposal_specialist_fixture):
        """Test specialist handles errors gracefully."""
        specialist = roadmap_proposal_specialist_fixture
        
        request = None
        result = await specialist.execute_capability(request)
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_roadmap_phases_structure(self, roadmap_proposal_specialist_fixture,
                                           sample_pillar_summaries):
        """Test roadmap has proper phase structure."""
        specialist = roadmap_proposal_specialist_fixture
        
        roadmap = specialist._create_implementation_roadmap(sample_pillar_summaries)
        
        assert "phases" in roadmap
        for phase in roadmap["phases"]:
            assert "name" in phase
            assert "duration" in phase
            assert "objectives" in phase
            assert "deliverables" in phase
            assert "success_criteria" in phase
    
    async def test_poc_scope_definition(self, roadmap_proposal_specialist_fixture,
                                       sample_pillar_summaries):
        """Test POC scope is well-defined."""
        specialist = roadmap_proposal_specialist_fixture
        
        poc = specialist._generate_poc_proposal(sample_pillar_summaries)
        
        assert "scope" in poc
        assert "in_scope" in poc["scope"]
        assert "out_of_scope" in poc["scope"]
        assert isinstance(poc["scope"]["in_scope"], list)
        assert isinstance(poc["scope"]["out_of_scope"], list)
    
    async def test_success_criteria_definition(self, roadmap_proposal_specialist_fixture,
                                              sample_pillar_summaries):
        """Test POC includes clear success criteria."""
        specialist = roadmap_proposal_specialist_fixture
        
        poc = specialist._generate_poc_proposal(sample_pillar_summaries)
        
        assert "success_criteria" in poc
        assert isinstance(poc["success_criteria"], list)
        assert len(poc["success_criteria"]) > 0
    
    async def test_resource_requirements_definition(self, roadmap_proposal_specialist_fixture,
                                                   sample_pillar_summaries):
        """Test POC includes resource requirements."""
        specialist = roadmap_proposal_specialist_fixture
        
        poc = specialist._generate_poc_proposal(sample_pillar_summaries)
        
        assert "resource_requirements" in poc
        assert "team" in poc["resource_requirements"]
        assert "technology" in poc["resource_requirements"]
        assert "budget_estimate" in poc["resource_requirements"]
    
    async def test_timeline_generation(self, roadmap_proposal_specialist_fixture,
                                      sample_pillar_summaries):
        """Test specialist generates realistic timeline."""
        specialist = roadmap_proposal_specialist_fixture
        
        roadmap = specialist._create_implementation_roadmap(sample_pillar_summaries)
        
        assert "timeline" in roadmap
        assert "start_date" in roadmap["timeline"]
        assert "end_date" in roadmap["timeline"]
        assert "total_duration" in roadmap["timeline"]
    
    async def test_milestone_tracking(self, roadmap_proposal_specialist_fixture,
                                     sample_pillar_summaries):
        """Test roadmap includes key milestones."""
        specialist = roadmap_proposal_specialist_fixture
        
        roadmap = specialist._create_implementation_roadmap(sample_pillar_summaries)
        
        assert "milestones" in roadmap
        assert isinstance(roadmap["milestones"], list)
        assert len(roadmap["milestones"]) > 0
        assert all("name" in m for m in roadmap["milestones"])
        assert all("target_date" in m for m in roadmap["milestones"])
    
    async def test_dependency_mapping(self, roadmap_proposal_specialist_fixture,
                                     sample_pillar_summaries):
        """Test roadmap maps dependencies between phases."""
        specialist = roadmap_proposal_specialist_fixture
        
        roadmap = specialist._create_implementation_roadmap(sample_pillar_summaries)
        
        assert "dependencies" in roadmap
        assert isinstance(roadmap["dependencies"], list)
    
    async def test_task_tracking(self, roadmap_proposal_specialist_fixture,
                                sample_pillar_summaries):
        """Test specialist tracks task execution history."""
        specialist = roadmap_proposal_specialist_fixture
        
        # Execute multiple tasks
        for i in range(2):
            request = {
                "task": f"proposal_{i}",
                "data": sample_pillar_summaries,
                "user_context": {}
            }
            await specialist.execute_capability(request)
        
        assert len(specialist.task_history) == 2
    
    async def test_specialist_service_configuration(self, roadmap_proposal_specialist_fixture):
        """Test specialist is configured with correct enabling service."""
        specialist = roadmap_proposal_specialist_fixture
        
        assert specialist.enabling_service_name == "ReportGeneratorService"
    
    async def test_specialist_mcp_tools_configuration(self, roadmap_proposal_specialist_fixture):
        """Test specialist is configured with correct MCP tools."""
        specialist = roadmap_proposal_specialist_fixture
        
        assert "generate_report" in specialist.capability_mcp_tools
        assert "synthesize_insights" in specialist.capability_mcp_tools
        assert "create_executive_document" in specialist.capability_mcp_tools
    
    async def test_specialist_ai_enhancements_configuration(self, roadmap_proposal_specialist_fixture):
        """Test specialist is configured with correct AI enhancements."""
        specialist = roadmap_proposal_specialist_fixture
        
        assert "multi_pillar_synthesis" in specialist.ai_enhancements
        assert "strategic_roadmap_creation" in specialist.ai_enhancements
        assert "poc_proposal_generation" in specialist.ai_enhancements
        assert "executive_presentation_formatting" in specialist.ai_enhancements

