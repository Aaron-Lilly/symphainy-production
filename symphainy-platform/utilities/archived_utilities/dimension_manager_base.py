"""
Dimension Manager Base Class

This provides a lightweight base class for dimension managers that coordinate
services within their domain and help with cross-dimension communication.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

from .error import get_error_handler
from .health import HealthManagementUtility, ServiceStatus
from .logging import get_logging_service
from .telemetry_reporting import get_telemetry_reporting_utility

logger = logging.getLogger(__name__)


class DimensionManagerBase(ABC):
    """
    Lightweight base class for dimension managers.
    
    Provides:
    - Basic utilities (logging, error handling, health, telemetry)
    - Service discovery within the dimension
    - Cross-dimension coordination
    - Simple orchestration when needed
    """
    
    def __init__(self, manager_name: str, dimension: str):
        """
        Initialize dimension manager.
        
        Args:
            manager_name: Name of the manager
            dimension: Dimension type (smart_city, business_pillars, experience, orchestration)
        """
        self.manager_name = manager_name
        self.dimension = dimension
        
        # Initialize utilities
        self.logger = get_logging_service(manager_name)
        self.error_handler = get_error_handler(manager_name)
        self.health_utility = HealthManagementUtility(manager_name)
        self.telemetry_reporting = get_telemetry_reporting_utility(manager_name)
        
        # Manager state
        self.status = ServiceStatus.INITIALIZING
        self.start_time = datetime.utcnow()
        self.services = []  # Services in this dimension
        self.cross_dimension_clients = {}  # Clients for other dimensions
        
        self.logger.info(f"Initialized {manager_name} Dimension Manager ({dimension})")
    
    @abstractmethod
    async def discover_dimension_services(self):
        """
        Discover services within this dimension.
        
        This method MUST be implemented by each manager
        to find and register services in their dimension.
        """
        pass
    
    @abstractmethod
    async def initialize_cross_dimension_clients(self):
        """
        Initialize clients for cross-dimension communication.
        
        This method MUST be implemented by each manager
        to set up communication with other dimensions.
        """
        pass
    
    async def initialize(self):
        """Initialize the dimension manager asynchronously."""
        try:
            # Discover services in this dimension
            await self.discover_dimension_services()
            
            # Initialize cross-dimension clients
            await self.initialize_cross_dimension_clients()
            
            # Set status to running
            self.status = ServiceStatus.RUNNING
            
            self.logger.info(f"✅ {self.manager_name} Dimension Manager initialized successfully")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ {self.manager_name} Dimension Manager initialization failed: {e}")
            self.error_handler.handle_error(e)
            raise
    
    def add_service(self, service_name: str, service_url: str, port: int, 
                   capabilities: List[str] = None, service_type: str = "soa"):
        """
        Add a service to this dimension.
        
        Args:
            service_name: Name of the service
            service_url: URL of the service
            port: Port of the service
            capabilities: List of service capabilities
            service_type: Type of service (soa, mcp)
        """
        service = {
            "name": service_name,
            "url": service_url,
            "port": port,
            "capabilities": capabilities or [],
            "type": service_type,
            "full_url": f"http://{service_url}:{port}",
            "registered_at": datetime.utcnow().isoformat()
        }
        
        self.services.append(service)
        self.logger.info(f"Added service to {self.dimension}: {service_name}")
    
    def add_cross_dimension_client(self, dimension: str, client):
        """
        Add a client for cross-dimension communication.
        
        Args:
            dimension: Name of the other dimension
            client: Client object for communication
        """
        self.cross_dimension_clients[dimension] = client
        self.logger.info(f"Added cross-dimension client: {dimension}")
    
    async def get_dimension_services(self, service_type: str = None) -> List[Dict[str, Any]]:
        """
        Get services in this dimension.
        
        Args:
            service_type: Filter by service type (soa, mcp)
            
        Returns:
            List of services
        """
        if service_type:
            return [s for s in self.services if s["type"] == service_type]
        return self.services
    
    async def find_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a specific service in this dimension.
        
        Args:
            service_name: Name of the service to find
            
        Returns:
            Service information or None if not found
        """
        for service in self.services:
            if service["name"] == service_name:
                return service
        return None
    
    async def coordinate_with_dimension(self, target_dimension: str, 
                                      coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate with another dimension.
        
        Args:
            target_dimension: Name of the target dimension
            coordination_request: Request details
            
        Returns:
            Coordination result
        """
        try:
            if target_dimension not in self.cross_dimension_clients:
                return {
                    "status": "error",
                    "error": f"No client available for dimension: {target_dimension}",
                    "target_dimension": target_dimension
                }
            
            client = self.cross_dimension_clients[target_dimension]
            
            # Execute coordination request
            result = await client.coordinate_request(coordination_request)
            
            # Log coordination
            await self.log_telemetry({
                "event": "cross_dimension_coordination",
                "source_dimension": self.dimension,
                "target_dimension": target_dimension,
                "request_type": coordination_request.get("type", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }, "coordination")
            
            return {
                "status": "success",
                "target_dimension": target_dimension,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error coordinating with {target_dimension}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "target_dimension": target_dimension
            }
    
    async def orchestrate_workflow(self, workflow_name: str, 
                                 participating_services: List[str]) -> Dict[str, Any]:
        """
        Orchestrate a workflow within this dimension.
        
        Args:
            workflow_name: Name of the workflow
            participating_services: List of services to include
            
        Returns:
            Orchestration result
        """
        try:
            # Find participating services
            workflow_services = []
            for service_name in participating_services:
                service = await self.find_service(service_name)
                if service:
                    workflow_services.append(service)
                else:
                    self.logger.warning(f"Service {service_name} not found in dimension")
            
            # Simple orchestration (can be enhanced)
            orchestration_result = {
                "workflow_name": workflow_name,
                "dimension": self.dimension,
                "participating_services": workflow_services,
                "orchestration_status": "initiated",
                "workflow_id": f"{workflow_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log orchestration
            await self.log_telemetry({
                "event": "workflow_orchestrated",
                "workflow_name": workflow_name,
                "dimension": self.dimension,
                "participating_services": participating_services,
                "timestamp": datetime.utcnow().isoformat()
            }, "orchestration")
            
            return {
                "status": "success",
                "orchestration_result": orchestration_result
            }
            
        except Exception as e:
            self.logger.error(f"Error orchestrating workflow {workflow_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "workflow_name": workflow_name
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for this dimension manager."""
        try:
            health_data = {
                "manager_name": self.manager_name,
                "dimension": self.dimension,
                "status": self.status.value,
                "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
                "services": {
                    "total": len(self.services),
                    "soa_services": len([s for s in self.services if s["type"] == "soa"]),
                    "mcp_services": len([s for s in self.services if s["type"] == "mcp"])
                },
                "cross_dimension_clients": list(self.cross_dimension_clients.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_data
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "manager_name": self.manager_name
            }
    
    async def get_manager_info(self) -> Dict[str, Any]:
        """Get comprehensive manager information."""
        return {
            "manager_name": self.manager_name,
            "dimension": self.dimension,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "services": self.services,
            "cross_dimension_clients": list(self.cross_dimension_clients.keys())
        }
    
    async def log_telemetry(self, telemetry_data: Dict[str, Any], 
                           telemetry_type: str = "general") -> Dict[str, Any]:
        """Log telemetry data."""
        return await self.telemetry_service.log_telemetry_data(telemetry_data, telemetry_type)
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None):
        """Handle errors."""
        return self.error_handler.handle_error(error, context)
    
    def get_status(self) -> ServiceStatus:
        """Get current manager status."""
        return self.status
    
    def set_status(self, status: ServiceStatus):
        """Set manager status."""
        self.status = status
        self.logger.info(f"Status changed to {status.value} for {self.manager_name}")
    
    async def start_manager(self):
        """Start the dimension manager."""
        self.set_status(ServiceStatus.RUNNING)
        self.logger.info(f"Started {self.manager_name} Dimension Manager")
        
        # Log startup telemetry
        await self.log_telemetry({
            "event": "dimension_manager_started",
            "manager_name": self.manager_name,
            "dimension": self.dimension,
            "timestamp": datetime.utcnow().isoformat()
        }, "manager_lifecycle")
    
    async def stop_manager(self):
        """Stop the dimension manager."""
        self.set_status(ServiceStatus.STOPPING)
        self.logger.info(f"Stopping {self.manager_name} Dimension Manager")
        
        # Log shutdown telemetry
        await self.log_telemetry({
            "event": "dimension_manager_stopped",
            "manager_name": self.manager_name,
            "dimension": self.dimension,
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "timestamp": datetime.utcnow().isoformat()
        }, "manager_lifecycle")
        
        self.set_status(ServiceStatus.STOPPED)
    
    async def restart_manager(self):
        """Restart the dimension manager."""
        await self.stop_manager()
        await asyncio.sleep(1)  # Brief pause
        await self.start_manager()

