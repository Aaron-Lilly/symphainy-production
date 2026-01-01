#!/usr/bin/env python3
"""
Policy Engine Interface - Clean Policy Abstraction

Generic policy engine interface with no technology dependencies.
This is the refactored security capability with clean separation of concerns.

WHAT (Engine Role): I define policy engine contracts
HOW (Engine Implementation): I use protocols with no technology dependencies
"""

import logging
from typing import Protocol, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

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

@dataclass(frozen=True)
class PolicyResult:
    """Policy result data structure - no technology dependencies."""
    allowed: bool
    reason: str
    policy_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class PolicyEngine(Protocol):
    """Generic policy engine protocol - no technology dependencies."""
    
    async def is_allowed(self, action: str, resource: str, context: 'PolicyContext') -> PolicyResult: ...
    async def get_user_permissions(self, user_id: str) -> List[str]: ...
    async def get_tenant_policies(self, tenant_id: str) -> Dict[str, Any]: ...
    async def update_policy(self, policy_id: str, policy_data: Dict[str, Any]) -> bool: ...
    async def delete_policy(self, policy_id: str) -> bool: ...
    async def get_policy_engine_info(self) -> Dict[str, Any]: ...



