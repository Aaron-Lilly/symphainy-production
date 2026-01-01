#!/usr/bin/env python3
"""
Tenant Context Utility - Bootstrap Pattern

Builds and manages tenant-related contexts using bootstrap pattern to avoid circular references.
This utility gets bootstrapped by foundation service, then works independently.

WHAT (Utility Role): I build and manage tenant contexts using bootstrap pattern
HOW (Utility Implementation): I bootstrap from foundation service, then work independently
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    tenant_type: str = "individual"
    features: List[str] = field(default_factory=list)
    limits: Dict[str, Any] = field(default_factory=dict)
    isolation_level: str = "strict" # strict, shared, global
    parent_tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {k: str(v) if isinstance(v, datetime) else v for k, v in self.__dict__.items()}

@dataclass(frozen=True)
class TenantIsolationContext:
    source_tenant_id: str
    target_tenant_id: str
    is_allowed: bool
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {k: str(v) if isinstance(v, datetime) else v for k, v in self.__dict__.items()}

@dataclass(frozen=True)
class TenantFeatureContext:
    tenant_id: str
    feature_name: str
    is_enabled: bool
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {k: str(v) if isinstance(v, datetime) else v for k, v in self.__dict__.items()}

class TenantContextUtilityBootstrap:
    """
    Tenant Context Utility - Bootstrap Pattern
    
    Builds and manages tenant-related contexts using bootstrap pattern to avoid circular references.
    This utility gets bootstrapped by foundation service, then works independently.
    """
    
    def __init__(self, service_name: str = "default_service"):
        """Initialize Tenant Context Utility (not yet bootstrapped)."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"TenantContextUtilityBootstrap-{service_name}")
        
        # Bootstrap state
        self.is_bootstrapped = False
        self.bootstrap_provider = None
        
        # Infrastructure abstractions (will be set after bootstrap)
        self.tenant_abstraction = None
        
        self.logger.info(f"Tenant Context Utility Bootstrap initialized for {service_name} (not yet bootstrapped)")
    
    def bootstrap(self, bootstrap_provider, tenant_abstraction=None):
        """
        Bootstrap the tenant context utility with infrastructure capabilities.
        
        Args:
            bootstrap_provider: Foundation service that provides bootstrap implementation
            tenant_abstraction: Optional tenant abstraction for enhanced capabilities
        """
        self.bootstrap_provider = bootstrap_provider
        self.tenant_abstraction = tenant_abstraction
        self.is_bootstrapped = True
        
        self.logger.info(f"Tenant Context Utility Bootstrap bootstrapped by {bootstrap_provider.__class__.__name__}")

    async def build_tenant_context(self, tenant_id: str, tenant_config: Optional[Dict[str, Any]] = None) -> TenantContext:
        """Build a TenantContext object for a given tenant."""
        if not self.is_bootstrapped:
            raise RuntimeError("Tenant Context Utility not bootstrapped. Call bootstrap() first.")
        
        # Try infrastructure abstraction first (enhanced implementation)
        if self.tenant_abstraction:
            try:
                # Use infrastructure abstraction for tenant config
                tenant_config = await self.tenant_abstraction.get_tenant_config(tenant_id)
            except Exception as e:
                self.logger.warning(f"Infrastructure tenant config failed: {e}")
                # Fallback to basic context building
                tenant_config = None
        
        # Build context (with or without infrastructure)
        if tenant_config:
            context = TenantContext(
                tenant_id=tenant_id,
                tenant_type=tenant_config.get("type", "individual"),
                features=tenant_config.get("features", []),
                limits=tenant_config.get("limits", {}),
                isolation_level=tenant_config.get("isolation_level", "strict"),
                parent_tenant_id=tenant_config.get("parent_tenant_id")
            )
        else:
            # Mock data for demonstration
            if tenant_id.startswith("org_"):
                context = TenantContext(
                    tenant_id=tenant_id,
                    tenant_type="organization",
                    features=["basic_analytics", "team_collaboration"],
                    limits={"storage_gb": 100},
                    isolation_level="strict"
                )
            elif tenant_id.startswith("ent_"):
                context = TenantContext(
                    tenant_id=tenant_id,
                    tenant_type="enterprise",
                    features=["basic_analytics", "team_collaboration", "audit_logs"],
                    limits={"storage_gb": 1000},
                    isolation_level="strict"
                )
            else:
                context = TenantContext(
                    tenant_id=tenant_id,
                    tenant_type="individual",
                    features=["basic_analytics"],
                    limits={"storage_gb": 1},
                    isolation_level="strict"
                )
        
        self.logger.debug(f"Tenant context built for tenant: {tenant_id}")
        return context

    async def build_tenant_isolation_context(self, source_tenant_id: str, target_tenant_id: str) -> TenantIsolationContext:
        """Build a TenantIsolationContext to describe access between tenants."""
        if not self.is_bootstrapped:
            raise RuntimeError("Tenant Context Utility not bootstrapped. Call bootstrap() first.")
        
        # Try infrastructure abstraction first (enhanced implementation)
        if self.tenant_abstraction:
            try:
                # Use infrastructure abstraction for tenant access validation
                is_allowed = await self.tenant_abstraction.validate_tenant_access(source_tenant_id, target_tenant_id)
                reason = "Tenant abstraction validation" if is_allowed else "Tenant abstraction denied access"
            except Exception as e:
                self.logger.warning(f"Infrastructure tenant validation failed: {e}")
                # Fallback to basic access check
                is_allowed = source_tenant_id == target_tenant_id # Strict by default
                reason = "Strict isolation (default due to infrastructure failure)"
        else:
            # Fallback: Basic access check without infrastructure
            is_allowed = source_tenant_id == target_tenant_id # Strict by default
            reason = "Strict isolation (default due to missing abstraction)"
        
        context = TenantIsolationContext(
            source_tenant_id=source_tenant_id,
            target_tenant_id=target_tenant_id,
            is_allowed=is_allowed,
            reason=reason
        )
        self.logger.debug(f"Tenant isolation context built: {source_tenant_id} -> {target_tenant_id}")
        return context

    async def build_tenant_feature_context(self, tenant_id: str, feature_name: str) -> TenantFeatureContext:
        """Build a TenantFeatureContext to describe a tenant's access to a feature."""
        if not self.is_bootstrapped:
            raise RuntimeError("Tenant Context Utility not bootstrapped. Call bootstrap() first.")
        
        # Try infrastructure abstraction first (enhanced implementation)
        if self.tenant_abstraction:
            try:
                # Use infrastructure abstraction for feature validation
                is_enabled = await self.tenant_abstraction.is_feature_enabled(tenant_id, feature_name)
                reason = f"Feature '{feature_name}' is {'enabled' if is_enabled else 'disabled'} for tenant {tenant_id} via abstraction"
            except Exception as e:
                self.logger.warning(f"Infrastructure feature validation failed: {e}")
                # Fallback to basic feature check
                is_enabled = False # Default to disabled
                reason = f"Feature '{feature_name}' disabled (default due to infrastructure failure)"
        else:
            # Fallback: Basic feature check without infrastructure
            is_enabled = False # Default to disabled
            reason = f"Feature '{feature_name}' disabled (default due to missing abstraction)"
        
        context = TenantFeatureContext(
            tenant_id=tenant_id,
            feature_name=feature_name,
            is_enabled=is_enabled,
            reason=reason
        )
        self.logger.debug(f"Feature access context built for tenant {tenant_id}, feature {feature_name}")
        return context
    
    async def build_tenant_hierarchy_context(self) -> Dict[str, Any]:
        """
        Build a context representing the tenant hierarchy or types.
        This would typically come from a configuration or a dedicated tenant service.
        """
        if not self.is_bootstrapped:
            raise RuntimeError("Tenant Context Utility not bootstrapped. Call bootstrap() first.")
        
        hierarchy = {
            "individual": {"max_users": 1, "features": ["basic_analytics"]},
            "organization": {"max_users": 50, "features": ["team_collaboration"]},
            "enterprise": {"max_users": 1000, "features": ["audit_logs", "custom_integrations"]}
        }
        self.logger.debug("Tenant hierarchy built")
        return hierarchy

    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the utility."""
        return {
            "utility_name": "TenantContextUtilityBootstrap",
            "service_name": self.service_name,
            "status": "active" if self.is_bootstrapped else "not_bootstrapped",
            "is_bootstrapped": self.is_bootstrapped,
            "bootstrap_provider": self.bootstrap_provider.__class__.__name__ if self.bootstrap_provider else None,
            "timestamp": datetime.utcnow().isoformat()
        }



