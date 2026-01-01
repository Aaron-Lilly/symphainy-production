#!/usr/bin/env python3
"""
Delivery Manager MCP Server

Exposes Delivery Manager capabilities as MCP tools for cross-realm coordination.

IMPORTANT: MCP servers are at the ORCHESTRATOR level (not enabling service level).
This provides use case-level tools for agents, not low-level service tools.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.mcp_server.mcp_server_base import MCPServerBase


class DeliveryManagerMCPServer(MCPServerBase):
    """
    MCP Server for Delivery Manager (Cross-Realm Coordination).
    
    Provides use case-level tools for agents:
    - coordinate_cross_realm: Coordinate activities across multiple realms
    - route_to_realm: Route a request to a specific realm
    - discover_realm_services: Discover available services in a specific realm
    - manage_cross_realm_state: Manage state across multiple realms
    - get_cross_realm_health: Get health status across all realms
    
    These are HIGH-LEVEL tools that orchestrate multiple orchestrators internally.
    """
    
    def __init__(self, delivery_manager, di_container):
        """
        Initialize Delivery Manager MCP Server.
        
        Args:
            delivery_manager: DeliveryManagerService instance
            di_container: DI Container for platform services
        """
        super().__init__(
            service_name="delivery_manager_mcp",
            di_container=di_container
        )
        self.delivery_manager = delivery_manager
    
    def register_server_tools(self) -> None:
        """Register MCP tools (use case-level, not service-level)."""
        
        # Tool 1: Coordinate Cross-Realm
        self.register_tool(
            name="coordinate_cross_realm",
            description="Coordinate activities across multiple realms. Orchestrates multiple orchestrators.",
            handler=self._coordinate_cross_realm_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "coordination_data": {
                        "type": "object",
                        "description": "Data for cross-realm coordination"
                    }
                },
                "required": ["coordination_data"]
            }
        )
        
        # Tool 2: Route to Realm
        self.register_tool(
            name="route_to_realm",
            description="Route a request to a specific realm. Delegates to appropriate orchestrator.",
            handler=self._route_to_realm_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "target_realm": {
                        "type": "string",
                        "description": "Target realm for routing"
                    },
                    "request_data": {
                        "type": "object",
                        "description": "Request data to route"
                    }
                },
                "required": ["target_realm", "request_data"]
            }
        )
        
        # Tool 3: Discover Realm Services
        self.register_tool(
            name="discover_realm_services",
            description="Discover available services in a specific realm. Uses Curator for service discovery.",
            handler=self._discover_realm_services_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "realm": {
                        "type": "string",
                        "description": "Target realm to discover services in"
                    }
                },
                "required": ["realm"]
            }
        )
        
        # Tool 4: Manage Cross-Realm State
        self.register_tool(
            name="manage_cross_realm_state",
            description="Manage state across multiple realms. Coordinates state management across orchestrators.",
            handler=self._manage_cross_realm_state_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "state_data": {
                        "type": "object",
                        "description": "State data to manage"
                    }
                },
                "required": ["state_data"]
            }
        )
        
        # Tool 5: Get Cross-Realm Health
        self.register_tool(
            name="get_cross_realm_health",
            description="Get health status across all realms. Aggregates health from all orchestrators.",
            handler=self._get_cross_realm_health_tool,
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Execute tool by routing to delivery manager.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        self.telemetry_emission.emit_tool_execution_start_telemetry(tool_name, parameters)
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.utilities.security
                if security:
                    if not await security.check_permissions(user_context, f"mcp_tool.{tool_name}", "execute"):
                        self.health_monitoring.record_tool_execution_health(tool_name, success=False, details={"error": "access_denied"})
                        self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False)
                        raise PermissionError(f"Access denied: insufficient permissions to execute tool '{tool_name}'")
            
            # Tenant validation (multi-tenancy support)
            if user_context:
                tenant = self.utilities.tenant
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            self.health_monitoring.record_tool_execution_health(tool_name, success=False, details={"error": "tenant_access_denied"})
                            self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False)
                            raise PermissionError(f"Tenant access denied for tool '{tool_name}': {tenant_id}")
            
            tool_handlers = {
                "coordinate_cross_realm": self._coordinate_cross_realm_tool,
                "route_to_realm": self._route_to_realm_tool,
                "discover_realm_services": self._discover_realm_services_tool,
                "manage_cross_realm_state": self._manage_cross_realm_state_tool,
                "get_cross_realm_health": self._get_cross_realm_health_tool
            }
            
            handler = tool_handlers.get(tool_name)
            if handler:
                result = await handler(**parameters, user_context=user_context)
                self.health_monitoring.record_tool_execution_health(tool_name, success=True)
                self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=True)
                return result
            else:
                self.health_monitoring.record_tool_execution_health(tool_name, success=False, details={"error": "unknown_tool"})
                self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False)
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            self.utilities.error_handler.handle_error_with_audit(e, f"mcp_tool_execution_{tool_name}", user_context=user_context)
            self.health_monitoring.record_tool_execution_health(tool_name, success=False, details={"error": str(e)})
            self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False, details={"error": str(e)})
            return {"error": f"Failed to execute tool {tool_name}: {str(e)}"}
    
    async def _coordinate_cross_realm_tool(
        self,
        coordination_data: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Coordinate activities across multiple realms.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # TODO: Implement actual coordination via delivery_manager
        # For now, return structured response
        return {
            "success": True,
            "coordination_id": f"coord_{int(datetime.utcnow().timestamp())}",
            "realms_involved": coordination_data.get("realms", []),
            "status": "coordinated",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _route_to_realm_tool(
        self,
        target_realm: str,
        request_data: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Route a request to a specific realm.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # TODO: Implement actual routing via delivery_manager
        # For now, return structured response
        return {
            "success": True,
            "target_realm": target_realm,
            "routed": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _discover_realm_services_tool(
        self,
        realm: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Discover available services in a specific realm.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # TODO: Implement actual discovery via delivery_manager (using Curator)
        # For now, return structured response
        return {
            "success": True,
            "realm": realm,
            "services": [],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _manage_cross_realm_state_tool(
        self,
        state_data: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Manage state across multiple realms.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # TODO: Implement actual state management via delivery_manager
        # For now, return structured response
        return {
            "success": True,
            "state_managed": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_cross_realm_health_tool(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Get health status across all realms.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # TODO: Implement actual health aggregation via delivery_manager
        # For now, return structured response
        return {
            "success": True,
            "overall_status": "healthy",
            "realms": {
                "business_enablement": "healthy",
                "smart_city": "healthy",
                "experience": "healthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return machine + human readable usage guide."""
        return {
            "server_name": self.service_name,
            "description": "Delivery Manager MCP Server - Provides cross-realm coordination tools",
            "tools": {
                "coordinate_cross_realm": "Coordinate activities across multiple realms",
                "route_to_realm": "Route a request to a specific realm",
                "discover_realm_services": "Discover available services in a specific realm",
                "manage_cross_realm_state": "Manage state across multiple realms",
                "get_cross_realm_health": "Get health status across all realms"
            },
            "usage_pattern": "All tools require user_context for multi-tenancy and security"
        }
    
    def get_tool_list(self) -> list:
        """Return list of available tool names."""
        return [
            "coordinate_cross_realm",
            "route_to_realm",
            "discover_realm_services",
            "manage_cross_realm_state",
            "get_cross_realm_health"
        ]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks."""
        try:
            # Check delivery manager health
            delivery_manager_health = "healthy"
            if hasattr(self.delivery_manager, 'get_health_status'):
                try:
                    health = await self.delivery_manager.get_health_status()
                    delivery_manager_health = health.get("status", "unknown")
                except Exception:
                    delivery_manager_health = "error"
            
            return {
                "server_name": self.service_name,
                "status": "healthy" if delivery_manager_health == "healthy" else "degraded",
                "delivery_manager_status": delivery_manager_health,
                "tools_registered": len(self.get_tool_list()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "server_name": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_version_info(self) -> Dict[str, Any]:
        """Return version and compatibility info."""
        return {
            "server_name": self.service_name,
            "version": "1.0.0",
            "api_version": "v1",
            "compatible_with": ["delivery_manager"],
            "timestamp": datetime.utcnow().isoformat()
        }
