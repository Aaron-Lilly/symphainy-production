#!/usr/bin/env python3
"""
Authentication Protocol - Abstraction Contract

Generic authentication interface with no technology dependencies.
This is Layer 2 of the 5-layer security architecture.

WHAT (Infrastructure Role): I define authentication contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class SecurityContext:
    """Security context data structure - no technology dependencies."""
    user_id: str | None = None
    tenant_id: str | None = None
    email: str | None = None  # User email (for ForwardAuth headers)
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    origin: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

class AuthenticationProtocol(Protocol):
    """Generic authentication protocol - no technology dependencies."""
    
    async def authenticate_user(self, credentials: Dict[str, Any]) -> SecurityContext: ...
    
    async def get_user_context(self, token: str) -> SecurityContext:
        """
        Get user/tenant context from authentication service (Supabase API).
        
        This is for user/tenant authentication - requires network call to get
        user context (tenant_id, roles, permissions).
        
        Use case: ForwardAuth endpoint (needs user context in headers)
        """
        ...
    
    async def validate_token(self, token: str) -> SecurityContext:
        """
        Validate token signature using local verification (JWKS).
        
        This is for token validation - fast, local, no network calls.
        Validates signature, expiration, issuer.
        
        Use case: Handler-level validation (fast token check)
        """
        ...
    
    async def refresh_token(self, refresh_token: str) -> SecurityContext: ...
    async def logout_user(self, token: str) -> bool: ...
    async def get_user_info(self, user_id: str) -> Dict[str, Any]: ...
    async def update_user_metadata(self, user_id: str, metadata: Dict[str, Any]) -> bool: ...
