#!/usr/bin/env python3
"""
Session Management Protocol - Abstraction Contract

Generic session management interface with no technology dependencies.
This is Layer 2 of the 5-layer architecture for Traffic Cop session management.

WHAT (Infrastructure Role): I define session management contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SessionRoute:
    """Session route data structure - no technology dependencies."""
    route_id: str
    session_id: str
    service_endpoint: str
    routing_config: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass(frozen=True)
class SessionRouteContext:
    """Session route context data structure - no technology dependencies."""
    route_id: str
    session_id: str
    user_id: str
    tenant_id: str
    service_endpoint: str
    routing_config: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


class SessionManagementProtocol(Protocol):
    """Generic session management protocol - no technology dependencies."""
    
    async def create_session_route(self, session_id: str, service_endpoint: str, 
                                 routing_config: Dict[str, Any]) -> str: ...
    async def validate_session_route(self, session_id: str) -> SessionRouteContext: ...
    async def update_session_route(self, session_id: str, routing_config: Dict[str, Any]) -> bool: ...
    async def destroy_session_route(self, session_id: str) -> bool: ...
    async def get_active_routes(self, user_id: str) -> List[SessionRouteContext]: ...
    async def cleanup_expired_routes(self) -> int: ...
    async def get_route_metrics(self) -> Dict[str, Any]: ...



