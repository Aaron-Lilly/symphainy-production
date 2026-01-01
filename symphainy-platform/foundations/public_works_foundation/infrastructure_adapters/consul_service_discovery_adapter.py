#!/usr/bin/env python3
"""
Consul Service Discovery Adapter - Layer 1 of 5-Layer Architecture

This adapter provides raw, technology-specific bindings for Consul service discovery.
Implements the ServiceDiscoveryAdapter protocol for swap-ability.

WHAT (Infrastructure Role): I provide raw Consul bindings for service registration and discovery
HOW (Infrastructure Implementation): I use the Consul client with direct commands
WHY: To enable service mesh capabilities with potential to swap for Istio/Linkerd
"""

import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from consul import Consul


class ConsulServiceDiscoveryAdapter:
    """
    Consul Service Discovery Adapter.
    
    Provides raw Consul bindings for service registration, discovery, and configuration management.
    Implements ServiceDiscoveryAdapter protocol to enable swap-ability.
    """

    def __init__(self, consul_client: Consul, service_name: str = "consul_service_discovery_adapter", di_container=None):
        """Initialize Consul Service Discovery Adapter with a Consul client."""
        if not di_container:
            raise ValueError("DI Container is required for ConsulServiceDiscoveryAdapter initialization")
        self.consul_client = consul_client
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"ConsulServiceDiscoveryAdapter-{service_name}")
        self.is_connected = False

        self.logger.info(f"✅ Consul Service Discovery Adapter '{service_name}' initialized")

    async def connect(self) -> bool:
        """
        Test Consul connection with timeout to prevent hanging.
        
        Consul is CRITICAL infrastructure - if unavailable, platform should fail gracefully.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If Consul is unavailable (with timeout to prevent hanging)
        """
        import asyncio
        
        try:
            # Use asyncio timeout to prevent hanging on unavailable Consul
            # Wrap synchronous consul call in executor to make it async and timeout-able
            loop = asyncio.get_event_loop()
            try:
                # Run consul connection check with timeout (5 seconds)
                agent_info = await asyncio.wait_for(
                    loop.run_in_executor(None, self.consul_client.agent.self),
                    timeout=5.0
                )
                self.is_connected = True
                self.logger.info(f"✅ Consul connection established for '{self.service_name}'")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("connect", {
                        "service": self.service_name,
                        "success": True
                    })
                
                return True
            except asyncio.TimeoutError:
                error_msg = f"Consul connection timeout for '{self.service_name}' - Consul is CRITICAL infrastructure and must be available"
                self.logger.error(f"❌ {error_msg}")
                self.is_connected = False
                # Raise error - Consul is critical, platform should fail gracefully
                raise ConnectionError(error_msg)
        except ConnectionError:
            # Re-raise ConnectionError (from timeout or other connection issues)
            raise
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "connect",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Consul connection failed for '{self.service_name}' - Consul is CRITICAL infrastructure: {e}")
            self.is_connected = False
            # Raise error - Consul is critical, platform should fail gracefully
            raise ConnectionError(f"Consul connection failed for '{self.service_name}': {e}")

    # ============================================================================
    # SERVICE REGISTRATION & DISCOVERY
    # ============================================================================

    async def register_service(self, service_name: str, service_data: Dict[str, Any]) -> bool:
        """
        Register a service with Consul.
        
        Args:
            service_name: Name of the service to register
            service_data: Service registration data including address, port, tags, etc.
        
        Returns:
            bool: True if registration successful, False otherwise
        """
        if not self.is_connected:
            await self.connect()

        try:
            # Extract service details
            service_id = service_data.get("service_id", service_name)
            address = service_data.get("address", "127.0.0.1")
            port = service_data.get("port", 8000)
            tags = service_data.get("tags", [])
            meta = service_data.get("meta", {})
            check = service_data.get("check", None)
            
            # Convert meta to tags (python-consul doesn't support meta parameter directly)
            # Add key metadata as tags in format "key:value"
            # CRITICAL: Only serialize simple types - skip complex objects (service instances, handlers, etc.)
            enriched_tags = tags.copy() if tags else []
            for k, v in meta.items():
                try:
                    # Skip complex objects that might contain thread locks
                    if hasattr(v, '__dict__') and not isinstance(v, (str, int, float, bool, type(None))):
                        # Skip service instances, handlers, etc.
                        self.logger.debug(f"⚠️ Skipping meta key '{k}' - complex object type: {type(v).__name__}")
                        continue
                    
                    # Handle simple types
                    if isinstance(v, (str, int, float, bool, type(None))):
                        enriched_tags.append(f"{k}:{v}")
                    elif isinstance(v, (list, tuple)):
                        # Convert lists/tuples to comma-separated strings (only if items are simple)
                        simple_items = [str(item) for item in v if isinstance(item, (str, int, float, bool))]
                        if simple_items:
                            enriched_tags.append(f"{k}:{','.join(simple_items)}")
                    elif isinstance(v, dict):
                        # Convert dicts to JSON strings (but skip if contains unpicklable objects)
                        try:
                            import json
                            # Only serialize if all values are simple types
                            if all(isinstance(v2, (str, int, float, bool, type(None), list, dict)) and not hasattr(v2, '__dict__') for v2 in v.values()):
                                enriched_tags.append(f"{k}:{json.dumps(v, default=str)}")
                            else:
                                self.logger.debug(f"⚠️ Skipping meta key '{k}' - dict contains complex objects")
                        except (TypeError, ValueError):
                            self.logger.debug(f"⚠️ Skipping meta key '{k}' - cannot serialize dict")
                    else:
                        # Try string conversion for other types (but this might fail)
                        enriched_tags.append(f"{k}:{str(v)}")
                except Exception as e:
                    # Skip this meta key if serialization fails
                    self.logger.debug(f"⚠️ Skipping meta key '{k}' - serialization error: {e}")
            
            # Register service with Consul
            self.consul_client.agent.service.register(
                name=service_name,
                service_id=service_id,
                address=address,
                port=port,
                tags=enriched_tags,
                check=check
            )
            
            self.logger.info(f"✅ Registered service '{service_name}' with Consul at {address}:{port}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("register_service", {
                    "service_name": service_name,
                    "address": address,
                    "port": port,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "register_service",
                    "service_name": service_name,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error registering service '{service_name}': {e}")
            return False

    async def deregister_service(self, service_name: str, service_id: Optional[str] = None) -> bool:
        """
        Deregister a service from Consul.
        
        Args:
            service_name: Name of the service to deregister
            service_id: Optional specific service ID to deregister
        
        Returns:
            bool: True if deregistration successful, False otherwise
        """
        if not self.is_connected:
            await self.connect()

        try:
            if service_id:
                # Deregister specific service instance
                self.consul_client.agent.service.deregister(service_id)
                self.logger.info(f"✅ Deregistered service instance '{service_id}' from Consul")
            else:
                # Deregister all instances of the service
                services = self.consul_client.health.service(service_name)
                for service in services[1]:
                    service_instance_id = service["Service"]["ID"]
                    self.consul_client.agent.service.deregister(service_instance_id)
                self.logger.info(f"✅ Deregistered all instances of service '{service_name}' from Consul")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("deregister_service", {
                    "service_name": service_name,
                    "service_id": service_id,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "deregister_service",
                    "service_name": service_name,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error deregistering service '{service_name}': {e}")
            return False

    async def discover_service(self, service_name: str) -> List[Dict[str, Any]]:
        """
        Discover services by name from Consul.
        
        Args:
            service_name: Name of the service to discover
        
        Returns:
            List[Dict]: List of service instances with metadata
        """
        if not self.is_connected:
            await self.connect()

        try:
            # Get healthy services
            services = self.consul_client.health.service(service_name, passing=True)
            
            service_instances = []
            for service in services[1]:
                service_info = {
                    "service_id": service["Service"]["ID"],
                    "service_name": service["Service"]["Service"],
                    "address": service["Service"]["Address"],
                    "port": service["Service"]["Port"],
                    "tags": service["Service"]["Tags"],
                    "meta": service["Service"]["Meta"],
                    "health_status": "passing"
                }
                service_instances.append(service_info)
            
            self.logger.debug(f"✅ Discovered {len(service_instances)} instances of service '{service_name}'")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("discover_service", {
                    "service_name": service_name,
                    "instance_count": len(service_instances),
                    "success": True
                })
            
            return service_instances
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "discover_service",
                    "service_name": service_name,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error discovering service '{service_name}': {e}")
            return []

    async def get_all_services(self) -> List[str]:
        """
        Get list of all registered service names.
        
        Returns:
            List[str]: List of service names
        """
        if not self.is_connected:
            await self.connect()

        try:
            services = self.consul_client.catalog.services()
            service_names = list(services[1].keys())
            self.logger.debug(f"✅ Retrieved {len(service_names)} registered services from Consul")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_all_services", {
                    "service_count": len(service_names),
                    "success": True
                })
            
            return service_names
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_all_services",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting services: {e}")
            return []

    # ============================================================================
    # HEALTH MANAGEMENT
    # ============================================================================

    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Get health status of a service from Consul.
        
        Args:
            service_name: Name of the service to check
        
        Returns:
            Dict: Health status information
        """
        if not self.is_connected:
            await self.connect()

        try:
            # Get service health information
            health_info = self.consul_client.health.service(service_name)
            
            health_status = {
                "service_name": service_name,
                "total_instances": len(health_info[1]),
                "healthy_instances": 0,
                "unhealthy_instances": 0,
                "instances": []
            }
            
            for service in health_info[1]:
                instance_info = {
                    "service_id": service["Service"]["ID"],
                    "address": service["Service"]["Address"],
                    "port": service["Service"]["Port"],
                    "health_status": "unknown",
                    "checks": []
                }
                
                # Check health from Consul checks
                is_healthy = True
                for check in service.get("Checks", []):
                    check_info = {
                        "check_id": check["CheckID"],
                        "status": check["Status"],
                        "output": check.get("Output", "")
                    }
                    instance_info["checks"].append(check_info)
                    
                    if check["Status"] != "passing":
                        is_healthy = False
                
                if is_healthy:
                    instance_info["health_status"] = "passing"
                    health_status["healthy_instances"] += 1
                else:
                    instance_info["health_status"] = "critical"
                    health_status["unhealthy_instances"] += 1
                
                health_status["instances"].append(instance_info)
            
            self.logger.debug(f"✅ Retrieved health status for service '{service_name}': {health_status['healthy_instances']} healthy, {health_status['unhealthy_instances']} unhealthy")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_service_health", {
                    "service_name": service_name,
                    "healthy_instances": health_status['healthy_instances'],
                    "unhealthy_instances": health_status['unhealthy_instances'],
                    "success": True
                })
            
            return health_status
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_service_health",
                    "service_name": service_name,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting health status for service '{service_name}': {e}")
            return {"error": str(e)}

    async def update_service_health(self, service_id: str, status: str) -> bool:
        """
        Update health status of a service instance.
        
        Note: Consul health checks are typically managed by Consul itself.
        This method is provided for compatibility with the protocol.
        
        Args:
            service_id: Service instance ID
            status: New health status (passing, warning, critical)
        
        Returns:
            bool: True if update successful
        """
        self.logger.warning(f"⚠️ update_service_health called for {service_id} - Consul manages health automatically")
        # Consul typically manages health checks automatically
        # For manual control, would need to use TTL checks
        return True

    # ============================================================================
    # CONFIGURATION MANAGEMENT (KV Store)
    # ============================================================================

    async def put_config(self, key: str, value: Any) -> bool:
        """
        Store configuration value in Consul KV store.
        
        Args:
            key: Configuration key
            value: Configuration value (will be JSON encoded if not string)
        
        Returns:
            bool: True if successful
        """
        if not self.is_connected:
            await self.connect()

        try:
            # Convert value to string (JSON encode if not string)
            if isinstance(value, str):
                str_value = value
            else:
                str_value = json.dumps(value)
            
            # Store in Consul KV
            success = self.consul_client.kv.put(key, str_value)
            
            if success:
                self.logger.debug(f"✅ Stored config key '{key}' in Consul KV")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("put_config", {
                        "key": key,
                        "success": True
                    })
            else:
                self.logger.warning(f"⚠️ Failed to store config key '{key}' in Consul KV")
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "put_config",
                    "key": key,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error storing config key '{key}': {e}")
            return False

    async def get_config(self, key: str) -> Optional[Any]:
        """
        Retrieve configuration value from Consul KV store.
        
        Args:
            key: Configuration key
        
        Returns:
            Configuration value (JSON decoded if possible) or None if not found
        """
        if not self.is_connected:
            await self.connect()

        try:
            # Get from Consul KV
            index, data = self.consul_client.kv.get(key)
            
            if data is None:
                self.logger.debug(f"ℹ️ Config key '{key}' not found in Consul KV")
                return None
            
            # Decode value
            str_value = data['Value'].decode('utf-8')
            
            # Try to JSON decode
            try:
                value = json.loads(str_value)
            except json.JSONDecodeError:
                # Return as string if not JSON
                value = str_value
            
            self.logger.debug(f"✅ Retrieved config key '{key}' from Consul KV")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_config", {
                    "key": key,
                    "found": value is not None,
                    "success": True
                })
            
            return value
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_config",
                    "key": key,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error retrieving config key '{key}': {e}")
            return None

    async def delete_config(self, key: str) -> bool:
        """
        Delete configuration value from Consul KV store.
        
        Args:
            key: Configuration key
        
        Returns:
            bool: True if successful
        """
        if not self.is_connected:
            await self.connect()

        try:
            success = self.consul_client.kv.delete(key)
            
            if success:
                self.logger.debug(f"✅ Deleted config key '{key}' from Consul KV")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("delete_config", {
                        "key": key,
                        "success": True
                    })
            else:
                self.logger.warning(f"⚠️ Failed to delete config key '{key}' from Consul KV")
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "delete_config",
                    "key": key,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error deleting config key '{key}': {e}")
            return False

    # ============================================================================
    # WATCH / REAL-TIME NOTIFICATIONS
    # ============================================================================

    async def watch_service(self, service_name: str, callback: Callable) -> Any:
        """
        Watch for changes to a service.
        
        Note: This is a simplified implementation. Production would use Consul's
        blocking queries or watches for efficient real-time updates.
        
        Args:
            service_name: Name of service to watch
            callback: Callback function to invoke on changes
        
        Returns:
            Watch handle (for future cancellation)
        """
        self.logger.info(f"🔍 Setting up watch for service '{service_name}'")
        # TODO: Implement proper Consul watch using blocking queries
        # For now, return placeholder
        return f"watch_{service_name}"

    async def watch_config(self, key: str, callback: Callable) -> Any:
        """
        Watch for changes to a configuration key.
        
        Note: This is a simplified implementation. Production would use Consul's
        blocking queries or watches for efficient real-time updates.
        
        Args:
            key: Configuration key to watch
            callback: Callback function to invoke on changes
        
        Returns:
            Watch handle (for future cancellation)
        """
        self.logger.info(f"🔍 Setting up watch for config key '{key}'")
        # TODO: Implement proper Consul watch using blocking queries
        # For now, return placeholder
        return f"watch_config_{key}"

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    async def get_agent_info(self) -> Dict[str, Any]:
        """
        Get Consul agent information.
        
        Returns:
            Dict: Agent information
        """
        if not self.is_connected:
            await self.connect()

        try:
            agent_info = self.consul_client.agent.self()
            result = {
                "agent_id": agent_info.get("Config", {}).get("NodeID"),
                "datacenter": agent_info.get("Config", {}).get("Datacenter"),
                "server": agent_info.get("Config", {}).get("Server"),
                "version": agent_info.get("Config", {}).get("Version"),
                "raft_leader": agent_info.get("Stats", {}).get("raft", {}).get("leader")
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_agent_info", {
                    "success": True
                })
            
            return result
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_agent_info",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting agent info: {e}")
            return {"error": str(e)}

