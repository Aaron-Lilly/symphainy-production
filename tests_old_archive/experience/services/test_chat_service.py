#!/usr/bin/env python3
"""
Chat Service Tests

Tests for the Experience realm Chat Service that routes messages to agents.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

@pytest.mark.unit
@pytest.mark.experience
class TestChatServiceUnit:
    """Unit tests for Chat Service."""
    
    @pytest.mark.asyncio
    async def test_chat_service_initialization(self, mock_di_container):
        """Test ChatService initializes correctly."""
        from backend.experience.services.chat_service import ChatService
        
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=mock_di_container
        )
        
        assert chat_service.service_name == "ChatService"
        assert chat_service.realm_name == "experience"
        assert chat_service.guide_agent is None  # Not initialized yet
        assert chat_service.conversations == {}
    
    @pytest.mark.asyncio
    async def test_send_message_to_guide_success(self, mock_di_container):
        """Test sending message to Guide Agent."""
        from backend.experience.services.chat_service import ChatService
        
        # Create ChatService
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=mock_di_container
        )
        
        # Mock Guide Agent
        mock_guide = AsyncMock()
        mock_guide.provide_guidance = AsyncMock(return_value={
            "guidance": "Hello! I'm here to help you navigate your journey."
        })
        chat_service.guide_agent = mock_guide
        
        # Send message
        result = await chat_service.send_message_to_guide(
            message="Hello, I need help",
            conversation_id="conv_123",
            user_id="user_456"
        )
        
        # Verify response
        assert result["success"] is True
        assert "response" in result
        assert result["conversation_id"] == "conv_123"
        assert result["agent"] == "guide"
        
        # Verify conversation created
        assert "conv_123" in chat_service.conversations
        assert len(chat_service.conversations["conv_123"]["messages"]) == 2  # User + Guide
    
    @pytest.mark.asyncio
    async def test_send_message_to_guide_not_available(self, mock_di_container):
        """Test sending message when Guide Agent not available."""
        from backend.experience.services.chat_service import ChatService
        
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=mock_di_container
        )
        
        # Guide Agent is None
        result = await chat_service.send_message_to_guide(
            message="Hello",
            conversation_id="conv_123",
            user_id="user_456"
        )
        
        assert result["success"] is False
        assert "not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_send_message_to_liaison_success(self, mock_di_container):
        """Test sending message to Liaison Agent."""
        from backend.experience.services.chat_service import ChatService
        
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=mock_di_container
        )
        
        # Mock Content Liaison Agent
        mock_liaison = AsyncMock()
        mock_liaison.process_user_query = AsyncMock(return_value={
            "success": True,
            "response": "I can help you with content analysis!"
        })
        chat_service.content_liaison = mock_liaison
        
        # Send message
        result = await chat_service.send_message_to_liaison(
            message="Help me analyze a document",
            pillar="content",
            conversation_id="conv_789",
            user_id="user_456"
        )
        
        # Verify response
        assert result["success"] is True
        assert "response" in result
        assert result["pillar"] == "content"
        assert result["agent"] == "content_liaison"
    
    @pytest.mark.asyncio
    async def test_send_message_to_liaison_not_available(self, mock_di_container):
        """Test sending message when Liaison Agent not available."""
        from backend.experience.services.chat_service import ChatService
        
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=mock_di_container
        )
        
        # Liaison Agent is None
        result = await chat_service.send_message_to_liaison(
            message="Hello",
            pillar="content",
            conversation_id="conv_123",
            user_id="user_456"
        )
        
        assert result["success"] is False
        assert "not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, mock_di_container):
        """Test creating a new conversation."""
        from backend.experience.services.chat_service import ChatService
        
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=mock_di_container
        )
        
        # Create conversation
        result = await chat_service.create_conversation(
            user_id="user_123",
            initial_agent="guide"
        )
        
        assert result["success"] is True
        assert "conversation_id" in result
        assert result["active_agent"] == "guide"
        
        # Verify conversation exists
        conv_id = result["conversation_id"]
        assert conv_id in chat_service.conversations
        assert chat_service.conversations[conv_id]["user_id"] == "user_123"
    
    @pytest.mark.asyncio
    async def test_get_conversation_history(self, mock_di_container):
        """Test retrieving conversation history."""
        from backend.experience.services.chat_service import ChatService
        
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=mock_di_container
        )
        
        # Create a conversation first
        create_result = await chat_service.create_conversation(
            user_id="user_123",
            initial_agent="guide"
        )
        conv_id = create_result["conversation_id"]
        
        # Get history
        result = await chat_service.get_conversation_history(
            conversation_id=conv_id
        )
        
        assert result["success"] is True
        assert "conversation" in result
        assert result["conversation"]["conversation_id"] == conv_id
    
    @pytest.mark.asyncio
    async def test_switch_agent(self, mock_di_container):
        """Test switching active agent in conversation."""
        from backend.experience.services.chat_service import ChatService
        
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=mock_di_container
        )
        
        # Create a conversation first
        create_result = await chat_service.create_conversation(
            user_id="user_123",
            initial_agent="guide"
        )
        conv_id = create_result["conversation_id"]
        
        # Switch to content liaison
        result = await chat_service.switch_agent(
            conversation_id=conv_id,
            new_agent="content"
        )
        
        assert result["success"] is True
        assert result["old_agent"] == "guide"
        assert result["new_agent"] == "content"
        assert chat_service.conversations[conv_id]["active_agent"] == "content"
    
    @pytest.mark.asyncio
    async def test_get_active_agent(self, mock_di_container):
        """Test getting active agent for conversation."""
        from backend.experience.services.chat_service import ChatService
        
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=mock_di_container
        )
        
        # Create a conversation first
        create_result = await chat_service.create_conversation(
            user_id="user_123",
            initial_agent="guide"
        )
        conv_id = create_result["conversation_id"]
        
        # Get active agent
        result = await chat_service.get_active_agent(
            conversation_id=conv_id
        )
        
        assert result["success"] is True
        assert result["active_agent"] == "guide"

@pytest.mark.integration
@pytest.mark.experience
class TestChatServiceIntegration:
    """Integration tests for Chat Service with real agents."""
    
    @pytest.mark.asyncio
    async def test_chat_service_discovers_agents(self, real_di_container, mock_curator):
        """Test ChatService discovers agents via Curator."""
        from backend.experience.services.chat_service import ChatService
        
        # Mock Curator with agent discovery
        mock_guide = MagicMock()
        mock_curator.get_service = AsyncMock(side_effect=lambda name: {
            "GuideAgent": mock_guide,
            "ContentAnalysisOrchestrator": MagicMock(liaison_agent=MagicMock())
        }.get(name))
        
        real_di_container.curator = mock_curator
        
        # Create ChatService
        chat_service = ChatService(
            service_name="ChatService",
            realm_name="experience",
            platform_gateway=MagicMock(),
            di_container=real_di_container
        )
        
        # Initialize (should discover agents)
        await chat_service.initialize()
        
        # Verify agents discovered
        assert chat_service.guide_agent is not None
        # Note: Liaison agents may be None if orchestrators not available

