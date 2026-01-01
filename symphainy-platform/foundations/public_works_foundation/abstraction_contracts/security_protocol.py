"""
Security Protocol - Infrastructure contract for security management

Defines the interface for authentication, authorization, audit logging, and threat detection.
This protocol enables swappable security management engines.
"""

from typing import Protocol, Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SecurityLevel(Enum):
    """Security level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatLevel(Enum):
    """Threat level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthMethod(Enum):
    """Authentication method enumeration."""
    PASSWORD = "password"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    BIOMETRIC = "biometric"
    MFA = "mfa"
    SSO = "sso"


class Permission(Enum):
    """Permission enumeration."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"


@dataclass(frozen=True)
class SecurityContext:
    """Context for security operations."""
    service_id: str
    agent_id: Optional[str] = None
    tenant_id: Optional[str] = None
    environment: str = "production"
    region: str = "us-west-2"
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class User:
    """User data structure."""
    user_id: str
    username: str
    email: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    permissions: List[Permission] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class AuthResult:
    """Authentication result."""
    success: bool
    user: Optional[User] = None
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class AuthToken:
    """Authentication token."""
    token_id: str
    user_id: str
    token_type: str = "access"
    token_value: str = ""
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_revoked: bool = False
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class SecurityEvent:
    """Security event data structure."""
    event_id: str
    event_type: str
    severity: SecurityLevel = SecurityLevel.MEDIUM
    threat_level: ThreatLevel = ThreatLevel.LOW
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    service_id: str = ""
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class SecurityPolicy:
    """Security policy data structure."""
    policy_id: str
    policy_name: str
    policy_type: str
    rules: List[Dict[str, Any]] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class SecurityProtocol(Protocol):
    """
    Security Protocol - Infrastructure contract for security management
    
    Defines the interface for authentication, authorization, audit logging, and threat detection.
    This protocol enables swappable security management engines.
    """
    
    async def authenticate_user(self, 
                              username: str,
                              ...word: str,
                              context: SecurityContext) -> AuthResult:
        """Authenticate user with username and password."""
        ...
    
    async def authenticate_token(self, 
                               token: str,
                               context: SecurityContext) -> AuthResult:
        """Authenticate user with token."""
        ...
    
    async def create_auth_token(self, 
                              user_id: str,
                              token_type: str,
                              context: SecurityContext) -> AuthToken:
        """Create authentication token."""
        ...
    
    async def validate_auth_token(self, 
                                token: str,
                                context: SecurityContext) -> Optional[User]:
        """Validate authentication token."""
        ...
    
    async def revoke_auth_token(self, 
                              token_id: str,
                              context: SecurityContext) -> bool:
        """Revoke authentication token."""
        ...
    
    async def check_permission(self, 
                             user_id: str,
                             permission: Permission,
                             resource: str,
                             context: SecurityContext) -> bool:
        """Check user permission for resource."""
        ...
    
    async def check_role(self, 
                       user_id: str,
                       role: str,
                       context: SecurityContext) -> bool:
        """Check user role."""
        ...
    
    async def create_user(self, 
                        username: str,
                        ...word: str,
                        email: Optional[str] = None,
                        roles: Optional[List[str]] = None,
                        context: SecurityContext = None) -> User:
        """Create new user."""
        ...
    
    async def get_user(self, 
                      user_id: str,
                      context: SecurityContext) -> Optional[User]:
        """Get user by ID."""
        ...
    
    async def update_user(self, 
                        user_id: str,
                        updates: Dict[str, Any],
                        context: SecurityContext) -> Optional[User]:
        """Update user data."""
        ...
    
    async def delete_user(self, 
                        user_id: str,
                        context: SecurityContext) -> bool:
        """Delete user."""
        ...
    
    async def log_security_event(self, 
                               event: SecurityEvent,
                               context: SecurityContext) -> bool:
        """Log security event."""
        ...
    
    async def get_security_events(self, 
                                context: SecurityContext,
                                filters: Optional[Dict[str, Any]] = None) -> List[SecurityEvent]:
        """Get security events with filters."""
        ...
    
    async def detect_threats(self, 
                           context: SecurityContext) -> List[SecurityEvent]:
        """Detect security threats."""
        ...
    
    async def create_security_policy(self, 
                                   policy: SecurityPolicy,
                                   context: SecurityContext) -> bool:
        """Create security policy."""
        ...
    
    async def evaluate_security_policy(self, 
                                     policy_id: str,
                                     context: SecurityContext) -> bool:
        """Evaluate security policy."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check security infrastructure health."""
        ...
