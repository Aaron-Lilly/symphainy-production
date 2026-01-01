#!/usr/bin/env python3
"""
Messaging Protocol - Abstraction Contract

Generic messaging interface with no technology dependencies.
This is Layer 2 of the 5-layer architecture for Post Office.

WHAT (Infrastructure Role): I define messaging contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class MessageStatus(str, Enum):
    """Message status levels."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"

class MessageType(str, Enum):
    """Message type levels."""
    NOTIFICATION = "notification"
    ALERT = "alert"
    COMMAND = "command"
    RESPONSE = "response"
    HEARTBEAT = "heartbeat"

@dataclass(frozen=True)
class MessageContext:
    """Message context data structure - no technology dependencies."""
    message_id: str
    message_type: MessageType
    sender: str
    recipient: str
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    message_content: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    tenant_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

class MessagingProtocol(Protocol):
    """Generic messaging protocol - no technology dependencies."""

    async def send_message(self, message_type: MessageType, sender: str, recipient: str,
                         message_content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
                         correlation_id: Optional[str] = None, tenant_id: Optional[str] = None) -> Optional[MessageContext]: ...

    async def send_broadcast_message(self, message_type: MessageType, sender: str, recipients: List[str],
                                   message_content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
                                   tenant_id: Optional[str] = None) -> List[MessageContext]: ...

    async def get_message(self, message_id: str) -> Optional[MessageContext]: ...

    async def get_messages_for_recipient(self, recipient: str, limit: int = 100) -> List[MessageContext]: ...

    async def get_messages_by_type(self, message_type: MessageType, limit: int = 100) -> List[MessageContext]: ...

    async def get_messages_by_tenant(self, tenant_id: str, limit: int = 100) -> List[MessageContext]: ...

    async def acknowledge_message(self, message_id: str) -> bool: ...

    async def retry_failed_message(self, message_id: str) -> bool: ...

    async def get_message_metrics(self) -> Dict[str, Any]: ...

    async def cleanup_old_messages(self, older_than_hours: int = 24) -> int: ...



