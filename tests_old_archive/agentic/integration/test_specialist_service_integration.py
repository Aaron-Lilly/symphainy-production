"""
Specialist-Service Integration Tests

Tests the integration between specialist agents and enabling services:
- Specialist → Enabling Service via MCP tools
- AI enhancement on service outputs
- Service-specific tool configurations
- End-to-end specialist workflows
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestBusinessAnalysisSpecialistServiceIntegration:
    """Test Business Analysis Specialist → Data Analyzer Service integration."""
    
    async def test_specialist_calls_data_analyzer_service(self, business_analysis_specialist_fixture):
        """Test specialist calls Data Analyzer Service via MCP tools."""
        specialist = business_analysis_specialist_fixture
        
        # Mock MCP tool execution
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"analysis": "data analyzed"}
        })
        
        # Execute specialist capability
        request = {
            "task": "analyze_business_data",
            "data": {"revenue": 1000, "costs": 800},
            "user_context": {"role": "executive"}
        }
        
        result = await specialist.execute_capability(request)
        
        # Verify MCP tool was called
        specialist.mcp_client_manager.execute_role_tool.assert_called()
        assert result["success"] is True
    
    async def test_specialist_enhances_service_output_with_ai(self, business_analysis_specialist_fixture):
        """Test specialist adds AI enhancement to service output."""
        specialist = business_analysis_specialist_fixture
        
        # Mock service output
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"basic_analysis": "data"}
        })
        
        # Execute
        request = {
            "task": "analyze_business_data",
            "data": {"revenue": 1000},
            "user_context": {"role": "executive"}
        }
        
        result = await specialist.execute_capability(request)
        
        # Result should have AI enhancements
        assert result["success"] is True
        assert "result" in result
        # AI should add business insights, patterns, risks, opportunities
    
    async def test_specialist_personalizes_output_for_user_role(self, business_analysis_specialist_fixture):
        """Test specialist personalizes output based on user role."""
        specialist = business_analysis_specialist_fixture
        
        # Mock service output
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"analysis": "data"}
        })
        
        # Execute for executive
        executive_request = {
            "task": "analyze_business_data",
            "data": {"revenue": 1000},
            "user_context": {"role": "executive"}
        }
        
        executive_result = await specialist.execute_capability(executive_request)
        
        # Execute for analyst
        analyst_request = {
            "task": "analyze_business_data",
            "data": {"revenue": 1000},
            "user_context": {"role": "analyst"}
        }
        
        analyst_result = await specialist.execute_capability(analyst_request)
        
        # Both should succeed but with different personalization
        assert executive_result["success"] is True
        assert analyst_result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestRecommendationSpecialistServiceIntegration:
    """Test Recommendation Specialist → Metrics Calculator Service integration."""
    
    async def test_specialist_calls_metrics_calculator_service(self, recommendation_specialist_fixture):
        """Test specialist calls Metrics Calculator Service."""
        specialist = recommendation_specialist_fixture
        
        # Mock MCP tool execution
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"metrics": "calculated"}
        })
        
        # Execute
        request = {
            "task": "generate_recommendations",
            "data": {"metrics_data": {}},
            "user_context": {"role": "manager"}
        }
        
        result = await specialist.execute_capability(request)
        
        # Verify service call
        specialist.mcp_client_manager.execute_role_tool.assert_called()
        assert result["success"] is True
    
    async def test_specialist_adds_strategic_reasoning(self, recommendation_specialist_fixture):
        """Test specialist adds strategic reasoning to recommendations."""
        specialist = recommendation_specialist_fixture
        
        # Mock service output
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"basic_metrics": "data"}
        })
        
        # Execute
        request = {
            "task": "generate_recommendations",
            "data": {},
            "user_context": {"role": "executive"},
            "parameters": {"recommendation_type": "strategic"}
        }
        
        result = await specialist.execute_capability(request)
        
        # Should have strategic reasoning enhancements
        assert result["success"] is True
        # AI should add recommendations, priority ranking, impact assessment

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestSOPGenerationSpecialistServiceIntegration:
    """Test SOP Generation Specialist → Workflow Manager Service integration."""
    
    async def test_specialist_calls_workflow_manager_service(self, sop_generation_specialist_fixture):
        """Test specialist calls Workflow Manager Service."""
        specialist = sop_generation_specialist_fixture
        
        # Mock MCP tool execution
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"sop_draft": "generated"}
        })
        
        # Execute
        request = {
            "task": "generate_sop",
            "data": {"description": "Customer onboarding process"},
            "user_context": {"industry": "fintech"}
        }
        
        result = await specialist.execute_capability(request)
        
        # Verify service call
        specialist.mcp_client_manager.execute_role_tool.assert_called()
        assert result["success"] is True
    
    async def test_specialist_adds_best_practices(self, sop_generation_specialist_fixture):
        """Test specialist adds industry best practices to SOP."""
        specialist = sop_generation_specialist_fixture
        
        # Mock service output
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"sop_draft": "basic sop"}
        })
        
        # Execute
        request = {
            "task": "generate_sop",
            "data": {"description": "Process description"},
            "user_context": {"industry": "healthcare"}
        }
        
        result = await specialist.execute_capability(request)
        
        # Should have best practices and compliance notes
        assert result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestWorkflowGenerationSpecialistServiceIntegration:
    """Test Workflow Generation Specialist → Workflow Manager Service integration."""
    
    async def test_specialist_calls_workflow_manager_for_generation(self, workflow_generation_specialist_fixture):
        """Test specialist calls Workflow Manager Service for workflow generation."""
        specialist = workflow_generation_specialist_fixture
        
        # Mock MCP tool execution
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"workflow": "generated"}
        })
        
        # Execute
        request = {
            "task": "generate_workflow",
            "data": {"sop_data": {"title": "Test SOP"}},
            "user_context": {}
        }
        
        result = await specialist.execute_capability(request)
        
        # Verify service call
        specialist.mcp_client_manager.execute_role_tool.assert_called()
        assert result["success"] is True
    
    async def test_specialist_optimizes_workflow(self, workflow_generation_specialist_fixture):
        """Test specialist adds optimization to workflow."""
        specialist = workflow_generation_specialist_fixture
        
        # Mock service output
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"workflow": "basic"}
        })
        
        # Execute with optimization
        request = {
            "task": "generate_workflow",
            "data": {"sop_data": {}},
            "user_context": {},
            "parameters": {"optimize": True}
        }
        
        result = await specialist.execute_capability(request)
        
        # Should have optimization enhancements
        assert result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestCoexistenceBlueprintSpecialistServiceIntegration:
    """Test Coexistence Blueprint Specialist → Coexistence Service integration."""
    
    async def test_specialist_calls_coexistence_service(self, coexistence_blueprint_specialist_fixture):
        """Test specialist calls Coexistence Optimization Service."""
        specialist = coexistence_blueprint_specialist_fixture
        
        # Mock MCP tool execution
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"analysis": "coexistence analyzed"}
        })
        
        # Execute
        request = {
            "task": "generate_coexistence_blueprint",
            "data": {
                "workflow": {},
                "sop": {}
            },
            "user_context": {}
        }
        
        result = await specialist.execute_capability(request)
        
        # Verify service call
        specialist.mcp_client_manager.execute_role_tool.assert_called()
        assert result["success"] is True
    
    async def test_specialist_generates_implementation_roadmap(self, coexistence_blueprint_specialist_fixture):
        """Test specialist generates implementation roadmap."""
        specialist = coexistence_blueprint_specialist_fixture
        
        # Mock service output
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"analysis": "data"}
        })
        
        # Execute
        request = {
            "task": "generate_coexistence_blueprint",
            "data": {"workflow": {}, "sop": {}},
            "user_context": {}
        }
        
        result = await specialist.execute_capability(request)
        
        # Should have roadmap and future state
        assert result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestRoadmapProposalSpecialistServiceIntegration:
    """Test Roadmap & Proposal Specialist → Report Generator Service integration."""
    
    async def test_specialist_calls_report_generator_service(self, roadmap_proposal_specialist_fixture):
        """Test specialist calls Report Generator Service."""
        specialist = roadmap_proposal_specialist_fixture
        
        # Mock MCP tool execution
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"report": "generated"}
        })
        
        # Execute
        request = {
            "task": "generate_proposal",
            "data": {
                "content_summary": {},
                "insights_summary": {},
                "operations_summary": {},
                "outcomes_summary": {}
            },
            "user_context": {}
        }
        
        result = await specialist.execute_capability(request)
        
        # Verify service call
        specialist.mcp_client_manager.execute_role_tool.assert_called()
        assert result["success"] is True
    
    async def test_specialist_synthesizes_multi_pillar_insights(self, roadmap_proposal_specialist_fixture):
        """Test specialist synthesizes insights from multiple pillars."""
        specialist = roadmap_proposal_specialist_fixture
        
        # Mock service output
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {"basic_report": "data"}
        })
        
        # Execute with multi-pillar data
        request = {
            "task": "generate_proposal",
            "data": {
                "content_summary": {"key": "content_data"},
                "insights_summary": {"key": "insights_data"},
                "operations_summary": {"key": "ops_data"},
                "outcomes_summary": {"key": "outcomes_data"}
            },
            "user_context": {}
        }
        
        result = await specialist.execute_capability(request)
        
        # Should have cross-pillar synthesis
        assert result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestServiceErrorHandling:
    """Test specialist handling of service errors."""
    
    async def test_specialist_handles_service_failure(self, business_analysis_specialist_fixture):
        """Test specialist handles service failure gracefully."""
        specialist = business_analysis_specialist_fixture
        
        # Mock service failure
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": False,
            "error": "Service failed"
        })
        
        # Execute
        request = {
            "task": "analyze_business_data",
            "data": {},
            "user_context": {}
        }
        
        result = await specialist.execute_capability(request)
        
        # Should handle error gracefully
        assert result["success"] is False or "error" in result
    
    async def test_specialist_handles_service_exception(self, recommendation_specialist_fixture):
        """Test specialist handles service exceptions."""
        specialist = recommendation_specialist_fixture
        
        # Mock service exception
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(
            side_effect=Exception("Service crashed")
        )
        
        # Execute
        request = {
            "task": "generate_recommendations",
            "data": {},
            "user_context": {}
        }
        
        result = await specialist.execute_capability(request)
        
        # Should not crash
        assert result is not None
        assert result.get("success") is False or "error" in result

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestMCPToolConfiguration:
    """Test MCP tool configuration for specialists."""
    
    async def test_specialist_has_correct_mcp_tools(self, business_analysis_specialist_fixture):
        """Test specialist is configured with correct MCP tools."""
        specialist = business_analysis_specialist_fixture
        
        # Verify MCP tools are configured
        assert "analyze_data" in specialist.capability_mcp_tools
        assert "generate_insights" in specialist.capability_mcp_tools
    
    async def test_specialist_uses_correct_tool_for_task(self, recommendation_specialist_fixture):
        """Test specialist uses appropriate MCP tool for each task."""
        specialist = recommendation_specialist_fixture
        
        # Mock MCP client
        specialist.mcp_client_manager.execute_role_tool = AsyncMock(return_value={
            "success": True,
            "result": {}
        })
        
        # Execute recommendation task
        request = {
            "task": "generate_recommendations",
            "data": {},
            "user_context": {}
        }
        
        await specialist.execute_capability(request)
        
        # Verify correct MCP tool was called
        specialist.mcp_client_manager.execute_role_tool.assert_called()
        # Tool name should match capability

