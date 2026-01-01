#!/usr/bin/env python3
"""
MessagingAbstraction Tests

Tests for MessagingAbstraction in isolation.
Verifies abstraction works correctly and realms can access it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestMessagingAbstraction:
    """Test MessagingAbstraction functionality."""
    
    @pytest.fixture
    def mock_messaging_adapter(self):
        """Mock messaging adapter."""
        adapter = MagicMock()
        adapter.send_message = AsyncMock(return_value=MagicMock(message_id="msg_123"))
        adapter.get_message = AsyncMock(return_value=MagicMock(message_id="msg_123"))
        return adapter
    
    @pytest.fixture
    def mock_config_adapter(self):
        """Mock config adapter."""
        return MagicMock()
    
    @pytest.fixture
    def abstraction(self, mock_messaging_adapter, mock_config_adapter):
        """Create MessagingAbstraction instance."""
        from foundations.public_works_foundation.infrastructure_abstractions.messaging_abstraction import MessagingAbstraction
        
        abstraction = MessagingAbstraction(
            messaging_adapter=mock_messaging_adapter,
            config_adapter=mock_config_adapter
        )
        return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_messaging_adapter, mock_config_adapter):
        """Test abstraction initializes correctly."""
        from foundations.public_works_foundation.infrastructure_abstractions.messaging_abstraction import MessagingAbstraction
        
        abstraction = MessagingAbstraction(
            messaging_adapter=mock_messaging_adapter,
            config_adapter=mock_config_adapter
        )
        assert abstraction.messaging_adapter == mock_messaging_adapter
        assert abstraction.config == mock_config_adapter
    
    @pytest.mark.asyncio
    async def test_send_message(self, abstraction, mock_messaging_adapter):
        """Test abstraction can send a message."""
        from foundations.public_works_foundation.abstraction_contracts.messaging_protocol import MessageType, MessagePriority
        
        message_context = await abstraction.send_message(
            message_type=MessageType.NOTIFICATION,
            sender="sender_123",
            recipient="recipient_123",
            message_content={"text": "test message"},
            priority=MessagePriority.NORMAL
        )
        
        assert message_context is not None
        mock_messaging_adapter.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_message(self, abstraction, mock_messaging_adapter):
        """Test abstraction can get a message."""
        message_context = await abstraction.get_message("msg_123")
        
        assert message_context is not None
        mock_messaging_adapter.get_message.assert_called_once()

