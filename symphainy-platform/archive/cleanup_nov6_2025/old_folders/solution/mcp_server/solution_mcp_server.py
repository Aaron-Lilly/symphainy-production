"""
Solution Realm MCP Server
MCP server for Solution Realm capabilities
"""

import logging
from typing import Dict, Any, List
from foundations.mcp_server.mcp_server_base import MCPServerBase
from ..services.solution_manager.solution_manager_service import SolutionManagerService

logger = logging.getLogger(__name__)

class SolutionMCPServer(MCPServerBase):
    """
    Solution Realm MCP Server
    Exposes Solution Realm capabilities as MCP tools.
    """
    
    def __init__(self, solution_manager: SolutionManagerService):
        super().__init__("solution_mcp_server")
        self.solution_manager = solution_manager
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available MCP tools."""
        return [
            {
                "name": "get_dashboard_summary",
                "description": "Get summary dashboard data for all realms",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_realm_dashboard",
                "description": "Get detailed dashboard data for a specific realm",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "realm_name": {
                            "type": "string",
                            "description": "Name of the realm (smart_city, agentic, business_enablement, experience, journey, platform_summary)",
                            "enum": ["smart_city", "agentic", "business_enablement", "experience", "journey", "platform_summary"]
                        }
                    },
                    "required": ["realm_name"]
                }
            },
            {
                "name": "get_journey_templates",
                "description": "Get all saved journey templates",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "save_journey_template",
                "description": "Save a journey template for reuse",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "template_data": {
                            "type": "object",
                            "description": "Journey template data",
                            "properties": {
                                "journey_id": {"type": "string"},
                                "journey_name": {"type": "string"},
                                "journey_description": {"type": "string"},
                                "required_capabilities": {"type": "array", "items": {"type": "string"}},
                                "required_dimensions": {"type": "array", "items": {"type": "string"}},
                                "service_composition": {"type": "object"},
                                "journey_steps": {"type": "array"},
                                "success_criteria": {"type": "object"},
                                "created_by": {"type": "string"}
                            },
                            "required": ["journey_id", "journey_name"]
                        }
                    },
                    "required": ["template_data"]
                }
            },
            {
                "name": "get_platform_health",
                "description": "Get overall platform health status",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool."""
        try:
            if tool_name == "get_dashboard_summary":
                result = await self.solution_manager.get_dashboard_summary()
                return {
                    "success": True,
                    "result": result
                }
            
            elif tool_name == "get_realm_dashboard":
                realm_name = parameters.get("realm_name")
                if not realm_name:
                    return {
                        "success": False,
                        "error": "realm_name parameter is required"
                    }
                result = await self.solution_manager.get_realm_dashboard(realm_name)
                return {
                    "success": True,
                    "result": result
                }
            
            elif tool_name == "get_journey_templates":
                result = await self.solution_manager.get_journey_templates()
                return {
                    "success": True,
                    "result": result
                }
            
            elif tool_name == "save_journey_template":
                template_data = parameters.get("template_data")
                if not template_data:
                    return {
                        "success": False,
                        "error": "template_data parameter is required"
                    }
                result = await self.solution_manager.save_journey_template(template_data)
                return {
                    "success": True,
                    "result": result
                }
            
            elif tool_name == "get_platform_health":
                result = await self.solution_manager.get_realm_dashboard("platform_summary")
                return {
                    "success": True,
                    "result": result
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to execute tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }




