#!/usr/bin/env python3
"""
Communication Registry - Communication Service Registry

Communication registry that manages and tracks all communication
infrastructure components and their relationships.

WHAT (Infrastructure Registry): I manage communication infrastructure components
HOW (Registry Implementation): I track and coordinate all communication services
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import infrastructure abstractions
from ..infrastructure_abstractions.communication_abstraction import CommunicationAbstraction
from ..infrastructure_abstractions.soa_client_abstraction import SOAClientAbstraction
from ..infrastructure_abstractions.websocket_abstraction import WebSocketAbstraction

logger = logging.getLogger(__name__)


class CommunicationRegistry:
    """
    Communication Registry - Communication Service Registry
    
    Manages and tracks all communication infrastructure components
    and their relationships for unified communication management.
    
    WHAT (Infrastructure Registry): I manage communication infrastructure components
    HOW (Registry Implementation): I track and coordinate all communication services
    """
    
    def __init__(self, communication_abstraction: CommunicationAbstraction,
                 soa_client_abstraction: SOAClientAbstraction,
                 websocket_abstraction: WebSocketAbstraction):
        """Initialize Communication Registry."""
        self.logger = logging.getLogger("CommunicationRegistry")
        
        # Infrastructure abstractions
        self.communication_abstraction = communication_abstraction
        self.soa_client_abstraction = soa_client_abstraction
        self.websocket_abstraction = websocket_abstraction
        
        # Registry data
        self.registered_services = {}
        self.service_relationships = {}
        self.communication_endpoints = {}
        self.health_status = {}
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ Communication Registry initialized")
    
    async def initialize(self):
        """Initialize Communication Registry."""
        try:
            self.logger.info("🚀 Initializing Communication Registry...")
            
            # Initialize all abstractions (if available)
            if self.communication_abstraction:
                await self.communication_abstraction.initialize()
                self.logger.info("✅ Communication abstraction initialized")
            else:
                self.logger.warning("⚠️ Communication abstraction not available, skipping")
            
            if self.soa_client_abstraction:
                await self.soa_client_abstraction.initialize()
                self.logger.info("✅ SOA Client abstraction initialized")
            else:
                self.logger.warning("⚠️ SOA Client abstraction not available, skipping")
            
            if self.websocket_abstraction:
                await self.websocket_abstraction.initialize()
                self.logger.info("✅ WebSocket abstraction initialized")
            else:
                self.logger.warning("⚠️ WebSocket abstraction not available, skipping")
            
            # Register communication services (even if some abstractions are None)
            await self._register_communication_services()
            
            # Setup service relationships
            await self._setup_service_relationships()
            
            # Setup health monitoring
            await self._setup_health_monitoring()
            
            self.is_initialized = True
            self.logger.info("✅ Communication Registry initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Communication Registry: {e}", exc_info=True)
            raise
    
    async def _register_communication_services(self):
        """Register communication services."""
        self.logger.info("📝 Registering communication services...")
        
        # Register Communication Abstraction
        self.registered_services["communication_abstraction"] = {
            "name": "Communication Abstraction",
            "type": "abstraction",
            "status": "active",
            "capabilities": ["api_communication", "messaging", "events", "websocket"],
            "registered_at": datetime.now()
        }
        
        # Register SOA Client Abstraction
        self.registered_services["soa_client_abstraction"] = {
            "name": "SOA Client Abstraction",
            "type": "abstraction",
            "status": "active",
            "capabilities": ["soa_api", "service_discovery", "service_registration"],
            "registered_at": datetime.now()
        }
        
        # Register WebSocket Abstraction
        self.registered_services["websocket_abstraction"] = {
            "name": "WebSocket Abstraction",
            "type": "abstraction",
            "status": "active",
            "capabilities": ["realtime_communication", "websocket_management"],
            "registered_at": datetime.now()
        }
        
        self.logger.info("✅ Communication services registered")
    
    async def _setup_service_relationships(self):
        """Setup service relationships."""
        self.logger.info("🔗 Setting up service relationships...")
        
        # Communication Abstraction relationships
        self.service_relationships["communication_abstraction"] = {
            "depends_on": [],
            "provides_to": ["soa_client_abstraction", "websocket_abstraction"],
            "relationships": {
                "orchestrates": ["api_gateway_adapter", "messaging_adapter", "event_bus_adapter"],
                "coordinates": ["soa_client_abstraction", "websocket_abstraction"]
            }
        }
        
        # SOA Client Abstraction relationships
        self.service_relationships["soa_client_abstraction"] = {
            "depends_on": ["communication_abstraction"],
            "provides_to": ["realm_services"],
            "relationships": {
                "uses": ["communication_abstraction"],
                "discovers": ["curator_foundation"]
            }
        }
        
        # WebSocket Abstraction relationships
        self.service_relationships["websocket_abstraction"] = {
            "depends_on": ["communication_abstraction"],
            "provides_to": ["realm_services"],
            "relationships": {
                "uses": ["communication_abstraction"],
                "manages": ["websocket_adapter"]
            }
        }
        
        self.logger.info("✅ Service relationships setup complete")
    
    async def _setup_health_monitoring(self):
        """Setup health monitoring."""
        self.logger.info("🏥 Setting up health monitoring...")
        
        # Initialize health status for all services
        for service_name in self.registered_services.keys():
            self.health_status[service_name] = {
                "status": "unknown",
                "last_check": None,
                "response_time_ms": 0,
                "error_count": 0,
                "success_count": 0
            }
        
        self.logger.info("✅ Health monitoring setup complete")
    
    async def start(self):
        """Start Communication Registry."""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            self.logger.info("🚀 Starting Communication Registry...")
            
            # Start all abstractions
            if self.communication_abstraction:
                await self.communication_abstraction.start()
            if self.soa_client_abstraction:
                await self.soa_client_abstraction.start()
            if self.websocket_abstraction:
                await self.websocket_abstraction.start()
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            self.is_running = True
            self.logger.info("✅ Communication Registry started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start Communication Registry: {e}", exc_info=True)
            raise
    
    async def _start_health_monitoring(self):
        """Start health monitoring."""
        self.logger.info("🏥 Starting health monitoring...")
        
        # Start background health monitoring task
        asyncio.create_task(self._health_monitoring_loop())
        
        self.logger.info("✅ Health monitoring started")
    
    async def _health_monitoring_loop(self):
        """Health monitoring loop."""
        while self.is_running:
            try:
                await self._check_service_health()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_service_health(self):
        """Check health of all services."""
        for service_name in self.registered_services.keys():
            try:
                start_time = datetime.now()
                
                # Check service health based on type
                if service_name == "communication_abstraction":
                    stats = await self.communication_abstraction.get_communication_stats()
                    health_status = "healthy" if stats.get("is_running", False) else "unhealthy"
                elif service_name == "soa_client_abstraction":
                    stats = await self.soa_client_abstraction.get_service_stats("", "")
                    health_status = "healthy" if stats else "unhealthy"
                elif service_name == "websocket_abstraction":
                    stats = await self.websocket_abstraction.get_global_stats()
                    health_status = "healthy" if stats.get("is_running", False) else "unhealthy"
                else:
                    health_status = "unknown"
                
                end_time = datetime.now()
                response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Update health status
                self.health_status[service_name].update({
                    "status": health_status,
                    "last_check": datetime.now(),
                    "response_time_ms": response_time_ms,
                    "success_count": self.health_status[service_name]["success_count"] + (1 if health_status == "healthy" else 0),
                    "error_count": self.health_status[service_name]["error_count"] + (1 if health_status != "healthy" else 0)
                })
                
            except Exception as e:
                self.logger.error(f"❌ Health check failed for {service_name}: {e}")
                self.health_status[service_name].update({
                    "status": "error",
                    "last_check": datetime.now(),
                    "error_count": self.health_status[service_name]["error_count"] + 1
                })
    
    async def stop(self):
        """Stop Communication Registry."""
        try:
            self.logger.info("🛑 Stopping Communication Registry...")
            
            # Stop all abstractions
            if self.websocket_abstraction:
                await self.websocket_abstraction.stop()
            if self.soa_client_abstraction:
                await self.soa_client_abstraction.stop()
            if self.communication_abstraction:
                await self.communication_abstraction.stop()
            
            self.is_running = False
            self.logger.info("✅ Communication Registry stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop Communication Registry: {e}", exc_info=True)
            raise
    
    async def shutdown(self):
        """Shutdown Communication Registry."""
        try:
            await self.stop()
            self.logger.info("🔌 Communication Registry shutdown complete")
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Communication Registry: {e}", exc_info=True)
            raise
    
    # Registry management methods
    
    async def register_service(self, service_name: str, service_info: Dict[str, Any]) -> bool:
        """Register a communication service."""
        try:
            self.registered_services[service_name] = {
                **service_info,
                "registered_at": datetime.now()
            }
            
            # Initialize health status
            self.health_status[service_name] = {
                "status": "unknown",
                "last_check": None,
                "response_time_ms": 0,
                "error_count": 0,
                "success_count": 0
            }
            
            self.logger.info(f"✅ Service registered: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register service: {e}")
            return False
    
    async def unregister_service(self, service_name: str) -> bool:
        """Unregister a communication service."""
        try:
            if service_name in self.registered_services:
                del self.registered_services[service_name]
            
            if service_name in self.health_status:
                del self.health_status[service_name]
            
            if service_name in self.service_relationships:
                del self.service_relationships[service_name]
            
            self.logger.info(f"✅ Service unregistered: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to unregister service: {e}")
            return False
    
    async def get_service_info(self, service_name: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get service information."""
        try:
            self.logger.debug(f"Getting service info for: {service_name}")
            
            # Note: Registry doesn't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.registered_services.get(service_name)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get service info for {service_name}: {e}", exc_info=True)
            return None
    
    async def get_service_health(self, service_name: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get service health status."""
        try:
            self.logger.debug(f"Getting service health for: {service_name}")
            
            # Note: Registry doesn't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.health_status.get(service_name)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get service health for {service_name}: {e}", exc_info=True)
            return None
    
    async def get_service_relationships(self, service_name: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get service relationships."""
        try:
            self.logger.debug(f"Getting service relationships for: {service_name}")
            
            # Note: Registry doesn't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.service_relationships.get(service_name)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get service relationships for {service_name}: {e}", exc_info=True)
            return None
    
    async def get_all_services(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all registered services."""
        try:
            self.logger.debug("Getting all services")
            
            # Note: Registry doesn't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.registered_services
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get all services: {e}", exc_info=True)
            return {}
    
    async def get_all_health_status(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get health status of all services."""
        try:
            self.logger.debug("Getting all health status")
            
            # Note: Registry doesn't have utility access yet
            # Security/tenant validation would be added when DI Container access is available
            
            return self.health_status
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get all health status: {e}", exc_info=True)
            return {}
    
    async def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_services": len(self.registered_services),
            "healthy_services": len([
                service for service, health in self.health_status.items()
                if health["status"] == "healthy"
            ]),
            "unhealthy_services": len([
                service for service, health in self.health_status.items()
                if health["status"] == "unhealthy"
            ]),
            "error_services": len([
                service for service, health in self.health_status.items()
                if health["status"] == "error"
            ]),
            "is_running": self.is_running,
            "is_initialized": self.is_initialized
        }
