"""
MCP Client Manager - Smart City Role Connection Management with Multi-Tenancy (Refactored with Pure DI)

Manages connections to all Smart City role MCP servers with multi-tenant awareness.
Provides unified interface for agent-to-role communication via MCP tools.

WHAT (Agentic Role): I manage MCP connections to Smart City roles for agent communication
HOW (MCP Client Manager): I use pure dependency injection and provide unified role access
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

# Import DIContainerService DI container
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import utility mixins
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin


class MCPClientManager(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    Manages MCP connections to Smart City roles with multi-tenant awareness.
    
    Refactored to use pure dependency injection through DIContainerService.
    
    Provides unified interface for agents to communicate with:
    - Librarian (document storage, metadata)
    - Data Steward (data quality, lifecycle)
    - Conductor (workflow management)
    - Post Office (structured outputs)
    - Security Guard (authentication/authorization)
    - Nurse (health monitoring, telemetry)
    - City Manager (governance, policies)
    - Traffic Cop (session management)
    
    Uses MCP tools for interaction (not direct business abstractions).
    """
    
    def __init__(self, foundation_services: DIContainerService,
                 agentic_foundation: 'AgenticFoundationService'):
        """Initialize MCP client manager with pure dependency injection."""
        # Initialize utility mixins
        self._init_utility_access(foundation_services)
        self._init_performance_monitoring(foundation_services)
        
        self.foundation_services = foundation_services
        self.agentic_foundation = agentic_foundation
        self.service_name = "mcp_client_manager"
        
        # Get utilities via mixins (logger is available from mixin)
        # Keep direct access for backward compatibility during migration
        self.config = foundation_services.get_config()
        self.health = foundation_services.get_health()
        self.telemetry = foundation_services.get_telemetry()
        self.security = foundation_services.get_security()
        
        # Multi-tenant context
        self.tenant_context = None
        self.tenant_isolation_enabled = True
        
        # Agentic business abstractions from public works
        self.agentic_abstractions = {}
        
        # Curator Foundation for service discovery
        self.curator_foundation = None
        
        # Unified Smart City MCP endpoint (discovered via Curator or config)
        self.smart_city_endpoint = None
        
        # Smart City role mappings (all point to unified endpoint)
        self.role_mappings = {
            "librarian": None,  # Will be set after discovery
            "data_steward": None,
            "conductor": None,
            "post_office": None,
            "security_guard": None,
            "nurse": None,
            "city_manager": None,
            "traffic_cop": None,
            "content_steward": None
        }
        
        # Active connection to unified server (single connection instead of 8)
        self.smart_city_connection = None
        
        # Business Enablement MCP server endpoints (discovered via Curator)
        self.business_enablement_mcp_servers = {}  # {server_name: endpoint}
        
        # Active connections (legacy - for backward compatibility during migration)
        self.connections = {}
        
        # MCP tools for smart city role interaction
        self.mcp_tools = {}
        
        self.logger.info("MCP Client Manager initialized - will discover MCP endpoint via Curator")
    
    async def initialize(self):
        """
        Initialize MCP Client Manager by discovering MCP server endpoint via Curator.
        
        This method should be called after DI Container is fully initialized.
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("mcp_client_manager_initialize_start", success=True)
            # Get Curator Foundation from DI Container
            self.curator_foundation = self.foundation_services.service_registry.get("CuratorFoundationService")
            if not self.curator_foundation:
                # Try alternative access method
                self.curator_foundation = self.foundation_services.get_foundation_service("CuratorFoundationService")
            
            if self.curator_foundation:
                # Try to discover MCP server via Curator
                mcp_server = await self.curator_foundation.discover_service_by_name("SmartCityMCPServer")
                if mcp_server:
                    # Extract endpoint from service
                    if hasattr(mcp_server, 'base_url'):
                        self.smart_city_endpoint = mcp_server.base_url
                    elif hasattr(mcp_server, 'endpoint'):
                        self.smart_city_endpoint = mcp_server.endpoint
                    elif isinstance(mcp_server, dict):
                        self.smart_city_endpoint = mcp_server.get("base_url") or mcp_server.get("endpoint")
                    
                    self.logger.info(f"✅ Discovered MCP server endpoint via Curator: {self.smart_city_endpoint}")
                else:
                    self.logger.warning("⚠️ MCP server not found in Curator - will use config fallback")
            else:
                self.logger.warning("⚠️ Curator Foundation not available - will use config fallback")
            
            # Fallback: Load from config if Curator discovery failed
            if not self.smart_city_endpoint:
                self.smart_city_endpoint = self._get_mcp_endpoint_from_config()
                self.logger.info(f"✅ Using MCP endpoint from config: {self.smart_city_endpoint}")
            
            # Update all role mappings to use discovered endpoint
            for role_name in self.role_mappings.keys():
                self.role_mappings[role_name] = self.smart_city_endpoint
            
            # Discover Business Enablement MCP servers via Curator
            if self.curator_foundation:
                await self._discover_business_enablement_mcp_servers()
            
            # Record success metric
            await self.record_health_metric("mcp_client_manager_initialize_success", 1.0, {"endpoint": self.smart_city_endpoint})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("mcp_client_manager_initialize_complete", success=True, 
                                                   details={"endpoint": self.smart_city_endpoint})
            
            self.logger.info(f"✅ MCP Client Manager initialized with endpoint: {self.smart_city_endpoint}")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "mcp_client_manager_initialize")
            self.logger.error(f"❌ Failed to initialize MCP Client Manager: {e}")
            # Fallback to config
            self.smart_city_endpoint = self._get_mcp_endpoint_from_config()
            for role_name in self.role_mappings.keys():
                self.role_mappings[role_name] = self.smart_city_endpoint
            self.logger.warning(f"⚠️ Using fallback endpoint from config: {self.smart_city_endpoint}")
    
    async def _discover_business_enablement_mcp_servers(self):
        """
        Discover Business Enablement MCP servers via Curator.
        
        Business Enablement orchestrators register their MCP servers with Curator.
        This method discovers them by:
        1. Querying Curator for services with "MCPServer" in the name and "business_enablement" realm
        2. Querying Curator for capabilities with mcp_tool contracts in business_enablement realm
        """
        try:
            if not self.curator_foundation:
                return
            
            # Business Enablement MCP server names to discover
            be_mcp_server_names = [
                "ContentAnalysisMCPServer",
                "InsightsMCPServer",
                "OperationsMCPServer",
                "BusinessOutcomesMCPServer"
            ]
            
            discovered_count = 0
            
            # Try to discover each Business Enablement MCP server by name
            for server_name in be_mcp_server_names:
                try:
                    # Try discover_service_by_name (uses service discovery)
                    mcp_server = await self.curator_foundation.discover_service_by_name(server_name)
                    
                    if mcp_server:
                        # Extract endpoint from service
                        endpoint = None
                        if hasattr(mcp_server, 'base_url'):
                            endpoint = mcp_server.base_url
                        elif hasattr(mcp_server, 'endpoint'):
                            endpoint = mcp_server.endpoint
                        elif isinstance(mcp_server, dict):
                            endpoint = mcp_server.get("base_url") or mcp_server.get("endpoint")
                        
                        if endpoint:
                            self.business_enablement_mcp_servers[server_name] = endpoint
                            discovered_count += 1
                            self.logger.info(f"✅ Discovered Business Enablement MCP server: {server_name} at {endpoint}")
                except Exception as e:
                    self.logger.debug(f"Could not discover {server_name} via service name: {e}")
                    continue
            
            # Alternative: Discover via capability registry (tools registered as capabilities)
            # Query capabilities with mcp_tool contracts in business_enablement realm
            try:
                if hasattr(self.curator_foundation, 'capability_registry'):
                    # Get all capabilities in business_enablement realm
                    # This is a fallback if service discovery doesn't work
                    # We can discover MCP servers by finding tools registered by them
                    pass  # TODO: Implement capability-based discovery if needed
            except Exception as e:
                self.logger.debug(f"Could not discover via capability registry: {e}")
            
            if discovered_count > 0:
                self.logger.info(f"✅ Discovered {discovered_count} Business Enablement MCP server(s)")
            else:
                self.logger.debug("⚠️ No Business Enablement MCP servers discovered (may not be registered yet)")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover Business Enablement MCP servers: {e}")
            # Non-blocking - agents can still work with Smart City MCP tools
    
    def _get_mcp_endpoint_from_config(self) -> str:
        """
        Get MCP endpoint from configuration.
        
        Returns:
            MCP endpoint URL
        """
        try:
            # Try to get from config
            if self.config:
                # Check infrastructure config
                mcp_config = self.config.get("infrastructure", {}).get("mcp_server", {})
                if mcp_config:
                    base_url = mcp_config.get("base_url") or mcp_config.get("url")
                    port = mcp_config.get("port", 8000)
                    if base_url:
                        # If base_url includes port, use it; otherwise append port
                        if ":" in base_url.split("://")[-1]:
                            return base_url
                        else:
                            return f"{base_url}:{port}/mcp"
                
                # Fallback: construct from api_server config or mcp_server config
                mcp_config = self.config.get("infrastructure", {}).get("mcp_server", {})
                if mcp_config:
                    base_url = mcp_config.get("base_url", "http://localhost")
                    port = mcp_config.get("port", 8000)
                    endpoint_path = mcp_config.get("endpoint_path", "/mcp")
                    # Construct full endpoint
                    if "://" in base_url:
                        # base_url already includes protocol
                        if ":" in base_url.split("://")[-1]:
                            # Port already in base_url
                            return f"{base_url}{endpoint_path}"
                        else:
                            return f"{base_url}:{port}{endpoint_path}"
                    else:
                        return f"http://{base_url}:{port}{endpoint_path}"
                
                # Fallback to api_server config
                api_server = self.config.get("infrastructure", {}).get("api_server", {})
                host = api_server.get("host", "localhost")
                port = api_server.get("port", 8000)
                # Use localhost for local connections, host for others
                if host == "0.0.0.0":
                    host = "localhost"
                return f"http://{host}:{port}/mcp"
            
            # Ultimate fallback
            return "http://localhost:8000/mcp"
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get MCP endpoint from config: {e}")
            return "http://localhost:8000/mcp"
    
    async def set_tenant_context(self, tenant_context: Dict[str, Any]) -> bool:
        """Set tenant context for multi-tenant operations."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("set_tenant_context_start", success=True)
            
            if not tenant_context:
                await self.record_health_metric("set_tenant_context_invalid", 1.0, {})
                await self.log_operation_with_telemetry("set_tenant_context_complete", success=False)
                return False
            
            self.tenant_context = tenant_context
            
            # Update all existing connections with tenant context
            for role_name, connection in self.connections.items():
                if connection:
                    connection["tenant_context"] = tenant_context
            
            # Record success metric
            await self.record_health_metric("set_tenant_context_success", 1.0, {"tenant_id": tenant_context.get('tenant_id', 'unknown')})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("set_tenant_context_complete", success=True, 
                                                   details={"tenant_id": tenant_context.get('tenant_id', 'unknown')})
            
            self.logger.info(f"Tenant context set for MCP Client Manager: {tenant_context.get('tenant_id', 'unknown')}")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "set_tenant_context")
            self.logger.error(f"Failed to set tenant context: {e}")
            return False
    
    async def load_agentic_abstractions(self):
        """Load agentic business abstractions from agentic foundation."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("load_agentic_abstractions_start", success=True)
            
            if self.agentic_foundation:
                # Get agentic abstractions from agentic foundation
                self.agentic_abstractions = await self.agentic_foundation.get_agentic_abstractions()
                
                # Record success metric
                await self.record_health_metric("load_agentic_abstractions_success", 1.0, {"abstractions_count": len(self.agentic_abstractions)})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("load_agentic_abstractions_complete", success=True, 
                                                        details={"abstractions_count": len(self.agentic_abstractions)})
                
                self.logger.info(f"Loaded {len(self.agentic_abstractions)} agentic business abstractions")
            else:
                await self.record_health_metric("load_agentic_abstractions_not_available", 1.0, {})
                await self.log_operation_with_telemetry("load_agentic_abstractions_complete", success=True)
                self.logger.warning("Agentic foundation not available - using limited abstractions")
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "load_agentic_abstractions")
            self.logger.error(f"Failed to load agentic abstractions: {e}")
            self.agentic_abstractions = {}
    
    # ============================================================================
    # ENHANCED PLATFORM CAPABILITIES FOR AGENTS
    # ============================================================================
    
    async def discover_business_enablement_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Discover Business Enablement MCP tools via Curator.
        
        Returns:
            List of discovered MCP tools from Business Enablement orchestrators
        """
        try:
            if not self.curator_foundation:
                return []
            
            discovered_tools = []
            
            # Query Curator for capabilities with mcp_tool contracts in business_enablement realm
            if hasattr(self.curator_foundation, 'capability_registry'):
                try:
                    # Get all capabilities in business_enablement realm
                    # This would require a method to query by realm
                    # For now, we'll try to discover via service names
                    pass
                except Exception as e:
                    self.logger.debug(f"Could not discover tools via capability registry: {e}")
            
            # Alternative: Discover tools from discovered Business Enablement MCP servers
            for server_name, endpoint in self.business_enablement_mcp_servers.items():
                try:
                    # Try to get tools from the MCP server
                    # In real implementation, this would query the MCP server for its tools
                    # For now, we return the server info as a tool source
                    discovered_tools.append({
                        "name": server_name,
                        "endpoint": endpoint,
                        "type": "business_enablement_mcp_server",
                        "realm": "business_enablement"
                    })
                except Exception as e:
                    self.logger.debug(f"Could not get tools from {server_name}: {e}")
            
            return discovered_tools
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover Business Enablement MCP tools: {e}")
            return []
    
    async def get_enhanced_tool_discovery(self) -> Dict[str, Any]:
        """Get enhanced tool discovery capabilities for agents."""
        try:
            if self.agentic_foundation:
                # Get agent service discovery capabilities
                service_discovery = getattr(self.agentic_foundation, 'agent_service_discovery', {})
                capability_registry = getattr(self.agentic_foundation, 'agent_capability_registry', {})
                
                return {
                    "tool_discovery": {
                        "agent_capability_discovery": service_discovery.get("agent_capability_discovery", False),
                        "agent_service_discovery": service_discovery.get("agent_service_discovery", False),
                        "agent_endpoint_discovery": service_discovery.get("agent_endpoint_discovery", False)
                    },
                    "capability_registry": {
                        "agent_types": capability_registry.get("agent_types", []),
                        "agent_tools": capability_registry.get("agent_tools", []),
                        "available_capabilities": len(capability_registry.get("agent_capabilities", {}))
                    }
                }
            return {}
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_enhanced_tool_discovery")
            self.logger.error(f"Failed to get enhanced tool discovery: {e}")
            return {}
    
    async def get_enhanced_security_capabilities(self) -> Dict[str, Any]:
        """Get enhanced security capabilities for agents."""
        try:
            if self.agentic_foundation:
                # Get agent security capabilities
                access_control = getattr(self.agentic_foundation, 'agent_access_control', {})
                policy_enforcement = getattr(self.agentic_foundation, 'agent_policy_enforcement', {})
                tenant_isolation = getattr(self.agentic_foundation, 'agent_tenant_isolation', {})
                
                return {
                    "access_control": access_control,
                    "policy_enforcement": policy_enforcement,
                    "tenant_isolation": tenant_isolation
                }
            return {}
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_enhanced_security_capabilities")
            self.logger.error(f"Failed to get enhanced security capabilities: {e}")
            return {}
    
    async def get_enhanced_utility_capabilities(self) -> Dict[str, Any]:
        """Get enhanced utility capabilities for agents."""
        try:
            if self.agentic_foundation:
                # Get agent utility capabilities
                logging = getattr(self.agentic_foundation, 'agent_logging', {})
                error_handling = getattr(self.agentic_foundation, 'agent_error_handling', {})
                health_monitoring = getattr(self.agentic_foundation, 'agent_health_monitoring', {})
                
                return {
                    "logging": logging,
                    "error_handling": error_handling,
                    "health_monitoring": health_monitoring
                }
            return {}
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_enhanced_utility_capabilities")
            self.logger.error(f"Failed to get enhanced utility capabilities: {e}")
            return {}
    
    async def connect_to_role(self, role_name: str, tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Establish MCP connection to Smart City role via unified endpoint.
        
        All Smart City roles use the unified MCP server endpoint.
        This method connects to the unified server if not already connected.
        
        Args:
            role_name: Name of the Smart City role
            tenant_context: Tenant context for multi-tenant operations
            
        Returns:
            Dict containing connection information
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("connect_to_role_start", success=True, details={"role_name": role_name})
            
            if role_name not in self.role_mappings:
                raise ValueError(f"Unknown Smart City role: {role_name}")
            
            # Ensure MCP endpoint is discovered/initialized
            if not self.smart_city_endpoint:
                await self.initialize()
            
            if not self.smart_city_endpoint:
                raise RuntimeError("MCP server endpoint not available - cannot connect to role")
            
            # Connect to unified Smart City MCP server (if not already connected)
            if not self.smart_city_connection:
                self.logger.info(f"Connecting to unified Smart City MCP server: {self.smart_city_endpoint}")
                self.smart_city_connection = await self._connect_to_smart_city(tenant_context)
                self.logger.info("✅ Connected to unified Smart City MCP server")
            
            # Create/return connection info for this role (all use same unified connection)
            connection = {
                "role_name": role_name,
                "endpoint": self.smart_city_endpoint,
                "unified_connection": self.smart_city_connection,
                "connected_at": datetime.now().isoformat(),
                "status": "connected",
                "capabilities": self._get_role_capabilities(role_name),
                "tenant_context": tenant_context,
                "mcp_protocol_version": "1.0"
            }
            
            # Store for backward compatibility
            self.connections[role_name] = connection
            
            # Record success metric
            await self.record_health_metric("connect_to_role_success", 1.0, {"role_name": role_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("connect_to_role_complete", success=True, details={"role_name": role_name})
            
            self.logger.info(f"Connected to {role_name} via unified Smart City MCP server")
            return connection
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "connect_to_role", details={"role_name": role_name})
            self.logger.error(f"Failed to connect to {role_name}: {e}")
            raise
    
    async def _connect_to_smart_city(self, tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Connect to unified Smart City MCP server.
        
        Args:
            tenant_context: Tenant context for multi-tenant operations
            
        Returns:
            Dict containing unified connection information
        """
        try:
            # Establish connection to unified Smart City MCP server
            # In real implementation, this would establish actual MCP connection
            connection = {
                "endpoint": self.smart_city_endpoint,
                "connected_at": datetime.now().isoformat(),
                "status": "connected",
                "server_type": "unified",
                "available_roles": list(self.role_mappings.keys()),
                "tenant_context": tenant_context,
                "mcp_protocol_version": "1.0"
            }
            
            self.logger.info(f"Connected to unified Smart City MCP server: {self.smart_city_endpoint}")
            return connection
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_connect_to_smart_city")
            self.logger.error(f"Failed to connect to unified Smart City MCP server: {e}")
            raise
    
    async def _create_connection(self, role_name: str, tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create MCP connection to specific role with tenant context (legacy method)."""
        try:
            # This method is kept for backward compatibility
            # It now uses the unified endpoint
            connection = {
                "role_name": role_name,
                "endpoint": self.smart_city_endpoint,
                "connected_at": datetime.now().isoformat(),
                "status": "connected",
                "capabilities": self._get_role_capabilities(role_name),
                "tenant_context": tenant_context,
                "mcp_protocol_version": "1.0"
            }
            
            return connection
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_create_connection", details={"role_name": role_name})
            self.logger.error(f"Failed to create connection to {role_name}: {e}")
            raise
    
    async def _create_mcp_tool(self, role_name: str, connection: Dict[str, Any]):
        """Create MCP tool for smart city role interaction."""
        try:
            # Create MCP tool for role interaction
            mcp_tool = MCPTool(
                role_name=role_name,
                connection=connection,
                tenant_context=self.tenant_context,
                di_container=self.di_container
            )
            
            self.mcp_tools[role_name] = mcp_tool
            self.logger.info(f"Created MCP tool for {role_name}")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_create_mcp_tool", details={"role_name": role_name})
            self.logger.error(f"Failed to create MCP tool for {role_name}: {e}")
            raise
    
    def get_mcp_tool(self, role_name: str) -> Optional['MCPTool']:
        """Get MCP tool for specific role."""
        return self.mcp_tools.get(role_name)
    
    def _get_role_capabilities(self, role_name: str) -> List[str]:
        """Get capabilities for specific Smart City role."""
        capabilities_map = {
            "librarian": [
                "document_storage",
                "metadata_management", 
                "knowledge_discovery",
                "semantic_search"
            ],
            "data_steward": [
                "data_quality",
                "data_lifecycle",
                "data_governance",
                "metadata_management"
            ],
            "conductor": [
                "workflow_management",
                "task_orchestration",
                "celery_integration",
                "crew_management"
            ],
            "post_office": [
                "message_delivery",
                "structured_outputs",
                "event_routing",
                "communication"
            ],
            "security_guard": [
                "authentication",
                "authorization",
                "security_monitoring",
                "threat_detection"
            ],
            "nurse": [
                "health_monitoring",
                "telemetry_collection",
                "alert_triage",
                "error_handling"
            ],
            "city_manager": [
                "governance",
                "policy_management",
                "resource_allocation",
                "coordination"
            ],
            "traffic_cop": [
                "session_management",
                "request_routing",
                "traffic_management",
                "state_management"
            ]
        }
        
        return capabilities_map.get(role_name, [])
    
    async def execute_role_tool(self, role_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on a specific Smart City role via unified MCP server.
        
        Tools are automatically namespaced: {role_name}_{tool_name}
        Example: execute_role_tool("librarian", "upload_file", {...})
                 calls: librarian_upload_file on unified server
        
        Args:
            role_name: Name of the Smart City role
            tool_name: Name of the tool to execute (without role prefix)
            parameters: Parameters for tool execution
            
        Returns:
            Dict containing tool execution results
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("execute_role_tool_start", success=True, 
                                                   details={"role_name": role_name, "tool_name": tool_name})
            
            # Ensure connected to unified server
            if not self.smart_city_connection:
                await self.connect_to_role(role_name)
            
            # Construct namespaced tool name
            namespaced_tool_name = f"{role_name}_{tool_name}"
            
            # Add tenant context to parameters
            parameters_with_tenant = {
                **parameters,
                "tenant_context": self.tenant_context or {}
            }
            
            # Execute tool via unified MCP server
            # In real implementation, this would call the unified MCP server
            # For now, we simulate the call structure
            result = await self._call_unified_mcp_tool(namespaced_tool_name, parameters_with_tenant)
            
            # Record success metric
            await self.record_health_metric("execute_role_tool_success", 1.0, {"role_name": role_name, "tool_name": tool_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("execute_role_tool_complete", success=True, 
                                                   details={"role_name": role_name, "tool_name": tool_name})
            
            self.logger.info(f"Executed {namespaced_tool_name} via unified Smart City MCP server")
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "execute_role_tool", 
                                              details={"role_name": role_name, "tool_name": tool_name})
            self.logger.error(f"Failed to execute {role_name}/{tool_name}: {e}")
            raise
    
    async def _call_unified_mcp_tool(self, namespaced_tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the unified Smart City MCP server.
        
        Args:
            namespaced_tool_name: Tool name with role prefix (e.g., "librarian_upload_file")
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            # Get unified MCP server instance from DI Container
            # In real implementation, this would call the actual MCP server
            smart_city_mcp_server = self.foundation_services.get_service("SmartCityMCPServer")
            
            if smart_city_mcp_server:
                # Execute tool via unified server
                result = await smart_city_mcp_server.execute_tool(namespaced_tool_name, parameters)
                return result
            else:
                # Fallback: simulate tool execution
                self.logger.warning(f"Smart City MCP Server not found in DI Container - simulating tool call")
                return {
                    "success": True,
                    "tool_name": namespaced_tool_name,
                    "result": f"Simulated execution of {namespaced_tool_name}",
                    "parameters": parameters,
                    "note": "Unified MCP server not available - simulated response"
                }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_call_unified_mcp_tool", 
                                              details={"tool_name": namespaced_tool_name})
            self.logger.error(f"Failed to call unified MCP tool {namespaced_tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": namespaced_tool_name
            }
    
    async def get_role_health(self, role_name: str) -> Dict[str, Any]:
        """Get health status of a specific Smart City role."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_role_health_start", success=True, details={"role_name": role_name})
            
            if role_name not in self.connections:
                await self.record_health_metric("get_role_health_not_connected", 1.0, {"role_name": role_name})
                await self.log_operation_with_telemetry("get_role_health_complete", success=True)
                return {"status": "not_connected", "role_name": role_name}
            
            connection = self.connections[role_name]
            mcp_tool = self.get_mcp_tool(role_name)
            
            # Get health via MCP tool
            if mcp_tool:
                health_result = await mcp_tool.get_health()
                result = {
                    "status": "connected",
                    "role_name": role_name,
                    "health": health_result,
                    "tenant_context": self.tenant_context
                }
            else:
                result = {
                    "status": "connected_no_tool",
                    "role_name": role_name,
                    "connection": connection
                }
            
            # Record success metric
            await self.record_health_metric("get_role_health_success", 1.0, {"role_name": role_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_role_health_complete", success=True, details={"role_name": role_name})
            
            return result
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_role_health", details={"role_name": role_name})
            self.logger.error(f"Failed to get health for {role_name}: {e}")
            return {"status": "error", "role_name": role_name, "error": str(e)}
    
    async def get_all_connections_health(self) -> Dict[str, Any]:
        """Get health status of all Smart City role connections."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_all_connections_health_start", success=True)
            
            health_status = {}
            
            for role_name in self.role_mappings.keys():
                health_status[role_name] = await self.get_role_health(role_name)
            
            result = {
                "overall_status": "healthy",
                "connections": health_status,
                "tenant_context": self.tenant_context,
                "total_connections": len(self.connections)
            }
            
            # Record success metric
            await self.record_health_metric("get_all_connections_health_success", 1.0, {"total_connections": len(self.connections)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_all_connections_health_complete", success=True, 
                                                   details={"total_connections": len(self.connections)})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_all_connections_health")
            self.logger.error(f"Failed to get all connections health: {e}")
            return {"overall_status": "error", "error": str(e)}
    
    async def disconnect_from_role(self, role_name: str) -> bool:
        """Disconnect from a specific Smart City role."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("disconnect_from_role_start", success=True, details={"role_name": role_name})
            
            if role_name in self.connections:
                # Remove MCP tool
                if role_name in self.mcp_tools:
                    del self.mcp_tools[role_name]
                
                # Remove connection
                del self.connections[role_name]
                
                # Record success metric
                await self.record_health_metric("disconnect_from_role_success", 1.0, {"role_name": role_name})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("disconnect_from_role_complete", success=True, details={"role_name": role_name})
                
                self.logger.info(f"Disconnected from {role_name}")
                return True
            else:
                await self.record_health_metric("disconnect_from_role_not_connected", 1.0, {"role_name": role_name})
                await self.log_operation_with_telemetry("disconnect_from_role_complete", success=True)
                self.logger.warning(f"Not connected to {role_name}")
                return False
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "disconnect_from_role", details={"role_name": role_name})
            self.logger.error(f"Failed to disconnect from {role_name}: {e}")
            return False
    
    async def disconnect_all(self) -> bool:
        """Disconnect from all Smart City roles."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("disconnect_all_start", success=True)
            
            disconnected_count = 0
            
            for role_name in list(self.connections.keys()):
                if await self.disconnect_from_role(role_name):
                    disconnected_count += 1
            
            # Record success metric
            await self.record_health_metric("disconnect_all_success", 1.0, {"disconnected_count": disconnected_count})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("disconnect_all_complete", success=True, 
                                                   details={"disconnected_count": disconnected_count})
            
            self.logger.info(f"Disconnected from {disconnected_count} roles")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "disconnect_all")
            self.logger.error(f"Failed to disconnect from all roles: {e}")
            return False
    
    # ============================================================================
    # AGENTIC BUSINESS ABSTRACTION ACCESS
    # ============================================================================
    
    def get_agentic_abstraction(self, abstraction_name: str) -> Any:
        """Get a specific agentic business abstraction."""
        return self.agentic_abstractions.get(abstraction_name)
    
    def has_agentic_abstraction(self, abstraction_name: str) -> bool:
        """Check if an agentic business abstraction is available."""
        return abstraction_name in self.agentic_abstractions
    
    def get_all_agentic_abstractions(self) -> Dict[str, Any]:
        """Get all available agentic business abstractions."""
        return self.agentic_abstractions.copy()
    
    def get_agentic_abstraction_names(self) -> List[str]:
        """Get names of all available agentic business abstractions."""
        return list(self.agentic_abstractions.keys())
    
    # ============================================================================
    # MANAGER HEALTH AND STATUS
    # ============================================================================
    
    def get_manager_health(self) -> Dict[str, Any]:
        """Get MCP Client Manager health status."""
        return {
            "manager_name": "MCPClientManager",
            "tenant_context": self.tenant_context,
            "connections_count": len(self.connections),
            "mcp_tools_count": len(self.mcp_tools),
            "agentic_abstractions_loaded": len(self.agentic_abstractions),
            "agentic_abstraction_names": self.get_agentic_abstraction_names(),
            "connected_roles": list(self.connections.keys()),
            "available_roles": list(self.role_mappings.keys()),
            "status": "healthy"
        }


class MCPTool:
    """MCP Tool for Smart City role interaction."""
    
    def __init__(self, role_name: str, connection: Dict[str, Any], tenant_context: Dict[str, Any] = None, di_container=None):
        """Initialize MCP tool for role interaction."""
        if not di_container:
            raise ValueError("DI Container is required for MCPTool initialization")
        
        self.role_name = role_name
        self.connection = connection
        self.tenant_context = tenant_context
        self.di_container = di_container
        
        # Get logger from DI Container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"mcp_tool_{role_name}")
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on the Smart City role."""
        try:
            # Simulated tool execution
            # In real implementation, this would make actual MCP calls
            
            result = {
                "tool_name": tool_name,
                "role_name": self.role_name,
                "parameters": parameters,
                "executed_at": datetime.now().isoformat(),
                "status": "success",
                "result": f"Tool {tool_name} executed on {self.role_name}",
                "tenant_context": self.tenant_context
            }
            
            self.logger.info(f"Executed {tool_name} on {self.role_name}")
            return result
            
        except Exception as e:
            # Note: MCPTool doesn't have mixins, but we can still log errors
            # In a full implementation, MCPTool would also have mixins or utilities passed in
            self.logger.error(f"Failed to execute {tool_name} on {self.role_name}: {e}")
            return {
                "tool_name": tool_name,
                "role_name": self.role_name,
                "status": "error",
                "error": str(e),
                "tenant_context": self.tenant_context
            }
    
    async def get_health(self) -> Dict[str, Any]:
        """Get health status of the Smart City role."""
        try:
            # Simulated health check
            # In real implementation, this would make actual health check calls
            
            return {
                "role_name": self.role_name,
                "status": "healthy",
                "endpoint": self.connection.get("endpoint"),
                "connected_at": self.connection.get("connected_at"),
                "capabilities": self.connection.get("capabilities", []),
                "tenant_context": self.tenant_context
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get health for {self.role_name}: {e}")
            return {
                "role_name": self.role_name,
                "status": "error",
                "error": str(e),
                "tenant_context": self.tenant_context
            }