"""
State Protocol - Infrastructure contract for state management

Defines the interface for state encryption, validation, persistence, and isolation.
This protocol enables swappable state management engines.
"""

from typing import Protocol
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class StateStatus(Enum):
    """State status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    LOCKED = "locked"
    CORRUPTED = "corrupted"


class StateType(Enum):
    """State type enumeration."""
    USER_STATE = "user_state"
    AGENT_STATE = "agent_state"
    SESSION_STATE = "session_state"
    APPLICATION_STATE = "application_state"
    SYSTEM_STATE = "system_state"
    CACHE_STATE = "cache_state"


class EncryptionLevel(Enum):
    """Encryption level enumeration."""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class StateContext:
    """Context for state operations."""
    service_id: str
    agent_id: Optional[str] = None
    tenant_id: Optional[str] = None
    environment: str = "production"
    region: str = "us-west-2"
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class State:
    """State data structure."""
    state_id: str
    state_type: StateType = StateType.APPLICATION_STATE
    status: StateStatus = StateStatus.ACTIVE
    data: Dict[str, Any] = field(default_factory=dict)
    encrypted: bool = False
    encryption_level: EncryptionLevel = EncryptionLevel.STANDARD
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    version: int = 1
    checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    tags: Optional[List[str]] = field(default_factory=list)


@dataclass(frozen=True)
class StateSnapshot:
    """State snapshot data structure."""
    snapshot_id: str
    state_id: str
    version: int
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class StateValidation:
    """State validation result."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    integrity_check: bool = True
    schema_validation: bool = True
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class StateProtocol(Protocol):
    """
    State Protocol - Infrastructure contract for state management
    
    Defines the interface for state encryption, validation, persistence, and isolation.
    This protocol enables swappable state management engines.
    """
    
    async def create_state(self, 
                         context: StateContext,
                         state_data: Dict[str, Any],
                         state_type: StateType = StateType.APPLICATION_STATE,
                         encryption_level: EncryptionLevel = EncryptionLevel.STANDARD) -> State:
        """Create a new state."""
        ...
    
    async def get_state(self, 
                      state_id: str,
                      context: StateContext) -> Optional[State]:
        """Get state by ID."""
        ...
    
    async def update_state(self, 
                          state_id: str,
                          updates: Dict[str, Any],
                          context: StateContext) -> Optional[State]:
        """Update state data."""
        ...
    
    async def delete_state(self, 
                          state_id: str,
                          context: StateContext) -> bool:
        """Delete state."""
        ...
    
    async def validate_state(self, 
                           state_id: str,
                           context: StateContext) -> StateValidation:
        """Validate state integrity and schema."""
        ...
    
    async def encrypt_state(self, 
                           state_id: str,
                           encryption_level: EncryptionLevel,
                           context: StateContext) -> bool:
        """Encrypt state data."""
        ...
    
    async def decrypt_state(self, 
                           state_id: str,
                           context: StateContext) -> Optional[State]:
        """Decrypt state data."""
        ...
    
    async def backup_state(self, 
                          state_id: str,
                          context: StateContext) -> bool:
        """Backup state data."""
        ...
    
    async def restore_state(self, 
                           state_id: str,
                           backup_id: str,
                           context: StateContext) -> Optional[State]:
        """Restore state from backup."""
        ...
    
    async def create_state_snapshot(self, 
                                   state_id: str,
                                   context: StateContext) -> StateSnapshot:
        """Create a state snapshot."""
        ...
    
    async def restore_state_snapshot(self, 
                                    state_id: str,
                                    snapshot_id: str,
                                    context: StateContext) -> Optional[State]:
        """Restore state from snapshot."""
        ...
    
    async def list_states(self, 
                        context: StateContext,
                        filters: Optional[Dict[str, Any]] = None) -> List[State]:
        """List states with optional filters."""
        ...
    
    async def search_states(self, 
                           query: Dict[str, Any],
                           context: StateContext) -> List[State]:
        """Search states by query."""
        ...
    
    async def get_state_history(self, 
                               state_id: str,
                               context: StateContext) -> List[StateSnapshot]:
        """Get state change history."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check state infrastructure health."""
        ...
