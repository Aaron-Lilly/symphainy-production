#!/usr/bin/env python3
"""
Tenant Context Utility - Integrated with Infrastructure

Builds and injects tenant context using infrastructure abstractions.
This integrates the refactored security capabilities with the 5-layer infrastructure.

WHAT (Utility Role): I build and inject tenant context using infrastructure
HOW (Utility Implementation): I use infrastructure abstractions with no enforcement logic
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

from contracts.tenant_protocol import TenantProtocol

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

class TenantContextUtilityIntegrated:
    """
    Tenant Context Utility - Integrated with Infrastructure
    
    Builds and injects tenant context using infrastructure abstractions.
    This utility only builds context - it does not make enforcement decisions.
    """
    
    def __init__(self, tenant_abstraction: TenantProtocol):
        """Initialize Tenant Context Utility with infrastructure abstractions."""
        self.tenant_abstraction = tenant_abstraction
        self.logger = logging.getLogger("TenantContextUtilityIntegrated")
        self.logger.info("✅ Tenant Context Utility Integrated initialized with infrastructure abstractions")
    
    # ============================================================================
    # TENANT CONTEXT BUILDING (Using Infrastructure Abstractions)
    # ============================================================================
    
    async def build_tenant_context(self, tenant_id: str) -> TenantContext:
        """Build tenant context using infrastructure abstractions."""
        try:
            # Use tenant abstraction to get tenant configuration
            tenant_config = await self.tenant_abstraction.get_tenant_config(tenant_id)
            
            # Build tenant context from infrastructure configuration
            context = TenantContext(
                tenant_id=tenant_id,
                tenant_name=tenant_config.get("tenant_name", f"tenant_{tenant_id}"),
                tenant_type=tenant_config.get("tenant_type", "individual"),
                max_users=tenant_config.get("max_users", 1),
                features=tenant_config.get("features", []),
                limits=tenant_config.get("limits", {}),
                is_active=tenant_config.get("is_active", True)
            )
            
            self.logger.info(f"✅ Tenant context built using infrastructure for tenant: {tenant_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build tenant context using infrastructure: {str(e)}")
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
        """Build tenant isolation context using infrastructure abstractions."""
        try:
            # Get tenant configurations for both tenants
            user_tenant_config = await self.tenant_abstraction.get_tenant_config(user_tenant)
            resource_tenant_config = await self.tenant_abstraction.get_tenant_config(resource_tenant)
            
            # Build isolation context
            context = IsolationContext(
                user_tenant=user_tenant,
                resource_tenant=resource_tenant,
                user_tenant_type=user_tenant_config.get("tenant_type", "individual"),
                resource_tenant_type=resource_tenant_config.get("tenant_type", "individual"),
                isolation_required=user_tenant_config.get("isolation_level", "strict") == "strict"
            )
            
            self.logger.info(f"✅ Tenant isolation context built using infrastructure: {user_tenant} -> {resource_tenant}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build tenant isolation context using infrastructure: {str(e)}")
            # Return default context on error
            return IsolationContext(
                user_tenant=user_tenant,
                resource_tenant=resource_tenant,
                user_tenant_type="individual",
                resource_tenant_type="individual",
                isolation_required=True
            )
    
    async def build_feature_access_context(self, tenant_id: str, feature: str) -> FeatureContext:
        """Build feature access context using infrastructure abstractions."""
        try:
            # Get tenant configuration
            tenant_config = await self.tenant_abstraction.get_tenant_config(tenant_id)
            
            # Check if feature is available for tenant
            tenant_features = tenant_config.get("features", [])
            feature_available = feature in tenant_features
            
            # Get usage limits for feature
            usage_limits = tenant_config.get("limits", {}).get(feature, {})
            
            # Build feature context
            context = FeatureContext(
                tenant_id=tenant_id,
                feature=feature,
                tenant_type=tenant_config.get("tenant_type", "individual"),
                feature_available=feature_available,
                usage_limits=usage_limits
            )
            
            self.logger.info(f"✅ Feature access context built using infrastructure for tenant {tenant_id}, feature {feature}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build feature access context using infrastructure: {str(e)}")
            # Return default context on error
            return FeatureContext(
                tenant_id=tenant_id,
                feature=feature,
                tenant_type="individual",
                feature_available=False,
                usage_limits={}
            )
    
    # ============================================================================
    # TENANT INFORMATION BUILDING (Using Infrastructure Abstractions)
    # ============================================================================
    
    async def build_tenant_hierarchy(self) -> Dict[str, Any]:
        """Build tenant hierarchy information using infrastructure abstractions."""
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
            
            self.logger.info("✅ Tenant hierarchy built using infrastructure")
            return hierarchy
            
        except Exception as e:
            self.logger.error(f"Failed to build tenant hierarchy using infrastructure: {str(e)}")
            return {}
    
    async def build_tenant_limits(self, tenant_id: str, tenant_type: str) -> Dict[str, Any]:
        """Build tenant limits information using infrastructure abstractions."""
        try:
            # Get tenant configuration
            tenant_config = await self.tenant_abstraction.get_tenant_config(tenant_id)
            
            # Build limits from infrastructure configuration
            limits = {
                "tenant_id": tenant_id,
                "tenant_type": tenant_type,
                "max_users": tenant_config.get("max_users", 1),
                "features": tenant_config.get("features", []),
                "limits": tenant_config.get("limits", {}),
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Tenant limits built using infrastructure for tenant {tenant_id}")
            return limits
            
        except Exception as e:
            self.logger.error(f"Failed to build tenant limits using infrastructure: {str(e)}")
            return {}
    
    # ============================================================================
    # CONTEXT VALIDATION (Using Infrastructure Abstractions)
    # ============================================================================
    
    def is_tenant_context_valid(self, context: TenantContext) -> bool:
        """Check if tenant context is valid using infrastructure abstractions."""
        try:
            # Basic validation - context must have tenant_id
            if not context.tenant_id:
                return False
            
            # Check if tenant is active
            if not context.is_active:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate tenant context using infrastructure: {str(e)}")
            return False
    
    def is_isolation_context_valid(self, context: IsolationContext) -> bool:
        """Check if isolation context is valid using infrastructure abstractions."""
        try:
            # Basic validation - context must have both tenants
            if not context.user_tenant or not context.resource_tenant:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate isolation context using infrastructure: {str(e)}")
            return False
    
    def is_feature_context_valid(self, context: FeatureContext) -> bool:
        """Check if feature context is valid using infrastructure abstractions."""
        try:
            # Basic validation - context must have tenant_id and feature
            if not context.tenant_id or not context.feature:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate feature context using infrastructure: {str(e)}")
            return False
    
    # ============================================================================
    # INFRASTRUCTURE INTEGRATION METHODS
    # ============================================================================
    
    async def validate_tenant_access(self, user_tenant: str, resource_tenant: str) -> bool:
        """Validate tenant access using infrastructure abstractions."""
        try:
            # Use tenant abstraction to validate tenant access
            is_valid = await self.tenant_abstraction.validate_tenant_access(user_tenant, resource_tenant)
            
            self.logger.info(f"✅ Tenant access validated using infrastructure: {user_tenant} -> {resource_tenant}")
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Failed to validate tenant access using infrastructure: {str(e)}")
            return False
    
    async def get_tenant_features(self, tenant_id: str) -> List[str]:
        """Get tenant features using infrastructure abstractions."""
        try:
            # Use tenant abstraction to get tenant features
            features = await self.tenant_abstraction.get_tenant_features(tenant_id)
            
            self.logger.info(f"✅ Tenant features retrieved using infrastructure for tenant: {tenant_id}")
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to get tenant features using infrastructure: {str(e)}")
            return []
    
    async def is_feature_enabled(self, tenant_id: str, feature: str) -> bool:
        """Check if feature is enabled using infrastructure abstractions."""
        try:
            # Use tenant abstraction to check if feature is enabled
            is_enabled = await self.tenant_abstraction.is_feature_enabled(tenant_id, feature)
            
            self.logger.info(f"✅ Feature enabled check using infrastructure for tenant {tenant_id}, feature {feature}")
            return is_enabled
            
        except Exception as e:
            self.logger.error(f"Failed to check feature enabled using infrastructure: {str(e)}")
            return False
    
    async def get_tenant_limits(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant limits using infrastructure abstractions."""
        try:
            # Use tenant abstraction to get tenant limits
            limits = await self.tenant_abstraction.get_tenant_limits(tenant_id)
            
            self.logger.info(f"✅ Tenant limits retrieved using infrastructure for tenant: {tenant_id}")
            return limits
            
        except Exception as e:
            self.logger.error(f"Failed to get tenant limits using infrastructure: {str(e)}")
            return {}
    
    # ============================================================================
    # UTILITY STATUS
    # ============================================================================
    
    def get_utility_status(self) -> Dict[str, Any]:
        """Get utility status information."""
        return {
            "utility_name": "TenantContextUtilityIntegrated",
            "status": "active",
            "infrastructure_connected": True,
            "capabilities": [
                "build_tenant_context",
                "build_tenant_isolation_context",
                "build_feature_access_context",
                "build_tenant_hierarchy",
                "build_tenant_limits",
                "validate_tenant_access",
                "get_tenant_features",
                "is_feature_enabled",
                "get_tenant_limits"
            ],
            "infrastructure_abstractions": [
                "TenantProtocol"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }



