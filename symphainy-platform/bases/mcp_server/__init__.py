#!/usr/bin/env python3
"""
MCP Server Package

Micro-module package for MCP server functionality in the SymphAIny platform.

Components:
- MCPServerBase: Main base class for MCP servers
- MCPToolDefinition: Tool definition data structures
- MCPToolRegistry: Tool registration and management
- MCPFastAPIIntegration: FastAPI app creation and endpoints
- MCPAuthValidation: Authentication and tenant validation
- MCPHealthMonitoring: Health status and monitoring
- MCPTelemetryEmission: Telemetry and metadata events
- MCPUtilityIntegration: DI container utility integration
"""

from .mcp_server_base import MCPServerBase
from .mcp_tool_definition import MCPToolDefinition, MCPExecutionResult
from .mcp_tool_registry import MCPToolRegistry
from .mcp_fastapi_integration import MCPFastAPIIntegration
from .mcp_auth_validation import MCPAuthValidation
from .mcp_health_monitoring import MCPHealthMonitoring
from .mcp_telemetry_emission import MCPTelemetryEmission
from .mcp_utility_integration import MCPUtilityIntegration

__all__ = [
    "MCPServerBase",
    "MCPToolDefinition", 
    "MCPExecutionResult",
    "MCPToolRegistry",
    "MCPFastAPIIntegration",
    "MCPAuthValidation",
    "MCPHealthMonitoring",
    "MCPTelemetryEmission",
    "MCPUtilityIntegration"
]




























