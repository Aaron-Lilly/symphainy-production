#!/usr/bin/env python3
"""
Dependency Manager Micro-Base

Focused micro-base for handling dependency management between managers.
Single responsibility: Manage startup dependencies between domain managers.

WHAT (Dependency Role): I manage dependencies between domain managers
HOW (Dependency Manager): I track dependencies, wait for readiness, and coordinate startup
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../'))

from foundations.di_container.di_container_service import DIContainerService
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService


class DependencyManager:
    """
    Dependency Manager Micro-Base
    
    Focused responsibility: Manage startup dependencies between domain managers.
    Handles dependency tracking, readiness waiting, and coordination.
    """
    
    def __init__(self, 
                 realm_name: str,
                 di_container: DIContainerService,
                 public_works_foundation: "PublicWorksFoundationService"):
        """
        Initialize Dependency Manager.
        
        Args:
            realm_name: Name of the realm this manager governs
            di_container: DI container service
            public_works_foundation: Public Works Foundation Service
        """
        self.realm_name = realm_name
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Initialize logger
        self.logger = di_container.get_logger(f"dependency_manager_{realm_name}")
        
        # Dependency tracking
        self.dependencies = []
        self.dependency_status = {}
        
        self.logger.info(f"Initialized Dependency Manager for {realm_name}")
    
    async def get_startup_dependencies(self) -> List[str]:
        """Get list of other managers this manager depends on for startup."""
        try:
            self.logger.info(f"Getting startup dependencies for {self.realm_name}...")
            
            # Define dependencies based on realm
            dependency_mapping = {
                "smart_city": [],  # Foundation realm, no dependencies
                "business_enablement": ["smart_city"],
                "experience": ["smart_city", "business_enablement"],
                "journey": ["smart_city", "business_enablement", "experience"],
                "agentic": ["smart_city"]  # Can start with smart city
            }
            
            self.dependencies = dependency_mapping.get(self.realm_name, [])
            
            self.logger.info(f"Dependencies for {self.realm_name}: {self.dependencies}")
            return self.dependencies
            
        except Exception as e:
            self.logger.error(f"Failed to get startup dependencies: {e}")
            return []
    
    async def wait_for_dependency_managers(self, dependency_managers: List[str]) -> bool:
        """Wait for dependency managers to be ready."""
        try:
            self.logger.info(f"⏳ Waiting for dependency managers: {dependency_managers}")
            
            for manager_name in dependency_managers:
                # Wait for specific manager to be healthy
                manager_ready = await self._wait_for_manager_health(manager_name)
                if not manager_ready:
                    self.logger.error(f"❌ Dependency manager {manager_name} not ready")
                    return False
                self.logger.info(f"✅ Dependency manager {manager_name} ready")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to wait for dependency managers: {e}")
            return False
    
    async def coordinate_with_other_managers(self, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate startup with other domain managers."""
        try:
            self.logger.info(f"🤝 Coordinating with other managers for {self.realm_name}...")
            
            # Get other managers to coordinate with
            other_managers = await self._get_other_managers()
            
            coordination_results = {}
            for manager_name in other_managers:
                try:
                    coordination_result = await self._coordinate_with_manager(manager_name, startup_context)
                    coordination_results[manager_name] = coordination_result
                except Exception as e:
                    coordination_results[manager_name] = {
                        "error": str(e), 
                        "status": "failed"
                    }
            
            return {
                "coordination_results": coordination_results,
                "status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to coordinate with other managers: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    async def _wait_for_manager_health(self, manager_name: str, timeout: int = 30) -> bool:
        """Wait for a specific manager to be healthy."""
        try:
            self.logger.info(f"Waiting for {manager_name} to be healthy...")
            
            # This would integrate with actual manager health checking
            # For now, simulate a health check
            import asyncio
            await asyncio.sleep(1)  # Simulate health check delay
            
            # In a real implementation, this would:
            # 1. Check manager service health endpoint
            # 2. Verify manager is registered in Consul
            # 3. Confirm manager is ready to accept requests
            
            self.logger.info(f"✅ {manager_name} is healthy")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ {manager_name} health check failed: {e}")
            return False
    
    async def _get_other_managers(self) -> List[str]:
        """Get list of other managers to coordinate with."""
        # This would integrate with service discovery to find other managers
        # For now, return a basic list
        all_managers = ["city_manager", "delivery_manager", "experience_manager", "journey_manager", "agentic_manager"]
        return [m for m in all_managers if m != f"{self.realm_name}_manager"]
    
    async def _coordinate_with_manager(self, manager_name: str, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with a specific manager."""
        try:
            self.logger.info(f"Coordinating with {manager_name}...")
            
            # This would make actual coordination requests
            # For now, simulate coordination
            import asyncio
            await asyncio.sleep(0.1)  # Simulate coordination delay
            
            return {
                "manager_name": manager_name,
                "coordination_status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to coordinate with {manager_name}: {e}")
            return {
                "manager_name": manager_name,
                "coordination_status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def register_dependency(self, dependency_manager: str) -> bool:
        """Register a dependency on another manager."""
        try:
            if dependency_manager not in self.dependencies:
                self.dependencies.append(dependency_manager)
                self.logger.info(f"Registered dependency on {dependency_manager}")
                return True
            return True  # Already registered
            
        except Exception as e:
            self.logger.error(f"Failed to register dependency on {dependency_manager}: {e}")
            return False
    
    async def check_dependency_status(self) -> Dict[str, Any]:
        """Check the status of all dependencies."""
        try:
            status_results = {}
            
            for dependency in self.dependencies:
                is_healthy = await self._wait_for_manager_health(dependency, timeout=5)
                status_results[dependency] = {
                    "healthy": is_healthy,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            all_healthy = all(result["healthy"] for result in status_results.values())
            
            return {
                "dependencies": status_results,
                "all_healthy": all_healthy,
                "total_dependencies": len(self.dependencies),
                "healthy_dependencies": len([r for r in status_results.values() if r["healthy"]]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check dependency status: {e}")
            return {
                "error": str(e),
                "all_healthy": False
            }




