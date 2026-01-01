#!/usr/bin/env python3
"""
Wave MCP Server

Wraps Wave Orchestrator as MCP Tools for agent consumption.

IMPORTANT: MCP servers are at the ORCHESTRATOR level (not enabling service level).
This provides use case-level tools for agents, not low-level service tools.
"""

import os
import sys
from typing import Dict, Any, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../../'))

from bases.mcp_server.mcp_server_base import MCPServerBase


class WaveMCPServer(MCPServerBase):
    """
    MCP Server for Wave Orchestrator (Insurance Use Case).
    
    Provides use case-level tools for agents:
    - create_wave_tool: Create a new migration wave
    - select_wave_candidates_tool: Select candidates for a wave
    - execute_wave_tool: Execute a migration wave
    - rollback_wave_tool: Rollback a wave migration
    - get_wave_status_tool: Get wave status and progress
    
    These are HIGH-LEVEL tools that orchestrate multiple services internally.
    """
    
    def __init__(self, orchestrator, di_container):
        """
        Initialize Wave MCP Server.
        
        Args:
            orchestrator: WaveOrchestrator instance
            di_container: DI Container for platform services
        """
        super().__init__(
            service_name="wave_migration_mcp",
            di_container=di_container
        )
        self.orchestrator = orchestrator
    
    def register_server_tools(self) -> None:
        """Register MCP tools (use case-level, not service-level)."""
        
        # Tool 1: Create Wave
        self.register_tool(
            tool_name="create_wave_tool",
            handler=self._create_wave_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "wave_number": {
                        "type": "integer",
                        "description": "Wave number (0 for clean candidates, 1+ for complex)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Wave name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Wave description"
                    },
                    "selection_criteria": {
                        "type": "object",
                        "description": "Routing rules for wave candidate selection"
                    },
                    "target_system": {
                        "type": "string",
                        "description": "Target system for migration"
                    },
                    "scheduled_start": {
                        "type": "string",
                        "description": "Scheduled start time (ISO format)",
                        "format": "date-time"
                    },
                    "scheduled_end": {
                        "type": "string",
                        "description": "Scheduled end time (ISO format)",
                        "format": "date-time"
                    },
                    "quality_gates": {
                        "type": "array",
                        "description": "List of quality gate definitions",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["data_quality", "completeness", "validation"]
                                },
                                "criteria": {"type": "object"}
                            }
                        }
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context for audit trail"
                    }
                },
                "required": ["wave_number", "name", "description", "selection_criteria", "target_system"]
            }
        )
        
        # Tool 2: Select Wave Candidates
        self.register_tool(
            tool_name="select_wave_candidates_tool",
            handler=self._select_wave_candidates_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "wave_id": {
                        "type": "string",
                        "description": "Wave ID"
                    },
                    "policy_pool": {
                        "type": "array",
                        "description": "Optional pool of policies to select from",
                        "items": {"type": "object"}
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context"
                    }
                },
                "required": ["wave_id"]
            }
        )
        
        # Tool 3: Execute Wave
        self.register_tool(
            tool_name="execute_wave_tool",
            handler=self._execute_wave_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "wave_id": {
                        "type": "string",
                        "description": "Wave ID to execute"
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context"
                    }
                },
                "required": ["wave_id"]
            }
        )
        
        # Tool 4: Rollback Wave
        self.register_tool(
            tool_name="rollback_wave_tool",
            handler=self._rollback_wave_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "wave_id": {
                        "type": "string",
                        "description": "Wave ID to rollback"
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context"
                    }
                },
                "required": ["wave_id"]
            }
        )
        
        # Tool 5: Get Wave Status
        self.register_tool(
            tool_name="get_wave_status_tool",
            handler=self._get_wave_status_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "wave_id": {
                        "type": "string",
                        "description": "Wave ID to check status for"
                    }
                },
                "required": ["wave_id"]
            }
        )
    
    # ============================================================================
    # TOOL HANDLERS
    # ============================================================================
    
    async def _create_wave_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Create a new migration wave."""
        try:
            from datetime import datetime as dt
            
            wave_number = kwargs.get("wave_number")
            name = kwargs.get("name")
            description = kwargs.get("description")
            selection_criteria = kwargs.get("selection_criteria")
            target_system = kwargs.get("target_system")
            
            if not all([wave_number is not None, name, description, selection_criteria, target_system]):
                return {
                    "success": False,
                    "error": "wave_number, name, description, selection_criteria, and target_system are required"
                }
            
            scheduled_start = None
            if kwargs.get("scheduled_start"):
                scheduled_start = dt.fromisoformat(kwargs["scheduled_start"].replace("Z", "+00:00"))
            
            scheduled_end = None
            if kwargs.get("scheduled_end"):
                scheduled_end = dt.fromisoformat(kwargs["scheduled_end"].replace("Z", "+00:00"))
            
            quality_gates = kwargs.get("quality_gates")
            user_context = kwargs.get("user_context", {})
            
            result = await self.orchestrator.create_wave(
                wave_number=wave_number,
                name=name,
                description=description,
                selection_criteria=selection_criteria,
                target_system=target_system,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                quality_gates=quality_gates,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ create_wave_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _select_wave_candidates_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Select candidates for a wave."""
        try:
            wave_id = kwargs.get("wave_id")
            if not wave_id:
                return {
                    "success": False,
                    "error": "wave_id is required"
                }
            
            policy_pool = kwargs.get("policy_pool")
            user_context = kwargs.get("user_context", {})
            
            result = await self.orchestrator.select_wave_candidates(
                wave_id=wave_id,
                policy_pool=policy_pool,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ select_wave_candidates_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_wave_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Execute a migration wave."""
        try:
            wave_id = kwargs.get("wave_id")
            if not wave_id:
                return {
                    "success": False,
                    "error": "wave_id is required"
                }
            
            user_context = kwargs.get("user_context", {})
            
            result = await self.orchestrator.execute_wave(
                wave_id=wave_id,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ execute_wave_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _rollback_wave_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Rollback a wave migration."""
        try:
            wave_id = kwargs.get("wave_id")
            if not wave_id:
                return {
                    "success": False,
                    "error": "wave_id is required"
                }
            
            user_context = kwargs.get("user_context", {})
            
            result = await self.orchestrator.rollback_wave(
                wave_id=wave_id,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ rollback_wave_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_wave_status_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Get wave status and progress."""
        try:
            wave_id = kwargs.get("wave_id")
            if not wave_id:
                return {
                    "success": False,
                    "error": "wave_id is required"
                }
            
            result = await self.orchestrator.get_wave_status(wave_id=wave_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ get_wave_status_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # MCP SERVER BASE IMPLEMENTATIONS
    # ============================================================================
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Dict[str, Any] = None) -> dict:
        """
        Execute tool by routing to orchestrator.
        
        Overrides base class to match pattern used by other MCP servers.
        Handlers use **kwargs, so we call them with **parameters.
        """
        try:
            # Start telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "execute_tool_start",
                        "value": 1.0,
                        "type": "counter",
                        "labels": {"tool_name": tool_name, "mcp_server": self.service_name}
                    })
                except Exception:
                    pass  # Telemetry is optional
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.utilities.security
                if security:
                    if not await security.check_permissions(user_context, f"mcp_tool.{tool_name}", "execute"):
                        raise PermissionError(f"Access denied: insufficient permissions to execute tool '{tool_name}'")
            
            # Tenant validation (multi-tenancy support)
            if user_context:
                tenant = self.utilities.tenant
                if tenant:
                    tenant_id = user_context.get("tenant_id") if isinstance(user_context, dict) else getattr(user_context, "tenant_id", None)
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            raise PermissionError(f"Tenant access denied for tool '{tool_name}': {tenant_id}")
            
            # Map tool names to handlers
            tool_handlers = {
                "create_wave_tool": self._create_wave_tool,
                "select_wave_candidates_tool": self._select_wave_candidates_tool,
                "execute_wave_tool": self._execute_wave_tool,
                "rollback_wave_tool": self._rollback_wave_tool,
                "get_wave_status_tool": self._get_wave_status_tool
            }
            
            handler = tool_handlers.get(tool_name)
            if handler:
                # Add user_context to parameters if not present (for handlers that use **kwargs)
                if user_context and "user_context" not in parameters:
                    parameters["user_context"] = user_context
                
                # Call handler with **parameters (handlers use **kwargs)
                result = await handler(**parameters)
                
                # End telemetry tracking
                if self.utilities.telemetry:
                    try:
                        await self.utilities.telemetry.collect_metric({
                            "name": "execute_tool_complete",
                            "value": 1.0,
                            "type": "counter",
                            "labels": {"tool_name": tool_name, "status": "success" if result.get("success", True) else "failed"}
                        })
                    except Exception:
                        pass
                
                return result
            else:
                # Record health metric (tool not found)
                if self.utilities.health:
                    try:
                        await self.utilities.health.record_metric("execute_tool_not_found", 1.0, {"tool_name": tool_name})
                    except Exception:
                        pass
                
                # End telemetry tracking
                if self.utilities.telemetry:
                    try:
                        await self.utilities.telemetry.collect_metric({
                            "name": "execute_tool_complete",
                            "value": 0.0,
                            "type": "counter",
                            "labels": {"tool_name": tool_name, "status": "not_found"}
                        })
                    except Exception:
                        pass
                
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            # Error handling
            self.logger.error(f"❌ execute_tool failed for {tool_name}: {e}", exc_info=True)
            
            # End telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "execute_tool_complete",
                        "value": 0.0,
                        "type": "counter",
                        "labels": {"tool_name": tool_name, "status": "error"}
                    })
                except Exception:
                    pass
            
            return {"error": f"Failed to execute tool {tool_name}: {str(e)}"}
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return machine + human readable usage guide."""
        return {
            "server_name": "wave_migration_mcp",
            "description": "MCP Server for Wave Orchestrator",
            "version": "1.0.0",
            "tools": {
                "create_wave_tool": {
                    "description": "Create a new migration wave with selection criteria and quality gates.",
                    "use_case": "Plan and define migration waves",
                    "example": {
                        "wave_number": 0,
                        "name": "Wave 0 - Clean Candidates",
                        "description": "First wave with clean, simple policies",
                        "selection_criteria": {"policy_type": "auto", "state": "CA"},
                        "target_system": "NewPlatformAPI"
                    }
                },
                "select_wave_candidates_tool": {
                    "description": "Select policy candidates for a wave based on selection criteria.",
                    "use_case": "Identify policies that match wave criteria",
                    "example": {
                        "wave_id": "wave-uuid-123",
                        "policy_pool": [{"policy_id": "POL-1", "policy_type": "auto"}]
                    }
                },
                "execute_wave_tool": {
                    "description": "Execute a migration wave, migrating all policies with quality gate enforcement.",
                    "use_case": "Run wave migration with automatic quality checks",
                    "example": {
                        "wave_id": "wave-uuid-123"
                    }
                },
                "rollback_wave_tool": {
                    "description": "Rollback a wave migration, compensating all successfully migrated policies.",
                    "use_case": "Undo wave migration if issues are discovered",
                    "example": {
                        "wave_id": "wave-uuid-123"
                    }
                },
                "get_wave_status_tool": {
                    "description": "Get wave status, progress, and statistics.",
                    "use_case": "Monitor wave execution progress",
                    "example": {
                        "wave_id": "wave-uuid-123"
                    }
                }
            },
            "workflow": {
                "typical_flow": [
                    "1. create_wave_tool - Define wave with criteria",
                    "2. select_wave_candidates_tool - Select policies for wave",
                    "3. execute_wave_tool - Execute migration",
                    "4. get_wave_status_tool - Monitor progress",
                    "5. rollback_wave_tool - Rollback if needed (compensation)"
                ],
                "quality_gates": "All waves support quality gate enforcement (data quality, completeness, validation)"
            }
        }
    
    def get_tool_list(self) -> List[str]:
        """Return list of available tool names."""
        return [
            "create_wave_tool",
            "select_wave_candidates_tool",
            "execute_wave_tool",
            "rollback_wave_tool",
            "get_wave_status_tool"
        ]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks."""
        try:
            orchestrator_healthy = self.orchestrator is not None
            
            # Check dependencies
            migration_available = False
            routing_available = False
            
            try:
                migration = await self.orchestrator._get_insurance_migration_orchestrator()
                migration_available = migration is not None
            except:
                pass
            
            try:
                routing = await self.orchestrator._get_routing_engine_service()
                routing_available = routing is not None
            except:
                pass
            
            return {
                "status": "healthy" if orchestrator_healthy else "unhealthy",
                "server": "wave_migration_mcp",
                "orchestrator": {
                    "available": orchestrator_healthy,
                    "name": self.orchestrator.orchestrator_name if orchestrator_healthy else None
                },
                "dependencies": {
                    "insurance_migration_orchestrator": migration_available,
                    "routing_engine_service": routing_available
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_version_info(self) -> Dict[str, Any]:
        """Return version and compatibility info."""
        return {
            "server_name": "wave_migration_mcp",
            "version": "1.0.0",
            "orchestrator": "WaveOrchestrator",
            "realm": "business_enablement",
            "use_case": "insurance_migration",
            "compatible_with": ["symphainy_platform_v1"],
            "tools_count": 5
        }



