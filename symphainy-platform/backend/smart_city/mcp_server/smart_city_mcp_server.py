#!/usr/bin/env python3
"""
Smart City Unified MCP Server

Unified MCP server for Smart City Realm providing single MCP endpoint
for all Smart City services with namespaced tool routing.

WHAT (MCP Server Role): I provide unified MCP endpoint for all Smart City services
HOW (MCP Implementation): I register all Smart City services and route tools with namespaced names
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from bases.mcp_server.mcp_server_base import MCPServerBase


class SmartCityMCPServer(MCPServerBase):
    """
    Unified MCP Server for Smart City Realm
    
    Provides single MCP endpoint for all Smart City services:
    - Librarian (knowledge management)
    - Data Steward (data governance)
    - Content Steward (content management)
    - Security Guard (authentication/authorization)
    - Conductor (workflow orchestration)
    - Post Office (messaging)
    - Traffic Cop (session/state management)
    - Nurse (health monitoring)
    - City Manager (platform governance)
    
    Tools are namespaced by role: {role}_{tool_name}
    Example: librarian_upload_file, data_steward_validate_schema
    """
    
    def __init__(self, di_container):
        """Initialize Smart City Unified MCP Server."""
        super().__init__(
            service_name="smart_city_mcp",
            di_container=di_container
        )
        
        self.registered_services = {}  # Track registered services for health checks
        self.logger.info("🏛️ Smart City Unified MCP Server initialized")
    
    def register_server_tools(self) -> None:
        """Register all tools from all Smart City services."""
        # Note: Tools are registered dynamically when services are initialized
        # This method is called by base class during initialization
        # Actual tool registration happens in async initialize() method
        pass
    
    async def initialize(self):
        """Initialize unified MCP server and register all Smart City services."""
        try:
            self.logger.info("🔧 Registering Smart City services with unified MCP server (Phase 2 - Curator discovery)...")
            
            # Get Curator Foundation for capability discovery
            curator = self.di_container.get_foundation_service("CuratorFoundationService")
            if not curator:
                self.logger.warning("⚠️ Curator Foundation not available, falling back to direct service discovery")
                return await self._initialize_fallback()
            
            # Get all Smart City services from DI Container for service instance access
            # Service class names match the pattern: {ServiceName}Service
            services_to_register = [
                ("librarian", "LibrarianService"),
                ("data_steward", "DataStewardService"),
                ("content_steward", "ContentStewardService"),
                ("security_guard", "SecurityGuardService"),
                ("conductor", "ConductorService"),
                ("post_office", "PostOfficeService"),
                ("traffic_cop", "TrafficCopService"),
                ("nurse", "NurseService"),
                ("city_manager", "CityManagerService")
            ]
            
            registered_count = 0
            total_tools = 0
            
            # Phase 2: Discover tools from Curator capability registry
            for role_name, service_class_name in services_to_register:
                try:
                    # Get service from DI Container (needed for handler execution)
                    service = self.di_container.get_service(service_class_name)
                    
                    if not service:
                        self.logger.warning(f"⚠️ Service {service_class_name} not found in DI Container")
                        continue
                    
                    # Ensure service is initialized
                    if not service.is_initialized:
                        self.logger.info(f"Initializing {role_name} service before registration...")
                        await service.initialize()
                    
                    # Discover capabilities from Curator (Phase 2 pattern)
                    capabilities = await curator.capability_registry.get_capabilities_by_service(
                        service_name=service_class_name
                    )
                    
                    if capabilities:
                        # Register tools from capability contracts
                        tools_count = await self._register_tools_from_capabilities(
                            service_name=role_name,
                            service_instance=service,
                            capabilities=capabilities,
                            tool_prefix=role_name
                        )
                        
                        registered_count += 1
                        total_tools += tools_count
                        self.logger.info(f"✅ Registered {role_name} service with {tools_count} tools (from Curator)")
                    else:
                        # Fallback: Try direct service discovery if no capabilities found
                        self.logger.warning(f"⚠️ No capabilities found in Curator for {role_name}, trying direct discovery...")
                        tools_count = await self._register_service_tools(
                            service_name=role_name,
                            service_instance=service,
                            tool_prefix=role_name
                        )
                        if tools_count > 0:
                            registered_count += 1
                            total_tools += tools_count
                            self.logger.info(f"✅ Registered {role_name} service with {tools_count} tools (fallback)")
                
                except Exception as e:
                    self.logger.error(f"❌ Failed to register {role_name} service: {e}")
                    import traceback
                    self.logger.error(f"Traceback: {traceback.format_exc()}")
                    continue
            
            self.logger.info(
                f"✅ Smart City Unified MCP Server initialized with "
                f"{registered_count} services and {total_tools} tools (Phase 2 - Curator discovery)"
            )
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Smart City Unified MCP Server: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.service_health = "unhealthy"
            return False
    
    async def _initialize_fallback(self):
        """Fallback initialization using direct service discovery (old pattern)."""
        self.logger.info("🔄 Using fallback initialization (direct service discovery)...")
        
        services_to_register = [
            ("librarian", "LibrarianService"),
            ("data_steward", "DataStewardService"),
            ("content_steward", "ContentStewardService"),
            ("security_guard", "SecurityGuardService"),
            ("conductor", "ConductorService"),
            ("post_office", "PostOfficeService"),
            ("traffic_cop", "TrafficCopService"),
            ("nurse", "NurseService"),
            ("city_manager", "CityManagerService")
        ]
        
        registered_count = 0
        total_tools = 0
        
        for role_name, service_class_name in services_to_register:
            try:
                service = self.di_container.get_service(service_class_name)
                if service:
                    if not service.is_initialized:
                        await service.initialize()
                    
                    tools_count = await self._register_service_tools(
                        service_name=role_name,
                        service_instance=service,
                        tool_prefix=role_name
                    )
                    registered_count += 1
                    total_tools += tools_count
            except Exception as e:
                self.logger.error(f"❌ Failed to register {role_name}: {e}")
                continue
        
        self.is_initialized = True
        self.service_health = "healthy"
        return True
    
    async def _register_tools_from_capabilities(
        self, 
        service_name: str, 
        service_instance: Any, 
        capabilities: List[Any],
        tool_prefix: str
    ) -> int:
        """
        Register tools from Curator capabilities (Phase 2 pattern).
        
        Args:
            service_name: Name of the service (e.g., "librarian")
            service_instance: The service instance
            capabilities: List of CapabilityDefinition objects from Curator
            tool_prefix: Prefix for tool names (e.g., "librarian")
            
        Returns:
            int: Number of tools registered
        """
        try:
            tools_registered = 0
            
            # Extract MCP tools from capability contracts
            for capability in capabilities:
                if not hasattr(capability, 'contracts') or not capability.contracts:
                    continue
                
                # Check for MCP tool contract
                mcp_tool_contract = capability.contracts.get("mcp_tool")
                if not mcp_tool_contract:
                    continue
                
                # Extract tool definition from contract
                tool_definition = mcp_tool_contract.get("tool_definition", {})
                tool_name = mcp_tool_contract.get("tool_name", "")
                
                if not tool_name or not tool_definition:
                    continue
                
                # Use the tool name from contract (should already be namespaced)
                # If not namespaced, add prefix
                if not tool_name.startswith(tool_prefix):
                    namespaced_tool_name = f"{tool_prefix}_{tool_name}"
                else:
                    namespaced_tool_name = tool_name
                
                # Extract original tool name (without prefix) for handler lookup
                original_tool_name = tool_name.replace(f"{tool_prefix}_", "") if tool_name.startswith(tool_prefix) else tool_name
                
                # Create handler that routes to service
                def create_handler(original_tool: str, original_service: Any, original_service_name: str):
                    async def handler(parameters: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
                        """Tool handler that routes to service method."""
                        try:
                            # Try to find and call the service method
                            method = None
                            
                            # Try direct service method (e.g., _mcp_tool_name)
                            if hasattr(original_service, f"_mcp_{original_tool}"):
                                attr = getattr(original_service, f"_mcp_{original_tool}")
                                if callable(attr):
                                    method = attr
                            
                            # Try direct service method (e.g., tool_name)
                            if not method and hasattr(original_service, original_tool):
                                attr = getattr(original_service, original_tool)
                                if callable(attr):
                                    method = attr
                            
                            # Try via service modules
                            if not method and hasattr(original_service, 'modules'):
                                for module_name, module_instance in original_service.modules.items():
                                    if hasattr(module_instance, f"_mcp_{original_tool}"):
                                        attr = getattr(module_instance, f"_mcp_{original_tool}")
                                        if callable(attr):
                                            method = attr
                                            break
                                    if hasattr(module_instance, original_tool):
                                        attr = getattr(module_instance, original_tool)
                                        if callable(attr):
                                            method = attr
                                            break
                            
                            if method:
                                # Call the method (handle both async and sync)
                                if hasattr(method, '__code__') and 'coroutine' in str(type(method)):
                                    result = await method(**parameters, user_context=user_context)
                                else:
                                    result = method(**parameters, user_context=user_context)
                                
                                # Ensure result is a dict
                                if not isinstance(result, dict):
                                    result = {"success": True, "result": result}
                                
                                return result
                            else:
                                return {"success": False, "error": f"Tool {original_tool} not found in service {original_service_name}"}
                            
                        except Exception as e:
                            self.utilities.logger.error(f"❌ Error executing tool {original_tool} from {original_service_name}: {e}")
                            return {"success": False, "error": str(e)}
                    return handler
                
                # Register tool with MCP server
                self.register_tool(
                    tool_name=namespaced_tool_name,
                    handler=create_handler(original_tool_name, service_instance, service_name),
                    input_schema=tool_definition.get("input_schema", {}),
                    description=tool_definition.get("description", tool_definition.get("name", ""))
                )
                
                tools_registered += 1
            
            if tools_registered > 0:
                self.logger.info(f"✅ Registered {tools_registered} tools from {service_name} capabilities (Phase 2)")
            else:
                self.logger.warning(f"⚠️ No MCP tools found in capabilities for {service_name}")
            
            return tools_registered
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register tools from capabilities for {service_name}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return 0
    
    async def _register_service_tools(self, service_name: str, service_instance: Any, tool_prefix: str) -> int:
        """
        Register tools from a Smart City service.
        
        Args:
            service_name: Name of the service (e.g., "librarian")
            service_instance: The service instance
            tool_prefix: Prefix for tool names (e.g., "librarian")
            
        Returns:
            int: Number of tools registered
        """
        try:
            # Track registered service
            self.registered_services[service_name] = service_instance
            
            tools_registered = 0
            
            # Get mcp_tools from service
            mcp_tools = None
            if hasattr(service_instance, 'mcp_tools') and service_instance.mcp_tools:
                mcp_tools = service_instance.mcp_tools
            elif hasattr(service_instance, 'modules') and isinstance(service_instance.modules, dict):
                soa_mcp_module = service_instance.modules.get('soa_mcp_module')
                if soa_mcp_module and hasattr(soa_mcp_module, 'service'):
                    service_ref = soa_mcp_module.service
                    if hasattr(service_ref, 'mcp_tools'):
                        mcp_tools = service_ref.mcp_tools
            
            if mcp_tools:
                for tool_name, tool_def in mcp_tools.items():
                    namespaced_tool_name = f"{tool_prefix}_{tool_name}"
                    
                    # Create handler that routes to service (using closure to capture values)
                    def create_handler(original_tool_name: str, original_service: Any, original_service_name: str):
                        async def handler(parameters: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
                            """Tool handler that routes to service method."""
                            try:
                                # Try to find and call the service method
                                method = None
                                
                                # Try direct service method
                                if hasattr(original_service, original_tool_name):
                                    attr = getattr(original_service, original_tool_name)
                                    if callable(attr):
                                        method = attr
                                
                                # Try via service modules
                                if not method and hasattr(original_service, 'modules'):
                                    for module_name, module_instance in original_service.modules.items():
                                        if hasattr(module_instance, original_tool_name):
                                            attr = getattr(module_instance, original_tool_name)
                                            if callable(attr):
                                                method = attr
                                                break
                                
                                if method:
                                    # Call the method (handle both async and sync)
                                    if hasattr(method, '__code__') and 'coroutine' in str(type(method)):
                                        result = await method(**parameters, user_context=user_context)
                                    else:
                                        result = method(**parameters, user_context=user_context)
                                    
                                    # Ensure result is a dict
                                    if not isinstance(result, dict):
                                        result = {"success": True, "result": result}
                                    
                                    return result
                                else:
                                    return {"success": False, "error": f"Tool {original_tool_name} not found in service {original_service_name}"}
                                
                            except Exception as e:
                                self.utilities.logger.error(f"❌ Error executing tool {original_tool_name} from {original_service_name}: {e}")
                                return {"success": False, "error": str(e)}
                        return handler
                    
                    # Register tool with new base
                    self.register_tool(
                        tool_name=namespaced_tool_name,
                        handler=create_handler(tool_name, service_instance, service_name),
                        input_schema=tool_def.get("input_schema", {}),
                        description=tool_def.get("description", tool_def.get("name", ""))
                    )
                    
                    tools_registered += 1
                
                self.logger.info(f"✅ Registered {tools_registered} tools from {service_name} service")
            else:
                self.logger.warning(f"⚠️ No mcp_tools found for {service_name} service")
            
            return tools_registered
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register service {service_name}: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown unified MCP server gracefully."""
        try:
            self.logger.info("🛑 Shutting down Smart City Unified MCP Server...")
            
            # Clear registered services
            self.registered_services.clear()
            
            self.is_initialized = False
            self.service_health = "shutdown"
            
            self.logger.info("✅ Smart City Unified MCP Server shut down successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Smart City Unified MCP Server: {e}")
            return False
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Execute tool by routing to dynamically registered service handlers.
        
        SmartCityMCPServer handlers have signature: handler(parameters: Dict, user_context: Dict = None)
        This is different from other MCP servers which use **kwargs.
        """
        try:
            # Start telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "execute_tool_start",
                        "value": 1.0,
                        "type": "counter",
                        "labels": {"tool_name": tool_name, "mcp_server": self.service_name}
                    })
                except Exception:
                    pass  # Telemetry is optional
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.utilities.security
                if security:
                    if not await security.check_permissions(user_context, f"mcp_tool.{tool_name}", "execute"):
                        raise PermissionError(f"Access denied: insufficient permissions to execute tool '{tool_name}'")
            
            # Tenant validation (multi-tenancy support)
            if user_context:
                tenant = self.utilities.tenant
                if tenant:
                    tenant_id = user_context.get("tenant_id") if isinstance(user_context, dict) else getattr(user_context, "tenant_id", None)
                    if tenant_id:
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            raise PermissionError(f"Tenant access denied for tool '{tool_name}': {tenant_id}")
            
            # Get handler from registered tools
            registered_tools = self.get_registered_tools()
            tool_def = registered_tools.get(tool_name)
            
            if tool_def and tool_def.handler:
                # SmartCityMCPServer handlers expect (parameters, user_context) signature
                result = await tool_def.handler(parameters, user_context)
                
                # End telemetry tracking
                if self.utilities.telemetry:
                    try:
                        await self.utilities.telemetry.collect_metric({
                            "name": "execute_tool_complete",
                            "value": 1.0,
                            "type": "counter",
                            "labels": {"tool_name": tool_name, "status": "success" if result.get("success", True) else "failed"}
                        })
                    except Exception:
                        pass
                
                return result
            else:
                # Record health metric (tool not found)
                if self.utilities.health:
                    try:
                        await self.utilities.health.record_metric("execute_tool_not_found", 1.0, {"tool_name": tool_name})
                    except Exception:
                        pass
                
                # End telemetry tracking
                if self.utilities.telemetry:
                    try:
                        await self.utilities.telemetry.collect_metric({
                            "name": "execute_tool_complete",
                            "value": 0.0,
                            "type": "counter",
                            "labels": {"tool_name": tool_name, "status": "not_found"}
                        })
                    except Exception:
                        pass
                
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            # Error handling
            self.logger.error(f"❌ execute_tool failed for {tool_name}: {e}", exc_info=True)
            
            # End telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "execute_tool_complete",
                        "value": 0.0,
                        "type": "counter",
                        "labels": {"tool_name": tool_name, "status": "error"}
                    })
                except Exception:
                    pass
            
            return {"error": f"Failed to execute tool {tool_name}: {str(e)}"}
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return machine + human readable usage guide."""
        # Build tool registry grouped by service
        tools_by_service = {}
        registered_tools = self.get_registered_tools()
        for tool_name in registered_tools.keys():
            # Extract service name from namespaced tool name (format: {role}_{tool_name})
            if '_' in tool_name:
                service_name = tool_name.split('_')[0]
                if service_name not in tools_by_service:
                    tools_by_service[service_name] = []
                tools_by_service[service_name].append(tool_name)
        
        return {
            "server_name": self.service_name,
            "description": "Smart City Unified MCP Server - Provides unified MCP endpoint for all Smart City services",
            "server_type": "unified",
            "registered_services": list(self.registered_services.keys()),
            "tools_by_service": tools_by_service,
            "tool_naming_pattern": "{role}_{tool_name}",
            "usage_pattern": "All tools require user_context for multi-tenancy and security"
        }
    
    def get_tool_list(self) -> List[str]:
        """Return list of available tool names."""
        return list(self.get_registered_tools().keys())
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks."""
        try:
            # Add service-specific health
            service_health = {}
            for service_name, service_instance in self.registered_services.items():
                try:
                    if hasattr(service_instance, 'service_health'):
                        service_health[service_name] = service_instance.service_health
                    elif hasattr(service_instance, 'is_initialized'):
                        service_health[service_name] = "healthy" if service_instance.is_initialized else "initializing"
                    else:
                        service_health[service_name] = "unknown"
                except:
                    service_health[service_name] = "error"
            
            all_healthy = all(
                status == "healthy" or status == "initializing"
                for status in service_health.values()
            )
            
            return {
                "server_name": self.service_name,
                "status": "healthy" if all_healthy else "degraded",
                "service_health": service_health,
                "all_services_healthy": all_healthy,
                "tools_registered": len(self.get_tool_list()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "server_name": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_version_info(self) -> Dict[str, Any]:
        """Return version and compatibility info."""
        return {
            "server_name": self.service_name,
            "version": "1.0.0",
            "api_version": "v1",
            "compatible_with": list(self.registered_services.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }






