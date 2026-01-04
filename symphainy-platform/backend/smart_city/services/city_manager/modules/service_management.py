#!/usr/bin/env python3
"""
City Manager Service - Service Management Module

Micro-module for Smart City service management (start, stop, health check, restart).
"""

from typing import Any, Dict, Optional
from datetime import datetime


class ServiceManagement:
    """Service management module for City Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
        
        # Lifecycle Registry (City Manager owns service lifecycle)
        # service_name -> lifecycle_state
        # States: "pending", "pending_initialization", "initializing", "initialized", "shutdown", "error"
        self.lifecycle_registry: Dict[str, str] = {}
    
    async def manage_smart_city_service(self, service_name: str, action: str) -> Dict[str, Any]:
        """Manage a Smart City service (start, stop, health check, restart)."""
        try:
            if action == "start":
                # Access realm_orchestration_module's private method via public method
                realm_module = self.service.realm_orchestration_module
                return await realm_module._start_smart_city_service(service_name)
            elif action == "stop":
                return await self._stop_smart_city_service(service_name)
            elif action == "health_check":
                return await self._get_service_health(service_name)
            elif action == "restart":
                await self._stop_smart_city_service(service_name)
                realm_module = self.service.realm_orchestration_module
                return await realm_module._start_smart_city_service(service_name)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"Failed to manage {service_name}: {str(e)}")
            return {
                "success": False,
                "service_name": service_name,
                "action": action,
                "error": str(e)
            }
    
    async def _stop_smart_city_service(self, service_name: str) -> Dict[str, Any]:
        """Stop a specific Smart City service."""
        try:
            if service_name in self.service.smart_city_services:
                service_info = self.service.smart_city_services[service_name]
                service_instance = service_info.get("instance")
                
                # Stop service if it has shutdown method
                if service_instance and hasattr(service_instance, "shutdown"):
                    success = await service_instance.shutdown()
                else:
                    success = True  # Simulate success
                
                # Update service registry
                self.service.smart_city_services[service_name] = {
                    "status": "stopped",
                    "instance": service_instance,
                    "stopped_at": datetime.utcnow().isoformat()
                }
                
                return {
                    "success": success,
                    "service_name": service_name,
                    "status": "stopped"
                }
            else:
                return {
                    "success": False,
                    "service_name": service_name,
                    "error": "Service not found in registry"
                }
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"Failed to stop {service_name}: {str(e)}")
            return {
                "success": False,
                "service_name": service_name,
                "error": str(e)
            }
    
    async def _get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status for a specific Smart City service."""
        try:
            if service_name in self.service.smart_city_services:
                service_info = self.service.smart_city_services[service_name]
                service_instance = service_info.get("instance")
                
                # Get health from service if it has health_check method
                if service_instance and hasattr(service_instance, "health_check"):
                    health_result = await service_instance.health_check()
                else:
                    # Use health abstraction to check service
                    if self.service.health_abstraction:
                        health_context = {
                            "service_id": service_name,
                            "metadata": {"service_type": "smart_city"}
                        }
                        health_result = await self.service.health_abstraction.check_health(
                            health_type="system",
                            context=health_context
                        )
                    else:
                        health_result = {
                            "status": service_info.get("status", "unknown"),
                            "healthy": service_info.get("status") == "started"
                        }
                
                return {
                    "success": True,
                    "service_name": service_name,
                    "health": health_result,
                    "checked_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "service_name": service_name,
                    "error": "Service not found in registry"
                }
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"Failed to get health for {service_name}: {str(e)}")
            return {
                "success": False,
                "service_name": service_name,
                "error": str(e)
            }
    
    # ============================================================================
    # LIFECYCLE OWNERSHIP ENFORCEMENT (Phase 0.8 - City Manager Lifecycle Ownership)
    # ============================================================================
    # City Manager owns service lifecycle - services cannot initialize without permission
    # ============================================================================
    
    async def register_service_for_initialization(self, service_name: str) -> bool:
        """
        Register service for initialization (City Manager controls this).
        
        This method must be called by City Manager before a service is allowed to initialize.
        Services cannot initialize themselves without being registered first.
        
        Args:
            service_name: Name of service to register (e.g., "SolutionManagerService")
        
        Returns:
            True if registered successfully, False otherwise
        """
        try:
            if service_name in self.lifecycle_registry:
                current_state = self.lifecycle_registry[service_name]
                if current_state == "initialized":
                    self.logger.warning(f"⚠️ Service '{service_name}' already initialized - cannot re-register")
                    return False
                elif current_state == "initializing":
                    self.logger.warning(f"⚠️ Service '{service_name}' is currently initializing - cannot re-register")
                    return False
            
            self.lifecycle_registry[service_name] = "pending_initialization"
            self.logger.info(f"✅ Registered service '{service_name}' for initialization (City Manager lifecycle ownership)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register service '{service_name}' for initialization: {e}")
            return False
    
    async def can_service_initialize(self, service_name: str) -> bool:
        """
        Check if service is allowed to initialize (City Manager controls this).
        
        Services must be registered for initialization before they can call initialize().
        This enforces that City Manager owns service lifecycle.
        
        Args:
            service_name: Name of service requesting initialization
        
        Returns:
            True if service is allowed to initialize, False otherwise
        """
        if service_name not in self.lifecycle_registry:
            self.logger.warning(f"⚠️ Service '{service_name}' not registered for initialization - City Manager controls lifecycle")
            return False
        
        state = self.lifecycle_registry[service_name]
        if state == "pending_initialization":
            # Mark as initializing to prevent concurrent initialization
            self.lifecycle_registry[service_name] = "initializing"
            return True
        elif state == "initialized":
            self.logger.warning(f"⚠️ Service '{service_name}' already initialized")
            return False
        elif state == "initializing":
            self.logger.warning(f"⚠️ Service '{service_name}' is currently initializing")
            return False
        else:
            self.logger.warning(f"⚠️ Service '{service_name}' in invalid state for initialization: {state}")
            return False
    
    async def mark_service_initialized(self, service_name: str) -> bool:
        """
        Mark service as initialized (City Manager controls this).
        
        This method should be called after a service successfully completes initialization.
        City Manager tracks service lifecycle state.
        
        Args:
            service_name: Name of service that completed initialization
        
        Returns:
            True if marked successfully, False otherwise
        """
        try:
            if service_name not in self.lifecycle_registry:
                self.logger.warning(f"⚠️ Service '{service_name}' not in lifecycle registry - cannot mark as initialized")
                return False
            
            current_state = self.lifecycle_registry[service_name]
            if current_state != "initializing":
                self.logger.warning(f"⚠️ Service '{service_name}' not in 'initializing' state (current: {current_state}) - cannot mark as initialized")
                return False
            
            self.lifecycle_registry[service_name] = "initialized"
            self.logger.info(f"✅ Marked service '{service_name}' as initialized (City Manager lifecycle ownership)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to mark service '{service_name}' as initialized: {e}")
            return False
    
    async def mark_service_error(self, service_name: str, error: str) -> bool:
        """
        Mark service as error state (City Manager controls this).
        
        This method should be called when a service fails to initialize.
        
        Args:
            service_name: Name of service that failed
            error: Error message
        
        Returns:
            True if marked successfully, False otherwise
        """
        try:
            self.lifecycle_registry[service_name] = "error"
            self.logger.error(f"❌ Marked service '{service_name}' as error: {error}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to mark service '{service_name}' as error: {e}")
            return False
    
    def get_service_lifecycle_state(self, service_name: str) -> Optional[str]:
        """
        Get current lifecycle state of a service.
        
        Args:
            service_name: Name of service
        
        Returns:
            Lifecycle state or None if not registered
        """
        return self.lifecycle_registry.get(service_name)
    
    def get_all_lifecycle_states(self) -> Dict[str, str]:
        """
        Get all service lifecycle states.
        
        Returns:
            Dict mapping service_name -> lifecycle_state
        """
        return self.lifecycle_registry.copy()
