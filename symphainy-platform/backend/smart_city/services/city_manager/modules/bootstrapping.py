#!/usr/bin/env python3
"""
City Manager Service - Bootstrapping Module

Micro-module for manager hierarchy bootstrapping using top-down solution instantiation pattern.
"""

import uuid
from typing import Any, Dict, Optional
from datetime import datetime


class Bootstrapping:
    """Bootstrapping module for City Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def bootstrap_manager_hierarchy(self, solution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Bootstrap manager hierarchy starting from Solution Manager.
        
        This implements the top-down solution instantiation pattern:
        City Manager → Solution Manager → Journey Manager → Delivery Manager
        
        Note: Experience is now a Foundation (not a Manager), so Journey Manager directly calls Delivery Manager.
        """
        try:
            if self.service.logger:
                self.service.logger.info("🚀 Bootstrapping manager hierarchy...")
            
            bootstrap_results = {
                "bootstrap_id": str(uuid.uuid4()),
                "started_at": datetime.utcnow().isoformat(),
                "managers": {},
                "success": False
            }
            
            # Step 1: Bootstrap Solution Manager
            if self.service.logger:
                self.service.logger.info("Step 1: Bootstrapping Solution Manager...")
            solution_result = await self._bootstrap_solution_manager(solution_context)
            bootstrap_results["managers"]["solution_manager"] = solution_result
            if not solution_result.get("success"):
                bootstrap_results["error"] = "Failed to bootstrap Solution Manager"
                return bootstrap_results
            
            # Step 2: Bootstrap Journey Manager (called by Solution Manager)
            if self.service.logger:
                self.service.logger.info("Step 2: Solution Manager bootstrapping Journey Manager...")
            journey_result = await self._bootstrap_journey_manager(solution_context)
            bootstrap_results["managers"]["journey_manager"] = journey_result
            if not journey_result.get("success"):
                bootstrap_results["error"] = "Failed to bootstrap Journey Manager"
                return bootstrap_results
            
            # Step 3: Bootstrap Delivery Manager (called by Journey Manager)
            # Note: Experience is now a Foundation SDK, not a Manager
            # Journey Manager composes experience "head" using Experience Foundation SDK
            if self.service.logger:
                self.service.logger.info("Step 3: Journey Manager bootstrapping Delivery Manager...")
            delivery_result = await self._bootstrap_delivery_manager(solution_context)
            bootstrap_results["managers"]["delivery_manager"] = delivery_result
            if not delivery_result.get("success"):
                bootstrap_results["error"] = "Failed to bootstrap Delivery Manager"
                return bootstrap_results
            
            # Bootstrap complete
            bootstrap_results["success"] = True
            bootstrap_results["completed_at"] = datetime.utcnow().isoformat()
            self.service.bootstrapping_complete = True
            
            # FIX 4: Bootstrap data paths after manager hierarchy
            if self.service.logger:
                self.service.logger.info("Step 4: Bootstrapping data paths...")
            data_path_result = await self.service.data_path_bootstrap_module.bootstrap_data_paths()
            bootstrap_results["data_paths"] = data_path_result
            
            if self.service.logger:
                self.service.logger.info("✅ Manager hierarchy bootstrapped successfully")
            return bootstrap_results
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to bootstrap manager hierarchy: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "bootstrap_id": str(uuid.uuid4()),
                "started_at": datetime.utcnow().isoformat()
            }
    
    async def _bootstrap_solution_manager(self, solution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Bootstrap Solution Manager."""
        try:
            # Check if Solution Manager already exists in DI Container
            solution_manager = self.service.di_container.get_foundation_service("SolutionManagerService")
            
            if not solution_manager:
                # Create Solution Manager instance (needs di_container and platform_gateway)
                from backend.solution.services.solution_manager.solution_manager_service import SolutionManagerService
                # Get Platform Gateway from DI Container
                platform_gateway = self.service.di_container.get_foundation_service("PlatformInfrastructureGateway")
                solution_manager = SolutionManagerService(
                    di_container=self.service.di_container,
                    platform_gateway=platform_gateway
                )
                
                # Register in DI Container service_registry (simple key-value storage)
                # Note: get_foundation_service() reads from service_registry, so we store directly
                self.service.di_container.service_registry["SolutionManagerService"] = solution_manager
            
            # Register Solution Manager for initialization (City Manager controls lifecycle)
            await self.service.service_management_module.register_service_for_initialization("SolutionManagerService")
            
            # Initialize Solution Manager
            # Check if already initialized (attribute may not exist, so check safely)
            if not hasattr(solution_manager, 'is_initialized') or not solution_manager.is_initialized:
                try:
                    success = await solution_manager.initialize()
                    if not success:
                        # If initialize() returned False, there was an error but it was caught
                        # Check if there's a more detailed error message
                        if hasattr(solution_manager, 'last_error'):
                            error_msg = solution_manager.last_error
                        else:
                            error_msg = "Solution Manager initialization returned False"
                        if self.service.logger:
                            self.service.logger.error(f"Solution Manager initialization failed: {error_msg}")
                        raise Exception(error_msg)
                except Exception as init_error:
                    if self.service.logger:
                        self.service.logger.error(f"Solution Manager initialization raised exception: {str(init_error)}")
                    raise
            else:
                success = True
            
            self.service.manager_hierarchy["solution_manager"] = {
                "status": "initialized" if success else "failed",
                "instance": solution_manager,
                "initialized_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": success,
                "manager_name": "solution_manager",
                "status": "initialized" if success else "failed"
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            # Log error to both logger and print for debugging
            error_msg = f"Failed to bootstrap Solution Manager: {str(e)}"
            if self.service.logger:
                self.service.logger.error(error_msg)
                self.service.logger.error(f"Traceback: {error_details}")
            # Also print for immediate visibility
            print(f"❌ {error_msg}")
            print(f"Traceback: {error_details}")
            return {
                "success": False,
                "manager_name": "solution_manager",
                "error": str(e),
                "traceback": error_details
            }
    
    async def _bootstrap_journey_manager(self, solution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Bootstrap Journey Manager (called by Solution Manager)."""
        try:
            # Check if Journey Manager already exists
            journey_manager = self.service.di_container.get_foundation_service("JourneyManagerService")
            
            if not journey_manager:
                # Create Journey Manager instance (needs di_container and platform_gateway)
                from backend.journey.services.journey_manager.journey_manager_service import JourneyManagerService
                # Get Platform Gateway from DI Container
                platform_gateway = self.service.di_container.get_foundation_service("PlatformInfrastructureGateway")
                journey_manager = JourneyManagerService(
                    di_container=self.service.di_container,
                    platform_gateway=platform_gateway
                )
                
                # Register in DI Container service_registry
                self.service.di_container.service_registry["JourneyManagerService"] = journey_manager
            
            # Register Journey Manager for initialization (City Manager controls lifecycle)
            await self.service.service_management_module.register_service_for_initialization("JourneyManagerService")
            
            # Initialize Journey Manager
            if not hasattr(journey_manager, 'is_initialized') or not journey_manager.is_initialized:
                try:
                    if self.service.logger:
                        self.service.logger.info("🔧 Calling Journey Manager.initialize()...")
                    success = await journey_manager.initialize()
                    if self.service.logger:
                        self.service.logger.info(f"🔧 Journey Manager.initialize() returned: {success}")
                    if not success:
                        # If initialize() returned False, there was an error but it was caught
                        # Check if there's a more detailed error message
                        if hasattr(journey_manager, 'last_error'):
                            error_msg = journey_manager.last_error
                        else:
                            error_msg = "Journey Manager initialization returned False"
                        if self.service.logger:
                            self.service.logger.error(f"Journey Manager initialization failed: {error_msg}")
                        raise Exception(error_msg)
                except Exception as init_error:
                    import traceback
                    error_details = traceback.format_exc()
                    if self.service.logger:
                        self.service.logger.error(f"Journey Manager initialization raised exception: {str(init_error)}")
                        self.service.logger.error(f"Traceback: {error_details}")
                    # Also print for immediate visibility
                    print(f"❌ Journey Manager initialization failed: {str(init_error)}")
                    print(f"Traceback: {error_details}")
                    raise
            else:
                success = True
            
            self.service.manager_hierarchy["journey_manager"] = {
                "status": "initialized" if success else "failed",
                "instance": journey_manager,
                "initialized_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": success,
                "manager_name": "journey_manager",
                "status": "initialized" if success else "failed"
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            if self.service.logger:
                self.service.logger.error(f"Failed to bootstrap Journey Manager: {str(e)}")
                self.service.logger.error(f"Traceback: {error_details}")
            # Also print for immediate visibility
            print(f"❌ Failed to bootstrap Journey Manager: {str(e)}")
            print(f"Traceback: {error_details}")
            return {
                "success": False,
                "manager_name": "journey_manager",
                "error": str(e),
                "traceback": error_details
            }
    
    async def _bootstrap_delivery_manager(self, solution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Bootstrap Delivery Manager (called by Journey Manager)."""
        try:
            # Check if Delivery Manager already exists
            delivery_manager = self.service.di_container.get_foundation_service("DeliveryManagerService")
            
            if not delivery_manager:
                # Create Delivery Manager instance (needs di_container and platform_gateway)
                from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
                # Get Platform Gateway from DI Container
                platform_gateway = self.service.di_container.get_foundation_service("PlatformInfrastructureGateway")
                delivery_manager = DeliveryManagerService(
                    di_container=self.service.di_container,
                    platform_gateway=platform_gateway
                )
                
                # Register in DI Container service_registry
                self.service.di_container.service_registry["DeliveryManagerService"] = delivery_manager
            
            # Register Delivery Manager for initialization (City Manager controls lifecycle)
            await self.service.service_management_module.register_service_for_initialization("DeliveryManagerService")
            
            # Initialize Delivery Manager
            if not hasattr(delivery_manager, 'is_initialized') or not delivery_manager.is_initialized:
                success = await delivery_manager.initialize()
            else:
                success = True
            
            self.service.manager_hierarchy["delivery_manager"] = {
                "status": "initialized" if success else "failed",
                "instance": delivery_manager,
                "initialized_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": success,
                "manager_name": "delivery_manager",
                "status": "initialized" if success else "failed"
            }
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"Failed to bootstrap Delivery Manager: {str(e)}")
            return {
                "success": False,
                "manager_name": "delivery_manager",
                "error": str(e)
            }




