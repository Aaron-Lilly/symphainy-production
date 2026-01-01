"""
Recommendation Specialist - Unit Tests

Tests for AI-powered recommendation generation specialist agent.
Tests strategic reasoning, priority ranking, impact assessment, and role-based personalization.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.unit
@pytest.mark.agentic
@pytest.mark.asyncio
class TestRecommendationSpecialist:
    """Test suite for RecommendationSpecialist."""
    
    async def test_initialization(self, recommendation_specialist_fixture):
        """Test specialist initializes correctly."""
        specialist = recommendation_specialist_fixture
        
        assert specialist is not None
        assert specialist.capability_name == "recommendation_generation"
        assert "strategic_reasoning" in specialist.ai_enhancements
        assert specialist.enabling_service_name == "MetricsCalculatorService"
    
    async def test_get_agent_capabilities(self, recommendation_specialist_fixture):
        """Test specialist reports correct capabilities."""
        specialist = recommendation_specialist_fixture
        
        capabilities = specialist.get_agent_capabilities()
        
        assert "recommendation_generation" in capabilities
        assert "strategic_reasoning" in capabilities
        assert "priority_ranking" in capabilities
    
    async def test_generate_recommendations(self, recommendation_specialist_fixture,
                                           sample_business_data):
        """Test main MVP use case: generate recommendations."""
        specialist = recommendation_specialist_fixture
        
        user_context = {
            "user_id": "test_user",
            "role": "manager",
            "industry": "technology"
        }
        
        result = await specialist.generate_recommendations(
            analysis_data=sample_business_data,
            user_context=user_context,
            recommendation_type="strategic"
        )
        
        assert result["success"] is True
        assert result["capability"] == "recommendation_generation"
        assert "result" in result
        assert "context_analysis" in result
    
    async def test_request_context_analysis(self, recommendation_specialist_fixture,
                                           sample_business_data):
        """Test AI analyzes recommendation request context."""
        specialist = recommendation_specialist_fixture
        
        request = {
            "task": "generate_recommendations",
            "data": sample_business_data,
            "user_context": {"role": "executive", "industry": "fintech"},
            "parameters": {"recommendation_type": "strategic"}
        }
        
        context_analysis = await specialist._analyze_request_context(request)
        
        assert "task_type" in context_analysis
        assert context_analysis["task_type"] == "recommendation_generation"
        assert "recommendation_type" in context_analysis
        assert context_analysis["recommendation_type"] == "strategic"
        assert "business_context" in context_analysis
    
    async def test_data_quality_assessment(self, recommendation_specialist_fixture):
        """Test specialist assesses input data quality."""
        specialist = recommendation_specialist_fixture
        
        # Insufficient data
        insufficient = {}
        quality = specialist._assess_data_quality(insufficient)
        assert quality == "insufficient"
        
        # Minimal data
        minimal = {"field1": "value1"}
        quality = specialist._assess_data_quality(minimal)
        assert quality == "minimal"
        
        # Adequate data
        adequate = {f"field{i}": f"value{i}" for i in range(5)}
        quality = specialist._assess_data_quality(adequate)
        assert quality == "adequate"
        
        # Comprehensive data
        comprehensive = {f"field{i}": f"value{i}" for i in range(10)}
        quality = specialist._assess_data_quality(comprehensive)
        assert quality == "comprehensive"
    
    async def test_recommendation_approach_determination(self, recommendation_specialist_fixture):
        """Test specialist determines appropriate recommendation approach."""
        specialist = recommendation_specialist_fixture
        
        # Strategic recommendations
        approach = specialist._determine_recommendation_approach("strategic")
        assert "strategic" in approach.lower()
        
        # Operational recommendations
        approach = specialist._determine_recommendation_approach("operational")
        assert "tactical" in approach.lower() or "operational" in approach.lower()
        
        # Insights recommendations
        approach = specialist._determine_recommendation_approach("insights")
        assert "data" in approach.lower()
    
    async def test_ai_enhancement_with_strategic_reasoning(self, recommendation_specialist_fixture):
        """Test AI enhancement adds strategic reasoning."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"metrics": "test"}
        request = {
            "data": {"revenue": 1000},
            "user_context": {"role": "executive"},
            "parameters": {"recommendation_type": "strategic"}
        }
        context_analysis = {
            "recommendation_type": "strategic",
            "business_context": "technology"
        }
        
        enhanced = await specialist._enhance_with_ai(
            service_result, request, context_analysis
        )
        
        assert "recommendations" in enhanced
        assert "priority_ranking" in enhanced
        assert "impact_assessment" in enhanced
        assert "implementation_guidance" in enhanced
        assert enhanced["confidence"] > 0
    
    async def test_strategic_recommendation_generation(self, recommendation_specialist_fixture):
        """Test AI generates strategic recommendations."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"data": "test"}
        recommendations = specialist._generate_strategic_recommendations(
            service_result, "strategic", "technology"
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all("recommendation" in rec for rec in recommendations)
        assert all("rationale" in rec for rec in recommendations)
        assert all("expected_benefit" in rec for rec in recommendations)
    
    async def test_priority_ranking(self, recommendation_specialist_fixture):
        """Test specialist ranks recommendations by priority."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"data": "test"}
        ranking = specialist._rank_by_priority(service_result)
        
        assert isinstance(ranking, list)
        assert len(ranking) > 0
        assert all("rank" in item for item in ranking)
        assert all("priority" in item for item in ranking)
        assert all("impact" in item for item in ranking)
        # Verify ranked in order
        ranks = [item["rank"] for item in ranking]
        assert ranks == sorted(ranks)
    
    async def test_impact_assessment(self, recommendation_specialist_fixture):
        """Test specialist assesses business impact."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"data": "test"}
        impact = specialist._assess_recommendation_impact(service_result)
        
        assert "financial_impact" in impact
        assert "operational_impact" in impact
        assert "strategic_impact" in impact
        assert all(key in impact["financial_impact"] for key in ["estimated_roi", "payback_period"])
    
    async def test_implementation_guidance(self, recommendation_specialist_fixture):
        """Test specialist provides implementation guidance."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"data": "test"}
        guidance = specialist._provide_implementation_guidance(service_result)
        
        assert "quick_wins" in guidance
        assert "phased_approach" in guidance
        assert "success_metrics" in guidance
        assert "risk_mitigation" in guidance
    
    async def test_personalization_for_executives(self, recommendation_specialist_fixture):
        """Test specialist adapts output for executive users."""
        specialist = recommendation_specialist_fixture
        
        enhanced_result = {
            "recommendations": [{"rec": "test1"}, {"rec": "test2"}]
        }
        request = {
            "user_context": {"role": "executive"}
        }
        
        personalized = await specialist._personalize_output(enhanced_result, request)
        
        assert "personalization" in personalized
        assert personalized["personalization"]["role"] == "executive"
        assert personalized["personalization"]["focus_area"] == "strategic_impact"
        assert personalized["presentation_style"] == "executive_summary"
    
    async def test_personalization_for_managers(self, recommendation_specialist_fixture):
        """Test specialist adapts output for manager users."""
        specialist = recommendation_specialist_fixture
        
        enhanced_result = {
            "recommendations": [{"rec": "test"}]
        }
        request = {
            "user_context": {"role": "manager"}
        }
        
        personalized = await specialist._personalize_output(enhanced_result, request)
        
        assert personalized["personalization"]["role"] == "manager"
        assert personalized["personalization"]["focus_area"] == "implementation_guidance"
        assert personalized["presentation_style"] == "action_oriented"
    
    async def test_personalization_for_analysts(self, recommendation_specialist_fixture):
        """Test specialist adapts output for analyst users."""
        specialist = recommendation_specialist_fixture
        
        enhanced_result = {
            "recommendations": [{"rec": "test"}]
        }
        request = {
            "user_context": {"role": "analyst"}
        }
        
        personalized = await specialist._personalize_output(enhanced_result, request)
        
        assert personalized["personalization"]["role"] == "analyst"
        assert personalized["personalization"]["focus_area"] == "detailed_analysis"
        assert personalized["presentation_style"] == "detailed_analytical"
    
    async def test_execute_capability_success(self, recommendation_specialist_fixture,
                                             sample_business_data):
        """Test full capability execution succeeds."""
        specialist = recommendation_specialist_fixture
        
        request = {
            "task": "generate_recommendations",
            "data": sample_business_data,
            "user_context": {
                "role": "manager",
                "industry": "technology"
            },
            "parameters": {
                "recommendation_type": "strategic"
            }
        }
        
        result = await specialist.execute_capability(request)
        
        assert result["success"] is True
        assert result["capability"] == "recommendation_generation"
        assert "context_analysis" in result
        assert "result" in result
        assert "execution_time" in result
    
    async def test_execute_capability_error_handling(self, recommendation_specialist_fixture):
        """Test specialist handles errors gracefully."""
        specialist = recommendation_specialist_fixture
        
        request = None
        result = await specialist.execute_capability(request)
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_recommendation_types_supported(self, recommendation_specialist_fixture):
        """Test specialist supports multiple recommendation types."""
        specialist = recommendation_specialist_fixture
        
        # Test different recommendation types
        types = ["strategic", "operational", "insights", "general"]
        
        for rec_type in types:
            approach = specialist._determine_recommendation_approach(rec_type)
            assert approach is not None
            assert isinstance(approach, str)
    
    async def test_roi_calculation_in_impact_assessment(self, recommendation_specialist_fixture):
        """Test impact assessment includes ROI calculations."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"data": "test"}
        impact = specialist._assess_recommendation_impact(service_result)
        
        assert "financial_impact" in impact
        assert "estimated_roi" in impact["financial_impact"]
        assert "payback_period" in impact["financial_impact"]
    
    async def test_phased_implementation_approach(self, recommendation_specialist_fixture):
        """Test specialist provides phased implementation approach."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"data": "test"}
        guidance = specialist._provide_implementation_guidance(service_result)
        
        assert "phased_approach" in guidance
        assert isinstance(guidance["phased_approach"], list)
        assert len(guidance["phased_approach"]) > 0
    
    async def test_quick_wins_identification(self, recommendation_specialist_fixture):
        """Test specialist identifies quick wins."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"data": "test"}
        guidance = specialist._provide_implementation_guidance(service_result)
        
        assert "quick_wins" in guidance
        assert isinstance(guidance["quick_wins"], list)
    
    async def test_risk_mitigation_strategies(self, recommendation_specialist_fixture):
        """Test specialist provides risk mitigation strategies."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"data": "test"}
        guidance = specialist._provide_implementation_guidance(service_result)
        
        assert "risk_mitigation" in guidance
        assert isinstance(guidance["risk_mitigation"], list)
    
    async def test_success_metrics_definition(self, recommendation_specialist_fixture):
        """Test specialist defines success metrics."""
        specialist = recommendation_specialist_fixture
        
        service_result = {"data": "test"}
        guidance = specialist._provide_implementation_guidance(service_result)
        
        assert "success_metrics" in guidance
        assert isinstance(guidance["success_metrics"], list)
    
    async def test_task_tracking(self, recommendation_specialist_fixture,
                                sample_business_data):
        """Test specialist tracks task execution history."""
        specialist = recommendation_specialist_fixture
        
        # Execute multiple tasks
        for i in range(3):
            request = {
                "task": f"recommendation_task_{i}",
                "data": sample_business_data,
                "user_context": {"role": "manager"},
                "parameters": {"recommendation_type": "strategic"}
            }
            await specialist.execute_capability(request)
        
        # Check task history
        assert len(specialist.task_history) == 3
        assert all("task" in task for task in specialist.task_history)
        assert all("capability" in task for task in specialist.task_history)
    
    async def test_specialist_service_configuration(self, recommendation_specialist_fixture):
        """Test specialist is configured with correct enabling service."""
        specialist = recommendation_specialist_fixture
        
        assert specialist.enabling_service_name == "MetricsCalculatorService"
    
    async def test_specialist_mcp_tools_configuration(self, recommendation_specialist_fixture):
        """Test specialist is configured with correct MCP tools."""
        specialist = recommendation_specialist_fixture
        
        assert "calculate_metrics" in specialist.capability_mcp_tools
        assert "generate_recommendations" in specialist.capability_mcp_tools
        assert "prioritize_actions" in specialist.capability_mcp_tools
    
    async def test_specialist_ai_enhancements_configuration(self, recommendation_specialist_fixture):
        """Test specialist is configured with correct AI enhancements."""
        specialist = recommendation_specialist_fixture
        
        assert "strategic_reasoning" in specialist.ai_enhancements
        assert "context_aware_recommendations" in specialist.ai_enhancements
        assert "priority_ranking" in specialist.ai_enhancements
        assert "impact_assessment" in specialist.ai_enhancements
    
    async def test_presentation_style_adaptation(self, recommendation_specialist_fixture):
        """Test specialist adapts presentation style."""
        specialist = recommendation_specialist_fixture
        
        # Test different roles
        styles = [
            ("executive", "executive_summary"),
            ("manager", "action_oriented"),
            ("analyst", "detailed_analytical"),
            ("general", "balanced_overview")
        ]
        
        for role, expected_style in styles:
            style = specialist._adapt_presentation(role)
            assert style == expected_style

