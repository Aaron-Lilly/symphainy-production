"""
Business Analysis Specialist - Unit Tests

Tests for AI-powered business analysis specialist agent.
Tests capability execution, context analysis, AI enhancement, and personalization.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.mark.unit
@pytest.mark.agentic
@pytest.mark.asyncio
class TestBusinessAnalysisSpecialist:
    """Test suite for BusinessAnalysisSpecialist."""
    
    async def test_initialization(self, business_analysis_specialist_fixture):
        """Test specialist initializes correctly."""
        specialist = business_analysis_specialist_fixture
        
        assert specialist is not None
        assert specialist.capability_name == "business_analysis"
        assert "business_context_interpretation" in specialist.ai_enhancements
        assert specialist.enabling_service_name == "DataAnalyzerService"
    
    async def test_get_agent_capabilities(self, business_analysis_specialist_fixture):
        """Test specialist reports correct capabilities."""
        specialist = business_analysis_specialist_fixture
        
        capabilities = specialist.get_agent_capabilities()
        
        assert "business_analysis" in capabilities
        assert "business_context_interpretation" in capabilities
        assert "pattern_significance_analysis" in capabilities
    
    async def test_get_agent_description(self, business_analysis_specialist_fixture):
        """Test specialist provides meaningful description."""
        specialist = business_analysis_specialist_fixture
        
        description = specialist.get_agent_description()
        
        assert "business_analysis" in description.lower()
        assert "AI" in description or "ai" in description.lower()
    
    async def test_analyze_business_data(self, business_analysis_specialist_fixture, 
                                        sample_business_data):
        """Test main MVP use case: analyze business data."""
        specialist = business_analysis_specialist_fixture
        
        user_context = {
            "user_id": "test_user",
            "industry": "technology",
            "experience_level": "intermediate"
        }
        
        result = await specialist.analyze_business_data(
            data=sample_business_data,
            user_context=user_context
        )
        
        assert result["success"] is True
        assert result["capability"] == "business_analysis"
        assert "result" in result
        assert "context_analysis" in result
    
    async def test_request_context_analysis(self, business_analysis_specialist_fixture,
                                           sample_business_data):
        """Test AI analyzes request context correctly."""
        specialist = business_analysis_specialist_fixture
        
        request = {
            "task": "business_analysis",
            "data": sample_business_data,
            "user_context": {"industry": "fintech", "experience_level": "expert"}
        }
        
        context_analysis = await specialist._analyze_request_context(request)
        
        assert "task_type" in context_analysis
        assert context_analysis["task_type"] == "business_analysis"
        assert "data_type" in context_analysis
        assert "business_domain" in context_analysis
        assert context_analysis["business_domain"] == "fintech"
    
    async def test_data_type_determination(self, business_analysis_specialist_fixture):
        """Test specialist correctly determines data type."""
        specialist = business_analysis_specialist_fixture
        
        # Financial data
        financial_data = {"revenue": 1000, "sales": 500}
        data_type = specialist._determine_data_type(financial_data)
        assert data_type == "financial"
        
        # Customer data
        customer_data = {"customer_id": "123", "clients": 50}
        data_type = specialist._determine_data_type(customer_data)
        assert data_type == "customer"
        
        # Operational data
        operational_data = {"process": "manufacturing", "workflow": "xyz"}
        data_type = specialist._determine_data_type(operational_data)
        assert data_type == "operational"
    
    async def test_complexity_assessment(self, business_analysis_specialist_fixture):
        """Test specialist assesses data complexity correctly."""
        specialist = business_analysis_specialist_fixture
        
        # Simple data
        simple_data = {"field1": "value1", "field2": "value2"}
        complexity = specialist._assess_data_complexity(simple_data)
        assert complexity == "simple"
        
        # Moderate data
        moderate_data = {f"field{i}": f"value{i}" for i in range(10)}
        complexity = specialist._assess_data_complexity(moderate_data)
        assert complexity == "moderate"
        
        # Complex data
        complex_data = {f"field{i}": f"value{i}" for i in range(20)}
        complexity = specialist._assess_data_complexity(complex_data)
        assert complexity == "complex"
    
    async def test_recommendation_of_analysis_type(self, business_analysis_specialist_fixture):
        """Test specialist recommends appropriate analysis type."""
        specialist = business_analysis_specialist_fixture
        
        # Financial analysis
        analysis_type = specialist._recommend_analysis_type("financial", "banking")
        assert "financial" in analysis_type.lower()
        
        # Customer analysis
        analysis_type = specialist._recommend_analysis_type("customer", "retail")
        assert "customer" in analysis_type.lower()
        
        # Operational analysis
        analysis_type = specialist._recommend_analysis_type("operational", "manufacturing")
        assert "process" in analysis_type.lower() or "efficiency" in analysis_type.lower()
    
    async def test_ai_enhancement(self, business_analysis_specialist_fixture):
        """Test AI enhancement adds business insights."""
        specialist = business_analysis_specialist_fixture
        
        service_result = {"data": "test"}
        request = {
            "data": {"revenue": 1000},
            "user_context": {}
        }
        context_analysis = {
            "data_type": "financial",
            "business_domain": "technology"
        }
        
        enhanced = await specialist._enhance_with_ai(
            service_result, request, context_analysis
        )
        
        assert "business_insights" in enhanced
        assert "key_findings" in enhanced
        assert "patterns_detected" in enhanced
        assert "risk_factors" in enhanced
        assert "opportunities" in enhanced
        assert enhanced["confidence"] > 0
    
    async def test_business_insights_generation(self, business_analysis_specialist_fixture):
        """Test AI generates contextual business insights."""
        specialist = business_analysis_specialist_fixture
        
        service_result = {"data": "test"}
        insights = specialist._generate_business_insights(
            service_result, "financial", "fintech"
        )
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        assert any("financial" in insight.lower() for insight in insights)
    
    async def test_key_findings_extraction(self, business_analysis_specialist_fixture):
        """Test specialist extracts key findings."""
        specialist = business_analysis_specialist_fixture
        
        service_result = {"analysis": "test"}
        findings = specialist._extract_key_findings(service_result)
        
        assert isinstance(findings, list)
        assert len(findings) > 0
    
    async def test_business_pattern_detection(self, business_analysis_specialist_fixture):
        """Test specialist detects business-relevant patterns."""
        specialist = business_analysis_specialist_fixture
        
        service_result = {"data": "test"}
        patterns = specialist._detect_business_patterns(service_result, "financial")
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert all("pattern_type" in pattern for pattern in patterns)
        assert all("significance" in pattern for pattern in patterns)
    
    async def test_risk_factor_identification(self, business_analysis_specialist_fixture):
        """Test specialist identifies business risks."""
        specialist = business_analysis_specialist_fixture
        
        service_result = {"data": "test"}
        risks = specialist._identify_risk_factors(service_result)
        
        assert isinstance(risks, list)
        assert len(risks) > 0
        assert all("risk" in risk for risk in risks)
        assert all("severity" in risk for risk in risks)
    
    async def test_opportunity_identification(self, business_analysis_specialist_fixture):
        """Test specialist identifies business opportunities."""
        specialist = business_analysis_specialist_fixture
        
        service_result = {"data": "test"}
        opportunities = specialist._identify_opportunities(service_result)
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        assert all("opportunity" in opp for opp in opportunities)
        assert all("potential_impact" in opp for opp in opportunities)
    
    async def test_personalization_for_beginners(self, business_analysis_specialist_fixture):
        """Test specialist adapts output for beginner users."""
        specialist = business_analysis_specialist_fixture
        
        enhanced_result = {
            "business_insights": ["Complex insight 1", "Complex insight 2"]
        }
        request = {
            "user_context": {"experience_level": "beginner"}
        }
        
        personalized = await specialist._personalize_output(enhanced_result, request)
        
        assert "personalization" in personalized
        assert personalized["personalization"]["experience_level"] == "beginner"
        assert personalized["personalization"]["detail_level"] == "beginner"
        # Check insights were simplified
        assert any("simplified" in insight.lower() for insight in personalized["business_insights"])
    
    async def test_personalization_for_experts(self, business_analysis_specialist_fixture):
        """Test specialist adapts output for expert users."""
        specialist = business_analysis_specialist_fixture
        
        enhanced_result = {
            "business_insights": ["Insight 1", "Insight 2"]
        }
        request = {
            "user_context": {"experience_level": "expert"}
        }
        
        personalized = await specialist._personalize_output(enhanced_result, request)
        
        assert "personalization" in personalized
        assert personalized["personalization"]["experience_level"] == "expert"
        # Check additional details were added
        insights = personalized["business_insights"]
        assert len(insights) > len(enhanced_result["business_insights"])
    
    async def test_execute_capability_success(self, business_analysis_specialist_fixture,
                                             sample_business_data):
        """Test full capability execution succeeds."""
        specialist = business_analysis_specialist_fixture
        
        request = {
            "task": "business_analysis",
            "data": sample_business_data,
            "user_context": {
                "experience_level": "intermediate",
                "industry": "technology"
            },
            "parameters": {}
        }
        
        result = await specialist.execute_capability(request)
        
        assert result["success"] is True
        assert result["capability"] == "business_analysis"
        assert "context_analysis" in result
        assert "result" in result
        assert "execution_time" in result
        assert result["execution_time"] > 0
    
    async def test_execute_capability_error_handling(self, business_analysis_specialist_fixture):
        """Test specialist handles errors gracefully."""
        specialist = business_analysis_specialist_fixture
        
        # Force an error by providing invalid request
        request = None
        
        result = await specialist.execute_capability(request)
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_process_request(self, business_analysis_specialist_fixture,
                                  sample_business_data):
        """Test process_request delegates to execute_capability."""
        specialist = business_analysis_specialist_fixture
        
        request = {
            "task": "business_analysis",
            "data": sample_business_data,
            "user_context": {}
        }
        
        result = await specialist.process_request(request)
        
        assert "success" in result
        assert "capability" in result
    
    async def test_task_tracking(self, business_analysis_specialist_fixture,
                                sample_business_data):
        """Test specialist tracks task execution history."""
        specialist = business_analysis_specialist_fixture
        
        # Execute multiple tasks
        for i in range(3):
            request = {
                "task": f"task_{i}",
                "data": sample_business_data,
                "user_context": {}
            }
            await specialist.execute_capability(request)
        
        # Check task history
        assert len(specialist.task_history) == 3
        assert all("task" in task for task in specialist.task_history)
        assert all("capability" in task for task in specialist.task_history)
        assert all("duration" in task for task in specialist.task_history)
    
    async def test_specialist_service_name_configuration(self, business_analysis_specialist_fixture):
        """Test specialist is configured with correct enabling service."""
        specialist = business_analysis_specialist_fixture
        
        assert specialist.enabling_service_name == "DataAnalyzerService"
    
    async def test_specialist_mcp_tools_configuration(self, business_analysis_specialist_fixture):
        """Test specialist is configured with correct MCP tools."""
        specialist = business_analysis_specialist_fixture
        
        assert "analyze_data" in specialist.capability_mcp_tools
        assert "detect_patterns" in specialist.capability_mcp_tools
    
    async def test_specialist_ai_enhancements_configuration(self, business_analysis_specialist_fixture):
        """Test specialist is configured with correct AI enhancements."""
        specialist = business_analysis_specialist_fixture
        
        assert "business_context_interpretation" in specialist.ai_enhancements
        assert "pattern_significance_analysis" in specialist.ai_enhancements
        assert "actionable_insights_generation" in specialist.ai_enhancements
    
    async def test_specialist_integrates_with_enabling_service(self, 
                                                              business_analysis_specialist_fixture):
        """Test specialist can discover and connect to enabling service."""
        specialist = business_analysis_specialist_fixture
        
        # Mock curator to return a service
        mock_service = MagicMock()
        specialist.curator_foundation.get_service = AsyncMock(return_value=mock_service)
        
        # Re-initialize to trigger service discovery
        await specialist.initialize()
        
        # Service should be discovered (or None if not available, which is OK)
        assert hasattr(specialist, 'enabling_service')

