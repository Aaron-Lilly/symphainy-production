#!/usr/bin/env python3
"""
Capability Registry Service

Handles capability registration, discovery, and management for all services
across the platform.

WHAT (Service Role): I need to manage service capability registration and discovery
HOW (Service Implementation): I maintain a central capability registry and integrate with service discovery
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import asdict

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase

# Import utilities directly
from utilities import (
    ValidationUtility, SerializationUtility, ConfigurationUtility,
    HealthManagementUtility
)
from ..models import CapabilityDefinition


class CapabilityRegistryService(FoundationServiceBase):
    """
    Capability Registry Service - Central capability registration and discovery
    
    Manages service capability registration, validation, and integration with
    service discovery systems like Consul.
    
    WHAT (Service Role): I need to manage service capability registration and discovery
    HOW (Service Implementation): I maintain a central capability registry and integrate with service discovery
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        """Initialize Capability Registry Service."""
        super().__init__("capability_registry", di_container)
        
        # Store public works foundation reference
        self.public_works_foundation = public_works_foundation
        
        # Central capability registry
        self.capability_registry: Dict[str, CapabilityDefinition] = {}
        
        # Service discovery integration
        self.service_discovery_enabled = False
        self.consul_client = None
        
        self.logger.info("📋 Capability Registry Service initialized")
    
    async def initialize(self):
        """Initialize the Capability Registry Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("capability_registry_initialize_start", success=True)
            
            await super().initialize()
            self.logger.info("🚀 Initializing Capability Registry Service...")
            
            # Initialize service discovery if available
            await self._initialize_service_discovery()
            
            self.logger.info("✅ Capability Registry Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("capability_registry_initialized", 1.0, {"service": "capability_registry"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("capability_registry_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "capability_registry_initialize")
            raise
    
    async def _initialize_service_discovery(self):
        """Initialize service discovery integration."""
        try:
            # Check if Consul is available through Public Works Foundation
            if self.public_works_foundation:
                # Get service discovery abstraction
                # Service discovery is handled via Consul adapter if available
                # Check if Consul adapter exists in Public Works Foundation
                try:
                    # Use Public Works Foundation's service discovery abstraction
                    service_discovery_abstraction = self.public_works_foundation.get_service_discovery_abstraction()
                    if service_discovery_abstraction:
                        service_discovery = service_discovery_abstraction
                    else:
                        service_discovery = None
                except:
                    service_discovery = None
                if service_discovery:
                    self.service_discovery_enabled = True
                    self.consul_client = service_discovery
                    self.logger.info("🔍 Service discovery integration enabled")
                else:
                    self.logger.info("ℹ️ Service discovery not available, using local registry only")
            else:
                self.logger.info("ℹ️ Public Works Foundation not available, using local registry only")
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "capability_registry_service_discovery_init")
            self.service_discovery_enabled = False
    
    # ============================================================================
    # CAPABILITY REGISTRATION
    
    async def register_capability_definition(self, capability_key: str, capability_def: 'CapabilityDefinition', user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a CapabilityDefinition directly (new Phase 2 pattern).
        
        Args:
            capability_key: Unique key for the capability (e.g., "NurseService.collect_telemetry")
            capability_def: CapabilityDefinition object
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with success status and capability info
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_capability_definition_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "capability_registry", "write"):
                        await self.record_health_metric("register_capability_definition_access_denied", 1.0, {"capability_key": capability_key})
                        await self.log_operation_with_telemetry("register_capability_definition_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_capability_definition_tenant_denied", 1.0, {"capability_key": capability_key, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_capability_definition_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            # Register in local registry (keyed by capability_key for unique identification)
            self.capability_registry[capability_key] = capability_def
            
            # Register in service discovery if available
            if self.service_discovery_enabled and self.consul_client:
                await self._register_with_service_discovery_new(capability_key, capability_def)
            
            result = {
                "success": True,
                "capability_key": capability_key,
                "capability_name": capability_def.capability_name,
                "service_name": capability_def.service_name,
                "registered_at": capability_def.registered_at
            }
            
            self.logger.info(f"✅ Registered capability '{capability_def.capability_name}' for {capability_def.service_name}")
            
            # Record health metric
            await self.record_health_metric("register_capability_definition_success", 1.0, {"capability_key": capability_key})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_capability_definition_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_capability_definition")
            self.logger.error(f"❌ Failed to register capability definition: {e}")
            return {"success": False, "error": str(e), "error_code": "REGISTRATION_FAILED"}
    
    async def register_capability(self, service_name: str, capability: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register a service capability in the central registry."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_capability_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "capability_registry", "write"):
                        await self.record_health_metric("register_capability_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("register_capability_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_capability_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_capability_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            # Validate capability structure
            if not self._validate_capability_structure(capability):
                raise ValueError(f"Invalid capability structure for {service_name}")
            
            # Create capability definition
            # Convert endpoints/tools to contracts format
            contracts = {}
            endpoints = capability.get("endpoints", [])
            tools = capability.get("tools", [])
            
            if endpoints:
                contracts["rest_api"] = {
                    "endpoints": endpoints,
                    "metadata": capability.get("metadata", {})
                }
            
            if tools:
                contracts["mcp_tool"] = {
                    "tools": tools,
                    "metadata": capability.get("metadata", {})
                }
            
            # If no contracts provided, create a default one
            if not contracts:
                contracts["rest_api"] = {
                    "endpoints": [],
                    "metadata": {}
                }
            
            capability_def = CapabilityDefinition(
                capability_name=capability.get("name", service_name),
                service_name=service_name,
                protocol_name=capability.get("protocol", f"{service_name}Protocol"),
                description=capability.get("description", f"{service_name} service capability"),
                realm=capability.get("realm", "unknown"),
                contracts=contracts,
                semantic_mapping=capability.get("semantic_mapping")
            )
            
            # Register in local registry
            self.capability_registry[service_name] = capability_def
            
            # Register in service discovery if available
            if self.service_discovery_enabled and self.consul_client:
                await self._register_with_service_discovery(service_name, capability_def)
            
            # Safely serialize capability definition (skip unpicklable objects)
            def safe_serialize_capability(cap_def):
                """Safely serialize CapabilityDefinition, skipping unpicklable objects."""
                def safe_serialize_value(value):
                    """Recursively serialize value, skipping unpicklable objects."""
                    # Skip objects with thread locks or other unpicklable attributes
                    if hasattr(value, '__dict__'):
                        # Check for common unpicklable attributes
                        unpicklable_attrs = ['_lock', '_thread', 'lock', 'thread', 'handler', 'service_instance', 'instance']
                        if any(hasattr(value, attr) for attr in unpicklable_attrs):
                            return None  # Skip this value
                        # For other objects, try to convert to dict if possible
                        try:
                            if hasattr(value, '__dict__'):
                                return {k: safe_serialize_value(v) for k, v in value.__dict__.items() if not k.startswith('_')}
                        except:
                            return None
                    
                    # Handle basic types
                    if isinstance(value, (str, int, float, bool, type(None))):
                        return value
                    elif isinstance(value, (list, tuple)):
                        serialized = [safe_serialize_value(item) for item in value]
                        return [item for item in serialized if item is not None]
                    elif isinstance(value, dict):
                        return {k: safe_serialize_value(v) for k, v in value.items() if safe_serialize_value(v) is not None}
                    else:
                        # Try string conversion for other types
                        try:
                            return str(value)
                        except:
                            return None
                
                return {
                    "capability_name": cap_def.capability_name,
                    "service_name": cap_def.service_name,
                    "protocol_name": cap_def.protocol_name,
                    "description": cap_def.description,
                    "realm": cap_def.realm,
                    "contracts": safe_serialize_value(cap_def.contracts),
                    "semantic_mapping": safe_serialize_value(cap_def.semantic_mapping) if cap_def.semantic_mapping else None,
                    "version": cap_def.version,
                    "registered_at": cap_def.registered_at
                }
            
            result = {
                "success": True,
                "service_name": service_name,
                "capability": safe_serialize_capability(capability_def),
                "registered_at": capability_def.registered_at
            }
            
            self.logger.info(f"✅ Registered capability for {service_name}")
            
            # Record health metric
            await self.record_health_metric("register_capability_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_capability_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_capability")
            raise
    
    def _validate_capability_structure(self, capability: Dict[str, Any]) -> bool:
        """
        Validate capability structure (Phase 2 refactoring - aligned with current architecture).
        
        The structure is flexible - interface, endpoints, and tools are optional
        and will be defaulted during CapabilityDefinition creation. This allows
        services to register with various capability formats while maintaining
        compatibility with the CapabilityDefinition model.
        
        Validation is permissive - only requires that capability is a dict with
        at least one identifying field.
        """
        # Basic validation: must be a dict
        if not isinstance(capability, dict):
            self.logger.warning(f"Capability structure must be a dict, got {type(capability).__name__}")
            return False
        
        # At minimum, should have some identifying information
        # Services may provide: description, name, service_name, realm, interface, endpoints, tools
        # Also support new Phase 2 fields: semantic_mapping, contracts
        identifying_fields = [
            "description", "name", "service_name", "realm", 
            "interface", "interface_name", "endpoints", "tools",
            "semantic_mapping", "contracts"  # New Phase 2 fields
        ]
        
        has_identifier = any(key in capability for key in identifying_fields)
        
        if not has_identifier:
            self.logger.warning(
                f"Capability structure missing identifying fields. "
                f"Expected at least one of: {', '.join(identifying_fields)}"
            )
        
        return has_identifier
    
    async def _register_with_service_discovery_new(self, capability_key: str, capability: CapabilityDefinition):
        """Register capability with service discovery (new Phase 2 pattern)."""
        try:
            if self.consul_client:
                # Extract endpoints from contracts
                endpoints = []
                if capability.contracts.get("soa_api"):
                    endpoints.append(capability.contracts["soa_api"].get("endpoint"))
                if capability.contracts.get("rest_api"):
                    endpoints.append(capability.contracts["rest_api"].get("endpoint"))
                if capability.contracts.get("mcp_tool"):
                    tool_def = capability.contracts["mcp_tool"].get("tool_definition", {})
                    endpoints.append(tool_def.get("endpoint"))
                
                # Safely serialize contracts and semantic_mapping (skip unpicklable objects)
                def safe_serialize_for_consul(value):
                    """Safely serialize value for Consul, skipping unpicklable objects."""
                    if hasattr(value, '__dict__'):
                        # Skip objects with thread locks or other unpicklable attributes
                        unpicklable_attrs = ['_lock', '_thread', 'lock', 'thread', 'handler', 'service_instance', 'instance']
                        if any(hasattr(value, attr) for attr in unpicklable_attrs):
                            return None
                        # Try to convert to dict if possible
                        try:
                            if hasattr(value, '__dict__'):
                                return {k: safe_serialize_for_consul(v) for k, v in value.__dict__.items() 
                                       if not k.startswith('_') and safe_serialize_for_consul(v) is not None}
                        except:
                            return None
                    
                    if isinstance(value, (str, int, float, bool, type(None))):
                        return value
                    elif isinstance(value, (list, tuple)):
                        serialized = [safe_serialize_for_consul(item) for item in value]
                        return [item for item in serialized if item is not None]
                    elif isinstance(value, dict):
                        return {k: safe_serialize_for_consul(v) for k, v in value.items() 
                               if safe_serialize_for_consul(v) is not None}
                    else:
                        try:
                            return str(value)
                        except:
                            return None
                
                service_data = {
                    "capability_key": capability_key,
                    "capability_name": capability.capability_name,
                    "service_name": capability.service_name,
                    "protocol_name": capability.protocol_name,
                    "endpoints": [e for e in endpoints if e],  # Filter out None values
                    "realm": capability.realm,
                    "version": capability.version,
                    "registered_at": capability.registered_at,
                    "contracts": safe_serialize_for_consul(capability.contracts),
                    "semantic_mapping": safe_serialize_for_consul(capability.semantic_mapping) if capability.semantic_mapping else None
                }
                
                # ServiceDiscoveryAbstraction.register_service() expects a single dict with service_name as a key
                service_info = {
                    "service_name": capability_key,
                    "service_type": capability.protocol_name,
                    "address": "localhost",  # Default for service discovery
                    "port": 0,  # Default for service discovery
                    "capabilities": [capability.capability_name],
                    "tags": [capability.realm] if capability.realm else [],
                    "meta": service_data,
                    "realm": capability.realm
                }
                await self.consul_client.register_service(service_info)
                self.logger.info(f"🔍 Registered capability '{capability.capability_name}' with service discovery")
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, f"capability_registry_service_discovery_register_{capability_key}")
    
    async def _register_with_service_discovery(self, service_name: str, capability: CapabilityDefinition):
        """Register capability with service discovery (legacy - for backward compatibility)."""
        try:
            if self.consul_client:
                # Extract endpoints from contracts if available, otherwise use empty list
                endpoints = []
                if hasattr(capability, 'contracts') and capability.contracts:
                    if capability.contracts.get("soa_api"):
                        endpoints.append(capability.contracts["soa_api"].get("endpoint"))
                    if capability.contracts.get("rest_api"):
                        endpoints.append(capability.contracts["rest_api"].get("endpoint"))
                    if capability.contracts.get("mcp_tool"):
                        tool_def = capability.contracts["mcp_tool"].get("tool_definition", {})
                        endpoints.append(tool_def.get("endpoint"))
                
                # Safely serialize for Consul (skip unpicklable objects)
                def safe_serialize_for_consul(value):
                    """Safely serialize value for Consul, skipping unpicklable objects."""
                    if hasattr(value, '__dict__'):
                        unpicklable_attrs = ['_lock', '_thread', 'lock', 'thread', 'handler', 'service_instance', 'instance']
                        if any(hasattr(value, attr) for attr in unpicklable_attrs):
                            return None
                        try:
                            if hasattr(value, '__dict__'):
                                return {k: safe_serialize_for_consul(v) for k, v in value.__dict__.items() 
                                       if not k.startswith('_') and safe_serialize_for_consul(v) is not None}
                        except:
                            return None
                    
                    if isinstance(value, (str, int, float, bool, type(None))):
                        return value
                    elif isinstance(value, (list, tuple)):
                        serialized = [safe_serialize_for_consul(item) for item in value]
                        return [item for item in serialized if item is not None]
                    elif isinstance(value, dict):
                        return {k: safe_serialize_for_consul(v) for k, v in value.items() 
                               if safe_serialize_for_consul(v) is not None}
                    else:
                        try:
                            return str(value)
                        except:
                            return None
                
                service_data = {
                    "service_name": service_name,
                    "protocol_name": getattr(capability, 'protocol_name', getattr(capability, 'interface_name', '')),
                    "endpoints": [e for e in endpoints if e] if endpoints else [],
                    "realm": capability.realm,
                    "version": capability.version,
                    "registered_at": capability.registered_at
                }
                
                # ServiceDiscoveryAbstraction.register_service() expects a single dict with service_name as a key
                service_info = {
                    "service_name": service_name,
                    "service_type": getattr(capability, 'protocol_name', getattr(capability, 'interface_name', '')),
                    "address": "localhost",  # Default for service discovery
                    "port": 0,  # Default for service discovery
                    "capabilities": [getattr(capability, 'capability_name', service_name)],
                    "tags": [capability.realm] if capability.realm else [],
                    "meta": service_data,
                    "realm": capability.realm
                }
                await self.consul_client.register_service(service_info)
                self.logger.info(f"🔍 Registered {service_name} with service discovery")
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, f"capability_registry_service_discovery_register_{service_name}")
    
    # ============================================================================
    # CAPABILITY DISCOVERY
    
    async def get_capability(self, service_name: str, user_context: Dict[str, Any] = None) -> Optional[CapabilityDefinition]:
        """Get a registered capability."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_capability_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, service_name, "read"):
                        await self.record_health_metric("get_capability_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("get_capability_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_capability_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_capability_complete", success=False)
                            return None
            
            capability = self.capability_registry.get(service_name)
            
            # Record health metric
            await self.record_health_metric("get_capability_success", 1.0, {"service_name": service_name, "found": capability is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_capability_complete", success=True)
            
            return capability
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_capability")
            return None
    
    async def list_capabilities(self, realm: str = None) -> List[CapabilityDefinition]:
        """List all registered capabilities, optionally filtered by realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("list_capabilities_start", success=True)
            
            capabilities = list(self.capability_registry.values())
            
            if realm:
                capabilities = [cap for cap in capabilities if cap.realm == realm]
            
            # Record health metric
            await self.record_health_metric("list_capabilities_success", 1.0, {"realm": realm, "count": len(capabilities)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("list_capabilities_complete", success=True)
            
            return capabilities
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "list_capabilities")
            return []
    
    async def get_capability_definition(self, capability_key: str, user_context: Dict[str, Any] = None) -> Optional[CapabilityDefinition]:
        """
        Get a registered capability by capability key.
        
        Args:
            capability_key: Unique capability key (e.g., "FileParserService.file_parsing")
            user_context: Optional user context for security and tenant validation
        
        Returns:
            CapabilityDefinition if found, None otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_capability_definition_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "capability_registry", "read"):
                        await self.record_health_metric("get_capability_definition_access_denied", 1.0, {"capability_key": capability_key})
                        await self.log_operation_with_telemetry("get_capability_definition_complete", success=False)
                        return None
            
            capability = self.capability_registry.get(capability_key)
            
            # Record health metric
            await self.record_health_metric("get_capability_definition_success", 1.0, {
                "capability_key": capability_key,
                "found": capability is not None
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_capability_definition_complete", success=True)
            
            return capability
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_capability_definition")
            return None
    
    async def get_capabilities_by_service(self, service_name: str, user_context: Dict[str, Any] = None) -> List[CapabilityDefinition]:
        """
        Get all capabilities for a service.
        
        Args:
            service_name: Name of the service
            user_context: Optional user context for security and tenant validation
        
        Returns:
            List of CapabilityDefinition objects for the service
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_capabilities_by_service_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "capability_registry", "read"):
                        await self.record_health_metric("get_capabilities_by_service_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("get_capabilities_by_service_complete", success=False)
                        return []
            
            # Filter capabilities by service_name
            capabilities = [
                cap for cap in self.capability_registry.values()
                if cap.service_name == service_name
            ]
            
            # Record health metric
            await self.record_health_metric("get_capabilities_by_service_success", 1.0, {
                "service_name": service_name,
                "count": len(capabilities)
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_capabilities_by_service_complete", success=True)
            
            return capabilities
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_capabilities_by_service")
            return []
    
    async def unregister_capability_definition(self, capability_key: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Unregister a specific capability by capability key.
        
        Args:
            capability_key: Unique capability key (e.g., "FileParserService.file_parsing")
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dict with unregistration result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("unregister_capability_definition_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "capability_registry", "write"):
                        await self.record_health_metric("unregister_capability_definition_access_denied", 1.0, {"capability_key": capability_key})
                        await self.log_operation_with_telemetry("unregister_capability_definition_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            if capability_key in self.capability_registry:
                capability = self.capability_registry[capability_key]
                del self.capability_registry[capability_key]
                
                # Unregister from service discovery if available
                if self.service_discovery_enabled and self.consul_client:
                    try:
                        await self.consul_client.deregister_service(capability.service_name)
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to deregister from service discovery: {e}")
                
                self.logger.info(f"🗑️ Unregistered capability {capability_key}")
                
                # Record health metric
                await self.record_health_metric("unregister_capability_definition_success", 1.0, {"capability_key": capability_key})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("unregister_capability_definition_complete", success=True)
                
                return {
                    "success": True,
                    "message": f"Capability {capability_key} unregistered successfully"
                }
            else:
                self.logger.warning(f"⚠️ Capability {capability_key} not found in registry")
                await self.record_health_metric("unregister_capability_definition_not_found", 1.0, {"capability_key": capability_key})
                await self.log_operation_with_telemetry("unregister_capability_definition_complete", success=True)
                return {
                    "success": False,
                    "error": f"Capability {capability_key} not found",
                    "error_code": "CAPABILITY_NOT_FOUND"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "unregister_capability_definition")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    # ============================================================================
    # REGISTRY MANAGEMENT
    
    async def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status and statistics."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_registry_status_start", success=True)
            
            capabilities_by_realm = {}
            for capability in self.capability_registry.values():
                realm = capability.realm
                if realm not in capabilities_by_realm:
                    capabilities_by_realm[realm] = 0
                capabilities_by_realm[realm] += 1
            
            status = {
                "total_capabilities": len(self.capability_registry),
                "capabilities_by_realm": capabilities_by_realm,
                "service_discovery_enabled": self.service_discovery_enabled,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Record health metric
            await self.record_health_metric("get_registry_status_success", 1.0, {"total_capabilities": len(self.capability_registry)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_registry_status_complete", success=True)
            
            return status
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_registry_status")
            return {"error": str(e), "error_code": type(e).__name__}
    
    async def unregister_capability(self, service_name: str) -> bool:
        """Unregister a service capability."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("unregister_capability_start", success=True)
            
            if service_name in self.capability_registry:
                del self.capability_registry[service_name]
                
                # Unregister from service discovery if available
                if self.service_discovery_enabled and self.consul_client:
                    await self.consul_client.deregister_service(service_name)
                
                self.logger.info(f"🗑️ Unregistered capability for {service_name}")
                
                # Record health metric
                await self.record_health_metric("unregister_capability_success", 1.0, {"service_name": service_name})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("unregister_capability_complete", success=True)
                
                return True
            else:
                self.logger.warning(f"⚠️ Service {service_name} not found in registry")
                await self.record_health_metric("unregister_capability_not_found", 1.0, {"service_name": service_name})
                await self.log_operation_with_telemetry("unregister_capability_complete", success=True)
                return False
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "unregister_capability")
            return False

    async def shutdown(self):
        """Shutdown the Capability Registry Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("capability_registry_shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Capability Registry Service...")
            
            # Clear capability registry
            self.capability_registry.clear()
            
            # Reset service discovery
            self.service_discovery_enabled = False
            
            self.logger.info("✅ Capability Registry Service shutdown complete")
            
            # Record health metric
            await self.record_health_metric("capability_registry_shutdown", 1.0, {"service": "capability_registry"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("capability_registry_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "capability_registry_shutdown")
            self.logger.error(f"❌ Error during Capability Registry Service shutdown: {e}")


