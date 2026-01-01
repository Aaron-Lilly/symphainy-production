"""
Workflow Generation Specialist - Unit Tests

Tests for AI-powered workflow generation and optimization specialist agent.
Tests workflow creation, optimization, bottleneck identification, and efficiency improvements.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.unit
@pytest.mark.agentic
@pytest.mark.asyncio
class TestWorkflowGenerationSpecialist:
    """Test suite for WorkflowGenerationSpecialist."""
    
    async def test_initialization(self, workflow_generation_specialist_fixture):
        """Test specialist initializes correctly."""
        specialist = workflow_generation_specialist_fixture
        
        assert specialist is not None
        assert specialist.capability_name == "workflow_generation"
        assert "process_optimization" in specialist.ai_enhancements
        assert specialist.enabling_service_name == "WorkflowManagerService"
    
    async def test_get_agent_capabilities(self, workflow_generation_specialist_fixture):
        """Test specialist reports correct capabilities."""
        specialist = workflow_generation_specialist_fixture
        
        capabilities = specialist.get_agent_capabilities()
        
        assert "workflow_generation" in capabilities
        assert "process_optimization" in capabilities
        assert "bottleneck_identification" in capabilities
    
    async def test_generate_workflow_from_sop(self, workflow_generation_specialist_fixture,
                                             sample_workflow_data):
        """Test main MVP use case: generate workflow from SOP."""
        specialist = workflow_generation_specialist_fixture
        
        user_context = {
            "user_id": "test_user",
            "industry": "manufacturing"
        }
        
        result = await specialist.generate_workflow_from_sop(
            sop_data=sample_workflow_data,
            user_context=user_context,
            optimize=True
        )
        
        assert result["success"] is True
        assert result["capability"] == "workflow_generation"
        assert "result" in result
    
    async def test_ai_enhancement_with_optimization(self, workflow_generation_specialist_fixture):
        """Test AI enhancement optimizes workflow."""
        specialist = workflow_generation_specialist_fixture
        
        service_result = {"workflow": "test"}
        request = {
            "data": {"nodes": [], "edges": []},
            "user_context": {},
            "parameters": {"optimize": True}
        }
        context_analysis = {
            "complexity": "moderate"
        }
        
        enhanced = await specialist._enhance_with_ai(
            service_result, request, context_analysis
        )
        
        assert "optimized_workflow" in enhanced
        assert "bottlenecks_identified" in enhanced
        assert "efficiency_improvements" in enhanced
        assert "parallel_opportunities" in enhanced
    
    async def test_workflow_optimization(self, workflow_generation_specialist_fixture):
        """Test specialist optimizes workflow using AI."""
        specialist = workflow_generation_specialist_fixture
        
        service_result = {"workflow": "test"}
        optimized = specialist._optimize_workflow(service_result)
        
        assert "optimized" in optimized
        assert optimized["optimized"] is True
        assert "improvements_applied" in optimized
    
    async def test_bottleneck_identification(self, workflow_generation_specialist_fixture):
        """Test specialist identifies process bottlenecks."""
        specialist = workflow_generation_specialist_fixture
        
        service_result = {"workflow": "test"}
        bottlenecks = specialist._identify_bottlenecks(service_result)
        
        assert isinstance(bottlenecks, list)
        assert len(bottlenecks) > 0
        assert all("location" in b for b in bottlenecks)
        assert all("severity" in b for b in bottlenecks)
        assert all("recommendation" in b for b in bottlenecks)
    
    async def test_efficiency_improvement_suggestions(self, workflow_generation_specialist_fixture):
        """Test specialist suggests efficiency improvements."""
        specialist = workflow_generation_specialist_fixture
        
        service_result = {"workflow": "test"}
        improvements = specialist._suggest_efficiency_improvements(service_result)
        
        assert isinstance(improvements, list)
        assert len(improvements) > 0
    
    async def test_parallel_opportunity_identification(self, workflow_generation_specialist_fixture):
        """Test specialist identifies opportunities for parallel execution."""
        specialist = workflow_generation_specialist_fixture
        
        service_result = {"workflow": "test"}
        opportunities = specialist._identify_parallel_opportunities(service_result)
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        assert all("tasks" in opp for opp in opportunities)
        assert all("potential_time_saving" in opp for opp in opportunities)
    
    async def test_execute_capability_success(self, workflow_generation_specialist_fixture,
                                             sample_workflow_data):
        """Test full capability execution succeeds."""
        specialist = workflow_generation_specialist_fixture
        
        request = {
            "task": "generate_workflow",
            "data": sample_workflow_data,
            "user_context": {"industry": "technology"},
            "parameters": {
                "optimize": True,
                "identify_bottlenecks": True
            }
        }
        
        result = await specialist.execute_capability(request)
        
        assert result["success"] is True
        assert result["capability"] == "workflow_generation"
        assert "result" in result
    
    async def test_execute_capability_error_handling(self, workflow_generation_specialist_fixture):
        """Test specialist handles errors gracefully."""
        specialist = workflow_generation_specialist_fixture
        
        request = None
        result = await specialist.execute_capability(request)
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_optimization_with_different_complexity(self, workflow_generation_specialist_fixture):
        """Test optimization handles different workflow complexities."""
        specialist = workflow_generation_specialist_fixture
        
        # Simple workflow
        simple_workflow = {"nodes": [{"id": "1"}, {"id": "2"}]}
        optimized_simple = specialist._optimize_workflow(simple_workflow)
        assert optimized_simple["optimized"] is True
        
        # Complex workflow
        complex_workflow = {"nodes": [{"id": str(i)} for i in range(20)]}
        optimized_complex = specialist._optimize_workflow(complex_workflow)
        assert optimized_complex["optimized"] is True
    
    async def test_task_tracking(self, workflow_generation_specialist_fixture,
                                sample_workflow_data):
        """Test specialist tracks task execution history."""
        specialist = workflow_generation_specialist_fixture
        
        # Execute multiple tasks
        for i in range(2):
            request = {
                "task": f"workflow_gen_{i}",
                "data": sample_workflow_data,
                "user_context": {}
            }
            await specialist.execute_capability(request)
        
        assert len(specialist.task_history) == 2
    
    async def test_specialist_service_configuration(self, workflow_generation_specialist_fixture):
        """Test specialist is configured with correct enabling service."""
        specialist = workflow_generation_specialist_fixture
        
        assert specialist.enabling_service_name == "WorkflowManagerService"
    
    async def test_specialist_mcp_tools_configuration(self, workflow_generation_specialist_fixture):
        """Test specialist is configured with correct MCP tools."""
        specialist = workflow_generation_specialist_fixture
        
        assert "create_workflow" in specialist.capability_mcp_tools
        assert "visualize_workflow" in specialist.capability_mcp_tools
        assert "optimize_process" in specialist.capability_mcp_tools
    
    async def test_specialist_ai_enhancements_configuration(self, workflow_generation_specialist_fixture):
        """Test specialist is configured with correct AI enhancements."""
        specialist = workflow_generation_specialist_fixture
        
        assert "process_optimization" in specialist.ai_enhancements
        assert "flow_efficiency_analysis" in specialist.ai_enhancements
        assert "bottleneck_identification" in specialist.ai_enhancements
        assert "parallel_opportunity_detection" in specialist.ai_enhancements

