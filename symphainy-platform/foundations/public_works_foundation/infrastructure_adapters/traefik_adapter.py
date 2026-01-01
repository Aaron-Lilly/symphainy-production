#!/usr/bin/env python3
"""
Traefik Routing Adapter - Layer 1 of 5-Layer Architecture

This adapter provides raw, technology-specific bindings for Traefik reverse proxy.
Implements routing operations for service discovery and load balancing.

WHAT (Infrastructure Role): I provide raw Traefik bindings for route registration and discovery
HOW (Infrastructure Implementation): I use the Traefik HTTP API with direct commands
WHY: To enable reverse proxy capabilities with automatic service discovery via Docker labels
"""

import json
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime


class TraefikAdapter:
    """
    Traefik Routing Adapter.
    
    Provides raw Traefik bindings for route registration, discovery, and health checking.
    Routes are primarily managed via Docker labels, but this adapter provides API access.
    """

    def __init__(self, traefik_api_url: str = "http://traefik:8080", service_name: str = "traefik_adapter", di_container=None):
        """Initialize Traefik Adapter with Traefik API URL."""
        if not di_container:
            raise ValueError("DI Container is required for TraefikAdapter initialization")
        self.traefik_api_url = traefik_api_url.rstrip('/')
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"TraefikAdapter-{service_name}")
        self.is_connected = False

        self.logger.info(f"✅ Traefik Adapter '{service_name}' initialized (API: {traefik_api_url})")

    async def connect(self) -> bool:
        """
        Test Traefik connection with timeout to prevent hanging.
        
        Traefik is CRITICAL infrastructure - if unavailable, platform should fail gracefully.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If Traefik is unavailable (with timeout to prevent hanging)
        """
        import asyncio
        
        try:
            # Use asyncio timeout to prevent hanging on unavailable Traefik
            # Traefik v3 uses /api/version or /api/overview for health checks (not /ping)
            async with httpx.AsyncClient(timeout=5.0) as client:
                try:
                    # Try /api/version first (more reliable)
                    response = await asyncio.wait_for(
                        client.get(f"{self.traefik_api_url}/api/version"),
                        timeout=5.0
                    )
                    if response.status_code == 200:
                        self.is_connected = True
                        self.logger.info(f"✅ Traefik connection established for '{self.service_name}'")
                        
                        # Record telemetry on success
                        telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                        if telemetry:
                            await telemetry.record_platform_operation_event("connect", {
                                "service": self.service_name,
                                "success": True
                            })
                        
                        return True
                    else:
                        raise ConnectionError(f"Traefik API returned status {response.status_code}")
                except asyncio.TimeoutError:
                    error_msg = f"Traefik connection timeout for '{self.service_name}' - Traefik is CRITICAL infrastructure and must be available"
                    self.logger.error(f"❌ {error_msg}")
                    self.is_connected = False
                    raise ConnectionError(error_msg)
        except ConnectionError:
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
                self.logger.error(f"❌ Traefik connection failed for '{self.service_name}' - Traefik is CRITICAL infrastructure: {e}")
            self.is_connected = False
            raise ConnectionError(f"Traefik connection failed for '{self.service_name}': {e}")

    async def discover_routes(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover routes from Traefik API.
        
        Routes are primarily managed via Docker labels, but this method provides
        programmatic access to discover what routes are currently registered.
        
        Args:
            service_name: Optional service name to filter routes
            
        Returns:
            List of route dictionaries with service, router, and rule information
        """
        if not self.is_connected:
            await self.connect()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get HTTP routers
                routers_response = await client.get(f"{self.traefik_api_url}/api/http/routers")
                routers_response.raise_for_status()
                routers = routers_response.json()
                
                # Get HTTP services
                services_response = await client.get(f"{self.traefik_api_url}/api/http/services")
                services_response.raise_for_status()
                services = services_response.json()
                
                # Combine router and service information
                routes = []
                for router in routers:
                    router_name = router.get("name", "")
                    service_name_filter = router.get("service", "")
                    
                    # Filter by service name if provided
                    if service_name and service_name_filter != service_name:
                        continue
                    
                    # Find matching service
                    service_info = next((s for s in services if s.get("name") == service_name_filter), None)
                    
                    route_info = {
                        "router": router_name,
                        "service": service_name_filter,
                        "rule": router.get("rule", ""),
                        "entrypoints": router.get("entryPoints", []),
                        "middlewares": router.get("middlewares", []),
                        "status": router.get("status", ""),
                        "service_info": service_info
                    }
                    routes.append(route_info)
                
                self.logger.debug(f"✅ Discovered {len(routes)} routes from Traefik")
                return routes
                
        except Exception as e:
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "discover_routes",
                    "service": self.service_name,
                    "filter": service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to discover routes from Traefik: {e}")
            return []

    async def get_service_routes(self, service_name: str) -> List[Dict[str, Any]]:
        """
        Get all routes for a specific service.
        
        Args:
            service_name: Service name to get routes for
            
        Returns:
            List of route dictionaries for the service
        """
        return await self.discover_routes(service_name=service_name)

    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Get health status for a service via Traefik.
        
        Args:
            service_name: Service name to check health for
            
        Returns:
            Dictionary with health status information
        """
        if not self.is_connected:
            await self.connect()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get HTTP services
                services_response = await client.get(f"{self.traefik_api_url}/api/http/services")
                services_response.raise_for_status()
                services = services_response.json()
                
                # Find service
                service_info = next((s for s in services if s.get("name") == service_name), None)
                
                if not service_info:
                    return {
                        "service": service_name,
                        "status": "not_found",
                        "healthy": False
                    }
                
                # Check server status
                servers = service_info.get("serverStatus", {})
                healthy_servers = sum(1 for status in servers.values() if status == "UP")
                total_servers = len(servers)
                
                return {
                    "service": service_name,
                    "status": "healthy" if healthy_servers > 0 else "unhealthy",
                    "healthy": healthy_servers > 0,
                    "servers": {
                        "total": total_servers,
                        "healthy": healthy_servers,
                        "unhealthy": total_servers - healthy_servers
                    },
                    "server_status": servers
                }
                
        except Exception as e:
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_service_health",
                    "service": self.service_name,
                    "target_service": service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to get health for service '{service_name}' from Traefik: {e}")
            return {
                "service": service_name,
                "status": "error",
                "healthy": False,
                "error": str(e)
            }

    async def get_dashboard_info(self) -> Dict[str, Any]:
        """
        Get Traefik dashboard information.
        
        Returns:
            Dictionary with dashboard URL and version information
        """
        if not self.is_connected:
            await self.connect()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get version info
                version_response = await client.get(f"{self.traefik_api_url}/api/version")
                version_response.raise_for_status()
                version_info = version_response.json()
                
                return {
                    "dashboard_url": f"{self.traefik_api_url}/dashboard/",
                    "api_url": f"{self.traefik_api_url}/api",
                    "version": version_info.get("version", "unknown"),
                    "codename": version_info.get("codename", "unknown")
                }
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get Traefik dashboard info: {e}")
            return {
                "dashboard_url": f"{self.traefik_api_url}/dashboard/",
                "api_url": f"{self.traefik_api_url}/api",
                "version": "unknown",
                "error": str(e)
            }

