#!/usr/bin/env python3
"""
Insurance Migration MCP Server

Wraps Insurance Migration Orchestrator as MCP Tools for agent consumption.

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


class InsuranceMigrationMCPServer(MCPServerBase):
    """
    MCP Server for Insurance Migration Orchestrator (Insurance Use Case).
    
    Provides use case-level tools for agents:
    - ingest_legacy_data_tool: Ingest legacy insurance data files
    - map_to_canonical_tool: Map source data to canonical policy model
    - route_policies_tool: Route policies to target systems based on rules
    
    These are HIGH-LEVEL tools that orchestrate multiple enabling services internally.
    Agents don't need to know about FileParser, CanonicalModelService, RoutingEngineService, etc.
    """
    
    def __init__(self, orchestrator, di_container):
        """
        Initialize Insurance Migration MCP Server.
        
        Args:
            orchestrator: InsuranceMigrationOrchestrator instance
            di_container: DI Container for platform services
        """
        super().__init__(
            service_name="insurance_migration_mcp",
            di_container=di_container
        )
        self.orchestrator = orchestrator
    
    def register_server_tools(self) -> None:
        """Register MCP tools (use case-level, not service-level)."""
        
        # Tool 1: Ingest Legacy Data
        self.register_tool(
            tool_name="ingest_legacy_data_tool",
            handler=self._ingest_legacy_data_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "ID of legacy insurance data file to ingest"
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context for audit trail",
                        "properties": {
                            "user_id": {"type": "string"},
                            "tenant_id": {"type": "string"},
                            "session_id": {"type": "string"}
                        }
                    }
                },
                "required": ["file_id"]
            }
        )
        
        # Tool 2: Map to Canonical
        self.register_tool(
            tool_name="map_to_canonical_tool",
            handler=self._map_to_canonical_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "source_data": {
                        "type": "object",
                        "description": "Source insurance data to map to canonical model"
                    },
                    "mapping_rules": {
                        "type": "object",
                        "description": "Optional custom mapping rules (uses defaults if not provided)",
                        "properties": {}
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context for audit trail",
                        "properties": {
                            "user_id": {"type": "string"},
                            "tenant_id": {"type": "string"},
                            "session_id": {"type": "string"}
                        }
                    }
                },
                "required": ["source_data"]
            }
        )
        
        # Tool 3: Route Policies
        self.register_tool(
            tool_name="route_policies_tool",
            handler=self._route_policies_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "policy_data": {
                        "type": "object",
                        "description": "Policy data to route (must include policy_id and routing keys)",
                        "properties": {
                            "policy_id": {"type": "string"},
                            "policy_type": {"type": "string"},
                            "coverage_type": {"type": "string"},
                            "state": {"type": "string"},
                            "effective_date": {"type": "string"}
                        },
                        "required": ["policy_id"]
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Routing namespace (default: 'default')",
                        "default": "default"
                    },
                    "user_context": {
                        "type": "object",
                        "description": "Optional user context for audit trail",
                        "properties": {
                            "user_id": {"type": "string"},
                            "tenant_id": {"type": "string"},
                            "session_id": {"type": "string"}
                        }
                    }
                },
                "required": ["policy_data"]
            }
        )
        
        # Tool 4: Get Migration Status
        self.register_tool(
            tool_name="get_migration_status_tool",
            handler=self._get_migration_status_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "File ID to check migration status for"
                    },
                    "policy_id": {
                        "type": "string",
                        "description": "Policy ID to check migration status for"
                    }
                }
            }
        )
    
    # ============================================================================
    # TOOL HANDLERS
    # ============================================================================
    
    async def _ingest_legacy_data_tool(self, **kwargs) -> Dict[str, Any]:
        """
        Tool handler: Ingest legacy insurance data.
        
        Delegates to orchestrator.ingest_legacy_data()
        """
        try:
            file_id = kwargs.get("file_id")
            if not file_id:
                return {
                    "success": False,
                    "error": "file_id is required"
                }
            
            user_context = kwargs.get("user_context", {})
            
            # Call orchestrator method
            result = await self.orchestrator.ingest_legacy_data(
                file_id=file_id,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ ingest_legacy_data_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _map_to_canonical_tool(self, **kwargs) -> Dict[str, Any]:
        """
        Tool handler: Map source data to canonical model.
        
        Delegates to orchestrator.map_to_canonical()
        """
        try:
            source_data = kwargs.get("source_data")
            if not source_data:
                return {
                    "success": False,
                    "error": "source_data is required"
                }
            
            mapping_rules = kwargs.get("mapping_rules")
            user_context = kwargs.get("user_context", {})
            
            # Call orchestrator method
            result = await self.orchestrator.map_to_canonical(
                source_data=source_data,
                mapping_rules=mapping_rules,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ map_to_canonical_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _route_policies_tool(self, **kwargs) -> Dict[str, Any]:
        """
        Tool handler: Route policies to target systems.
        
        Delegates to orchestrator.route_policies()
        """
        try:
            policy_data = kwargs.get("policy_data")
            if not policy_data:
                return {
                    "success": False,
                    "error": "policy_data is required"
                }
            
            namespace = kwargs.get("namespace", "default")
            user_context = kwargs.get("user_context", {})
            
            # Call orchestrator method
            result = await self.orchestrator.route_policies(
                policy_data=policy_data,
                namespace=namespace,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ route_policies_tool failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_migration_status_tool(self, **kwargs) -> Dict[str, Any]:
        """
        Tool handler: Get migration status for file or policy.
        
        This is a convenience tool to check migration progress.
        """
        try:
            file_id = kwargs.get("file_id")
            policy_id = kwargs.get("policy_id")
            
            if not file_id and not policy_id:
                return {
                    "success": False,
                    "error": "Either file_id or policy_id is required"
                }
            
            # TODO: Implement status tracking (will be added when Policy Tracker is created)
            # For now, return a placeholder
            return {
                "success": True,
                "message": "Migration status tracking will be available after Policy Tracker implementation",
                "file_id": file_id,
                "policy_id": policy_id,
                "status": "pending_implementation"
            }
            
        except Exception as e:
            self.logger.error(f"❌ get_migration_status_tool failed: {e}", exc_info=True)
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
                "ingest_legacy_data_tool": self._ingest_legacy_data_tool,
                "map_to_canonical_tool": self._map_to_canonical_tool,
                "route_policies_tool": self._route_policies_tool,
                "get_migration_status_tool": self._get_migration_status_tool
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
            "server_name": "insurance_migration_mcp",
            "description": "MCP Server for Insurance Migration Orchestrator",
            "version": "1.0.0",
            "tools": {
                "ingest_legacy_data_tool": {
                    "description": "Ingest legacy insurance data files. Parses files and prepares for migration.",
                    "use_case": "Start migration by ingesting legacy data files",
                    "example": {
                        "file_id": "file-uuid-123",
                        "user_context": {"user_id": "user-123", "tenant_id": "tenant-abc"}
                    }
                },
                "map_to_canonical_tool": {
                    "description": "Map source insurance data to canonical policy model. Transforms legacy format to standard format.",
                    "use_case": "Transform legacy data to canonical model for routing",
                    "example": {
                        "source_data": {"policy_number": "POL-123", "coverage": "auto"},
                        "mapping_rules": {}
                    }
                },
                "route_policies_tool": {
                    "description": "Route policies to target systems based on routing rules. Determines which target system should receive the policy.",
                    "use_case": "Route migrated policies to appropriate target systems",
                    "example": {
                        "policy_data": {
                            "policy_id": "POL-123",
                            "policy_type": "auto",
                            "state": "CA",
                            "coverage_type": "comprehensive"
                        },
                        "namespace": "default"
                    }
                },
                "get_migration_status_tool": {
                    "description": "Get migration status for a file or policy. Tracks progress through migration pipeline.",
                    "use_case": "Check migration progress and status",
                    "example": {
                        "file_id": "file-uuid-123"
                    }
                }
            },
            "workflow": {
                "typical_flow": [
                    "1. ingest_legacy_data_tool - Ingest legacy files",
                    "2. map_to_canonical_tool - Transform to canonical model",
                    "3. route_policies_tool - Route to target systems",
                    "4. get_migration_status_tool - Check status"
                ],
                "compensation": "All operations are logged to WAL and support Saga compensation handlers"
            }
        }
    
    def get_tool_list(self) -> List[str]:
        """Return list of available tool names."""
        return [
            "ingest_legacy_data_tool",
            "map_to_canonical_tool",
            "route_policies_tool",
            "get_migration_status_tool"
        ]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks."""
        try:
            # Check orchestrator availability
            orchestrator_healthy = self.orchestrator is not None
            
            # Check enabling services (lazy check)
            canonical_available = False
            routing_available = False
            file_parser_available = False
            
            try:
                canonical = await self.orchestrator._get_canonical_model_service()
                canonical_available = canonical is not None
            except:
                pass
            
            try:
                routing = await self.orchestrator._get_routing_engine_service()
                routing_available = routing is not None
            except:
                pass
            
            try:
                file_parser = await self.orchestrator.get_enabling_service("FileParserService")
                file_parser_available = file_parser is not None
            except:
                pass
            
            return {
                "status": "healthy" if orchestrator_healthy else "unhealthy",
                "server": "insurance_migration_mcp",
                "orchestrator": {
                    "available": orchestrator_healthy,
                    "name": self.orchestrator.orchestrator_name if orchestrator_healthy else None
                },
                "dependencies": {
                    "canonical_model_service": canonical_available,
                    "routing_engine_service": routing_available,
                    "file_parser_service": file_parser_available
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
            "server_name": "insurance_migration_mcp",
            "version": "1.0.0",
            "orchestrator": "InsuranceMigrationOrchestrator",
            "realm": "business_enablement",
            "use_case": "insurance_migration",
            "compatible_with": ["symphainy_platform_v1"],
            "tools_count": 4
        }



