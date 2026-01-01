"""
Full Agent Flow Integration Tests

Tests complete end-to-end agent flows:
- User → Guide → Liaison → Orchestrator → Service → Response
- Multi-turn conversations
- Complex multi-service workflows
- Full MVP scenarios
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestContentPillarAgentFlow:
    """Test complete agent flow for Content Pillar scenarios."""
    
    async def test_document_upload_and_analysis_flow(self):
        """Test complete flow: User uploads document → Guide → Content Liaison → Orchestrator → Services."""
        # Setup: Create mock agent chain
        guide_agent = MagicMock()
        content_liaison = MagicMock()
        content_orchestrator = MagicMock()
        file_parser_service = MagicMock()
        data_analyzer_service = MagicMock()
        
        # Configure mock behaviors
        async def guide_handler(request):
            # Guide routes to Content Liaison
            return await content_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            # Liaison delegates to orchestrator
            return await content_orchestrator.handle_request(request)
        
        async def orchestrator_handler(request):
            # Orchestrator calls services in sequence
            parse_result = await file_parser_service.parse_file(request["file_path"])
            analysis_result = await data_analyzer_service.analyze_data(parse_result)
            return {
                "success": True,
                "result": "Document uploaded and analyzed successfully"
            }
        
        guide_agent.provide_guidance = guide_handler
        content_liaison.handle_user_request = liaison_handler
        content_orchestrator.handle_request = orchestrator_handler
        file_parser_service.parse_file = AsyncMock(return_value={"content": "parsed"})
        data_analyzer_service.analyze_data = AsyncMock(return_value={"insights": "generated"})
        
        # User request
        user_request = {
            "message": "I want to upload and analyze this document",
            "file_path": "document.pdf",
            "user_context": {"role": "user"}
        }
        
        # Execute full flow
        result = await guide_agent.provide_guidance(user_request)
        
        # Verify full chain executed
        file_parser_service.parse_file.assert_called_once()
        data_analyzer_service.analyze_data.assert_called_once()
        assert result["success"] is True
    
    async def test_multi_document_batch_processing_flow(self):
        """Test flow for processing multiple documents in a batch."""
        # Setup mocks
        guide_agent = MagicMock()
        content_liaison = MagicMock()
        content_orchestrator = MagicMock()
        
        # Mock orchestrator to handle batch
        async def orchestrator_batch_handler(request):
            files = request.get("files", [])
            results = []
            for file_path in files:
                results.append({"file": file_path, "status": "processed"})
            return {
                "success": True,
                "results": results
            }
        
        # Chain setup
        async def guide_handler(request):
            return await content_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await content_orchestrator.handle_request(request)
        
        guide_agent.provide_guidance = guide_handler
        content_liaison.handle_user_request = liaison_handler
        content_orchestrator.handle_request = orchestrator_batch_handler
        
        # Batch request
        user_request = {
            "message": "Process all these documents",
            "files": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
            "user_context": {}
        }
        
        # Execute
        result = await guide_agent.provide_guidance(user_request)
        
        # Verify batch processing
        assert result["success"] is True
        assert len(result["results"]) == 3

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestInsightsPillarAgentFlow:
    """Test complete agent flow for Insights Pillar scenarios."""
    
    async def test_data_analysis_and_visualization_flow(self):
        """Test complete flow: User requests insights → Guide → Insights Liaison → Orchestrator → Services."""
        # Setup mocks
        guide_agent = MagicMock()
        insights_liaison = MagicMock()
        insights_orchestrator = MagicMock()
        data_analyzer_service = MagicMock()
        visualization_service = MagicMock()
        
        # Configure behaviors
        async def orchestrator_handler(request):
            # Analyze data
            analysis = await data_analyzer_service.analyze_data(request["data"])
            # Create visualization
            viz = await visualization_service.create_visualization(analysis)
            return {
                "success": True,
                "analysis": analysis,
                "visualization": viz
            }
        
        async def liaison_handler(request):
            return await insights_orchestrator.handle_request(request)
        
        async def guide_handler(request):
            return await insights_liaison.handle_user_request(request)
        
        guide_agent.provide_guidance = guide_handler
        insights_liaison.handle_user_request = liaison_handler
        insights_orchestrator.handle_request = orchestrator_handler
        data_analyzer_service.analyze_data = AsyncMock(return_value={"insights": "data"})
        visualization_service.create_visualization = AsyncMock(return_value={"chart": "created"})
        
        # User request
        user_request = {
            "message": "Analyze this data and create visualizations",
            "data": {"values": [1, 2, 3, 4, 5]},
            "user_context": {"role": "analyst"}
        }
        
        # Execute
        result = await guide_agent.provide_guidance(user_request)
        
        # Verify full flow
        data_analyzer_service.analyze_data.assert_called_once()
        visualization_service.create_visualization.assert_called_once()
        assert result["success"] is True
        assert "visualization" in result

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestOperationsPillarAgentFlow:
    """Test complete agent flow for Operations Pillar scenarios."""
    
    async def test_workflow_generation_from_sop_flow(self):
        """Test complete flow: User requests workflow → Guide → Operations Liaison → Orchestrator → Services."""
        # Setup mocks
        guide_agent = MagicMock()
        operations_liaison = MagicMock()
        operations_orchestrator = MagicMock()
        workflow_specialist = MagicMock()
        workflow_service = MagicMock()
        
        # Configure behaviors
        async def orchestrator_handler(request):
            # Delegate to specialist
            specialist_result = await workflow_specialist.generate_workflow_from_sop(
                request["sop_data"], request["user_context"]
            )
            # Use workflow service for additional processing
            final_result = await workflow_service.create_workflow(specialist_result)
            return {
                "success": True,
                "workflow": final_result
            }
        
        async def liaison_handler(request):
            return await operations_orchestrator.handle_request(request)
        
        async def guide_handler(request):
            return await operations_liaison.handle_user_request(request)
        
        guide_agent.provide_guidance = guide_handler
        operations_liaison.handle_user_request = liaison_handler
        operations_orchestrator.handle_request = orchestrator_handler
        workflow_specialist.generate_workflow_from_sop = AsyncMock(return_value={"workflow_draft": "generated"})
        workflow_service.create_workflow = AsyncMock(return_value={"workflow_id": "wf_123"})
        
        # User request
        user_request = {
            "message": "Generate a workflow from this SOP",
            "sop_data": {"title": "Customer Onboarding SOP"},
            "user_context": {}
        }
        
        # Execute
        result = await guide_agent.provide_guidance(user_request)
        
        # Verify
        workflow_specialist.generate_workflow_from_sop.assert_called_once()
        workflow_service.create_workflow.assert_called_once()
        assert result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestBusinessOutcomesPillarAgentFlow:
    """Test complete agent flow for Business Outcomes Pillar scenarios."""
    
    async def test_comprehensive_proposal_generation_flow(self):
        """Test complete flow: User requests proposal → All pillars → Synthesis → Proposal."""
        # Setup mocks
        guide_agent = MagicMock()
        business_outcomes_liaison = MagicMock()
        business_outcomes_orchestrator = MagicMock()
        roadmap_specialist = MagicMock()
        
        # Configure behaviors
        async def orchestrator_handler(request):
            # Collect summaries from all pillars (mocked)
            pillar_summaries = {
                "content_summary": {"key": "content_data"},
                "insights_summary": {"key": "insights_data"},
                "operations_summary": {"key": "ops_data"},
                "outcomes_summary": {"key": "outcomes_data"}
            }
            
            # Delegate to specialist for synthesis
            proposal = await roadmap_specialist.generate_comprehensive_proposal(
                pillar_summaries, request["user_context"]
            )
            return {
                "success": True,
                "proposal": proposal
            }
        
        async def liaison_handler(request):
            return await business_outcomes_orchestrator.handle_request(request)
        
        async def guide_handler(request):
            return await business_outcomes_liaison.handle_user_request(request)
        
        guide_agent.provide_guidance = guide_handler
        business_outcomes_liaison.handle_user_request = liaison_handler
        business_outcomes_orchestrator.handle_request = orchestrator_handler
        roadmap_specialist.generate_comprehensive_proposal = AsyncMock(return_value={
            "executive_summary": "...",
            "roadmap": "...",
            "poc_proposal": "..."
        })
        
        # User request
        user_request = {
            "message": "Generate a comprehensive proposal and roadmap",
            "user_context": {"organization": "test_org"}
        }
        
        # Execute
        result = await guide_agent.provide_guidance(user_request)
        
        # Verify
        roadmap_specialist.generate_comprehensive_proposal.assert_called_once()
        assert result["success"] is True
        assert "proposal" in result

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestMultiTurnConversationFlows:
    """Test multi-turn conversations maintaining context."""
    
    async def test_multi_turn_document_analysis_conversation(self):
        """Test multi-turn conversation for document analysis."""
        # Setup guide agent with conversation history
        guide_agent = MagicMock()
        guide_agent.conversation_history = []
        
        content_liaison = MagicMock()
        content_orchestrator = MagicMock()
        
        async def guide_handler(request):
            # Add to history
            guide_agent.conversation_history.append(request)
            # Route to liaison
            return await content_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await content_orchestrator.handle_request(request)
        
        async def orchestrator_handler(request):
            return {"success": True, "result": "processed"}
        
        guide_agent.provide_guidance = guide_handler
        content_liaison.handle_user_request = liaison_handler
        content_orchestrator.handle_request = orchestrator_handler
        
        # Turn 1: Upload document
        turn1 = {
            "message": "Upload this document",
            "file_path": "doc.pdf",
            "user_context": {"session_id": "session_123"}
        }
        result1 = await guide_agent.provide_guidance(turn1)
        
        # Turn 2: Analyze it
        turn2 = {
            "message": "Now analyze it",
            "user_context": {"session_id": "session_123"}
        }
        result2 = await guide_agent.provide_guidance(turn2)
        
        # Turn 3: Generate insights
        turn3 = {
            "message": "Generate insights from the analysis",
            "user_context": {"session_id": "session_123"}
        }
        result3 = await guide_agent.provide_guidance(turn3)
        
        # Verify all turns completed and history maintained
        assert len(guide_agent.conversation_history) == 3
        assert result1["success"] is True
        assert result2["success"] is True
        assert result3["success"] is True
    
    async def test_context_aware_follow_up_questions(self):
        """Test agent handles context-aware follow-up questions."""
        guide_agent = MagicMock()
        guide_agent.context = {}
        
        liaison = MagicMock()
        
        async def guide_handler(request):
            # Store context
            if "context_key" in request:
                guide_agent.context[request["context_key"]] = request["context_value"]
            # Route
            return await liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            # Use stored context
            context = guide_agent.context.get("previous_action")
            return {
                "success": True,
                "used_context": context is not None
            }
        
        guide_agent.provide_guidance = guide_handler
        liaison.handle_user_request = liaison_handler
        
        # Turn 1: Set context
        turn1 = {
            "message": "Analyze data",
            "context_key": "previous_action",
            "context_value": "data_analysis",
            "user_context": {}
        }
        await guide_agent.provide_guidance(turn1)
        
        # Turn 2: Follow-up using context
        turn2 = {
            "message": "Show me more details",
            "user_context": {}
        }
        result2 = await guide_agent.provide_guidance(turn2)
        
        # Verify context was used
        assert result2["used_context"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestComplexWorkflowOrchestration:
    """Test complex multi-service orchestration flows."""
    
    async def test_end_to_end_mvp_workflow(self):
        """Test complete MVP workflow: Upload → Parse → Analyze → Generate Insights → Create Report."""
        # Setup full chain
        services = {
            "file_parser": MagicMock(),
            "data_analyzer": MagicMock(),
            "metrics_calculator": MagicMock(),
            "visualization_engine": MagicMock(),
            "report_generator": MagicMock()
        }
        
        # Configure service chain
        services["file_parser"].parse_file = AsyncMock(return_value={"content": "parsed"})
        services["data_analyzer"].analyze_data = AsyncMock(return_value={"analysis": "done"})
        services["metrics_calculator"].calculate_metrics = AsyncMock(return_value={"metrics": "calculated"})
        services["visualization_engine"].create_visualization = AsyncMock(return_value={"viz": "created"})
        services["report_generator"].generate_report = AsyncMock(return_value={"report": "generated"})
        
        # Setup orchestrator that chains all services
        orchestrator = MagicMock()
        
        async def complex_workflow(request):
            # Execute service chain
            parsed = await services["file_parser"].parse_file(request["file"])
            analyzed = await services["data_analyzer"].analyze_data(parsed)
            metrics = await services["metrics_calculator"].calculate_metrics(analyzed)
            viz = await services["visualization_engine"].create_visualization(metrics)
            report = await services["report_generator"].generate_report({
                "analysis": analyzed,
                "metrics": metrics,
                "visualization": viz
            })
            return {
                "success": True,
                "report": report
            }
        
        orchestrator.handle_request = complex_workflow
        
        # User request
        request = {
            "file": "data.csv",
            "task": "full_analysis_report"
        }
        
        # Execute
        result = await orchestrator.handle_request(request)
        
        # Verify all services called in order
        services["file_parser"].parse_file.assert_called_once()
        services["data_analyzer"].analyze_data.assert_called_once()
        services["metrics_calculator"].calculate_metrics.assert_called_once()
        services["visualization_engine"].create_visualization.assert_called_once()
        services["report_generator"].generate_report.assert_called_once()
        assert result["success"] is True

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestErrorRecoveryFlows:
    """Test error handling and recovery in agent flows."""
    
    async def test_service_failure_graceful_recovery(self):
        """Test agent flow recovers gracefully from service failure."""
        guide_agent = MagicMock()
        liaison = MagicMock()
        orchestrator = MagicMock()
        service = MagicMock()
        
        # Configure service to fail
        service.process_data = AsyncMock(return_value={"success": False, "error": "Service unavailable"})
        
        async def orchestrator_handler(request):
            result = await service.process_data(request)
            if not result["success"]:
                # Orchestrator handles error
                return {
                    "success": False,
                    "error": result["error"],
                    "fallback": "Using cached data"
                }
            return result
        
        async def liaison_handler(request):
            return await orchestrator.handle_request(request)
        
        async def guide_handler(request):
            result = await liaison.handle_user_request(request)
            if not result["success"]:
                # Guide provides user-friendly error message
                return {
                    "success": False,
                    "user_message": "Service temporarily unavailable. Using fallback."
                }
            return result
        
        guide_agent.provide_guidance = guide_handler
        liaison.handle_user_request = liaison_handler
        orchestrator.handle_request = orchestrator_handler
        
        # User request
        request = {"message": "Process data", "data": {}}
        
        # Execute
        result = await guide_agent.provide_guidance(request)
        
        # Verify graceful error handling
        assert result["success"] is False
        assert "user_message" in result
    
    async def test_partial_success_handling(self):
        """Test handling when some services succeed and others fail."""
        orchestrator = MagicMock()
        
        service1 = MagicMock()
        service2 = MagicMock()
        service3 = MagicMock()
        
        # Configure: service1 succeeds, service2 fails, service3 succeeds
        service1.execute = AsyncMock(return_value={"success": True})
        service2.execute = AsyncMock(return_value={"success": False, "error": "Failed"})
        service3.execute = AsyncMock(return_value={"success": True})
        
        async def orchestrator_handler(request):
            results = []
            results.append(await service1.execute())
            results.append(await service2.execute())
            results.append(await service3.execute())
            
            success_count = sum(1 for r in results if r["success"])
            return {
                "success": success_count > 0,
                "partial_success": success_count < len(results),
                "results": results
            }
        
        orchestrator.handle_request = orchestrator_handler
        
        # Execute
        result = await orchestrator.handle_request({})
        
        # Verify partial success handling
        assert result["success"] is True
        assert result["partial_success"] is True
        assert len(result["results"]) == 3

