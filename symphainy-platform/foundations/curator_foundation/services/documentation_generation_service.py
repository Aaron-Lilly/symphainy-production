#!/usr/bin/env python3
"""
Documentation Generation Service

Handles OpenAPI specification and documentation generation for services
across the platform.

WHAT (Service Role): I need to generate OpenAPI specs and documentation
HOW (Service Implementation): I create OpenAPI specifications and service documentation
"""

import os
import sys
from typing import Dict, Any, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase

# Direct library usage - no abstractions needed for standard libraries
import json
import yaml
import re
import ast
from pathlib import Path
from ..models import CapabilityDefinition


class DocumentationGenerationService(FoundationServiceBase):
    """
    Documentation Generation Service - OpenAPI and documentation generation
    
    Generates OpenAPI specifications and service documentation for all
    registered services across the platform.
    
    WHAT (Service Role): I need to generate OpenAPI specs and documentation
    HOW (Service Implementation): I create OpenAPI specifications and service documentation
    """
    
    def __init__(self, di_container, capability_registry_service=None):
        """Initialize Documentation Generation Service."""
        super().__init__("documentation_generation", di_container)
        self.capability_registry_service = capability_registry_service
        
        self.logger.info("📄 Documentation Generation Service initialized")
    
    async def initialize(self):
        """Initialize the Documentation Generation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("documentation_generation_initialize_start", success=True)
            
            await super().initialize()
            self.logger.info("🚀 Initializing Documentation Generation Service...")
            
            self.logger.info("✅ Documentation Generation Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("documentation_generation_initialized", 1.0, {"service": "documentation_generation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("documentation_generation_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "documentation_generation_initialize")
            raise
    
    # ============================================================================
    # OPENAPI GENERATION
    
    async def generate_openapi_spec(self, service_name: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate OpenAPI specification for a service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("generate_openapi_spec_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, service_name, "read"):
                        await self.record_health_metric("generate_openapi_spec_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("generate_openapi_spec_complete", success=False)
                        return {"error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("generate_openapi_spec_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("generate_openapi_spec_complete", success=False)
                            return {"error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            if not self.capability_registry_service:
                raise ValueError("Capability Registry Service not available")
            
            capability = await self.capability_registry_service.get_capability(service_name, user_context)
            if not capability:
                raise ValueError(f"Service {service_name} not found in registry")
            
            # Generate OpenAPI spec
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": f"{service_name.title()} Service",
                    "description": capability.description,
                    "version": capability.version
                },
                "servers": [
                    {
                        "url": f"http://localhost:8000/{service_name}",
                        "description": f"{service_name} service server"
                    }
                ],
                "paths": self._generate_paths_from_capability(capability),
                "components": {
                    "schemas": self._generate_schemas_from_protocol(capability.protocol_name)
                }
            }
            
            self.logger.info(f"📄 Generated OpenAPI spec for {service_name}")
            
            # Record health metric
            await self.record_health_metric("generate_openapi_spec_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_openapi_spec_complete", success=True)
            
            return openapi_spec
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "generate_openapi_spec")
            raise
    
    def _extract_endpoints_from_contracts(self, capability: CapabilityDefinition) -> List[str]:
        """Extract endpoints from capability contracts."""
        endpoints = []
        if capability.contracts:
            if capability.contracts.get("rest_api"):
                endpoints.append(capability.contracts["rest_api"].get("endpoint"))
            if capability.contracts.get("soa_api"):
                endpoints.append(capability.contracts["soa_api"].get("endpoint"))
            if capability.contracts.get("mcp_tool"):
                tool_def = capability.contracts["mcp_tool"].get("tool_definition", {})
                endpoints.append(tool_def.get("endpoint"))
        return [e for e in endpoints if e]  # Filter out None values
    
    def _extract_tools_from_contracts(self, capability: CapabilityDefinition) -> List[str]:
        """Extract tool names from capability contracts."""
        tools = []
        if capability.contracts and capability.contracts.get("mcp_tool"):
            tool_name = capability.contracts["mcp_tool"].get("tool_name")
            if tool_name:
                tools.append(tool_name)
        return tools
    
    def _generate_paths_from_capability(self, capability: CapabilityDefinition) -> Dict[str, Any]:
        """Generate OpenAPI paths from capability contracts."""
        paths = {}
        endpoints = self._extract_endpoints_from_contracts(capability)
        
        for endpoint in endpoints:
            # Determine method from contract
            method = "get"
            if capability.contracts:
                if capability.contracts.get("rest_api") and capability.contracts["rest_api"].get("endpoint") == endpoint:
                    method = capability.contracts["rest_api"].get("method", "POST").lower()
                elif capability.contracts.get("soa_api") and capability.contracts["soa_api"].get("endpoint") == endpoint:
                    method = capability.contracts["soa_api"].get("method", "POST").lower()
            
            # Simple path generation - can be enhanced
            path_item = {
                method: {
                    "summary": f"{capability.capability_name.replace('_', ' ').title()}",
                    "description": capability.description,
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
            }
            paths[endpoint] = path_item
        
        return paths
    
    def _generate_schemas_from_protocol(self, protocol_name: str) -> Dict[str, Any]:
        """Generate OpenAPI schemas from protocol name."""
        # Simple schema generation - can be enhanced
        return {
            f"{protocol_name}Request": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "Request data"
                    }
                }
            },
            f"{protocol_name}Response": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Operation success status"
                    },
                    "data": {
                        "type": "object",
                        "description": "Response data"
                    }
                }
            }
        }
    
    # ============================================================================
    # DOCUMENTATION GENERATION
    
    async def generate_docs(self, service_name: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate documentation for a service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("generate_docs_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, service_name, "read"):
                        await self.record_health_metric("generate_docs_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("generate_docs_complete", success=False)
                        return {"error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("generate_docs_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("generate_docs_complete", success=False)
                            return {"error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            if not self.capability_registry_service:
                raise ValueError("Capability Registry Service not available")
            
            capability = await self.capability_registry_service.get_capability(service_name, user_context)
            if not capability:
                raise ValueError(f"Service {service_name} not found in registry")
            
            # Extract endpoints and tools from contracts
            endpoints = self._extract_endpoints_from_contracts(capability)
            tools = self._extract_tools_from_contracts(capability)
            
            docs = {
                "service_name": service_name,
                "capability_name": capability.capability_name,
                "protocol_name": capability.protocol_name,
                "description": capability.description,
                "realm": capability.realm,
                "version": capability.version,
                "endpoints": endpoints,
                "tools": tools,
                "contracts": capability.contracts,
                "semantic_mapping": capability.semantic_mapping,
                "openapi_url": f"/{service_name}/openapi.json",
                "docs_url": f"/{service_name}/docs",
                "registered_at": capability.registered_at
            }
            
            self.logger.info(f"📚 Generated docs for {service_name}")
            
            # Record health metric
            await self.record_health_metric("generate_docs_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_docs_complete", success=True)
            
            return docs
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "generate_docs")
            raise
    
    async def generate_platform_docs(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive platform documentation."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("generate_platform_docs_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "platform_documentation", "read"):
                        await self.record_health_metric("generate_platform_docs_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("generate_platform_docs_complete", success=False)
                        return {"error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("generate_platform_docs_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("generate_platform_docs_complete", success=False)
                            return {"error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            if not self.capability_registry_service:
                raise ValueError("Capability Registry Service not available")
            
            # Get all capabilities
            capabilities = await self.capability_registry_service.list_capabilities()
            
            # Group by realm
            capabilities_by_realm = {}
            for capability in capabilities:
                realm = capability.realm
                if realm not in capabilities_by_realm:
                    capabilities_by_realm[realm] = []
                capabilities_by_realm[realm].append(capability)
            
            # Generate platform overview
            platform_docs = {
                "platform_name": "Symphainy Platform",
                "description": "Smart City Platform with micro-modular architecture",
                "total_services": len(capabilities),
                "realms": list(capabilities_by_realm.keys()),
                "capabilities_by_realm": {},
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Add detailed realm information
            for realm, realm_capabilities in capabilities_by_realm.items():
                platform_docs["capabilities_by_realm"][realm] = {
                    "service_count": len(realm_capabilities),
                    "services": [
                        {
                            "name": cap.service_name,
                            "capability_name": cap.capability_name,
                            "protocol_name": cap.protocol_name,
                            "description": cap.description,
                            "version": cap.version,
                            "endpoints": self._extract_endpoints_from_contracts(cap),
                            "tools": self._extract_tools_from_contracts(cap)
                        }
                        for cap in realm_capabilities
                    ]
                }
            
            self.logger.info(f"📚 Generated platform documentation for {len(capabilities)} services")
            
            # Record health metric
            await self.record_health_metric("generate_platform_docs_success", 1.0, {"total_services": len(capabilities)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_platform_docs_complete", success=True)
            
            return platform_docs
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "generate_platform_docs")
            raise
    
    # ============================================================================
    # DOCUMENTATION MANAGEMENT
    
    async def get_documentation_status(self) -> Dict[str, Any]:
        """Get documentation generation service status."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_documentation_status_start", success=True)
            
            status = {
                "service_name": "documentation_generation",
                "capability_registry_available": self.capability_registry_service is not None,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            if self.capability_registry_service:
                registry_status = await self.capability_registry_service.get_registry_status()
                status["registry_status"] = registry_status
            
            # Record health metric
            await self.record_health_metric("get_documentation_status_success", 1.0, {})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_documentation_status_complete", success=True)
            
            return status
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_documentation_status")
            return {"error": str(e), "error_code": type(e).__name__}
    
    async def generate_service_summary(self, service_name: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a concise service summary."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("generate_service_summary_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, service_name, "read"):
                        await self.record_health_metric("generate_service_summary_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("generate_service_summary_complete", success=False)
                        return {"error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("generate_service_summary_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("generate_service_summary_complete", success=False)
                            return {"error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            if not self.capability_registry_service:
                raise ValueError("Capability Registry Service not available")
            
            capability = await self.capability_registry_service.get_capability(service_name, user_context)
            if not capability:
                raise ValueError(f"Service {service_name} not found in registry")
            
            # Extract endpoints and tools from contracts
            endpoints = self._extract_endpoints_from_contracts(capability)
            tools = self._extract_tools_from_contracts(capability)
            
            summary = {
                "service_name": service_name,
                "capability_name": capability.capability_name,
                "protocol_name": capability.protocol_name,
                "description": capability.description,
                "realm": capability.realm,
                "version": capability.version,
                "endpoint_count": len(endpoints),
                "tool_count": len(tools),
                "registered_at": capability.registered_at,
                "openapi_url": f"/{service_name}/openapi.json",
                "docs_url": f"/{service_name}/docs"
            }
            
            # Record health metric
            await self.record_health_metric("generate_service_summary_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_service_summary_complete", success=True)
            
            return summary
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "generate_service_summary")
            return {"error": str(e), "error_code": type(e).__name__}

    async def shutdown(self):
        """Shutdown the Documentation Generation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("documentation_generation_shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Documentation Generation Service...")
            
            # Clear any cached documentation
            # (No specific cleanup needed for this service)
            
            self.logger.info("✅ Documentation Generation Service shutdown complete")
            
            # Record health metric
            await self.record_health_metric("documentation_generation_shutdown", 1.0, {"service": "documentation_generation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("documentation_generation_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "documentation_generation_shutdown")
            self.logger.error(f"❌ Error during Documentation Generation Service shutdown: {e}")


