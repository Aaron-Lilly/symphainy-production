#!/usr/bin/env python3
"""
Journey Manager Factory - Factory for creating and managing journey managers

This factory enables easy addition of new journey managers for different use cases
while maintaining a consistent interface and pattern.

WHAT (Journey/Solution Role): I create and manage journey managers for different use cases
HOW (Service Implementation): I provide a factory pattern for journey manager creation and management
"""

import os
import sys
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import uuid
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from utilities import UserContext


class JourneyManagerFactory:
    """
    Journey Manager Factory - Factory for creating and managing journey managers
    
    This factory enables easy addition of new journey managers for different use cases
    while maintaining a consistent interface and pattern.
    """

    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize Journey Manager Factory."""
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Registered journey managers
        self.registered_journey_managers: Dict[str, Type] = {}
        
        # Journey manager instances
        self.journey_manager_instances: Dict[str, Any] = {}
        
        # Use case mappings
        self.use_case_mappings = {
            "mvp": "mvp_journey_manager",
            "autonomous_vehicle": "autonomous_vehicle_journey_manager",
            "insurance_ai": "insurance_ai_journey_manager",
            "default": "mvp_journey_manager"
        }
        
        print(f"🏭 Journey Manager Factory initialized")

    async def initialize(self):
        """Initialize the Journey Manager Factory."""
        try:
            print("🏭 Initializing Journey Manager Factory...")
            
            # Register default journey managers
            await self._register_default_journey_managers()
            
            # Initialize journey manager instances
            await self._initialize_journey_manager_instances()
            
            print("✅ Journey Manager Factory initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Journey Manager Factory: {e}")
            raise

    async def _register_default_journey_managers(self):
        """Register default journey managers."""
        try:
            # Register MVP Journey Manager
            from ..roles.mvp_journey_manager.mvp_journey_manager_service import MVPJourneyManagerService
            self.registered_journey_managers["mvp_journey_manager"] = MVPJourneyManagerService
            print("✅ MVP Journey Manager registered")
            
            # Register Autonomous Vehicle Journey Manager (placeholder for future)
            # from ..roles.autonomous_vehicle_journey_manager.autonomous_vehicle_journey_manager_service import AutonomousVehicleJourneyManagerService
            # self.registered_journey_managers["autonomous_vehicle_journey_manager"] = AutonomousVehicleJourneyManagerService
            print("✅ Autonomous Vehicle Journey Manager placeholder registered")
            
            # Register Insurance AI Journey Manager (placeholder for future)
            # from ..roles.insurance_ai_journey_manager.insurance_ai_journey_manager_service import InsuranceAIJourneyManagerService
            # self.registered_journey_managers["insurance_ai_journey_manager"] = InsuranceAIJourneyManagerService
            print("✅ Insurance AI Journey Manager placeholder registered")
            
        except Exception as e:
            print(f"⚠️ Some journey managers not available: {e}")

    async def _initialize_journey_manager_instances(self):
        """Initialize journey manager instances."""
        for manager_name, manager_class in self.registered_journey_managers.items():
            try:
                if manager_name == "mvp_journey_manager":
                    instance = manager_class(self.di_container, self.public_works_foundation)
                    await instance.initialize()
                    self.journey_manager_instances[manager_name] = instance
                    print(f"✅ {manager_name} instance created and initialized")
                else:
                    # Placeholder for future journey managers
                    print(f"⏳ {manager_name} placeholder ready for implementation")
                    
            except Exception as e:
                print(f"⚠️ Failed to initialize {manager_name}: {e}")

    # ============================================================================
    # JOURNEY MANAGER CREATION METHODS
    # ============================================================================

    async def create_journey_manager(self, use_case: str, user_context: UserContext):
        """
        Create a journey manager for a specific use case.
        """
        try:
            print(f"🏭 Creating journey manager for use case: {use_case}")
            
            # Get journey manager type for use case
            manager_type = self._get_journey_manager_type(use_case)
            
            # Get or create journey manager instance
            journey_manager = await self._get_journey_manager_instance(manager_type)
            
            # Create journey manager context
            journey_manager_context = await self._create_journey_manager_context(
                use_case, user_context
            )
            
            return {
                "journey_manager": journey_manager,
                "manager_type": manager_type,
                "use_case": use_case,
                "context": journey_manager_context,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Journey manager creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "use_case": use_case
            }

    def _get_journey_manager_type(self, use_case: str) -> str:
        """Get journey manager type for a specific use case."""
        return self.use_case_mappings.get(use_case, self.use_case_mappings["default"])

    async def _get_journey_manager_instance(self, manager_type: str):
        """Get or create journey manager instance."""
        if manager_type in self.journey_manager_instances:
            return self.journey_manager_instances[manager_type]
        else:
            # Create new instance if not exists
            if manager_type in self.registered_journey_managers:
                manager_class = self.registered_journey_managers[manager_type]
                instance = manager_class(self.di_container, self.public_works_foundation)
                await instance.initialize()
                self.journey_manager_instances[manager_type] = instance
                return instance
            else:
                raise ValueError(f"Unknown journey manager type: {manager_type}")

    async def _create_journey_manager_context(self, use_case: str, user_context: UserContext):
        """Create journey manager context."""
        return {
            "use_case": use_case,
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id,
            "created_at": datetime.utcnow().isoformat(),
            "manager_factory": "JourneyManagerFactory"
        }

    # ============================================================================
    # JOURNEY MANAGER REGISTRATION METHODS
    # ============================================================================

    async def register_journey_manager(self, manager_name: str, manager_class: Type, use_cases: List[str]):
        """
        Register a new journey manager.
        """
        try:
            print(f"🏭 Registering journey manager: {manager_name}")
            
            # Register the journey manager class
            self.registered_journey_managers[manager_name] = manager_class
            
            # Update use case mappings
            for use_case in use_cases:
                self.use_case_mappings[use_case] = manager_name
            
            # Create and initialize instance
            instance = manager_class(self.di_container, self.public_works_foundation)
            await instance.initialize()
            self.journey_manager_instances[manager_name] = instance
            
            print(f"✅ Journey manager {manager_name} registered successfully")
            
            return {
                "success": True,
                "manager_name": manager_name,
                "use_cases": use_cases,
                "registered_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Journey manager registration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "manager_name": manager_name
            }

    async def unregister_journey_manager(self, manager_name: str):
        """
        Unregister a journey manager.
        """
        try:
            print(f"🏭 Unregistering journey manager: {manager_name}")
            
            # Remove from registered managers
            if manager_name in self.registered_journey_managers:
                del self.registered_journey_managers[manager_name]
            
            # Remove from instances
            if manager_name in self.journey_manager_instances:
                del self.journey_manager_instances[manager_name]
            
            # Remove from use case mappings
            use_cases_to_remove = [
                use_case for use_case, manager in self.use_case_mappings.items()
                if manager == manager_name
            ]
            for use_case in use_cases_to_remove:
                del self.use_case_mappings[use_case]
                self.use_case_mappings[use_case] = "default"
            
            print(f"✅ Journey manager {manager_name} unregistered successfully")
            
            return {
                "success": True,
                "manager_name": manager_name,
                "unregistered_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Journey manager unregistration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "manager_name": manager_name
            }

    # ============================================================================
    # JOURNEY MANAGER MANAGEMENT METHODS
    # ============================================================================

    async def get_available_journey_managers(self):
        """Get list of available journey managers."""
        return {
            "registered_managers": list(self.registered_journey_managers.keys()),
            "active_instances": list(self.journey_manager_instances.keys()),
            "use_case_mappings": self.use_case_mappings,
            "total_managers": len(self.registered_journey_managers)
        }

    async def get_journey_manager_for_use_case(self, use_case: str):
        """Get journey manager for a specific use case."""
        manager_type = self._get_journey_manager_type(use_case)
        
        if manager_type in self.journey_manager_instances:
            return {
                "use_case": use_case,
                "manager_type": manager_type,
                "manager_instance": self.journey_manager_instances[manager_type],
                "available": True
            }
        else:
            return {
                "use_case": use_case,
                "manager_type": manager_type,
                "manager_instance": None,
                "available": False
            }

    async def execute_journey_operation(self, use_case: str, operation: str, operation_data: Dict[str, Any], user_context: UserContext):
        """
        Execute a journey operation using the appropriate journey manager.
        """
        try:
            print(f"🏭 Executing journey operation: {operation} for use case: {use_case}")
            
            # Get journey manager for use case
            journey_manager_info = await self.get_journey_manager_for_use_case(use_case)
            
            if not journey_manager_info["available"]:
                return {
                    "success": False,
                    "error": f"Journey manager not available for use case: {use_case}"
                }
            
            journey_manager = journey_manager_info["manager_instance"]
            
            # Execute operation based on type
            if operation == "analyze_business_outcome_and_route":
                result = await journey_manager.analyze_business_outcome_and_route(
                    operation_data.get("business_outcome"), user_context
                )
            elif operation == "process_user_response":
                result = await journey_manager.process_user_response(
                    operation_data.get("business_outcome"),
                    operation_data.get("user_response"),
                    user_context
                )
            elif operation == "get_routing_questions":
                result = await journey_manager.get_routing_questions(
                    operation_data.get("business_outcome")
                )
            elif operation == "get_routing_recommendations":
                result = await journey_manager.get_routing_recommendations(
                    operation_data.get("business_outcome")
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
            return {
                "success": True,
                "operation": operation,
                "use_case": use_case,
                "result": result,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Journey operation execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": operation,
                "use_case": use_case
            }

    # ============================================================================
    # HEALTH AND CAPABILITIES
    # ============================================================================

    async def health_check(self):
        """Get health status of the Journey Manager Factory."""
        try:
            health_status = {
                "service_name": "JourneyManagerFactory",
                "status": "healthy",
                "registered_managers_count": len(self.registered_journey_managers),
                "active_instances_count": len(self.journey_manager_instances),
                "use_case_mappings_count": len(self.use_case_mappings),
                "registered_managers": list(self.registered_journey_managers.keys()),
                "active_instances": list(self.journey_manager_instances.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service_name": "JourneyManagerFactory",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_capabilities(self):
        """Get capabilities of the Journey Manager Factory."""
        return {
            "service_name": "JourneyManagerFactory",
            "capabilities": [
                "journey_manager_creation",
                "journey_manager_registration",
                "journey_manager_management",
                "use_case_routing",
                "operation_execution",
                "dynamic_journey_manager_addition"
            ],
            "registered_managers": list(self.registered_journey_managers.keys()),
            "use_case_mappings": self.use_case_mappings,
            "factory_pattern_enabled": True
        }


# Create service instance factory function
def create_journey_manager_factory(di_container: DIContainerService,
                                   public_works_foundation: PublicWorksFoundationService) -> JourneyManagerFactory:
    """Factory function to create JourneyManagerFactory with proper DI."""
    return JourneyManagerFactory(
        di_container=di_container,
        public_works_foundation=public_works_foundation
    )


# Create default service instance (will be properly initialized by foundation services)
journey_manager_factory = None  # Will be set by foundation services during initialization
