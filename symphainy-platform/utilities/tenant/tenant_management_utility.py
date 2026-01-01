"""
Tenant Management Utility

Provides basic tenant operations that can be used across the platform.
Follows the lightweight utility pattern - delegates heavy lifting to Security Guard.

WHAT (Utility Role): I provide basic tenant operations
HOW (Utility Implementation): I delegate complex operations to Security Guard
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TenantManagementUtility:
    """Utility for basic tenant operations."""
    
    def __init__(self, env_loader):
        """Initialize tenant management utility."""
        self.env_loader = env_loader
        if env_loader is not None:
            self.multi_tenant_enabled = env_loader.is_multi_tenant_enabled()
        else:
            self.multi_tenant_enabled = False
        self.logger = logging.getLogger("TenantManagementUtility")
        
        self.logger.info(f"Tenant Management Utility initialized - Multi-tenant: {self.multi_tenant_enabled}")
    
    def get_tenant_config(self, tenant_type: str) -> Dict[str, Any]:
        """Get configuration for tenant type."""
        if not self.multi_tenant_enabled or self.env_loader is None:
            return {"max_users": 1, "features": ["basic_analytics"], "type": "individual"}
        
        # Use the available method from ConfigurationUtility
        multi_tenant_config = self.env_loader.get_multi_tenant_config()
        
        # Return tenant-specific config based on type
        if tenant_type == "individual":
            return {
                "max_users": 1,
                "features": ["basic_analytics"],
                "type": "individual"
            }
        elif tenant_type == "organization":
            return {
                "max_users": 50,
                "features": ["basic_analytics", "advanced_analytics", "team_collaboration"],
                "type": "organization"
            }
        elif tenant_type == "enterprise":
            return {
                "max_users": 1000,
                "features": ["basic_analytics", "advanced_analytics", "team_collaboration", "enterprise_features"],
                "type": "enterprise"
            }
        else:
            return multi_tenant_config.get("default_tenant_config", {"max_users": 1, "features": ["basic_analytics"], "type": "individual"})
    
    def validate_tenant_type(self, tenant_type: str) -> bool:
        """Validate tenant type."""
        valid_types = ["individual", "organization", "enterprise"]
        return tenant_type in valid_types
    
    def get_tenant_features(self, tenant_type: str) -> List[str]:
        """Get features available for tenant type."""
        config = self.get_tenant_config(tenant_type)
        return config.get("features", [])
    
    def can_user_access_feature(self, user_tenant_type: str, feature: str) -> bool:
        """Check if user's tenant type can access feature."""
        features = self.get_tenant_features(user_tenant_type)
        return feature in features
    
    def get_tenant_limits(self, tenant_type: str) -> Dict[str, Any]:
        """Get limits for tenant type."""
        config = self.get_tenant_config(tenant_type)
        return {
            "max_users": config.get("max_users", 1),
            "features": config.get("features", []),
            "type": config.get("type", "individual")
        }
    
    def is_multi_tenant_enabled(self) -> bool:
        """Check if multi-tenancy is enabled."""
        return self.multi_tenant_enabled
    
    def get_default_tenant_type(self) -> str:
        """Get default tenant type."""
        if self.env_loader is None:
            return "individual"
        return self.env_loader.config_manager.get("DEFAULT_TENANT_TYPE", "individual")
    
    def validate_tenant_access(self, user_tenant_id: str, resource_tenant_id: str) -> bool:
        """Validate if user can access resource from another tenant."""
        if not self.multi_tenant_enabled:
            return True  # No tenant isolation if multi-tenancy is disabled
        
        # Users can only access resources from their own tenant
        return user_tenant_id == resource_tenant_id
    
    def get_tenant_metadata(self, tenant_type: str) -> Dict[str, Any]:
        """Get metadata for tenant type."""
        config = self.get_tenant_config(tenant_type)
        return {
            "type": tenant_type,
            "max_users": config.get("max_users", 1),
            "features": config.get("features", []),
            "created_at": datetime.utcnow().isoformat(),
            "is_enterprise": tenant_type == "enterprise",
            "is_organization": tenant_type == "organization",
            "is_individual": tenant_type == "individual"
        }
    
    def create_tenant_context(self, tenant_id: str, tenant_type: str, tenant_name: str) -> Dict[str, Any]:
        """Create tenant context for operations."""
        config = self.get_tenant_config(tenant_type)
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "tenant_type": tenant_type,
            "max_users": config.get("max_users", 1),
            "features": config.get("features", []),
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
    
    def validate_tenant_creation(self, tenant_type: str, admin_user_id: str) -> Dict[str, Any]:
        """Validate if tenant can be created."""
        if not self.multi_tenant_enabled:
            return {"valid": False, "error": "Multi-tenancy not enabled"}
        
        if not self.validate_tenant_type(tenant_type):
            return {"valid": False, "error": f"Invalid tenant type: {tenant_type}"}
        
        # Additional validation logic could be added here
        # For example, checking if user already has a tenant, etc.
        
        return {"valid": True, "message": "Tenant creation validated"}
    
    def get_tenant_hierarchy(self) -> Dict[str, Any]:
        """Get tenant type hierarchy and relationships."""
        return {
            "individual": {
                "level": 1,
                "max_users": 1,
                "features": self.get_tenant_features("individual"),
                "can_upgrade_to": ["organization", "enterprise"]
            },
            "organization": {
                "level": 2,
                "max_users": 50,
                "features": self.get_tenant_features("organization"),
                "can_upgrade_to": ["enterprise"],
                "can_downgrade_to": ["individual"]
            },
            "enterprise": {
                "level": 3,
                "max_users": 1000,
                "features": self.get_tenant_features("enterprise"),
                "can_downgrade_to": ["organization", "individual"]
            }
        }
    
    def get_multi_tenant_config(self) -> Dict[str, Any]:
        """Get multi-tenant configuration."""
        if self.env_loader is None:
            return {
                "enabled": False,
                "default_tenant_type": "individual",
                "max_tenants_per_user": 1,
                "tenant_limits": {"individual": 1, "organization": 50, "enterprise": 1000},
                "tenant_features": {"individual": ["basic_analytics"], "organization": ["basic_analytics", "team_collaboration"], "enterprise": ["basic_analytics", "team_collaboration", "advanced_insights"]},
                "security_guard": {"mcp_server_url": "http://localhost:8001"},
                "caching": {"tenant_cache_ttl": 3600, "user_context_cache_ttl": 1800},
                "rls": {"enabled": True, "strict_isolation": True}
            }
        return self.env_loader.get_multi_tenant_config()
    
    def get_features_for_tenant_type(self, tenant_type: str) -> List[str]:
        """Get features for tenant type."""
        return self.get_tenant_features(tenant_type)
    
    def get_security_guard_mcp_url(self) -> str:
        """Get Security Guard MCP server URL."""
        config = self.get_multi_tenant_config()
        return config.get("security_guard", {}).get("mcp_server_url", "http://localhost:8001")
    
    def get_tenant_cache_ttl(self) -> int:
        """Get tenant cache TTL."""
        config = self.get_multi_tenant_config()
        return config.get("caching", {}).get("tenant_cache_ttl", 3600)
    
    def get_user_context_cache_ttl(self) -> int:
        """Get user context cache TTL."""
        config = self.get_multi_tenant_config()
        return config.get("caching", {}).get("user_context_cache_ttl", 1800)
    
    def is_rls_enabled(self) -> bool:
        """Check if RLS is enabled."""
        config = self.get_multi_tenant_config()
        return config.get("rls", {}).get("enabled", True)
    
    def is_tenant_isolation_strict(self) -> bool:
        """Check if tenant isolation is strict."""
        config = self.get_multi_tenant_config()
        return config.get("rls", {}).get("strict_isolation", True)
    
    def calculate_tenant_usage(self, tenant_id: str, current_users: int, tenant_type: str) -> Dict[str, Any]:
        """Calculate tenant usage statistics."""
        config = self.get_tenant_config(tenant_type)
        max_users = config.get("max_users", 1)
        
        usage_percentage = (current_users / max_users) * 100 if max_users > 0 else 0
        
        return {
            "tenant_id": tenant_id,
            "tenant_type": tenant_type,
            "current_users": current_users,
            "max_users": max_users,
            "usage_percentage": round(usage_percentage, 2),
            "is_at_limit": current_users >= max_users,
            "can_add_users": current_users < max_users,
            "remaining_capacity": max(0, max_users - current_users)
        }
    
    def get_tenant_health_status(self, tenant_id: str, tenant_type: str, current_users: int) -> Dict[str, Any]:
        """Get tenant health status."""
        usage = self.calculate_tenant_usage(tenant_id, current_users, tenant_type)
        
        if usage["usage_percentage"] >= 90:
            status = "critical"
        elif usage["usage_percentage"] >= 75:
            status = "warning"
        elif usage["usage_percentage"] >= 50:
            status = "moderate"
        else:
            status = "healthy"
        
        return {
            "tenant_id": tenant_id,
            "status": status,
            "usage": usage,
            "recommendations": self._get_tenant_recommendations(status, usage)
        }
    
    def _get_tenant_recommendations(self, status: str, usage: Dict[str, Any]) -> List[str]:
        """Get recommendations based on tenant status."""
        recommendations = []
        
        if status == "critical":
            recommendations.append("Consider upgrading to a higher tier")
            recommendations.append("Review user access and remove inactive users")
        elif status == "warning":
            recommendations.append("Monitor usage closely")
            recommendations.append("Consider planning for upgrade")
        elif status == "moderate":
            recommendations.append("Usage is healthy")
        else:
            recommendations.append("Tenant is operating efficiently")
        
        return recommendations
