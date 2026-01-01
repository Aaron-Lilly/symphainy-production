#!/usr/bin/env python3
"""
Authorization Abstraction - Generic Infrastructure Implementation

Generic authorization implementation using real adapters.
This is Layer 3 of the 5-layer security architecture.

WHAT (Infrastructure Role): I provide generic authorization services
HOW (Infrastructure Implementation): I use real adapters with generic interfaces
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.authorization_protocol import AuthorizationProtocol, AuthorizationContext
from foundations.public_works_foundation.abstraction_contracts.policy_engine_protocol import PolicyEngine
from ..infrastructure_adapters.redis_adapter import RedisAdapter
from ..infrastructure_adapters.supabase_adapter import SupabaseAdapter

logger = logging.getLogger(__name__)

class AuthorizationAbstraction(AuthorizationProtocol):
    """
    Generic authorization abstraction using real adapters.
    
    This abstraction implements the AuthorizationProtocol using real
    Redis and Supabase adapters, providing a generic interface.
    """
    
    def __init__(self, redis_adapter: RedisAdapter, supabase_adapter: SupabaseAdapter, policy_engine: Optional[PolicyEngine] = None, di_container=None):
        """
        Initialize Authorization abstraction with real adapters.
        
        Args:
            redis_adapter: Redis adapter for caching
            supabase_adapter: Supabase adapter for user data
            policy_engine: Optional policy engine for authorization
            di_container: Dependency injection container
        """
        self.redis = redis_adapter
        self.supabase = supabase_adapter
        self.policy_engine = policy_engine
        self.di_container = di_container
        self.service_name = "authorization_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Authorization Abstraction initialized")
    
    async def enforce(self, action: str, resource: str, context: 'SecurityContext') -> bool:
        """
        Enforce authorization using real adapters and policy engine.
        
        Zero-trust authorization: "Secure by design, open by policy"
        
        For MVP: Open policy (allow all authenticated users)
        For Production: Policy engine + permissions + tenant isolation
        """
        try:
            # For API endpoints (starting with /api/), skip tenant access check
            # Tenant isolation is for data resources, not API endpoints
            if not resource.startswith("/api/"):
                # Check tenant access for data resources
                if not await self.check_tenant_access(context.tenant_id, resource):
                    self.logger.warning(f"Tenant access denied: {context.tenant_id} -> {resource}")
                    return False
            
            # Use policy engine if available
            if self.policy_engine:
                allowed = await self.policy_engine.is_allowed(action, resource, context)
                if not allowed:
                    self.logger.warning(f"Policy engine denied: {action} on {resource}")
                    return False
            
            # MVP: Open policy for authenticated users
            # For production, implement proper permission checks
            if context.user_id and context.user_id != "anonymous":
                self.logger.info(f"✅ Authorization granted (MVP open policy): {action} on {resource} for {context.user_id}")
                return True
            
            # DEMO MODE: Allow anonymous access to API endpoints for demo purposes
            # TODO: Remove this for production - require proper authentication
            if resource.startswith("/api/"):
                self.logger.info(f"✅ Authorization granted (demo mode - anonymous API access): {action} on {resource}")
                return True
            
            # Check user permissions for anonymous users (non-API resources)
            user_permissions = await self.get_user_permissions(context.user_id)
            # FIX: Simple permission check - if user has any permissions, allow
            # For MVP: Open policy (allow if user exists)
            if user_permissions and len(user_permissions) > 0:
                self.logger.info(f"✅ Authorization granted (user has permissions): {action} on {resource}")
                return True
            else:
                self.logger.warning(f"Permission denied: {action} on {resource} - no permissions")
                return False
            
            self.logger.info(f"✅ Authorization granted: {action} on {resource}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Authorization enforcement error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Get user permissions using real Redis adapter."""
        try:
            # Try to get from Redis cache first
            cache_key = f"user_permissions:{user_id}"
            cached_permissions = await self.redis.get(cache_key)
            
            if cached_permissions:
                import json
                permissions = json.loads(cached_permissions)
                self.logger.info(f"✅ Retrieved permissions from cache for user {user_id}")
                return permissions
            
            # If not in cache, get from Supabase
            result = await self.supabase.admin_get_user(user_id)
            if result.get("success"):
                user_data = result.get("user", {})
                permissions = user_data.get("user_metadata", {}).get("permissions", [])
                
                # Cache the permissions
                await self.redis.set(cache_key, json.dumps(permissions), ttl=1800)
                
                self.logger.info(f"✅ Retrieved permissions from Supabase for user {user_id}")
                return permissions
            
            # Default permissions if user not found
            default_permissions = ["read", "write"]
            await self.redis.set(cache_key, json.dumps(default_permissions), ttl=1800)
            
            return default_permissions
            
        except Exception as e:
            self.logger.error(f"❌ Get user permissions error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Check tenant access using real adapters."""
        try:
            if not user_tenant or not resource_tenant:
                raise  # Re-raise for service layer to handle

            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Tenant access check error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Validate feature access using real adapters."""
        try:
            # Get user info to check tenant features
            result = await self.supabase.admin_get_user(user_id)
            if not result.get("success"):
                return False
            
            user_data = result.get("user", {})
            tenant_id = user_data.get("user_metadata", {}).get("tenant_id")
            
            if not tenant_id:
                return False
            
            # Check tenant features (this would typically come from a tenant service)
            # For now, we'll use a simple approach
            tenant_features = await self._get_tenant_features(tenant_id)
            result = feature in tenant_features
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Feature access validation error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Get tenant policies using real adapters."""
        try:
            # Try to get from Redis cache first
            cache_key = f"tenant_policies:{tenant_id}"
            cached_policies = await self.redis.get(cache_key)
            
            if cached_policies:
                import json
                policies = json.loads(cached_policies)
                self.logger.info(f"✅ Retrieved policies from cache for tenant {tenant_id}")
                return policies
            
            # If not in cache, get default policies
            default_policies = {
                "tenant_id": tenant_id,
                "isolation_level": "strict",
                "features": ["basic_analytics"],
                "limits": {"max_users": 1, "max_storage": "1GB"},
                "policies": {
                    "data_access": "tenant_only",
                    "cross_tenant": False,
                    "audit_logging": True
                }
            }
            
            # Cache the policies
            await self.redis.set(cache_key, json.dumps(default_policies), ttl=3600)
            
            self.logger.info(f"✅ Retrieved default policies for tenant {tenant_id}")
            
            return default_policies
            
        except Exception as e:
            self.logger.error(f"❌ Get tenant policies error: {str(e)}")
    
            raise  # Re-raise for service layer to handle

        """Update authorization policy using real adapters."""
        try:
            # Store policy in Redis
            policy_key = f"role_policy:{role}"
            import json
            policy_data = {
                "role": role,
                "permissions": permissions,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            success = await self.redis.set(policy_key, json.dumps(policy_data), ttl=86400)
            
            if success:
                self.logger.info(f"✅ Authorization policy updated for role: {role}")
            else:
                self.logger.warning(f"Failed to update authorization policy for role: {role}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Update authorization policy error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Check if user has required permissions."""
        try:
            # Simple permission checking logic
            # In a real implementation, this would be more sophisticated
            
            if "admin" in permissions:
                return True
            
            if action == "read" and "read" in permissions:
                return True
            
            if action == "write" and "write" in permissions:
                return True
            
            if action == "delete" and "delete" in permissions:
                return True
            
            # Check for resource-specific permissions
            resource_permission = f"{action}:{resource}"
            if resource_permission in permissions:
                return True
            
            return False
            
        except Exception as e:
            # Sync method - just use logger (error_handler is async)
            self.logger.error(f"❌ Permission check error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Get tenant features using real adapters."""
        try:
            # Try to get from Redis cache first
            cache_key = f"tenant_features:{tenant_id}"
            cached_features = await self.redis.get(cache_key)
            
            if cached_features:
                import json
                features = json.loads(cached_features)
                return features
            
            # Default features based on tenant type
            # In a real implementation, this would come from a tenant service
            default_features = ["basic_analytics", "file_upload"]
            
            # Cache the features
            await self.redis.set(cache_key, json.dumps(default_features), ttl=3600)
            
            return default_features
            
        except Exception as e:
            self.logger.error(f"❌ Get tenant features error: {str(e)}")
            raise  # Re-raise for service layer to handle
