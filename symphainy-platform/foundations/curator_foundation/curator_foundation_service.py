#!/usr/bin/env python3
"""
Curator Foundation Service

Platform-wide pattern enforcement and registry management service that coordinates
8 focused micro-services (4 core + 4 agentic) for comprehensive platform governance.

WHAT (Foundation Role): I provide platform-wide pattern enforcement, registry management, and agentic coordination
HOW (Foundation Service): I coordinate specialized micro-services for comprehensive platform governance including agentic capabilities
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from bases.foundation_service_base import FoundationServiceBase

# Import core micro-services
from .services import (
    CapabilityRegistryService,
    PatternValidationService,
    AntiPatternDetectionService,
    DocumentationGenerationService,
    ServiceProtocolRegistryService,
    RouteRegistryService,
    ServiceMeshMetadataReporterService
)

# Import agentic micro-services
from .services.agent_capability_registry_service import AgentCapabilityRegistryService
from .services.agent_specialization_management_service import AgentSpecializationManagementService
from .services.agui_schema_documentation_service import AGUISchemaDocumentationService
from .services.agent_health_monitoring_service import AgentHealthMonitoringService

# Import SOA Client Service (moved from Communication Foundation)
from .services.soa_client_service import SOAClientService

# Import models from micro-modules
from .models import CapabilityDefinition, PatternDefinition, AntiPatternViolation


class ServiceState(str, Enum):
    """Service lifecycle states for registry management."""
    ACTIVE = "active"           # Service is running and accepting requests
    INACTIVE = "inactive"       # Service is stopped but registered
    MAINTENANCE = "maintenance" # Service is in maintenance mode
    DEPRECATED = "deprecated"   # Service is deprecated (will be removed)
    DRAINING = "draining"       # Service is shutting down (draining connections)


class CapabilityState(str, Enum):
    """Capability lifecycle states for registry management."""
    ACTIVE = "active"           # Capability is available and working
    DEPRECATED = "deprecated"   # Capability is deprecated (will be removed)
    MAINTENANCE = "maintenance" # Capability is in maintenance mode
    EXPERIMENTAL = "experimental" # Capability is experimental (use with caution)


class CuratorFoundationService(FoundationServiceBase):
    """
    Curator Foundation Service
    
    Coordinates 8 specialized micro-services to provide comprehensive platform governance
    including full agentic dimension management. This service acts as a coordinator and 
    provides access to focused micro-services.
    
    Core Micro-Services:
    - CapabilityRegistryService: Service capability registration and discovery
    - PatternValidationService: Architectural pattern validation and rule enforcement
    - AntiPatternDetectionService: Code scanning and violation tracking
    - DocumentationGenerationService: OpenAPI and documentation generation
    
    Agentic Micro-Services:
    - AgentCapabilityRegistryService: Real-time agent capability reporting and management
    - AgentSpecializationManagementService: Agent specialization registration and management
    - AGUISchemaDocumentationService: AGUI schema documentation generation
    - AgentHealthMonitoringService: Agent-specific health monitoring and operational status
    
    WHAT (Foundation Role): I coordinate platform-wide pattern enforcement, registry management, and agentic coordination
    HOW (Foundation Service): I coordinate specialized micro-services for comprehensive platform governance including agentic capabilities
    """
    
    def __init__(self, foundation_services: DIContainerService, 
                 public_works_foundation: Optional[PublicWorksFoundationService] = None):
        """Initialize Curator Foundation Service."""
        # Initialize base class with DI container
        super().__init__(
            service_name="curator_foundation",
            di_container=foundation_services,
            security_provider=None,
            authorization_guard=None
        )
        
        self.foundation_services = foundation_services
        self.public_works_foundation = public_works_foundation
        
        # Initialize core micro-services with proper utilities
        self.capability_registry = CapabilityRegistryService(
            foundation_services, public_works_foundation
        )
        self.pattern_validation = PatternValidationService(foundation_services)
        self.antipattern_detection = AntiPatternDetectionService(foundation_services)
        self.documentation_generation = DocumentationGenerationService(
            foundation_services, self.capability_registry
        )
        
        # Initialize new micro-services (Phase 2 refactoring)
        self.service_protocol_registry = ServiceProtocolRegistryService(
            foundation_services, public_works_foundation
        )
        self.route_registry = RouteRegistryService(
            foundation_services, public_works_foundation
        )
        self.service_mesh_metadata_reporter = ServiceMeshMetadataReporterService(
            foundation_services, public_works_foundation
        )
        
        # Initialize agentic micro-services
        self.agent_capability_registry = AgentCapabilityRegistryService(
            foundation_services, public_works_foundation
        )
        self.agent_specialization_management = AgentSpecializationManagementService(
            foundation_services, public_works_foundation
        )
        self.agui_schema_documentation = AGUISchemaDocumentationService(
            foundation_services, public_works_foundation
        )
        self.agent_health_monitoring = AgentHealthMonitoringService(
            foundation_services, public_works_foundation
        )
        
        # Initialize SOA Client Service (moved from Communication Foundation)
        self.soa_client = SOAClientService(
            foundation_services, self  # Pass self as curator_foundation reference
        )
        
        # Auto-Discovery Service (cloud-ready)
        from utilities.configuration.cloud_ready_config import get_cloud_ready_config
        cloud_ready_config = get_cloud_ready_config()
        
        if cloud_ready_config.should_use_auto_discovery():
            from .services.auto_discovery_service import AutoDiscoveryService
            self.auto_discovery = AutoDiscoveryService(
                di_container=foundation_services,
                curator_foundation=self
            )
            self.logger.info("✅ Auto-Discovery Service enabled (cloud-ready mode)")
        else:
            self.auto_discovery = None
            self.logger.info("✅ Auto-Discovery Service disabled (current mode)")
        
        # Service Discovery (delegated to Public Works Foundation)
        self.service_discovery = None  # Will be initialized from Public Works
        
        # Service registration cache (for fast local lookups)
        # Public Works/Consul is the source of truth, this is just a cache
        self.registered_services: Dict[str, Dict[str, Any]] = {}
        
        # SOA API and MCP Tool registries (NEW - Week 2 Enhancement)
        self.soa_api_registry: Dict[str, Dict[str, Any]] = {}
        self.mcp_tool_registry: Dict[str, Dict[str, Any]] = {}
        
        # Artifact registry (NEW - Phase 1, Week 2: Artifact Discovery)
        # Stores artifacts for discovery (Solution and Journey artifacts)
        self.artifact_registry: Dict[str, Dict[str, Any]] = {}  # artifact_id -> artifact_data
        
        self.is_initialized = False
        
        self.logger.info("🏛️ Curator Foundation Service initialized as Platform Registry Coordinator")
    
    async def initialize(self):
        """Initialize the Curator Foundation Service and all micro-services."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("curator_foundation_initialize_start", success=True)
            
            self.logger.info("🚀 Initializing Curator Foundation Service...")
            
            # PHASE 1: Get Service Discovery from Public Works Foundation
            if self.public_works_foundation:
                try:
                    self.service_discovery = self.public_works_foundation.get_abstraction("service_discovery")
                    self.logger.info("✅ Service discovery obtained from Public Works Foundation (Consul DNA)")
                except Exception as e:
                    # Use enhanced error handling with audit
                    await self.handle_error_with_audit(e, "curator_foundation_initialize_service_discovery")
                    self.logger.warning(f"⚠️ Could not get service discovery from Public Works: {e}")
                    self.logger.warning("⚠️ Curator will operate without service mesh capabilities")
                    self.service_discovery = None
            else:
                self.logger.warning("⚠️ Public Works Foundation not available - no service discovery")
                self.service_discovery = None
            
            # PHASE 2: Initialize core micro-services
            await self.capability_registry.initialize()
            await self.pattern_validation.initialize()
            await self.antipattern_detection.initialize()
            await self.documentation_generation.initialize()
            
            # PHASE 2.5: Initialize new micro-services (Phase 2 refactoring)
            await self.service_protocol_registry.initialize()
            await self.route_registry.initialize()
            await self.service_mesh_metadata_reporter.initialize()
            
            # PHASE 3: Initialize agentic micro-services
            await self.agent_capability_registry.initialize()
            await self.agent_specialization_management.initialize()
            await self.agui_schema_documentation.initialize()
            await self.agent_health_monitoring.initialize()
            
            # PHASE 3.5: Initialize SOA Client Service (moved from Communication Foundation)
            await self.soa_client.initialize()
            
            # PHASE 3.6: Initialize Auto-Discovery Service (cloud-ready)
            if self.auto_discovery:
                await self.auto_discovery.initialize()
                # Run auto-discovery
                discovered_services = await self.auto_discovery.discover_all_services()
                if discovered_services:
                    registration_results = await self.auto_discovery.register_discovered_services(discovered_services)
                    self.logger.info(f"✅ Auto-discovery completed: {len(registration_results.get('registered', []))} services discovered")
            
            # PHASE 4: Register with Public Works Foundation if available
            if self.public_works_foundation:
                # TODO: Implement register_foundation_capabilities method in Public Works Foundation
                # await self._register_with_public_works()
                self.logger.info("ℹ️ Skipping Public Works Foundation registration (method not implemented)")
            
            # PHASE 5: Register agentic capabilities (agents need to register their capabilities)
            await self._register_agentic_capabilities()
            
            self.is_initialized = True
            self.logger.info("✅ Curator Foundation Service initialized successfully (using Public Works service discovery)")
            
            # Record health metric
            await self.record_health_metric("curator_foundation_initialized", 1.0, {"service": "curator_foundation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("curator_foundation_initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "curator_foundation_initialize")
            self.logger.error(f"❌ Failed to initialize Curator Foundation Service: {e}")
            raise
    
    
    
    async def _register_agentic_capabilities(self):
        """Register agentic-specific capabilities."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_agentic_capabilities_start", success=True)
            
            # Register agentic capabilities with the capability registry
            agentic_capabilities = [
                {
                    "name": "agent_capability_reporting",
                    "interface": "IAgentCapabilityRegistry",
                    "endpoints": [],
                    "tools": [],
                    "type": "agentic",
                    "description": "Real-time agent capability reporting and management",
                    "version": "1.0.0",
                    "status": "active",
                    "realm": "curator"
                },
                {
                    "name": "agent_specialization_management",
                    "interface": "IAgentSpecializationManagement",
                    "endpoints": [],
                    "tools": [],
                    "type": "agentic",
                    "description": "Agent specialization registration and management",
                    "version": "1.0.0",
                    "status": "active",
                    "realm": "curator"
                },
                {
                    "name": "agui_schema_documentation",
                    "interface": "IAGUISchemaDocumentation",
                    "endpoints": [],
                    "tools": [],
                    "type": "agentic",
                    "description": "AGUI schema documentation generation",
                    "version": "1.0.0",
                    "status": "active",
                    "realm": "curator"
                },
                {
                    "name": "agent_health_monitoring",
                    "interface": "IAgentHealthMonitoring",
                    "endpoints": [],
                    "tools": [],
                    "type": "agentic",
                    "description": "Agent health monitoring and operational status tracking",
                    "version": "1.0.0",
                    "status": "active",
                    "realm": "curator"
                }
            ]
            
            for capability in agentic_capabilities:
                await self.capability_registry.register_capability(capability["name"], capability)
            
            self.logger.info("✅ Registered agentic capabilities with Curator Foundation")
            
            # Record health metric
            await self.record_health_metric("register_agentic_capabilities_success", 1.0, {"capabilities_count": len(agentic_capabilities)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_agentic_capabilities_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_agentic_capabilities")
            self.logger.error(f"Failed to register agentic capabilities: {e}")
            raise
    
    # ============================================================================
    # SERVICE REGISTRATION API (Following Remediation Plan Pattern)
    # ============================================================================
    
    async def register_service(self, service_instance, service_metadata: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a service with the Curator Foundation via Consul.
        
        This method registers services in Consul (source of truth) and maintains
        a local cache for fast lookups. Consul enables service mesh evolution.
        
        Args:
            service_instance: The service instance to register
            service_metadata: Service metadata including capabilities, endpoints, etc.
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with registration result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_service_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    # Check if user has permission to register services
                    if not await security.check_permissions(user_context, "service_registry", "write"):
                        await self.record_health_metric("register_service_access_denied", 1.0, {"service_name": service_metadata.get("service_name")})
                        await self.log_operation_with_telemetry("register_service_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_service_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_service_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            service_name = service_metadata.get("service_name")
            if not service_name:
                return {"success": False, "error": "Service name is required", "error_code": "MISSING_SERVICE_NAME"}
            
            # Check local cache first (fast path)
            if service_name in self.registered_services:
                self.logger.info(f"ℹ️ Service {service_name} already in cache")
                await self.record_health_metric("register_service_cached", 1.0, {"service_name": service_name})
                await self.log_operation_with_telemetry("register_service_complete", success=True)
                return {"success": True, "message": "Service already registered", "registration_id": service_name}
            
            # Validate service metadata
            validation_result = await self._validate_service_metadata(service_metadata)
            if not validation_result["valid"]:
                return {"success": False, "error": f"Invalid service metadata: {validation_result['errors']}", "error_code": "INVALID_METADATA"}
            
            # Register service capabilities with Capability Registry
            capabilities = service_metadata.get("capabilities", [])
            for capability_name in capabilities:
                # Convert string capability to dict format expected by CapabilityRegistryService
                # REQUIRED fields: interface, endpoints, tools (validated by _validate_capability_structure)
                capability_dict = {
                    "name": capability_name,
                    "interface": f"I{service_name}",
                    "service_type": service_metadata.get("service_type", "unknown"),
                    "endpoints": [],  # Required by validation
                    "tools": []  # Required by validation
                }
                await self.capability_registry.register_capability(service_name, capability_dict)
            
            # Register with service discovery (via Public Works Foundation)
            # CRITICAL: Service discovery registration is OPTIONAL - cache registration is PRIMARY
            # If service discovery fails, we still register in cache (cache-only mode is valid)
            service_id = None
            if self.service_discovery:
                try:
                    # Prepare service info for service discovery registration
                    # Ensure all values are serializable (no thread locks, no complex objects)
                    service_info = {
                        "service_name": service_name,
                        "service_type": service_metadata.get("service_type", "unknown"),
                        "address": service_metadata.get("address", "localhost"),
                        "port": service_metadata.get("port", 8000),
                        "tags": service_metadata.get("tags", []),
                        "capabilities": [str(c) if not isinstance(c, str) else c for c in capabilities],  # Ensure all capabilities are strings
                        "endpoints": [str(e) if not isinstance(e, str) else e for e in service_metadata.get("endpoints", [])],  # Ensure all endpoints are strings
                        "realm": service_metadata.get("realm", "unknown"),
                        "health_check_endpoint": service_metadata.get("health_check_endpoint")
                    }
                    
                    # Register with service discovery (Consul/Istio/Linkerd via Public Works)
                    registration = await self.service_discovery.register_service(service_info)
                    if not registration:
                        self.logger.warning(f"⚠️ Service discovery registration failed for {service_name}, continuing with local cache only")
                    else:
                        # Extract service_id from registration result
                        service_id = registration.service_id if hasattr(registration, 'service_id') else None
                        if not service_id:
                            # Fallback: generate service_id from service_info
                            service_id = f"{service_name}-{service_info.get('address', 'localhost')}-{service_info.get('port', 8000)}"
                        self.logger.info(f"✅ Service {service_name} registered with service discovery (via Public Works) - ID: {service_id}")
                except Exception as e:
                    # Service discovery registration failed - log but continue with cache registration
                    # This is expected in cache-only mode or when service discovery is unavailable
                    self.logger.warning(f"⚠️ Service discovery registration failed for {service_name}: {e}")
                    self.logger.debug(f"   Continuing with local cache registration (cache-only mode)")
                    service_id = None
            else:
                self.logger.warning(f"⚠️ Service discovery not available, using local cache only for {service_name}")
            
            # Update local cache (provides fast lookups while service discovery is source of truth)
            self.registered_services[service_name] = {
                "service_instance": service_instance,
                "metadata": service_metadata,
                "service_id": service_id,  # Store service_id for deregistration
                "registered_at": self._get_current_timestamp(),
                "status": ServiceState.ACTIVE.value
            }
            
            # Log registration
            self.logger.info(f"✅ Registered service {service_name} with Curator Foundation (service discovery + cache)")
            
            # Record health metric
            await self.record_health_metric("register_service_success", 1.0, {"service_name": service_name, "capabilities_count": len(capabilities)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_service_complete", success=True)
            
            return {
                "success": True,
                "registration_id": service_name,
                "message": f"Service {service_name} registered successfully"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_service")
            self.logger.error(f"Failed to register service: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def _validate_service_metadata(self, service_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate service metadata (Phase 2 refactoring - aligned with current architecture).
        
        Current architecture supports flexible service metadata formats:
        - Services may provide: service_name, service_type, realm, capabilities
        - service_type can be any string (e.g., "content_processing", "health_monitor")
        - realm is separate from service_type (e.g., "smart_city")
        - capabilities can be list of strings OR dict with detailed_capabilities
        - Services may also include: soa_api_exposure, mcp_server_integration, infrastructure_connections
        
        Validation is permissive - only service_name is required.
        """
        try:
            errors = []
            warnings = []
            
            # Only service_name is truly required
            service_name = service_metadata.get("service_name")
            if not service_name:
                errors.append("Missing required field: 'service_name' (unique service identifier)")
            elif not isinstance(service_name, str):
                errors.append(f"Field 'service_name' must be a string, got {type(service_name).__name__}")
            elif not service_name.strip():
                errors.append("Field 'service_name' cannot be empty")
            
            # Validate capabilities if present (flexible format)
            capabilities = service_metadata.get("capabilities")
            if capabilities is not None:
                # Can be list of strings, list of dicts, or dict with detailed_capabilities
                if not isinstance(capabilities, (list, dict)):
                    errors.append(f"Field 'capabilities' must be a list or dict, got {type(capabilities).__name__}")
                elif isinstance(capabilities, list):
                    # List can contain strings or dicts
                    for i, cap in enumerate(capabilities):
                        if not isinstance(cap, (str, dict)):
                            errors.append(f"Capability at index {i} must be a string or dict, got {type(cap).__name__}")
                elif isinstance(capabilities, dict):
                    # Dict format is valid (e.g., {"knowledge_management": {...}})
                    pass
            
            # Validate realm if present (should be string, validate format)
            realm = service_metadata.get("realm")
            if realm is not None:
                if not isinstance(realm, str):
                    errors.append(f"Field 'realm' must be a string, got {type(realm).__name__}")
                elif realm.strip():
                    # Validate realm format (should be valid realm name)
                    valid_realms = ["smart_city", "business_enablement", "journey", "solution", "experience", "agentic"]
                    if realm not in valid_realms:
                        warnings.append(f"Realm '{realm}' is not a standard realm name (expected one of: {', '.join(valid_realms)})")
            
            # Validate service_type if present (can be any string, not restricted)
            service_type = service_metadata.get("service_type")
            if service_type is not None:
                if not isinstance(service_type, str):
                    errors.append(f"Field 'service_type' must be a string, got {type(service_type).__name__}")
                # No restriction on service_type values (can be any string like "content_processing", "health_monitor", etc.)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate service metadata: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }
    
    async def unregister_service(
        self,
        service_name: str,
        service_id: Optional[str] = None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Unregister a service from the Curator Foundation.
        
        This method properly deregisters services from Consul (via ServiceDiscoveryAbstraction)
        and removes them from local cache and capability registry.
        
        Args:
            service_name: Name of the service to unregister
            service_id: Optional specific service instance ID (if not provided, uses stored service_id)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with unregistration result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("unregister_service_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "service_registry", "write"):
                        await self.record_health_metric("unregister_service_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("unregister_service_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            if service_name not in self.registered_services:
                return {"success": False, "error": "Service not registered", "error_code": "SERVICE_NOT_FOUND"}
            
            # Get service_id from cache if not provided
            cached_service = self.registered_services[service_name]
            if not service_id:
                service_id = cached_service.get("service_id")
            
            # 1. Deregister from Consul (via ServiceDiscoveryAbstraction)
            if self.service_discovery and service_id:
                try:
                    success = await self.service_discovery.unregister_service(service_id)
                    if success:
                        self.logger.info(f"✅ Deregistered service {service_name} (ID: {service_id}) from Consul")
                    else:
                        self.logger.warning(f"⚠️ Failed to deregister service {service_name} from Consul, continuing with local cleanup")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error deregistering from Consul: {e}, continuing with local cleanup")
            else:
                if not self.service_discovery:
                    self.logger.warning(f"⚠️ Service discovery not available, skipping Consul deregistration for {service_name}")
                if not service_id:
                    self.logger.warning(f"⚠️ Service ID not available, skipping Consul deregistration for {service_name}")
            
            # 2. Remove from capability registry (unregister all capabilities for service)
            try:
                # Use new unregister_capability() method which supports individual or all capabilities
                unregister_result = await self.unregister_capability(service_name, None, user_context)
                if not unregister_result.get("success", False):
                    self.logger.warning(f"⚠️ Error unregistering capabilities for {service_name}: {unregister_result.get('error')}")
            except Exception as e:
                self.logger.warning(f"⚠️ Error unregistering capabilities for {service_name}: {e}")
            
            # 3. Remove from local cache
            del self.registered_services[service_name]
            
            self.logger.info(f"✅ Unregistered service {service_name} from Curator Foundation (Consul + cache + capabilities)")
            
            # Record health metric
            await self.record_health_metric("unregister_service_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("unregister_service_complete", success=True)
            
            return {
                "success": True,
                "message": f"Service {service_name} unregistered successfully"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "unregister_service")
            self.logger.error(f"Failed to unregister service {service_name}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def update_service(
        self,
        service_name: str,
        updates: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Update service registration metadata.
        
        This method allows services to update their registration information without
        re-registering. Updates are applied to both Consul (via ServiceDiscoveryAbstraction)
        and local cache.
        
        Args:
            service_name: Name of the service to update
            updates: Dictionary of fields to update (capabilities, endpoints, metadata, etc.)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with update result
        
        Example:
            await curator.update_service(
                "MyService",
                {
                    "capabilities": ["new_capability"],
                    "version": "2.0.0",
                    "tags": ["updated", "v2"]
                }
            )
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("update_service_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "service_registry", "write"):
                        await self.record_health_metric("update_service_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("update_service_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Validate service exists
            if service_name not in self.registered_services:
                return {"success": False, "error": "Service not registered", "error_code": "SERVICE_NOT_FOUND"}
            
            # Get current registration
            current_registration = self.registered_services[service_name]
            current_metadata = current_registration["metadata"]
            service_id = current_registration.get("service_id")
            
            # Merge updates with current metadata
            updated_metadata = {**current_metadata, **updates}
            
            # Update in Consul (re-register with updated metadata)
            if self.service_discovery and service_id:
                try:
                    # Prepare updated service info for re-registration
                    service_info = {
                        "service_name": service_name,
                        "service_id": service_id,  # Keep same service_id
                        "service_type": updated_metadata.get("service_type", current_metadata.get("service_type", "unknown")),
                        "address": updated_metadata.get("address", current_metadata.get("address", "localhost")),
                        "port": updated_metadata.get("port", current_metadata.get("port", 8000)),
                        "tags": updated_metadata.get("tags", current_metadata.get("tags", [])),
                        "capabilities": updated_metadata.get("capabilities", current_metadata.get("capabilities", [])),
                        "endpoints": updated_metadata.get("endpoints", current_metadata.get("endpoints", [])),
                        "realm": updated_metadata.get("realm", current_metadata.get("realm", "unknown")),
                        "health_check_endpoint": updated_metadata.get("health_check_endpoint", current_metadata.get("health_check_endpoint"))
                    }
                    
                    # Re-register with updated metadata (Consul supports this)
                    registration = await self.service_discovery.register_service(service_info)
                    if registration:
                        self.logger.info(f"✅ Updated service {service_name} in Consul")
                    else:
                        self.logger.warning(f"⚠️ Failed to update service {service_name} in Consul, continuing with local cache update")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error updating service in Consul: {e}, continuing with local cache update")
            else:
                if not self.service_discovery:
                    self.logger.warning(f"⚠️ Service discovery not available, updating local cache only for {service_name}")
            
            # Update local cache
            self.registered_services[service_name]["metadata"] = updated_metadata
            self.registered_services[service_name]["updated_at"] = self._get_current_timestamp()
            
            # Update capabilities if provided
            if "capabilities" in updates:
                # Unregister old capabilities and register new ones
                await self.capability_registry.unregister_capability(service_name)
                for capability_name in updates["capabilities"]:
                    capability_dict = {
                        "name": capability_name,
                        "interface": f"I{service_name}",
                        "service_type": updated_metadata.get("service_type", "unknown"),
                        "endpoints": updated_metadata.get("endpoints", []),
                        "tools": []
                    }
                    await self.capability_registry.register_capability(service_name, capability_dict)
            
            self.logger.info(f"✅ Updated service {service_name} in Curator Foundation")
            
            # Record health metric
            await self.record_health_metric("update_service_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("update_service_complete", success=True)
            
            return {
                "success": True,
                "message": f"Service {service_name} updated successfully"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "update_service")
            self.logger.error(f"Failed to update service {service_name}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def update_service_state(
        self,
        service_name: str,
        state: ServiceState,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Update service lifecycle state.
        
        This method allows services to update their lifecycle state (active, inactive,
        maintenance, deprecated, draining) without full re-registration.
        
        Args:
            service_name: Name of the service
            state: New lifecycle state (ServiceState enum)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with update result
        
        Example:
            await curator.update_service_state(
                "MyService",
                ServiceState.MAINTENANCE
            )
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("update_service_state_start", success=True)
            
            # Update service with state change
            result = await self.update_service(
                service_name,
                {
                    "state": state.value,
                    "state_updated_at": self._get_current_timestamp()
                },
                user_context
            )
            
            if result["success"]:
                # Update local cache status
                if service_name in self.registered_services:
                    self.registered_services[service_name]["status"] = state.value
                
                self.logger.info(f"✅ Updated service {service_name} state to {state.value}")
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("update_service_state_complete", success=result["success"])
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "update_service_state")
            self.logger.error(f"Failed to update service state for {service_name}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def graceful_shutdown(
        self,
        service_name: str,
        drain_period_seconds: int = 30,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Gracefully shutdown a service with drain period.
        
        This method implements graceful shutdown pattern:
        1. Mark service as "draining" (stops accepting new requests)
        2. Wait for drain period (allows existing requests to complete)
        3. Deregister from Consul
        4. Remove from local cache
        
        Args:
            service_name: Name of the service to shutdown
            drain_period_seconds: Number of seconds to wait for connections to drain (default: 30)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with shutdown result
        
        Example:
            await curator.graceful_shutdown(
                "MyService",
                drain_period_seconds=60
            )
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("graceful_shutdown_start", success=True)
            
            # 1. Mark service as "draining"
            self.logger.info(f"🛑 Marking service {service_name} as draining...")
            state_result = await self.update_service_state(service_name, ServiceState.DRAINING, user_context)
            if not state_result["success"]:
                self.logger.warning(f"⚠️ Failed to mark service {service_name} as draining, continuing with shutdown")
            
            # 2. Wait for drain period
            self.logger.info(f"⏳ Waiting {drain_period_seconds} seconds for connections to drain...")
            await asyncio.sleep(drain_period_seconds)
            
            # 3. Deregister service
            self.logger.info(f"🗑️ Deregistering service {service_name}...")
            unregister_result = await self.unregister_service(service_name, None, user_context)
            
            if unregister_result["success"]:
                self.logger.info(f"✅ Service {service_name} gracefully shutdown")
            else:
                self.logger.warning(f"⚠️ Service {service_name} shutdown completed with warnings: {unregister_result.get('error')}")
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("graceful_shutdown_complete", success=unregister_result["success"])
            
            return unregister_result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "graceful_shutdown")
            self.logger.error(f"Failed to gracefully shutdown service {service_name}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    def get_soa_client_service(self) -> SOAClientService:
        """
        Get SOA Client Service (moved from Communication Foundation).
        
        Returns:
            SOAClientService instance for inter-service communication
        """
        if not self.is_initialized:
            raise RuntimeError("Curator Foundation not initialized")
        return self.soa_client
    
    async def get_registered_services(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all registered services (filtered by tenant if user_context provided)."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_registered_services_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "service_registry", "read"):
                        await self.record_health_metric("get_registered_services_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_registered_services_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation and filtering (multi-tenant support)
            services_to_return = self.registered_services
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_registered_services_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_registered_services_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
                        # Filter services by tenant if tenant_id is in metadata
                        services_to_return = {
                            name: data for name, data in self.registered_services.items()
                            if data.get("metadata", {}).get("tenant_id") == tenant_id or not data.get("metadata", {}).get("tenant_id")
                        }
            
            result = {
                "total_services": len(services_to_return),
                "services": {
                    name: {
                        "metadata": data["metadata"],
                        "registered_at": data["registered_at"],
                        "status": data["status"],
                        "service_instance": data.get("service_instance")  # Include instance for discovery
                    }
                    for name, data in services_to_return.items()
                },
                "generated_at": self._get_current_timestamp()
            }
            
            # Record health metric
            await self.record_health_metric("get_registered_services_success", 1.0, {"total_services": len(services_to_return)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_registered_services_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_registered_services")
            self.logger.error(f"Failed to get registered services: {e}")
            return {}
    
    async def discover_agents(
        self,
        agent_type: Optional[str] = None,
        realm_name: Optional[str] = None,
        orchestrator_name: Optional[str] = None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Discover agents registered with Curator.
        
        Args:
            agent_type: Filter by agent type ("liaison", "specialist", "guide", etc.)
            realm_name: Filter by realm name
            orchestrator_name: Filter by orchestrator name
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dictionary of agent_name -> agent_info
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_agents_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_registry", "read"):
                        await self.record_health_metric("discover_agents_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("discover_agents_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_agents_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_agents_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            registered_services = await self.get_registered_services(user_context)
            services_dict = registered_services.get("services", {})
            
            agents = {}
            for service_name, service_info in services_dict.items():
                metadata = service_info.get("metadata", {})
                
                # Check if this is an agent (has agent_type in metadata or tags)
                if "agent_type" in metadata or "agent" in metadata.get("tags", []):
                    # Apply filters
                    if agent_type and metadata.get("agent_type") != agent_type:
                        continue
                    if realm_name and metadata.get("realm") != realm_name:
                        continue
                    if orchestrator_name and metadata.get("orchestrator") != orchestrator_name:
                        continue
                    
                    agents[service_name] = {
                        "agent_name": service_name,
                        "agent_type": metadata.get("agent_type", "unknown"),
                        "realm": metadata.get("realm", "unknown"),
                        "orchestrator": metadata.get("orchestrator"),
                        "capabilities": metadata.get("capabilities", []),
                        "service_instance": service_info.get("service_instance"),
                        "status": service_info.get("status", "unknown"),
                        "registered_at": service_info.get("registered_at")
                    }
            
            result = {
                "total_agents": len(agents),
                "agents": agents
            }
            
            # Record health metric
            await self.record_health_metric("discover_agents_success", 1.0, {"total_agents": len(agents)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_agents_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_agents")
            self.logger.error(f"Failed to discover agents: {e}")
            return {"total_agents": 0, "agents": {}}
    
    async def get_agent(self, agent_name: str, user_context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Get an agent instance by name from Curator registry.
        
        Args:
            agent_name: Name of the agent
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Agent instance or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_name, "read"):
                        await self.record_health_metric("get_agent_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("get_agent_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_tenant_denied", 1.0, {"agent_name": agent_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_complete", success=False)
                            return None
            
            registered_services = await self.get_registered_services(user_context)
            services_dict = registered_services.get("services", {})
            
            agent_instance = None
            if agent_name in services_dict:
                service_info = services_dict[agent_name]
                agent_instance = service_info.get("service_instance")
            
            # Record health metric
            await self.record_health_metric("get_agent_success", 1.0, {"agent_name": agent_name, "found": agent_instance is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_complete", success=True)
            
            return agent_instance
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent")
            self.logger.error(f"Failed to get agent {agent_name}: {e}")
            return None
    
    # ============================================================================
    # AGENTIC INTEGRATION API METHODS
    # ============================================================================
    
    async def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        characteristics: Dict[str, Any],
        contracts: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> bool:
        """
        Register an agent with MCP tool access pattern (Phase 2 refactoring).
        
        Agents use MCP Tools (not direct service access): Agent → MCP Tool → Service
        Services can directly access agents: Service → Agent
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            characteristics: Agent characteristics (specialization, pillar, capabilities, etc.)
            contracts: Agent contracts (MCP tools, agent API)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            bool: True if registration successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "register_agent_start",
                success=True,
                details={"agent_id": agent_id, "agent_name": agent_name}
            )
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_registry", "write"):
                        await self.record_health_metric("register_agent_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("register_agent_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_agent_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_agent_complete", success=False)
                            return False
            
            self.logger.info(f"📝 Registering agent {agent_name} with MCP tool access pattern")
            
            # Build agent_config for backward compatibility with existing methods
            agent_config = {
                "capabilities": characteristics.get("capabilities", []),
                "pillar": characteristics.get("pillar"),
                "specialization": characteristics.get("specialization"),
                "specialization_config": {
                    "specialization": characteristics.get("specialization"),
                    "pillar": characteristics.get("pillar"),
                    "required_roles": characteristics.get("required_roles", []),
                    "agui_schema": characteristics.get("agui_schema", {})
                },
                "mcp_tools": contracts.get("mcp_tools", []),  # New: MCP tool mappings
                "agent_api": contracts.get("agent_api", {})  # New: Agent API for service access
            }
            
            # Register agent capabilities
            capabilities = agent_config.get("capabilities", [])
            if capabilities:
                await self.agent_capability_registry.register_agent_capabilities(
                    agent_id, agent_name, capabilities,
                    pillar=agent_config.get("pillar"),
                    specialization=agent_config.get("specialization")
                )
            
            # Register agent specialization
            specialization_config = agent_config.get("specialization_config")
            if specialization_config:
                await self.agent_specialization_management.register_agent_specialization(
                    agent_id, agent_name, specialization_config
                )
            
            # Store MCP tool mappings (for agent → MCP tool → service access)
            # This will be used by agents to discover which MCP tools they can use
            if contracts.get("mcp_tools"):
                # Store in agent capability registry for discovery
                for mcp_tool in contracts["mcp_tools"]:
                    # Register MCP tool mapping
                    tool_name = mcp_tool.get("tool_name")
                    if tool_name:
                        # Link agent to MCP tool
                        await self.register_mcp_tool(
                            tool_name=tool_name,
                            tool_definition={
                                "agent_id": agent_id,
                                "agent_name": agent_name,
                                "mcp_server": mcp_tool.get("mcp_server"),
                                "wraps_service": mcp_tool.get("wraps_service"),
                                "wraps_method": mcp_tool.get("wraps_method")
                            },
                            metadata={
                                "agent_id": agent_id,
                                "agent_name": agent_name,
                                "access_pattern": "agent_to_service_via_mcp"
                            },
                            user_context=user_context
                        )
            
            # Generate AGUI documentation
            await self.agui_schema_documentation.generate_agent_documentation(
                agent_name, "api"
            )
            await self.agui_schema_documentation.generate_agent_documentation(
                agent_name, "user_guide"
            )
            
            # Register for health monitoring
            await self.agent_health_monitoring.register_agent_for_monitoring(
                agent_id, agent_name
            )
            
            self.logger.info(f"✅ Successfully registered agent {agent_name} with MCP tool access pattern")
            
            # Record health metric
            await self.record_health_metric("register_agent_success", 1.0, {"agent_id": agent_id, "agent_name": agent_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "register_agent_complete",
                success=True,
                details={"agent_id": agent_id, "agent_name": agent_name}
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_agent")
            self.logger.error(f"❌ Failed to register agent {agent_name}: {e}")
            return False
    
    async def register_agent_with_curator(self, agent_id: str, agent_name: str, 
                                        agent_config: Dict[str, Any], user_context: Dict[str, Any] = None) -> bool:
        """
        Register an agent with the Curator Foundation (backward compatibility wrapper).
        
        This method converts the old agent_config format to the new characteristics/contracts
        format and calls register_agent(). This maintains backward compatibility during migration.
        
        DEPRECATED: Use register_agent() directly with characteristics and contracts.
        This method will be removed after all callers are migrated.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            agent_config: Agent configuration (old format)
            user_context: Optional user context for security and tenant validation
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "register_agent_with_curator_start",
                success=True,
                details={"agent_id": agent_id, "agent_name": agent_name}
            )
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_registry", "write"):
                        await self.record_health_metric("register_agent_with_curator_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("register_agent_with_curator_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_agent_with_curator_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_agent_with_curator_complete", success=False)
                            return False
            
            # Convert old agent_config format to new characteristics/contracts format
            characteristics = {
                "capabilities": agent_config.get("capabilities", []),
                "pillar": agent_config.get("pillar"),
                "specialization": agent_config.get("specialization"),
                "required_roles": agent_config.get("specialization_config", {}).get("required_roles", []),
                "agui_schema": agent_config.get("specialization_config", {}).get("agui_schema", {})
            }
            
            contracts = {
                "mcp_tools": agent_config.get("mcp_tools", []),
                "agent_api": agent_config.get("agent_api", {})
            }
            
            # Call new register_agent() method
            result = await self.register_agent(
                agent_id=agent_id,
                agent_name=agent_name,
                characteristics=characteristics,
                contracts=contracts,
                user_context=user_context
            )
            
            # Record health metric
            await self.record_health_metric("register_agent_with_curator_success", 1.0, {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "success": result
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "register_agent_with_curator_complete",
                success=result,
                details={"agent_id": agent_id, "agent_name": agent_name}
            )
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_agent_with_curator")
            self.logger.error(f"❌ Failed to register agent {agent_name} (backward compatibility): {e}")
            return False
    
    async def discover_agents_for_capability(
        self,
        capability: str,
        user_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Services discover agents that can help with a capability.
        
        Returns agents that can be directly accessed by services (Service → Agent pattern).
        
        Args:
            capability: Capability name (e.g., "content_analysis", "file_parsing")
            user_context: Optional user context for security and tenant validation
        
        Returns:
            List of agent information dictionaries:
            [
                {
                    "agent_id": "...",
                    "agent_name": "...",
                    "agent_api": {...},  # How service calls agent directly
                    "capabilities": [...]
                }
            ]
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "discover_agents_for_capability_start",
                success=True,
                details={"capability": capability}
            )
            
            # Security validation
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_registry", "read"):
                        await self.record_health_metric("discover_agents_for_capability_access_denied", 1.0, {"capability": capability})
                        await self.log_operation_with_telemetry("discover_agents_for_capability_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_agents_for_capability_tenant_denied", 1.0, {"capability": capability, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_agents_for_capability_complete", success=False)
                            return []
            
            # Get agent capability reports
            agents = []
            
            # Search through agent capability registry
            for agent_id, agent_capabilities in self.agent_capability_registry.agent_capabilities.items():
                # Check if agent has the requested capability
                matching_capabilities = [
                    cap for cap in agent_capabilities
                    if capability.lower() in cap.capability_name.lower() or
                       capability.lower() in (cap.description or "").lower()
                ]
                
                if matching_capabilities:
                    # Get agent info
                    agent_report = await self.get_agent_curator_report(agent_id, user_context)
                    if agent_report:
                        # Extract agent API from MCP tool registry or agent config
                        agent_api = None
                        
                        # Try to find agent API from registered MCP tools
                        for tool_name, tool_data in self.mcp_tool_registry.items():
                            tool_metadata = tool_data.get("metadata", {})
                            if tool_metadata.get("agent_id") == agent_id:
                                # Agent API might be in tool definition
                                tool_def = tool_data.get("tool_definition", {})
                                if "agent_api" in tool_def:
                                    agent_api = tool_def["agent_api"]
                        
                        # If not found, use default pattern
                        if not agent_api:
                            agent_api = {
                                "endpoint": f"/api/agents/{agent_id}",
                                "method": "POST"
                            }
                        
                        agents.append({
                            "agent_id": agent_id,
                            "agent_name": agent_report.get("agent_name", agent_id),
                            "agent_api": agent_api,
                            "capabilities": [cap.capability_name for cap in matching_capabilities]
                        })
            
            # Record success metric
            await self.record_health_metric("discover_agents_for_capability_success", 1.0, {
                "capability": capability,
                "agents_count": len(agents)
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "discover_agents_for_capability_complete",
                success=True,
                details={"capability": capability, "count": len(agents)}
            )
            
            return agents
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_agents_for_capability")
            self.logger.error(f"❌ Failed to discover agents for capability {capability}: {e}")
            return []
    
    async def get_agent_curator_report(self, agent_id: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get comprehensive Curator report for an agent."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_curator_report_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "read"):
                        await self.record_health_metric("get_agent_curator_report_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("get_agent_curator_report_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_curator_report_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_curator_report_complete", success=False)
                            return None
            
            # Get capability report
            capability_report = await self.agent_capability_registry.get_agent_capability_report(agent_id)
            
            # Get specialization info
            specialization = await self.agent_specialization_management.get_agent_specialization(agent_id)
            
            # Get documentation info
            agent_name = capability_report.agent_name if capability_report else f"Agent_{agent_id}"
            documentation = await self.agui_schema_documentation.get_agent_documentation(agent_name)
            
            # Get health report
            health_report = await self.agent_health_monitoring.get_agent_health_report(agent_id)
            
            result = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "capability_report": capability_report.__dict__ if capability_report else None,
                "specialization": specialization.__dict__ if specialization else None,
                "documentation": [doc.__dict__ for doc in documentation] if documentation else [],
                "health_report": health_report.__dict__ if health_report else None,
                "generated_at": self._get_current_timestamp()
            }
            
            # Record health metric
            await self.record_health_metric("get_agent_curator_report_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_curator_report_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_curator_report")
            self.logger.error(f"Failed to generate Curator report for agent {agent_id}: {e}")
            return None
    
    async def get_agentic_dimension_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of the agentic dimension."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agentic_dimension_summary_start", success=True)
            
            # Get all agent capability reports
            capability_reports = await self.agent_capability_registry.get_all_agent_reports()
            
            # Get all specialization analytics
            specialization_analytics = await self.agent_specialization_management.get_all_specialization_analytics()
            
            # Get documentation report
            documentation_report = await self.agui_schema_documentation.get_documentation_report()
            
            # Get health summary
            health_summary = await self.agent_health_monitoring.get_health_summary()
            
            # Get capability analytics
            capability_analytics = await self.agent_capability_registry.get_capability_analytics()
            
            result = {
                "total_agents": len(capability_reports),
                "capability_summary": {
                    "total_capabilities": sum(report.total_capabilities for report in capability_reports),
                    "active_capabilities": sum(report.active_capabilities for report in capability_reports),
                    "capabilities_by_type": capability_analytics.get("type_distribution", {}),
                    "capabilities_by_pillar": capability_analytics.get("pillar_distribution", {})
                },
                "specialization_summary": {
                    "total_specializations": len(specialization_analytics),
                    "specializations_by_pillar": {spec.pillar: 1 for spec in specialization_analytics},
                    "average_success_rate": sum(spec.average_success_rate for spec in specialization_analytics) / len(specialization_analytics) if specialization_analytics else 0.0
                },
                "documentation_summary": {
                    "documentation_coverage": documentation_report.documentation_coverage,
                    "quality_score": documentation_report.quality_score,
                    "documentation_types": documentation_report.documentation_types
                },
                "health_summary": health_summary,
                "generated_at": self._get_current_timestamp()
            }
            
            # Record health metric
            await self.record_health_metric("get_agentic_dimension_summary_success", 1.0, {"total_agents": len(capability_reports)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agentic_dimension_summary_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agentic_dimension_summary")
            self.logger.error(f"Failed to generate agentic dimension summary: {e}")
            return {}
    
    # ============================================================================
    # CORE CURATOR API METHODS (Delegated to micro-services)
    # ============================================================================
    
    async def register_capability(self, capability_definition: Dict[str, Any], user_context: Dict[str, Any] = None) -> bool:
        """
        Register a capability (backward compatibility wrapper).
        
        This method converts the old dict-based format to CapabilityDefinition and calls
        register_domain_capability(). This maintains backward compatibility during migration.
        
        DEPRECATED: Use register_domain_capability() directly with CapabilityDefinition object.
        This method will be removed after all callers are migrated.
        
        Args:
            capability_definition: Capability definition dictionary (old format)
            user_context: Optional user context for security and tenant validation
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "register_capability_start",
                success=True,
                details={"service_name": capability_definition.get("service_name")}
            )
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "capability_registry", "write"):
                        await self.record_health_metric("register_capability_access_denied", 1.0, {"service_name": capability_definition.get("service_name")})
                        await self.log_operation_with_telemetry("register_capability_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_capability_tenant_denied", 1.0, {"service_name": capability_definition.get("service_name"), "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_capability_complete", success=False)
                            return False
            
            # Convert dict to CapabilityDefinition
            from .models.capability_definition import CapabilityDefinition
            
            capability = CapabilityDefinition(
                service_name=capability_definition.get("service_name", "unknown"),
                interface_name=capability_definition.get("interface_name", ""),
                endpoints=capability_definition.get("endpoints", []),
                tools=capability_definition.get("tools", []),
                description=capability_definition.get("description", ""),
                realm=capability_definition.get("realm", "unknown"),
                version=capability_definition.get("version", "1.0.0"),
                semantic_mapping=capability_definition.get("semantic_mapping"),
                contracts=capability_definition.get("contracts")
            )
            
            # Call new register_domain_capability() method
            result = await self.register_domain_capability(capability, user_context)
            
            # Record health metric
            await self.record_health_metric("register_capability_success", 1.0, {
                "service_name": capability_definition.get("service_name"),
                "success": result
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "register_capability_complete",
                success=result,
                details={"service_name": capability_definition.get("service_name")}
            )
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_capability")
            self.logger.error(f"❌ Failed to register capability (backward compatibility): {e}")
            return False
    
    async def register_domain_capability(
        self,
        capability: 'CapabilityDefinition',
        user_context: Dict[str, Any] = None
    ) -> bool:
        """
        Register a domain capability using CapabilityDefinition (extended with semantic mapping).
        
        This is the new unified method for registering capabilities with semantic mapping
        and contract mappings. Aligns with Phase 2 refactoring.
        
        Args:
            capability: CapabilityDefinition object (extended with semantic_mapping and contracts)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "register_domain_capability_start",
                success=True,
                details={"service_name": capability.service_name}
            )
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "capability_registry", "write"):
                        await self.record_health_metric(
                            "register_domain_capability_access_denied",
                            1.0,
                            {"service_name": capability.service_name}
                        )
                        await self.log_operation_with_telemetry("register_domain_capability_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric(
                                "register_domain_capability_tenant_denied",
                                1.0,
                                {"service_name": capability.service_name}
                            )
                            await self.log_operation_with_telemetry("register_domain_capability_complete", success=False)
                            return False
            
            # Register CapabilityDefinition directly with capability registry
            # Use capability_name as the key for unique identification
            capability_key = f"{capability.service_name}.{capability.capability_name}"
            result = await self.capability_registry.register_capability_definition(
                capability_key,
                capability
            )
            
            # Check if registration was successful
            success = result.get("success", False) if isinstance(result, dict) else result
            
            if success:
                # If capability has contracts with REST API, register route automatically
                if capability.contracts and capability.contracts.get("rest_api"):
                    rest_api = capability.contracts["rest_api"]
                    route_metadata = {
                        "route_id": f"{capability.service_name}_{capability.capability_name}_{rest_api.get('endpoint', '').replace('/', '_')}",
                        "path": rest_api.get("endpoint", ""),
                        "method": rest_api.get("method", "POST"),
                        "pillar": capability.semantic_mapping.get("semantic_api", "").split("/")[2] if capability.semantic_mapping and capability.semantic_mapping.get("semantic_api") else "",
                        "realm": capability.realm,
                        "service_name": capability.service_name,
                        "capability_name": capability.capability_name,
                        "protocol_name": capability.protocol_name,
                        "handler": rest_api.get("handler", ""),
                        "description": capability.description,
                        "version": capability.version,
                        "defined_by": capability.realm,
                        "contract_type": "rest_api"
                    }
                    await self.register_route(route_metadata, user_context)
                
                # Also register SOA API endpoints if present
                if capability.contracts and capability.contracts.get("soa_api"):
                    soa_api = capability.contracts["soa_api"]
                    route_metadata = {
                        "route_id": f"{capability.service_name}_{capability.capability_name}_soa_{soa_api.get('api_name', '')}",
                        "path": soa_api.get("endpoint", ""),
                        "method": soa_api.get("method", "POST"),
                        "realm": capability.realm,
                        "service_name": capability.service_name,
                        "capability_name": capability.capability_name,
                        "protocol_name": capability.protocol_name,
                        "handler": soa_api.get("handler", ""),
                        "description": capability.description,
                        "version": capability.version,
                        "defined_by": capability.realm,
                        "contract_type": "soa_api"
                    }
                    await self.register_route(route_metadata, user_context)
                
                # Record health metric
                await self.record_health_metric(
                    "register_domain_capability_success",
                    1.0,
                    {"service_name": capability.service_name}
                )
                
                # End telemetry tracking
                await self.log_operation_with_telemetry(
                    "register_domain_capability_complete",
                    success=True,
                    details={"service_name": capability.service_name}
                )
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry(
                    "register_domain_capability_complete",
                    success=False,
                    details={"service_name": capability.service_name, "error": result.get("error") if isinstance(result, dict) else "Unknown error"}
                )
            
            return success
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_domain_capability")
            raise
    
    async def update_capability(
        self,
        service_name: str,
        capability_name: str,
        updates: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Update capability metadata.
        
        This method allows services to update their capability registration information
        without re-registering. Updates are applied to the Capability Registry.
        
        Args:
            service_name: Name of the service that owns the capability
            capability_name: Name of the capability to update
            updates: Dictionary of fields to update (description, contracts, semantic_mapping, etc.)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with update result
        
        Example:
            await curator.update_capability(
                "FileParserService",
                "file_parsing",
                {
                    "description": "Updated description",
                    "contracts": {
                        "rest_api": {
                            "endpoint": "/api/v1/content-pillar/upload-file-v2",
                            "method": "POST"
                        }
                    }
                }
            )
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("update_capability_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "capability_registry", "write"):
                        await self.record_health_metric("update_capability_access_denied", 1.0, {
                            "service_name": service_name,
                            "capability_name": capability_name
                        })
                        await self.log_operation_with_telemetry("update_capability_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Get capability from registry
            capability_key = f"{service_name}.{capability_name}"
            capability = await self.capability_registry.get_capability_definition(capability_key)
            
            if not capability:
                return {
                    "success": False,
                    "error": f"Capability {capability_key} not found",
                    "error_code": "CAPABILITY_NOT_FOUND"
                }
            
            # Update capability fields
            from dataclasses import replace, fields
            from .models import CapabilityDefinition
            
            # Get all field names from CapabilityDefinition
            field_names = {f.name for f in fields(CapabilityDefinition)}
            
            # Filter updates to only include valid fields
            valid_updates = {k: v for k, v in updates.items() if k in field_names}
            
            # Use dataclasses.replace() to create updated capability
            updated_capability = replace(capability, **valid_updates)
            
            # Re-register updated capability
            result = await self.capability_registry.register_capability_definition(
                capability_key,
                updated_capability
            )
            
            if result.get("success", False):
                self.logger.info(f"✅ Updated capability {capability_key} in Curator Foundation")
                
                # Record health metric
                await self.record_health_metric("update_capability_success", 1.0, {
                    "service_name": service_name,
                    "capability_name": capability_name
                })
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("update_capability_complete", success=True)
                
                return {
                    "success": True,
                    "message": f"Capability {capability_key} updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "error_code": "UPDATE_FAILED"
                }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "update_capability")
            self.logger.error(f"Failed to update capability {service_name}.{capability_name}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def update_capability_state(
        self,
        service_name: str,
        capability_name: str,
        state: CapabilityState,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Update capability lifecycle state.
        
        This method allows services to update their capability lifecycle state
        (active, deprecated, maintenance, experimental) without full re-registration.
        
        Args:
            service_name: Name of the service that owns the capability
            capability_name: Name of the capability
            state: New lifecycle state (CapabilityState enum)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with update result
        
        Example:
            await curator.update_capability_state(
                "FileParserService",
                "file_parsing",
                CapabilityState.DEPRECATED
            )
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("update_capability_state_start", success=True)
            
            # Update capability with state change
            result = await self.update_capability(
                service_name,
                capability_name,
                {
                    "state": state.value,
                    "state_updated_at": self._get_current_timestamp()
                },
                user_context
            )
            
            if result["success"]:
                self.logger.info(f"✅ Updated capability {service_name}.{capability_name} state to {state.value}")
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("update_capability_state_complete", success=result["success"])
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "update_capability_state")
            self.logger.error(f"Failed to update capability state for {service_name}.{capability_name}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def unregister_capability(
        self,
        service_name: str,
        capability_name: Optional[str] = None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Unregister capability (individual or all for service).
        
        This method allows services to unregister individual capabilities or all
        capabilities for a service. If capability_name is None, unregisters all
        capabilities for the service.
        
        Args:
            service_name: Name of the service that owns the capability
            capability_name: Optional specific capability name (if None, unregister all)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with unregistration result
        
        Example:
            # Unregister specific capability
            await curator.unregister_capability("FileParserService", "file_parsing")
            
            # Unregister all capabilities for service
            await curator.unregister_capability("FileParserService")
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("unregister_capability_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "capability_registry", "write"):
                        await self.record_health_metric("unregister_capability_access_denied", 1.0, {
                            "service_name": service_name,
                            "capability_name": capability_name
                        })
                        await self.log_operation_with_telemetry("unregister_capability_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            if capability_name:
                # Unregister specific capability
                capability_key = f"{service_name}.{capability_name}"
                result = await self.capability_registry.unregister_capability_definition(capability_key)
                
                if result.get("success", False):
                    self.logger.info(f"✅ Unregistered capability {capability_key}")
                else:
                    self.logger.warning(f"⚠️ Failed to unregister capability {capability_key}")
                
                # Record health metric
                await self.record_health_metric("unregister_capability_success", 1.0, {
                    "service_name": service_name,
                    "capability_name": capability_name
                })
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("unregister_capability_complete", success=result.get("success", False))
                
                return result
            else:
                # Unregister all capabilities for service
                # Get all capabilities for this service
                all_capabilities = await self.capability_registry.get_capabilities_by_service(service_name)
                
                unregistered_count = 0
                failed_count = 0
                
                for capability in all_capabilities:
                    capability_key = f"{service_name}.{capability.capability_name}"
                    result = await self.capability_registry.unregister_capability_definition(capability_key)
                    if result.get("success", False):
                        unregistered_count += 1
                    else:
                        failed_count += 1
                
                self.logger.info(f"✅ Unregistered {unregistered_count} capabilities for {service_name} (failed: {failed_count})")
                
                # Record health metric
                await self.record_health_metric("unregister_capabilities_success", 1.0, {
                    "service_name": service_name,
                    "unregistered_count": unregistered_count,
                    "failed_count": failed_count
                })
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("unregister_capability_complete", success=True)
                
                return {
                    "success": True,
                    "message": f"Unregistered {unregistered_count} capabilities for {service_name}",
                    "unregistered_count": unregistered_count,
                    "failed_count": failed_count
                }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "unregister_capability")
            self.logger.error(f"Failed to unregister capability {service_name}.{capability_name if capability_name else 'all'}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def register_service_protocol(
        self,
        service_name: str,
        protocol_name: str,
        protocol: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> bool:
        """
        Register a service protocol (Python typing.Protocol).
        
        Delegates to ServiceProtocolRegistryService.
        
        Args:
            service_name: Name of the service
            protocol_name: Name of the protocol (e.g., "IFileParser")
            protocol: Protocol definition with method contracts
            user_context: Optional user context for security and tenant validation
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "register_service_protocol_start",
                success=True,
                details={"service_name": service_name, "protocol_name": protocol_name}
            )
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "protocol_registry", "write"):
                        await self.record_health_metric("register_service_protocol_access_denied", 1.0, {"service_name": service_name, "protocol_name": protocol_name})
                        await self.log_operation_with_telemetry("register_service_protocol_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_service_protocol_tenant_denied", 1.0, {"service_name": service_name, "protocol_name": protocol_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_service_protocol_complete", success=False)
                            return False
            
            result = await self.service_protocol_registry.register_service_protocol(
                service_name,
                protocol_name,
                protocol,
                user_context
            )
            
            # Record health metric
            await self.record_health_metric(
                "register_service_protocol_success",
                1.0,
                {"service_name": service_name, "protocol_name": protocol_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "register_service_protocol_complete",
                success=True,
                details={"service_name": service_name, "protocol_name": protocol_name}
            )
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_service_protocol")
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
        
        Delegates to RouteRegistryService.
        
        Args:
            route_metadata: Route metadata dictionary
            user_context: Optional user context for security and tenant validation
        
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
            
            result = await self.route_registry.register_route(route_metadata, user_context)
            
            # Record health metric
            await self.record_health_metric(
                "register_route_success",
                1.0,
                {"route_id": route_metadata.get("route_id")}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "register_route_complete",
                success=True,
                details={"route_id": route_metadata.get("route_id")}
            )
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_route")
            raise
    
    async def discover_routes(
        self,
        pillar: str = None,
        realm: str = None,
        service_name: str = None,
        user_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover routes from endpoint registry.
        
        Delegates to RouteRegistryService.
        
        Args:
            pillar: Optional pillar filter
            realm: Optional realm filter
            service_name: Optional service name filter
        
        Returns:
            List of route metadata dictionaries
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_routes_start", success=True)
            
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
            
            result = await self.route_registry.discover_routes(pillar, realm, service_name, user_context)
            
            # Record success metric
            await self.record_health_metric("discover_routes_success", 1.0, {
                "pillar": pillar or "all",
                "realm": realm or "all",
                "service_name": service_name or "all"
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_routes_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_routes")
            self.logger.error(f"❌ Failed to discover routes: {e}")
            return []
    
    async def report_service_mesh_policies(
        self,
        service_name: str,
        policies: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> bool:
        """
        Report service mesh policies (domain owns, Curator reports).
        
        Delegates to ServiceMeshMetadataReporterService.
        
        Args:
            service_name: Name of the service
            policies: Policy metadata dictionary (domain-provided)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            True if reporting successful, False otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "report_service_mesh_policies_start",
                success=True,
                details={"service_name": service_name}
            )
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "service_mesh_policies", "write"):
                        await self.record_health_metric("report_service_mesh_policies_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("report_service_mesh_policies_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("report_service_mesh_policies_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("report_service_mesh_policies_complete", success=False)
                            return False
            
            result = await self.service_mesh_metadata_reporter.report_service_mesh_policies(
                service_name,
                policies,
                user_context
            )
            
            # Record health metric
            await self.record_health_metric(
                "report_service_mesh_policies_success",
                1.0,
                {"service_name": service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "report_service_mesh_policies_complete",
                success=True,
                details={"service_name": service_name}
            )
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "report_service_mesh_policies")
            raise
    
    async def get_service_mesh_policy_report(
        self,
        service_name: str
    ) -> Dict[str, Any]:
        """
        Get aggregated service mesh policy report.
        
        Delegates to ServiceMeshMetadataReporterService.
        
        Args:
            service_name: Name of the service
        
        Returns:
            Aggregated policy report
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_service_mesh_policy_report_start", success=True)
            
            result = await self.service_mesh_metadata_reporter.get_service_mesh_policy_report(service_name)
            
            # Record success metric
            await self.record_health_metric("get_service_mesh_policy_report_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_service_mesh_policy_report_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_service_mesh_policy_report")
            self.logger.error(f"❌ Failed to get service mesh policy report: {e}")
            return {}
    
    async def validate_pattern(self, pattern_definition: Dict[str, Any], user_context: Dict[str, Any] = None) -> bool:
        """Validate an architectural pattern."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("validate_pattern_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "pattern_validation", "read"):
                        await self.record_health_metric("validate_pattern_access_denied", 1.0, {"pattern_name": pattern_definition.get("name", "unknown")})
                        await self.log_operation_with_telemetry("validate_pattern_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("validate_pattern_tenant_denied", 1.0, {"pattern_name": pattern_definition.get("name", "unknown")})
                            await self.log_operation_with_telemetry("validate_pattern_complete", success=False)
                            return False
            
            result = await self.pattern_validation.validate_pattern(pattern_definition)
            
            # Record health metric
            await self.record_health_metric("validate_pattern_success", 1.0, {"pattern_name": pattern_definition.get("name", "unknown")})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_pattern_complete", success=True)
            
            return result.get("success", False) if isinstance(result, dict) else result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "validate_pattern")
            raise
    
    async def detect_antipatterns(self, code_path: str) -> List[AntiPatternViolation]:
        """Detect anti-patterns in code."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("detect_antipatterns_start", success=True)
            
            result = await self.antipattern_detection.detect_antipatterns(code_path)
            
            # Record health metric
            await self.record_health_metric("detect_antipatterns_success", 1.0, {"code_path": code_path, "violations_count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("detect_antipatterns_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "detect_antipatterns")
            raise
    
    async def generate_documentation(self, service_name: str, documentation_type: str = "openapi") -> bool:
        """Generate documentation for a service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("generate_documentation_start", success=True)
            
            result = await self.documentation_generation.generate_documentation(service_name, documentation_type)
            
            # Record health metric
            await self.record_health_metric("generate_documentation_success", 1.0, {"service_name": service_name, "documentation_type": documentation_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_documentation_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "generate_documentation")
            raise
    
    async def discover_service_by_name(self, service_name: str, user_context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Discover a service instance by name from service discovery.
        
        This method queries service discovery (via Public Works) with local cache fallback.
        Enables service mesh and federation patterns.
        
        Args:
            service_name: Name of the service to discover
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Service instance if found, None otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_service_by_name_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, service_name, "read"):
                        await self.record_health_metric("discover_service_by_name_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("discover_service_by_name_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_service_by_name_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_service_by_name_complete", success=False)
                            return None
            
            # Fast path: Check local cache first
            if service_name in self.registered_services:
                self.logger.debug(f"✅ Service {service_name} found in local cache")
                cache_entry = self.registered_services[service_name]
                result = cache_entry.get("service_instance")
                
                # Diagnostic logging for cache-only mode
                if result is None:
                    self.logger.warning(f"⚠️ Service {service_name} in cache but service_instance is None")
                    self.logger.debug(f"   Cache entry keys: {list(cache_entry.keys())}")
                    self.logger.debug(f"   Cache entry metadata: {cache_entry.get('metadata', {}).get('service_name', 'N/A')}")
                    # In cache-only mode, if service_instance is None, the service wasn't registered locally
                    # This can happen if the service was discovered from service discovery (which doesn't have instances)
                    # OR if registration failed silently
                    await self.record_health_metric("discover_service_by_name_cache_miss_instance", 1.0, {"service_name": service_name, "reason": "service_instance_is_none"})
                    await self.log_operation_with_telemetry("discover_service_by_name_complete", success=False)
                    return None
                
                await self.record_health_metric("discover_service_by_name_success", 1.0, {"service_name": service_name, "source": "cache"})
                await self.log_operation_with_telemetry("discover_service_by_name_complete", success=True)
                return result
            
            # Query service discovery (via Public Works) for service discovery
            if self.service_discovery:
                self.logger.debug(f"🔍 Querying service discovery for service: {service_name}")
                
                # Discover service from service discovery (Consul/Istio/Linkerd via Public Works)
                service_registrations = await self.service_discovery.discover_service(service_name)
                
                if service_registrations and len(service_registrations) > 0:
                    # Get the first healthy instance
                    service_reg = service_registrations[0]
                    self.logger.info(f"✅ Discovered service {service_name} from service discovery at {service_reg.address}:{service_reg.port}")
                    
                    # Update local cache for future fast lookups
                    # Note: We don't have the service_instance from service discovery, only metadata
                    # This is expected - service discovery knows WHERE services are, not their Python instances
                    self.registered_services[service_name] = {
                        "service_instance": None,  # Not available from service discovery
                        "metadata": {
                            "service_name": service_reg.service_name,
                            "service_type": service_reg.service_type,
                            "address": service_reg.address,
                            "port": service_reg.port,
                            "capabilities": service_reg.capabilities,
                            "endpoints": service_reg.endpoints
                        },
                        "registered_at": service_reg.registered_at.isoformat() if service_reg.registered_at else None,
                        "status": str(service_reg.health_status.value) if service_reg.health_status else "unknown"
                    }
                    
                    # Return the metadata (for service mesh communication)
                    result = self.registered_services[service_name].get("metadata")
                    await self.record_health_metric("discover_service_by_name_success", 1.0, {"service_name": service_name, "source": "service_discovery"})
                    await self.log_operation_with_telemetry("discover_service_by_name_complete", success=True)
                    return result
                else:
                    self.logger.warning(f"⚠️ Service {service_name} not found in service discovery")
                    await self.record_health_metric("discover_service_by_name_not_found", 1.0, {"service_name": service_name})
                    await self.log_operation_with_telemetry("discover_service_by_name_complete", success=True)
                    return None
            else:
                # Service discovery not available - cache-only mode
                # Log diagnostic info about what's in cache
                cache_keys = list(self.registered_services.keys())
                self.logger.warning(f"⚠️ Service discovery not available for {service_name}, cache-only mode")
                self.logger.debug(f"   Services in cache ({len(cache_keys)}): {cache_keys[:10]}")  # Show first 10
                self.logger.debug(f"   Looking for: {service_name}")
                if service_name not in cache_keys:
                    self.logger.warning(f"   ❌ Service {service_name} NOT in cache")
                else:
                    cache_entry = self.registered_services[service_name]
                    self.logger.debug(f"   ✅ Service {service_name} IS in cache")
                    self.logger.debug(f"   Cache entry has service_instance: {cache_entry.get('service_instance') is not None}")
                
                await self.record_health_metric("discover_service_by_name_not_found", 1.0, {"service_name": service_name, "reason": "no_service_discovery"})
                await self.log_operation_with_telemetry("discover_service_by_name_complete", success=True)
                return None
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_service_by_name")
            self.logger.error(f"Failed to discover service {service_name}: {e}")
            return None
    
    async def get_service(self, service_name: str, user_context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Get service instance by name (alias for discover_service_by_name).
        
        This is a convenience wrapper that extracts the service instance
        from discover_service_by_name() result. Provides backward compatibility
        for code that uses get_service() instead of discover_service_by_name().
        
        Args:
            service_name: Name of the service to get
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Service instance if found, None otherwise
        """
        try:
            # Use discover_service_by_name which handles cache and service discovery
            result = await self.discover_service_by_name(service_name, user_context)
            
            # If result is already the service instance (from cache), return it
            if result is not None and not isinstance(result, dict):
                return result
            
            # If result is metadata dict, try to get service_instance from cache
            if isinstance(result, dict):
                # Check cache directly for service_instance
                if service_name in self.registered_services:
                    service_instance = self.registered_services[service_name].get("service_instance")
                    if service_instance:
                        return service_instance
                # If no service_instance in cache, return None (service not registered locally)
                return None
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get service {service_name}: {e}")
            return None
    
    # ============================================================================
    # SOA API REGISTRY METHODS (NEW - Week 2 Enhancement)
    # ============================================================================
    
    async def register_soa_api(self, service_name: str, api_name: str, endpoint: str, handler: Any, metadata: Dict[str, Any] = None, user_context: Dict[str, Any] = None) -> bool:
        """
        Register a SOA API (backward compatibility wrapper).
        
        This method registers the SOA API as a capability with contracts using the new pattern.
        It also maintains the old in-memory registry for backward compatibility during migration.
        
        DEPRECATED: Use register_domain_capability() directly with contracts={'soa_api': {...}}.
        This method will be removed after all callers are migrated.
        
        Args:
            service_name: Name of the Smart City service
            api_name: Name of the SOA API
            endpoint: API endpoint path
            handler: Handler function for the API
            metadata: Additional metadata about the API
            user_context: Optional user context for security and tenant validation
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_soa_api_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "soa_api_registry", "write"):
                        await self.record_health_metric("register_soa_api_access_denied", 1.0, {"service_name": service_name, "api_name": api_name})
                        await self.log_operation_with_telemetry("register_soa_api_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_soa_api_tenant_denied", 1.0, {"service_name": service_name, "api_name": api_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_soa_api_complete", success=False)
                            return False
            
            self.logger.info(f"🔗 Registering SOA API: {service_name}.{api_name} at {endpoint}")
            
            # Register as capability with contracts (new pattern)
            from .models.capability_definition import CapabilityDefinition
            
            capability = CapabilityDefinition(
                service_name=service_name,
                interface_name=f"I{service_name}",
                endpoints=[endpoint],
                tools=[],
                description=f"SOA API: {api_name}",
                realm="smart_city",  # Default realm, can be overridden
                version="1.0.0",
                semantic_mapping=None,
                contracts={
                    "soa_api": {
                        "api_name": api_name,
                        "endpoint": endpoint,
                        "handler": handler,
                        "metadata": metadata or {}
                    }
                }
            )
            
            # Register using new pattern
            success = await self.register_domain_capability(capability, user_context)
            
            # Maintain backward compatibility: also store in old registry
            if success:
                soa_api_key = f"{service_name}.{api_name}"
                self.soa_api_registry[soa_api_key] = {
                    "service_name": service_name,
                    "api_name": api_name,
                    "endpoint": endpoint,
                    "handler": handler,
                    "metadata": metadata or {},
                    "registered_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }
                self.logger.info(f"✅ SOA API registered successfully: {soa_api_key}")
            
            # Record health metric
            await self.record_health_metric("register_soa_api_success", 1.0, {"service_name": service_name, "api_name": api_name, "endpoint": endpoint})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_soa_api_complete", success=True)
            
            return success
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_soa_api")
            self.logger.error(f"❌ Failed to register SOA API {service_name}.{api_name}: {e}")
            return False
    
    async def get_soa_api(self, service_name: str, api_name: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Get SOA API information for realm consumption.
        
        Args:
            service_name: Name of the Smart City service
            api_name: Name of the SOA API
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Optional[Dict[str, Any]]: SOA API information if found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_soa_api_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    soa_api_key = f"{service_name}.{api_name}"
                    if not await security.check_permissions(user_context, soa_api_key, "read"):
                        await self.record_health_metric("get_soa_api_access_denied", 1.0, {"service_name": service_name, "api_name": api_name})
                        await self.log_operation_with_telemetry("get_soa_api_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_soa_api_tenant_denied", 1.0, {"service_name": service_name, "api_name": api_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_soa_api_complete", success=False)
                            return None
            
            soa_api_key = f"{service_name}.{api_name}"
            api_info = self.soa_api_registry.get(soa_api_key)
            
            if api_info:
                self.logger.info(f"✅ Found SOA API: {soa_api_key}")
            else:
                self.logger.warning(f"⚠️ SOA API not found: {soa_api_key}")
            
            # Record health metric
            await self.record_health_metric("get_soa_api_success", 1.0, {"service_name": service_name, "api_name": api_name, "found": api_info is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_soa_api_complete", success=True)
            
            return api_info
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_soa_api")
            self.logger.error(f"❌ Failed to get SOA API {service_name}.{api_name}: {e}")
            return None
    
    async def list_soa_apis(self, service_name: Optional[str] = None, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        List all registered SOA APIs, optionally filtered by service.
        
        Args:
            service_name: Optional service name to filter by
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict[str, Any]: Dictionary of SOA APIs
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("list_soa_apis_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "soa_api_registry", "read"):
                        await self.record_health_metric("list_soa_apis_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("list_soa_apis_complete", success=False)
                        return {}
            
            # Tenant validation and filtering (multi-tenant support)
            if service_name:
                # Filter by service name
                filtered_apis = {
                    key: value for key, value in self.soa_api_registry.items()
                    if value["service_name"] == service_name
                }
                result = filtered_apis
            else:
                # Return all SOA APIs
                result = self.soa_api_registry.copy()
            
            # Apply tenant filtering if user_context provided
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("list_soa_apis_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("list_soa_apis_complete", success=False)
                            return {}
                        # Filter by tenant if tenant_id is in metadata
                        result = {
                            key: value for key, value in result.items()
                            if value.get("metadata", {}).get("tenant_id") == tenant_id or not value.get("metadata", {}).get("tenant_id")
                        }
            
            # Record health metric
            await self.record_health_metric("list_soa_apis_success", 1.0, {"service_name": service_name, "count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("list_soa_apis_complete", success=True)
            
            return result
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "list_soa_apis")
            self.logger.error(f"❌ Failed to list SOA APIs: {e}")
            return {}
    
    # ============================================================================
    # MCP TOOL REGISTRY METHODS (NEW - Week 2 Enhancement)
    # ============================================================================
    
    async def register_mcp_tool(self, tool_name: str, tool_definition: Dict[str, Any], metadata: Dict[str, Any] = None, user_context: Dict[str, Any] = None) -> bool:
        """
        Register an MCP tool (backward compatibility wrapper).
        
        This method registers the MCP tool as a capability with contracts using the new pattern.
        It also maintains the old in-memory registry for backward compatibility during migration.
        
        DEPRECATED: Use register_domain_capability() directly with contracts={'mcp_tool': {...}}.
        This method will be removed after all callers are migrated.
        
        Args:
            tool_name: Name of the MCP tool
            tool_definition: Tool definition including schema, handler, etc.
            metadata: Additional metadata about the tool
            user_context: Optional user context for security and tenant validation
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_mcp_tool_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "mcp_tool_registry", "write"):
                        await self.record_health_metric("register_mcp_tool_access_denied", 1.0, {"tool_name": tool_name})
                        await self.log_operation_with_telemetry("register_mcp_tool_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_mcp_tool_tenant_denied", 1.0, {"tool_name": tool_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_mcp_tool_complete", success=False)
                            return False
            
            self.logger.info(f"🔧 Registering MCP Tool: {tool_name}")
            
            # Extract service name from metadata or tool_definition
            service_name = metadata.get("service_name") if metadata else None
            if not service_name:
                service_name = tool_definition.get("wraps_service", "unknown")
            
            # Register as capability with contracts (new pattern)
            from .models.capability_definition import CapabilityDefinition
            
            capability = CapabilityDefinition(
                service_name=service_name,
                interface_name=f"I{service_name}",
                endpoints=[tool_definition.get("endpoint", f"/mcp/{tool_name}")],
                tools=[tool_name],
                description=f"MCP Tool: {tool_name}",
                realm=metadata.get("realm", "agentic") if metadata else "agentic",
                version="1.0.0",
                semantic_mapping=None,
                contracts={
                    "mcp_tool": {
                        "tool_name": tool_name,
                        "tool_definition": tool_definition,
                        "metadata": metadata or {}
                    }
                }
            )
            
            # Register using new pattern
            success = await self.register_domain_capability(capability, user_context)
            
            # Maintain backward compatibility: also store in old registry
            if success:
                self.mcp_tool_registry[tool_name] = {
                    "tool_name": tool_name,
                    "tool_definition": tool_definition,
                    "metadata": metadata or {},
                    "registered_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }
                self.logger.info(f"✅ MCP Tool registered successfully: {tool_name}")
            
            # Record health metric
            await self.record_health_metric("register_mcp_tool_success", 1.0, {"tool_name": tool_name, "tool_type": tool_definition.get("type", "unknown")})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_mcp_tool_complete", success=True)
            
            return success
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_mcp_tool")
            self.logger.error(f"❌ Failed to register MCP Tool {tool_name}: {e}")
            return False
    
    async def get_mcp_tool(self, tool_name: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Get MCP tool information for agent access.
        
        Args:
            tool_name: Name of the MCP tool
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Optional[Dict[str, Any]]: MCP tool information if found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_mcp_tool_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, tool_name, "read"):
                        await self.record_health_metric("get_mcp_tool_access_denied", 1.0, {"tool_name": tool_name})
                        await self.log_operation_with_telemetry("get_mcp_tool_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_mcp_tool_tenant_denied", 1.0, {"tool_name": tool_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_mcp_tool_complete", success=False)
                            return None
            
            tool_info = self.mcp_tool_registry.get(tool_name)
            
            if tool_info:
                self.logger.info(f"✅ Found MCP Tool: {tool_name}")
            else:
                self.logger.warning(f"⚠️ MCP Tool not found: {tool_name}")
            
            # Record health metric
            await self.record_health_metric("get_mcp_tool_success", 1.0, {"tool_name": tool_name, "found": tool_info is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_mcp_tool_complete", success=True)
            
            return tool_info
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_mcp_tool")
            self.logger.error(f"❌ Failed to get MCP Tool {tool_name}: {e}")
            return None
    
    async def list_mcp_tools(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        List all registered MCP tools.
        
        Args:
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict[str, Any]: Dictionary of MCP tools
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("list_mcp_tools_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "mcp_tool_registry", "read"):
                        await self.record_health_metric("list_mcp_tools_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("list_mcp_tools_complete", success=False)
                        return {}
            
            # Tenant validation and filtering (multi-tenant support)
            result = self.mcp_tool_registry.copy()
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("list_mcp_tools_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("list_mcp_tools_complete", success=False)
                            return {}
                        # Filter by tenant if tenant_id is in metadata
                        result = {
                            key: value for key, value in result.items()
                            if value.get("metadata", {}).get("tenant_id") == tenant_id or not value.get("metadata", {}).get("tenant_id")
                        }
            
            # Record health metric
            await self.record_health_metric("list_mcp_tools_success", 1.0, {"count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("list_mcp_tools_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "list_mcp_tools")
            self.logger.error(f"❌ Failed to list MCP tools: {e}")
            return {}
    
    # ============================================================================
    # HEALTH AND STATUS METHODS
    # ============================================================================
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Curator Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_status_start", success=True)
            
            # Get status from all micro-services
            core_services_status = {
                "capability_registry": await self.capability_registry.get_status(),
                "pattern_validation": await self.pattern_validation.get_status(),
                "antipattern_detection": await self.antipattern_detection.get_status(),
                "documentation_generation": await self.documentation_generation.get_status()
            }
            
            agentic_services_status = {
                "agent_capability_registry": "healthy",  # These services don't have get_status yet
                "agent_specialization_management": "healthy",
                "agui_schema_documentation": "healthy",
                "agent_health_monitoring": "healthy"
            }
            
            # Determine overall status
            all_statuses = list(core_services_status.values()) + list(agentic_services_status.values())
            overall_status = "healthy" if all(status == "healthy" for status in all_statuses) else "degraded"
            
            result = {
                "service_name": "curator_foundation",
                "overall_status": overall_status,
                "core_services": core_services_status,
                "agentic_services": agentic_services_status,
                "total_services": len(core_services_status) + len(agentic_services_status),
                "healthy_services": len([s for s in all_statuses if s == "healthy"]),
                "registered_services_count": len(self.registered_services),
                "is_initialized": self.is_initialized,
                "timestamp": self._get_current_timestamp()
            }
            
            # Record health metric
            await self.record_health_metric("get_status_success", 1.0, {"overall_status": overall_status})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_status_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_status")
            self.logger.error(f"Failed to get Curator Foundation status: {e}")
            return {
                "service_name": "curator_foundation",
                "overall_status": "error",
                "error": str(e),
                "error_code": type(e).__name__,
                "timestamp": self._get_current_timestamp()
            }
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check for the Curator Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("run_health_check_start", success=True)
            
            self.logger.info("🔍 Running Curator Foundation health check...")
            
            # Get status
            status = await self.get_status()
            
            # Get agentic dimension summary
            agentic_summary = await self.get_agentic_dimension_summary()
            
            # Get registered services
            registered_services = await self.get_registered_services()
            
            # Determine health
            overall_health = "healthy" if status["overall_status"] == "healthy" else "degraded"
            
            result = {
                "service_name": "curator_foundation",
                "overall_health": overall_health,
                "status": status,
                "agentic_dimension": agentic_summary,
                "registered_services": registered_services,
                "health_checks": {
                    "core_services": status["healthy_services"],
                    "total_services": status["total_services"],
                    "agentic_integration": "active",
                    "registered_services": len(self.registered_services)
                },
                "timestamp": self._get_current_timestamp()
            }
            
            # Record health metric
            await self.record_health_metric("run_health_check_success", 1.0, {"overall_health": overall_health})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("run_health_check_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "run_health_check")
            self.logger.error(f"Health check failed: {e}")
            return {
                "service_name": "curator_foundation",
                "overall_health": "unhealthy",
                "error": str(e),
                "error_code": type(e).__name__,
                "timestamp": self._get_current_timestamp()
            }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # ============================================================================
    # ARTIFACT REGISTRY METHODS (NEW - Phase 1, Week 2: Artifact Discovery)
    # ============================================================================
    
    async def register_artifact(
        self,
        artifact_id: str,
        artifact_type: str,  # "solution" or "journey"
        artifact_data: Dict[str, Any],
        client_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register an artifact for discovery.
        
        This method registers Solution or Journey artifacts in the Curator registry
        so they can be discovered by other services. Artifacts are stored in Librarian
        (via SolutionComposerService or StructuredJourneyOrchestratorService), and
        this method registers them in Curator for discovery.
        
        Args:
            artifact_id: Unique identifier for the artifact
            artifact_type: Type of artifact ("solution" or "journey")
            artifact_data: Full artifact data (including status, version, etc.)
            client_id: Optional client ID for multi-tenant scoping
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict[str, Any]: Registration result with success status
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_artifact_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "artifact_registry", "write"):
                        await self.record_health_metric("register_artifact_access_denied", 1.0, {"artifact_id": artifact_id, "artifact_type": artifact_type})
                        await self.log_operation_with_telemetry("register_artifact_complete", success=False)
                        return {
                            "success": False,
                            "error": "Access denied: insufficient permissions"
                        }
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_artifact_tenant_denied", 1.0, {"artifact_id": artifact_id, "artifact_type": artifact_type, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_artifact_complete", success=False)
                            return {
                                "success": False,
                                "error": "Access denied: invalid tenant"
                            }
            
            # Validate artifact_type
            if artifact_type not in ["solution", "journey"]:
                await self.record_health_metric("register_artifact_invalid_type", 1.0, {"artifact_id": artifact_id, "artifact_type": artifact_type})
                await self.log_operation_with_telemetry("register_artifact_complete", success=False)
                return {
                    "success": False,
                    "error": f"Invalid artifact_type: {artifact_type}. Must be 'solution' or 'journey'"
                }
            
            self.logger.info(f"📋 Registering {artifact_type} artifact: {artifact_id}")
            
            # Register artifact in registry
            self.artifact_registry[artifact_id] = {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id,
                "artifact_data": artifact_data,
                "registered_at": datetime.utcnow().isoformat(),
                "status": artifact_data.get("status", "draft"),
                "version": artifact_data.get("version", 1),
                "user_id": user_context.get("user_id") if user_context else None,
                "tenant_id": user_context.get("tenant_id") if user_context else None
            }
            
            # Record health metric
            await self.record_health_metric("register_artifact_success", 1.0, {"artifact_id": artifact_id, "artifact_type": artifact_type, "client_id": client_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_artifact_complete", success=True)
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "registered_at": self.artifact_registry[artifact_id]["registered_at"]
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_artifact")
            self.logger.error(f"❌ Failed to register artifact {artifact_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": type(e).__name__
            }
    
    async def get_artifact(
        self,
        artifact_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get artifact by ID for discovery.
        
        Args:
            artifact_id: Unique identifier for the artifact
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Optional[Dict[str, Any]]: Artifact data if found, None otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_artifact_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "artifact_registry", "read"):
                        await self.record_health_metric("get_artifact_access_denied", 1.0, {"artifact_id": artifact_id})
                        await self.log_operation_with_telemetry("get_artifact_complete", success=False)
                        return None
            
            # Check registry
            artifact_entry = self.artifact_registry.get(artifact_id)
            
            if not artifact_entry:
                self.logger.warning(f"⚠️ Artifact not found in registry: {artifact_id}")
                await self.record_health_metric("get_artifact_not_found", 1.0, {"artifact_id": artifact_id})
                await self.log_operation_with_telemetry("get_artifact_complete", success=True)
                return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    artifact_tenant_id = artifact_entry.get("tenant_id")
                    if tenant_id and artifact_tenant_id and tenant_id != artifact_tenant_id:
                        await self.record_health_metric("get_artifact_tenant_denied", 1.0, {"artifact_id": artifact_id, "tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("get_artifact_complete", success=False)
                        return None
            
            self.logger.info(f"✅ Found artifact in registry: {artifact_id}")
            
            # Return artifact data
            result = artifact_entry.get("artifact_data", {})
            
            # Record health metric
            await self.record_health_metric("get_artifact_success", 1.0, {"artifact_id": artifact_id, "artifact_type": artifact_entry.get("artifact_type")})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_artifact_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_artifact")
            self.logger.error(f"❌ Failed to get artifact {artifact_id}: {e}")
            return None
    
    async def update_artifact(
        self,
        artifact_id: str,
        artifact_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update artifact in registry.
        
        This method updates the artifact data in the Curator registry when
        an artifact is updated (e.g., status change, version increment).
        
        Args:
            artifact_id: Unique identifier for the artifact
            artifact_data: Updated artifact data
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict[str, Any]: Update result with success status
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("update_artifact_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "artifact_registry", "write"):
                        await self.record_health_metric("update_artifact_access_denied", 1.0, {"artifact_id": artifact_id})
                        await self.log_operation_with_telemetry("update_artifact_complete", success=False)
                        return {
                            "success": False,
                            "error": "Access denied: insufficient permissions"
                        }
            
            # Check if artifact exists
            if artifact_id not in self.artifact_registry:
                await self.record_health_metric("update_artifact_not_found", 1.0, {"artifact_id": artifact_id})
                await self.log_operation_with_telemetry("update_artifact_complete", success=False)
                return {
                    "success": False,
                    "error": f"Artifact not found: {artifact_id}"
                }
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    artifact_tenant_id = self.artifact_registry[artifact_id].get("tenant_id")
                    if tenant_id and artifact_tenant_id and tenant_id != artifact_tenant_id:
                        await self.record_health_metric("update_artifact_tenant_denied", 1.0, {"artifact_id": artifact_id, "tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("update_artifact_complete", success=False)
                        return {
                            "success": False,
                            "error": "Access denied: invalid tenant"
                        }
            
            self.logger.info(f"🔄 Updating artifact in registry: {artifact_id}")
            
            # Update artifact data
            self.artifact_registry[artifact_id]["artifact_data"] = artifact_data
            self.artifact_registry[artifact_id]["status"] = artifact_data.get("status", "draft")
            self.artifact_registry[artifact_id]["version"] = artifact_data.get("version", 1)
            self.artifact_registry[artifact_id]["updated_at"] = datetime.utcnow().isoformat()
            
            # Record health metric
            await self.record_health_metric("update_artifact_success", 1.0, {"artifact_id": artifact_id, "status": artifact_data.get("status"), "version": artifact_data.get("version")})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("update_artifact_complete", success=True)
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "updated_at": self.artifact_registry[artifact_id]["updated_at"]
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "update_artifact")
            self.logger.error(f"❌ Failed to update artifact {artifact_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": type(e).__name__
            }
    
    async def list_client_artifacts(
        self,
        client_id: str,
        artifact_type: Optional[str] = None,  # "solution" or "journey" or None for all
        status: Optional[str] = None,  # Filter by status
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all artifacts for a specific client.
        
        Args:
            client_id: Client ID to filter by
            artifact_type: Optional filter by artifact type ("solution" or "journey")
            status: Optional filter by status
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict[str, Any]: Dictionary of artifacts keyed by artifact_id
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("list_client_artifacts_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "artifact_registry", "read"):
                        await self.record_health_metric("list_client_artifacts_access_denied", 1.0, {"client_id": client_id})
                        await self.log_operation_with_telemetry("list_client_artifacts_complete", success=False)
                        return {}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("list_client_artifacts_tenant_denied", 1.0, {"client_id": client_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("list_client_artifacts_complete", success=False)
                            return {}
            
            self.logger.info(f"📋 Listing artifacts for client: {client_id}")
            
            # Filter artifacts by client_id
            filtered_artifacts = {}
            for artifact_id, artifact_entry in self.artifact_registry.items():
                artifact_client_id = artifact_entry.get("client_id")
                
                # Match client_id
                if artifact_client_id != client_id:
                    continue
                
                # Filter by artifact_type if provided
                if artifact_type and artifact_entry.get("artifact_type") != artifact_type:
                    continue
                
                # Filter by status if provided
                if status and artifact_entry.get("status") != status:
                    continue
                
                # Add to results
                filtered_artifacts[artifact_id] = artifact_entry.get("artifact_data", {})
            
            # Record health metric
            await self.record_health_metric("list_client_artifacts_success", 1.0, {"client_id": client_id, "count": len(filtered_artifacts), "artifact_type": artifact_type, "status": status})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("list_client_artifacts_complete", success=True)
            
            return filtered_artifacts
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "list_client_artifacts")
            self.logger.error(f"❌ Failed to list artifacts for client {client_id}: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup the Curator Foundation Service and all micro-services."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("cleanup_start", success=True)
            
            self.logger.info("🧹 Cleaning up Curator Foundation Service...")
            
            # Cleanup core micro-services
            if hasattr(self.capability_registry, 'cleanup'):
                await self.capability_registry.cleanup()
            if hasattr(self.pattern_validation, 'cleanup'):
                await self.pattern_validation.cleanup()
            if hasattr(self.antipattern_detection, 'cleanup'):
                await self.antipattern_detection.cleanup()
            if hasattr(self.documentation_generation, 'cleanup'):
                await self.documentation_generation.cleanup()
            
            # Cleanup agentic micro-services
            await self.agent_capability_registry.cleanup()
            await self.agent_specialization_management.cleanup()
            await self.agui_schema_documentation.cleanup()
            await self.agent_health_monitoring.cleanup()
            
            # Clear registered services
            self.registered_services.clear()
            self.is_initialized = False
            
            self.logger.info("✅ Curator Foundation Service cleanup completed")
            
            # Record health metric
            await self.record_health_metric("cleanup_success", 1.0, {"service": "curator_foundation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("cleanup_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "cleanup")
            self.logger.error(f"Error during cleanup: {e}")
    
    async def shutdown(self):
        """Shutdown the Curator Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("curator_foundation_shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Curator Foundation Service...")
            
            # Shutdown all micro-services
            await self.cleanup()
            
            # Record health metric
            await self.record_health_metric("curator_foundation_shutdown", 1.0, {"service": "curator_foundation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("curator_foundation_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "curator_foundation_shutdown")
            self.logger.error(f"❌ Error during Curator Foundation Service shutdown: {e}")
    