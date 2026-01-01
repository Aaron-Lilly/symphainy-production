#!/usr/bin/env python3
"""
Business Outcome Analyzer MCP Server

Model Context Protocol server for Business Outcome Analyzer Service.
Provides comprehensive business outcome analysis and capability determination capabilities via MCP tools.

WHAT (MCP Server Role): I provide business outcome analysis tools via MCP
HOW (MCP Implementation): I expose Business Outcome Analyzer operations as MCP tools using MCPServerBase
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


class BusinessOutcomeAnalyzerMCPServer(MCPServerBase):
    """
    MCP Server for Business Outcome Analyzer Service.
    
    API Consumer Pattern: Uses service interfaces and direct method calls to expose
    Business Outcome Analyzer capabilities as MCP tools for AI agent consumption.
    """

    def __init__(self, di_container: DIContainerService):
        """
        Initialize Business Outcome Analyzer MCP Server.
        
        Args:
            di_container: DI container for utilities (config, logger, health, telemetry, security, error_handler, tenant)
        """
        super().__init__("business_outcome_analyzer_mcp", di_container)
        
        # Service interface for API discovery (will be set when service is available)
        self.service_interface = None
        
        # All utilities available via di_container (config, logger, health, telemetry, security, error_handler, tenant)
        self.logger.info("🔍 Business Outcome Analyzer MCP Server initialized - API consumer pattern")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        return {
            "name": "BusinessOutcomeAnalyzerMCPServer",
            "version": "1.0.0",
            "description": "MCP Server for Business Outcome Analyzer Service - Business outcome analysis and capability determination",
            "capabilities": [
                "business_outcome_analysis",
                "capability_determination",
                "user_intent_analysis",
                "pattern_matching"
            ]
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available MCP tools."""
        return [
            {
                "name": "analyze_business_outcome",
                "description": "Analyze a business outcome and determine required capabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "business_outcome": {
                            "type": "string",
                            "description": "The business outcome to analyze"
                        },
                        "use_case": {
                            "type": "string",
                            "description": "The use case for the outcome"
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
                "name": "determine_required_capabilities",
                "description": "Determine required platform capabilities for a business outcome",
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
                        }
                    },
                    "required": ["business_outcome", "use_case"]
                }
            },
            {
                "name": "analyze_user_intent",
                "description": "Analyze user input to determine intent and requirements",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_input": {
                            "type": "string",
                            "description": "User input text"
                        }
                    },
                    "required": ["user_input"]
                }
            },
            {
                "name": "match_outcome_patterns",
                "description": "Match business outcome against known patterns",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "business_outcome": {
                            "type": "string",
                            "description": "The business outcome to match"
                        }
                    },
                    "required": ["business_outcome"]
                }
            },
            {
                "name": "get_capability_requirements",
                "description": "Get detailed capability requirements for a business outcome",
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
                        }
                    },
                    "required": ["business_outcome", "use_case"]
                }
            },
            {
                "name": "suggest_alternative_outcomes",
                "description": "Suggest alternative business outcomes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "business_outcome": {
                            "type": "string",
                            "description": "The original business outcome"
                        },
                        "use_case": {
                            "type": "string",
                            "description": "The use case"
                        }
                    },
                    "required": ["business_outcome", "use_case"]
                }
            },
            {
                "name": "validate_business_outcome",
                "description": "Validate a business outcome for feasibility",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "business_outcome": {
                            "type": "string",
                            "description": "The business outcome to validate"
                        },
                        "use_case": {
                            "type": "string",
                            "description": "The use case"
                        }
                    },
                    "required": ["business_outcome", "use_case"]
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
                return {"error": "Business Outcome Analyzer service not available", "status": "unavailable"}
            
            if tool_name == "analyze_business_outcome":
                user_context = UserContext(**arguments["user_context"])
                return await self.service_interface.analyze_business_outcome(
                    arguments["business_outcome"],
                    arguments["use_case"],
                    user_context
                )
            
            elif tool_name == "determine_required_capabilities":
                return await self.service_interface.determine_required_capabilities(
                    arguments["business_outcome"],
                    arguments["use_case"]
                )
            
            elif tool_name == "analyze_user_intent":
                return await self.service_interface.analyze_user_intent(arguments["user_input"])
            
            elif tool_name == "match_outcome_patterns":
                return await self.service_interface.match_outcome_patterns(arguments["business_outcome"])
            
            elif tool_name == "get_capability_requirements":
                return await self.service_interface.get_capability_requirements(
                    arguments["business_outcome"],
                    arguments["use_case"]
                )
            
            elif tool_name == "suggest_alternative_outcomes":
                return await self.service_interface.suggest_alternative_outcomes(
                    arguments["business_outcome"],
                    arguments["use_case"]
                )
            
            elif tool_name == "validate_business_outcome":
                return await self.service_interface.validate_business_outcome(
                    arguments["business_outcome"],
                    arguments["use_case"]
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
        self.logger.info("✅ Business Outcome Analyzer service interface connected")





