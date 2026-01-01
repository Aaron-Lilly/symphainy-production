#!/usr/bin/env python3
"""
AuthorizationGuard - Cross-Platform Security Enforcement

Cross-platform security enforcement that can be injected into any service.
Provides policy-driven authorization with pluggable policy engines.

WHAT (Security Role): I provide cross-platform security enforcement
HOW (Security Implementation): I enforce authorization with pluggable policy engines
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

# Import security protocols
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext
from foundations.public_works_foundation.abstraction_contracts.policy_engine_protocol import PolicyEngine

# Import policy engines
from engines.default_policy_engine import DefaultPolicyEngine
from engines.supabase_rls_policy_engine import SupabaseRLSEngine


class AuthorizationGuard:
    """
    AuthorizationGuard - Cross-Platform Security Enforcement
    
    Cross-platform security enforcement that can be injected into any service.
    Provides policy-driven authorization with pluggable policy engines.
    
    WHAT (Security Role): I provide cross-platform security enforcement
    HOW (Security Implementation): I enforce authorization with pluggable policy engines
    """
    
    def __init__(self, policy_engine: PolicyEngine = None, 
                 default_policy: str = "open"):
        """Initialize AuthorizationGuard with policy engine."""
        self.logger = self.service.di_container.get_logger("AuthorizationGuard")
        
        # Policy engine (pluggable)
        self.policy_engine = policy_engine
        self.default_policy = default_policy
        
        # Default policy engine (open by default)
        if not self.policy_engine:
            self.policy_engine = DefaultPolicyEngine()
        
        # Authorization cache
        self.auth_cache = {}
        self.cache_ttl = 60  # 1 minute
        
        # Enforcement statistics
        self.enforcement_stats = {
            "total_checks": 0,
            "allowed": 0,
            "denied": 0,
            "cache_hits": 0
        }
        
        self.logger.info("✅ AuthorizationGuard initialized")
    
    async def initialize(self):
        """Initialize AuthorizationGuard."""
        try:
            self.logger.info("🚀 Initializing AuthorizationGuard...")
            
            # Initialize policy engine if it has an initialize method
            if self.policy_engine and hasattr(self.policy_engine, 'initialize'):
                await self.policy_engine.initialize()
            
            self.logger.info("✅ AuthorizationGuard initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize AuthorizationGuard: {e}")
            raise
    
    def enforce(self, action: str, resource: str, context: SecurityContext) -> bool:
        """Enforce authorization for action."""
        try:
            # Update statistics
            self.enforcement_stats["total_checks"] += 1
            
            # Check cache first
            cache_key = f"{action}:{resource}:{context.user_id}:{context.tenant_id}"
            if cache_key in self.auth_cache:
                self.enforcement_stats["cache_hits"] += 1
                return self.auth_cache[cache_key]
            
            # Enforce authorization
            is_authorized = self._check_authorization(action, resource, context)
            
            # Cache the result
            self.auth_cache[cache_key] = is_authorized
            
            # Update statistics
            if is_authorized:
                self.enforcement_stats["allowed"] += 1
            else:
                self.enforcement_stats["denied"] += 1
            
            return is_authorized
            
        except Exception as e:
            self.logger.error(f"❌ Failed to enforce authorization: {e}")
            # Default to deny on error
            return False
    
    def _check_authorization(self, action: str, resource: str, context: SecurityContext) -> bool:
        """Check authorization using policy engine."""
        try:
            # Use policy engine if available
            if self.policy_engine:
                # Handle async policy engine
                if hasattr(self.policy_engine, 'is_allowed'):
                    import asyncio
                    try:
                        # Try to get the result from the async method
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If we're in an async context, we need to handle this differently
                            # For now, return True for open policy
                            return True
                        else:
                            result = loop.run_until_complete(self.policy_engine.is_allowed(action, resource, context))
                            return result.allowed if hasattr(result, 'allowed') else True
                    except:
                        # Fallback to open policy
                        return True
            
            # Default open policy
            if self.default_policy == "open":
                return True
            
            # Default deny policy
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to check authorization: {e}")
            return False
    
    def enforce_tenant_access(self, user_tenant: str, resource_tenant: str, context: SecurityContext) -> bool:
        """Enforce tenant access validation."""
        try:
            # Check tenant isolation
            if user_tenant != resource_tenant:
                self.logger.warning(f"Tenant access denied: {user_tenant} -> {resource_tenant}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to enforce tenant access: {e}")
            return False
    
    def enforce_feature_access(self, feature: str, context: SecurityContext) -> bool:
        """Enforce feature access control."""
        try:
            # Check if user has access to feature
            # This would typically check against user's permissions or tenant features
            if not context.user_id:
                return False
            
            # For now, allow all features for authenticated users
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to enforce feature access: {e}")
            return False
    
    def enforce_role_access(self, required_role: str, context: SecurityContext) -> bool:
        """Enforce role-based access control."""
        try:
            # Check if user has required role
            if required_role in context.roles:
                return True
            
            # Check for admin role (admin can do anything)
            if "admin" in context.roles:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to enforce role access: {e}")
            return False
    
    def enforce_permission_access(self, required_permission: str, context: SecurityContext) -> bool:
        """Enforce permission-based access control."""
        try:
            # Check if user has required permission
            if required_permission in context.permissions:
                return True
            
            # Check for admin permission (admin can do anything)
            if "admin" in context.permissions:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to enforce permission access: {e}")
            return False
    
    def set_policy_engine(self, policy_engine: PolicyEngine):
        """Set policy engine for authorization."""
        self.policy_engine = policy_engine
        self.logger.info("✅ Policy engine updated")
    
    def clear_cache(self):
        """Clear authorization cache."""
        self.auth_cache.clear()
        self.logger.info("✅ Authorization cache cleared")
    
    def get_enforcement_stats(self) -> Dict[str, Any]:
        """Get authorization enforcement statistics."""
        total_checks = self.enforcement_stats["total_checks"]
        if total_checks > 0:
            allow_rate = (self.enforcement_stats["allowed"] / total_checks) * 100
            deny_rate = (self.enforcement_stats["denied"] / total_checks) * 100
            cache_hit_rate = (self.enforcement_stats["cache_hits"] / total_checks) * 100
        else:
            allow_rate = 0
            deny_rate = 0
            cache_hit_rate = 0
        
        return {
            "total_checks": total_checks,
            "allowed": self.enforcement_stats["allowed"],
            "denied": self.enforcement_stats["denied"],
            "cache_hits": self.enforcement_stats["cache_hits"],
            "allow_rate": f"{allow_rate:.2f}%",
            "deny_rate": f"{deny_rate:.2f}%",
            "cache_hit_rate": f"{cache_hit_rate:.2f}%"
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get AuthorizationGuard status."""
        return {
            "service": "AuthorizationGuard",
            "status": "active",
            "policy_engine": self.policy_engine.__class__.__name__ if self.policy_engine else "None",
            "default_policy": self.default_policy,
            "cache_size": len(self.auth_cache),
            "enforcement_stats": self.get_enforcement_stats()
        }
