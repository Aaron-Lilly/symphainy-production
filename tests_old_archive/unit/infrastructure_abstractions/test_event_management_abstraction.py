#!/usr/bin/env python3
"""
EventManagementAbstraction Tests

Tests for EventManagementAbstraction in isolation.
Verifies abstraction works correctly and realms can access it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestEventManagementAbstraction:
    """Test EventManagementAbstraction functionality."""
    
    @pytest.fixture
    def mock_event_bus_adapter(self):
        """Mock event bus adapter."""
        adapter = MagicMock()
        adapter.publish_event = AsyncMock(return_value=MagicMock(event_id="event_123"))
        adapter.subscribe_to_events = AsyncMock(return_value=True)
        adapter.unsubscribe_from_events = AsyncMock(return_value=True)
        return adapter
    
    @pytest.fixture
    def mock_config_adapter(self):
        """Mock config adapter."""
        return MagicMock()
    
    @pytest.fixture
    def abstraction(self, mock_event_bus_adapter, mock_config_adapter):
        """Create EventManagementAbstraction instance."""
        from foundations.public_works_foundation.infrastructure_abstractions.event_management_abstraction import EventManagementAbstraction
        
        abstraction = EventManagementAbstraction(
            event_bus_adapter=mock_event_bus_adapter,
            config_adapter=mock_config_adapter
        )
        return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_event_bus_adapter, mock_config_adapter):
        """Test abstraction initializes correctly."""
        from foundations.public_works_foundation.infrastructure_abstractions.event_management_abstraction import EventManagementAbstraction
        
        abstraction = EventManagementAbstraction(
            event_bus_adapter=mock_event_bus_adapter,
            config_adapter=mock_config_adapter
        )
        assert abstraction.event_bus_adapter == mock_event_bus_adapter
        assert abstraction.config == mock_config_adapter
    
    @pytest.mark.asyncio
    async def test_publish_event(self, abstraction, mock_event_bus_adapter):
        """Test abstraction can publish an event."""
        from foundations.public_works_foundation.abstraction_contracts.event_management_protocol import EventPriority
        
        event_context = await abstraction.publish_event(
            event_type="test_event",
            source="test_source",
            target="test_target",
            event_data={"key": "value"},
            priority=EventPriority.NORMAL
        )
        
        assert event_context is not None
        mock_event_bus_adapter.publish_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_subscribe_to_events(self, abstraction, mock_event_bus_adapter):
        """Test abstraction can subscribe to events."""
        async def callback(event_context):
            pass
        
        result = await abstraction.subscribe_to_events("test_event", callback)
        assert result is True
        mock_event_bus_adapter.subscribe_to_events.assert_called_once()

