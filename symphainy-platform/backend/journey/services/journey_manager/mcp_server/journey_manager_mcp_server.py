#!/usr/bin/env python3
"""
Journey Manager MCP Server

Exposes Journey Manager capabilities as MCP tools for journey orchestration.

IMPORTANT: MCP servers are at the MANAGER level (not orchestrator level).
This provides journey-level tools for agents, not low-level service tools.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.mcp_server.mcp_server_base import MCPServerBase


class JourneyManagerMCPServer(MCPServerBase):
    """
    MCP Server for Journey Manager (Journey Orchestration).
    
    Provides journey-level tools for agents:
    - design_journey_tool: Design a journey based on requirements
    - create_roadmap_tool: Create a roadmap for a journey
    - track_milestones_tool: Track milestones for a journey
    - orchestrate_experience_tool: Orchestrate experience via Experience Manager (top-down flow)
    
    These are HIGH-LEVEL tools that orchestrate journey services internally.
    """
    
    def __init__(self, journey_manager, di_container):
        """
        Initialize Journey Manager MCP Server.
        
        Args:
            journey_manager: JourneyManagerService instance
            di_container: DI Container for platform services
        """
        super().__init__(
            service_name="journey_manager_mcp",
            di_container=di_container
        )
        self.journey_manager = journey_manager
    
    def register_server_tools(self) -> None:
        """Register MCP tools (journey-level, not service-level)."""
        
        # Tool 1: Design Journey
        self.register_tool(
            name="design_journey_tool",
            description="Design a journey based on requirements. Creates journey structure and milestones.",
            handler=self._design_journey_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "journey_request": {
                        "type": "object",
                        "description": "Journey design request with journey_type and requirements",
                        "properties": {
                            "journey_type": {"type": "string"},
                            "requirements": {"type": "object"}
                        }
                    }
                },
                "required": ["journey_request"]
            }
        )
        
        # Tool 2: Create Roadmap
        self.register_tool(
            name="create_roadmap_tool",
            description="Create a roadmap for a journey. Defines milestones and timeline.",
            handler=self._create_roadmap_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "roadmap_request": {
                        "type": "object",
                        "description": "Roadmap creation request with journey_id and milestones",
                        "properties": {
                            "journey_id": {"type": "string"},
                            "milestones": {"type": "array"}
                        }
                    }
                },
                "required": ["roadmap_request"]
            }
        )
        
        # Tool 3: Track Milestones
        self.register_tool(
            name="track_milestones_tool",
            description="Track milestones for a journey. Updates milestone status and progress.",
            handler=self._track_milestones_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "tracking_request": {
                        "type": "object",
                        "description": "Milestone tracking request with journey_id, milestone_id, and status",
                        "properties": {
                            "journey_id": {"type": "string"},
                            "milestone_id": {"type": "string"},
                            "status": {"type": "string"}
                        }
                    }
                },
                "required": ["tracking_request"]
            }
        )
        
        # Tool 4: Orchestrate Experience
        self.register_tool(
            name="orchestrate_experience_tool",
            description="Orchestrate experience via Experience Manager (top-down flow: Journey → Experience). Coordinates experience flow.",
            handler=self._orchestrate_experience_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "experience_context": {
                        "type": "object",
                        "description": "Experience orchestration context with journey_id and experience requirements"
                    }
                },
                "required": ["experience_context"]
            }
        )
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Execute tool by routing to journey manager.
        
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
                "design_journey_tool": self._design_journey_tool,
                "create_roadmap_tool": self._create_roadmap_tool,
                "track_milestones_tool": self._track_milestones_tool,
                "orchestrate_experience_tool": self._orchestrate_experience_tool
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
    
    async def _design_journey_tool(
        self,
        journey_request: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Design a journey based on requirements.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        try:
            result = await self.journey_manager.design_journey(journey_request, user_context=user_context)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_roadmap_tool(
        self,
        roadmap_request: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Create a roadmap for a journey.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        try:
            result = await self.journey_manager.create_roadmap(roadmap_request, user_context=user_context)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _track_milestones_tool(
        self,
        tracking_request: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Track milestones for a journey.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        try:
            result = await self.journey_manager.track_milestones(tracking_request, user_context=user_context)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _orchestrate_experience_tool(
        self,
        experience_context: dict,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Orchestrate experience via Experience Manager (top-down flow).
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        try:
            result = await self.journey_manager.orchestrate_experience(experience_context, user_context=user_context)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return machine + human readable usage guide."""
        return {
            "server_name": self.service_name,
            "description": "Journey Manager MCP Server - Provides journey orchestration tools",
            "tools": {
                "design_journey_tool": "Design a journey based on requirements",
                "create_roadmap_tool": "Create a roadmap for a journey",
                "track_milestones_tool": "Track milestones for a journey",
                "orchestrate_experience_tool": "Orchestrate experience via Experience Manager (top-down flow)"
            },
            "usage_pattern": "All tools require user_context for multi-tenancy and security"
        }
    
    def get_tool_list(self) -> list:
        """Return list of available tool names."""
        return [
            "design_journey_tool",
            "create_roadmap_tool",
            "track_milestones_tool",
            "orchestrate_experience_tool"
        ]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks."""
        try:
            # Check journey manager health
            journey_manager_health = "healthy"
            if hasattr(self.journey_manager, 'health_check'):
                try:
                    health = await self.journey_manager.health_check()
                    journey_manager_health = health.get("status", "unknown")
                except Exception:
                    journey_manager_health = "error"
            
            return {
                "server_name": self.service_name,
                "status": "healthy" if journey_manager_health == "healthy" else "degraded",
                "journey_manager_status": journey_manager_health,
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
            "compatible_with": ["journey_manager"],
            "timestamp": datetime.utcnow().isoformat()
        }



