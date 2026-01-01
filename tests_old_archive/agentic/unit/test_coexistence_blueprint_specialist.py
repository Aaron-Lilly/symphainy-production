"""
Coexistence Blueprint Specialist - Unit Tests

Tests for AI-powered coexistence blueprint generation specialist agent.
Tests human-AI collaboration analysis, blueprint generation, and strategic recommendations.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.unit
@pytest.mark.agentic
@pytest.mark.asyncio
class TestCoexistenceBlueprintSpecialist:
    """Test suite for CoexistenceBlueprintSpecialist."""
    
    async def test_initialization(self, coexistence_blueprint_specialist_fixture):
        """Test specialist initializes correctly."""
        specialist = coexistence_blueprint_specialist_fixture
        
        assert specialist is not None
        assert specialist.capability_name == "coexistence_blueprint"
        assert "collaboration_pattern_analysis" in specialist.ai_enhancements
        assert specialist.enabling_service_name == "CoexistenceOptimizationService"
    
    async def test_get_agent_capabilities(self, coexistence_blueprint_specialist_fixture):
        """Test specialist reports correct capabilities."""
        specialist = coexistence_blueprint_specialist_fixture
        
        capabilities = specialist.get_agent_capabilities()
        
        assert "coexistence_blueprint" in capabilities
        assert "collaboration_pattern_analysis" in capabilities
        assert "optimization_opportunity_identification" in capabilities
    
    async def test_generate_coexistence_blueprint(self, coexistence_blueprint_specialist_fixture,
                                                  sample_workflow_data):
        """Test main MVP use case: generate coexistence blueprint."""
        specialist = coexistence_blueprint_specialist_fixture
        
        user_context = {
            "user_id": "test_user",
            "industry": "manufacturing"
        }
        
        sop_data = {"title": "Test SOP", "steps": []}
        
        result = await specialist.generate_coexistence_blueprint(
            workflow_data=sample_workflow_data,
            sop_data=sop_data,
            user_context=user_context
        )
        
        assert result["success"] is True
        assert result["capability"] == "coexistence_blueprint"
        assert "result" in result
    
    async def test_ai_enhancement_with_strategic_insights(self, coexistence_blueprint_specialist_fixture):
        """Test AI enhancement adds strategic coexistence insights."""
        specialist = coexistence_blueprint_specialist_fixture
        
        service_result = {"analysis": "test"}
        request = {
            "data": {"workflow": {}, "sop": {}},
            "user_context": {}
        }
        context_analysis = {}
        
        enhanced = await specialist._enhance_with_ai(
            service_result, request, context_analysis
        )
        
        assert "coexistence_score" in enhanced
        assert "current_state_analysis" in enhanced
        assert "optimization_opportunities" in enhanced
        assert "future_state_blueprint" in enhanced
        assert "implementation_roadmap" in enhanced
        assert "expected_benefits" in enhanced
    
    async def test_coexistence_score_calculation(self, coexistence_blueprint_specialist_fixture):
        """Test specialist calculates coexistence quality score."""
        specialist = coexistence_blueprint_specialist_fixture
        
        service_result = {"data": "test"}
        score = specialist._calculate_coexistence_score(service_result)
        
        assert "overall_score" in score
        assert "human_efficiency" in score
        assert "ai_effectiveness" in score
        assert "collaboration_quality" in score
        assert "potential_score" in score
        assert 0 <= score["overall_score"] <= 100
    
    async def test_current_state_analysis(self, coexistence_blueprint_specialist_fixture):
        """Test specialist analyzes current collaboration state."""
        specialist = coexistence_blueprint_specialist_fixture
        
        service_result = {"data": "test"}
        analysis = specialist._analyze_current_state(service_result)
        
        assert "strengths" in analysis
        assert "weaknesses" in analysis
        assert "critical_issues" in analysis
    
    async def test_optimization_opportunity_identification(self, coexistence_blueprint_specialist_fixture):
        """Test specialist identifies optimization opportunities."""
        specialist = coexistence_blueprint_specialist_fixture
        
        service_result = {"data": "test"}
        opportunities = specialist._identify_optimization_opportunities(service_result)
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        assert all("opportunity" in opp for opp in opportunities)
        assert all("impact" in opp for opp in opportunities)
        assert all("effort" in opp for opp in opportunities)
        assert all("expected_improvement" in opp for opp in opportunities)
    
    async def test_future_state_design(self, coexistence_blueprint_specialist_fixture):
        """Test specialist designs optimized future state."""
        specialist = coexistence_blueprint_specialist_fixture
        
        service_result = {"data": "test"}
        future_state = specialist._design_future_state(service_result)
        
        assert "vision" in future_state
        assert "key_changes" in future_state
        assert "target_metrics" in future_state
    
    async def test_implementation_roadmap_generation(self, coexistence_blueprint_specialist_fixture):
        """Test specialist generates implementation roadmap."""
        specialist = coexistence_blueprint_specialist_fixture
        
        service_result = {"data": "test"}
        roadmap = specialist._generate_implementation_roadmap(service_result)
        
        assert "phases" in roadmap
        assert isinstance(roadmap["phases"], list)
        assert len(roadmap["phases"]) > 0
        assert all("phase" in p for p in roadmap["phases"])
        assert all("objectives" in p for p in roadmap["phases"])
        assert all("deliverables" in p for p in roadmap["phases"])
    
    async def test_benefits_projection(self, coexistence_blueprint_specialist_fixture):
        """Test specialist projects expected benefits."""
        specialist = coexistence_blueprint_specialist_fixture
        
        service_result = {"data": "test"}
        benefits = specialist._project_benefits(service_result)
        
        assert "efficiency_gains" in benefits
        assert "quality_improvements" in benefits
        assert "cost_savings" in benefits
        assert "strategic_benefits" in benefits
    
    async def test_execute_capability_success(self, coexistence_blueprint_specialist_fixture,
                                             sample_workflow_data):
        """Test full capability execution succeeds."""
        specialist = coexistence_blueprint_specialist_fixture
        
        request = {
            "task": "generate_coexistence_blueprint",
            "data": {
                "workflow": sample_workflow_data,
                "sop": {"title": "Test SOP"}
            },
            "user_context": {"industry": "technology"},
            "parameters": {
                "include_analysis": True,
                "include_future_state": True
            }
        }
        
        result = await specialist.execute_capability(request)
        
        assert result["success"] is True
        assert result["capability"] == "coexistence_blueprint"
        assert "result" in result
    
    async def test_execute_capability_error_handling(self, coexistence_blueprint_specialist_fixture):
        """Test specialist handles errors gracefully."""
        specialist = coexistence_blueprint_specialist_fixture
        
        request = None
        result = await specialist.execute_capability(request)
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_collaboration_pattern_analysis(self, coexistence_blueprint_specialist_fixture):
        """Test specialist analyzes human-AI collaboration patterns."""
        specialist = coexistence_blueprint_specialist_fixture
        
        # This is an AI enhancement, so it's part of the enhancement flow
        assert "collaboration_pattern_analysis" in specialist.ai_enhancements
    
    async def test_task_tracking(self, coexistence_blueprint_specialist_fixture,
                                sample_workflow_data):
        """Test specialist tracks task execution history."""
        specialist = coexistence_blueprint_specialist_fixture
        
        # Execute tasks
        for i in range(2):
            request = {
                "task": f"coexistence_{i}",
                "data": {
                    "workflow": sample_workflow_data,
                    "sop": {"title": "Test"}
                },
                "user_context": {}
            }
            await specialist.execute_capability(request)
        
        assert len(specialist.task_history) == 2
    
    async def test_specialist_service_configuration(self, coexistence_blueprint_specialist_fixture):
        """Test specialist is configured with correct enabling service."""
        specialist = coexistence_blueprint_specialist_fixture
        
        assert specialist.enabling_service_name == "CoexistenceOptimizationService"
    
    async def test_specialist_mcp_tools_configuration(self, coexistence_blueprint_specialist_fixture):
        """Test specialist is configured with correct MCP tools."""
        specialist = coexistence_blueprint_specialist_fixture
        
        assert "analyze_coexistence" in specialist.capability_mcp_tools
        assert "generate_blueprint" in specialist.capability_mcp_tools
        assert "assess_collaboration" in specialist.capability_mcp_tools
    
    async def test_specialist_ai_enhancements_configuration(self, coexistence_blueprint_specialist_fixture):
        """Test specialist is configured with correct AI enhancements."""
        specialist = coexistence_blueprint_specialist_fixture
        
        assert "collaboration_pattern_analysis" in specialist.ai_enhancements
        assert "optimization_opportunity_identification" in specialist.ai_enhancements
        assert "future_state_design" in specialist.ai_enhancements
        assert "strategic_roadmap_generation" in specialist.ai_enhancements

