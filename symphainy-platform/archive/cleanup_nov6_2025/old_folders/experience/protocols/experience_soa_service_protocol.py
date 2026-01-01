#!/usr/bin/env python3
"""
Experience SOA Service Protocol (DI-Based)

Defines the standard protocol for Experience Dimension services using pure dependency injection.

WHAT (SOA Protocol): I define the standard structure for Experience services
HOW (Protocol): I follow SOA patterns with service contracts, operations, and data models using pure DI
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

# Import Public Works Foundation for DI (following Security Guard pattern)
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService


class ExperienceServiceType(Enum):
    """Defines types of Experience services."""
    EXPERIENCE_MANAGER = "experience_manager"
    JOURNEY_MANAGER = "journey_manager"
    FRONTEND_INTEGRATION = "frontend_integration"
    
    def __str__(self):
        return self.value


class ExperienceOperationType(Enum):
    """Defines types of operations Experience services can perform."""
    SESSION_MANAGEMENT = "session_management"
    UI_STATE_MANAGEMENT = "ui_state_management"
    REAL_TIME_COORDINATION = "real_time_coordination"
    FRONTEND_ROUTING = "frontend_routing"
    JOURNEY_TRACKING = "journey_tracking"
    FLOW_MANAGEMENT = "flow_management"
    API_GATEWAY = "api_gateway"
    WEBSOCKET_MANAGEMENT = "websocket_management"
    
    def __str__(self):
        return self.value


class ExperienceServiceProtocol(ABC):
    """
    Experience Service Protocol (DI-Based)
    
    Abstract base class that defines the standard protocol for Experience services
    using pure dependency injection instead of inheritance.
    """
    
    def __init__(self, service_name: str, service_type: ExperienceServiceType, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize experience service protocol with dependency injection."""
        self.service_name = service_name
        self.service_type = service_type
        self.public_works_foundation = public_works_foundation
        self.is_initialized = False
        
        # Experience abstractions from public works
        self.experience_abstractions = {}
        
        print(f"🎨 {self.service_name} initialized with public works foundation")
        
    @abstractmethod
    async def initialize(self, user_context: Optional[Dict[str, Any]] = None):
        """Initialize the experience service."""
        pass
    
    @abstractmethod
    async def execute_operation(self, operation_type: ExperienceOperationType, 
                               operation_data: Dict[str, Any], 
                               user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific operation."""
        pass
    
    @abstractmethod
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this service."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the service."""
        pass


class ExperienceServiceBase:
    """
    Experience Service Base Class (DI-Based)
    
    Base class for Experience services using pure dependency injection.
    Provides common functionality and integration with foundation services.
    """
    
    def __init__(self, service_name: str, service_type: ExperienceServiceType, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize experience service base with dependency injection."""
        self.service_name = service_name
        self.service_type = service_type
        self.public_works_foundation = public_works_foundation
        self.is_initialized = False
        
        # Experience abstractions from public works
        self.experience_abstractions = {}
        
        # Service capabilities
        self.supported_operations = []
        self.service_contract = {}
        
        print(f"🔧 {self.service_name} initialized with DI pattern")
        
    async def initialize(self, user_context: Optional[Dict[str, Any]] = None):
        """Initialize the experience service."""
        try:
            print(f"🚀 Initializing {self.service_name}...")
            
            # Load experience abstractions from public works foundation
            if self.public_works_foundation:
                await self._load_experience_abstractions()
                print(f"✅ Loaded {len(self.experience_abstractions)} experience abstractions from public works")
            else:
                print("⚠️ Public works foundation not available - using limited abstractions")
            
            # Initialize service-specific components
            await self._initialize_service_components(user_context)
            
            self.is_initialized = True
            print(f"✅ {self.service_name} initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize {self.service_name}: {e}")
            raise
    
    async def _load_experience_abstractions(self):
        """Load experience abstractions from public works foundation."""
        try:
            # This would load experience-specific abstractions from public works
            # For now, we'll create a basic structure
            self.experience_abstractions = {
                "frontend_integration": {"available": True},
                "user_experience": {"available": True},
                "journey_management": {"available": True}
            }
        except Exception as e:
            print(f"⚠️ Failed to load experience abstractions: {e}")
            self.experience_abstractions = {}
        
    async def shutdown(self):
        """Shutdown the experience service."""
        try:
            self.logger.info(f"🛑 Shutting down {self.service_name}...")
            await self._shutdown_service_components()
            self.is_initialized = False
            self.logger.info(f"✅ {self.service_name} shutdown successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown {self.service_name}: {e}")
            raise
        
    async def _initialize_service_components(self, user_context: Optional[Dict[str, Any]] = None):
        """Initialize service-specific components."""
        # Override in subclasses
        pass
        
    async def _shutdown_service_components(self):
        """Shutdown service-specific components."""
        # Override in subclasses
        pass
        
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this service."""
        return {
            "service_name": self.service_name,
            "service_type": self.service_type.value,
            "supported_operations": [op.value for op in self.supported_operations],
            "service_contract": self.service_contract,
            "is_initialized": self.is_initialized,
            "architecture": "DI-Based",
            "foundation_services_available": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the experience service."""
        try:
            # Get foundation services health
            foundation_health = await self.foundation_services.get_container_health()
            
            return {
                "service_name": self.service_name,
                "service_type": self.service_type.value,
                "status": "healthy" if self.is_initialized else "unhealthy",
                "architecture": "DI-Based",
                "foundation_services_health": foundation_health,
                "capabilities": await self.get_service_capabilities(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "service_name": self.service_name,
                "service_type": self.service_type.value,
                "status": "error",
                "error": str(e),
                "architecture": "DI-Based",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def validate_dependencies(self) -> Dict[str, Any]:
        """Validate that all dependencies are properly injected."""
        try:
            validation_results = {
                "foundation_services": False,
                "logger": False,
                "config": False,
                "health": False,
                "telemetry": False,
                "security": False
            }
            
            # Validate foundation services
            if self.foundation_services:
                validation_results["foundation_services"] = True
            
            # Validate utilities
            if hasattr(self.logger, 'info'):
                validation_results["logger"] = True
            
            if hasattr(self.config, 'is_bootstrapped'):
                validation_results["config"] = True
            
            if hasattr(self.health, 'get_health_summary'):
                validation_results["health"] = True
            
            if hasattr(self.telemetry, 'is_bootstrapped'):
                validation_results["telemetry"] = True
            
            if hasattr(self.security, 'is_bootstrapped'):
                validation_results["security"] = True
            
            all_valid = all(validation_results.values())
            
            return {
                "all_valid": all_valid,
                "validation_results": validation_results,
                "service_name": self.service_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "all_valid": False,
                "error": str(e),
                "service_name": self.service_name,
                "timestamp": datetime.utcnow().isoformat()
            }