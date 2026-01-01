#!/usr/bin/env python3
"""
Tenant Abstraction - Generic Infrastructure Implementation

Generic tenant implementation using real adapters.
This is Layer 3 of the 5-layer security architecture.

WHAT (Infrastructure Role): I provide generic tenant services
HOW (Infrastructure Implementation): I use real adapters with generic interfaces
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantProtocol, TenantContext
from ..infrastructure_adapters.redis_adapter import RedisAdapter
from ..infrastructure_adapters.config_adapter import ConfigAdapter

logger = logging.getLogger(__name__)

class TenantAbstraction(TenantProtocol):
    """
    Generic tenant abstraction using real adapters.
    
    This abstraction implements the TenantProtocol using real
    Redis and Config adapters, providing a generic interface.
    """
    
    def __init__(self, redis_adapter: RedisAdapter, config_adapter: ConfigAdapter, di_container=None):
        """
        Initialize Tenant abstraction with real adapters.
        
        Args:
            redis_adapter: Redis adapter
            config_adapter: Configuration adapter
            di_container: Dependency injection container
        """
        self.redis = redis_adapter
        self.config = config_adapter
        self.di_container = di_container
        self.service_name = "tenant_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Tenant abstraction initialized with real adapters")
    
    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant configuration using real adapters."""
        try:
            # Try to get from Redis cache first
            cache_key = f"tenant_config:{tenant_id}"
            cached_config = await self.redis.get(cache_key)
            
            if cached_config:
                import json
                config = json.loads(cached_config)
                self.logger.info(f"✅ Retrieved tenant config from cache for tenant {tenant_id}")
                return config
            
            # If not in cache, get from config adapter
            multi_tenant_config = self.config.get_multi_tenant_config()
            default_tenant_type = self.config.get_default_tenant_type()
            
            # Create default tenant config
            tenant_config = {
                "tenant_id": tenant_id,
                "tenant_type": default_tenant_type,
                "max_users": self._get_max_users_for_type(default_tenant_type),
                "features": self._get_features_for_type(default_tenant_type),
                "limits": self._get_limits_for_type(default_tenant_type),
                "isolation_level": "strict" if self.config.is_tenant_isolation_strict() else "relaxed",
                "rls_enabled": self.config.is_rls_enabled(),
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            # Cache the config
            await self.redis.set(cache_key, json.dumps(tenant_config), ttl=3600)
            
            self.logger.info(f"✅ Retrieved tenant config for tenant {tenant_id}")
            return tenant_config
            
        except Exception as e:
            self.logger.error(f"❌ Get tenant config error: {str(e)}")
    
            raise  # Re-raise for service layer to handle

        """Validate tenant access using real adapters."""
        try:
            if not user_tenant or not resource_tenant:
                raise  # Re-raise for service layer to handle

                return True  # No tenant isolation if multi-tenancy is disabled
            
            # Check if tenant isolation is strict
            if not self.config.is_tenant_isolation_strict():
                return True  # No strict isolation
            
            # Users can only access resources from their own tenant
            result = user_tenant == resource_tenant
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Tenant access validation error: {str(e)}")
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
            
            # Get tenant config to determine features
            tenant_config = await self.get_tenant_config(tenant_id)
            features = tenant_config.get("features", [])
            
            # Cache the features
            await self.redis.set(cache_key, json.dumps(features), ttl=3600)
            
            self.logger.info(f"✅ Retrieved features for tenant {tenant_id}")
            return features
            
        except Exception as e:
            self.logger.error(f"❌ Get tenant features error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Check if feature is enabled for tenant using real adapters."""
        try:
            # Get tenant features
            features = await self.get_tenant_features(tenant_id)
            return feature in features
            
        except Exception as e:
            self.logger.error(f"❌ Feature enabled check error: {str(e)}")
            raise  # Re-raise for service layer to handle

        """Get tenant limits using real adapters."""
        try:
            # Try to get from Redis cache first
            cache_key = f"tenant_limits:{tenant_id}"
            cached_limits = await self.redis.get(cache_key)
            
            if cached_limits:
                import json
                limits = json.loads(cached_limits)
                return limits
            
            # Get tenant config to determine limits
            tenant_config = await self.get_tenant_config(tenant_id)
            limits = tenant_config.get("limits", {})
            
            # Cache the limits
            await self.redis.set(cache_key, json.dumps(limits), ttl=3600)
            
            self.logger.info(f"✅ Retrieved limits for tenant {tenant_id}")
            return limits
            
        except Exception as e:
            self.logger.error(f"❌ Get tenant limits error: {str(e)}")
    
            raise  # Re-raise for service layer to handle

        """Create tenant context using real adapters."""
        try:
            # Get tenant config
            tenant_config = await self.get_tenant_config(tenant_id)
            
            # Create tenant context
            context = TenantContext(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                tenant_type=tenant_type,
                max_users=tenant_config.get("max_users", 1),
                features=tenant_config.get("features", []),
                limits=tenant_config.get("limits", {}),
                created_at=datetime.fromisoformat(tenant_config.get("created_at", datetime.utcnow().isoformat())),
                is_active=tenant_config.get("is_active", True)
            )
            
            self.logger.info(f"✅ Created tenant context for tenant {tenant_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Create tenant context error: {str(e)}")
            raise  # Re-raise for service layer to handle
    
    def _get_max_users_for_type(self, tenant_type: str) -> int:
        """Get max users for tenant type."""
        if tenant_type == "individual":
            return 1
        elif tenant_type == "organization":
            return 50
        elif tenant_type == "enterprise":
            return 1000
        else:
            return 1
    
    def _get_features_for_type(self, tenant_type: str) -> List[str]:
        """Get features for tenant type."""
        if tenant_type == "individual":
            return ["basic_analytics", "file_upload"]
        elif tenant_type == "organization":
            return ["basic_analytics", "file_upload", "team_collaboration", "advanced_analytics"]
        elif tenant_type == "enterprise":
            return ["basic_analytics", "file_upload", "team_collaboration", "advanced_analytics", "enterprise_features", "audit_logs"]
        else:
            return ["basic_analytics"]
    
    def _get_limits_for_type(self, tenant_type: str) -> Dict[str, Any]:
        """Get limits for tenant type."""
        if tenant_type == "individual":
            return {"max_storage": "1GB", "max_files": 100, "max_analyses": 10}
        elif tenant_type == "organization":
            return {"max_storage": "10GB", "max_files": 1000, "max_analyses": 100}
        elif tenant_type == "enterprise":
            return {"max_storage": "100GB", "max_files": 10000, "max_analyses": 1000}
        else:
            return {"max_storage": "1GB", "max_files": 100, "max_analyses": 10}
