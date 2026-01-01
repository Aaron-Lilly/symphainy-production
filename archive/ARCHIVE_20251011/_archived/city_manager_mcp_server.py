#!/usr/bin/env python3
"""
City Manager MCP Server

Exposes City Manager service capabilities as MCP tools for agent integration with multi-tenant awareness.

WHAT (MCP Server Role): I expose City Manager governance capabilities as tools with tenant context
HOW (MCP Server Implementation): I provide MCP tools for tenant-aware policy management, resource allocation, governance enforcement, strategic coordination, city health monitoring, and emergency coordination
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.smart_city.protocols.smart_city_service_base import SmartCityServiceBase
from backend.smart_city.protocols.mcp_server_protocol import MCPServerProtocol, MCPTool, MCPServerInfo
from config.environment_loader import EnvironmentLoader
from config import Environment
from utilities import UserContext

from ..city_manager_service import CityManagerService


class CityManagerMCPServer(SmartCityServiceBase):
    """
    City Manager MCP Server - Multi-Tenant Smart City Governance Hub
    
    Exposes City Manager service capabilities as MCP tools for agent integration
    with proper tenant isolation and security integration.
    """
    
    def __init__(self, utility_foundation, curator_foundation=None, 
                 public_works_foundation=None, environment=Environment.DEVELOPMENT):
        """Initialize City Manager MCP Server with multi-tenant capabilities."""
        super().__init__("CityManagerMCPServer", utility_foundation, curator_foundation)
        
        self.public_works_foundation = public_works_foundation
        self.environment = environment
        
        # Initialize City Manager service with multi-tenant capabilities
        self.city_manager_service = CityManagerService(
            utility_foundation=utility_foundation,
            curator_foundation=curator_foundation,
            public_works_foundation=public_works_foundation,
            environment=environment
        )
        
        # Initialize MCP protocol
        self.mcp_protocol = CityManagerMCPProtocol("CityManagerMCPServer", self, curator_foundation)
        
        # Initialize MCP server info
        self.server_info = MCPServerInfo(
            server_name="CityManagerMCPServer",
            interface_name="city_manager_governance",
            version="1.0.0",
            description="City Manager MCP Server for Multi-Tenant Smart City Governance",
            tools=[]
        )
    
    async def initialize(self):
        """Initialize the MCP server and protocol."""
        try:
            # Initialize MCP protocol
            await self.mcp_protocol.initialize()
            self.logger.info("✅ MCP Protocol initialized")
            
            # Initialize City Manager service
            await self.city_manager_service.initialize()
            self.logger.info("✅ City Manager Service initialized")
            
            self.logger.info("✅ City Manager MCP Server initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize City Manager MCP Server: {e}")
            raise
        
        # Register tools
        self.tools = self.register_tools()
        self.server_info.tools = self.tools
        
        # Use utility foundation logger
        self.logger = utility_foundation.logger
        self.logger.info("🏛️ City Manager MCP Server initialized with multi-tenant capabilities")
    
    def register_tools(self) -> List[MCPTool]:
        """Register all City Manager MCP tools."""
        return [
            # Policy Management Tools
            MCPTool(
                name="create_city_policy",
                description="Create a new city-wide policy",
                input_schema={
                    "type": "object",
                    "properties": {
                        "policy_definition": {
                            "type": "object",
                            "description": "Policy definition including rules and enforcement settings"
                        }
                    },
                    "required": ["policy_definition"]
                },
                handler=self._handle_create_city_policy,
                tags=["policy", "governance", "create"]
            ),
            MCPTool(
                name="enforce_city_policy",
                description="Enforce a city policy against a context",
                input_schema={
                    "type": "object",
                    "properties": {
                        "policy_id": {"type": "string", "description": "ID of the policy to enforce"},
                        "context": {"type": "object", "description": "Context to validate against the policy"}
                    },
                    "required": ["policy_id", "context"]
                },
                handler=self._handle_enforce_city_policy,
                tags=["policy", "governance", "enforce"]
            ),
            MCPTool(
                name="list_city_policies",
                description="List all city policies",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filter_criteria": {
                            "type": "object",
                            "description": "Optional filter criteria for policies"
                        }
                    }
                },
                handler=self._handle_list_city_policies,
                tags=["policy", "governance", "list"]
            ),
            
            # Resource Allocation Tools
            MCPTool(
                name="allocate_city_resources",
                description="Allocate resources for city operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "allocation_request": {
                            "type": "object",
                            "description": "Resource allocation request including resources and budget"
                        }
                    },
                    "required": ["allocation_request"]
                },
                handler=self._handle_allocate_city_resources,
                tags=["resources", "allocation", "budget"]
            ),
            MCPTool(
                name="get_city_budget_status",
                description="Get current city budget status",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_city_budget_status,
                tags=["resources", "budget", "status"]
            ),
            MCPTool(
                name="optimize_city_resources",
                description="Optimize current resource allocations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "optimization_criteria": {
                            "type": "object",
                            "description": "Criteria for resource optimization"
                        }
                    },
                    "required": ["optimization_criteria"]
                },
                handler=self._handle_optimize_city_resources,
                tags=["resources", "optimization"]
            ),
            
            # Governance Enforcement Tools
            MCPTool(
                name="check_city_compliance",
                description="Check compliance for a specific component and governance layer",
                input_schema={
                    "type": "object",
                    "properties": {
                        "component_id": {"type": "string", "description": "ID of the component to check"},
                        "governance_layer": {"type": "string", "description": "Governance layer to check against"},
                        "component_data": {"type": "object", "description": "Component data to validate"}
                    },
                    "required": ["component_id", "governance_layer", "component_data"]
                },
                handler=self._handle_check_city_compliance,
                tags=["governance", "compliance", "check"]
            ),
            MCPTool(
                name="run_city_governance_audit",
                description="Run a comprehensive city governance audit",
                input_schema={
                    "type": "object",
                    "properties": {
                        "audit_scope": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional scope of the audit"
                        }
                    }
                },
                handler=self._handle_run_city_governance_audit,
                tags=["governance", "audit", "compliance"]
            ),
            MCPTool(
                name="get_governance_violations",
                description="Get governance violations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filter_criteria": {
                            "type": "object",
                            "description": "Optional filter criteria for violations"
                        }
                    }
                },
                handler=self._handle_get_governance_violations,
                tags=["governance", "violations", "compliance"]
            ),
            
            # Strategic Coordination Tools
            MCPTool(
                name="create_coordination_plan",
                description="Create a strategic coordination plan",
                input_schema={
                    "type": "object",
                    "properties": {
                        "business_operation": {"type": "string", "description": "Business operation to coordinate"},
                        "parameters": {"type": "object", "description": "Parameters for the coordination plan"}
                    },
                    "required": ["business_operation", "parameters"]
                },
                handler=self._handle_create_coordination_plan,
                tags=["coordination", "strategic", "planning"]
            ),
            MCPTool(
                name="coordinate_city_roles",
                description="Coordinate operations between multiple city roles",
                input_schema={
                    "type": "object",
                    "properties": {
                        "coordination_request": {
                            "type": "object",
                            "description": "Coordination request including roles and operations"
                        }
                    },
                    "required": ["coordination_request"]
                },
                handler=self._handle_coordinate_city_roles,
                tags=["coordination", "roles", "cross-role"]
            ),
            MCPTool(
                name="orchestrate_city_workflow",
                description="Orchestrate a city-wide workflow",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow_definition": {
                            "type": "object",
                            "description": "Workflow definition including steps and participants"
                        }
                    },
                    "required": ["workflow_definition"]
                },
                handler=self._handle_orchestrate_city_workflow,
                tags=["coordination", "workflow", "orchestration"]
            ),
            MCPTool(
                name="get_city_state_summary",
                description="Get summary of current city state",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_city_state_summary,
                tags=["coordination", "state", "summary"]
            ),
            
            # City Health Monitoring Tools
            MCPTool(
                name="check_city_health",
                description="Check overall city health status",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_check_city_health,
                tags=["health", "monitoring", "status"]
            ),
            MCPTool(
                name="get_city_health_status",
                description="Get current city health status",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_city_health_status,
                tags=["health", "monitoring", "status"]
            ),
            MCPTool(
                name="monitor_service_health",
                description="Monitor health of a specific service",
                input_schema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string", "description": "ID of the service to monitor"},
                        "service_data": {"type": "object", "description": "Service data for health monitoring"}
                    },
                    "required": ["service_id", "service_data"]
                },
                handler=self._handle_monitor_service_health,
                tags=["health", "monitoring", "service"]
            ),
            MCPTool(
                name="get_health_alerts",
                description="Get city health alerts",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filter_criteria": {
                            "type": "object",
                            "description": "Optional filter criteria for health alerts"
                        }
                    }
                },
                handler=self._handle_get_health_alerts,
                tags=["health", "alerts", "monitoring"]
            ),
            
            # Emergency Coordination Tools
            MCPTool(
                name="detect_emergency",
                description="Detect and initiate emergency response",
                input_schema={
                    "type": "object",
                    "properties": {
                        "emergency_data": {
                            "type": "object",
                            "description": "Emergency data including type, severity, and description"
                        }
                    },
                    "required": ["emergency_data"]
                },
                handler=self._handle_detect_emergency,
                tags=["emergency", "detection", "response"]
            ),
            MCPTool(
                name="coordinate_emergency_response",
                description="Coordinate emergency response across city roles",
                input_schema={
                    "type": "object",
                    "properties": {
                        "emergency_id": {"type": "string", "description": "ID of the emergency"},
                        "coordination_request": {
                            "type": "object",
                            "description": "Coordination request for emergency response"
                        }
                    },
                    "required": ["emergency_id", "coordination_request"]
                },
                handler=self._handle_coordinate_emergency_response,
                tags=["emergency", "coordination", "response"]
            ),
            MCPTool(
                name="get_active_emergencies",
                description="Get all active emergencies",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_active_emergencies,
                tags=["emergency", "status", "active"]
            ),
            
            # Comprehensive City Management Tools
            MCPTool(
                name="get_city_overview",
                description="Get comprehensive city overview",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_city_overview,
                tags=["overview", "comprehensive", "status"]
            ),
            MCPTool(
                name="run_city_maintenance",
                description="Run comprehensive city maintenance",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_run_city_maintenance,
                tags=["maintenance", "comprehensive", "health"]
            ),
            
            # Multi-Tenant Specific Tools
            MCPTool(
                name="get_tenant_policies",
                description="Get all policies for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "ID of the tenant"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_policies,
                tags=["tenant", "policies", "multi-tenant"]
            ),
            MCPTool(
                name="get_tenant_resource_usage",
                description="Get resource usage for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "ID of the tenant"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_resource_usage,
                tags=["tenant", "resources", "multi-tenant"]
            ),
            MCPTool(
                name="get_tenant_governance_summary",
                description="Get governance summary for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "ID of the tenant"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_governance_summary,
                tags=["tenant", "governance", "multi-tenant"]
            )
        ]
    
    # ============================================================================
    # POLICY MANAGEMENT HANDLERS
    # ============================================================================
    
    async def _handle_create_city_policy(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle create_city_policy tool with tenant awareness."""
        try:
            # Convert user_context dict to UserContext object if needed
            user_ctx = None
            if user_context:
                user_ctx = UserContext(
                    user_id=user_context.get("user_id"),
                    email=user_context.get("email"),
                    full_name=user_context.get("full_name"),
                    session_id=user_context.get("session_id"),
                    permissions=user_context.get("permissions", []),
                    tenant_id=user_context.get("tenant_id")
                )
            
            return await self.city_manager_service.create_city_policy(
                arguments["policy_definition"], user_ctx
            )
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="mcp_create_city_policy")
            return {"success": False, "error": str(e)}
    
    async def _handle_enforce_city_policy(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle enforce_city_policy tool with tenant awareness."""
        try:
            # Convert user_context dict to UserContext object if needed
            user_ctx = None
            if user_context:
                user_ctx = UserContext(
                    user_id=user_context.get("user_id"),
                    email=user_context.get("email"),
                    full_name=user_context.get("full_name"),
                    session_id=user_context.get("session_id"),
                    permissions=user_context.get("permissions", []),
                    tenant_id=user_context.get("tenant_id")
                )
            
            return await self.city_manager_service.enforce_city_policy(
                arguments["policy_id"], arguments["context"], user_ctx
            )
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="mcp_enforce_city_policy")
            return {"success": False, "error": str(e)}
    
    async def _handle_list_city_policies(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle list_city_policies tool with tenant awareness."""
        try:
            # Convert user_context dict to UserContext object if needed
            user_ctx = None
            if user_context:
                user_ctx = UserContext(
                    user_id=user_context.get("user_id"),
                    email=user_context.get("email"),
                    full_name=user_context.get("full_name"),
                    session_id=user_context.get("session_id"),
                    permissions=user_context.get("permissions", []),
                    tenant_id=user_context.get("tenant_id")
                )
            
            filter_criteria = arguments.get("filter_criteria")
            return await self.city_manager_service.list_city_policies(filter_criteria, user_ctx)
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="mcp_list_city_policies")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # RESOURCE ALLOCATION HANDLERS
    # ============================================================================
    
    async def _handle_allocate_city_resources(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle allocate_city_resources tool."""
        return await self.city_manager_service.allocate_city_resources(arguments["allocation_request"])
    
    async def _handle_get_city_budget_status(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_city_budget_status tool."""
        return await self.city_manager_service.get_city_budget_status()
    
    async def _handle_optimize_city_resources(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle optimize_city_resources tool."""
        return await self.city_manager_service.optimize_city_resources(arguments["optimization_criteria"])
    
    # ============================================================================
    # GOVERNANCE ENFORCEMENT HANDLERS
    # ============================================================================
    
    async def _handle_check_city_compliance(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle check_city_compliance tool."""
        return await self.city_manager_service.check_city_compliance(
            arguments["component_id"], 
            arguments["governance_layer"], 
            arguments["component_data"]
        )
    
    async def _handle_run_city_governance_audit(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle run_city_governance_audit tool."""
        audit_scope = arguments.get("audit_scope")
        return await self.city_manager_service.run_city_governance_audit(audit_scope)
    
    async def _handle_get_governance_violations(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_governance_violations tool."""
        filter_criteria = arguments.get("filter_criteria")
        return await self.city_manager_service.get_governance_violations(filter_criteria)
    
    # ============================================================================
    # STRATEGIC COORDINATION HANDLERS
    # ============================================================================
    
    async def _handle_create_coordination_plan(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle create_coordination_plan tool."""
        return await self.city_manager_service.create_coordination_plan(
            arguments["business_operation"], 
            arguments["parameters"]
        )
    
    async def _handle_coordinate_city_roles(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle coordinate_city_roles tool."""
        return await self.city_manager_service.coordinate_city_roles(arguments["coordination_request"])
    
    async def _handle_orchestrate_city_workflow(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle orchestrate_city_workflow tool."""
        return await self.city_manager_service.orchestrate_city_workflow(arguments["workflow_definition"])
    
    async def _handle_get_city_state_summary(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_city_state_summary tool."""
        return await self.city_manager_service.get_city_state_summary()
    
    # ============================================================================
    # CITY HEALTH MONITORING HANDLERS
    # ============================================================================
    
    async def _handle_check_city_health(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle check_city_health tool."""
        return await self.city_manager_service.check_city_health()
    
    async def _handle_get_city_health_status(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_city_health_status tool."""
        return await self.city_manager_service.get_city_health_status()
    
    async def _handle_monitor_service_health(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle monitor_service_health tool."""
        return await self.city_manager_service.monitor_service_health(
            arguments["service_id"], 
            arguments["service_data"]
        )
    
    async def _handle_get_health_alerts(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_health_alerts tool."""
        filter_criteria = arguments.get("filter_criteria")
        return await self.city_manager_service.get_health_alerts(filter_criteria)
    
    # ============================================================================
    # EMERGENCY COORDINATION HANDLERS
    # ============================================================================
    
    async def _handle_detect_emergency(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle detect_emergency tool."""
        return await self.city_manager_service.detect_emergency(arguments["emergency_data"])
    
    async def _handle_coordinate_emergency_response(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle coordinate_emergency_response tool."""
        return await self.city_manager_service.coordinate_emergency_response(
            arguments["emergency_id"], 
            arguments["coordination_request"]
        )
    
    async def _handle_get_active_emergencies(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_active_emergencies tool."""
        return await self.city_manager_service.get_active_emergencies()
    
    # ============================================================================
    # COMPREHENSIVE CITY MANAGEMENT HANDLERS
    # ============================================================================
    
    async def _handle_get_city_overview(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_city_overview tool."""
        return await self.city_manager_service.get_city_overview()
    
    async def _handle_run_city_maintenance(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle run_city_maintenance tool."""
        return await self.city_manager_service.run_city_maintenance()
    
    # ============================================================================
    # MCP SERVER LIFECYCLE
    # ============================================================================
    
    async def initialize_service_integration(self) -> bool:
        """Initialize service integration."""
        try:
            # Initialize City Manager service
            self.logger.info("🏛️ Initializing City Manager service integration")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize City Manager service integration: {e}")
            return False
    
    def get_server_info(self) -> MCPServerInfo:
        """Get MCP server information."""
        return self.server_info
    
    # ============================================================================
    # MULTI-TENANT SPECIFIC HANDLERS
    # ============================================================================
    
    async def _handle_get_tenant_policies(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_tenant_policies tool with tenant awareness."""
        try:
            # Convert user_context dict to UserContext object if needed
            user_ctx = None
            if user_context:
                user_ctx = UserContext(
                    user_id=user_context.get("user_id"),
                    email=user_context.get("email"),
                    full_name=user_context.get("full_name"),
                    session_id=user_context.get("session_id"),
                    permissions=user_context.get("permissions", []),
                    tenant_id=user_context.get("tenant_id")
                )
            
            return await self.city_manager_service.get_tenant_policies(
                arguments["tenant_id"], user_ctx
            )
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="mcp_get_tenant_policies")
            return {"success": False, "error": str(e)}
    
    async def _handle_get_tenant_resource_usage(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_tenant_resource_usage tool with tenant awareness."""
        try:
            # Convert user_context dict to UserContext object if needed
            user_ctx = None
            if user_context:
                user_ctx = UserContext(
                    user_id=user_context.get("user_id"),
                    email=user_context.get("email"),
                    full_name=user_context.get("full_name"),
                    session_id=user_context.get("session_id"),
                    permissions=user_context.get("permissions", []),
                    tenant_id=user_context.get("tenant_id")
                )
            
            return await self.city_manager_service.get_tenant_resource_usage(
                arguments["tenant_id"], user_ctx
            )
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="mcp_get_tenant_resource_usage")
            return {"success": False, "error": str(e)}
    
    async def _handle_get_tenant_governance_summary(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_tenant_governance_summary tool with tenant awareness."""
        try:
            # Convert user_context dict to UserContext object if needed
            user_ctx = None
            if user_context:
                user_ctx = UserContext(
                    user_id=user_context.get("user_id"),
                    email=user_context.get("email"),
                    full_name=user_context.get("full_name"),
                    session_id=user_context.get("session_id"),
                    permissions=user_context.get("permissions", []),
                    tenant_id=user_context.get("tenant_id")
                )
            
            return await self.city_manager_service.get_tenant_governance_summary(
                arguments["tenant_id"], user_ctx
            )
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="mcp_get_tenant_governance_summary")
            return {"success": False, "error": str(e)}


class CityManagerMCPProtocol(MCPServerProtocol):
    """MCP Protocol implementation for City Manager MCP Server."""
    
    def __init__(self, server_name: str, server_instance, curator_foundation=None):
        """Initialize City Manager MCP Protocol."""
        super().__init__(server_name, None, curator_foundation)
        self.server_instance = server_instance
        self.server_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the MCP server."""
        # Create server info with multi-tenant metadata
        self.server_info = MCPServerInfo(
            server_name="CityManagerMCPServer",
            version="1.0.0",
            description="City Manager MCP Server - Multi-tenant smart city governance and coordination tools",
            interface_name="ICityManagerMCP",
            tools=self._create_all_tools(),
            capabilities=["governance", "coordination", "multi-tenant", "city-management"],
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_server_info(self) -> MCPServerInfo:
        """Get server information for MCP manifest generation."""
        return self.server_info
    
    def get_tools(self) -> List[MCPTool]:
        """Get all available MCP tools."""
        return self.server_info.tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Execute an MCP tool with given parameters."""
        # Find the tool
        tool = None
        for t in self.server_info.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            return self._create_error_response(f"Tool '{tool_name}' not found", "TOOL_NOT_FOUND")
        
        # Validate tenant context if required
        if tool.requires_tenant:
            validation = self._validate_tenant_context(user_context, tool)
            if not validation["valid"]:
                return self._create_error_response(validation["error"], "TENANT_CONTEXT_REQUIRED")
        
        try:
            # Execute the tool handler
            result = await tool.handler(parameters, user_context)
            return self._create_success_response(result)
        except Exception as e:
            return self._create_error_response(str(e), "TOOL_EXECUTION_ERROR")
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this server with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.server_info.interface_name,
                "endpoints": [],  # MCP servers don't have HTTP endpoints
                "tools": [tool.name for tool in self.server_info.tools],
                "description": self.server_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.server_info.multi_tenant_enabled,
                "tenant_isolation_level": self.server_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.server_name,
                capability,
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_tools(self) -> List[MCPTool]:
        """Create all tools for City Manager MCP Server."""
        tools = []
        
        # Standard tools
        tools.extend(self._create_standard_tools())
        tools.extend(self._create_tenant_aware_tools())
        
        # City Manager specific tools
        tools.extend([
            MCPTool(
                name="create_city_policy",
                description="Create a new city governance policy",
                input_schema={
                    "type": "object",
                    "properties": {
                        "policy_definition": {"type": "object", "description": "Policy definition"}
                    },
                    "required": ["policy_definition"]
                },
                handler=self._handle_create_city_policy,
                tags=["governance", "policies"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="allocate_resources",
                description="Allocate resources for city operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "resource_type": {"type": "string", "description": "Type of resource"},
                        "amount": {"type": "number", "description": "Amount to allocate"},
                        "priority": {"type": "string", "description": "Allocation priority"}
                    },
                    "required": ["resource_type", "amount", "priority"]
                },
                handler=self._handle_allocate_resources,
                tags=["resources", "allocation"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="get_tenant_policies",
                description="Get governance policies for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_policies,
                tags=["tenant", "governance"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="get_tenant_resource_usage",
                description="Get resource usage metrics for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_resource_usage,
                tags=["tenant", "resources"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="get_tenant_governance_summary",
                description="Get governance summary for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_governance_summary,
                tags=["tenant", "governance"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return tools
    
    async def _handle_create_city_policy(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle create_city_policy tool execution."""
        policy_definition = parameters.get("policy_definition")
        if not policy_definition:
            return {"error": "Policy definition required"}
        
        result = await self.server_instance.city_manager_service.create_city_policy(
            policy_definition, user_context
        )
        return result
    
    async def _handle_allocate_resources(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle allocate_resources tool execution."""
        resource_type = parameters.get("resource_type")
        amount = parameters.get("amount")
        priority = parameters.get("priority")
        
        if not all([resource_type, amount, priority]):
            return {"error": "All parameters required"}
        
        result = await self.server_instance.city_manager_service.allocate_resources(
            resource_type, amount, priority, user_context
        )
        return result
    
    async def _handle_get_tenant_policies(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_policies tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.city_manager_service.get_tenant_policies(
            tenant_id, user_context
        )
        return result
    
    async def _handle_get_tenant_resource_usage(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_resource_usage tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.city_manager_service.get_tenant_resource_usage(
            tenant_id, user_context
        )
        return result
    
    async def _handle_get_tenant_governance_summary(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_governance_summary tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.city_manager_service.get_tenant_governance_summary(
            tenant_id, user_context
        )
        return result
