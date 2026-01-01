#!/usr/bin/env python3
"""
Session Protocol - Abstraction Contract

Generic session interface with no technology dependencies.
This is Layer 2 of the 5-layer security architecture.

WHAT (Infrastructure Role): I define session contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class SessionContext:
    """Session context data structure - no technology dependencies."""
    session_id: str
    user_id: str
    tenant_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

class SessionProtocol(Protocol):
    """Generic session protocol - no technology dependencies."""
    
    async def create_session(self, user_id: str, tenant_id: str, session_data: Dict[str, Any] = None) -> str: ...
    async def validate_session(self, session_id: str) -> SessionContext: ...
    async def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool: ...
    async def revoke_session(self, session_id: str) -> bool: ...
    async def get_active_sessions(self, user_id: str) -> List[SessionContext]: ...
    async def cleanup_expired_sessions(self) -> int: ...



