#!/usr/bin/env python3
"""
Service Discovery Abstraction - Layer 3 of 5-Layer Architecture

This abstraction provides business logic for service registration and discovery.
Technology-agnostic interface that can use Consul, Istio, Linkerd, etc.

WHAT (Infrastructure Role): I provide business logic for service registration and discovery
HOW (Infrastructure Implementation): I use a ServiceDiscoveryAdapter with business logic
WHY: To enable swap-ability between different service mesh technologies
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.service_discovery_protocol import (
    ServiceRegistration, ServiceHealth, HealthStatus, ServiceDiscoveryAdapter
)

class ServiceDiscoveryAbstraction:
    """
    Service Discovery Abstraction.
    
    Provides business logic for service registration and discovery.
    Technology-agnostic - works with any adapter implementing ServiceDiscoveryAdapter protocol.
    """

    def __init__(self, adapter: ServiceDiscoveryAdapter, service_name: str = "service_discovery_abstraction", di_container=None):
        """
        Initialize Service Discovery Abstraction with an adapter.
        
        Args:
            adapter: Service discovery adapter (Consul, Istio, Linkerd, etc.)
            service_name: Name for this abstraction instance
            di_container: DI Container for logging (required)
        """
        if not di_container:
            raise ValueError("DI Container is required for ServiceDiscoveryAbstraction initialization")
        
        self.adapter = adapter
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"ServiceDiscoveryAbstraction-{service_name}")
        
        self.logger.info(f"✅ Service Discovery Abstraction '{service_name}' initialized")

    # ============================================================================
    # SERVICE REGISTRATION
    # ============================================================================

    async def register_service(self, service_info: Dict[str, Any]) -> Optional[ServiceRegistration]:
        """
        Register a service with business logic validation.
        
        Args:
            service_info: Service information including:
                - service_name (required)
                - service_type (required)
                - address (required)
                - port (required)
                - capabilities (list)
                - tags (list)
                - meta (dict)
                - realm (optional)
                - health_check_endpoint (optional)
        
        Returns:
            ServiceRegistration: Registration information or None if failed
        """
        try:
            # Validate required fields
            required_fields = ["service_name", "service_type", "address", "port"]
            for field in required_fields:
                if field not in service_info:
                    self.logger.error(f"❌ Missing required field '{field}' in service_info")
                    return None
            
            service_name = service_info["service_name"]
            
            # Generate service ID (unique per instance)
            service_id = service_info.get("service_id", f"{service_name}-{service_info['address']}-{service_info['port']}")
            
            # Prepare adapter-compatible service data
            service_data = {
                "service_id": service_id,
                "address": service_info["address"],
                "port": service_info["port"],
                "tags": service_info.get("tags", []),
                "meta": {
                    "service_type": service_info["service_type"],
                    "capabilities": ",".join(service_info.get("capabilities", [])),
                    "endpoints": ",".join(service_info.get("endpoints", [])),
                    "realm": service_info.get("realm", "unknown"),
                    "registered_at": datetime.utcnow().isoformat()
                }
            }
            
            # Add health check if specified
            health_check_endpoint = service_info.get("health_check_endpoint")
            if health_check_endpoint:
                service_data["check"] = {
                    "http": f"http://{service_info['address']}:{service_info['port']}{health_check_endpoint}",
                    "interval": "10s",
                    "timeout": "5s"
                }
            
            # Register with adapter
            success = await self.adapter.register_service(service_name, service_data)
            
            if not success:
                self.logger.error(f"❌ Failed to register service '{service_name}' with adapter")
                return None
            
            # Create ServiceRegistration object
            registration = ServiceRegistration(
                service_id=service_id,
                service_name=service_name,
                service_type=service_info["service_type"],
                address=service_info["address"],
                port=service_info["port"],
                tags=service_info.get("tags", []),
                meta=service_data["meta"],
                health_status=HealthStatus.UNKNOWN,
                endpoints=service_info.get("endpoints", []),
                capabilities=service_info.get("capabilities", []),
                realm=service_info.get("realm"),
                health_check_endpoint=health_check_endpoint
            )
            
            self.logger.info(f"✅ Registered service '{service_name}' (ID: {service_id})")
            return registration
            
        except Exception as e:
            self.logger.error(f"❌ Error registering service '{service_name}': {e}")
            raise  # Re-raise for service layer to handle
    
    async def unregister_service(self, service_id: str) -> bool:
        """
        Unregister a service.
        
        Args:
            service_id: Service instance ID
        
        Returns:
            bool: True if successful
        """
        try:
            # Extract service name from service_id (format: servicename-address-port)
            service_name = service_id.split("-")[0]
            
            success = await self.adapter.deregister_service(service_name, service_id)
            
            if success:
                self.logger.info(f"✅ Unregistered service '{service_id}'")
            else:
                self.logger.warning(f"⚠️ Failed to unregister service '{service_id}'")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error unregistering service '{service_id}': {e}")
            raise  # Re-raise for service layer to handle

        """
        Discover service instances by name with business logic.
        
        Args:
            service_name: Name of the service to discover
        
        Returns:
            List[ServiceRegistration]: List of discovered service registrations
        """
        try:
            # Get service instances from adapter
            service_instances = await self.adapter.discover_service(service_name)
            
            service_registrations = []
            for service in service_instances:
                # Parse capabilities and endpoints from meta
                capabilities_str = service.get("meta", {}).get("capabilities", "")
                capabilities = [c.strip() for c in capabilities_str.split(",") if c.strip()]
                
                endpoints_str = service.get("meta", {}).get("endpoints", "")
                endpoints = [e.strip() for e in endpoints_str.split(",") if e.strip()]
                
                service_registration = ServiceRegistration(
                    service_id=service["service_id"],
                    service_name=service["service_name"],
                    service_type=service.get("meta", {}).get("service_type", "unknown"),
                    address=service["address"],
                    port=service["port"],
                    tags=service["tags"],
                    meta=service["meta"],
                    health_status=HealthStatus.PASSING if service.get("health_status") == "passing" else HealthStatus.UNKNOWN,
                    endpoints=endpoints,
                    capabilities=capabilities,
                    realm=service.get("meta", {}).get("realm")
                )
                service_registrations.append(service_registration)
            
            self.logger.debug(f"✅ Discovered {len(service_registrations)} instances of service '{service_name}'")
            return service_registrations
            
        except Exception as e:
            self.logger.error(f"❌ Error discovering service '{service_name}': {e}")
            raise  # Re-raise for service layer to handle

        """
        Discover services by capability.
        
        Args:
            capability: Capability name
        
        Returns:
            List[ServiceRegistration]: Services with this capability
        """
        try:
            # Get all services
            all_service_names = await self.adapter.get_all_services()
            
            matching_services = []
            for service_name in all_service_names:
                # Discover each service
                services = await self.discover_service(service_name)
                
                # Filter by capability
                for service in services:
                    if capability in service.capabilities:
                        matching_services.append(service)
            
            self.logger.debug(f"✅ Found {len(matching_services)} services with capability '{capability}'")
            return matching_services
            
        except Exception as e:
            self.logger.error(f"❌ Error discovering by capability '{capability}': {e}")
            raise  # Re-raise for service layer to handle

        """
        Discover services by tags.
        
        Args:
            tags: List of tags to match
        
        Returns:
            List[ServiceRegistration]: Services matching tags
        """
        try:
            # Get all services
            all_service_names = await self.adapter.get_all_services()
            
            matching_services = []
            for service_name in all_service_names:
                # Discover each service
                services = await self.discover_service(service_name)
                
                # Filter by tags (service must have all specified tags)
                for service in services:
                    if all(tag in service.tags for tag in tags):
                        matching_services.append(service)
            
            self.logger.debug(f"✅ Found {len(matching_services)} services with tags {tags}'")
            return matching_services
            
        except Exception as e:
            self.logger.error(f"❌ Error discovering by tags {tags}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get all registered service names.
        
        Returns:
            List[str]: Service names
        """
        try:
            service_names = await self.adapter.get_all_services()
            self.logger.debug(f"✅ Retrieved {len(service_names)} service names")
            return service_names
        except Exception as e:
            self.logger.error(f"❌ Error getting all services: {e}")
            raise  # Re-raise for service layer to handle

        """
        Check health of a service.
        
        Args:
            service_name: Service name
        
        Returns:
            ServiceHealth: Health information or None if error
        """
        try:
            health_data = await self.adapter.get_service_health(service_name)
            
            if "error" in health_data:
                self.logger.error(f"❌ Error checking health for '{service_name}': {health_data['error']}")
            
            # Determine overall health status
            if health_data["healthy_instances"] > 0:
                status = HealthStatus.PASSING
            elif health_data["unhealthy_instances"] > 0:
                status = HealthStatus.CRITICAL
            else:
                status = HealthStatus.UNKNOWN
            
            # Build kwargs - only include checks if provided (default factory handles None)
            kwargs = {
                "service_id": f"{service_name}-cluster",
                "service_name": service_name,
                "status": status,
                "message": f"{health_data['healthy_instances']}/{health_data['total_instances']} instances healthy"
            }
            if health_data.get("instances"):
                kwargs["checks"] = health_data.get("instances")
            service_health = ServiceHealth(**kwargs)
            
            self.logger.debug(f"✅ Health check for '{service_name}': {status}")
            return service_health
            
        except Exception as e:
            self.logger.error(f"❌ Error checking service health '{service_name}': {e}")
            raise  # Re-raise for service layer to handle

        """
        Store configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        
        Returns:
            bool: True if successful
        """
        try:
            success = await self.adapter.put_config(key, value)
            if success:
                self.logger.debug(f"✅ Stored config '{key}'")
            else:
                self.logger.warning(f"⚠️ Failed to store config '{key}'")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error setting config '{key}': {e}")
            raise  # Re-raise for service layer to handle

        """
        Retrieve configuration value.
        
        Args:
            key: Configuration key
        
        Returns:
            Configuration value or None if not found
        """
        try:
            value = await self.adapter.get_config(key)
            if value is not None:
                self.logger.debug(f"✅ Retrieved config '{key}'")
            else:
                self.logger.debug(f"ℹ️ Config '{key}' not found")
            return value
        except Exception as e:
            self.logger.error(f"❌ Error getting config '{key}': {e}")
            raise  # Re-raise for service layer to handle

        """
        Delete configuration value.
        
        Args:
            key: Configuration key
        
        Returns:
            bool: True if successful
        """
        try:
            success = await self.adapter.delete_config(key)
            if success:
                self.logger.debug(f"✅ Deleted config '{key}'")
            else:
                self.logger.warning(f"⚠️ Failed to delete config '{key}'")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error deleting config '{key}': {e}")
            raise  # Re-raise for service layer to handle

        """
        Watch for service changes.
        
        Args:
            service_name: Service name to watch
            callback: Callback function for changes
        
        Returns:
            Watch handle
        """
        try:
            handle = await self.adapter.watch_service(service_name, callback)
            self.logger.info(f"🔍 Watching service '{service_name}'")
            return handle
        except Exception as e:
            self.logger.error(f"❌ Error watching service '{service_name}': {e}")
            raise  # Re-raise for service layer to handle

        """
        Watch for configuration changes.
        
        Args:
            key: Configuration key to watch
            callback: Callback function for changes
        
        Returns:
            Watch handle
        """
        try:
            handle = await self.adapter.watch_config(key, callback)
            self.logger.info(f"🔍 Watching config '{key}'")
            return handle
        except Exception as e:
            self.logger.error(f"❌ Error watching config '{key}': {e}")
            raise  # Re-raise for service layer to handle
