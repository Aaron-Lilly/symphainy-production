#!/usr/bin/env python3
"""
Journey Orchestrator MCP Server

Model Context Protocol server for Journey Orchestrator Service.
Provides comprehensive business outcome journey orchestration capabilities via MCP tools.

WHAT (MCP Server Role): I provide journey orchestration tools via MCP
HOW (MCP Implementation): I expose Journey Orchestrator operations as MCP tools using MCPServerBase
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


class JourneyOrchestratorMCPServer(MCPServerBase):
    """
    MCP Server for Journey Orchestrator Service.
    
    API Consumer Pattern: Uses service interfaces and direct method calls to expose
    Journey Orchestrator capabilities as MCP tools for AI agent consumption.
    """

    def __init__(self, di_container: DIContainerService):
        """
        Initialize Journey Orchestrator MCP Server.
        
        Args:
            di_container: DI container for utilities (config, logger, health, telemetry, security, error_handler, tenant)
        """
        super().__init__("journey_orchestrator_mcp", di_container)
        
        # Service interface for API discovery (will be set when service is available)
        self.service_interface = None
        
        # All utilities available via di_container (config, logger, health, telemetry, security, error_handler, tenant)
        self.logger.info("🎯 Journey Orchestrator MCP Server initialized - API consumer pattern")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        return {
            "name": "JourneyOrchestratorMCPServer",
            "version": "1.0.0",
            "description": "MCP Server for Journey Orchestrator Service - Business outcome journey orchestration",
            "capabilities": [
                "business_outcome_journey_creation",
                "cross_dimensional_orchestration",
                "solution_architecture",
                "journey_tracking"
            ]
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available MCP tools."""
        return [
            {
                "name": "create_business_outcome_journey",
                "description": "Create a complete business outcome journey across all dimensions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "business_outcome": {
                            "type": "string",
                            "description": "The business outcome to achieve"
                        },
                        "use_case": {
                            "type": "string",
                            "description": "The use case for the journey"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "User context data",
                            "properties": {
                                "user_id": {"type": "string"},
                                "email": {"type": "string"},
                                "full_name": {"type": "string"},
                                "permissions": {"type": "array", "items": {"type": "string"}},
                                "session_id": {"type": "string"}
                            },
                            "required": ["user_id", "email", "full_name", "permissions", "session_id"]
                        }
                    },
                    "required": ["business_outcome", "use_case", "user_context"]
                }
            },
            {
                "name": "orchestrate_cross_dimensional_journey",
                "description": "Orchestrate cross-dimensional execution of a journey",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "business_outcome": {
                            "type": "string",
                            "description": "The business outcome to achieve"
                        },
                        "use_case": {
                            "type": "string",
                            "description": "The use case for the journey"
                        },
                        "solution_architecture": {
                            "type": "object",
                            "description": "Solution architecture data"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "User context data",
                            "properties": {
                                "user_id": {"type": "string"},
                                "email": {"type": "string"},
                                "full_name": {"type": "string"},
                                "permissions": {"type": "array", "items": {"type": "string"}},
                                "session_id": {"type": "string"}
                            },
                            "required": ["user_id", "email", "full_name", "permissions", "session_id"]
                        }
                    },
                    "required": ["business_outcome", "use_case", "solution_architecture", "user_context"]
                }
            },
            {
                "name": "create_journey_record",
                "description": "Create a journey record for tracking",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "business_outcome": {
                            "type": "string",
                            "description": "The business outcome"
                        },
                        "use_case": {
                            "type": "string",
                            "description": "The use case"
                        },
                        "journey_result": {
                            "type": "object",
                            "description": "Journey execution result"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "User context data",
                            "properties": {
                                "user_id": {"type": "string"},
                                "email": {"type": "string"},
                                "full_name": {"type": "string"},
                                "permissions": {"type": "array", "items": {"type": "string"}},
                                "session_id": {"type": "string"}
                            },
                            "required": ["user_id", "email", "full_name", "permissions", "session_id"]
                        }
                    },
                    "required": ["business_outcome", "use_case", "journey_result", "user_context"]
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
                "name": "update_journey_status",
                "description": "Update status of a specific journey",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "journey_id": {
                            "type": "string",
                            "description": "ID of the journey"
                        },
                        "status": {
                            "type": "string",
                            "description": "New status",
                            "enum": ["created", "active", "paused", "completed", "failed", "cancelled"]
                        }
                    },
                    "required": ["journey_id", "status"]
                }
            },
            {
                "name": "get_active_journeys",
                "description": "Get active journeys for a user",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "ID of the user"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "get_journey_analytics",
                "description": "Get analytics for a specific journey",
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
                return {"error": "Journey Orchestrator service not available", "status": "unavailable"}
            
            if tool_name == "create_business_outcome_journey":
                user_context = UserContext(**arguments["user_context"])
                return await self.service_interface.create_business_outcome_journey(
                    arguments["business_outcome"],
                    arguments["use_case"],
                    user_context
                )
            
            elif tool_name == "orchestrate_cross_dimensional_journey":
                user_context = UserContext(**arguments["user_context"])
                return await self.service_interface.orchestrate_cross_dimensional_journey(
                    arguments["business_outcome"],
                    arguments["use_case"],
                    arguments["solution_architecture"],
                    user_context
                )
            
            elif tool_name == "create_journey_record":
                user_context = UserContext(**arguments["user_context"])
                return await self.service_interface.create_journey_record(
                    arguments["business_outcome"],
                    arguments["use_case"],
                    arguments["journey_result"],
                    user_context
                )
            
            elif tool_name == "get_journey_status":
                return await self.service_interface.get_journey_status(arguments["journey_id"])
            
            elif tool_name == "update_journey_status":
                return await self.service_interface.update_journey_status(
                    arguments["journey_id"],
                    arguments["status"]
                )
            
            elif tool_name == "get_active_journeys":
                return await self.service_interface.get_active_journeys(arguments["user_id"])
            
            elif tool_name == "get_journey_analytics":
                return await self.service_interface.get_journey_analytics(arguments["journey_id"])
            
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
        self.logger.info("✅ Journey Orchestrator service interface connected")





