#!/usr/bin/env python3
"""
Policy Tracker MCP Server

Wraps Policy Tracker Orchestrator as MCP Tools for agent consumption.

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


class PolicyTrackerMCPServer(MCPServerBase):
    """
    MCP Server for Policy Tracker Orchestrator (Insurance Use Case).
    
    Provides use case-level tools for agents:
    - register_policy_tool: Register a policy in the tracking system
    - update_migration_status_tool: Update migration status for a policy
    - get_policy_location_tool: Get current location and status of a policy
    - validate_migration_tool: Validate a policy migration
    - reconcile_systems_tool: Reconcile policies between two systems
    - get_policies_by_location_tool: Get all policies at a specific location
    
    These are HIGH-LEVEL tools that orchestrate multiple services internally.
    """
    
    def __init__(self, orchestrator, di_container):
        """
        Initialize Policy Tracker MCP Server.
        
        Args:
            orchestrator: PolicyTrackerOrchestrator instance
            di_container: DI Container for platform services
        """
        super().__init__(
            service_name="policy_tracker_mcp",
            di_container=di_container
        )
        self.orchestrator = orchestrator
    
    def register_server_tools(self) -> None:
        """Register MCP tools (use case-level, not service-level)."""
        
        # Tool 1: Register Policy
        self.register_tool(
            tool_name="register_policy_tool",
            handler=self._register_policy_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "policy_id": {
                        "type": "string",
                        "description": "Policy identifier"
                    },
                    "location": {
                        "type": "string",
                        "enum": ["legacy_system", "new_system", "in_transit", "coexistence", "unknown"],
                        "description": "Current location of the policy"
                    },
                    "system_id": {
                        "type": "string",
                        "description": "System identifier (if applicable)"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional policy metadata"
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context"
                    }
                },
                "required": ["policy_id", "location"]
            }
        )
        
        # Tool 2: Update Migration Status
        self.register_tool(
            tool_name="update_migration_status_tool",
            handler=self._update_migration_status_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "policy_id": {
                        "type": "string",
                        "description": "Policy identifier"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["not_started", "in_progress", "completed", "failed", "rolled_back", "validated"],
                        "description": "Migration status"
                    },
                    "wave_id": {
                        "type": "string",
                        "description": "Optional wave ID if part of a wave"
                    },
                    "details": {
                        "type": "object",
                        "description": "Optional status details"
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context"
                    }
                },
                "required": ["policy_id", "status"]
            }
        )
        
        # Tool 3: Get Policy Location
        self.register_tool(
            tool_name="get_policy_location_tool",
            handler=self._get_policy_location_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "policy_id": {
                        "type": "string",
                        "description": "Policy identifier"
                    }
                },
                "required": ["policy_id"]
            }
        )
        
        # Tool 4: Validate Migration
        self.register_tool(
            tool_name="validate_migration_tool",
            handler=self._validate_migration_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "policy_id": {
                        "type": "string",
                        "description": "Policy identifier"
                    },
                    "validation_rules": {
                        "type": "array",
                        "description": "Optional custom validation rules",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["location_check", "status_check", "data_integrity"]
                                },
                                "description": {"type": "string"},
                                "expected_location": {"type": "string"},
                                "expected_status": {"type": "string"}
                            }
                        }
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context"
                    }
                },
                "required": ["policy_id"]
            }
        )
        
        # Tool 5: Reconcile Systems
        self.register_tool(
            tool_name="reconcile_systems_tool",
            handler=self._reconcile_systems_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "system_a": {
                        "type": "string",
                        "description": "First system identifier"
                    },
                    "system_b": {
                        "type": "string",
                        "description": "Second system identifier"
                    },
                    "policy_ids": {
                        "type": "array",
                        "description": "Optional list of policy IDs to reconcile (all if not provided)",
                        "items": {"type": "string"}
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context"
                    }
                },
                "required": ["system_a", "system_b"]
            }
        )
        
        # Tool 6: Get Policies by Location
        self.register_tool(
            tool_name="get_policies_by_location_tool",
            handler=self._get_policies_by_location_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "enum": ["legacy_system", "new_system", "in_transit", "coexistence", "unknown"],
                        "description": "Policy location to filter by"
                    },
                    "system_id": {
                        "type": "string",
                        "description": "Optional system ID to filter by"
                    }
                },
                "required": ["location"]
            }
        )
    
    # ============================================================================
    # TOOL HANDLERS
    # ============================================================================
    
    async def _register_policy_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Register a policy in the tracking system."""
        try:
            from .policy_tracker_orchestrator import PolicyLocation
            
            policy_id = kwargs.get("policy_id")
            location_str = kwargs.get("location")
            
            if not policy_id or not location_str:
                return {
                    "success": False,
                    "error": "policy_id and location are required"
                }
            
            try:
                location = PolicyLocation(location_str)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid location: {location_str}"
                }
            
            system_id = kwargs.get("system_id")
            metadata = kwargs.get("metadata")
            user_context = kwargs.get("user_context", {})
            
            result = await self.orchestrator.register_policy(
                policy_id=policy_id,
                location=location,
                system_id=system_id,
                metadata=metadata,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ register_policy_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_migration_status_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Update migration status for a policy."""
        try:
            from ..policy_tracker_orchestrator import MigrationStatus
            
            policy_id = kwargs.get("policy_id")
            status_str = kwargs.get("status")
            
            if not policy_id or not status_str:
                return {
                    "success": False,
                    "error": "policy_id and status are required"
                }
            
            try:
                status = MigrationStatus(status_str)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid status: {status_str}"
                }
            
            wave_id = kwargs.get("wave_id")
            details = kwargs.get("details")
            user_context = kwargs.get("user_context", {})
            
            result = await self.orchestrator.update_migration_status(
                policy_id=policy_id,
                status=status,
                wave_id=wave_id,
                details=details,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ update_migration_status_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_policy_location_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Get current location and status of a policy."""
        try:
            policy_id = kwargs.get("policy_id")
            if not policy_id:
                return {
                    "success": False,
                    "error": "policy_id is required"
                }
            
            result = await self.orchestrator.get_policy_location(policy_id=policy_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ get_policy_location_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _validate_migration_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Validate a policy migration."""
        try:
            policy_id = kwargs.get("policy_id")
            if not policy_id:
                return {
                    "success": False,
                    "error": "policy_id is required"
                }
            
            validation_rules = kwargs.get("validation_rules")
            user_context = kwargs.get("user_context", {})
            
            result = await self.orchestrator.validate_migration(
                policy_id=policy_id,
                validation_rules=validation_rules,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ validate_migration_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _reconcile_systems_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Reconcile policies between two systems."""
        try:
            system_a = kwargs.get("system_a")
            system_b = kwargs.get("system_b")
            
            if not system_a or not system_b:
                return {
                    "success": False,
                    "error": "system_a and system_b are required"
                }
            
            policy_ids = kwargs.get("policy_ids")
            user_context = kwargs.get("user_context", {})
            
            result = await self.orchestrator.reconcile_systems(
                system_a=system_a,
                system_b=system_b,
                policy_ids=policy_ids,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ reconcile_systems_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_policies_by_location_tool(self, **kwargs) -> Dict[str, Any]:
        """Tool handler: Get all policies at a specific location."""
        try:
            from ..policy_tracker_orchestrator import PolicyLocation
            
            location_str = kwargs.get("location")
            if not location_str:
                return {
                    "success": False,
                    "error": "location is required"
                }
            
            try:
                location = PolicyLocation(location_str)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid location: {location_str}"
                }
            
            system_id = kwargs.get("system_id")
            
            result = await self.orchestrator.get_policies_by_location(
                location=location,
                system_id=system_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ get_policies_by_location_tool failed: {e}", exc_info=True)
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
                "register_policy_tool": self._register_policy_tool,
                "update_migration_status_tool": self._update_migration_status_tool,
                "get_policy_location_tool": self._get_policy_location_tool,
                "validate_migration_tool": self._validate_migration_tool,
                "reconcile_systems_tool": self._reconcile_systems_tool,
                "get_policies_by_location_tool": self._get_policies_by_location_tool
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
            "server_name": "policy_tracker_mcp",
            "description": "MCP Server for Policy Tracker Orchestrator",
            "version": "1.0.0",
            "tools": {
                "register_policy_tool": {
                    "description": "Register a policy in the tracking system with its current location.",
                    "use_case": "Track policy location when first discovered or migrated",
                    "example": {
                        "policy_id": "POL-12345",
                        "location": "legacy_system",
                        "system_id": "LegacyMainframe"
                    }
                },
                "update_migration_status_tool": {
                    "description": "Update migration status for a policy (not_started, in_progress, completed, etc.).",
                    "use_case": "Track migration progress through lifecycle",
                    "example": {
                        "policy_id": "POL-12345",
                        "status": "completed",
                        "wave_id": "wave-uuid-123"
                    }
                },
                "get_policy_location_tool": {
                    "description": "Get current location and status of a policy. Answers 'Where is policy X?'",
                    "use_case": "Query policy location and migration status",
                    "example": {
                        "policy_id": "POL-12345"
                    }
                },
                "validate_migration_tool": {
                    "description": "Validate a policy migration, checking data integrity and location.",
                    "use_case": "Verify migration completed successfully",
                    "example": {
                        "policy_id": "POL-12345",
                        "validation_rules": []
                    }
                },
                "reconcile_systems_tool": {
                    "description": "Reconcile policies between two systems, identifying discrepancies.",
                    "use_case": "Cross-system reconciliation and audit",
                    "example": {
                        "system_a": "LegacyMainframe",
                        "system_b": "NewPlatformAPI",
                        "policy_ids": ["POL-12345", "POL-67890"]
                    }
                },
                "get_policies_by_location_tool": {
                    "description": "Get all policies at a specific location (legacy_system, new_system, etc.).",
                    "use_case": "Query policies by location for reporting and analysis",
                    "example": {
                        "location": "new_system",
                        "system_id": "NewPlatformAPI"
                    }
                }
            },
            "workflow": {
                "typical_flow": [
                    "1. register_policy_tool - Register policy when discovered",
                    "2. update_migration_status_tool - Track migration progress",
                    "3. validate_migration_tool - Validate after migration",
                    "4. get_policy_location_tool - Query location anytime",
                    "5. reconcile_systems_tool - Periodic reconciliation"
                ],
                "locations": [
                    "legacy_system - Policy in legacy system only",
                    "new_system - Policy in new system only",
                    "in_transit - Policy being migrated",
                    "coexistence - Policy exists in both systems",
                    "unknown - Location not yet determined"
                ]
            }
        }
    
    def get_tool_list(self) -> List[str]:
        """Return list of available tool names."""
        return [
            "register_policy_tool",
            "update_migration_status_tool",
            "get_policy_location_tool",
            "validate_migration_tool",
            "reconcile_systems_tool",
            "get_policies_by_location_tool"
        ]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks."""
        try:
            orchestrator_healthy = self.orchestrator is not None
            
            return {
                "status": "healthy" if orchestrator_healthy else "unhealthy",
                "server": "policy_tracker_mcp",
                "orchestrator": {
                    "available": orchestrator_healthy,
                    "name": self.orchestrator.orchestrator_name if orchestrator_healthy else None
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
            "server_name": "policy_tracker_mcp",
            "version": "1.0.0",
            "orchestrator": "PolicyTrackerOrchestrator",
            "realm": "business_enablement",
            "use_case": "insurance_migration",
            "compatible_with": ["symphainy_platform_v1"],
            "tools_count": 6
        }

