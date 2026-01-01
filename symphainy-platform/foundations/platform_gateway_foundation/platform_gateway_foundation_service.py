#!/usr/bin/env python3
"""
Platform Gateway Foundation Service

Provides platform-wide governance and access control for realm-specific infrastructure abstractions.
Wraps PlatformInfrastructureGateway as a Foundation Service.

WHAT (Platform Gateway Foundation Role): I provide governance and access control for all realms
HOW (Platform Gateway Foundation Implementation): I enforce realm-specific abstraction access policies via PlatformInfrastructureGateway
"""

import logging
from typing import Dict, Any, Optional

from bases.foundation_service_base import FoundationServiceBase

# Import Platform Infrastructure Gateway
try:
    from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
except ImportError:
    from platform.infrastructure.platform_gateway import PlatformInfrastructureGateway


class PlatformGatewayFoundationService(FoundationServiceBase):
    """
    Platform Gateway Foundation Service
    
    Provides platform-wide governance and access control for realm-specific infrastructure abstractions.
    Wraps PlatformInfrastructureGateway as a Foundation Service following the foundation pattern.
    
    WHAT (Platform Gateway Foundation Role): I provide governance and access control for all realms
    HOW (Platform Gateway Foundation Implementation): I wrap PlatformInfrastructureGateway and provide foundation lifecycle
    
    Responsibilities:
    - Initialize PlatformInfrastructureGateway with Public Works Foundation
    - Provide platform-wide governance for realm abstraction access
    - Enforce realm-specific access policies
    - Register in DI Container for realm access
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        """Initialize Platform Gateway Foundation Service."""
        super().__init__(
            service_name="platform_gateway_foundation",
            di_container=di_container,
            security_provider=None,  # Will be set by DI container
            authorization_guard=None  # Will be set by DI container
        )
        
        # Foundation dependencies
        self.public_works_foundation = public_works_foundation
        
        # Platform Infrastructure Gateway instance (will be initialized in initialize())
        self.platform_gateway: Optional[PlatformInfrastructureGateway] = None
        
        self.logger.info("🏗️ Platform Gateway Foundation Service initialized")
    
    async def initialize(self):
        """Initialize Platform Gateway Foundation Service."""
        try:
            self.logger.info("🔧 Initializing Platform Gateway Foundation Service...")
            
            # Validate Public Works Foundation is available
            if not self.public_works_foundation:
                raise ValueError("Public Works Foundation is required for Platform Gateway Foundation")
            
            # Initialize Platform Infrastructure Gateway
            self.platform_gateway = PlatformInfrastructureGateway(self.public_works_foundation)
            await self.platform_gateway.initialize()
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            self.logger.info("✅ Platform Gateway Foundation Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Platform Gateway Foundation Service: {e}")
            self.service_health = "unhealthy"
            raise
    
    async def shutdown(self):
        """Shutdown Platform Gateway Foundation Service."""
        try:
            self.logger.info("🔧 Shutting down Platform Gateway Foundation Service...")
            
            # Platform Gateway doesn't have explicit shutdown, but we can clear references
            self.platform_gateway = None
            
            self.is_initialized = False
            self.service_health = "shutdown"
            
            self.logger.info("✅ Platform Gateway Foundation Service shut down successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Platform Gateway Foundation Service: {e}")
            return False
    
    def get_platform_gateway(self) -> Optional[PlatformInfrastructureGateway]:
        """
        Get the Platform Infrastructure Gateway instance.
        
        Returns:
            PlatformInfrastructureGateway instance or None if not initialized
        """
        return self.platform_gateway
    
    # Delegate methods to Platform Infrastructure Gateway for convenience
    def get_abstraction(self, realm_name: str, abstraction_name: str) -> Any:
        """
        Get infrastructure abstraction with realm validation.
        
        Delegates to PlatformInfrastructureGateway.get_abstraction()
        
        Args:
            realm_name: Name of the requesting realm
            abstraction_name: Name of the abstraction to access
            
        Returns:
            Infrastructure abstraction instance
        """
        if not self.platform_gateway:
            raise RuntimeError("Platform Gateway not initialized")
        return self.platform_gateway.get_abstraction(realm_name, abstraction_name)
    
    def get_realm_abstractions(self, realm_name: str) -> list:
        """
        Get all abstractions allowed for a realm.
        
        Delegates to PlatformInfrastructureGateway.get_realm_abstractions()
        
        Args:
            realm_name: Name of the realm
            
        Returns:
            List of abstraction names the realm can access
        """
        if not self.platform_gateway:
            return []
        return self.platform_gateway.get_realm_abstractions(realm_name)
    
    def validate_realm_access(self, realm_name: str, abstraction_name: str) -> bool:
        """
        Validate if realm can access specific abstraction.
        
        Delegates to PlatformInfrastructureGateway.validate_realm_access()
        
        Args:
            realm_name: Name of the realm
            abstraction_name: Name of the abstraction
            
        Returns:
            True if realm can access abstraction, False otherwise
        """
        if not self.platform_gateway:
            return False
        return self.platform_gateway.validate_realm_access(realm_name, abstraction_name)








