#!/usr/bin/env python3
"""
Public Works Enabled Service Base Class

Extends FoundationServiceBase to provide access to Public Works Foundation abstractions.
This replaces the old ServiceBase and provides clean access to business abstractions.

WHAT (Service Role): I need to provide business logic with access to Public Works abstractions
HOW (Service Implementation): I extend FoundationServiceBase and integrate with Public Works Foundation
"""

import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from bases.foundation_service_base import FoundationServiceBase
from common.utilities import UserContext
from abc import abstractmethod


class PublicWorksEnabledServiceBase(FoundationServiceBase):
    """
    Public Works Enabled Service Base Class
    
    Extends FoundationServiceBase to provide access to Public Works Foundation abstractions.
    This replaces the old ServiceBase and provides clean access to business abstractions.
    
    WHAT (Service Role): I need to provide business logic with access to Public Works abstractions
    HOW (Service Implementation): I extend FoundationServiceBase and integrate with Public Works Foundation
    
    Features:
    - HTTP API endpoint registration
    - Service registration with Consul
    - Business logic integration
    - Access to Public Works Foundation abstractions
    - Smart City realm access (for Smart City roles)
    - 1:1 abstraction access (for other roles)
    """
    
    def __init__(self, service_name: str, service_url: str, port: int, utility_foundation=None):
        """
        Initialize Public Works Enabled Service.
        
        Args:
            service_name: Name of the service
            service_url: URL of the service
            port: Port of the service
            utility_foundation: Utility Foundation Service instance
        """
        super().__init__(service_name, utility_foundation)
        
        # Service configuration
        self.service_url = service_url
        self.port = port
        
        # Service state
        self.http_endpoints = []
        self.capabilities = []
        self.business_logic = None
        
        # Public Works Foundation integration
        self.public_works_foundation = None
        self.available_abstractions = {}
        
        self.logger.info(f"Initialized {service_name} Public Works Enabled Service")
    
    async def initialize_public_works_integration(self):
        """Initialize integration with Public Works Foundation."""
        try:
            self.logger.info("🔗 Initializing Public Works Foundation integration...")
            
            # Import and initialize Public Works Foundation
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
            # Create Public Works Foundation instance
            self.public_works_foundation = PublicWorksFoundationService(
                self.utility_foundation, 
                None,  # No infrastructure foundation needed here
                None   # No configuration foundation needed here
            )
            
            # Initialize Public Works Foundation
            await self.public_works_foundation.initialize()
            
            # Get available abstractions based on service type
            await self._load_available_abstractions()
            
            self.logger.info("✅ Public Works Foundation integration initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Public Works Foundation integration: {e}")
            await self.handle_error_with_audit(e, "initialize_public_works_integration")
            raise
    
    async def _load_available_abstractions(self):
        """Load available abstractions based on service type."""
        try:
            # Determine service type from service name
            if "smart_city" in self.service_name.lower() or any(role in self.service_name.lower() for role in [
                "traffic_cop", "security_guard", "data_steward", "librarian", 
                "post_office", "nurse", "city_manager"
            ]):
                # Smart City roles get realm access
                await self._load_smart_city_abstractions()
            else:
                # Other roles get 1:1 mapping
                await self._load_business_abstractions()
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load available abstractions: {e}")
            await self.handle_error_with_audit(e, "load_available_abstractions")
            raise
    
    async def _load_smart_city_abstractions(self):
        """Load Smart City abstractions with realm access."""
        try:
            # Extract role name from service name
            role_name = self._extract_role_name()
            
            # Get Smart City abstractions (own + realm + Conductor)
            self.available_abstractions = await self.public_works_foundation.get_smart_city_abstractions(role_name)
            
            self.logger.info(f"✅ Loaded Smart City abstractions for {role_name}: {len(self.available_abstractions)} abstractions")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load Smart City abstractions: {e}")
            await self.handle_error_with_audit(e, "load_smart_city_abstractions")
            raise
    
    async def _load_business_abstractions(self):
        """Load business abstractions with 1:1 mapping."""
        try:
            # For now, business roles get basic abstractions
            # This can be extended when we implement business pillar abstractions
            self.available_abstractions = {}
            
            self.logger.info(f"✅ Loaded business abstractions: {len(self.available_abstractions)} abstractions")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load business abstractions: {e}")
            await self.handle_error_with_audit(e, "load_business_abstractions")
            raise
    
    def _extract_role_name(self) -> str:
        """Extract role name from service name."""
        # Remove common suffixes
        role_name = self.service_name.replace("_service", "").replace("_mcp", "")
        
        # Handle special cases
        if "traffic_cop" in role_name:
            return "traffic_cop"
        elif "security_guard" in role_name:
            return "security_guard"
        elif "data_steward" in role_name:
            return "data_steward"
        elif "librarian" in role_name:
            return "librarian"
        elif "post_office" in role_name:
            return "post_office"
        elif "nurse" in role_name:
            return "nurse"
        elif "city_manager" in role_name:
            return "city_manager"
        else:
            return role_name
    
    @abstractmethod
    async def initialize_business_logic(self):
        """
        Initialize the business logic for this service.
        
        This method MUST be implemented by each service
        to set up the actual business logic implementation.
        """
        pass
    
    @abstractmethod
    def register_http_endpoints(self):
        """
        Register HTTP API endpoints for this service.
        
        This method MUST be implemented by each service
        to define its HTTP API endpoints.
        """
        pass
    
    async def initialize(self):
        """Initialize the service asynchronously."""
        try:
            # Initialize Public Works integration first
            await self.initialize_public_works_integration()
            
            # Initialize business logic
            await self.initialize_business_logic()
            
            # Register HTTP endpoints
            self.register_http_endpoints()
            
            # Mark as initialized
            self.is_initialized = True
            self.service_health = "healthy"
            
            self.logger.info(f"✅ {self.service_name} Public Works Enabled Service initialized successfully")
            
        except Exception as e:
            self.service_health = "unhealthy"
            self.logger.error(f"❌ {self.service_name} Public Works Enabled Service initialization failed: {e}")
            await self.handle_error_with_audit(e, "service_initialization")
            raise
    
    def add_http_endpoint(self, method: str, path: str, handler, description: str = None):
        """
        Add an HTTP endpoint to this service.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: URL path
            handler: Function to handle the request
            description: Description of the endpoint
        """
        endpoint = {
            "method": method.upper(),
            "path": path,
            "handler": handler,
            "description": description or f"{method} {path}",
            "full_url": f"http://{self.service_url}:{self.port}{path}"
        }
        
        self.http_endpoints.append(endpoint)
        self.logger.info(f"Added HTTP endpoint: {method} {path}")
    
    def add_capability(self, capability: str, description: str = None):
        """
        Add a capability to this service.
        
        Args:
            capability: Name of the capability
            description: Description of the capability
        """
        cap = {
            "name": capability,
            "description": description or f"Provides {capability} functionality"
        }
        
        self.capabilities.append(cap)
        self.logger.info(f"Added capability: {capability}")
    
    # ============================================================================
    # ABSTRACTION ACCESS METHODS
    
    def get_abstraction(self, abstraction_name: str) -> Optional[Any]:
        """Get a specific abstraction by name."""
        return self.available_abstractions.get(abstraction_name)
    
    def get_abstraction_methods(self, abstraction_name: str) -> List[str]:
        """Get available methods for a specific abstraction."""
        abstraction = self.get_abstraction(abstraction_name)
        if abstraction and isinstance(abstraction, dict) and "methods" in abstraction:
            return abstraction["methods"]
        return []
    
    def list_available_abstractions(self) -> Dict[str, Any]:
        """List all available abstractions."""
        return self.available_abstractions
    
    def has_abstraction(self, abstraction_name: str) -> bool:
        """Check if an abstraction is available."""
        return abstraction_name in self.available_abstractions
    
    # ============================================================================
    # ENHANCED HEALTH AND INFO METHODS
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get comprehensive service health status."""
        try:
            base_health = await super().get_service_health()
            
            # Add Public Works specific health info
            public_works_health = {
                "public_works_integration": self.public_works_foundation is not None,
                "available_abstractions": len(self.available_abstractions),
                "http_endpoints": len(self.http_endpoints),
                "capabilities": len(self.capabilities),
                "business_logic_available": self.business_logic is not None,
                "service_url": f"http://{self.service_url}:{self.port}"
            }
            
            return {**base_health, **public_works_health}
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "service": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get comprehensive service information."""
        try:
            base_info = await super().get_service_health()
            
            # Add Public Works specific info
            service_info = {
                "service_name": self.service_name,
                "service_url": f"http://{self.service_url}:{self.port}",
                "status": self.service_health,
                "start_time": self.start_time.isoformat(),
                "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
                "http_endpoints": [
                    {
                        "method": ep["method"],
                        "path": ep["path"],
                        "description": ep["description"],
                        "full_url": ep["full_url"]
                    }
                    for ep in self.http_endpoints
                ],
                "capabilities": self.capabilities,
                "available_abstractions": list(self.available_abstractions.keys()),
                "business_logic_available": self.business_logic is not None,
                "public_works_integration": self.public_works_foundation is not None
            }
            
            return service_info
            
        except Exception as e:
            self.logger.error(f"Failed to get service info: {e}")
            return {
                "service_name": self.service_name,
                "status": "error",
                "error": str(e)
            }
