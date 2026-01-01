#!/usr/bin/env python3
"""
Smart City Role Protocol

Clean protocol definition for Smart City roles - contracts only, no implementations.
Aligned with new architecture for platform orchestration and SOA API exposure.

WHAT (Smart City Role): I define the contract for all Smart City roles
HOW (Smart City Role Protocol): I provide platform orchestration and SOA API capabilities
"""

from typing import Protocol, Dict, Any, Optional, List, runtime_checkable
from datetime import datetime


@runtime_checkable
class SmartCityRoleProtocol(Protocol):
    """
    Protocol for Smart City Roles.
    
    Smart City roles orchestrate foundational capabilities into composable SOA APIs
    and provide platform enablement for all other realms.
    """
    
    # Core Properties
    service_name: str
    role_name: str
    di_container: Any  # DIContainerService
    start_time: datetime
    is_initialized: bool
    service_health: str
    
    # Micro-module Support
    modules: Dict[str, Any]
    _micro_module_path: Optional[str]
    
    # Lifecycle Methods
    async def initialize(self) -> bool:
        """Initialize the Smart City role."""
        ...
    
    async def shutdown(self) -> bool:
        """Shutdown the Smart City role gracefully."""
        ...
    
    # Health and Monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        ...
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and metadata."""
        ...
    
    # Direct Foundation Access (Smart City privilege)
    def get_foundation_abstraction(self, name: str) -> Any:
        """Get foundation abstraction directly (Smart City privilege)."""
        ...
    
    def get_all_foundation_abstractions(self) -> Dict[str, Any]:
        """Get all foundation abstractions (Smart City privilege)."""
        ...
    
    # Micro-module Management
    def get_module(self, module_name: str) -> Any:
        """Get micro-module instance."""
        ...
    
    def load_micro_module(self, module_name: str) -> bool:
        """Load micro-module dynamically."""
        ...
    
    # SOA API Exposure
    async def expose_soa_api(self, api_name: str, endpoint: str, handler: Any) -> bool:
        """Expose SOA API for realm consumption."""
        ...
    
    async def get_soa_apis(self) -> Dict[str, Any]:
        """Get all exposed SOA APIs."""
        ...
    
    # Platform Orchestration
    async def orchestrate_foundation_capabilities(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate foundational capabilities into platform services."""
        ...
    
    async def coordinate_with_other_roles(self, role_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with other Smart City roles."""
        ...
    
    # Configuration and Metadata
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        ...
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """Get service metadata and information."""
        ...