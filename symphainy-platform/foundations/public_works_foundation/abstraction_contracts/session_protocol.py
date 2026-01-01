"""
Session Protocol - Infrastructure contract for session management

Defines the interface for session lifecycle, security, storage, and analytics.
This protocol enables swappable session management engines.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, Dict, Any, List, Optional, Union
from enum import Enum


class SessionStatus(Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    PENDING = "pending"


class SessionType(Enum):
    """Session type enumeration."""
    USER = "user"
    AGENT = "agent"
    SERVICE = "service"
    API = "api"
    WEB = "web"
    MOBILE = "mobile"


class SecurityLevel(Enum):
    """Security level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SessionContext:
    """Context for session operations."""
    service_id: str
    agent_id: Optional[str] = None
    tenant_id: Optional[str] = None
    environment: str = "production"
    region: str = "us-west-2"
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class Session:
    """Session data structure."""
    session_id: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_type: SessionType = SessionType.USER
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    tags: Optional[List[str]] = field(default_factory=list)


@dataclass(frozen=True)
class SessionToken:
    """Session token data structure."""
    token_id: str
    session_id: str
    token_type: str = "access"
    token_value: str = ""
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class SessionAnalytics:
    """Session analytics data structure."""
    session_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_activity: datetime = field(default_factory=datetime.utcnow)
    security_events: int = 0
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class SessionProtocol(Protocol):
    """
    Session Protocol - Infrastructure contract for session management
    
    Defines the interface for session lifecycle, security, storage, and analytics.
    This protocol enables swappable session management engines.
    """
    
    async def create_session(self, 
                           context: SessionContext,
                           session_data: Dict[str, Any]) -> Session:
        """Create a new session."""
        ...
    
    async def get_session(self, 
                         session_id: str,
                         context: SessionContext) -> Optional[Session]:
        """Get session by ID."""
        ...
    
    async def update_session(self, 
                           session_id: str,
                           updates: Dict[str, Any],
                           context: SessionContext) -> bool:
        """Update session data."""
        ...
    
    async def delete_session(self, 
                           session_id: str,
                           context: SessionContext) -> bool:
        """Delete session."""
        ...
    
    async def validate_session(self, 
                             session_id: str,
                             context: SessionContext) -> bool:
        """Validate session exists and is active."""
        ...
    
    async def refresh_session(self, 
                            session_id: str,
                            context: SessionContext) -> Optional[Session]:
        """Refresh session expiration."""
        ...
    
    async def revoke_session(self, 
                           session_id: str,
                           context: SessionContext) -> bool:
        """Revoke session access."""
        ...
    
    async def list_sessions(self, 
                          context: SessionContext,
                          filters: Optional[Dict[str, Any]] = None) -> List[Session]:
        """List sessions with optional filters."""
        ...
    
    async def create_session_token(self, 
                                 session_id: str,
                                 token_type: str,
                                 context: SessionContext) -> SessionToken:
        """Create a session token."""
        ...
    
    async def validate_session_token(self, 
                                   token_value: str,
                                   context: SessionContext) -> Optional[Session]:
        """Validate session token and return session."""
        ...
    
    async def revoke_session_token(self, 
                                 token_id: str,
                                 context: SessionContext) -> bool:
        """Revoke session token."""
        ...
    
    async def get_session_analytics(self, 
                                   session_id: str,
                                   context: SessionContext) -> SessionAnalytics:
        """Get session analytics."""
        ...
    
    async def update_session_analytics(self, 
                                     session_id: str,
                                     analytics_data: Dict[str, Any],
                                     context: SessionContext) -> bool:
        """Update session analytics."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check session infrastructure health."""
        ...