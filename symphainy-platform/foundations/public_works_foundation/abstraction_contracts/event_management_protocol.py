#!/usr/bin/env python3
"""
Event Management Protocol - Abstraction Contract

Generic event management interface with no technology dependencies.
This is Layer 2 of the 5-layer architecture for Post Office.

WHAT (Infrastructure Role): I define event management contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class EventPriority(str, Enum):
    """Event priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class EventStatus(str, Enum):
    """Event status levels."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass(frozen=True)
class EventContext:
    """Event context data structure - no technology dependencies."""
    event_id: str
    event_type: str
    source: str
    target: str
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    event_data: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    tenant_id: Optional[str] = None

class EventManagementProtocol(Protocol):
    """Generic event management protocol - no technology dependencies."""

    async def publish_event(self, event_type: str, source: str, target: str, 
                          event_data: Dict[str, Any], priority: EventPriority = EventPriority.NORMAL,
                          correlation_id: Optional[str] = None, tenant_id: Optional[str] = None) -> Optional[EventContext]: ...

    async def subscribe_to_events(self, event_type: str, callback: Callable[[EventContext], None], 
                                 consumer_group: Optional[str] = None) -> bool: ...

    async def unsubscribe_from_events(self, event_type: str, consumer_group: Optional[str] = None) -> bool: ...

    async def get_event(self, event_id: str) -> Optional[EventContext]: ...

    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[EventContext]: ...

    async def get_events_by_tenant(self, tenant_id: str, limit: int = 100) -> List[EventContext]: ...

    async def acknowledge_event(self, event_id: str, consumer_group: str) -> bool: ...

    async def get_event_metrics(self) -> Dict[str, Any]: ...

    async def cleanup_processed_events(self, older_than_hours: int = 24) -> int: ...



