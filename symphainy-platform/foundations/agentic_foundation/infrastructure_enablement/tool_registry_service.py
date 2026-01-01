#!/usr/bin/env python3
"""
Tool Registry Service - Agentic Realm Business Service

Manages tool registration, discovery, and lifecycle as a business service.
Integrates with Curator Foundation's capability registry for distributed tool discovery.

WHAT (Agentic Role): I manage tool registration and discovery for agentic operations
HOW (Business Service): I orchestrate tool storage and Curator capability registry
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.tool_storage_protocol import (
    ToolDefinition, ToolStorageProtocol
)

# Import utility mixins
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin


class ToolRegistryService(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    Tool Registry Service - Agentic Realm Business Service
    
    Manages tool registration, discovery, and lifecycle for agentic operations.
    Integrates with Curator Foundation's capability registry for distributed tool discovery.
    
    This is a BUSINESS SERVICE that orchestrates tool storage and Curator capability registry
    for agentic operations.
    """
    
    def __init__(self, tool_storage_abstraction: ToolStorageProtocol, 
                 curator_foundation=None, di_container=None):
        """Initialize Tool Registry Service with tool storage and Curator Foundation."""
        if not di_container:
            raise ValueError("DI Container is required for ToolRegistryService initialization")
        
        # Initialize utility mixins
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.tool_storage_abstraction = tool_storage_abstraction
        self.curator_foundation = curator_foundation
        
        # Business metrics
        self.business_metrics = {
            "total_tools_registered": 0,
            "total_tools_discovered": 0,
            "successful_registrations": 0,
            "failed_registrations": 0,
            "curator_integrations": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        self.logger.info("✅ Tool Registry Service (Business Service) initialized")
    
    async def register_tool(self, tool_definition: ToolDefinition, 
                          agent_id: str = None,
                          tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a tool with the registry.
        
        Args:
            tool_definition: Tool definition to register
            agent_id: ID of the agent registering the tool
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            Dict containing registration result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_tool_start", success=True, details={"tool_name": tool_definition.name})
            
            # Security validation (zero-trust: secure by design)
            if tenant_context:
                security = self.get_security()
                if security:
                    # Create user_context from tenant_context for security check
                    user_context = {"tenant_id": tenant_context.get("tenant_id")} if tenant_context.get("tenant_id") else None
                    if user_context:
                        if not await security.check_permissions(user_context, "tool_registry", "write"):
                            await self.record_health_metric("register_tool_access_denied", 1.0, {"tool_name": tool_definition.name})
                            await self.log_operation_with_telemetry("register_tool_complete", success=False)
                            return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_tool_tenant_denied", 1.0, {"tool_name": tool_definition.name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_tool_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            self.logger.info(f"📝 Registering tool: {tool_definition.name}")
            
            # Set agent and tenant context
            if agent_id:
                tool_definition.owner_agent = agent_id
            if tenant_context:
                tool_definition.realm = tenant_context.get("realm", "agentic")
                tool_definition.pillar = tenant_context.get("pillar", "agentic")
            
            # Store tool in infrastructure storage
            success = await self.tool_storage_abstraction.save_tool(tool_definition)
            
            if not success:
                self.business_metrics["failed_registrations"] += 1
                return {
                    "success": False,
                    "error": "Failed to save tool to storage",
                    "tool_name": tool_definition.name
                }
            
            # Register with Curator Foundation if available
            if self.curator_foundation:
                curator_result = await self._register_with_curator(
                    tool_definition, agent_id, tenant_context
                )
                if curator_result.get("success"):
                    self.business_metrics["curator_integrations"] += 1
            
            # Update business metrics
            self.business_metrics["total_tools_registered"] += 1
            self.business_metrics["successful_registrations"] += 1
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            self.logger.info(f"✅ Tool registered successfully: {tool_definition.name}")
            
            # Record success metric
            await self.record_health_metric("register_tool_success", 1.0, {
                "tool_name": tool_definition.name,
                "agent_id": agent_id,
                "curator_registered": self.curator_foundation is not None
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_tool_complete", success=True, details={"tool_name": tool_definition.name})
            
            return {
                "success": True,
                "tool_name": tool_definition.name,
                "version": tool_definition.version,
                "agent_id": agent_id,
                "curator_registered": self.curator_foundation is not None
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_tool", details={"tool_name": tool_definition.name})
            self.logger.error(f"❌ Failed to register tool {tool_definition.name}: {e}")
            self.business_metrics["failed_registrations"] += 1
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_definition.name
            }
    
    async def discover_tools(self, filters: Optional[Dict[str, Any]] = None,
                           agent_id: str = None,
                           tenant_context: Dict[str, Any] = None) -> List[ToolDefinition]:
        """
        Discover tools based on filters.
        
        Args:
            filters: Filters to apply (realm, pillar, tags, etc.)
            agent_id: ID of the agent discovering tools
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            List of discovered tool definitions
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_tools_start", success=True, details={"filters": filters})
            
            # Security validation (zero-trust: secure by design)
            if tenant_context:
                security = self.get_security()
                if security:
                    # Create user_context from tenant_context for security check
                    user_context = {"tenant_id": tenant_context.get("tenant_id")} if tenant_context.get("tenant_id") else None
                    if user_context:
                        if not await security.check_permissions(user_context, "tool_registry", "read"):
                            await self.record_health_metric("discover_tools_access_denied", 1.0, {})
                            await self.log_operation_with_telemetry("discover_tools_complete", success=False)
                            return []
            
            # Tenant validation (multi-tenant support)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_tools_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_tools_complete", success=False)
                            return []
            
            self.logger.info(f"🔍 Discovering tools with filters: {filters}")
            
            # Apply tenant context to filters
            if tenant_context:
                if not filters:
                    filters = {}
                filters["realm"] = tenant_context.get("realm", "agentic")
                filters["pillar"] = tenant_context.get("pillar", "agentic")
            
            # Get tools from storage
            tools = await self.tool_storage_abstraction.list_tools(filters)
            
            # Update business metrics
            self.business_metrics["total_tools_discovered"] += len(tools)
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            # Record success metric
            await self.record_health_metric("discover_tools_success", 1.0, {"tools_count": len(tools)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_tools_complete", success=True, details={"tools_count": len(tools)})
            
            self.logger.info(f"✅ Discovered {len(tools)} tools")
            return tools
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_tools", details={"filters": filters})
            self.logger.error(f"❌ Failed to discover tools: {e}")
            return []
    
    async def get_tool(self, tool_name: str, version: Optional[str] = None,
                      agent_id: str = None, tenant_context: Dict[str, Any] = None) -> Optional[ToolDefinition]:
        """
        Get a specific tool by name and version.
        
        Args:
            tool_name: Name of the tool
            version: Version of the tool (optional)
            agent_id: ID of the agent requesting the tool
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            Tool definition or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_tool_start", success=True, details={"tool_name": tool_name, "version": version})
            
            # Security validation (zero-trust: secure by design)
            if tenant_context:
                security = self.get_security()
                if security:
                    # Create user_context from tenant_context for security check
                    user_context = {"tenant_id": tenant_context.get("tenant_id")} if tenant_context.get("tenant_id") else None
                    if user_context:
                        if not await security.check_permissions(user_context, "tool_registry", "read"):
                            await self.record_health_metric("get_tool_access_denied", 1.0, {"tool_name": tool_name})
                            await self.log_operation_with_telemetry("get_tool_complete", success=False)
                            return None
            
            # Tenant validation (multi-tenant support)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_tool_tenant_denied", 1.0, {"tool_name": tool_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_tool_complete", success=False)
                            return None
            
            self.logger.debug(f"🔍 Getting tool: {tool_name} v{version or 'latest'}")
            
            tool = await self.tool_storage_abstraction.get_tool(tool_name, version)
            
            if tool:
                # Record success metric
                await self.record_health_metric("get_tool_success", 1.0, {"tool_name": tool_name, "found": True})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_tool_complete", success=True, details={"tool_name": tool_name, "found": True})
                self.logger.debug(f"✅ Found tool: {tool_name}")
            else:
                # Record not found metric
                await self.record_health_metric("get_tool_not_found", 1.0, {"tool_name": tool_name})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_tool_complete", success=True, details={"tool_name": tool_name, "found": False})
                self.logger.debug(f"⚠️ Tool not found: {tool_name}")
            
            return tool
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_tool", details={"tool_name": tool_name, "version": version})
            self.logger.error(f"❌ Failed to get tool {tool_name}: {e}")
            return None
    
    async def unregister_tool(self, tool_name: str, version: Optional[str] = None,
                            agent_id: str = None, tenant_context: Dict[str, Any] = None) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            tool_name: Name of the tool to unregister
            version: Version of the tool (optional)
            agent_id: ID of the agent unregistering the tool
            tenant_context: Tenant context for multi-tenancy (optional, for validation)
            
        Returns:
            True if successfully unregistered, False otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("unregister_tool_start", success=True, details={"tool_name": tool_name, "version": version})
            
            # Security validation (zero-trust: secure by design)
            if tenant_context:
                security = self.get_security()
                if security:
                    user_context = {"tenant_id": tenant_context.get("tenant_id")} if tenant_context.get("tenant_id") else None
                    if user_context:
                        if not await security.check_permissions(user_context, "tool_registry", "write"):
                            await self.record_health_metric("unregister_tool_access_denied", 1.0, {"tool_name": tool_name})
                            await self.log_operation_with_telemetry("unregister_tool_complete", success=False)
                            return False
            
            # Tenant validation (multi-tenant support)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("unregister_tool_tenant_denied", 1.0, {"tool_name": tool_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("unregister_tool_complete", success=False)
                            return False
            
            self.logger.info(f"🗑️ Unregistering tool: {tool_name} v{version or 'all'}")
            
            # Remove from storage
            success = await self.tool_storage_abstraction.delete_tool(tool_name, version)
            
            if success:
                # Record success metric
                await self.record_health_metric("unregister_tool_success", 1.0, {"tool_name": tool_name})
                # End telemetry tracking
                await self.log_operation_with_telemetry("unregister_tool_complete", success=True, details={"tool_name": tool_name})
                self.logger.info(f"✅ Tool unregistered successfully: {tool_name}")
            else:
                # Record failure metric
                await self.record_health_metric("unregister_tool_not_found", 1.0, {"tool_name": tool_name})
                # End telemetry tracking
                await self.log_operation_with_telemetry("unregister_tool_complete", success=False, details={"tool_name": tool_name})
                self.logger.warning(f"⚠️ Tool not found for unregistration: {tool_name}")
            
            return success
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "unregister_tool", details={"tool_name": tool_name, "version": version})
            self.logger.error(f"❌ Failed to unregister tool {tool_name}: {e}")
            return False
    
    async def _register_with_curator(self, tool_definition: ToolDefinition,
                                   agent_id: str = None,
                                   tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register tool with Curator Foundation capability registry."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("_register_with_curator_start", success=True, details={"tool_name": tool_definition.name})
            
            if not self.curator_foundation:
                await self.record_health_metric("_register_with_curator_not_available", 1.0, {"tool_name": tool_definition.name})
                await self.log_operation_with_telemetry("_register_with_curator_complete", success=False)
                return {"success": False, "error": "Curator Foundation not available"}
            
            # Create capability definition for Curator
            capability_data = {
                "interface": f"I{tool_definition.name.title()}",
                "endpoints": [],
                "tools": [{
                    "name": tool_definition.name,
                    "description": tool_definition.description,
                    "parameters": tool_definition.parameters,
                    "returns": tool_definition.returns
                }],
                "description": f"Tool capability: {tool_definition.name}",
                "realm": tool_definition.realm or "agentic",
                "version": tool_definition.version
            }
            
            # Register with Curator capability registry
            result = await self.curator_foundation.capability_registry.register_capability(
                service_name=f"tool_{tool_definition.name}",
                capability=capability_data,
                tenant_context=tenant_context
            )
            
            if result.get("success"):
                # Record success metric
                await self.record_health_metric("_register_with_curator_success", 1.0, {"tool_name": tool_definition.name})
                # End telemetry tracking
                await self.log_operation_with_telemetry("_register_with_curator_complete", success=True, details={"tool_name": tool_definition.name})
                self.logger.info(f"✅ Tool registered with Curator: {tool_definition.name}")
                return {"success": True, "curator_result": result}
            else:
                # Record failure metric
                await self.record_health_metric("_register_with_curator_failed", 1.0, {"tool_name": tool_definition.name, "error": result.get("error")})
                # End telemetry tracking
                await self.log_operation_with_telemetry("_register_with_curator_complete", success=False, details={"tool_name": tool_definition.name})
                self.logger.warning(f"⚠️ Failed to register with Curator: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_register_with_curator", details={"tool_name": tool_definition.name})
            self.logger.error(f"❌ Failed to register with Curator: {e}")
            return {"success": False, "error": str(e)}
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """Get business metrics for tool registry operations."""
        return self.business_metrics.copy()
    
    def get_registry_health(self) -> Dict[str, Any]:
        """Get Tool Registry Service health status."""
        return {
            "service_name": "ToolRegistryService",
            "service_type": "business_service",
            "realm": "agentic",
            "tool_storage_available": self.tool_storage_abstraction is not None,
            "curator_foundation_available": self.curator_foundation is not None,
            "business_metrics": self.get_business_metrics(),
            "status": "healthy"
        }


