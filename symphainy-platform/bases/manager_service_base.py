#!/usr/bin/env python3
"""
Manager Service Base Class

Simplified base class for manager services that extends RealmServiceBase.
Implements ManagerServiceProtocol with stateful orchestration capabilities.

WHAT (Manager Service Role): I provide stateful orchestration and lifecycle coordination
HOW (Manager Service): I extend RealmServiceBase with management-specific capabilities
"""

from typing import Dict, Any, Optional
from datetime import datetime
from abc import ABC
from enum import Enum

from bases.protocols.manager_service_protocol import ManagerServiceProtocol
from bases.realm_service_base import RealmServiceBase
from bases.startup_policy import StartupPolicy


class ManagerServiceType(Enum):
    """Manager service type enumeration."""
    CITY_MANAGER = "city_manager"
    SOLUTION_MANAGER = "solution_manager"
    DELIVERY_MANAGER = "delivery_manager"
    EXPERIENCE_MANAGER = "experience_manager"
    JOURNEY_MANAGER = "journey_manager"
    AGENTIC_MANAGER = "agentic_manager"
    CONTENT_MANAGER = "content_manager"
    INSIGHTS_MANAGER = "insights_manager"
    CUSTOM = "custom"


class GovernanceLevel(Enum):
    """Governance level enumeration."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class OrchestrationScope(Enum):
    """Orchestration scope enumeration."""
    REALM_ONLY = "realm_only"
    CROSS_DIMENSIONAL = "cross_dimensional"
    PLATFORM_WIDE = "platform_wide"


class ManagerServiceBase(ManagerServiceProtocol, RealmServiceBase, ABC):
    """
    Manager Service Base Class - Stateful Orchestrators and Lifecycle Coordinators
    
    Extends RealmServiceBase with management-specific capabilities for
    stateful orchestration and lifecycle coordination.
    """
    
    # Startup policy: Managers are LAZY by default (City Manager overrides to EAGER)
    startup_policy: StartupPolicy = StartupPolicy.LAZY
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Manager Service Base with management capabilities."""
        # Initialize parent class (skip Protocol in MRO, call RealmServiceBase directly)
        # Protocols have a no-op __init__ that would prevent RealmServiceBase.__init__ from being called
        from bases.realm_service_base import RealmServiceBase
        RealmServiceBase.__init__(self, service_name, realm_name, platform_gateway, di_container)
        
        # Manager-specific properties
        self.managed_services = {}
        self.service_registry = {}
        self.lifecycle_state = "initialized"
        
        # Logger is initialized in RealmServiceBase parent class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info(f"🏗️ ManagerServiceBase '{service_name}' initialized for realm '{realm_name}'")
    
    async def register_service(self, service_name: str, service_instance: Any) -> bool:
        """Register a service under management."""
        try:
            self.managed_services[service_name] = service_instance
            self.service_registry[service_name] = {
                "instance": service_instance,
                "registered_at": datetime.utcnow().isoformat(),
                "status": "registered"
            }
            
            self.logger.info(f"Registered service: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service {service_name}: {e}")
            return False
    
    async def unregister_service(self, service_name: str) -> bool:
        """Unregister a service from management."""
        try:
            if service_name in self.managed_services:
                del self.managed_services[service_name]
                del self.service_registry[service_name]
                
                self.logger.info(f"Unregistered service: {service_name}")
                return True
            else:
                self.logger.warning(f"Service {service_name} not found in managed services")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to unregister service {service_name}: {e}")
            return False
    
    async def get_managed_services(self) -> Dict[str, Any]:
        """Get all managed services."""
        return self.service_registry.copy()
    
    async def start_managed_services(self) -> Dict[str, bool]:
        """Start all managed services."""
        results = {}
        
        for service_name, service_instance in self.managed_services.items():
            try:
                if hasattr(service_instance, 'initialize'):
                    success = await service_instance.initialize()
                    results[service_name] = success
                    self.logger.info(f"Started service {service_name}: {success}")
                else:
                    results[service_name] = False
                    self.logger.warning(f"Service {service_name} has no initialize method")
            except Exception as e:
                results[service_name] = False
                self.logger.error(f"Failed to start service {service_name}: {e}")
        
        return results
    
    async def stop_managed_services(self) -> Dict[str, bool]:
        """Stop all managed services."""
        results = {}
        
        for service_name, service_instance in self.managed_services.items():
            try:
                if hasattr(service_instance, 'shutdown'):
                    success = await service_instance.shutdown()
                    results[service_name] = success
                    self.logger.info(f"Stopped service {service_name}: {success}")
                else:
                    results[service_name] = False
                    self.logger.warning(f"Service {service_name} has no shutdown method")
            except Exception as e:
                results[service_name] = False
                self.logger.error(f"Failed to stop service {service_name}: {e}")
        
        return results
    
    async def restart_managed_services(self) -> Dict[str, bool]:
        """Restart all managed services."""
        # Stop all services first
        stop_results = await self.stop_managed_services()
        
        # Start all services
        start_results = await self.start_managed_services()
        
        # Combine results
        results = {}
        for service_name in self.managed_services.keys():
            results[service_name] = (
                stop_results.get(service_name, False) and 
                start_results.get(service_name, False)
            )
        
        return results
    
    async def get_lifecycle_state(self) -> str:
        """Get current lifecycle state."""
        return self.lifecycle_state
    
    async def set_lifecycle_state(self, state: str) -> bool:
        """Set lifecycle state."""
        try:
            self.lifecycle_state = state
            self.logger.info(f"Lifecycle state changed to: {state}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set lifecycle state to {state}: {e}")
            return False
    
    async def orchestrate_services(self, orchestration_request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate managed services for complex workflows."""
        try:
            self.logger.info(f"Orchestrating services: {orchestration_request}")
            
            # This would implement actual orchestration logic
            return {
                "status": "orchestration_started",
                "request": orchestration_request,
                "managed_services": list(self.managed_services.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Service orchestration failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def coordinate_service_interactions(self, service_a: str, service_b: str, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate interactions between managed services."""
        try:
            if service_a not in self.managed_services or service_b not in self.managed_services:
                return {"status": "error", "error": "One or both services not managed"}
            
            self.logger.info(f"Coordinating interaction between {service_a} and {service_b}")
            
            # This would implement actual coordination logic
            return {
                "status": "coordination_started",
                "service_a": service_a,
                "service_b": service_b,
                "interaction": interaction,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Service coordination failed: {e}")
            return {"status": "error", "error": str(e)}