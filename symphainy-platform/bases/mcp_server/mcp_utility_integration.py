#!/usr/bin/env python3
"""
MCP Utility Integration

Handles integration with DIContainerService utilities for MCP servers.

WHAT (Micro-Module Role): I provide utility integration for MCP servers
HOW (Micro-Module Implementation): I integrate all utilities from DIContainerService
"""

from typing import Dict, Any, TYPE_CHECKING

# FIX: Use TYPE_CHECKING to avoid circular import
if TYPE_CHECKING:
    from foundations.di_container.di_container_service import DIContainerService


class MCPUtilityIntegration:
    """
    Utility integration for MCP servers.
    
    Provides access to all utilities from DIContainerService in a clean interface.
    """
    
    def __init__(self, di_container: 'DIContainerService'):
        """Initialize utility integration."""
        # FIX: Lazy import to avoid circular dependency
        from foundations.di_container.di_container_service import DIContainerService
        self.di_container = di_container
        
        # All utilities from DI container (our proven platform pattern)
        self.config = di_container.config
        self.logger = di_container.logger
        self.health = di_container.health
        self.telemetry = di_container.telemetry
        self.security = di_container.security
        self.error_handler = di_container.error_handler
        self.tenant = di_container.tenant
        self.validation = di_container.validation
        self.serialization = di_container.serialization
    
    def get_all_utilities(self) -> Dict[str, Any]:
        """Get all utilities as a dictionary."""
        return {
            "config": self.config,
            "logger": self.logger,
            "health": self.health,
            "telemetry": self.telemetry,
            "security": self.security,
            "error_handler": self.error_handler,
            "tenant": self.tenant,
            "validation": self.validation,
            "serialization": self.serialization
        }
    
    def get_utility(self, utility_name: str) -> Any:
        """Get a specific utility by name."""
        utilities = self.get_all_utilities()
        return utilities.get(utility_name)
    
    def is_utility_available(self, utility_name: str) -> bool:
        """Check if a utility is available."""
        return self.get_utility(utility_name) is not None




























