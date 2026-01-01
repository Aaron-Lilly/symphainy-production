#!/usr/bin/env python3
"""
Traffic Cop Interface

Defines the contracts for Traffic Cop service operations.
This interface is for consumers, not implementers.

WHAT (Interface Role): I define the contracts for session and state management
HOW (Interface Implementation): I provide clear, typed interfaces for consumers
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class SessionPriority(str, Enum):
    """Session priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class StatePriority(str, Enum):
    """State priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class SessionStatus(str, Enum):
    """Session status levels."""
    ACTIVE = "active"
    ROUTING = "routing"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    EXPIRED = "expired"


class StateStatus(str, Enum):
    """State status levels."""
    ACTIVE = "active"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    RESOLVED = "resolved"
    STALE = "stale"


# Request Models
class SessionRequest(BaseModel):
    """Request to create a new session."""
    user_id: str = Field(..., description="User ID for the session")
    initial_pillar: Optional[str] = Field(None, description="Initial pillar to route to")
    priority: Optional[SessionPriority] = Field(SessionPriority.NORMAL, description="Session priority")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Session metadata")


class RoutingRequest(BaseModel):
    """Request to route a session to a pillar."""
    session_id: str = Field(..., description="Session ID to route")
    pillar_name: str = Field(..., description="Target pillar name")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Routing context")


class StateRequest(BaseModel):
    """Request to set state."""
    key: str = Field(..., description="State key")
    value: Any = Field(..., description="State value")
    pillar_name: Optional[str] = Field(None, description="Target pillar name")
    priority: Optional[StatePriority] = Field(StatePriority.NORMAL, description="State priority")
    ttl_seconds: Optional[int] = Field(None, description="Time to live in seconds")


class SyncRequest(BaseModel):
    """Request to synchronize state between pillars."""
    source_pillar: str = Field(..., description="Source pillar name")
    target_pillar: str = Field(..., description="Target pillar name")
    keys: Optional[List[str]] = Field(None, description="Specific keys to sync (all if None)")


class AnalyticsRequest(BaseModel):
    """Request for analytics data."""
    analytics_type: str = Field(..., description="Type of analytics (session, state)")
    session_id: Optional[str] = Field(None, description="Session ID for session analytics")
    pillar_name: Optional[str] = Field(None, description="Pillar name for state analytics")


class HealthCheckRequest(BaseModel):
    """Request for health check."""
    service_name: str = Field("traffic_cop", description="Service name to check")


# Response Models
class SessionResponse(BaseModel):
    """Response for session operations."""
    success: bool = Field(..., description="Operation success status")
    session_id: Optional[str] = Field(None, description="Session ID")
    session_data: Optional[Dict[str, Any]] = Field(None, description="Session data")
    message: str = Field(..., description="Response message")


class RoutingResponse(BaseModel):
    """Response for routing operations."""
    success: bool = Field(..., description="Operation success status")
    session_id: Optional[str] = Field(None, description="Session ID")
    pillar: Optional[str] = Field(None, description="Target pillar")
    message: str = Field(..., description="Response message")


class StateResponse(BaseModel):
    """Response for state operations."""
    success: bool = Field(..., description="Operation success status")
    key: Optional[str] = Field(None, description="State key")
    value: Optional[Any] = Field(None, description="State value")
    pillar: Optional[str] = Field(None, description="Pillar name")
    state_id: Optional[str] = Field(None, description="State ID")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    message: str = Field(..., description="Response message")


class SyncResponse(BaseModel):
    """Response for sync operations."""
    success: bool = Field(..., description="Operation success status")
    source_pillar: Optional[str] = Field(None, description="Source pillar")
    target_pillar: Optional[str] = Field(None, description="Target pillar")
    synced_count: Optional[int] = Field(None, description="Number of keys synced")
    conflicts: Optional[List[Dict[str, Any]]] = Field(None, description="Conflicts found")
    message: str = Field(..., description="Response message")


class AnalyticsResponse(BaseModel):
    """Response for analytics operations."""
    success: bool = Field(..., description="Operation success status")
    analytics_type: Optional[str] = Field(None, description="Type of analytics")
    data: Optional[Dict[str, Any]] = Field(None, description="Analytics data")
    message: str = Field(..., description="Response message")


class HealthCheckResponse(BaseModel):
    """Response for health check operations."""
    success: bool = Field(..., description="Health check success status")
    service_name: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status")
    details: Optional[Dict[str, Any]] = Field(None, description="Health check details")
    timestamp: str = Field(..., description="Health check timestamp")


# Interface Definition
class ITrafficCop:
    """
    Traffic Cop Interface

    Defines the contracts for Traffic Cop service operations.
    This interface is for consumers, not implementers.
    """

    # Session Management
    async def create_session(self, request: SessionRequest) -> SessionResponse:
        """Create a new session and route it to appropriate pillars."""
        pass

    async def route_session(self, request: RoutingRequest) -> RoutingResponse:
        """Route a session to a specific pillar."""
        pass

    async def get_session_status(self, session_id: str) -> SessionResponse:
        """Get the current status of a session."""
        pass

    async def terminate_session(self, session_id: str, reason: str = "user_request") -> SessionResponse:
        """Terminate a session."""
        pass

    # State Management
    async def set_state(self, request: StateRequest) -> StateResponse:
        """Set state for a key, optionally scoped to a pillar."""
        pass

    async def get_state(self, key: str, pillar_name: str = None) -> StateResponse:
        """Get state for a key, optionally scoped to a pillar."""
        pass

    async def sync_state(self, request: SyncRequest) -> SyncResponse:
        """Synchronize state between pillars."""
        pass

    # Analytics
    async def get_analytics(self, request: AnalyticsRequest) -> AnalyticsResponse:
        """Get analytics for sessions or state management."""
        pass

    # Health Check
    async def health_check(self, request: HealthCheckRequest) -> HealthCheckResponse:
        """Perform health check on the Traffic Cop service."""
        pass




