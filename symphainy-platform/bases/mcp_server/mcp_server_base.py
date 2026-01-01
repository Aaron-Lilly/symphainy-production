#!/usr/bin/env python3
"""
MCP Server Base

Main base class for MCP servers in the SymphAIny platform.
Uses micro-modules for tool registration, discovery, and execution patterns.

WHAT (Base Role): I provide MCP server functionality for platform services
HOW (Base Implementation): I coordinate micro-modules for comprehensive MCP server functionality
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from foundations.di_container.di_container_service import DIContainerService

from .mcp_utility_integration import MCPUtilityIntegration
from .mcp_fastapi_integration import MCPFastAPIIntegration
from .mcp_tool_registry import MCPToolRegistry
from .mcp_health_monitoring import MCPHealthMonitoring
from .mcp_telemetry_emission import MCPTelemetryEmission


class MCPServerBase(ABC):
    """
    Base class for all MCP servers in the SymphAIny platform.
    
    This is THE base class that all MCP servers inherit from. It provides:
    - Tool registration and management via micro-modules
    - Tool discovery and metadata
    - Tool execution with validation
    - Multi-tenant support
    - Error handling and logging
    - Standard MCP server lifecycle management
    
    WHAT (Base Role): I provide the foundation for all MCP servers in the platform
    HOW (Base Implementation): I coordinate micro-modules for comprehensive functionality
    """
    
    def __init__(self, service_name: str, di_container: "DIContainerService"):
        """Initialize MCP server base with micro-module integration."""
        self.service_name = service_name
        self.di_container = di_container
        
        # Initialize utility integration
        self.utilities = MCPUtilityIntegration(di_container)
        self.logger = self.utilities.logger
        
        # Initialize FastAPI integration
        self.fastapi = MCPFastAPIIntegration(di_container, service_name)
        self.app = self.fastapi.create_fastapi_app()
        
        # Initialize tool registry
        self.tool_registry = MCPToolRegistry(service_name, self.utilities, self.app)
        
        # Initialize health monitoring
        self.health_monitoring = MCPHealthMonitoring(self.utilities, service_name)
        
        # Initialize telemetry emission
        self.telemetry_emission = MCPTelemetryEmission(self.utilities, service_name)
        
        # Setup FastAPI endpoints
        self.fastapi.setup_required_endpoints(self)
        
        # Register tools
        self.register_server_tools()
        
        # Emit startup telemetry
        self.telemetry_emission.emit_server_startup_telemetry()
        
        self.logger.info(f"🚀 {service_name} MCP Server initialized with micro-module architecture")
    
    # ============================================================================
    # ABSTRACT METHODS - MCP SERVERS MUST IMPLEMENT
    # ============================================================================
    
    @abstractmethod
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return machine + human readable usage guide. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_tool_list(self) -> List[str]:
        """Return list of available tool names. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_version_info(self) -> Dict[str, Any]:
        """Return version and compatibility info. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def register_server_tools(self) -> None:
        """Register all tools for this MCP server. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Execute a tool by routing to the appropriate handler.
        
        Must be implemented by subclasses. Each MCP server has different tool handlers
        and needs to implement security/tenant validation, telemetry, and error handling.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters (dict)
            user_context: Optional user context dict with user_id, tenant_id, etc.
            
        Returns:
            Tool execution result (dict)
        """
        pass
    
    # ============================================================================
    # CONVENIENCE METHODS - DELEGATE TO MICRO-MODULES
    # ============================================================================
    
    def register_tool(self, tool_name: str = None, name: str = None, handler=None, input_schema: Dict[str, Any] = None, 
                     description: str = None, tags: List[str] = None, requires_tenant: bool = True, **kwargs):
        """
        Register a tool endpoint - delegates to tool registry.
        
        Supports both patterns:
        - New pattern: register_tool(tool_name="...", handler=..., input_schema={...}, description="...")
        - Legacy pattern: register_tool(name="...", description="...", handler=..., input_schema={...})
        
        Args:
            tool_name: Tool name (preferred)
            name: Tool name (legacy, used if tool_name not provided)
            handler: Tool handler function
            input_schema: Tool input schema
            description: Tool description
            tags: Optional tags
            requires_tenant: Whether tool requires tenant context
            **kwargs: Additional metadata
        """
        # Support both 'name' and 'tool_name' for backward compatibility
        actual_tool_name = tool_name or name
        if not actual_tool_name:
            raise ValueError("Tool name is required (use 'tool_name=' or 'name=')")
        if not handler:
            raise ValueError("Tool handler is required")
        if not input_schema:
            raise ValueError("Tool input_schema is required")
        
        self.tool_registry.register_tool(actual_tool_name, handler, input_schema, description, tags, requires_tenant)
    
    def get_registered_tools(self) -> Dict[str, Any]:
        """Get all registered tools - delegates to tool registry."""
        return self.tool_registry.get_registered_tools()
    
    def get_tool(self, tool_name: str) -> Any:
        """Get a specific tool - delegates to tool registry."""
        return self.tool_registry.get_tool(tool_name)
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool - delegates to tool registry."""
        return self.tool_registry.unregister_tool(tool_name)
    
    # ============================================================================
    # SERVER LIFECYCLE
    # ============================================================================
    
    async def start_server(self) -> bool:
        """Start the MCP server."""
        try:
            self.logger.info(f"Starting MCP server: {self.service_name}")
            
            # Register with Curator (non-blocking - server works without Curator)
            try:
                await self.register_with_curator()
            except Exception as e:
                self.logger.warning(f"⚠️ Curator registration failed (non-critical): {e}")
            
            # TODO: Implement actual server startup logic
            return True
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            return False
    
    async def stop_server(self) -> bool:
        """Stop the MCP server."""
        try:
            self.logger.info(f"Stopping MCP server: {self.service_name}")
            
            # Emit shutdown telemetry
            self.telemetry_emission.emit_server_shutdown_telemetry()
            
            # TODO: Implement actual server shutdown logic
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop MCP server: {e}")
            return False
    
    # ============================================================================
    # UTILITY ACCESS - DELEGATE TO UTILITY INTEGRATION
    # ============================================================================
    
    @property
    def config(self):
        """Get configuration utility."""
        return self.utilities.config
    
    @property
    def health(self):
        """Get health utility."""
        return self.utilities.health
    
    @property
    def telemetry(self):
        """Get telemetry utility."""
        return self.utilities.telemetry
    
    @property
    def security(self):
        """Get security utility."""
        return self.utilities.security
    
    @property
    def error_handler(self):
        """Get error handler utility."""
        return self.utilities.error_handler
    
    @property
    def tenant(self):
        """Get tenant utility."""
        return self.utilities.tenant
    
    @property
    def validation(self):
        """Get validation utility."""
        return self.utilities.validation
    
    @property
    def serialization(self):
        """Get serialization utility."""
        return self.utilities.serialization
    
    # ============================================================================
    # CURATOR REGISTRATION
    # ============================================================================
    
    def get_curator(self):
        """Get Curator Foundation service."""
        if hasattr(self, 'di_container') and self.di_container:
            if hasattr(self.di_container, 'get_curator'):
                return self.di_container.get_curator()
            elif hasattr(self.di_container, 'curator'):
                return self.di_container.curator
        return None
    
    def _get_realm(self) -> str:
        """Determine realm from service name or configuration."""
        # Business Enablement MCP servers
        if any(x in self.service_name for x in ["content_analysis", "insights", "operations", "business_outcomes", "delivery_manager"]):
            return "business_enablement"
        # Smart City MCP server
        elif "smart_city" in self.service_name:
            return "smart_city"
        # Default
        else:
            return "agentic"  # MCP servers are agentic by nature
    
    async def register_with_curator(self, user_context: Dict[str, Any] = None) -> bool:
        """
        Register MCP server and all tools with Curator.
        
        Registers each tool as an individual capability with mcp_tool contract.
        This enables tool discovery, usage tracking, and service mesh integration.
        
        Args:
            user_context: Optional user context for security/tenant validation
            
        Returns:
            True if at least one tool registered successfully, False otherwise
        """
        try:
            curator = self.get_curator()
            if not curator:
                self.logger.warning("⚠️ Curator not available, skipping MCP tool registration")
                return False
            
            from foundations.curator_foundation.models.capability_definition import CapabilityDefinition
            from datetime import datetime
            
            registered_count = 0
            total_tools = len(self.get_registered_tools())
            
            if total_tools == 0:
                self.logger.warning(f"⚠️ No tools registered for {self.service_name}, skipping Curator registration")
                return False
            
            self.logger.info(f"🔧 Registering {total_tools} MCP tools with Curator for {self.service_name}...")
            
            # Register each tool as a capability
            for tool_name, tool_def in self.get_registered_tools().items():
                try:
                    # Convert MCPToolDefinition to dict format for tool_definition
                    tool_definition_dict = {
                        "name": tool_def.name if hasattr(tool_def, 'name') else tool_name,
                        "description": tool_def.description if hasattr(tool_def, 'description') else f"MCP Tool: {tool_name}",
                        "input_schema": tool_def.input_schema if hasattr(tool_def, 'input_schema') else {},
                        "tags": tool_def.tags if hasattr(tool_def, 'tags') else [],
                        "requires_tenant": tool_def.requires_tenant if hasattr(tool_def, 'requires_tenant') else True,
                        "tenant_scope": tool_def.tenant_scope if hasattr(tool_def, 'tenant_scope') else "user"
                    }
                    
                    # Determine protocol name (convert service_name to Protocol class name)
                    # e.g., "content_analysis_mcp" -> "ContentAnalysisMcpProtocol"
                    protocol_name = self.service_name.replace('_', ' ').title().replace(' ', '') + "Protocol"
                    
                    # Create capability definition
                    capability = CapabilityDefinition(
                        capability_name=tool_name,
                        service_name=self.service_name,
                        protocol_name=protocol_name,
                        description=tool_definition_dict["description"],
                        realm=self._get_realm(),
                        contracts={
                            "mcp_tool": {
                                "tool_name": tool_name,
                                "tool_definition": tool_definition_dict,
                                "metadata": {
                                    "server_name": self.service_name,
                                    "realm": self._get_realm(),
                                    "registered_at": datetime.utcnow().isoformat(),
                                    "tags": tool_definition_dict.get("tags", []),
                                    "requires_tenant": tool_definition_dict.get("requires_tenant", True)
                                }
                            }
                        },
                        version="1.0.0"
                    )
                    
                    # Register with Curator
                    success = await curator.register_domain_capability(capability, user_context)
                    if success:
                        registered_count += 1
                        self.logger.debug(f"✅ Registered MCP tool '{tool_name}' with Curator")
                    else:
                        self.logger.warning(f"⚠️ Failed to register MCP tool '{tool_name}' with Curator")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error registering tool '{tool_name}' with Curator: {e}")
                    continue
            
            if registered_count > 0:
                self.logger.info(f"✅ Registered {registered_count}/{total_tools} MCP tools with Curator for {self.service_name}")
            else:
                self.logger.warning(f"⚠️ No tools registered with Curator for {self.service_name}")
            
            return registered_count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register MCP server with Curator: {e}")
            return False
