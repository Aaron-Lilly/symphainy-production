#!/usr/bin/env python3
"""
Nurse Service MCP Server

Model Context Protocol server for the Enhanced Nurse Service, providing comprehensive
health monitoring, telemetry collection, alert management, and failure classification
capabilities as MCP tools.

Refactored to use MCPServerBase with full utility integration via DIContainer.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.mcp_server_base import MCPServerBase, MCPToolDefinition
from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext
from ..nurse_service import NurseService


class NurseMCPServer(MCPServerBase):
    """
    MCP Server for the Enhanced Nurse Service.
    
    API Consumer Pattern: Uses service interfaces and direct method calls to expose
    NurseService capabilities as MCP tools for AI agent consumption.
    """
    
    def __init__(self, di_container: DIContainerService):
        """
        Initialize Nurse MCP Server.
        
        Args:
            di_container: DI container for utilities (config, logger, health, telemetry, security, error_handler, tenant)
        """
        super().__init__("nurse_mcp", di_container)
        
        # Import service interface (not implementation)
        from backend.smart_city.protocols.soa_service_protocol import SOAServiceProtocol
        
        # Service interface for API discovery
        self.service_interface = None  # Will be set when service is available
        
        # All utilities available via di_container (config, logger, health, telemetry, security, error_handler, tenant)
        self.logger.info("🏥 Nurse MCP Server initialized - API consumer pattern")
    
    async def initialize(self):
        """Initialize the MCP server."""
        try:
            await super().initialize()
            
            # Initialize MCP protocol
            await self.mcp_protocol.initialize()
            self.logger.info("✅ MCP Protocol initialized")
            
            await self.nurse_service.initialize()
            self.logger.info("✅ Nurse MCP Server initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Nurse MCP Server: {e}")
            raise
    
    def initialize_service_integration(self) -> bool:
        """Initialize integration with the Nurse Service."""
        try:
            if not self.nurse_service:
                self.logger.error("Nurse Service not available")
                return False
            
            self.logger.info("Nurse Service integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing Nurse Service integration: {e}")
            return False
    
    def register_tools(self) -> List[MCPTool]:
        """Register all Nurse Service MCP tools."""
        tools = [
            # Health Monitoring Tools
            MCPTool(
                name="perform_system_health_check",
                description="Perform a comprehensive system health check including CPU, memory, disk, and process monitoring",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_perform_system_health_check,
                tags=["health", "monitoring", "system"]
            ),
            MCPTool(
                name="perform_service_health_check",
                description="Perform a health check for a specific service",
                input_schema={
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service to check"
                        }
                    },
                    "required": ["service_name"]
                },
                handler=self._handle_perform_service_health_check,
                tags=["health", "monitoring", "service"]
            ),
            MCPTool(
                name="start_continuous_monitoring",
                description="Start continuous health monitoring for a service over a specified duration",
                input_schema={
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service to monitor"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Duration in minutes to monitor (default: 60)",
                            "default": 60
                        }
                    },
                    "required": ["service_name"]
                },
                handler=self._handle_start_continuous_monitoring,
                tags=["health", "monitoring", "continuous"]
            ),
            MCPTool(
                name="get_health_dashboard_data",
                description="Get comprehensive health dashboard data with metrics and trends",
                input_schema={
                    "type": "object",
                    "properties": {
                        "hours": {
                            "type": "integer",
                            "description": "Number of hours of data to retrieve (default: 24)",
                            "default": 24
                        }
                    },
                    "required": []
                },
                handler=self._handle_get_health_dashboard_data,
                tags=["health", "dashboard", "analytics"]
            ),
            
            # Telemetry Collection Tools
            MCPTool(
                name="collect_system_telemetry",
                description="Collect comprehensive system telemetry data including metrics, traces, and logs",
                input_schema={
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service to collect telemetry for (optional)"
                        }
                    },
                    "required": []
                },
                handler=self._handle_collect_system_telemetry,
                tags=["telemetry", "collection", "metrics"]
            ),
            MCPTool(
                name="start_telemetry_collection",
                description="Start continuous telemetry collection for a service",
                input_schema={
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service to collect telemetry for"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Duration in minutes to collect telemetry (default: 60)",
                            "default": 60
                        }
                    },
                    "required": ["service_name"]
                },
                handler=self._handle_start_telemetry_collection,
                tags=["telemetry", "collection", "continuous"]
            ),
            MCPTool(
                name="create_custom_metric",
                description="Create a custom metric with tags and metadata",
                input_schema={
                    "type": "object",
                    "properties": {
                        "metric_name": {
                            "type": "string",
                            "description": "Name of the metric"
                        },
                        "value": {
                            "type": "number",
                            "description": "Value of the metric"
                        },
                        "tags": {
                            "type": "object",
                            "description": "Tags for the metric",
                            "additionalProperties": {"type": "string"}
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata for the metric"
                        }
                    },
                    "required": ["metric_name", "value"]
                },
                handler=self._handle_create_custom_metric,
                tags=["telemetry", "metrics", "custom"]
            ),
            MCPTool(
                name="start_trace",
                description="Start a distributed trace for operation monitoring",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation_name": {
                            "type": "string",
                            "description": "Name of the operation being traced"
                        },
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service (optional)"
                        },
                        "parent_span_id": {
                            "type": "string",
                            "description": "Parent span ID for trace hierarchy (optional)"
                        },
                        "tags": {
                            "type": "object",
                            "description": "Tags for the trace",
                            "additionalProperties": {"type": "string"}
                        }
                    },
                    "required": ["operation_name"]
                },
                handler=self._handle_start_trace,
                tags=["telemetry", "tracing", "distributed"]
            ),
            MCPTool(
                name="finish_trace",
                description="Finish a distributed trace with status and logs",
                input_schema={
                    "type": "object",
                    "properties": {
                        "span_id": {
                            "type": "string",
                            "description": "ID of the span to finish"
                        },
                        "status": {
                            "type": "string",
                            "description": "Status of the operation (default: ok)",
                            "default": "ok"
                        },
                        "tags": {
                            "type": "object",
                            "description": "Additional tags for the trace",
                            "additionalProperties": {"type": "string"}
                        },
                        "logs": {
                            "type": "array",
                            "description": "Log entries for the trace",
                            "items": {"type": "object"}
                        }
                    },
                    "required": ["span_id"]
                },
                handler=self._handle_finish_trace,
                tags=["telemetry", "tracing", "distributed"]
            ),
            MCPTool(
                name="get_telemetry_dashboard_data",
                description="Get comprehensive telemetry dashboard data with metrics and traces",
                input_schema={
                    "type": "object",
                    "properties": {
                        "hours": {
                            "type": "integer",
                            "description": "Number of hours of data to retrieve (default: 24)",
                            "default": 24
                        }
                    },
                    "required": []
                },
                handler=self._handle_get_telemetry_dashboard_data,
                tags=["telemetry", "dashboard", "analytics"]
            ),
            
            # Alert Management Tools
            MCPTool(
                name="create_health_alert",
                description="Create a health-related alert with severity and metadata",
                input_schema={
                    "type": "object",
                    "properties": {
                        "alert_type": {
                            "type": "string",
                            "description": "Type of the alert (e.g., cpu_high, memory_low)"
                        },
                        "severity": {
                            "type": "string",
                            "description": "Severity level (low, medium, high, critical)",
                            "enum": ["low", "medium", "high", "critical"]
                        },
                        "message": {
                            "type": "string",
                            "description": "Alert message"
                        },
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service (optional)"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata for the alert"
                        }
                    },
                    "required": ["alert_type", "severity", "message"]
                },
                handler=self._handle_create_health_alert,
                tags=["alerts", "health", "monitoring"]
            ),
            MCPTool(
                name="create_failure_alert",
                description="Create a failure-related alert with automatic classification",
                input_schema={
                    "type": "object",
                    "properties": {
                        "error_message": {
                            "type": "string",
                            "description": "Error message to classify and alert on"
                        },
                        "error_code": {
                            "type": "string",
                            "description": "Error code (optional)"
                        },
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service (optional)"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata for the alert"
                        }
                    },
                    "required": ["error_message"]
                },
                handler=self._handle_create_failure_alert,
                tags=["alerts", "failure", "classification"]
            ),
            MCPTool(
                name="acknowledge_alert",
                description="Acknowledge an alert with optional notes",
                input_schema={
                    "type": "object",
                    "properties": {
                        "alert_id": {
                            "type": "string",
                            "description": "ID of the alert to acknowledge"
                        },
                        "acknowledged_by": {
                            "type": "string",
                            "description": "Who is acknowledging the alert (default: system)",
                            "default": "system"
                        },
                        "acknowledgment_notes": {
                            "type": "string",
                            "description": "Notes about the acknowledgment"
                        }
                    },
                    "required": ["alert_id"]
                },
                handler=self._handle_acknowledge_alert,
                tags=["alerts", "acknowledgment"]
            ),
            MCPTool(
                name="resolve_alert",
                description="Resolve an alert with resolution details",
                input_schema={
                    "type": "object",
                    "properties": {
                        "alert_id": {
                            "type": "string",
                            "description": "ID of the alert to resolve"
                        },
                        "resolved_by": {
                            "type": "string",
                            "description": "Who is resolving the alert (default: system)",
                            "default": "system"
                        },
                        "resolution_notes": {
                            "type": "string",
                            "description": "Notes about the resolution"
                        },
                        "resolution_category": {
                            "type": "string",
                            "description": "Category of the resolution (optional)"
                        }
                    },
                    "required": ["alert_id"]
                },
                handler=self._handle_resolve_alert,
                tags=["alerts", "resolution"]
            ),
            MCPTool(
                name="get_alert_dashboard_data",
                description="Get comprehensive alert dashboard data with statistics and trends",
                input_schema={
                    "type": "object",
                    "properties": {
                        "hours": {
                            "type": "integer",
                            "description": "Number of hours of data to retrieve (default: 24)",
                            "default": 24
                        }
                    },
                    "required": []
                },
                handler=self._handle_get_alert_dashboard_data,
                tags=["alerts", "dashboard", "analytics"]
            ),
            
            # Failure Classification Tools
            MCPTool(
                name="classify_failure",
                description="Classify a failure without creating an alert",
                input_schema={
                    "type": "object",
                    "properties": {
                        "error_message": {
                            "type": "string",
                            "description": "Error message to classify"
                        },
                        "error_code": {
                            "type": "string",
                            "description": "Error code (optional)"
                        },
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service (optional)"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata for classification"
                        }
                    },
                    "required": ["error_message"]
                },
                handler=self._handle_classify_failure,
                tags=["failure", "classification", "analysis"]
            ),
            MCPTool(
                name="classify_and_alert",
                description="Classify a failure and optionally create an alert",
                input_schema={
                    "type": "object",
                    "properties": {
                        "error_message": {
                            "type": "string",
                            "description": "Error message to classify and alert on"
                        },
                        "error_code": {
                            "type": "string",
                            "description": "Error code (optional)"
                        },
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service (optional)"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata for classification"
                        }
                    },
                    "required": ["error_message"]
                },
                handler=self._handle_classify_and_alert,
                tags=["failure", "classification", "alerts"]
            ),
            MCPTool(
                name="analyze_failure_patterns",
                description="Analyze failure patterns over time with insights and recommendations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "hours": {
                            "type": "integer",
                            "description": "Number of hours to analyze (default: 24)",
                            "default": 24
                        }
                    },
                    "required": []
                },
                handler=self._handle_analyze_failure_patterns,
                tags=["failure", "analysis", "patterns"]
            ),
            MCPTool(
                name="get_failure_dashboard_data",
                description="Get comprehensive failure classification dashboard data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "hours": {
                            "type": "integer",
                            "description": "Number of hours of data to retrieve (default: 24)",
                            "default": 24
                        }
                    },
                    "required": []
                },
                handler=self._handle_get_failure_dashboard_data,
                tags=["failure", "dashboard", "analytics"]
            ),
            
            # Service Management Tools
            MCPTool(
                name="get_service_status",
                description="Get comprehensive service status and health information",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_get_service_status,
                tags=["service", "status", "health"]
            ),
            MCPTool(
                name="configure_service",
                description="Configure service parameters for different modules",
                input_schema={
                    "type": "object",
                    "properties": {
                        "config_type": {
                            "type": "string",
                            "description": "Type of configuration (health_monitoring, telemetry_collection, alert_management, failure_classification)",
                            "enum": ["health_monitoring", "telemetry_collection", "alert_management", "failure_classification"]
                        },
                        "config_data": {
                            "type": "object",
                            "description": "Configuration data for the specified type"
                        }
                    },
                    "required": ["config_type", "config_data"]
                },
                handler=self._handle_configure_service,
                tags=["service", "configuration"]
            ),
            MCPTool(
                name="get_comprehensive_dashboard_data",
                description="Get comprehensive dashboard data from all modules",
                input_schema={
                    "type": "object",
                    "properties": {
                        "hours": {
                            "type": "integer",
                            "description": "Number of hours of data to retrieve (default: 24)",
                            "default": 24
                        }
                    },
                    "required": []
                },
                handler=self._handle_get_comprehensive_dashboard_data,
                tags=["dashboard", "comprehensive", "analytics"]
            )
        ]
        
        return tools
    
    # ============================================================================
    # HEALTH MONITORING HANDLERS
    # ============================================================================
    
    async def _handle_perform_system_health_check(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle perform_system_health_check tool."""
        return self.nurse_service.perform_system_health_check(arguments, user_context)
    
    async def _handle_perform_service_health_check(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle perform_service_health_check tool."""
        return self.nurse_service.perform_service_health_check(arguments, user_context)
    
    async def _handle_start_continuous_monitoring(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle start_continuous_monitoring tool."""
        return self.nurse_service.start_continuous_monitoring(arguments, user_context)
    
    async def _handle_get_health_dashboard_data(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_health_dashboard_data tool."""
        return self.nurse_service.get_health_dashboard_data(arguments, user_context)
    
    # ============================================================================
    # TELEMETRY COLLECTION HANDLERS
    # ============================================================================
    
    async def _handle_collect_system_telemetry(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle collect_system_telemetry tool."""
        return self.nurse_service.collect_system_telemetry(arguments, user_context)
    
    async def _handle_start_telemetry_collection(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle start_telemetry_collection tool."""
        return self.nurse_service.start_telemetry_collection(arguments, user_context)
    
    async def _handle_create_custom_metric(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle create_custom_metric tool."""
        return self.nurse_service.create_custom_metric(arguments, user_context)
    
    async def _handle_start_trace(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle start_trace tool."""
        return self.nurse_service.start_trace(arguments, user_context)
    
    async def _handle_finish_trace(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle finish_trace tool."""
        return self.nurse_service.finish_trace(arguments, user_context)
    
    async def _handle_get_telemetry_dashboard_data(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_telemetry_dashboard_data tool."""
        return self.nurse_service.get_telemetry_dashboard_data(arguments, user_context)
    
    # ============================================================================
    # ALERT MANAGEMENT HANDLERS
    # ============================================================================
    
    async def _handle_create_health_alert(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle create_health_alert tool."""
        return self.nurse_service.create_health_alert(arguments, user_context)
    
    async def _handle_create_failure_alert(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle create_failure_alert tool."""
        return self.nurse_service.create_failure_alert(arguments, user_context)
    
    async def _handle_acknowledge_alert(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle acknowledge_alert tool."""
        return self.nurse_service.acknowledge_alert(arguments, user_context)
    
    async def _handle_resolve_alert(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle resolve_alert tool."""
        return self.nurse_service.resolve_alert(arguments, user_context)
    
    async def _handle_get_alert_dashboard_data(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_alert_dashboard_data tool."""
        return self.nurse_service.get_alert_dashboard_data(arguments, user_context)
    
    # ============================================================================
    # FAILURE CLASSIFICATION HANDLERS
    # ============================================================================
    
    async def _handle_classify_failure(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle classify_failure tool."""
        return self.nurse_service.classify_failure(arguments, user_context)
    
    async def _handle_classify_and_alert(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle classify_and_alert tool."""
        return self.nurse_service.classify_and_alert(arguments, user_context)
    
    async def _handle_analyze_failure_patterns(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle analyze_failure_patterns tool."""
        return self.nurse_service.analyze_failure_patterns(arguments, user_context)
    
    async def _handle_get_failure_dashboard_data(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_failure_dashboard_data tool."""
        return self.nurse_service.get_failure_dashboard_data(arguments, user_context)
    
    # ============================================================================
    # SERVICE MANAGEMENT HANDLERS
    # ============================================================================
    
    async def _handle_get_service_status(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_service_status tool."""
        return self.nurse_service.get_service_status(arguments, user_context)
    
    async def _handle_configure_service(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle configure_service tool."""
        return self.nurse_service.configure_service(arguments, user_context)
    
    async def _handle_get_comprehensive_dashboard_data(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_comprehensive_dashboard_data tool."""
        return self.nurse_service.get_comprehensive_dashboard_data(arguments, user_context)


class NurseMCPProtocol(MCPServerProtocol):
    """MCP Protocol implementation for Nurse MCP Server."""
    
    def __init__(self, server_name: str, server_instance, curator_foundation=None):
        """Initialize Nurse MCP Protocol."""
        super().__init__(server_name, None, curator_foundation)
        self.server_instance = server_instance
        self.server_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the MCP server."""
        # Create server info with multi-tenant metadata
        self.server_info = MCPServerInfo(
            server_name="NurseMCPServer",
            version="1.0.0",
            description="Nurse MCP Server - Multi-tenant health monitoring and telemetry tools",
            interface_name="INurseMCP",
            tools=self._create_all_tools(),
            capabilities=["health-monitoring", "telemetry", "multi-tenant", "alerting"],
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
        """Create all tools for Nurse MCP Server."""
        tools = []
        
        # Standard tools
        tools.extend(self._create_standard_tools())
        tools.extend(self._create_tenant_aware_tools())
        
        # Nurse specific tools
        tools.extend([
            MCPTool(
                name="perform_health_check",
                description="Perform a health check with tenant awareness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string", "description": "Name of the service to check"},
                        "check_type": {"type": "string", "description": "Type of health check"},
                        "metadata": {"type": "object", "description": "Additional metadata"}
                    },
                    "required": ["service_name", "check_type"]
                },
                handler=self._handle_perform_health_check,
                tags=["health", "monitoring"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="collect_telemetry",
                description="Collect telemetry data with tenant awareness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "metric_name": {"type": "string", "description": "Name of the metric"},
                        "value": {"type": "number", "description": "Metric value"},
                        "tags": {"type": "object", "description": "Metric tags"},
                        "timestamp": {"type": "string", "description": "Timestamp"}
                    },
                    "required": ["metric_name", "value"]
                },
                handler=self._handle_collect_telemetry,
                tags=["telemetry", "collection"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="list_alerts",
                description="List alerts for the current tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "description": "Filter by alert status"},
                        "severity": {"type": "string", "description": "Filter by severity"}
                    }
                },
                handler=self._handle_list_alerts,
                tags=["alerts", "management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="create_alert",
                description="Create a new alert",
                input_schema={
                    "type": "object",
                    "properties": {
                        "rule_id": {"type": "string", "description": "Alert rule ID"},
                        "severity": {"type": "string", "description": "Alert severity"},
                        "message": {"type": "string", "description": "Alert message"},
                        "metadata": {"type": "object", "description": "Additional metadata"}
                    },
                    "required": ["rule_id", "severity", "message"]
                },
                handler=self._handle_create_alert,
                tags=["alerts", "management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="get_tenant_health_summary",
                description="Get health summary for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_health_summary,
                tags=["tenant", "health"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            MCPTool(
                name="get_tenant_alert_summary",
                description="Get alert summary for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_alert_summary,
                tags=["tenant", "alerts"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return tools
    
    async def _handle_perform_health_check(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle perform_health_check tool execution."""
        service_name = parameters.get("service_name")
        check_type = parameters.get("check_type")
        metadata = parameters.get("metadata", {})
        
        if not all([service_name, check_type]):
            return {"error": "Service name and check type required"}
        
        result = await self.server_instance.nurse_service.perform_health_check(
            service_name, check_type, metadata, user_context
        )
        return result
    
    async def _handle_collect_telemetry(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle collect_telemetry tool execution."""
        metric_name = parameters.get("metric_name")
        value = parameters.get("value")
        tags = parameters.get("tags", {})
        timestamp = parameters.get("timestamp")
        
        if not all([metric_name, value]):
            return {"error": "Metric name and value required"}
        
        result = await self.server_instance.nurse_service.collect_telemetry(
            metric_name, value, tags, timestamp, user_context
        )
        return result
    
    async def _handle_list_alerts(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle list_alerts tool execution."""
        status = parameters.get("status")
        severity = parameters.get("severity")
        
        result = await self.server_instance.nurse_service.list_alerts(
            status, severity, user_context
        )
        return result
    
    async def _handle_create_alert(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle create_alert tool execution."""
        rule_id = parameters.get("rule_id")
        severity = parameters.get("severity")
        message = parameters.get("message")
        metadata = parameters.get("metadata", {})
        
        if not all([rule_id, severity, message]):
            return {"error": "Rule ID, severity, and message required"}
        
        result = await self.server_instance.nurse_service.create_alert(
            rule_id, severity, message, metadata, user_context
        )
        return result
    
    async def _handle_get_tenant_health_summary(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_health_summary tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.nurse_service.get_tenant_health_summary(
            tenant_id, user_context
        )
        return result
    
    async def _handle_get_tenant_alert_summary(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_alert_summary tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.nurse_service.get_tenant_alert_summary(
            tenant_id, user_context
        )
        return result
