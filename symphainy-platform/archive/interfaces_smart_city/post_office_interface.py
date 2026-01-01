#!/usr/bin/env python3
"""
Post Office Interface

Defines the contracts for Post Office service operations.
This interface matches the existing PostOfficeService APIs.

WHAT (Interface Role): I define the contracts for messaging and event routing
HOW (Interface Implementation): I provide clear, typed interfaces for consumers
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MessageStatus(str, Enum):
    """Message status levels."""
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    PENDING = "pending"
    RETRYING = "retrying"


class EventType(str, Enum):
    """Event type levels."""
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    BUSINESS_EVENT = "business_event"
    ERROR_EVENT = "error_event"
    NOTIFICATION = "notification"


class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AgentStatus(str, Enum):
    """Agent status levels."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    OFFLINE = "offline"


# Request Models
class SendMessageRequest(BaseModel):
    """Request to send a message."""
    message_id: str = Field(..., description="Unique identifier for the message")
    sender_id: str = Field(..., description="ID of the message sender")
    recipient_id: str = Field(..., description="ID of the message recipient")
    subject: str = Field(..., description="Message subject")
    content: str = Field(..., description="Message content")
    message_type: Optional[str] = Field("text", description="Type of message")
    priority: Optional[MessagePriority] = Field(MessagePriority.NORMAL, description="Message priority")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Message metadata")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant messaging")


class RouteEventRequest(BaseModel):
    """Request to route an event."""
    event_id: str = Field(..., description="Unique identifier for the event")
    event_type: EventType = Field(..., description="Type of event")
    source: str = Field(..., description="Source of the event")
    target: str = Field(..., description="Target for the event")
    event_data: Dict[str, Any] = Field(..., description="Event data payload")
    priority: Optional[MessagePriority] = Field(MessagePriority.NORMAL, description="Event priority")
    routing_rules: Optional[List[str]] = Field(default_factory=list, description="Routing rules to apply")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant events")


class RegisterAgentRequest(BaseModel):
    """Request to register an agent."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    agent_name: str = Field(..., description="Name of the agent")
    agent_type: str = Field(..., description="Type of agent")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    endpoint: Optional[str] = Field(None, description="Agent endpoint URL")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Agent metadata")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant agents")


class GetMessagesRequest(BaseModel):
    """Request to get messages for a recipient."""
    recipient_id: str = Field(..., description="ID of the message recipient")
    message_status: Optional[MessageStatus] = Field(None, description="Filter by message status")
    limit: Optional[int] = Field(10, description="Maximum number of messages to retrieve")
    offset: Optional[int] = Field(0, description="Offset for pagination")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


class GetMessageStatusRequest(BaseModel):
    """Request to get message delivery status."""
    message_id: str = Field(..., description="ID of the message")
    include_history: Optional[bool] = Field(False, description="Include delivery history")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


# Response Models
class SendMessageResponse(BaseModel):
    """Response for message sending."""
    success: bool = Field(..., description="Message sending success status")
    message_id: Optional[str] = Field(None, description="Sent message ID")
    sender_id: Optional[str] = Field(None, description="Message sender ID")
    recipient_id: Optional[str] = Field(None, description="Message recipient ID")
    message_status: Optional[MessageStatus] = Field(None, description="Initial message status")
    sent_at: Optional[str] = Field(None, description="Sending timestamp")
    message: str = Field(..., description="Response message")


class RouteEventResponse(BaseModel):
    """Response for event routing."""
    success: bool = Field(..., description="Event routing success status")
    event_id: Optional[str] = Field(None, description="Routed event ID")
    event_type: Optional[EventType] = Field(None, description="Type of routed event")
    source: Optional[str] = Field(None, description="Event source")
    target: Optional[str] = Field(None, description="Event target")
    routing_path: Optional[List[str]] = Field(None, description="Path taken for routing")
    routed_at: Optional[str] = Field(None, description="Routing timestamp")
    message: str = Field(..., description="Response message")


class RegisterAgentResponse(BaseModel):
    """Response for agent registration."""
    success: bool = Field(..., description="Agent registration success status")
    agent_id: Optional[str] = Field(None, description="Registered agent ID")
    agent_name: Optional[str] = Field(None, description="Agent name")
    agent_type: Optional[str] = Field(None, description="Agent type")
    agent_status: Optional[AgentStatus] = Field(None, description="Initial agent status")
    registered_at: Optional[str] = Field(None, description="Registration timestamp")
    message: str = Field(..., description="Response message")


class GetMessagesResponse(BaseModel):
    """Response for message retrieval."""
    success: bool = Field(..., description="Message retrieval success status")
    recipient_id: Optional[str] = Field(None, description="Message recipient ID")
    messages: Optional[List[Dict[str, Any]]] = Field(None, description="Retrieved messages")
    total_count: Optional[int] = Field(None, description="Total number of messages")
    retrieved_at: Optional[str] = Field(None, description="Retrieval timestamp")
    message: str = Field(..., description="Response message")


class GetMessageStatusResponse(BaseModel):
    """Response for message status."""
    success: bool = Field(..., description="Status retrieval success status")
    message_id: Optional[str] = Field(None, description="Message ID")
    message_status: Optional[MessageStatus] = Field(None, description="Current message status")
    delivery_history: Optional[List[Dict[str, Any]]] = Field(None, description="Delivery history if requested")
    last_updated: Optional[str] = Field(None, description="Last status update timestamp")
    message: str = Field(..., description="Response message")


# Interface Definition
class IPostOffice:
    """
    Post Office Interface

    Defines the contracts for Post Office service operations.
    This interface matches the existing PostOfficeService APIs.
    """

    # Messaging
    async def send_message(self, request: SendMessageRequest) -> SendMessageResponse:
        """Send a message to a recipient."""
        pass

    # Event Routing
    async def route_event(self, request: RouteEventRequest) -> RouteEventResponse:
        """Route an event to appropriate handlers."""
        pass

    # Agent Management
    async def register_agent(self, request: RegisterAgentRequest) -> RegisterAgentResponse:
        """Register an agent for communication."""
        pass

    # Message Management
    async def get_messages(self, request: GetMessagesRequest) -> GetMessagesResponse:
        """Get messages for a recipient."""
        pass

    async def get_message_status(self, request: GetMessageStatusRequest) -> GetMessageStatusResponse:
        """Get delivery status of a message."""
        pass























