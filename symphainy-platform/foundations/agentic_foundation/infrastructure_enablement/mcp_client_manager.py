#!/usr/bin/env python3
"""
MCP Client Manager - Agentic Realm Business Service

Manages MCP connections to Smart City roles with multi-tenant awareness.
Provides unified interface for agent-to-role communication via MCP tools.

This is a BUSINESS SERVICE that orchestrates role interactions and manages
tenant context. It uses direct MCP client injection for actual MCP communication.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

# Import utility mixins
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin


class MCPClientManager(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    MCP Client Manager - Agentic Realm Business Service
    
    Manages MCP connections to Smart City roles with multi-tenant awareness.
    Provides unified interface for agent-to-role communication via MCP tools.
    
    This is a BUSINESS SERVICE that orchestrates role interactions and manages
    tenant context. It uses direct MCP client injection for actual MCP communication.
    """
    
    def __init__(self, mcp_client_factory=None, di_container=None):
        """Initialize MCP Client Manager with MCP client factory."""
        if not di_container:
            raise ValueError("DI Container is required for MCPClientManager initialization")
        
        # Initialize utility mixins
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.di_container = di_container
        self.service_name = "mcp_client_manager"
        self.mcp_client_factory = mcp_client_factory
        self.active_connections: Dict[str, Any] = {}
        self.tenant_contexts: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("🔧 MCP Client Manager initialized with direct client injection")
    
    async def connect_to_role(self, role_name: str, tenant_id: str, connection_params: Dict[str, Any] = None, user_context: Dict[str, Any] = None) -> bool:
        """
        Connect to a Smart City role via MCP.
        
        Args:
            role_name: Name of the Smart City role to connect to
            tenant_id: Tenant ID for multi-tenant awareness
            connection_params: Optional connection parameters
            user_context: User context for security validation
            
        Returns:
            bool: True if connection successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("connect_to_role_start", success=True, details={"role_name": role_name, "tenant_id": tenant_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "mcp_connection", "write"):
                        await self.record_health_metric("connect_to_role_access_denied", 1.0, {"role_name": role_name})
                        await self.log_operation_with_telemetry("connect_to_role_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id_from_context = user_context.get("tenant_id")
                    if tenant_id_from_context and tenant_id_from_context != tenant_id:
                        await self.record_health_metric("connect_to_role_tenant_mismatch", 1.0, {"role_name": role_name})
                        await self.log_operation_with_telemetry("connect_to_role_complete", success=False)
                        return False
                    if tenant_id_from_context:
                        if not await tenant.validate_tenant_access(tenant_id_from_context):
                            await self.record_health_metric("connect_to_role_tenant_denied", 1.0, {"role_name": role_name})
                            await self.log_operation_with_telemetry("connect_to_role_complete", success=False)
                            return False
            
            self.logger.info(f"🔗 Connecting to role '{role_name}' for tenant '{tenant_id}'")
            
            # Create MCP client using factory
            if self.mcp_client_factory:
                mcp_client = self.mcp_client_factory()
            else:
                # Fallback to mock client for testing
                mcp_client = self._create_mock_client()
            
            # Store connection
            connection_key = f"{role_name}:{tenant_id}"
            self.active_connections[connection_key] = {
                "client": mcp_client,
                "role_name": role_name,
                "tenant_id": tenant_id,
                "connected_at": datetime.utcnow().isoformat(),
                "status": "connected"
            }
            
            # Store tenant context
            self.tenant_contexts[tenant_id] = {
                "tenant_id": tenant_id,
                "active_roles": [role_name],
                "last_activity": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("connect_to_role_success", 1.0, {"role_name": role_name, "tenant_id": tenant_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("connect_to_role_complete", success=True, details={"role_name": role_name, "tenant_id": tenant_id})
            
            self.logger.info(f"✅ Connected to role '{role_name}' for tenant '{tenant_id}'")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "connect_to_role", details={"role_name": role_name, "tenant_id": tenant_id})
            self.logger.error(f"❌ Failed to connect to role '{role_name}': {e}")
            return False
    
    async def execute_tool(self, role_name: str, tenant_id: str, tool_name: str, parameters: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a tool on a connected Smart City role.
        
        Args:
            role_name: Name of the Smart City role
            tenant_id: Tenant ID for multi-tenant awareness
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            user_context: User context for tenant validation
            
        Returns:
            Dict[str, Any]: Tool execution result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("execute_tool_start", success=True, 
                                                   details={"role_name": role_name, "tool_name": tool_name, "tenant_id": tenant_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "mcp_tool_execution", "write"):
                        await self.record_health_metric("execute_tool_access_denied", 1.0, {"role_name": role_name, "tool_name": tool_name})
                        await self.log_operation_with_telemetry("execute_tool_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id_from_context = user_context.get("tenant_id")
                    if tenant_id_from_context and tenant_id_from_context != tenant_id:
                        await self.record_health_metric("execute_tool_tenant_mismatch", 1.0, {"role_name": role_name, "tool_name": tool_name})
                        await self.log_operation_with_telemetry("execute_tool_complete", success=False)
                        return {"success": False, "error": "Tenant mismatch"}
                    if tenant_id_from_context:
                        if not await tenant.validate_tenant_access(tenant_id_from_context):
                            await self.record_health_metric("execute_tool_tenant_denied", 1.0, {"role_name": role_name, "tool_name": tool_name})
                            await self.log_operation_with_telemetry("execute_tool_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            connection_key = f"{role_name}:{tenant_id}"
            connection = self.active_connections.get(connection_key)
            
            if not connection:
                await self.record_health_metric("execute_tool_no_connection", 1.0, {"role_name": role_name, "tool_name": tool_name})
                await self.log_operation_with_telemetry("execute_tool_complete", success=False)
                raise ValueError(f"No active connection to role '{role_name}' for tenant '{tenant_id}'")
            
            self.logger.info(f"🔧 Executing tool '{tool_name}' on role '{role_name}' for tenant '{tenant_id}'")
            
            # Execute tool via MCP client
            client = connection["client"]
            result = await self._execute_tool_via_client(client, tool_name, parameters)
            
            # Update tenant context
            if tenant_id in self.tenant_contexts:
                self.tenant_contexts[tenant_id]["last_activity"] = datetime.utcnow().isoformat()
            
            # Record success metric
            await self.record_health_metric("execute_tool_success", 1.0, {"role_name": role_name, "tool_name": tool_name, "tenant_id": tenant_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("execute_tool_complete", success=True, 
                                                   details={"role_name": role_name, "tool_name": tool_name, "tenant_id": tenant_id})
            
            self.logger.info(f"✅ Tool '{tool_name}' executed successfully")
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "execute_tool", details={"role_name": role_name, "tool_name": tool_name, "tenant_id": tenant_id})
            self.logger.error(f"❌ Failed to execute tool '{tool_name}': {e}")
            return {"error": str(e), "success": False}
    
    async def _execute_tool_via_client(self, client: Any, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool via MCP client."""
        try:
            # This would be the actual MCP tool execution
            # For now, return a mock result
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": f"Mock result for {tool_name}",
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _create_mock_client(self) -> Any:
        """Create a mock MCP client for testing."""
        class MockMCPClient:
            def __init__(self):
                self.connected = True
            
            async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]):
                return {"result": f"Mock execution of {tool_name}", "success": True}
        
        return MockMCPClient()
    
    async def disconnect_from_role(self, role_name: str, tenant_id: str, user_context: Dict[str, Any] = None) -> bool:
        """Disconnect from a Smart City role."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("disconnect_from_role_start", success=True, details={"role_name": role_name, "tenant_id": tenant_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "mcp_connection", "write"):
                        await self.record_health_metric("disconnect_from_role_access_denied", 1.0, {"role_name": role_name})
                        await self.log_operation_with_telemetry("disconnect_from_role_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id_from_context = user_context.get("tenant_id")
                    if tenant_id_from_context and tenant_id_from_context != tenant_id:
                        await self.record_health_metric("disconnect_from_role_tenant_mismatch", 1.0, {"role_name": role_name})
                        await self.log_operation_with_telemetry("disconnect_from_role_complete", success=False)
                        return False
                    if tenant_id_from_context:
                        if not await tenant.validate_tenant_access(tenant_id_from_context):
                            await self.record_health_metric("disconnect_from_role_tenant_denied", 1.0, {"role_name": role_name})
                            await self.log_operation_with_telemetry("disconnect_from_role_complete", success=False)
                            return False
            
            connection_key = f"{role_name}:{tenant_id}"
            if connection_key in self.active_connections:
                del self.active_connections[connection_key]
                
                # Record success metric
                await self.record_health_metric("disconnect_from_role_success", 1.0, {"role_name": role_name, "tenant_id": tenant_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("disconnect_from_role_complete", success=True, details={"role_name": role_name, "tenant_id": tenant_id})
                
                self.logger.info(f"✅ Disconnected from role '{role_name}' for tenant '{tenant_id}'")
                return True
            
            # Record not found metric
            await self.record_health_metric("disconnect_from_role_not_found", 1.0, {"role_name": role_name, "tenant_id": tenant_id})
            await self.log_operation_with_telemetry("disconnect_from_role_complete", success=True)
            
            return False
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "disconnect_from_role", details={"role_name": role_name, "tenant_id": tenant_id})
            self.logger.error(f"❌ Failed to disconnect from role '{role_name}': {e}")
            return False
    
    async def get_active_connections(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get active MCP connections."""
        if tenant_id:
            return {k: v for k, v in self.active_connections.items() if v["tenant_id"] == tenant_id}
        return self.active_connections.copy()
    
    async def get_tenant_context(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant context information."""
        return self.tenant_contexts.get(tenant_id)