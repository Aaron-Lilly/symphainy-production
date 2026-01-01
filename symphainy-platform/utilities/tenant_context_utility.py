#!/usr/bin/env python3
"""
Tenant Context Utility - Clean Tenant Context Building

Builds and injects tenant context with no enforcement decisions.
This is the refactored security capability with clean separation of concerns.

WHAT (Utility Role): I build and inject tenant context
HOW (Utility Implementation): I use clean interfaces with no enforcement logic
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class IsolationContext:
    """Tenant isolation context data structure - no enforcement logic."""
    user_tenant: str
    resource_tenant: str
    user_tenant_type: str
    resource_tenant_type: str
    isolation_required: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class FeatureContext:
    """Feature access context data structure - no enforcement logic."""
    tenant_id: str
    feature: str
    tenant_type: str
    feature_available: bool
    usage_limits: Dict[str, Any] = field(default_factory=dict)
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

class TenantContextUtility:
    """
    Tenant Context Utility - Clean Tenant Context Building
    
    Builds and injects tenant context with no enforcement decisions.
    This utility only builds context - it does not make authorization decisions.
    """
    
    def __init__(self):
        """Initialize Tenant Context Utility."""
        self.logger = logging.getLogger("TenantContextUtility")
        self.logger.info("✅ Tenant Context Utility initialized")
    
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
                tenant_info = await self._get_tenant_info(tenant_id)
            
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
    
    async def build_tenant_isolation_context(self, user_tenant: str, resource_tenant: str) -> IsolationContext:
        """Build tenant isolation context - no enforcement decisions."""
        try:
            # Get tenant information for both tenants
            user_tenant_info = await self._get_tenant_info(user_tenant)
            resource_tenant_info = await self._get_tenant_info(resource_tenant)
            
            # Build isolation context
            context = IsolationContext(
                user_tenant=user_tenant,
                resource_tenant=resource_tenant,
                user_tenant_type=user_tenant_info.get("tenant_type", "individual"),
                resource_tenant_type=resource_tenant_info.get("tenant_type", "individual"),
                isolation_required=user_tenant_info.get("isolation_level", "strict") == "strict"
            )
            
            self.logger.info(f"✅ Tenant isolation context built: {user_tenant} -> {resource_tenant}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build tenant isolation context: {str(e)}")
            # Return default context on error
            return IsolationContext(
                user_tenant=user_tenant,
                resource_tenant=resource_tenant,
                user_tenant_type="individual",
                resource_tenant_type="individual",
                isolation_required=True
            )
    
    async def build_feature_access_context(self, tenant_id: str, feature: str) -> FeatureContext:
        """Build feature access context - no enforcement decisions."""
        try:
            # Get tenant information
            tenant_info = await self._get_tenant_info(tenant_id)
            
            # Check if feature is available for tenant
            tenant_features = tenant_info.get("features", [])
            feature_available = feature in tenant_features
            
            # Get usage limits for feature
            usage_limits = tenant_info.get("limits", {}).get(feature, {})
            
            # Build feature context
            context = FeatureContext(
                tenant_id=tenant_id,
                feature=feature,
                tenant_type=tenant_info.get("tenant_type", "individual"),
                feature_available=feature_available,
                usage_limits=usage_limits
            )
            
            self.logger.info(f"✅ Feature access context built for tenant {tenant_id}, feature {feature}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build feature access context: {str(e)}")
            # Return default context on error
            return FeatureContext(
                tenant_id=tenant_id,
                feature=feature,
                tenant_type="individual",
                feature_available=False,
                usage_limits={}
            )
    
    # ============================================================================
    # TENANT INFORMATION BUILDING (No Enforcement)
    # ============================================================================
    
    async def build_tenant_hierarchy(self) -> Dict[str, Any]:
        """Build tenant hierarchy information - no enforcement decisions."""
        try:
            # Build tenant type hierarchy
            hierarchy = {
                "individual": {
                    "level": 1,
                    "max_users": 1,
                    "features": ["basic_analytics"],
                    "can_upgrade_to": ["organization", "enterprise"]
                },
                "organization": {
                    "level": 2,
                    "max_users": 50,
                    "features": ["basic_analytics", "team_collaboration", "advanced_analytics"],
                    "can_upgrade_to": ["enterprise"],
                    "can_downgrade_to": ["individual"]
                },
                "enterprise": {
                    "level": 3,
                    "max_users": 1000,
                    "features": ["basic_analytics", "team_collaboration", "advanced_analytics", "enterprise_features", "audit_logs"],
                    "can_downgrade_to": ["organization", "individual"]
                }
            }
            
            self.logger.info("✅ Tenant hierarchy built")
            return hierarchy
            
        except Exception as e:
            self.logger.error(f"Failed to build tenant hierarchy: {str(e)}")
            return {}
    
    async def build_tenant_limits(self, tenant_id: str, tenant_type: str) -> Dict[str, Any]:
        """Build tenant limits information - no enforcement decisions."""
        try:
            # Get limits based on tenant type
            limits = await self._get_limits_for_tenant_type(tenant_type)
            
            # Add tenant-specific information
            limits["tenant_id"] = tenant_id
            limits["tenant_type"] = tenant_type
            limits["created_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Tenant limits built for tenant {tenant_id}")
            return limits
            
        except Exception as e:
            self.logger.error(f"Failed to build tenant limits: {str(e)}")
            return {}
    
    # ============================================================================
    # CONTEXT VALIDATION (No Enforcement)
    # ============================================================================
    
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
    
    def is_isolation_context_valid(self, context: IsolationContext) -> bool:
        """Check if isolation context is valid - no enforcement decisions."""
        try:
            # Basic validation - context must have both tenants
            if not context.user_tenant or not context.resource_tenant:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate isolation context: {str(e)}")
            return False
    
    def is_feature_context_valid(self, context: FeatureContext) -> bool:
        """Check if feature context is valid - no enforcement decisions."""
        try:
            # Basic validation - context must have tenant_id and feature
            if not context.tenant_id or not context.feature:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate feature context: {str(e)}")
            return False
    
    # ============================================================================
    # PRIVATE HELPER METHODS (No Enforcement)
    # ============================================================================
    
    async def _get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information - no enforcement."""
        try:
            # This is a simplified tenant info retrieval
            # In real implementation, this would use tenant abstraction or similar
            
            # For now, return mock data based on tenant_id
            tenant_type = "individual"
            if "org" in tenant_id:
                tenant_type = "organization"
            elif "ent" in tenant_id:
                tenant_type = "enterprise"
            
            return {
                "tenant_name": f"tenant_{tenant_id}",
                "tenant_type": tenant_type,
                "max_users": self._get_max_users_for_type(tenant_type),
                "features": self._get_features_for_type(tenant_type),
                "limits": self._get_limits_for_type(tenant_type),
                "isolation_level": "strict",
                "is_active": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get tenant info: {str(e)}")
            return {}
    
    def _get_max_users_for_type(self, tenant_type: str) -> int:
        """Get max users for tenant type - no enforcement."""
        if tenant_type == "individual":
            return 1
        elif tenant_type == "organization":
            return 50
        elif tenant_type == "enterprise":
            return 1000
        else:
            return 1
    
    def _get_features_for_type(self, tenant_type: str) -> List[str]:
        """Get features for tenant type - no enforcement."""
        if tenant_type == "individual":
            return ["basic_analytics", "file_upload"]
        elif tenant_type == "organization":
            return ["basic_analytics", "file_upload", "team_collaboration", "advanced_analytics"]
        elif tenant_type == "enterprise":
            return ["basic_analytics", "file_upload", "team_collaboration", "advanced_analytics", "enterprise_features", "audit_logs"]
        else:
            return ["basic_analytics"]
    
    def _get_limits_for_type(self, tenant_type: str) -> Dict[str, Any]:
        """Get limits for tenant type - no enforcement."""
        if tenant_type == "individual":
            return {"max_storage": "1GB", "max_files": 100, "max_analyses": 10}
        elif tenant_type == "organization":
            return {"max_storage": "10GB", "max_files": 1000, "max_analyses": 100}
        elif tenant_type == "enterprise":
            return {"max_storage": "100GB", "max_files": 10000, "max_analyses": 1000}
        else:
            return {"max_storage": "1GB", "max_files": 100, "max_analyses": 10}
    
    async def _get_limits_for_tenant_type(self, tenant_type: str) -> Dict[str, Any]:
        """Get limits for tenant type - no enforcement."""
        return self._get_limits_for_type(tenant_type)
    
    # ============================================================================
    # UTILITY STATUS
    # ============================================================================
    
    def get_utility_status(self) -> Dict[str, Any]:
        """Get utility status information."""
        return {
            "utility_name": "TenantContextUtility",
            "status": "active",
            "capabilities": [
                "build_tenant_context",
                "build_tenant_isolation_context",
                "build_feature_access_context",
                "build_tenant_hierarchy",
                "build_tenant_limits"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }



