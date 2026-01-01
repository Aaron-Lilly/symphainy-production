#!/usr/bin/env python3
"""
Route Registry Service

Tracks routes centrally in Curator's endpoint registry for discovery and service mesh evolution.
Routes are DEFINED by domains (when registering capabilities/SOA APIs), but TRACKED centrally by Curator.

WHAT (Service Role): I need to track routes centrally for discovery and service mesh evolution
HOW (Service Implementation): I maintain an endpoint registry that tracks all routes with domain attribution
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase

# Import utilities directly
from utilities import (
    ValidationUtility, SerializationUtility, ConfigurationUtility,
    HealthManagementUtility
)


class RouteRegistryService(FoundationServiceBase):
    """
    Route Registry Service - Central route tracking (endpoint registry)
    
    Tracks routes centrally in Curator's endpoint registry. Routes are defined
    by domains (when registering capabilities/SOA APIs), but tracked centrally
    by Curator for discovery and service mesh evolution.
    
    WHAT (Service Role): I need to track routes centrally for discovery and service mesh evolution
    HOW (Service Implementation): I maintain an endpoint registry that tracks all routes with domain attribution
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        """Initialize Route Registry Service."""
        super().__init__("route_registry", di_container)
        
        # Store public works foundation reference
        self.public_works_foundation = public_works_foundation
        
        # Endpoint registry: route_id -> route_metadata
        self.route_registry: Dict[str, Dict[str, Any]] = {}
        
        # Indexes for fast lookup
        self.routes_by_pillar: Dict[str, List[str]] = {}  # pillar -> [route_ids]
        self.routes_by_realm: Dict[str, List[str]] = {}  # realm -> [route_ids]
        self.routes_by_service: Dict[str, List[str]] = {}  # service_name -> [route_ids]
        
        self.logger.info("📋 Route Registry Service initialized")
    
    async def initialize(self):
        """Initialize the Route Registry Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("route_registry_initialize_start", success=True)
            
            await super().initialize()
            self.logger.info("🚀 Initializing Route Registry Service...")
            
            self.logger.info("✅ Route Registry Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("route_registry_initialized", 1.0, {"service": "route_registry"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("route_registry_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "route_registry_initialize")
            raise
    
    async def register_route(
        self,
        route_metadata: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> bool:
        """
        Register a route in Curator's endpoint registry.
        
        Routes are DEFINED by domains (when registering capabilities/SOA APIs),
        but TRACKED centrally by Curator (endpoint registry for discovery).
        
        Args:
            route_metadata: Route metadata dictionary
            user_context: Optional user context for security and tenant validation
        
        Route metadata format:
        {
            "route_id": "...",
            "path": "/api/v1/content-pillar/upload-file",
            "method": "POST",
            "pillar": "content-pillar",
            "realm": "business_enablement",
            "service_name": "FileParserService",
            "capability_name": "file_parsing",
            "handler": "parse_file",
            "description": "...",
            "version": "v1",
            "defined_by": "business_enablement_realm"  # Domain that defined this route
        }
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "register_route_start",
                success=True,
                details={"route_id": route_metadata.get("route_id")}
            )
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "route_registry", "write"):
                        await self.record_health_metric("register_route_access_denied", 1.0, {"route_id": route_metadata.get("route_id")})
                        await self.log_operation_with_telemetry("register_route_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_route_tenant_denied", 1.0, {"route_id": route_metadata.get("route_id"), "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_route_complete", success=False)
                            return False
            
            # Validate required fields
            route_id = route_metadata.get("route_id")
            if not route_id:
                raise ValueError("route_id is required in route_metadata")
            
            path = route_metadata.get("path")
            if not path:
                raise ValueError("path is required in route_metadata")
            
            # Add registration timestamp
            route_metadata["registered_at"] = datetime.utcnow().isoformat()
            route_metadata["user_context"] = user_context
            
            # Store route in endpoint registry
            self.route_registry[route_id] = route_metadata
            
            # Update indexes for fast lookup
            pillar = route_metadata.get("pillar")
            if pillar:
                if pillar not in self.routes_by_pillar:
                    self.routes_by_pillar[pillar] = []
                if route_id not in self.routes_by_pillar[pillar]:
                    self.routes_by_pillar[pillar].append(route_id)
            
            realm = route_metadata.get("realm")
            if realm:
                if realm not in self.routes_by_realm:
                    self.routes_by_realm[realm] = []
                if route_id not in self.routes_by_realm[realm]:
                    self.routes_by_realm[realm].append(route_id)
            
            service_name = route_metadata.get("service_name")
            if service_name:
                if service_name not in self.routes_by_service:
                    self.routes_by_service[service_name] = []
                if route_id not in self.routes_by_service[service_name]:
                    self.routes_by_service[service_name].append(route_id)
            
            self.logger.info(f"✅ Route registered: {path} ({route_id})")
            
            # Record health metric
            await self.record_health_metric(
                "route_registered",
                1.0,
                {"route_id": route_id, "path": path, "pillar": pillar, "realm": realm}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "register_route_complete",
                success=True,
                details={"route_id": route_id, "path": path}
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(
                e,
                "register_route",
                details={"route_metadata": route_metadata}
            )
            return False
    
    async def discover_routes(
        self,
        pillar: str = None,
        realm: str = None,
        service_name: str = None,
        user_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover routes from endpoint registry.
        
        Returns routes tracked in Curator's endpoint registry.
        Used for route discovery and service mesh evolution.
        
        Args:
            pillar: Optional pillar filter (e.g., "content-pillar")
            realm: Optional realm filter (e.g., "business_enablement")
            service_name: Optional service name filter
        
        Returns:
            List of route metadata dictionaries
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "discover_routes_start",
                success=True,
                details={"pillar": pillar, "realm": realm, "service_name": service_name}
            )
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "route_registry", "read"):
                        await self.record_health_metric("discover_routes_access_denied", 1.0, {"pillar": pillar or "all", "realm": realm or "all"})
                        await self.log_operation_with_telemetry("discover_routes_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_routes_tenant_denied", 1.0, {"pillar": pillar or "all", "realm": realm or "all", "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_routes_complete", success=False)
                            return []
            
            # Get route IDs based on filters
            route_ids = set()
            
            if pillar:
                route_ids.update(self.routes_by_pillar.get(pillar, []))
            
            if realm:
                realm_routes = self.routes_by_realm.get(realm, [])
                if route_ids:
                    route_ids = route_ids.intersection(set(realm_routes))
                else:
                    route_ids.update(realm_routes)
            
            if service_name:
                service_routes = self.routes_by_service.get(service_name, [])
                if route_ids:
                    route_ids = route_ids.intersection(set(service_routes))
                else:
                    route_ids.update(service_routes)
            
            # If no filters, return all routes
            if not route_ids and not pillar and not realm and not service_name:
                route_ids = set(self.route_registry.keys())
            
            # Get route metadata
            routes = []
            for route_id in route_ids:
                if route_id in self.route_registry:
                    routes.append(self.route_registry[route_id])
            
            # Record success metric
            await self.record_health_metric("discover_routes_success", 1.0, {
                "routes_count": len(routes),
                "pillar": pillar or "all",
                "realm": realm or "all",
                "service_name": service_name or "all"
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "discover_routes_complete",
                success=True,
                details={"count": len(routes)}
            )
            
            return routes
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(
                e,
                "discover_routes",
                details={"pillar": pillar, "realm": realm, "service_name": service_name}
            )
            return []
    
    async def get_route(
        self,
        route_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific route by route_id.
        
        Args:
            route_id: Route identifier
        
        Returns:
            Route metadata or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_route_start", success=True)
            
            result = self.route_registry.get(route_id)
            
            # Record success metric
            await self.record_health_metric("get_route_success", 1.0, {"route_id": route_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_route_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_route")
            self.logger.error(f"❌ Failed to get route: {e}")
            return None

