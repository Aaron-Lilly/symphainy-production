#!/usr/bin/env python3
"""
Tenant Protocol - Abstraction Contract

Generic tenant interface with no technology dependencies.
This is Layer 2 of the 5-layer security architecture.

WHAT (Infrastructure Role): I define tenant contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class TenantContext:
    """Tenant context data structure - no technology dependencies."""
    tenant_id: str
    tenant_name: str
    tenant_type: str
    max_users: int
    features: list[str] = field(default_factory=list)
    limits: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

class TenantProtocol(Protocol):
    """Generic tenant protocol - no technology dependencies."""
    
    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]: ...
    async def validate_tenant_access(self, user_tenant: str, resource_tenant: str) -> bool: ...
    async def get_tenant_features(self, tenant_id: str) -> List[str]: ...
    async def is_feature_enabled(self, tenant_id: str, feature: str) -> bool: ...
    async def get_tenant_limits(self, tenant_id: str) -> Dict[str, Any]: ...
    async def create_tenant_context(self, tenant_id: str, tenant_type: str, tenant_name: str) -> TenantContext: ...



