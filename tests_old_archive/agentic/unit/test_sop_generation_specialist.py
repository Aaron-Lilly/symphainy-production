"""
SOP Generation Specialist - Unit Tests

Tests for AI-powered SOP generation specialist agent.
Tests natural language processing, process classification, template selection, and best practices integration.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.unit
@pytest.mark.agentic
@pytest.mark.asyncio
class TestSOPGenerationSpecialist:
    """Test suite for SOPGenerationSpecialist."""
    
    async def test_initialization(self, sop_generation_specialist_fixture):
        """Test specialist initializes correctly."""
        specialist = sop_generation_specialist_fixture
        
        assert specialist is not None
        assert specialist.capability_name == "sop_generation"
        assert "natural_language_understanding" in specialist.ai_enhancements
        assert specialist.enabling_service_name == "WorkflowManagerService"
    
    async def test_get_agent_capabilities(self, sop_generation_specialist_fixture):
        """Test specialist reports correct capabilities."""
        specialist = sop_generation_specialist_fixture
        
        capabilities = specialist.get_agent_capabilities()
        
        assert "sop_generation" in capabilities
        assert "natural_language_understanding" in capabilities
        assert "best_practices_integration" in capabilities
    
    async def test_generate_sop_from_description(self, sop_generation_specialist_fixture,
                                                 sample_sop_description):
        """Test main MVP use case: generate SOP from natural language."""
        specialist = sop_generation_specialist_fixture
        
        user_context = {
            "user_id": "test_user",
            "industry": "fintech"
        }
        
        result = await specialist.generate_sop_from_description(
            description=sample_sop_description,
            user_context=user_context
        )
        
        assert result["success"] is True
        assert result["capability"] == "sop_generation"
        assert "result" in result
    
    async def test_request_context_analysis(self, sop_generation_specialist_fixture,
                                           sample_sop_description):
        """Test AI analyzes SOP generation request context."""
        specialist = sop_generation_specialist_fixture
        
        request = {
            "task": "generate_sop",
            "data": {"description": sample_sop_description},
            "user_context": {"industry": "technology"}
        }
        
        context_analysis = await specialist._analyze_request_context(request)
        
        assert "task_type" in context_analysis
        assert context_analysis["task_type"] == "sop_generation"
        assert "process_type" in context_analysis
        assert "complexity" in context_analysis
        assert "recommended_template" in context_analysis
    
    async def test_process_type_classification(self, sop_generation_specialist_fixture):
        """Test specialist classifies process types correctly."""
        specialist = sop_generation_specialist_fixture
        
        # Customer service process
        desc = "Customer support process for handling inquiries"
        process_type = specialist._classify_process_type(desc)
        assert process_type == "customer_service"
        
        # Manufacturing process
        desc = "Manufacturing assembly line process"
        process_type = specialist._classify_process_type(desc)
        assert process_type == "manufacturing"
        
        # Administrative process
        desc = "Administrative document approval process"
        process_type = specialist._classify_process_type(desc)
        assert process_type == "administrative"
        
        # Technical process
        desc = "System maintenance and technical support"
        process_type = specialist._classify_process_type(desc)
        assert process_type == "technical"
    
    async def test_process_complexity_assessment(self, sop_generation_specialist_fixture):
        """Test specialist assesses process complexity."""
        specialist = sop_generation_specialist_fixture
        
        # Simple process (short description)
        simple_desc = "Collect information and create account"
        complexity = specialist._assess_process_complexity(simple_desc)
        assert complexity == "simple"
        
        # Moderate process
        moderate_desc = "Process customer onboarding: collect information, verify identity, create account, setup preferences, send welcome email, and schedule follow-up"
        complexity = specialist._assess_process_complexity(moderate_desc)
        assert complexity == "moderate"
        
        # Complex process (long description)
        complex_desc = " ".join([f"Step {i}: detailed process description" for i in range(20)])
        complexity = specialist._assess_process_complexity(complex_desc)
        assert complexity == "complex"
    
    async def test_sop_template_recommendation(self, sop_generation_specialist_fixture):
        """Test specialist recommends appropriate SOP template."""
        specialist = sop_generation_specialist_fixture
        
        # Test different process types and industries
        templates = [
            ("customer_service", "retail", "customer_service_retail_template"),
            ("manufacturing", "automotive", "manufacturing_automotive_template"),
            ("administrative", "healthcare", "administrative_healthcare_template")
        ]
        
        for process_type, industry, expected in templates:
            template = specialist._recommend_sop_template(process_type, industry)
            assert template == expected
    
    async def test_ai_enhancement_with_best_practices(self, sop_generation_specialist_fixture):
        """Test AI enhancement adds best practices."""
        specialist = sop_generation_specialist_fixture
        
        service_result = {"sop": "test"}
        request = {
            "data": {"description": "test process"},
            "user_context": {"industry": "technology"}
        }
        context_analysis = {
            "process_type": "technical",
            "industry": "technology"
        }
        
        enhanced = await specialist._enhance_with_ai(
            service_result, request, context_analysis
        )
        
        assert "sop_document" in enhanced
        assert "best_practices_added" in enhanced
        assert "compliance_considerations" in enhanced
        assert "quality_checks" in enhanced
        assert "improvement_suggestions" in enhanced
    
    async def test_sop_content_enhancement(self, sop_generation_specialist_fixture):
        """Test specialist enhances SOP content with AI."""
        specialist = sop_generation_specialist_fixture
        
        service_result = {"sop_draft": "test"}
        sop_document = specialist._enhance_sop_content(
            service_result, "customer_service", "retail"
        )
        
        assert "title" in sop_document
        assert "sections" in sop_document
        assert "metadata" in sop_document
        assert sop_document["metadata"]["ai_enhanced"] is True
    
    async def test_best_practices_addition(self, sop_generation_specialist_fixture):
        """Test specialist adds industry best practices."""
        specialist = sop_generation_specialist_fixture
        
        best_practices = specialist._add_best_practices("manufacturing")
        
        assert isinstance(best_practices, list)
        assert len(best_practices) > 0
    
    async def test_compliance_notes_addition(self, sop_generation_specialist_fixture):
        """Test specialist adds compliance considerations."""
        specialist = sop_generation_specialist_fixture
        
        compliance = specialist._add_compliance_notes("healthcare")
        
        assert isinstance(compliance, list)
        assert len(compliance) > 0
        assert any("healthcare" in note.lower() for note in compliance)
    
    async def test_quality_checkpoints_addition(self, sop_generation_specialist_fixture):
        """Test specialist adds quality checkpoints."""
        specialist = sop_generation_specialist_fixture
        
        checkpoints = specialist._add_quality_checkpoints("customer_service")
        
        assert isinstance(checkpoints, list)
        assert len(checkpoints) > 0
    
    async def test_improvement_suggestions(self, sop_generation_specialist_fixture):
        """Test specialist suggests process improvements."""
        specialist = sop_generation_specialist_fixture
        
        service_result = {"sop": "test"}
        suggestions = specialist._suggest_improvements(service_result)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    async def test_execute_capability_success(self, sop_generation_specialist_fixture,
                                             sample_sop_description):
        """Test full capability execution succeeds."""
        specialist = sop_generation_specialist_fixture
        
        request = {
            "task": "generate_sop",
            "data": {
                "description": sample_sop_description,
                "options": {"enhance_content": True}
            },
            "user_context": {"industry": "fintech"},
            "parameters": {
                "include_best_practices": True,
                "adapt_to_industry": True
            }
        }
        
        result = await specialist.execute_capability(request)
        
        assert result["success"] is True
        assert result["capability"] == "sop_generation"
        assert "result" in result
        assert "context_analysis" in result
    
    async def test_execute_capability_error_handling(self, sop_generation_specialist_fixture):
        """Test specialist handles errors gracefully."""
        specialist = sop_generation_specialist_fixture
        
        request = None
        result = await specialist.execute_capability(request)
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_sop_wizard_integration(self, sop_generation_specialist_fixture):
        """Test specialist integrates with SOP Builder Wizard."""
        specialist = sop_generation_specialist_fixture
        
        # Specialist should work with SOP Builder Wizard
        # This tests the enabling service integration pattern
        assert specialist.enabling_service_name == "WorkflowManagerService"
    
    async def test_natural_language_processing(self, sop_generation_specialist_fixture):
        """Test specialist processes natural language descriptions."""
        specialist = sop_generation_specialist_fixture
        
        # Test various natural language inputs
        descriptions = [
            "First, collect customer data. Then, verify their identity.",
            "Step 1: Gather information\nStep 2: Process application",
            "We need to onboard customers by collecting info and creating accounts"
        ]
        
        for desc in descriptions:
            request = {
                "data": {"description": desc},
                "user_context": {}
            }
            context = await specialist._analyze_request_context(request)
            assert context["process_type"] is not None
    
    async def test_industry_specific_adaptation(self, sop_generation_specialist_fixture):
        """Test specialist adapts SOPs for specific industries."""
        specialist = sop_generation_specialist_fixture
        
        industries = ["healthcare", "fintech", "manufacturing", "retail"]
        
        for industry in industries:
            compliance = specialist._add_compliance_notes(industry)
            assert len(compliance) > 0
            assert any(industry in note.lower() for note in compliance)
    
    async def test_task_tracking(self, sop_generation_specialist_fixture,
                                sample_sop_description):
        """Test specialist tracks task execution history."""
        specialist = sop_generation_specialist_fixture
        
        # Execute multiple tasks
        for i in range(2):
            request = {
                "task": f"sop_gen_{i}",
                "data": {"description": sample_sop_description},
                "user_context": {}
            }
            await specialist.execute_capability(request)
        
        assert len(specialist.task_history) == 2
    
    async def test_specialist_service_configuration(self, sop_generation_specialist_fixture):
        """Test specialist is configured with correct enabling service."""
        specialist = sop_generation_specialist_fixture
        
        assert specialist.enabling_service_name == "WorkflowManagerService"
    
    async def test_specialist_mcp_tools_configuration(self, sop_generation_specialist_fixture):
        """Test specialist is configured with correct MCP tools."""
        specialist = sop_generation_specialist_fixture
        
        assert "generate_sop" in specialist.capability_mcp_tools
        assert "create_workflow" in specialist.capability_mcp_tools
        assert "validate_process" in specialist.capability_mcp_tools
    
    async def test_specialist_ai_enhancements_configuration(self, sop_generation_specialist_fixture):
        """Test specialist is configured with correct AI enhancements."""
        specialist = sop_generation_specialist_fixture
        
        assert "natural_language_understanding" in specialist.ai_enhancements
        assert "process_context_inference" in specialist.ai_enhancements
        assert "best_practices_integration" in specialist.ai_enhancements
        assert "industry_specific_adaptation" in specialist.ai_enhancements

