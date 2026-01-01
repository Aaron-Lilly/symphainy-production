#!/usr/bin/env python3
"""
Security Context Utility - Clean Context Building

Builds and injects security context with no enforcement decisions.
This is the refactored security capability with clean separation of concerns.

WHAT (Utility Role): I build and inject security context
HOW (Utility Implementation): I use clean interfaces with no enforcement logic
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
class TenantContext:
    """Tenant context data structure - no enforcement logic."""
    tenant_id: str
    tenant_name: str
    tenant_type: str
    max_users: int
    features: list[str] = field(default_factory=list)
    limits: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

@dataclass(frozen=True)
class TraceContext:
    """Trace context data structure - no enforcement logic."""
    request_id: str
    trace_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    service_name: str = "security_context_utility"

class SecurityContextUtility:
    """
    Security Context Utility - Clean Context Building
    
    Builds and injects security context with no enforcement decisions.
    This utility only builds context - it does not make authorization decisions.
    """
    
    def __init__(self):
        """Initialize Security Context Utility."""
        self.logger = logging.getLogger("SecurityContextUtility")
        self.logger.info("✅ Security Context Utility initialized")
    
    # ============================================================================
    # USER CONTEXT BUILDING (No Enforcement)
    # ============================================================================
    
    async def build_user_context(self, token: str) -> SecurityContext:
        """Build user context from token - no enforcement decisions."""
        try:
            # Parse token to extract user information
            user_data = await self._parse_token(token)
            
            # Build security context
            context = SecurityContext(
                user_id=user_data.get("user_id"),
                tenant_id=user_data.get("tenant_id"),
                roles=user_data.get("roles", []),
                permissions=user_data.get("permissions", []),
                origin="security_context_utility"
            )
            
            self.logger.info(f"✅ User context built for user: {context.user_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build user context: {str(e)}")
            # Return empty context on error
            return SecurityContext(origin="security_context_utility")
    
    async def build_user_context_from_credentials(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Build user context from credentials - no enforcement decisions."""
        try:
            # Extract user information from credentials
            user_data = {
                "user_id": credentials.get("user_id"),
                "tenant_id": credentials.get("tenant_id"),
                "roles": credentials.get("roles", []),
                "permissions": credentials.get("permissions", [])
            }
            
            # Build security context
            context = SecurityContext(
                user_id=user_data.get("user_id"),
                tenant_id=user_data.get("tenant_id"),
                roles=user_data.get("roles", []),
                permissions=user_data.get("permissions", []),
                origin="security_context_utility"
            )
            
            self.logger.info(f"✅ User context built from credentials for user: {context.user_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build user context from credentials: {str(e)}")
            return SecurityContext(origin="security_context_utility")
    
    async def build_user_context_from_session(self, session_data: Dict[str, Any]) -> SecurityContext:
        """Build user context from session data - no enforcement decisions."""
        try:
            # Extract user information from session
            user_data = session_data.get("user_data", {})
            
            # Build security context
            context = SecurityContext(
                user_id=user_data.get("user_id"),
                tenant_id=user_data.get("tenant_id"),
                roles=user_data.get("roles", []),
                permissions=user_data.get("permissions", []),
                origin="security_context_utility"
            )
            
            self.logger.info(f"✅ User context built from session for user: {context.user_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build user context from session: {str(e)}")
            return SecurityContext(origin="security_context_utility")
    
    # ============================================================================
    # TENANT CONTEXT BUILDING (No Enforcement)
    # ============================================================================
    
    async def build_tenant_context(self, tenant_id: str, tenant_data: Dict[str, Any] = None) -> TenantContext:
        """Build tenant context - no enforcement decisions."""
        try:
            # Use provided tenant data or create default
            if tenant_data:
                tenant_info = tenant_data
            else:
                tenant_info = await self._get_default_tenant_info(tenant_id)
            
            # Build tenant context
            context = TenantContext(
                tenant_id=tenant_id,
                tenant_name=tenant_info.get("tenant_name", f"tenant_{tenant_id}"),
                tenant_type=tenant_info.get("tenant_type", "individual"),
                max_users=tenant_info.get("max_users", 1),
                features=tenant_info.get("features", []),
                limits=tenant_info.get("limits", {}),
                is_active=tenant_info.get("is_active", True)
            )
            
            self.logger.info(f"✅ Tenant context built for tenant: {tenant_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build tenant context: {str(e)}")
            # Return default context on error
            return TenantContext(
                tenant_id=tenant_id,
                tenant_name=f"tenant_{tenant_id}",
                tenant_type="individual",
                max_users=1,
                features=["basic_analytics"],
                limits={}
            )
    
    # ============================================================================
    # TRACE CONTEXT BUILDING (No Enforcement)
    # ============================================================================
    
    async def build_trace_context(self, request_id: str, service_name: str = "security_context_utility") -> TraceContext:
        """Build trace context for audit - no enforcement decisions."""
        try:
            # Build trace context
            context = TraceContext(
                request_id=request_id,
                trace_id=str(uuid.uuid4()),
                service_name=service_name
            )
            
            self.logger.info(f"✅ Trace context built for request: {request_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build trace context: {str(e)}")
            return TraceContext(
                request_id=request_id,
                trace_id=str(uuid.uuid4()),
                service_name=service_name
            )
    
    # ============================================================================
    # CONTEXT VALIDATION (No Enforcement)
    # ============================================================================
    
    def is_context_valid(self, context: SecurityContext) -> bool:
        """Check if security context is valid - no enforcement decisions."""
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
            self.logger.error(f"Failed to validate context: {str(e)}")
            return False
    
    def is_tenant_context_valid(self, context: TenantContext) -> bool:
        """Check if tenant context is valid - no enforcement decisions."""
        try:
            # Basic validation - context must have tenant_id
            if not context.tenant_id:
                return False
            
            # Check if tenant is active
            if not context.is_active:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate tenant context: {str(e)}")
            return False
    
    # ============================================================================
    # PRIVATE HELPER METHODS (No Enforcement)
    # ============================================================================
    
    async def _parse_token(self, token: str) -> Dict[str, Any]:
        """Parse token to extract user information - no enforcement."""
        try:
            # This is a simplified token parsing
            # In real implementation, this would use JWT adapter or similar
            
            # For now, return mock data
            return {
                "user_id": f"user_{hash(token) % 1000}",
                "tenant_id": f"tenant_{hash(token) % 100}",
                "roles": ["user"],
                "permissions": ["read", "write"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse token: {str(e)}")
            return {}
    
    async def _get_default_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get default tenant information - no enforcement."""
        try:
            # Return default tenant information
            return {
                "tenant_name": f"tenant_{tenant_id}",
                "tenant_type": "individual",
                "max_users": 1,
                "features": ["basic_analytics"],
                "limits": {"max_storage": "1GB", "max_files": 100},
                "is_active": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get default tenant info: {str(e)}")
            return {}
    
    # ============================================================================
    # UTILITY STATUS
    # ============================================================================
    
    def get_utility_status(self) -> Dict[str, Any]:
        """Get utility status information."""
        return {
            "utility_name": "SecurityContextUtility",
            "status": "active",
            "capabilities": [
                "build_user_context",
                "build_tenant_context", 
                "build_trace_context",
                "validate_context"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }



