#!/usr/bin/env python3
"""
Traffic Cop Service Protocol

Realm-specific protocol for Traffic Cop services with proper data models.
Inherits standard methods from ServiceProtocol.

WHAT (Traffic Cop Role): I orchestrate API Gateway routing, session management, and state synchronization
HOW (Traffic Cop Protocol): I provide API routing, load balancing, rate limiting, and state management
"""

from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from bases.protocols.service_protocol import ServiceProtocol


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    HEALTH_BASED = "health_based"
    RANDOM = "random"


class RateLimitType(Enum):
    """Rate limit types."""
    PER_USER = "per_user"
    PER_API = "per_api"
    PER_IP = "per_ip"
    GLOBAL = "global"


class SessionStatus(Enum):
    """Session status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class StateSyncStatus(Enum):
    """State synchronization status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ServiceInstance:
    """Service instance for load balancing."""
    id: str
    host: str
    port: int
    weight: int = 1
    health_check_url: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LoadBalancingRequest:
    """Load balancing request."""
    service_name: str
    strategy: Optional[LoadBalancingStrategy] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class LoadBalancingResponse:
    """Load balancing response."""
    success: bool
    service_instance: Optional[ServiceInstance] = None
    service_name: Optional[str] = None
    strategy_used: Optional[str] = None
    selection_time: Optional[str] = None
    error: Optional[str] = None


@dataclass
class RateLimitRequest:
    """Rate limit request."""
    user_id: Optional[str] = None
    api_endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    limit_type: RateLimitType = RateLimitType.PER_USER
    requests_per_minute: int = 60
    requests_per_hour: int = 1000


@dataclass
class RateLimitResponse:
    """Rate limit response."""
    allowed: bool
    remaining_requests: int = 0
    reset_time: Optional[str] = None
    limit_type: Optional[str] = None
    error: Optional[str] = None


@dataclass
class SessionRequest:
    """Session management request."""
    session_id: str
    user_id: Optional[str] = None
    session_type: str = "web"
    context: Dict[str, Any] = None
    ttl_seconds: int = 3600
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class SessionResponse:
    """Session management response."""
    success: bool
    session_id: str
    status: SessionStatus
    message: Optional[str] = None
    expires_at: Optional[str] = None
    error: Optional[str] = None


@dataclass
class StateSyncRequest:
    """State synchronization request."""
    key: str
    source_pillar: str
    target_pillar: str
    state_data: Dict[str, Any]
    sync_type: str = "full"
    priority: int = 1
    
    def __post_init__(self):
        if self.state_data is None:
            self.state_data = {}


@dataclass
class StateSyncResponse:
    """State synchronization response."""
    success: bool
    key: str
    sync_status: StateSyncStatus
    message: Optional[str] = None
    sync_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class APIGatewayRequest:
    """API Gateway request."""
    method: str
    path: str
    headers: Dict[str, str] = None
    query_params: Dict[str, str] = None
    body: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.query_params is None:
            self.query_params = {}
        if self.body is None:
            self.body = {}


@dataclass
class APIGatewayResponse:
    """API Gateway response."""
    success: bool
    status_code: int
    headers: Dict[str, str] = None
    body: Optional[Dict[str, Any]] = None
    service_instance: Optional[ServiceInstance] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.body is None:
            self.body = {}


@dataclass
class TrafficAnalyticsRequest:
    """Traffic analytics request."""
    time_range: str = "1h"  # 1h, 6h, 24h, 7d
    service_name: Optional[str] = None
    endpoint: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class TrafficAnalyticsResponse:
    """Traffic analytics response."""
    success: bool
    analytics_data: Dict[str, Any] = None
    time_range: Optional[str] = None
    generated_at: Optional[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.analytics_data is None:
            self.analytics_data = {}


class TrafficCopServiceProtocol(ServiceProtocol, Protocol):
    """
    Protocol for Traffic Cop services.
    Inherits standard methods from ServiceProtocol.
    """
    
    # Load Balancing Methods
    async def select_service(self, request: LoadBalancingRequest) -> LoadBalancingResponse:
        """Select service instance using load balancing strategy."""
        ...
    
    async def register_service_instance(self, service_name: str, instance: ServiceInstance) -> bool:
        """Register a new service instance."""
        ...
    
    async def unregister_service_instance(self, service_name: str, instance_id: str) -> bool:
        """Unregister a service instance."""
        ...
    
    # Rate Limiting Methods
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResponse:
        """Check if request is within rate limits."""
        ...
    
    async def reset_rate_limit(self, user_id: str, api_endpoint: Optional[str] = None) -> bool:
        """Reset rate limits for user/API."""
        ...
    
    # Session Management Methods
    async def create_session(self, request: SessionRequest) -> SessionResponse:
        """Create a new session."""
        ...
    
    async def get_session(self, session_id: str) -> SessionResponse:
        """Get session information."""
        ...
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> SessionResponse:
        """Update session data."""
        ...
    
    async def destroy_session(self, session_id: str) -> SessionResponse:
        """Destroy a session."""
        ...
    
    # State Synchronization Methods
    async def sync_state(self, request: StateSyncRequest) -> StateSyncResponse:
        """Synchronize state between pillars."""
        ...
    
    async def get_state_sync_status(self, sync_id: str) -> StateSyncResponse:
        """Get state synchronization status."""
        ...
    
    # API Gateway Methods
    async def route_api_request(self, request: APIGatewayRequest) -> APIGatewayResponse:
        """Route API request to appropriate service."""
        ...
    
    async def get_api_routes(self) -> List[Dict[str, Any]]:
        """Get available API routes."""
        ...
    
    # Traffic Analytics Methods
    async def get_traffic_analytics(self, request: TrafficAnalyticsRequest) -> TrafficAnalyticsResponse:
        """Get traffic analytics data."""
        ...
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get service health information."""
        ...
    
    # Orchestration Methods
    async def orchestrate_api_gateway(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate API Gateway operations."""
        ...
    
    async def orchestrate_session_management(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate session management operations."""
        ...
    
    async def orchestrate_state_synchronization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate state synchronization operations."""
        ...