#!/usr/bin/env python3
"""
City Manager Service - Service Management Module

Micro-module for Smart City service management (start, stop, health check, restart).
"""

from typing import Any, Dict
from datetime import datetime


class ServiceManagement:
    """Service management module for City Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
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

