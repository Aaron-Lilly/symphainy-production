#!/usr/bin/env python3
"""
MCP Tool Registry

Handles tool registration, management, and FastAPI endpoint creation for MCP servers.

WHAT (Micro-Module Role): I provide tool registration and management for MCP servers
HOW (Micro-Module Implementation): I handle tool registration and FastAPI endpoint creation
"""

from typing import Dict, Any, List, Callable
from datetime import datetime
from fastapi import Request, HTTPException

from .mcp_tool_definition import MCPToolDefinition
from .mcp_auth_validation import MCPAuthValidation
from .mcp_telemetry_emission import MCPTelemetryEmission


class MCPToolRegistry:
    """
    Tool registry for MCP servers.
    
    Handles tool registration, management, and FastAPI endpoint creation.
    """
    
    def __init__(self, service_name: str, utilities, fastapi_app):
        """Initialize tool registry."""
        self.service_name = service_name
        self.utilities = utilities
        self.app = fastapi_app
        self.registered_tools: Dict[str, MCPToolDefinition] = {}
        
        # Initialize helper classes
        self.auth_validation = MCPAuthValidation(utilities)
        self.telemetry_emission = MCPTelemetryEmission(utilities, service_name)
        
        self.logger = utilities.logger
    
    def register_tool(self, tool_name: str, handler: Callable, input_schema: Dict[str, Any], 
                     description: str = None, tags: List[str] = None, requires_tenant: bool = True):
        """Register a tool endpoint following CTO guidance."""
        
        # Create tool definition
        tool_def = MCPToolDefinition(
            name=tool_name,
            description=description or f"Execute {tool_name}",
            input_schema=input_schema,
            handler=handler,
            tags=tags or [],
            requires_tenant=requires_tenant
        )
        
        # Register in tool registry
        self.registered_tools[tool_name] = tool_def
        
        # Create FastAPI endpoint
        self._create_fastapi_endpoint(tool_name, handler, input_schema, tool_def)
        
        self.logger.info(f"✅ Registered MCP tool: {tool_name}")
    
    def _create_fastapi_endpoint(self, tool_name: str, handler: Callable, 
                               input_schema: Dict[str, Any], tool_def: MCPToolDefinition):
        """Create FastAPI endpoint for tool."""
        
        @self.app.post(f"/tool/{tool_name}")
        async def tool_endpoint(request: Request):
            """Tool endpoint with full platform integration."""
            start_time = datetime.utcnow()
            
            try:
                # 1) Get request payload
                payload = await request.json()
                
                # 2) Auth & tenant validation
                auth_result = await self.auth_validation.validate_auth_and_tenant(request, payload, tool_def)
                if not auth_result["valid"]:
                    raise HTTPException(status_code=401, detail=auth_result["error"])
                
                # 3) Input validation (simplified for now)
                # TODO: Implement proper schema validation
                required_fields = input_schema.get("required", [])
                for field in required_fields:
                    if field not in payload:
                        raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
                
                # 4) Policy guard (optional)
                policy_result = await self._check_policy(payload, tool_name)
                if not policy_result["allowed"]:
                    raise HTTPException(status_code=403, detail="policy_denied")
                
                # 5) Forward to authoritative service
                result = await handler(payload)
                
                # 6) Emit metadata_event for mutations
                if self._is_mutation_tool(tool_name):
                    await self.telemetry_emission.emit_metadata_event(tool_name, result, payload)
                
                # 7) Telemetry
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.telemetry_emission.emit_tool_execution_telemetry(
                    tool_name, execution_time, True, payload.get("tenant_id")
                )
                
                # 8) Logging
                self.logger.info(f"Tool {tool_name} executed successfully", extra={
                    "tool": tool_name,
                    "service": self.service_name,
                    "execution_time_ms": execution_time,
                    "tenant": payload.get("tenant_id")
                })
                
                return {"status": "ok", "result": result}
                
            except HTTPException:
                raise
            except Exception as e:
                # Error handling
                self.utilities.error_handler.handle_error(e, f"mcp_tool_{tool_name}_failed")
                
                # Telemetry for errors
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.telemetry_emission.emit_tool_execution_telemetry(
                    tool_name, execution_time, False, payload.get("tenant_id"), str(e)
                )
                
                return {"status": "error", "error": str(e)}
    
    async def execute_tool_direct(self, tool_name: str, context: Dict[str, Any], user_context) -> Dict[str, Any]:
        """Execute a tool directly without HTTP request."""
        start_time = datetime.utcnow()
        
        try:
            # Get tool definition
            tool_def = self.registered_tools.get(tool_name)
            if not tool_def:
                raise ValueError(f"Tool {tool_name} not found")
            
            # Get handler
            handler = tool_def.handler
            
            # Add user context to payload
            payload = context.copy()
            payload["tenant_id"] = user_context.tenant_id
            payload["user_id"] = user_context.user_id
            
            # Input validation (simplified for now)
            # TODO: Implement proper schema validation
            # For now, just check required fields
            required_fields = tool_def.input_schema.get("required", [])
            for field in required_fields:
                if field not in payload:
                    raise ValueError(f"Missing required field: {field}")
            
            # Execute handler
            result = await handler(payload, user_context)
            
            # Emit metadata_event for mutations
            if self._is_mutation_tool(tool_name):
                await self.telemetry_emission.emit_metadata_event(tool_name, result, payload)
            
            # Telemetry
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.telemetry_emission.emit_tool_execution_telemetry(
                tool_name, execution_time, True, payload.get("tenant_id")
            )
            
            # Logging
            self.logger.info(f"Tool {tool_name} executed successfully", extra={
                "tool": tool_name,
                "service": self.service_name,
                "execution_time_ms": execution_time,
                "tenant": payload.get("tenant_id")
            })
            
            return result
            
        except Exception as e:
            # Error handling
            self.utilities.error_handler.handle_error(e, f"mcp_tool_{tool_name}_failed")
            
            # Telemetry for errors
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.telemetry_emission.emit_tool_execution_telemetry(
                tool_name, execution_time, False, context.get("tenant_id"), str(e)
            )
            
            raise
    
    async def _check_policy(self, payload: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
        """Check policy using Curator (optional)."""
        # TODO: Implement Curator policy check
        return {"allowed": True}
    
    def _is_mutation_tool(self, tool_name: str) -> bool:
        """Check if tool is a mutation tool."""
        mutation_verbs = ["create", "update", "delete", "modify", "set", "add", "remove"]
        return any(verb in tool_name.lower() for verb in mutation_verbs)
    
    def get_registered_tools(self) -> Dict[str, MCPToolDefinition]:
        """Get all registered tools."""
        return self.registered_tools.copy()
    
    def get_tool(self, tool_name: str) -> MCPToolDefinition:
        """Get a specific tool by name."""
        return self.registered_tools.get(tool_name)
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool."""
        if tool_name in self.registered_tools:
            del self.registered_tools[tool_name]
            self.logger.info(f"Unregistered MCP tool: {tool_name}")
            return True
        return False
    
    def get_tool_list(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self.registered_tools.keys())
