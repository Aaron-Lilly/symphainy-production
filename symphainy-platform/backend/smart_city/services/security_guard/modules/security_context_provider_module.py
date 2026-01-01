#!/usr/bin/env python3
"""
SecurityContextProvider - Central Security Abstraction

Central security abstraction that extracts context from tokens and provides
security context management across the platform.

WHAT (Security Role): I provide central security context management
HOW (Security Implementation): I extract context from tokens and manage security state
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import security protocols
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext
from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantContext
from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionContext

# Import infrastructure adapters
from foundations.public_works_foundation.infrastructure_adapters.supabase_adapter import SupabaseAdapter
from foundations.public_works_foundation.infrastructure_adapters.jwt_adapter import JWTAdapter
from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter


class SecurityContextProvider:
    """
    SecurityContextProvider - Central Security Abstraction
    
    Central security abstraction that extracts context from tokens and provides
    security context management across the platform.
    
    WHAT (Security Role): I provide central security context management
    HOW (Security Implementation): I extract context from tokens and manage security state
    """
    
    def __init__(self, supabase_adapter: SupabaseAdapter = None, 
                 jwt_adapter: JWTAdapter = None, config_adapter: ConfigAdapter = None):
        """Initialize SecurityContextProvider with infrastructure adapters."""
        self.logger = self.service.di_container.get_logger("SecurityContextProvider")
        
        # Infrastructure adapters
        self.supabase_adapter = supabase_adapter
        self.jwt_adapter = jwt_adapter
        self.config_adapter = config_adapter
        
        # Security context cache
        self.context_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Default policy (open by default)
        self.default_policy = "open"
        
        self.logger.info("✅ SecurityContextProvider initialized")
    
    async def initialize(self):
        """Initialize SecurityContextProvider."""
        try:
            self.logger.info("🚀 Initializing SecurityContextProvider...")
            
            # Initialize adapters if available
            if self.supabase_adapter:
                await self.supabase_adapter.initialize()
            
            if self.jwt_adapter:
                await self.jwt_adapter.initialize()
            
            if self.config_adapter:
                await self.config_adapter.initialize()
            
            self.logger.info("✅ SecurityContextProvider initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize SecurityContextProvider: {e}")
            raise
    
    async def get_context(self, token: str | None = None) -> SecurityContext:
        """Get security context from token."""
        try:
            if not token:
                return self._create_anonymous_context()
            
            # Check cache first
            cache_key = f"context:{token[:20]}"  # Use first 20 chars as cache key
            if cache_key in self.context_cache:
                cached_context = self.context_cache[cache_key]
                if datetime.utcnow() < cached_context.get("expires_at", datetime.utcnow()):
                    return cached_context["context"]
            
            # Extract context from token
            context = await self._extract_context_from_token(token)
            
            # Cache the context
            self.context_cache[cache_key] = {
                "context": context,
                "expires_at": datetime.utcnow().timestamp() + self.cache_ttl
            }
            
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get security context: {e}")
            return self._create_anonymous_context()
    
    async def _extract_context_from_token(self, token: str) -> SecurityContext:
        """Extract security context from token."""
        try:
            # Try Supabase adapter first
            if self.supabase_adapter:
                result = await self.supabase_adapter.get_user(token)
                if result.get("success"):
                    user_data = result.get("user", {})
                    return SecurityContext(
                        user_id=user_data.get("id"),
                        tenant_id=user_data.get("tenant_id"),
                        roles=user_data.get("roles", []),
                        permissions=user_data.get("permissions", []),
                        origin="supabase"
                    )
            
            # Try JWT adapter
            if self.jwt_adapter:
                jwt_data = await self.jwt_adapter.decode_token(token)
                if jwt_data:
                    return SecurityContext(
                        user_id=jwt_data.get("user_id"),
                        tenant_id=jwt_data.get("tenant_id"),
                        roles=jwt_data.get("roles", []),
                        permissions=jwt_data.get("permissions", []),
                        origin="jwt"
                    )
            
            # Fallback to anonymous context
            return self._create_anonymous_context()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract context from token: {e}")
            return self._create_anonymous_context()
    
    def _create_anonymous_context(self) -> SecurityContext:
        """Create anonymous security context."""
        return SecurityContext(
            user_id=None,
            tenant_id=None,
            roles=[],
            permissions=[],
            origin="anonymous"
        )
    
    async def get_tenant_context(self, tenant_id: str) -> TenantContext:
        """Get tenant context for multi-tenant operations."""
        try:
            # This would typically come from tenant abstraction
            # For now, return a basic tenant context
            return TenantContext(
                tenant_id=tenant_id,
                tenant_type="standard",
                features=[],
                limits={},
                isolation_level="strict"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get tenant context: {e}")
            return TenantContext(
                tenant_id=tenant_id,
                tenant_type="unknown",
                features=[],
                limits={},
                isolation_level="strict"
            )
    
    async def get_session_context(self, session_id: str) -> SessionContext:
        """Get session context for session management."""
        try:
            # This would typically come from session abstraction
            # For now, return a basic session context
            return SessionContext(
                session_id=session_id,
                user_id=None,
                tenant_id=None,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow(),
                is_active=True
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get session context: {e}")
            return SessionContext(
                session_id=session_id,
                user_id=None,
                tenant_id=None,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow(),
                is_active=False
            )
    
    async def validate_context(self, context: SecurityContext) -> bool:
        """Validate security context."""
        try:
            # Basic validation
            if not context:
                return False
            
            # Check if context is not expired (if it has expiration)
            # This would be more sophisticated in a real implementation
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to validate context: {e}")
            return False
    
    async def refresh_context(self, context: SecurityContext) -> SecurityContext:
        """Refresh security context."""
        try:
            # This would typically involve re-validating the token
            # For now, return the same context
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Failed to refresh context: {e}")
            return context
    
    def clear_cache(self):
        """Clear security context cache."""
        self.context_cache.clear()
        self.logger.info("✅ Security context cache cleared")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get SecurityContextProvider status."""
        return {
            "service": "SecurityContextProvider",
            "status": "active",
            "adapters": {
                "supabase": self.supabase_adapter is not None,
                "jwt": self.jwt_adapter is not None,
                "config": self.config_adapter is not None
            },
            "cache_size": len(self.context_cache),
            "default_policy": self.default_policy
        }
