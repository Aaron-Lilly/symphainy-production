#!/usr/bin/env python3
"""
Authorization Protocol - Abstraction Contract

Generic authorization interface with no technology dependencies.
This is Layer 2 of the 5-layer security architecture.

WHAT (Infrastructure Role): I define authorization contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class AuthorizationContext:
    """Authorization context data structure - no technology dependencies."""
    user_id: str
    tenant_id: str
    action: str
    resource: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    tenant_features: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

class AuthorizationProtocol(Protocol):
    """Generic authorization protocol - no technology dependencies."""
    
    async def enforce(self, action: str, resource: str, context: 'SecurityContext') -> bool: ...
    async def get_user_permissions(self, user_id: str) -> List[str]: ...
    async def check_tenant_access(self, user_tenant: str, resource_tenant: str) -> bool: ...
    async def validate_feature_access(self, user_id: str, feature: str) -> bool: ...
    async def get_tenant_policies(self, tenant_id: str) -> Dict[str, Any]: ...
    async def update_authorization_policy(self, role: str, permissions: List[str]) -> bool: ...



