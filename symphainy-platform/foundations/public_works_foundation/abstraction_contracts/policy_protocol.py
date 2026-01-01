"""
Policy Protocol - Infrastructure abstraction contracts for policy management

Defines the core contracts for policy evaluation, enforcement, and management
at the infrastructure level. This enables swappable policy engines (OPA, custom, etc.)
"""

from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PolicyDecision(Enum):
    """Policy decision outcomes"""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    UNKNOWN = "unknown"


class PolicyType(Enum):
    """Types of policies"""
    ACCESS_CONTROL = "access_control"
    RESOURCE_LIMITS = "resource_limits"
    DATA_GOVERNANCE = "data_governance"
    AGENT_BEHAVIOR = "agent_behavior"
    SECURITY = "security"
    COMPLIANCE = "compliance"


@dataclass
class PolicyContext:
    """Context for policy evaluation"""
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    agent_id: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    environment: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PolicyResult:
    """Result of policy evaluation"""
    decision: PolicyDecision
    policy_id: str
    policy_name: str
    reason: str
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class PolicyProtocol(Protocol):
    """Protocol for policy evaluation infrastructure"""
    
    async def evaluate_policy(self, 
                            policy_id: str, 
                            context: PolicyContext) -> PolicyResult:
        """Evaluate a specific policy against the given context"""
        ...
    
    async def evaluate_policies(self, 
                              policy_ids: List[str], 
                              context: PolicyContext) -> List[PolicyResult]:
        """Evaluate multiple policies against the given context"""
        ...
    
    async def evaluate_policy_set(self, 
                                policy_set: str, 
                                context: PolicyContext) -> List[PolicyResult]:
        """Evaluate all policies in a policy set against the given context"""
        ...
    
    async def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy definition by ID"""
        ...
    
    async def list_policies(self, 
                          policy_type: Optional[PolicyType] = None,
                          tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List available policies with optional filtering"""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check policy engine health and availability"""
        ...


class PolicyStorageProtocol(Protocol):
    """Protocol for policy storage infrastructure"""
    
    async def connect(self) -> bool:
        """Connect to policy storage"""
        ...
    
    async def disconnect(self) -> bool:
        """Disconnect from policy storage"""
        ...
    
    async def store_policy(self, policy_id: str, policy_definition: Dict[str, Any]) -> bool:
        """Store a policy definition"""
        ...
    
    async def retrieve_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a policy definition"""
        ...
    
    async def delete_policy(self, policy_id: str) -> bool:
        """Delete a policy definition"""
        ...
    
    async def list_policies(self, 
                          policy_type: Optional[PolicyType] = None,
                          tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List stored policies with optional filtering"""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check policy storage health"""
        ...
