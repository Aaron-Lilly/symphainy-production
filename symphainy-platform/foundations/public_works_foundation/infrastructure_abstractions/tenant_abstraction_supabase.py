#!/usr/bin/env python3
"""
Tenant Abstraction - Supabase Implementation

Corrected tenant abstraction using Supabase for tenant data storage.
This is Layer 3 of the 5-layer security architecture.

WHAT (Infrastructure Role): I provide tenant services with Supabase storage
HOW (Infrastructure Implementation): I use Supabase for tenant data with Redis caching
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantProtocol, TenantContext
from ..infrastructure_adapters.supabase_adapter import SupabaseAdapter
from ..infrastructure_adapters.redis_adapter import RedisAdapter
from ..infrastructure_adapters.config_adapter import ConfigAdapter

logger = logging.getLogger(__name__)

class TenantAbstraction(TenantProtocol):
    """
    Tenant abstraction using Supabase for tenant data storage.
    
    This abstraction implements the TenantProtocol using Supabase
    for tenant data storage and Redis for caching.
    """
    
    def __init__(self, supabase_adapter: SupabaseAdapter, redis_adapter: RedisAdapter, 
                 config_adapter: ConfigAdapter, di_container=None):
        """
        Initialize Tenant abstraction with Supabase and Redis.
        
        Args:
            supabase_adapter: Supabase adapter
            redis_adapter: Redis adapter
            config_adapter: Configuration adapter
            di_container: Dependency injection container
        """
        self.supabase = supabase_adapter
        self.redis = redis_adapter
        self.config = config_adapter
        self.di_container = di_container
        self.service_name = "tenant_abstraction_supabase"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Tenant table configuration
        self.tenant_table = "tenants"
        self.tenant_users_table = "tenant_users"
        
        self.logger.info("✅ Tenant abstraction initialized with Supabase + Redis")
    
    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant configuration using Supabase + Redis caching."""
        try:
            # Try to get from Redis cache first
            cache_key = f"tenant_config:{tenant_id}"
            cached_config = await self.redis.get(cache_key)
            
            if cached_config:
                config = json.loads(cached_config)
                self.logger.info(f"✅ Retrieved tenant config from cache for tenant {tenant_id}")
                return config
            
            # Get tenant data from Supabase
            tenant_data = await self.supabase.get_tenant_data(tenant_id)
            
            if tenant_data:
                # Create tenant config from Supabase data
                tenant_config = {
                    "tenant_id": tenant_id,
                    "tenant_name": tenant_data.get("tenant_name"),
                    "tenant_type": tenant_data.get("tenant_type", "standard"),
                    "max_users": tenant_data.get("max_users", 100),
                    "features": tenant_data.get("features", []),
                    "limits": tenant_data.get("limits", {}),
                    "isolation_level": tenant_data.get("isolation_level", "strict"),
                    "rls_enabled": tenant_data.get("rls_enabled", True),
                    "created_at": tenant_data.get("created_at"),
                    "updated_at": tenant_data.get("updated_at"),
                    "is_active": tenant_data.get("is_active", True)
                }
                
                # Cache the config
                await self.redis.set(cache_key, json.dumps(tenant_config), ttl=3600)
                
                self.logger.info(f"✅ Retrieved tenant config from Supabase for tenant {tenant_id}")
                return tenant_config
            else:
                # Create default tenant config if not found
                default_tenant_type = self.config.get_default_tenant_type()
                tenant_config = {
                    "tenant_id": tenant_id,
                    "tenant_name": f"Tenant {tenant_id}",
                    "tenant_type": default_tenant_type,
                    "max_users": self._get_max_users_for_type(default_tenant_type),
                    "features": self._get_features_for_type(default_tenant_type),
                    "limits": self._get_limits_for_type(default_tenant_type),
                    "isolation_level": "strict" if self.config.is_tenant_isolation_strict() else "relaxed",
                    "rls_enabled": self.config.is_rls_enabled(),
                    "created_at": datetime.utcnow().isoformat(),
                    "is_active": True
                }
                
                # Store default tenant in Supabase
                await self.supabase.create_tenant_data(tenant_config)
                
                # Cache the config
                await self.redis.set(cache_key, json.dumps(tenant_config), ttl=3600)
                
                self.logger.info(f"✅ Created default tenant config for tenant {tenant_id}")
                return tenant_config
            
        except Exception as e:
            self.logger.error(f"Failed to create default tenant config: {e}")
            raise  # Re-raise for service layer to handle
    
    async def validate_tenant_access(self, user_tenant: str, resource_tenant: str) -> bool:
        """Validate tenant access using Supabase."""
        try:
            if not user_tenant or not resource_tenant:
                raise  # Re-raise for service layer to handle

                return True  # No tenant isolation if multi-tenancy is disabled
            
            # Check if tenant isolation is strict
            if not self.config.is_tenant_isolation_strict():
                return True  # No strict isolation
            
            # Check tenant access in Supabase
            access_result = await self.supabase.validate_tenant_access(user_tenant, resource_tenant)
            
            if access_result:
                self.logger.debug(f"✅ Tenant access validated: {user_tenant} -> {resource_tenant}")
                return True
            else:
                self.logger.warning(f"⚠️ Tenant access denied: {user_tenant} -> {resource_tenant}")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Tenant access validation error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Get tenant features using Supabase."""
        try:
            # Try cache first
            cache_key = f"tenant_features:{tenant_id}"
            cached_features = await self.redis.get(cache_key)
            
            if cached_features:
                features = json.loads(cached_features)
                self.logger.debug(f"✅ Retrieved tenant features from cache for tenant {tenant_id}")
                return features
            
            # Get tenant data from Supabase
            tenant_data = await self.supabase.get_tenant_data(tenant_id)
            
            if tenant_data:
                features = tenant_data.get("features", [])
                
                # Cache features
                await self.redis.set(cache_key, json.dumps(features), ttl=1800)
                
                self.logger.debug(f"✅ Retrieved tenant features from Supabase for tenant {tenant_id}")
                return features
            else:
                # Return default features
                default_features = self._get_features_for_type("standard")
                self.logger.warning(f"⚠️ Tenant not found, returning default features for tenant {tenant_id}")
                return default_features
            
        except Exception as e:
            self.logger.error(f"❌ Get tenant features error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Get tenant limits using Supabase."""
        try:
            # Try cache first
            cache_key = f"tenant_limits:{tenant_id}"
            cached_limits = await self.redis.get(cache_key)
            
            if cached_limits:
                limits = json.loads(cached_limits)
                self.logger.debug(f"✅ Retrieved tenant limits from cache for tenant {tenant_id}")
                return limits
            
            # Get tenant data from Supabase
            tenant_data = await self.supabase.get_tenant_data(tenant_id)
            
            if tenant_data:
                limits = tenant_data.get("limits", {})
                
                # Cache limits
                await self.redis.set(cache_key, json.dumps(limits), ttl=1800)
                
                self.logger.debug(f"✅ Retrieved tenant limits from Supabase for tenant {tenant_id}")
                return limits
            else:
                # Return default limits
                default_limits = self._get_limits_for_type("standard")
                self.logger.warning(f"⚠️ Tenant not found, returning default limits for tenant {tenant_id}")
                return default_limits
            
        except Exception as e:
            self.logger.error(f"❌ Get tenant limits error: {str(e)}")
    
            raise  # Re-raise for service layer to handle

        """Create tenant using Supabase."""
        try:
            # Validate required fields
            required_fields = ["tenant_id", "tenant_name", "tenant_type"]
            for field in required_fields:
                if field not in tenant_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add default values
            enhanced_tenant_data = {
                **tenant_data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "max_users": tenant_data.get("max_users", self._get_max_users_for_type(tenant_data["tenant_type"])),
                "features": tenant_data.get("features", self._get_features_for_type(tenant_data["tenant_type"])),
                "limits": tenant_data.get("limits", self._get_limits_for_type(tenant_data["tenant_type"])),
                "isolation_level": tenant_data.get("isolation_level", "strict"),
                "rls_enabled": tenant_data.get("rls_enabled", True)
            }
            
            # Create tenant in Supabase
            result = await self.supabase.create_tenant_data(enhanced_tenant_data)
            
            if result:
                # Clear cache
                await self._clear_tenant_cache(tenant_data["tenant_id"])
                
                self.logger.info(f"✅ Tenant created: {tenant_data['tenant_id']}")
                
                return tenant_data["tenant_id"]
            else:
                raise Exception("Failed to create tenant in Supabase")
            
        except Exception as e:
            self.logger.error(f"❌ Create tenant error: {str(e)}")
            raise
    
            raise  # Re-raise for service layer to handle
    async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> bool:
        """Update tenant using Supabase."""
        try:
            # Validate updates
            allowed_updates = ["tenant_name", "tenant_type", "max_users", "features", 
                             "limits", "isolation_level", "rls_enabled", "is_active"]
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_updates}
            
            if not filtered_updates:
                raise ValueError("No valid updates provided")
            
            # Add update timestamp
            filtered_updates["updated_at"] = datetime.utcnow().isoformat()
            
            # Update tenant in Supabase
            result = await self.supabase.update_tenant_data(tenant_id, filtered_updates)
            
            if result:
                # Clear cache
                await self._clear_tenant_cache(tenant_id)
                
                self.logger.info(f"✅ Tenant updated: {tenant_id}")
                
                return True
            else:
                self.logger.error(f"❌ Failed to update tenant: {tenant_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Update tenant error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Delete tenant using Supabase."""
        try:
            # Soft delete by updating status
            updates = {
                "is_active": False,
                "deleted_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update tenant in Supabase
            result = await self.supabase.update_tenant_data(tenant_id, updates)
            
            if result:
                # Clear cache
                await self._clear_tenant_cache(tenant_id)
                
                self.logger.info(f"✅ Tenant deleted: {tenant_id}")
                
                return True
            else:
                self.logger.error(f"❌ Failed to delete tenant: {tenant_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Delete tenant error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """List tenants using Supabase."""
        try:
            # Add default filters
            enhanced_filters = {
                "is_active": True,
                **(filters or {})
            }
            
            # List tenants from Supabase
            result = await self.supabase.list_tenant_data(
                filters=enhanced_filters,
                limit=limit,
                offset=offset
            )
            
            self.logger.debug(f"✅ Listed {len(result)} tenants")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ List tenants error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Get tenant context using Supabase."""
        try:
            # Get tenant config
            tenant_config = await self.get_tenant_config(tenant_id)
            
            if tenant_config:
                return TenantContext(
                    tenant_id=tenant_id,
                    tenant_name=tenant_config.get("tenant_name"),
                    security_config=tenant_config,
                    isolation_level=tenant_config.get("isolation_level", "strict")
                )
            else:
                raise ValueError(f"Tenant config not found for tenant {tenant_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Get tenant context error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Health check for tenant abstraction."""
        try:
            # Check Supabase health
            supabase_health = await self.supabase.health_check()
            
            # Check Redis health
            redis_health = await self.redis.health_check()
            
            # Add business logic health checks
            if supabase_health.get("status") == "healthy" and redis_health.get("status") == "healthy":
                # Test tenant operations
                test_tenants = await self.list_tenants(limit=1)
                result = {
                    "status": "healthy",
                    "supabase": supabase_health,
                    "redis": redis_health,
                    "business_logic": "operational",
                    "test_results": {"tenant_count": len(test_tenants)}
                }
            else:
                result = {
                    "status": "unhealthy",
                    "supabase": supabase_health,
                    "redis": redis_health,
                    "business_logic": "degraded"
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Health check error: {str(e)}")
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
            raise  # Re-raise for service layer to handle

        """Clear tenant-related cache entries."""
        try:
            cache_keys = [
                f"tenant_config:{tenant_id}",
                f"tenant_features:{tenant_id}",
                f"tenant_limits:{tenant_id}"
            ]
            
            for key in cache_keys:
                await self.redis.delete(key)
            
            self.logger.debug(f"✅ Cleared cache for tenant: {tenant_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            self.logger.warning(f"⚠️ Failed to clear cache for tenant {tenant_id}: {str(e)}")
    
            raise  # Re-raise for service layer to handle

        """Get max users for tenant type."""
        limits = {
            "free": 5,
            "standard": 100,
            "premium": 1000,
            "enterprise": 10000
        }
        return limits.get(tenant_type, 100)
    
    def _get_features_for_type(self, tenant_type: str) -> List[str]:
        """Get features for tenant type."""
        features = {
            "free": ["basic_storage", "basic_analytics"],
            "standard": ["basic_storage", "basic_analytics", "file_sharing", "collaboration"],
            "premium": ["advanced_storage", "advanced_analytics", "file_sharing", "collaboration", "api_access"],
            "enterprise": ["unlimited_storage", "advanced_analytics", "file_sharing", "collaboration", "api_access", "custom_integrations", "priority_support"]
        }
        return features.get(tenant_type, ["basic_storage", "basic_analytics"])
    
    def _get_limits_for_type(self, tenant_type: str) -> Dict[str, Any]:
        """Get limits for tenant type."""
        limits = {
            "free": {
                "storage_gb": 1,
                "files_per_month": 100,
                "api_calls_per_month": 1000
            },
            "standard": {
                "storage_gb": 100,
                "files_per_month": 10000,
                "api_calls_per_month": 100000
            },
            "premium": {
                "storage_gb": 1000,
                "files_per_month": 100000,
                "api_calls_per_month": 1000000
            },
            "enterprise": {
                "storage_gb": -1,  # Unlimited
                "files_per_month": -1,  # Unlimited
                "api_calls_per_month": -1  # Unlimited
            }
        }
        return limits.get(tenant_type, limits["standard"])
