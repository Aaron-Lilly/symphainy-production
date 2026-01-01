#!/usr/bin/env python3
"""
Security Context Utility - Integrated with Infrastructure

Builds and injects security context using infrastructure abstractions.
This integrates the refactored security capabilities with the 5-layer infrastructure.

WHAT (Utility Role): I build and inject security context using infrastructure
HOW (Utility Implementation): I use infrastructure abstractions with no enforcement logic
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import uuid

from contracts.authentication_protocol import SecurityContext as InfrastructureSecurityContext
from contracts.session_protocol import SessionProtocol
from contracts.authentication_protocol import AuthenticationProtocol

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
    service_name: str = "security_context_utility_integrated"

class SecurityContextUtilityIntegrated:
    """
    Security Context Utility - Integrated with Infrastructure
    
    Builds and injects security context using infrastructure abstractions.
    This utility only builds context - it does not make enforcement decisions.
    """
    
    def __init__(self, 
                 auth_abstraction: AuthenticationProtocol,
                 session_abstraction: SessionProtocol):
        """Initialize Security Context Utility with infrastructure abstractions."""
        self.auth_abstraction = auth_abstraction
        self.session_abstraction = session_abstraction
        self.logger = logging.getLogger("SecurityContextUtilityIntegrated")
        self.logger.info("✅ Security Context Utility Integrated initialized with infrastructure abstractions")
    
    # ============================================================================
    # USER CONTEXT BUILDING (Using Infrastructure Abstractions)
    # ============================================================================
    
    async def build_user_context(self, token: str) -> SecurityContext:
        """Build user context from token using infrastructure abstractions."""
        try:
            # Use authentication abstraction to validate token
            auth_context = await self.auth_abstraction.validate_token(token)
            
            # Build security context from infrastructure context
            context = SecurityContext(
                user_id=auth_context.user_id,
                tenant_id=auth_context.tenant_id,
                roles=auth_context.roles,
                permissions=auth_context.permissions,
                origin="security_context_utility_integrated"
            )
            
            self.logger.info(f"✅ User context built using infrastructure for user: {context.user_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build user context using infrastructure: {str(e)}")
            # Return empty context on error
            return SecurityContext(origin="security_context_utility_integrated")
    
    async def build_user_context_from_credentials(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Build user context from credentials using infrastructure abstractions."""
        try:
            # Use authentication abstraction to authenticate user
            auth_context = await self.auth_abstraction.authenticate_user(credentials)
            
            # Build security context from infrastructure context
            context = SecurityContext(
                user_id=auth_context.user_id,
                tenant_id=auth_context.tenant_id,
                roles=auth_context.roles,
                permissions=auth_context.permissions,
                origin="security_context_utility_integrated"
            )
            
            self.logger.info(f"✅ User context built from credentials using infrastructure for user: {context.user_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build user context from credentials using infrastructure: {str(e)}")
            return SecurityContext(origin="security_context_utility_integrated")
    
    async def build_user_context_from_session(self, session_id: str) -> SecurityContext:
        """Build user context from session using infrastructure abstractions."""
        try:
            # Use session abstraction to validate session
            session_context = await self.session_abstraction.validate_session(session_id)
            
            # Build security context from session context
            context = SecurityContext(
                user_id=session_context.user_id,
                tenant_id=session_context.tenant_id,
                roles=session_context.roles,
                permissions=session_context.permissions,
                origin="security_context_utility_integrated"
            )
            
            self.logger.info(f"✅ User context built from session using infrastructure for user: {context.user_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build user context from session using infrastructure: {str(e)}")
            return SecurityContext(origin="security_context_utility_integrated")
    
    # ============================================================================
    # TRACE CONTEXT BUILDING (Using Infrastructure Abstractions)
    # ============================================================================
    
    async def build_trace_context(self, request_id: str, service_name: str = "security_context_utility_integrated") -> TraceContext:
        """Build trace context for audit using infrastructure abstractions."""
        try:
            # Build trace context
            context = TraceContext(
                request_id=request_id,
                trace_id=str(uuid.uuid4()),
                service_name=service_name
            )
            
            self.logger.info(f"✅ Trace context built using infrastructure for request: {request_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build trace context using infrastructure: {str(e)}")
            return TraceContext(
                request_id=request_id,
                trace_id=str(uuid.uuid4()),
                service_name=service_name
            )
    
    # ============================================================================
    # CONTEXT VALIDATION (Using Infrastructure Abstractions)
    # ============================================================================
    
    def is_context_valid(self, context: SecurityContext) -> bool:
        """Check if security context is valid using infrastructure abstractions."""
        try:
            # Basic validation - context must have user_id
            if not context.user_id:
                return False
            
            # Check if context is not too old (1 hour)
            age = datetime.utcnow() - context.created_at
            if age.total_seconds() > 3600:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate context using infrastructure: {str(e)}")
            return False
    
    # ============================================================================
    # INFRASTRUCTURE INTEGRATION METHODS
    # ============================================================================
    
    async def refresh_user_context(self, context: SecurityContext) -> SecurityContext:
        """Refresh user context using infrastructure abstractions."""
        try:
            # If context has a session, validate it
            if context.user_id:
                # Try to refresh using session abstraction
                # This would typically involve getting a new token or validating existing session
                refreshed_context = SecurityContext(
                    user_id=context.user_id,
                    tenant_id=context.tenant_id,
                    roles=context.roles,
                    permissions=context.permissions,
                    origin="security_context_utility_integrated_refreshed"
                )
                
                self.logger.info(f"✅ User context refreshed using infrastructure for user: {refreshed_context.user_id}")
                return refreshed_context
            
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to refresh user context using infrastructure: {str(e)}")
            return context
    
    async def get_user_session_info(self, user_id: str) -> Dict[str, Any]:
        """Get user session information using infrastructure abstractions."""
        try:
            # Use session abstraction to get active sessions
            active_sessions = await self.session_abstraction.get_active_sessions(user_id)
            
            session_info = {
                "user_id": user_id,
                "active_sessions": len(active_sessions),
                "sessions": active_sessions,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ User session info retrieved using infrastructure for user: {user_id}")
            return session_info
            
        except Exception as e:
            self.logger.error(f"Failed to get user session info using infrastructure: {str(e)}")
            return {"user_id": user_id, "active_sessions": 0, "sessions": [], "error": str(e)}
    
    # ============================================================================
    # UTILITY STATUS
    # ============================================================================
    
    def get_utility_status(self) -> Dict[str, Any]:
        """Get utility status information."""
        return {
            "utility_name": "SecurityContextUtilityIntegrated",
            "status": "active",
            "infrastructure_connected": True,
            "capabilities": [
                "build_user_context",
                "build_user_context_from_credentials",
                "build_user_context_from_session",
                "build_trace_context",
                "validate_context",
                "refresh_user_context",
                "get_user_session_info"
            ],
            "infrastructure_abstractions": [
                "AuthenticationProtocol",
                "SessionProtocol"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }



