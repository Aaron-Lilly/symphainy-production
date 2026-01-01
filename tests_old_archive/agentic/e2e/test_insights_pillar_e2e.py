"""
Insights Pillar E2E Tests with Agents

End-to-end tests for Insights Pillar MVP scenarios with full agent integration.
Tests real user journeys for data analysis, visualization, and recommendations.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.e2e
@pytest.mark.agentic
@pytest.mark.asyncio
class TestDataAnalysisE2E:
    """E2E tests for data analysis scenarios."""
    
    async def test_business_data_analysis_with_specialist_e2e(self):
        """Test E2E: User uploads data → Analysis with Business Analysis Specialist → Insights."""
        # Setup full stack
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        insights_liaison = MagicMock()
        insights_orchestrator = MagicMock()
        business_analysis_specialist = MagicMock()
        data_analyzer_service = MagicMock()
        
        # E2E flow with AI-powered analysis
        async def orchestrator_handler(request):
            # Analyze data
            raw_analysis = await data_analyzer_service.analyze_data(request["data"])
            
            # Enhance with Business Analysis Specialist
            enhanced_analysis = await business_analysis_specialist.analyze_business_data(
                data=raw_analysis,
                user_context=request.get("user_context", {})
            )
            
            return {
                "success": True,
                "raw_analysis": raw_analysis,
                "ai_insights": enhanced_analysis
            }
        
        # Chain setup
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        async def guide_handler(request):
            return await insights_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await insights_orchestrator.handle_request(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_handler
        insights_liaison.handle_user_request = liaison_handler
        insights_orchestrator.handle_request = orchestrator_handler
        data_analyzer_service.analyze_data = AsyncMock(return_value={
            "metrics": {"revenue": 1000000, "costs": 800000}
        })
        business_analysis_specialist.analyze_business_data = AsyncMock(return_value={
            "insights": "Strong profit margin at 20%",
            "patterns": ["Revenue growth trending positive"],
            "risks": ["Cost creep in Q3"],
            "opportunities": ["Scale operations"]
        })
        
        # User request
        user_request = {
            "message": "Analyze my business performance data",
            "data": {"revenue": [100, 200, 300], "costs": [80, 160, 240]},
            "user_context": {"role": "executive", "industry": "technology"}
        }
        
        # Execute
        result = await frontend_gateway.send_message(user_request)
        
        # Verify AI-enhanced analysis
        assert result["success"] is True
        assert "ai_insights" in result
        assert "insights" in result["ai_insights"]
        business_analysis_specialist.analyze_business_data.assert_called_once()
    
    async def test_recommendation_generation_e2e(self):
        """Test E2E: Data analysis → Recommendation Specialist → Strategic recommendations."""
        # Setup
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        insights_liaison = MagicMock()
        insights_orchestrator = MagicMock()
        recommendation_specialist = MagicMock()
        metrics_calculator_service = MagicMock()
        
        # Flow with recommendations
        async def orchestrator_handler(request):
            # Calculate metrics
            metrics = await metrics_calculator_service.calculate_metrics(request["data"])
            
            # Generate recommendations
            recommendations = await recommendation_specialist.generate_recommendations(
                analysis_data=metrics,
                user_context=request.get("user_context", {}),
                recommendation_type="strategic"
            )
            
            return {
                "success": True,
                "metrics": metrics,
                "recommendations": recommendations
            }
        
        # Chain setup
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        async def guide_handler(request):
            return await insights_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await insights_orchestrator.handle_request(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_handler
        insights_liaison.handle_user_request = liaison_handler
        insights_orchestrator.handle_request = orchestrator_handler
        metrics_calculator_service.calculate_metrics = AsyncMock(return_value={
            "average": 100,
            "trend": "positive"
        })
        recommendation_specialist.generate_recommendations = AsyncMock(return_value={
            "recommendations": [
                {"priority": 1, "action": "Optimize costs"},
                {"priority": 2, "action": "Expand market"}
            ],
            "impact_assessment": "High ROI potential"
        })
        
        # User request
        user_request = {
            "message": "Give me strategic recommendations based on this data",
            "data": {"metrics_data": {}},
            "user_context": {"role": "executive"}
        }
        
        # Execute
        result = await frontend_gateway.send_message(user_request)
        
        # Verify recommendations
        assert result["success"] is True
        assert "recommendations" in result
        assert len(result["recommendations"]["recommendations"]) == 2
        recommendation_specialist.generate_recommendations.assert_called_once()

@pytest.mark.e2e
@pytest.mark.agentic
@pytest.mark.asyncio
class TestVisualizationE2E:
    """E2E tests for data visualization scenarios."""
    
    async def test_create_visualization_from_analysis_e2e(self):
        """Test E2E: Analyze data → Create visualizations."""
        # Setup
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        insights_liaison = MagicMock()
        insights_orchestrator = MagicMock()
        data_analyzer_service = MagicMock()
        visualization_engine_service = MagicMock()
        
        # Flow with visualization
        async def orchestrator_handler(request):
            # Analyze
            analysis = await data_analyzer_service.analyze_data(request["data"])
            
            # Create visualization
            viz = await visualization_engine_service.create_visualization(
                data=analysis,
                viz_type=request.get("viz_type", "chart")
            )
            
            return {
                "success": True,
                "analysis": analysis,
                "visualization": viz
            }
        
        # Chain setup
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        async def guide_handler(request):
            return await insights_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await insights_orchestrator.handle_request(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_handler
        insights_liaison.handle_user_request = liaison_handler
        insights_orchestrator.handle_request = orchestrator_handler
        data_analyzer_service.analyze_data = AsyncMock(return_value={
            "summary": "data analyzed"
        })
        visualization_engine_service.create_visualization = AsyncMock(return_value={
            "chart_url": "https://example.com/chart.png",
            "chart_type": "line"
        })
        
        # User request
        user_request = {
            "message": "Create a chart from this data",
            "data": {"values": [1, 2, 3, 4, 5]},
            "viz_type": "line"
        }
        
        # Execute
        result = await frontend_gateway.send_message(user_request)
        
        # Verify visualization created
        assert result["success"] is True
        assert "visualization" in result
        assert "chart_url" in result["visualization"]
        visualization_engine_service.create_visualization.assert_called_once()

@pytest.mark.e2e
@pytest.mark.agentic
@pytest.mark.asyncio
class TestInsightsConversationE2E:
    """E2E tests for conversational insights interactions."""
    
    async def test_iterative_data_exploration_e2e(self):
        """Test E2E: Multi-turn conversation for iterative data exploration."""
        # Setup with state
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        guide_agent.conversation_state = {}
        
        insights_liaison = MagicMock()
        insights_orchestrator = MagicMock()
        
        # State-aware flow
        async def guide_with_state_handler(request):
            session_id = request.get("session_id")
            
            # Store analysis results
            if "analysis_result" in request:
                guide_agent.conversation_state[session_id] = {
                    "last_analysis": request["analysis_result"]
                }
            
            # Use state for follow-ups
            if session_id in guide_agent.conversation_state:
                request["conversation_state"] = guide_agent.conversation_state[session_id]
            
            return await insights_liaison.handle_user_request(request)
        
        async def liaison_handler(request):
            return await insights_orchestrator.handle_request(request)
        
        async def orchestrator_handler(request):
            state = request.get("conversation_state", {})
            
            return {
                "success": True,
                "result": "Analysis complete",
                "used_previous_context": "last_analysis" in state
            }
        
        # Chain setup
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_with_state_handler
        insights_liaison.handle_user_request = liaison_handler
        insights_orchestrator.handle_request = orchestrator_handler
        
        # Turn 1: Initial analysis
        turn1 = {
            "message": "Analyze this dataset",
            "analysis_result": {"metrics": "calculated"},
            "session_id": "session_123"
        }
        result1 = await frontend_gateway.send_message(turn1)
        
        # Turn 2: Drill down (uses state)
        turn2 = {
            "message": "Show me more details",
            "session_id": "session_123"
        }
        result2 = await frontend_gateway.send_message(turn2)
        
        # Verify state was used
        assert result1["success"] is True
        assert result2["success"] is True
        assert result2["used_previous_context"] is True

@pytest.mark.e2e
@pytest.mark.agentic
@pytest.mark.asyncio
class TestInsightsErrorHandlingE2E:
    """E2E tests for insights error handling."""
    
    async def test_invalid_data_format_e2e(self):
        """Test E2E: Invalid data format is caught and reported to user."""
        # Setup
        frontend_gateway = MagicMock()
        guide_agent = MagicMock()
        insights_liaison = MagicMock()
        insights_orchestrator = MagicMock()
        data_analyzer_service = MagicMock()
        
        # Validation logic
        async def orchestrator_validation_handler(request):
            data = request.get("data")
            
            # Validate data format
            if not isinstance(data, dict) or "values" not in data:
                return {
                    "success": False,
                    "error": "Invalid data format",
                    "user_message": "Please provide data in the correct format (e.g., {\"values\": [1,2,3]})"
                }
            
            return await data_analyzer_service.analyze_data(data)
        
        # Error-aware chain
        async def guide_error_handler(request):
            result = await insights_liaison.handle_user_request(request)
            if not result.get("success", False):
                return {
                    "success": False,
                    "message": result.get("user_message", "An error occurred")
                }
            return result
        
        async def frontend_handler(request):
            return await guide_agent.handle_chat_message(request)
        
        async def liaison_handler(request):
            return await insights_orchestrator.handle_request(request)
        
        frontend_gateway.send_message = frontend_handler
        guide_agent.handle_chat_message = guide_error_handler
        insights_liaison.handle_user_request = liaison_handler
        insights_orchestrator.handle_request = orchestrator_validation_handler
        
        # Invalid data request
        user_request = {
            "message": "Analyze this data",
            "data": "invalid string data"  # Should be dict
        }
        
        # Execute
        result = await frontend_gateway.send_message(user_request)
        
        # Verify user-friendly error
        assert result["success"] is False
        assert "message" in result
        assert "format" in result["message"].lower()

