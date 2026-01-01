#!/usr/bin/env python3
"""
Solution Manager MCP Server

Exposes Solution Manager capabilities as MCP tools for solution orchestration.

IMPORTANT: MCP servers are at the MANAGER level.
This provides solution-level tools for agents, not low-level service tools.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.mcp_server.mcp_server_base import MCPServerBase


class SolutionManagerMCPServer(MCPServerBase):
    """
    MCP Server for Solution Manager.
    
    Provides solution-level tools for agents:
    - design_solution_tool: Design a solution based on requirements
    - compose_capabilities_tool: Compose capabilities from multiple sources
    - generate_poc_tool: Generate proof of concept for a solution
    - orchestrate_journey_tool: Orchestrate journey via Journey Manager (top-down flow)
    - discover_solutions_tool: Discover available solutions on the platform
    - get_platform_health_tool: Get overall platform health
    
    These are HIGH-LEVEL tools that orchestrate solution services internally.
    """
    
    def __init__(self, solution_manager: Any, di_container: Any):
        """
        Initialize Solution Manager MCP Server.
        
        Args:
            solution_manager: SolutionManagerService instance
            di_container: DI Container for platform services
        """
        super().__init__(
            service_name="solution_manager_mcp",
            di_container=di_container
        )
        self.solution_manager = solution_manager
        self.logger = self.di_container.get_logger(self.service_name)
        
        # Initialize utility services from the DI container
        # Note: security, tenant, and error_handler are properties in MCPServerBase, don't set them directly
        self.telemetry_emission = self.di_container.get_foundation_service("TelemetryFoundationService")
        self.health_monitoring = self.di_container.get_foundation_service("HealthFoundationService")
        # Don't set self.security, self.tenant, or self.error_handler - they are properties from MCPServerBase
        # Access via self.security, self.tenant, and self.error_handler properties when needed
        
        # Register tools in __init__
        self.register_server_tools()
    
    def register_server_tools(self) -> None:
        """Register MCP tools (solution-level, not service-level)."""
        
        # Tool 1: Design Solution
        self.register_tool(
            name="design_solution_tool",
            description="Design a solution based on requirements.",
            handler=self._design_solution_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "solution_request": {
                        "type": "object",
                        "description": "Data for solution design, e.g., {'solution_type': 'enterprise_migration', 'requirements': {'goal': 'migrate content'}}"
                    }
                },
                "required": ["solution_request"]
            }
        )
        
        # Tool 2: Compose Capabilities
        self.register_tool(
            name="compose_capabilities_tool",
            description="Compose capabilities from multiple sources.",
            handler=self._compose_capabilities_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "capability_request": {
                        "type": "object",
                        "description": "Data for capability composition, e.g., {'capabilities': ['content_processing', 'insights'], 'solution_context': {}}"
                    }
                },
                "required": ["capability_request"]
            }
        )
        
        # Tool 3: Generate POC
        self.register_tool(
            name="generate_poc_tool",
            description="Generate proof of concept for a solution.",
            handler=self._generate_poc_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "poc_request": {
                        "type": "object",
                        "description": "Data for POC generation, e.g., {'solution_type': 'enterprise_migration', 'scope': 'basic'}"
                    }
                },
                "required": ["poc_request"]
            }
        )
        
        # Tool 4: Orchestrate Journey
        self.register_tool(
            name="orchestrate_journey_tool",
            description="Orchestrate journey via Journey Manager (top-down flow: Solution → Journey).",
            handler=self._orchestrate_journey_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "journey_context": {
                        "type": "object",
                        "description": "Context for journey orchestration, e.g., {'journey_id': 'journey_123', 'journey_request': {'journey_type': 'structured'}}"
                    }
                },
                "required": ["journey_context"]
            }
        )
        
        # Tool 5: Discover Solutions
        self.register_tool(
            name="discover_solutions_tool",
            description="Discover available solutions on the platform.",
            handler=self._discover_solutions_tool,
            input_schema={
                "type": "object",
                "properties": {}
            }
        )
        
        # Tool 6: Get Platform Health
        self.register_tool(
            name="get_platform_health_tool",
            description="Get overall platform health across all solutions.",
            handler=self._get_platform_health_tool,
            input_schema={
                "type": "object",
                "properties": {}
            }
        )
        
        self.logger.info(f"✅ {self.service_name} registered {len(self.get_tool_list())} tools.")
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Execute tool by routing to solution manager.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        if self.telemetry_emission:
            await self.telemetry_emission.record_platform_operation_event(f"mcp_tool_execution_start_{tool_name}", {
                "server_name": self.service_name,
                "tool_name": tool_name,
                "parameters": parameters,
                "user_context": user_context
            })
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                if not await self.security.check_permissions(user_context, f"mcp_tool.{tool_name}", "execute"):
                    if self.health_monitoring:
                        await self.health_monitoring.record_metric(f"mcp_tool_execution_failed.{tool_name}", 1.0, {"error": "access_denied"})
                    if self.telemetry_emission:
                        await self.telemetry_emission.record_platform_operation_event(f"mcp_tool_execution_complete_{tool_name}", success=False, details={"error": "access_denied"})
                    raise PermissionError(f"Access denied: insufficient permissions to execute tool '{tool_name}'")
            
            # Tenant validation (multi-tenancy support)
            if user_context and self.tenant:
                tenant_id = user_context.get("tenant_id")
                if tenant_id:
                    if not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                        if self.health_monitoring:
                            await self.health_monitoring.record_metric(f"mcp_tool_execution_failed.{tool_name}", 1.0, {"error": "tenant_access_denied"})
                        if self.telemetry_emission:
                            await self.telemetry_emission.record_platform_operation_event(f"mcp_tool_execution_complete_{tool_name}", success=False, details={"error": "tenant_access_denied"})
                        raise PermissionError(f"Tenant access denied for tool '{tool_name}': {tenant_id}")
            
            tool_handlers = {
                "design_solution_tool": self._design_solution_tool,
                "compose_capabilities_tool": self._compose_capabilities_tool,
                "generate_poc_tool": self._generate_poc_tool,
                "orchestrate_journey_tool": self._orchestrate_journey_tool,
                "discover_solutions_tool": self._discover_solutions_tool,
                "get_platform_health_tool": self._get_platform_health_tool
            }
            
            handler = tool_handlers.get(tool_name)
            if handler:
                result = await handler(**parameters, user_context=user_context)
                if self.health_monitoring:
                    await self.health_monitoring.record_metric(f"mcp_tool_execution_success.{tool_name}", 1.0)
                if self.telemetry_emission:
                    await self.telemetry_emission.record_platform_operation_event(f"mcp_tool_execution_complete_{tool_name}", success=True)
                return result
            else:
                if self.health_monitoring:
                    await self.health_monitoring.record_metric(f"mcp_tool_execution_failed.{tool_name}", 1.0, {"error": "unknown_tool"})
                if self.telemetry_emission:
                    await self.telemetry_emission.record_platform_operation_event(f"mcp_tool_execution_complete_{tool_name}", success=False, details={"error": "unknown_tool"})
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            if self.error_handler:
                await self.error_handler.handle_error_with_audit(e, f"mcp_tool_execution_{tool_name}", user_context=user_context)
            if self.health_monitoring:
                await self.health_monitoring.record_metric(f"mcp_tool_execution_failed.{tool_name}", 1.0, {"error": type(e).__name__})
            if self.telemetry_emission:
                await self.telemetry_emission.record_platform_operation_event(f"mcp_tool_execution_complete_{tool_name}", success=False, details={"error": str(e)})
            return {"error": f"Failed to execute tool {tool_name}: {str(e)}"}
    
    async def _design_solution_tool(
        self,
        solution_request: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """MCP Tool: Design a solution based on requirements."""
        return await self.solution_manager.design_solution(solution_request, user_context=user_context)
    
    async def _compose_capabilities_tool(
        self,
        capability_request: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """MCP Tool: Compose capabilities from multiple sources."""
        return await self.solution_manager.compose_capabilities(capability_request, user_context=user_context)
    
    async def _generate_poc_tool(
        self,
        poc_request: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """MCP Tool: Generate proof of concept for a solution."""
        return await self.solution_manager.generate_poc(poc_request, user_context=user_context)
    
    async def _orchestrate_journey_tool(
        self,
        journey_context: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """MCP Tool: Orchestrate journey via Journey Manager (top-down flow: Solution → Journey)."""
        return await self.solution_manager.orchestrate_journey(journey_context, user_context=user_context)
    
    async def _discover_solutions_tool(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """MCP Tool: Discover available solutions on the platform."""
        return await self.solution_manager.discover_solutions(user_context=user_context)
    
    async def _get_platform_health_tool(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """MCP Tool: Get overall platform health across all solutions."""
        return await self.solution_manager.get_platform_health(user_context=user_context)
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return machine + human readable usage guide."""
        return {
            "server_name": self.service_name,
            "description": "Solution Manager MCP Server - Provides solution orchestration tools",
            "tools": {
                "design_solution_tool": "Design a solution based on requirements",
                "compose_capabilities_tool": "Compose capabilities from multiple sources",
                "generate_poc_tool": "Generate proof of concept for a solution",
                "orchestrate_journey_tool": "Orchestrate journey via Journey Manager (top-down flow)",
                "discover_solutions_tool": "Discover available solutions on the platform",
                "get_platform_health_tool": "Get overall platform health across all solutions"
            },
            "usage_pattern": "All tools require user_context for multi-tenancy and security"
        }
    
    def get_tool_list(self) -> list:
        """Return list of available tool names."""
        return [
            "design_solution_tool",
            "compose_capabilities_tool",
            "generate_poc_tool",
            "orchestrate_journey_tool",
            "discover_solutions_tool",
            "get_platform_health_tool"
        ]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks."""
        try:
            solution_manager_health = "healthy"
            if hasattr(self.solution_manager, 'health_check'):
                try:
                    health = await self.solution_manager.health_check()
                    solution_manager_health = health.get("status", "unknown")
                except Exception:
                    solution_manager_health = "error"
            
            return {
                "server_name": self.service_name,
                "status": "healthy" if solution_manager_health == "healthy" else "degraded",
                "solution_manager_status": solution_manager_health,
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
            "compatible_with": ["solution_manager"],
            "timestamp": datetime.utcnow().isoformat()
        }



