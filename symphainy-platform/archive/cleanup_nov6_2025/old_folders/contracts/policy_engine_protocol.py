#!/usr/bin/env python3
"""
Policy Engine Protocol - Abstraction Contract

Generic policy engine interface with no technology dependencies.
This is Layer 2 of the 5-layer security architecture.

WHAT (Infrastructure Role): I define policy engine contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class PolicyContext:
    """Policy context data structure - no technology dependencies."""
    user_id: str
    tenant_id: str
    action: str
    resource: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    tenant_features: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

class PolicyEngine(Protocol):
    """Generic policy engine protocol - no technology dependencies."""
    
    async def is_allowed(self, action: str, resource: str, context: 'SecurityContext') -> bool: ...
    async def get_user_permissions(self, user_id: str) -> List[str]: ...
    async def get_tenant_policies(self, tenant_id: str) -> Dict[str, Any]: ...
    async def update_policy(self, policy_id: str, policy_data: Dict[str, Any]) -> bool: ...
    async def delete_policy(self, policy_id: str) -> bool: ...
    async def get_policy_engine_info(self) -> Dict[str, Any]: ...



