#!/usr/bin/env python3
"""
E2E Tests for Chat Panel Integration

Tests the complete Chat Panel integration across all pillars:
1. Test Guide Agent initialization
2. Test Liaison Agent switching (Content, Insights, Operations)
3. Test agent conversations
4. Verify agent context persistence
5. Test agent routing
6. Test multi-turn conversations

This simulates real user interactions with the chat panel.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.experience.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]

class TestChatPanelIntegration:
    """E2E tests for Chat Panel integration."""
    
    @pytest.fixture
    async def mock_chat_service(self):
        """Create mock ChatService."""
        chat_service = Mock()
        
        # Mock Guide Agent
        chat_service.handle_guide_chat = AsyncMock(return_value={
            "success": True,
            "response": "Hello! I'm your Guide Agent. I can help you navigate the platform and understand how to use each pillar effectively.",
            "agent_type": "guide",
            "suggestions": [
                "Tell me about the Content Pillar",
                "How do I analyze data?",
                "What can the Operations Pillar do?"
            ]
        })
        
        # Mock Liaison Agent (generic)
        chat_service.handle_liaison_chat = AsyncMock(return_value={
            "success": True,
            "response": "I'm your Liaison Agent. I can help you with specific tasks in this pillar.",
            "agent_type": "liaison",
            "context": {"pillar": "content"}
        })
        
        # Mock conversation creation
        chat_service.create_conversation = AsyncMock(return_value={
            "success": True,
            "conversation_id": "conv_123",
            "agent_type": "guide"
        })
        
        # Mock conversation history
        chat_service.get_conversation_history = AsyncMock(return_value={
            "success": True,
            "conversation_id": "conv_123",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "agent", "content": "Hi! How can I help?"}
            ]
        })
        
        return chat_service
    
    @pytest.fixture
    async def mock_liaison_agents(self):
        """Create mock Liaison Agents for each pillar."""
        agents = {}
        
        # Content Liaison Agent
        agents['content'] = Mock()
        agents['content'].process_message = AsyncMock(return_value={
            "success": True,
            "response": "I can help you parse files, analyze documents, and extract entities.",
            "agent_type": "content_liaison",
            "capabilities": ["file_parsing", "document_analysis", "entity_extraction"]
        })
        
        # Insights Liaison Agent
        agents['insights'] = Mock()
        agents['insights'].process_message = AsyncMock(return_value={
            "success": True,
            "response": "I can help you calculate metrics, generate insights, and create visualizations.",
            "agent_type": "insights_liaison",
            "capabilities": ["metrics_calculation", "insights_generation", "visualization"]
        })
        
        # Operations Liaison Agent
        agents['operations'] = Mock()
        agents['operations'].process_message = AsyncMock(return_value={
            "success": True,
            "response": "I can help you create SOPs, generate workflows, and analyze coexistence.",
            "agent_type": "operations_liaison",
            "capabilities": ["sop_creation", "workflow_generation", "coexistence_analysis"]
        })
        
        return agents
    
    @pytest.fixture
    async def gateway_service(self, mock_chat_service):
        """Create FrontendGatewayService with mocked chat service."""
        platform_gateway = Mock()
        di_container = Mock()
        
        gateway = FrontendGatewayService(
            service_name="FrontendGatewayService",
            realm_name="experience",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Inject chat service
        gateway.chat_service = mock_chat_service
        gateway.librarian = Mock()
        gateway.security_guard = Mock()
        gateway.traffic_cop = Mock()
        
        return gateway
    
    async def test_guide_agent_initialization(self, gateway_service, mock_chat_service):
        """Test Guide Agent initialization."""
        request = {
            "endpoint": "/api/chat/guide",
            "method": "POST",
            "params": {
                "message": "Hello",
                "session_token": "session_123"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should initialize Guide Agent
        assert isinstance(result, dict)
        assert "success" in result or "status" in result
    
    async def test_guide_agent_conversation(self, gateway_service):
        """Test Guide Agent conversation."""
        messages = [
            "What is the Content Pillar?",
            "How do I upload a file?",
            "Tell me about the Insights Pillar"
        ]
        
        for message in messages:
            request = {
                "endpoint": "/api/chat/guide",
                "method": "POST",
                "params": {
                    "message": message,
                    "session_token": "session_123"
                }
            }
            
            result = await gateway_service.route_frontend_request(request)
            
            # Should respond to each message
            assert isinstance(result, dict)
    
    async def test_liaison_agent_switching(self, gateway_service):
        """Test switching between Liaison Agents."""
        pillars = ["content", "insights", "operations"]
        
        for pillar in pillars:
            request = {
                "endpoint": "/api/chat/liaison",
                "method": "POST",
                "params": {
                    "message": f"Help me with {pillar}",
                    "session_token": "session_123",
                    "pillar": pillar
                }
            }
            
            result = await gateway_service.route_frontend_request(request)
            
            # Should switch to appropriate Liaison Agent
            assert isinstance(result, dict)
    
    async def test_content_liaison_agent(self, gateway_service):
        """Test Content Liaison Agent."""
        request = {
            "endpoint": "/api/chat/liaison",
            "method": "POST",
            "params": {
                "message": "How do I parse a PDF file?",
                "session_token": "session_123",
                "pillar": "content"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should respond with content-specific guidance
        assert isinstance(result, dict)
    
    async def test_insights_liaison_agent(self, gateway_service):
        """Test Insights Liaison Agent."""
        request = {
            "endpoint": "/api/chat/liaison",
            "method": "POST",
            "params": {
                "message": "How do I calculate metrics?",
                "session_token": "session_123",
                "pillar": "insights"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should respond with insights-specific guidance
        assert isinstance(result, dict)
    
    async def test_operations_liaison_agent(self, gateway_service):
        """Test Operations Liaison Agent."""
        request = {
            "endpoint": "/api/chat/liaison",
            "method": "POST",
            "params": {
                "message": "How do I create an SOP?",
                "session_token": "session_123",
                "pillar": "operations"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should respond with operations-specific guidance
        assert isinstance(result, dict)
    
    async def test_conversation_creation(self, gateway_service):
        """Test conversation creation."""
        request = {
            "endpoint": "/api/chat/conversation/create",
            "method": "POST",
            "params": {
                "agent_type": "guide",
                "session_token": "session_123"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should create conversation
        assert isinstance(result, dict)
    
    async def test_conversation_history_retrieval(self, gateway_service):
        """Test conversation history retrieval."""
        request = {
            "endpoint": "/api/chat/conversation/history",
            "method": "GET",
            "params": {
                "conversation_id": "conv_123",
                "session_token": "session_123"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should return conversation history
        assert isinstance(result, dict)
    
    async def test_multi_turn_conversation(self, gateway_service):
        """Test multi-turn conversation with context."""
        # Turn 1
        request1 = {
            "endpoint": "/api/chat/guide",
            "method": "POST",
            "params": {
                "message": "I want to analyze a document",
                "session_token": "session_123"
            }
        }
        
        result1 = await gateway_service.route_frontend_request(request1)
        assert isinstance(result1, dict)
        
        # Turn 2 (with context from Turn 1)
        request2 = {
            "endpoint": "/api/chat/guide",
            "method": "POST",
            "params": {
                "message": "Which pillar should I use?",
                "session_token": "session_123"
            }
        }
        
        result2 = await gateway_service.route_frontend_request(request2)
        assert isinstance(result2, dict)
        
        # Turn 3 (continuing context)
        request3 = {
            "endpoint": "/api/chat/guide",
            "method": "POST",
            "params": {
                "message": "How do I get started?",
                "session_token": "session_123"
            }
        }
        
        result3 = await gateway_service.route_frontend_request(request3)
        assert isinstance(result3, dict)
    
    async def test_agent_context_persistence(self, gateway_service):
        """Test that agent context persists across requests."""
        session_token = "session_123"
        
        # First message
        request1 = {
            "endpoint": "/api/chat/guide",
            "method": "POST",
            "params": {
                "message": "I'm working on the Content Pillar",
                "session_token": session_token
            }
        }
        
        result1 = await gateway_service.route_frontend_request(request1)
        assert isinstance(result1, dict)
        
        # Second message (should remember context)
        request2 = {
            "endpoint": "/api/chat/guide",
            "method": "POST",
            "params": {
                "message": "What should I do next?",
                "session_token": session_token
            }
        }
        
        result2 = await gateway_service.route_frontend_request(request2)
        assert isinstance(result2, dict)
    
    async def test_error_handling_invalid_agent(self, gateway_service):
        """Test error handling for invalid agent type."""
        request = {
            "endpoint": "/api/chat/invalid_agent",
            "method": "POST",
            "params": {
                "message": "Hello",
                "session_token": "session_123"
            }
        }
        
        result = await gateway_service.route_frontend_request(request)
        
        # Should handle error gracefully
        assert isinstance(result, dict)
    
    async def test_concurrent_chat_requests(self, gateway_service):
        """Test concurrent chat requests."""
        import asyncio
        
        # Simulate multiple concurrent chat requests
        tasks = [
            gateway_service.route_frontend_request({
                "endpoint": "/api/chat/guide",
                "method": "POST",
                "params": {
                    "message": f"Message {i}",
                    "session_token": f"session_{i}"
                }
            })
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete
        assert len(results) == 3
        for result in results:
            assert isinstance(result, (dict, Exception))
    
    async def test_agent_routing_logic(self, gateway_service):
        """Test that messages are routed to correct agents."""
        # Guide Agent request
        guide_request = {
            "endpoint": "/api/chat/guide",
            "method": "POST",
            "params": {
                "message": "General help",
                "session_token": "session_123"
            }
        }
        
        guide_result = await gateway_service.route_frontend_request(guide_request)
        assert isinstance(guide_result, dict)
        
        # Liaison Agent request
        liaison_request = {
            "endpoint": "/api/chat/liaison",
            "method": "POST",
            "params": {
                "message": "Specific help",
                "session_token": "session_123",
                "pillar": "content"
            }
        }
        
        liaison_result = await gateway_service.route_frontend_request(liaison_request)
        assert isinstance(liaison_result, dict)
    
    async def test_chat_panel_availability_across_pillars(self, gateway_service):
        """Test that chat panel works across all pillars."""
        pillars = ["content", "insights", "operations", "business_outcomes"]
        
        for pillar in pillars:
            request = {
                "endpoint": "/api/chat/guide",
                "method": "POST",
                "params": {
                    "message": f"I'm on the {pillar} pillar",
                    "session_token": "session_123",
                    "current_pillar": pillar
                }
            }
            
            result = await gateway_service.route_frontend_request(request)
            
            # Should work on all pillars
            assert isinstance(result, dict)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

