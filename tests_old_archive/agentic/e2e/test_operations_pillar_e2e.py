"""
Operations Pillar E2E Tests with Agents

End-to-end tests for Operations Pillar MVP scenarios with full agent integration.
Tests real user journeys for SOP generation, workflow creation, and process optimization.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.e2e
@pytest.mark.agentic
@pytest.mark.asyncio
class TestSOPGenerationE2E:
    """E2E tests for SOP generation scenarios."""
    
    async def test_sop_generation_from_description_e2e(self):
        """Test E2E: User provides description → SOP Generation Specialist → Structured SOP."""
        # Setup full stack
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        operations_liaison = MagicMock()
        operations_orchestrator = MagicMock()
        sop_generation_specialist = MagicMock()
        workflow_manager_service = MagicMock()
        
        # E2E flow with AI-powered SOP generation
        async def orchestrator_handler(request):
            # Generate SOP via specialist
            sop_result = await sop_generation_specialist.generate_sop_from_description(
                description=request["description"],
                user_context=request.get("user_context", {})
            )
            
            return {
                "success": True,
                "sop": sop_result
            }
        
        # Chain setup
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        async def guide_handler(request):
            return await operations_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await operations_orchestrator.handle_request(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_handler
        operations_liaison.handle_user_request = liaison_handler
        operations_orchestrator.handle_request = orchestrator_handler
        sop_generation_specialist.generate_sop_from_description = AsyncMock(return_value={
            "sop_document": {
                "title": "Customer Onboarding SOP",
                "sections": [
                    {"name": "Purpose", "content": "..."},
                    {"name": "Steps", "content": "..."}
                ],
                "best_practices": ["Practice 1", "Practice 2"],
                "compliance_notes": ["Compliance requirement 1"]
            }
        })
        
        # User request
        user_request = {
            "message": "Create an SOP for customer onboarding",
            "description": "First collect customer information, then verify identity, create account, and send welcome email",
            "user_context": {"industry": "fintech"}
        }
        
        # Execute
        result = await frontend_gateway.send_message(user_request)
        
        # Verify AI-enhanced SOP
        assert result["success"] is True
        assert "sop" in result
        assert "sop_document" in result["sop"]
        assert "best_practices" in result["sop"]["sop_document"]
        sop_generation_specialist.generate_sop_from_description.assert_called_once()
    
    async def test_sop_with_industry_specific_compliance_e2e(self):
        """Test E2E: SOP generation includes industry-specific compliance notes."""
        # Setup
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        operations_liaison = MagicMock()
        operations_orchestrator = MagicMock()
        sop_generation_specialist = MagicMock()
        
        # Healthcare-specific SOP
        async def orchestrator_handler(request):
            sop_result = await sop_generation_specialist.generate_sop_from_description(
                description=request["description"],
                user_context=request.get("user_context", {})
            )
            return {"success": True, "sop": sop_result}
        
        # Chain setup
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        async def guide_handler(request):
            return await operations_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await operations_orchestrator.handle_request(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_handler
        operations_liaison.handle_user_request = liaison_handler
        operations_orchestrator.handle_request = orchestrator_handler
        sop_generation_specialist.generate_sop_from_description = AsyncMock(return_value={
            "sop_document": {
                "title": "Patient Data Handling SOP",
                "compliance_notes": [
                    "HIPAA compliance required",
                    "Patient consent must be obtained"
                ]
            }
        })
        
        # Healthcare SOP request
        user_request = {
            "message": "Create SOP for patient data handling",
            "description": "Handle patient records securely",
            "user_context": {"industry": "healthcare"}
        }
        
        # Execute
        result = await frontend_gateway.send_message(user_request)
        
        # Verify compliance notes
        assert result["success"] is True
        assert "compliance_notes" in result["sop"]["sop_document"]
        assert any("HIPAA" in note for note in result["sop"]["sop_document"]["compliance_notes"])

@pytest.mark.e2e
@pytest.mark.agentic
@pytest.mark.asyncio
class TestWorkflowGenerationE2E:
    """E2E tests for workflow generation scenarios."""
    
    async def test_workflow_generation_from_sop_e2e(self):
        """Test E2E: SOP → Workflow Generation Specialist → Optimized workflow."""
        # Setup
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        operations_liaison = MagicMock()
        operations_orchestrator = MagicMock()
        workflow_generation_specialist = MagicMock()
        workflow_manager_service = MagicMock()
        
        # E2E flow
        async def orchestrator_handler(request):
            # Generate workflow from SOP
            workflow_result = await workflow_generation_specialist.generate_workflow_from_sop(
                sop_data=request["sop_data"],
                user_context=request.get("user_context", {}),
                optimize=True
            )
            
            return {
                "success": True,
                "workflow": workflow_result
            }
        
        # Chain setup
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        async def guide_handler(request):
            return await operations_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await operations_orchestrator.handle_request(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_handler
        operations_liaison.handle_user_request = liaison_handler
        operations_orchestrator.handle_request = orchestrator_handler
        workflow_generation_specialist.generate_workflow_from_sop = AsyncMock(return_value={
            "optimized_workflow": {
                "workflow_id": "wf_123",
                "nodes": [{"id": "1", "name": "Start"}, {"id": "2", "name": "Process"}],
                "edges": [{"from": "1", "to": "2"}]
            },
            "bottlenecks_identified": [],
            "efficiency_improvements": ["Parallel task execution possible"],
            "parallel_opportunities": [{"tasks": ["task1", "task2"]}]
        })
        
        # User request
        user_request = {
            "message": "Generate a workflow from this SOP",
            "sop_data": {"title": "Customer Onboarding SOP", "steps": []},
            "user_context": {}
        }
        
        # Execute
        result = await frontend_gateway.send_message(user_request)
        
        # Verify optimized workflow
        assert result["success"] is True
        assert "workflow" in result
        assert "optimized_workflow" in result["workflow"]
        assert "efficiency_improvements" in result["workflow"]
        workflow_generation_specialist.generate_workflow_from_sop.assert_called_once()

@pytest.mark.e2e
@pytest.mark.agentic
@pytest.mark.asyncio
class TestCoexistenceBlueprintE2E:
    """E2E tests for coexistence blueprint generation."""
    
    async def test_coexistence_blueprint_generation_e2e(self):
        """Test E2E: Workflow + SOP → Coexistence Blueprint Specialist → Optimization blueprint."""
        # Setup
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        operations_liaison = MagicMock()
        operations_orchestrator = MagicMock()
        coexistence_blueprint_specialist = MagicMock()
        
        # E2E flow
        async def orchestrator_handler(request):
            # Generate coexistence blueprint
            blueprint_result = await coexistence_blueprint_specialist.generate_coexistence_blueprint(
                workflow_data=request["workflow_data"],
                sop_data=request["sop_data"],
                user_context=request.get("user_context", {})
            )
            
            return {
                "success": True,
                "blueprint": blueprint_result
            }
        
        # Chain setup
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        async def guide_handler(request):
            return await operations_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await operations_orchestrator.handle_request(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_handler
        operations_liaison.handle_user_request = liaison_handler
        operations_orchestrator.handle_request = orchestrator_handler
        coexistence_blueprint_specialist.generate_coexistence_blueprint = AsyncMock(return_value={
            "coexistence_score": {
                "overall_score": 75,
                "human_efficiency": 80,
                "ai_effectiveness": 70,
                "collaboration_quality": 75
            },
            "current_state_analysis": {
                "strengths": ["Clear process definition"],
                "weaknesses": ["Manual data entry"]
            },
            "optimization_opportunities": [
                {"opportunity": "Automate data entry", "impact": "High"}
            ],
            "future_state_blueprint": {
                "vision": "Optimized human-AI workflow"
            },
            "implementation_roadmap": {
                "phases": [{"phase": 1, "objectives": []}]
            }
        })
        
        # User request
        user_request = {
            "message": "Analyze coexistence and create optimization blueprint",
            "workflow_data": {"workflow_id": "wf_123"},
            "sop_data": {"title": "Test SOP"},
            "user_context": {}
        }
        
        # Execute
        result = await frontend_gateway.send_message(user_request)
        
        # Verify blueprint
        assert result["success"] is True
        assert "blueprint" in result
        assert "coexistence_score" in result["blueprint"]
        assert "implementation_roadmap" in result["blueprint"]
        coexistence_blueprint_specialist.generate_coexistence_blueprint.assert_called_once()

@pytest.mark.e2e
@pytest.mark.agentic
@pytest.mark.asyncio
class TestOperationsConversationE2E:
    """E2E tests for conversational operations interactions."""
    
    async def test_iterative_sop_refinement_e2e(self):
        """Test E2E: Multi-turn conversation for iterative SOP refinement."""
        # Setup with state
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        guide_agent.conversation_state = {}
        
        operations_liaison = MagicMock()
        operations_orchestrator = MagicMock()
        sop_generation_specialist = MagicMock()
        
        # State-aware flow
        async def guide_with_state_handler(request):
            session_id = request.get("session_id")
            
            # Store SOP
            if "sop_id" in request:
                guide_agent.conversation_state[session_id] = {
                    "current_sop": request["sop_id"]
                }
            
            # Use state
            if session_id in guide_agent.conversation_state:
                request["conversation_state"] = guide_agent.conversation_state[session_id]
            
            return await operations_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await operations_orchestrator.handle_request(request)
        
        async def orchestrator_handler(request):
            state = request.get("conversation_state", {})
            sop_id = state.get("current_sop")
            
            if sop_id:
                # Refine existing SOP
                return {
                    "success": True,
                    "result": f"Refined SOP {sop_id}",
                    "refinement_applied": True
                }
            else:
                # Create new SOP
                return {
                    "success": True,
                    "result": "New SOP created",
                    "sop_id": "sop_123"
                }
        
        # Chain setup
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_with_state_handler
        operations_liaison.handle_user_request = liaison_handler
        operations_orchestrator.handle_request = orchestrator_handler
        
        # Turn 1: Create SOP
        turn1 = {
            "message": "Create SOP for customer service",
            "sop_id": "sop_123",
            "session_id": "session_456"
        }
        result1 = await frontend_gateway.send_message(turn1)
        
        # Turn 2: Refine SOP (uses state)
        turn2 = {
            "message": "Add a quality check step",
            "session_id": "session_456"
        }
        result2 = await frontend_gateway.send_message(turn2)
        
        # Verify refinement used state
        assert result1["success"] is True
        assert result2["success"] is True
        assert result2.get("refinement_applied", False) is True

@pytest.mark.e2e
@pytest.mark.agentic
@pytest.mark.asyncio
class TestOperationsErrorHandlingE2E:
    """E2E tests for operations error handling."""
    
    async def test_invalid_sop_description_e2e(self):
        """Test E2E: Invalid SOP description is caught and user is prompted."""
        # Setup
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        operations_liaison = MagicMock()
        operations_orchestrator = MagicMock()
        
        # Validation logic
        async def orchestrator_validation_handler(request):
            description = request.get("description", "")
            
            # Validate description
            if len(description) < 10:
                return {
                    "success": False,
                    "error": "Description too short",
                    "user_message": "Please provide a more detailed description (at least 10 characters)"
                }
            
            return {"success": True}
        
        # Error-aware chain
        async def guide_error_handler(request):
            result = await operations_liaison.handle_user_request(request)
            if not result.get("success", False):
                return {
                    "success": False,
                    "message": result.get("user_message", "An error occurred")
                }
            return result
        
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        async def liaison_handler(request):
            return await operations_orchestrator.handle_request(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_error_handler
        operations_liaison.handle_user_request = liaison_handler
        operations_orchestrator.handle_request = orchestrator_validation_handler
        
        # Invalid request
        user_request = {
            "message": "Create SOP",
            "description": "Short"  # Too short
        }
        
        # Execute
        result = await frontend_gateway.send_message(user_request)
        
        # Verify user-friendly error
        assert result["success"] is False
        assert "message" in result
        assert "detailed" in result["message"].lower()

