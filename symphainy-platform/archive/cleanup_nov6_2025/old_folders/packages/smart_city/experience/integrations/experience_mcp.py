#!/usr/bin/env python3
"""
Experience MCP - MCP Server Implementation

This MCP server integrates the Experience Manager role and service.
"""

from backend.foundation.bases.core import BaseMCP
from typing import Dict, Any, List


class ExperienceMCP(BaseMCP):
    """
    Experience MCP - integrates role and service for MCP server.
    
    Experience Manager MCP Server - Orchestrates user experience, frontend integration, and agent coordination
    """
    
    def __init__(self):
        """Initialize the Experience MCP server."""
        # Import role and service classes
        from backend.packages.smart_city.experience.roles.experience_manager_role import ExperienceManagerRole
        from backend.packages.smart_city.experience.services.experience_service import ExperienceService
        
        # Initialize role and service first
        self.role = ExperienceManagerRole()
        self.service = ExperienceService()
        
        # Initialize MCP server
        super().__init__(
            server_name=self.role.role_name + " MCP",
            server_description=self.role.role_description + " via MCP"
        )
        
        # Integrate metadata and config from role and service
        self.server_info["role_metadata"] = self.role.get_role_info()
        self.server_info["service_metadata"] = self.service.get_service_info()
        self.server_info["role_config"] = self.role.get_role_config()
        self.server_info["service_config"] = self.service.get_service_config()
        self.server_info["deployment_info"] = {
            "role": self.role.get_deployment_info(),
            "service": self.service.get_deployment_info(),
            "mcp": self.deployment_info
        }
        
        # Initialize MCP components
        self._initialize_mcp_components()
    
    def _initialize_mcp_components(self):
        """Initialize MCP-specific components."""
        self.logger.info("Initializing Experience MCP components")
        
        # Define tools from role and service
        self.tools = []
        
        # Add role tools
        for tool_name in self.role.mcp_tools:
            self.tools.append({
                "name": tool_name,
                "description": f"Execute {tool_name} operation via Experience Manager",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "args": {"type": "array", "description": "Tool arguments"},
                        "kwargs": {"type": "object", "description": "Tool keyword arguments"}
                    }
                }
            })
        
        # Add service tools
        for tool_name in self.service.mcp_tools:
            self.tools.append({
                "name": tool_name,
                "description": f"Execute {tool_name} operation via Experience Service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "args": {"type": "array", "description": "Tool arguments"},
                        "kwargs": {"type": "object", "description": "Tool keyword arguments"}
                    }
                }
            })
        
        # Define resources from role and service
        self.resources = []
        
        # Add role resources
        for resource in self.role.mcp_resources:
            self.resources.append({
                "uri": resource,
                "name": resource.split("/")[-1],
                "description": f"Access {resource} resource via Experience Manager",
                "mimeType": "application/json"
            })
        
        # Add service resources
        for resource in self.service.mcp_resources:
            self.resources.append({
                "uri": resource,
                "name": resource.split("/")[-1],
                "description": f"Access {resource} resource via Experience Service",
                "mimeType": "application/json"
            })
        
        # Define prompts from role and service
        self.prompts = []
        
        # Add role prompts
        for prompt in self.role.mcp_prompts:
            self.prompts.append({
                "name": prompt,
                "description": f"Prompt for {prompt} via Experience Manager",
                "arguments": []
            })
        
        # Add service prompts
        for prompt in self.service.mcp_prompts:
            self.prompts.append({
                "name": prompt,
                "description": f"Prompt for {prompt} via Experience Service",
                "arguments": []
            })
        
        self.logger.info(f"Initialized {len(self.tools)} tools, {len(self.resources)} resources, {len(self.prompts)} prompts")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool on this MCP server."""
        try:
            self.logger.info(f"Calling tool: {tool_name}")
            
            # Route to appropriate role or service method
            if tool_name in self.role.mcp_tools:
                # Call role method
                method_name = f"_{tool_name}_capability"
                if hasattr(self.role, method_name):
                    return getattr(self.role, method_name)(arguments)
                else:
                    return {"success": False, "error": f"Role method {method_name} not found"}
            
            elif tool_name in self.service.mcp_tools:
                # Call service method
                method_name = f"_{tool_name}"
                if hasattr(self.service, method_name):
                    return getattr(self.service, method_name)(arguments)
                else:
                    return {"success": False, "error": f"Service method {method_name} not found"}
            
            else:
                return {"success": False, "error": f"Tool {tool_name} not found"}
                
        except Exception as e:
            self.logger.error(f"Failed to call tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        return self.server_info
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "tools": self.tools,
            "count": len(self.tools)
        }
    
    def list_resources(self) -> Dict[str, Any]:
        """List available resources."""
        return {
            "resources": self.resources,
            "count": len(self.resources)
        }
    
    def list_prompts(self) -> Dict[str, Any]:
        """List available prompts."""
        return {
            "prompts": self.prompts,
            "count": len(self.prompts)
        }

