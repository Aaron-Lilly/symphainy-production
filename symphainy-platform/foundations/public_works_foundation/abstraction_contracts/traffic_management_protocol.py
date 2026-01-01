#!/usr/bin/env python3
"""
Traffic Management Protocol - Abstraction Contract

Generic traffic management interface with no technology dependencies.
This is Layer 2 of the 5-layer architecture for Traffic Cop traffic management.

WHAT (Infrastructure Role): I define traffic management contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class TrafficRoute:
    """Traffic route data structure - no technology dependencies."""
    route_id: str
    request_id: str
    session_id: str
    service_endpoint: str
    routing_config: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "pending"
    is_successful: bool = False


@dataclass(frozen=True)
class TrafficMetrics:
    """Traffic metrics data structure - no technology dependencies."""
    total_requests: int
    active_sessions: int
    routes_created: int
    sync_operations: int
    successful_routes: int
    failed_routes: int
    average_response_time: float
    last_updated: datetime = field(default_factory=datetime.utcnow)


class TrafficManagementProtocol(Protocol):
    """Generic traffic management protocol - no technology dependencies."""
    
    async def route_request(self, request_data: Dict[str, Any], session_id: str, 
                           service_endpoint: str) -> str: ...
    async def validate_route(self, route_id: str) -> TrafficRoute: ...
    async def update_route_status(self, route_id: str, status: str, 
                                 is_successful: bool = False) -> bool: ...
    async def get_active_routes(self, session_id: str) -> List[TrafficRoute]: ...
    async def cleanup_completed_routes(self) -> int: ...
    async def get_traffic_metrics(self) -> TrafficMetrics: ...
    async def update_traffic_metrics(self, metrics: Dict[str, Any]) -> bool: ...
    async def get_route_analytics(self, time_range: str) -> Dict[str, Any]: ...



