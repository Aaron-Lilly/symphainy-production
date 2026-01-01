#!/usr/bin/env python3
"""
Foundation Service Base Class

Simplified base class for foundation services that composes focused mixins.
Implements FoundationServiceProtocol with clean, composable architecture.

WHAT (Foundation Role): I provide the foundation for all foundation services
HOW (Foundation Service): I compose utility access, infrastructure access, and performance monitoring
"""

from typing import Dict, Any, Optional
from datetime import datetime
from abc import ABC

from bases.protocols.foundation_service_protocol import FoundationServiceProtocol
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.infrastructure_access_mixin import InfrastructureAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin
from bases.startup_policy import StartupPolicy


class FoundationServiceBase(FoundationServiceProtocol, UtilityAccessMixin, InfrastructureAccessMixin, PerformanceMonitoringMixin, ABC):
    """
    Foundation Service Base Class - Simplified Foundation for ALL Foundation Services
    
    Composes focused mixins to provide comprehensive platform capabilities with
    zero-trust security, multi-tenancy, and enhanced utilities.
    """
    
    # Startup policy: Foundations are EAGER by default (always start at boot)
    startup_policy: StartupPolicy = StartupPolicy.EAGER
    
    def __init__(self, service_name: str, di_container: Any,
                 security_provider=None, authorization_guard=None):
        """Initialize Foundation Service Base with composed mixins."""
        # Core service properties
        self.service_name = service_name
        self.di_container = di_container
        self.start_time = datetime.utcnow()
        self.is_initialized = False
        self.service_health = "unknown"
        
        # Initialize mixins
        self._init_utility_access(di_container)
        self._init_infrastructure_access(di_container)
        self._init_performance_monitoring(di_container)
        
        # Security infrastructure (foundation requirement)
        self.security_provider = security_provider
        self.authorization_guard = authorization_guard
        self.current_security_context = None
        
        # Logger is already set by UtilityAccessMixin
        self.logger.info(f"🏗️ FoundationServiceBase '{service_name}' initialized")
    
    async def initialize(self) -> bool:
        """Initialize the foundation service."""
        try:
            self.logger.info(f"🚀 Initializing {self.service_name}...")
            
            # Foundation-specific initialization
            self.service_health = "healthy"
            self.is_initialized = True
            
            self.logger.info(f"✅ {self.service_name} Foundation Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            self.service_health = "unhealthy"
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the foundation service gracefully."""
        try:
            self.logger.info(f"🛑 Shutting down {self.service_name}...")
            
            # Foundation-specific shutdown
            self.is_initialized = False
            self.service_health = "shutdown"
            
            self.logger.info(f"✅ {self.service_name} Foundation Service shutdown successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown {self.service_name}: {e}")
            return False
    
    def get_security_context(self) -> Optional[Dict[str, Any]]:
        """Get current security context."""
        return self.current_security_context
    
    def validate_access(self, resource: str, action: str) -> bool:
        """Validate access to resource for action."""
        if not self.current_security_context:
            return False
        
        if self.authorization_guard:
            return self.authorization_guard.check_permission(
                self.current_security_context, resource, action
            )
        return False
    
    # ============================================================================
    # INFRASTRUCTURE ACCESS - Explicit delegation to mixin
    # ============================================================================
    # Override to ensure mixin's implementation is used (not protocol's)
    # The Protocol defines get_infrastructure_abstraction with ..., but the mixin has the real implementation
    # CRITICAL: Protocol comes before Mixin in MRO, so we must explicitly call the mixin
    def get_infrastructure_abstraction(self, name: str) -> Any:
        """Get infrastructure abstraction - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return InfrastructureAccessMixin.get_infrastructure_abstraction(self, name)
    
    def get_auth_abstraction(self) -> Any:
        """Get authentication abstraction - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return InfrastructureAccessMixin.get_auth_abstraction(self)
    
    # ============================================================================
    # UTILITY ACCESS - Explicit delegation to mixin
    # ============================================================================
    # Override to ensure mixin's implementation is used (not protocol's)
    # The Protocol defines get_utility with ..., but the mixin has the real implementation
    # CRITICAL: Protocol comes before Mixin in MRO, so we must explicitly call the mixin
    def get_utility(self, name: str) -> Any:
        """Get utility service - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return UtilityAccessMixin.get_utility(self, name)
    
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        config = self.get_config()
        return config.get(key, default)
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """Get service metadata and information."""
        return {
            "service_name": self.service_name,
            "service_type": "foundation",
            "is_initialized": self.is_initialized,
            "service_health": self.service_health,
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }