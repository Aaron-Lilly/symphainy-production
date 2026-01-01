#!/usr/bin/env python3
"""
Platform Gateway Protocol

Clean protocol definition for Platform Infrastructure Gateway - contracts only, no implementations.
Aligned with new architecture for controlled abstraction access.

WHAT (Platform Gateway Role): I define the contract for platform infrastructure gateway
HOW (Platform Gateway Protocol): I provide controlled access to Public Works abstractions
"""

from typing import Protocol, Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class RealmCapability:
    """Capability definition for a realm."""
    abstractions: List[str]
    description: str
    byoi_support: bool


class PlatformGatewayProtocol(Protocol):
    """
    Protocol for Platform Infrastructure Gateway.
    
    Provides controlled access to Public Works Foundation abstractions
    based on realm-specific capability mappings.
    """
    
    # Realm Capability Mappings
    REALM_ABSTRACTION_MAPPINGS: Dict[str, RealmCapability]
    
    # Abstraction Access Methods
    def get_abstraction(self, abstraction_name: str, realm_name: str) -> Any:
        """Get abstraction for specific realm with validation."""
        ...
    
    def get_realm_abstractions(self, realm_name: str) -> Dict[str, Any]:
        """Get all allowed abstractions for a realm."""
        ...
    
    # Validation Methods
    def validate_realm_access(self, realm_name: str, abstraction_name: str) -> bool:
        """Validate if realm can access specific abstraction."""
        ...
    
    def get_realm_capabilities(self, realm_name: str) -> Optional[RealmCapability]:
        """Get capability definition for realm."""
        ...
    
    # BYOI Support
    def supports_byoi(self, realm_name: str) -> bool:
        """Check if realm supports Bring Your Own Infrastructure."""
        ...
    
    def register_custom_abstraction(self, realm_name: str, name: str, implementation: Any) -> bool:
        """Register custom abstraction for BYOI-enabled realm."""
        ...

