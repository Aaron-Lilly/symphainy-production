#!/usr/bin/env python3
"""
Journey Manager MCP Server

Model Context Protocol server for Journey Manager Service.
Provides comprehensive journey orchestration and service management capabilities via MCP tools.

WHAT (MCP Server Role): I provide journey management tools via MCP
HOW (MCP Implementation): I expose Journey Manager operations as MCP tools using MCPServerBase
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from bases.mcp_server_base import MCPServerBase
from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext


class JourneyManagerMCPServer(MCPServerBase):
    """
    MCP Server for Journey Manager Service.
    
    API Consumer Pattern: Uses service interfaces and direct method calls to expose
    Journey Manager capabilities as MCP tools for AI agent consumption.
    """

    def __init__(self, di_container: DIContainerService):
        """
        Initialize Journey Manager MCP Server.
        
        Args:
            di_container: DI container for utilities (config, logger, health, telemetry, security, error_handler, tenant)
        """
        super().__init__("journey_manager_mcp", di_container)
        
        # Service interface for API discovery (will be set when service is available)
        self.service_interface = None
        
        # All utilities available via di_container (config, logger, health, telemetry, security, error_handler, tenant)
        self.logger.info("🗺️ Journey Manager MCP Server initialized - API consumer pattern")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        return {
            "name": "JourneyManagerMCPServer",
            "version": "1.0.0",
            "description": "MCP Server for Journey Manager Service - Journey orchestration and service management",
            "capabilities": [
                "journey_orchestration",
                "service_management", 
                "cross_dimensional_coordination",
                "mvp_journey_orchestration"
            ]
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available MCP tools."""
        return [
            {
                "name": "orchestrate_journey",
                "description": "Orchestrate a user journey using service registry for composition",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "journey_context": {
                            "type": "object",
                            "description": "Journey context data including requirements and capabilities",
                            "properties": {
                                "journey_id": {"type": "string", "description": "Unique journey identifier"},
                                "requirements": {
                                    "type": "object",
                                    "properties": {
                                        "capabilities": {"type": "array", "items": {"type": "string"}},
                                        "dimensions": {"type": "array", "items": {"type": "string"}}
                                    }
                                }
                            },
                            "required": ["journey_id", "requirements"]
                        }
                    },
                    "required": ["journey_context"]
                }
            },
            {
                "name": "orchestrate_mvp_journey",
                "description": "Orchestrate MVP journey across all 4 pillars with solution context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "journey_request": {
                            "type": "object",
                            "description": "MVP journey request data",
                            "properties": {
                                "solution_context": {"type": "object"},
                                "business_outcome": {"type": "string"},
                                "journey_steps": {"type": "array", "items": {"type": "string"}},
                                "pillar_focus": {"type": "object"}
                            },
                            "required": ["business_outcome"]
                        }
                    },
                    "required": ["journey_request"]
                }
            },
            {
                "name": "get_journey_status",
                "description": "Get status of a specific journey",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "journey_id": {
                            "type": "string",
                            "description": "ID of the journey"
                        }
                    },
                    "required": ["journey_id"]
                }
            },
            {
                "name": "start_journey_service",
                "description": "Start a specific journey service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service to start",
                            "enum": ["journey_orchestrator", "business_outcome_landing_page", "journey_persistence"]
                        }
                    },
                    "required": ["service_name"]
                }
            },
            {
                "name": "get_service_health",
                "description": "Get health status of a specific service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service",
                            "enum": ["journey_orchestrator", "business_outcome_landing_page", "journey_persistence"]
                        }
                    },
                    "required": ["service_name"]
                }
            },
            {
                "name": "shutdown_journey_service",
                "description": "Shutdown a specific service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service to shutdown",
                            "enum": ["journey_orchestrator", "business_outcome_landing_page", "journey_persistence"]
                        }
                    },
                    "required": ["service_name"]
                }
            },
            {
                "name": "get_startup_dependencies",
                "description": "Get startup dependencies for the Journey Manager",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "coordinate_with_manager",
                "description": "Coordinate with a specific manager",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "manager_name": {
                            "type": "string",
                            "description": "Name of the manager to coordinate with",
                            "enum": ["experience_manager", "delivery_manager", "city_manager"]
                        },
                        "startup_context": {
                            "type": "object",
                            "description": "Optional startup context data"
                        }
                    },
                    "required": ["manager_name"]
                }
            },
            {
                "name": "get_service_capabilities",
                "description": "Get service capabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "health_check",
                "description": "Perform health check",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool."""
        try:
            if not self.service_interface:
                return {"error": "Journey Manager service not available", "status": "unavailable"}
            
            if tool_name == "orchestrate_journey":
                return await self.service_interface.orchestrate_journey(arguments["journey_context"])
            
            elif tool_name == "orchestrate_mvp_journey":
                return await self.service_interface.orchestrate_mvp_journey(arguments["journey_request"])
            
            elif tool_name == "get_journey_status":
                return await self.service_interface.get_journey_status(arguments["journey_id"])
            
            elif tool_name == "start_journey_service":
                return await self.service_interface.start_service(arguments["service_name"])
            
            elif tool_name == "get_service_health":
                return await self.service_interface.get_service_health(arguments["service_name"])
            
            elif tool_name == "shutdown_journey_service":
                return await self.service_interface.shutdown_service(arguments["service_name"])
            
            elif tool_name == "get_startup_dependencies":
                return await self.service_interface.get_startup_dependencies()
            
            elif tool_name == "coordinate_with_manager":
                return await self.service_interface.coordinate_with_manager(
                    arguments["manager_name"], 
                    arguments.get("startup_context")
                )
            
            elif tool_name == "get_service_capabilities":
                return await self.service_interface.get_service_capabilities()
            
            elif tool_name == "health_check":
                return await self.service_interface.health_check()
            
            else:
                return {"error": f"Unknown tool: {tool_name}", "status": "error"}
                
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e), "status": "error"}
    
    def set_service_interface(self, service_interface):
        """Set the service interface for API discovery."""
        self.service_interface = service_interface
        self.logger.info("✅ Journey Manager service interface connected")





