#!/usr/bin/env python3
"""
Realm Startup Orchestrator Micro-Base

Focused micro-base for handling realm startup orchestration.
Single responsibility: Orchestrate startup of all services in a realm.

WHAT (Realm Startup Role): I orchestrate startup of all services in my realm
HOW (Realm Startup Orchestrator): I coordinate service startup, health monitoring, and shutdown
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


class RealmStartupOrchestrator:
    """
    Realm Startup Orchestrator Micro-Base
    
    Focused responsibility: Orchestrate startup of all services in a realm.
    Handles service startup, health monitoring, and graceful shutdown.
    """
    
    def __init__(self, 
                 realm_name: str,
                 di_container: DIContainerService,
                 public_works_foundation: "PublicWorksFoundationService"):
        """
        Initialize Realm Startup Orchestrator.
        
        Args:
            realm_name: Name of the realm to orchestrate
            di_container: DI container service
            public_works_foundation: Public Works Foundation Service
        """
        self.realm_name = realm_name
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Initialize logger
        self.logger = di_container.get_logger(f"realm_startup_{realm_name}")
        
        self.logger.info(f"Initialized Realm Startup Orchestrator for {realm_name}")
    
    async def orchestrate_realm_startup(self) -> Dict[str, Any]:
        """Orchestrate startup of all services in this realm."""
        try:
            self.logger.info(f"🚀 Orchestrating {self.realm_name} realm startup...")
            
            # 1. Get realm services
            realm_services = await self._get_realm_services()
            
            # 2. Start services in dependency order
            startup_results = await self._start_services_in_order(realm_services)
            
            # 3. Monitor startup health
            health_status = await self._monitor_startup_health(realm_services)
            
            # 4. Validate startup success
            startup_success = await self._validate_startup_success(startup_results, health_status)
            
            self.logger.info(f"✅ {self.realm_name} realm startup complete")
            
            return {
                "realm_name": self.realm_name,
                "startup_results": startup_results,
                "health_status": health_status,
                "startup_success": startup_success,
                "status": "started" if startup_success else "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ {self.realm_name} realm startup failed: {e}")
            return {
                "realm_name": self.realm_name,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def start_realm_services(self) -> Dict[str, Any]:
        """Start all services managed by this realm."""
        try:
            self.logger.info(f"🔧 Starting {self.realm_name} realm services...")
            
            # Get services to start
            realm_services = await self._get_realm_services()
            
            # Start services
            startup_results = await self._start_services_in_order(realm_services)
            
            # Calculate success metrics
            total_services = len(realm_services)
            successful_services = len([r for r in startup_results.values() if r.get("status") == "started"])
            failed_services = total_services - successful_services
            
            return {
                "realm_name": self.realm_name,
                "startup_results": startup_results,
                "total_services": total_services,
                "successful_services": successful_services,
                "failed_services": failed_services,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start {self.realm_name} realm services: {e}")
            return {
                "realm_name": self.realm_name,
                "error": str(e),
                "status": "failed"
            }
    
    async def monitor_realm_health(self) -> Dict[str, Any]:
        """Monitor health of all services in this realm."""
        try:
            self.logger.info(f"🏥 Monitoring {self.realm_name} realm health...")
            
            # Get realm services
            realm_services = await self._get_realm_services()
            
            # Check health of each service
            health_results = {}
            for service_name in realm_services:
                try:
                    health_status = await self._check_service_health(service_name)
                    health_results[service_name] = health_status
                except Exception as e:
                    health_results[service_name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            
            # Calculate overall health
            healthy_services = len([h for h in health_results.values() if h.get("status") == "healthy"])
            total_services = len(health_results)
            health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
            
            return {
                "realm_name": self.realm_name,
                "health_results": health_results,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "health_percentage": health_percentage,
                "overall_status": "healthy" if health_percentage >= 80 else "degraded" if health_percentage >= 50 else "unhealthy"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to monitor {self.realm_name} realm health: {e}")
            return {
                "realm_name": self.realm_name,
                "error": str(e),
                "status": "failed"
            }
    
    async def coordinate_realm_shutdown(self) -> Dict[str, Any]:
        """Coordinate shutdown of all services in this realm."""
        try:
            self.logger.info(f"🛑 Coordinating {self.realm_name} realm shutdown...")
            
            # Get realm services
            realm_services = await self._get_realm_services()
            
            # Shutdown services in reverse dependency order
            shutdown_results = await self._shutdown_services_in_order(realm_services)
            
            # Calculate shutdown metrics
            total_services = len(realm_services)
            successful_shutdowns = len([r for r in shutdown_results.values() if r.get("status") == "shutdown"])
            failed_shutdowns = total_services - successful_shutdowns
            
            return {
                "realm_name": self.realm_name,
                "shutdown_results": shutdown_results,
                "total_services": total_services,
                "successful_shutdowns": successful_shutdowns,
                "failed_shutdowns": failed_shutdowns,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown {self.realm_name} realm: {e}")
            return {
                "realm_name": self.realm_name,
                "error": str(e),
                "status": "failed"
            }
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    async def _get_realm_services(self) -> List[str]:
        """Get list of services managed by this realm."""
        # This would integrate with service discovery
        # For now, return a basic list
        return [f"{self.realm_name}_service"]
    
    async def _start_services_in_order(self, services: List[str]) -> Dict[str, Dict[str, Any]]:
        """Start services in dependency order."""
        results = {}
        
        for service_name in services:
            try:
                self.logger.info(f"  Starting {service_name}...")
                # This would start the actual service
                results[service_name] = {
                    "status": "started",
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.logger.info(f"  ✅ {service_name} started")
            except Exception as e:
                self.logger.error(f"  ❌ {service_name} failed: {e}")
                results[service_name] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        return results
    
    async def _shutdown_services_in_order(self, services: List[str]) -> Dict[str, Dict[str, Any]]:
        """Shutdown services in reverse dependency order."""
        results = {}
        
        # Reverse the order for shutdown
        for service_name in reversed(services):
            try:
                self.logger.info(f"  Shutting down {service_name}...")
                # This would shutdown the actual service
                results[service_name] = {
                    "status": "shutdown",
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.logger.info(f"  ✅ {service_name} shutdown")
            except Exception as e:
                self.logger.error(f"  ❌ {service_name} shutdown failed: {e}")
                results[service_name] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        return results
    
    async def _check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service."""
        try:
            # This would make actual health check requests
            # For now, return a basic health status
            return {
                "service_name": service_name,
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "service_name": service_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _monitor_startup_health(self, services: List[str]) -> Dict[str, Any]:
        """Monitor health during startup."""
        health_results = {}
        
        for service_name in services:
            health_results[service_name] = await self._check_service_health(service_name)
        
        return health_results
    
    async def _validate_startup_success(self, startup_results: Dict[str, Any], health_status: Dict[str, Any]) -> bool:
        """Validate that startup was successful."""
        # Check that all services started successfully
        all_started = all(
            result.get("status") == "started" 
            for result in startup_results.values()
        )
        
        # Check that all services are healthy
        all_healthy = all(
            health.get("status") == "healthy"
            for health in health_status.values()
        )
        
        return all_started and all_healthy




