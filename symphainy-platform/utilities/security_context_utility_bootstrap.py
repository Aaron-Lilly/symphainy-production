#!/usr/bin/env python3
"""
Security Context Utility - Bootstrap Pattern

Builds and injects security context using bootstrap pattern to avoid circular references.
This utility gets bootstrapped by foundation service, then works independently.

WHAT (Utility Role): I build and inject security context using bootstrap pattern
HOW (Utility Implementation): I bootstrap from foundation service, then work independently
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class SecurityContext:
    """Security context data structure - no enforcement logic."""
    user_id: str | None = None
    tenant_id: str | None = None
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    origin: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class TraceContext:
    """Trace context data structure - no enforcement logic."""
    request_id: str
    trace_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    service_name: str = "security_context_utility_bootstrap"

class SecurityContextUtilityBootstrap:
    """
    Security Context Utility - Bootstrap Pattern
    
    Builds and injects security context using bootstrap pattern to avoid circular references.
    This utility gets bootstrapped by foundation service, then works independently.
    """
    
    def __init__(self, service_name: str = "default_service"):
        """Initialize Security Context Utility (not yet bootstrapped)."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"SecurityContextUtilityBootstrap-{service_name}")
        
        # Bootstrap state
        self.is_bootstrapped = False
        self.bootstrap_provider = None
        
        # Infrastructure abstractions (will be set after bootstrap)
        self.auth_abstraction = None
        self.session_abstraction = None
        
        self.logger.info(f"Security Context Utility Bootstrap initialized for {service_name} (not yet bootstrapped)")
    
    def bootstrap(self, bootstrap_provider, auth_abstraction=None, session_abstraction=None):
        """
        Bootstrap the security context utility with infrastructure capabilities.
        
        Args:
            bootstrap_provider: Foundation service that provides bootstrap implementation
            auth_abstraction: Optional authentication abstraction for enhanced capabilities
            session_abstraction: Optional session abstraction for enhanced capabilities
        """
        self.bootstrap_provider = bootstrap_provider
        self.auth_abstraction = auth_abstraction
        self.session_abstraction = session_abstraction
        self.is_bootstrapped = True
        
        self.logger.info(f"Security Context Utility Bootstrap bootstrapped by {bootstrap_provider.__class__.__name__}")
    
    async def build_user_context(self, user_id: str, tenant_id: Optional[str] = None, 
                                 roles: Optional[List[str]] = None, permissions: Optional[List[str]] = None,
                                 session_id: Optional[str] = None, request_id: Optional[str] = None,
                                 is_authenticated: bool = True, is_authorized: bool = False) -> SecurityContext:
        """Build a SecurityContext object for a given user."""
        if not self.is_bootstrapped:
            raise RuntimeError("Security Context Utility not bootstrapped. Call bootstrap() first.")
        
        context = SecurityContext(
            user_id=user_id,
            tenant_id=tenant_id,
            roles=roles if roles is not None else [],
            permissions=permissions if permissions is not None else [],
            origin=self.service_name
        )
        self.logger.debug(f"User context built for user: {user_id}")
        return context

    async def build_user_context_from_credentials(self, credentials: Dict[str, Any]) -> SecurityContext:
        """
        Build a SecurityContext from user credentials (e.g., email/password).
        This utility only *builds* the context, it does not authenticate.
        Authentication would be handled by an abstraction.
        """
        if not self.is_bootstrapped:
            raise RuntimeError("Security Context Utility not bootstrapped. Call bootstrap() first.")
        
        # Try infrastructure abstraction first (enhanced implementation)
        if self.auth_abstraction:
            try:
                # Use infrastructure abstraction for authentication
                auth_context = await self.auth_abstraction.authenticate_user(credentials)
                return SecurityContext(
                    user_id=auth_context.user_id,
                    tenant_id=auth_context.tenant_id,
                    roles=auth_context.roles,
                    permissions=auth_context.permissions,
                    origin=self.service_name
                )
            except Exception as e:
                self.logger.warning(f"Infrastructure authentication failed: {e}")
                # Fallback to basic context building
                pass
        
        # Fallback: Basic context building without infrastructure
        user_id = credentials.get("user_id", f"temp_user_{str(uuid.uuid4())[:8]}")
        tenant_id = credentials.get("tenant_id", "default_tenant")
        roles = credentials.get("roles", ["user"])
        
        context = SecurityContext(
            user_id=user_id,
            tenant_id=tenant_id,
            roles=roles,
            origin=self.service_name
        )
        self.logger.debug(f"User context built from credentials for user: {user_id}")
        return context

    async def build_trace_context(self, trace_id: Optional[str] = None, span_id: Optional[str] = None,
                                  parent_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> TraceContext:
        """Build a TraceContext object."""
        if not self.is_bootstrapped:
            raise RuntimeError("Security Context Utility not bootstrapped. Call bootstrap() first.")
        
        context = TraceContext(
            request_id=str(uuid.uuid4()),
            trace_id=trace_id if trace_id else str(uuid.uuid4()),
            service_name=self.service_name
        )
        self.logger.debug(f"Trace context built for request: {context.trace_id}")
        return context

    async def validate_context(self, context: SecurityContext) -> bool:
        """Perform basic validation on a SecurityContext (e.g., not empty user_id)."""
        if not self.is_bootstrapped:
            raise RuntimeError("Security Context Utility not bootstrapped. Call bootstrap() first.")
        
        is_valid = bool(context.user_id)
        self.logger.debug(f"Context validation: {is_valid}")
        return is_valid

    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the utility."""
        return {
            "utility_name": "SecurityContextUtilityBootstrap",
            "service_name": self.service_name,
            "status": "active" if self.is_bootstrapped else "not_bootstrapped",
            "is_bootstrapped": self.is_bootstrapped,
            "bootstrap_provider": self.bootstrap_provider.__class__.__name__ if self.bootstrap_provider else None,
            "timestamp": datetime.utcnow().isoformat()
        }



