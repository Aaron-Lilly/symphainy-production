#!/usr/bin/env python3
"""
City Manager Service - Realm Orchestration Module

Micro-module for Smart City realm startup orchestration.
"""

import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime


class RealmOrchestration:
    """Realm orchestration module for City Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def orchestrate_realm_startup(self, services: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Orchestrate Smart City realm startup.
        
        Starts all Smart City services in the proper order:
        Security Guard → Traffic Cop → Nurse → Librarian → Data Steward → Content Steward → Post Office → Conductor
        """
        try:
            # Use module's own logger (self.logger) instead of service's logger
            if self.logger:
                self.logger.info("🏛️ Orchestrating Smart City realm startup...")
            
            startup_results = {
                "startup_id": str(uuid.uuid4()),
                "started_at": datetime.utcnow().isoformat(),
                "services": {},
                "success": False
            }
            
            # Startup order (dependencies considered)
            # Note: Content Steward consolidated into Data Steward
            startup_order = [
                "security_guard",  # First: Security infrastructure
                "traffic_cop",     # Second: Traffic management
                "nurse",           # Third: Health monitoring
                "librarian",       # Fourth: Knowledge management
                "data_steward",    # Fifth: Data management (includes Content Steward capabilities)
                "post_office",     # Sixth: Communication
                "conductor"        # Seventh: Workflow orchestration
            ]
            
            # Determine which services to start
            # If services list provided, use it; otherwise start all services in startup_order
            if services:
                services_to_start = services
            else:
                services_to_start = startup_order
            
            # Start services in order
            for service_name in startup_order:
                if service_name in services_to_start:
                    if self.logger:
                        self.logger.info(f"Starting {service_name}...")
                    service_result = await self._start_smart_city_service(service_name)
                    startup_results["services"][service_name] = service_result
                    
                    if not service_result.get("success"):
                        if self.logger:
                            self.logger.warning(f"Failed to start {service_name}: {service_result.get('error')}")
            
            # Check if all services started successfully
            all_successful = all(
                result.get("success", False) 
                for result in startup_results["services"].values()
            )
            
            startup_results["success"] = all_successful
            startup_results["completed_at"] = datetime.utcnow().isoformat()
            self.service.realm_startup_complete = all_successful
            
            if all_successful:
                if self.logger:
                    self.logger.info("✅ Smart City realm startup completed successfully")
            else:
                if self.logger:
                    self.logger.warning("⚠️ Some Smart City services failed to start")
            
            return startup_results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to orchestrate realm startup: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "startup_id": str(uuid.uuid4()),
                "started_at": datetime.utcnow().isoformat()
            }
    
    async def _start_smart_city_service(self, service_name: str) -> Dict[str, Any]:
        """
        Start a specific Smart City service (lazy initialization).
        
        Creates and initializes the service if it doesn't exist.
        """
        try:
            # Check if service is already initialized
            if service_name in self.service.smart_city_services:
                service_info = self.service.smart_city_services[service_name]
                if service_info.get("status") == "active" and service_info.get("instance"):
                    if self.logger:
                        self.logger.debug(f"✅ {service_name} already initialized")
                    return {
                        "success": True,
                        "service_name": service_name,
                        "status": "active",
                        "note": "Service already initialized"
                    }
            
            # Service not initialized - create and initialize it
            if self.logger:
                self.logger.info(f"🔄 Lazy initializing Smart City service: {service_name}")
            
            # Map service_name to service class
            service_classes = {
                "traffic_cop": ("backend.smart_city.services.traffic_cop.traffic_cop_service", "TrafficCopService"),
                "security_guard": ("backend.smart_city.services.security_guard.security_guard_service", "SecurityGuardService"),
                "nurse": ("backend.smart_city.services.nurse.nurse_service", "NurseService"),
                "librarian": ("backend.smart_city.services.librarian.librarian_service", "LibrarianService"),
                "data_steward": ("backend.smart_city.services.data_steward.data_steward_service", "DataStewardService"),
                # Note: Content Steward consolidated into Data Steward - removed from registry
                "post_office": ("backend.smart_city.services.post_office.post_office_service", "PostOfficeService"),
                "conductor": ("backend.smart_city.services.conductor.conductor_service", "ConductorService"),
            }
            
            if service_name not in service_classes:
                error_msg = f"Unknown Smart City service: {service_name}"
                if self.logger:
                    self.logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "service_name": service_name,
                    "error": error_msg
                }
            
            # Import and create service instance
            module_path, class_name = service_classes[service_name]
            try:
                module = __import__(module_path, fromlist=[class_name])
                service_class = getattr(module, class_name)
                
                # Create service instance (Smart City services take di_container)
                service_instance = service_class(di_container=self.service.di_container)
                
                # Register service for initialization (City Manager controls lifecycle)
                await self.service.service_management_module.register_service_for_initialization(service_name)
                
                # Initialize service
                try:
                    init_success = await service_instance.initialize()
                    if not init_success:
                        # Try to get more detailed error from service
                        error_details = getattr(service_instance, 'service_health', 'unknown')
                        error_msg = f"{service_name} initialization returned False (health: {error_details})"
                        if self.logger:
                            self.logger.error(f"❌ {error_msg}")
                        # Check if there's a last_error attribute
                        if hasattr(service_instance, 'last_error'):
                            if self.logger:
                                self.logger.error(f"   Last error: {service_instance.last_error}")
                        return {
                            "success": False,
                            "service_name": service_name,
                            "error": error_msg
                        }
                    
                    # Mark service as initialized (City Manager lifecycle ownership)
                    await self.service.service_management_module.mark_service_initialized(service_name)
                    
                except Exception as init_error:
                    error_msg = f"{service_name} initialization raised exception: {init_error}"
                    if self.logger:
                        self.logger.error(f"❌ {error_msg}")
                        import traceback
                        self.logger.error(f"Traceback: {traceback.format_exc()}")
                    return {
                        "success": False,
                        "service_name": service_name,
                        "error": error_msg
                    }
                
                # Register service in City Manager's registry
                self.service.smart_city_services[service_name] = {
                    "status": "active",
                    "instance": service_instance,
                    "started_at": datetime.utcnow().isoformat()
                }
                
                # Note: Smart City services now register themselves using Phase 2 pattern
                # via their own register_capabilities() methods in their soa_mcp modules.
                # City Manager no longer needs to register them here - they self-register during initialization.
                # This ensures services register their own capabilities with proper contracts.
                if self.logger:
                    self.logger.info(f"   📝 {service_name} will self-register with Curator (Phase 2 pattern)")
                
                if self.logger:
                    self.logger.info(f"✅ {service_name} initialized and registered")
                
                return {
                    "success": True,
                    "service_name": service_name,
                    "status": "active"
                }
                
            except ImportError as e:
                error_msg = f"Failed to import {service_name} service: {e}"
                if self.logger:
                    self.logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "service_name": service_name,
                    "error": error_msg
                }
            except Exception as e:
                error_msg = f"Failed to initialize {service_name}: {e}"
                if self.logger:
                    self.logger.error(f"❌ {error_msg}")
                import traceback
                if self.logger:
                    self.logger.error(f"Traceback: {traceback.format_exc()}")
                return {
                    "success": False,
                    "service_name": service_name,
                    "error": error_msg
                }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to start {service_name}: {str(e)}")
            import traceback
            if self.logger:
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "service_name": service_name,
                "error": str(e)
            }






