#!/usr/bin/env python3
"""
MCP Composition Service - Layer 3 of 5-Layer Architecture

This composition service provides business logic for MCP operations by coordinating
MCP abstractions and handling business concerns like tenant management, role
orchestration, and communication strategies.

WHAT (Business Role): I orchestrate MCP operations for agentic business logic
HOW (Composition Service): I coordinate MCP abstractions and handle business concerns
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.infrastructure_abstractions.mcp_abstraction import MCPAbstraction


class MCPCompositionService:
    """
    MCP Composition Service.
    
    Orchestrates MCP abstractions to provide business logic for MCP operations
    including tenant management, role orchestration, and communication strategies.
    """
    
    def __init__(self, mcp_abstraction: MCPAbstraction):
        """Initialize MCP composition service with MCP abstraction."""
        self.mcp_abstraction = mcp_abstraction
        self.logger = logging.getLogger("MCPCompositionService")
        
        # Business state
        self.active_tenants: Dict[str, Dict[str, Any]] = {}
        self.role_assignments: Dict[str, List[str]] = {}
        self.communication_strategies: Dict[str, str] = {}
        
        # Business metrics
        self.business_metrics = {
            "total_connections": 0,
            "active_tenants": 0,
            "role_interactions": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        self.logger.info("✅ MCP Composition Service initialized")
    
    async def establish_tenant_connections(self, tenant_id: str, 
                                         role_requirements: List[str]) -> Dict[str, Any]:
        """
        Establish MCP connections for a tenant with required roles.
        
        Args:
            tenant_id: Tenant identifier
            role_requirements: List of required role names
            
        Returns:
            Dict containing connection results for all required roles
        """
        try:
            self.logger.info(f"🏢 Establishing tenant connections for {tenant_id}")
            
            tenant_context = {
                "tenant_id": tenant_id,
                "established_at": datetime.now().isoformat(),
                "role_requirements": role_requirements
            }
            
            connection_results = {}
            successful_connections = 0
            
            for role_name in role_requirements:
                try:
                    # Get role endpoint (in real implementation, this would be dynamic)
                    endpoint = self._get_role_endpoint(role_name)
                    
                    # Connect to role
                    result = await self.mcp_abstraction.connect_to_server(
                        server_name=role_name,
                        endpoint=endpoint,
                        tenant_context=tenant_context
                    )
                    
                    connection_results[role_name] = result
                    
                    if result.get("success", False):
                        successful_connections += 1
                        self.logger.info(f"✅ Connected {role_name} for tenant {tenant_id}")
                    else:
                        self.logger.warning(f"⚠️ Failed to connect {role_name} for tenant {tenant_id}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error connecting {role_name} for tenant {tenant_id}: {e}")
                    connection_results[role_name] = {
                        "success": False,
                        "error": str(e),
                        "role_name": role_name
                    }
            
            # Update tenant state
            self.active_tenants[tenant_id] = {
                "tenant_id": tenant_id,
                "role_requirements": role_requirements,
                "successful_connections": successful_connections,
                "connection_results": connection_results,
                "established_at": datetime.now().isoformat()
            }
            
            # Update role assignments
            self.role_assignments[tenant_id] = role_requirements
            
            # Update metrics
            self.business_metrics["total_connections"] += successful_connections
            self.business_metrics["active_tenants"] = len(self.active_tenants)
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            return {
                "success": successful_connections > 0,
                "tenant_id": tenant_id,
                "successful_connections": successful_connections,
                "total_required": len(role_requirements),
                "connection_results": connection_results,
                "message": f"Established {successful_connections}/{len(role_requirements)} connections for tenant {tenant_id}"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to establish tenant connections for {tenant_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tenant_id": tenant_id
            }
    
    async def execute_tenant_operation(self, tenant_id: str, role_name: str, 
                                     tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation for a specific tenant and role.
        
        Args:
            tenant_id: Tenant identifier
            role_name: Name of the role
            tool_name: Name of the tool to execute
            parameters: Parameters for tool execution
            
        Returns:
            Dict containing operation result
        """
        try:
            # Validate tenant has access to role
            if tenant_id not in self.active_tenants:
                return {
                    "success": False,
                    "error": f"Tenant {tenant_id} not found",
                    "message": "Tenant not established"
                }
            
            if role_name not in self.role_assignments.get(tenant_id, []):
                return {
                    "success": False,
                    "error": f"Role {role_name} not assigned to tenant {tenant_id}",
                    "message": "Role not assigned to tenant"
                }
            
            # Add tenant context to parameters
            parameters_with_tenant = {
                **parameters,
                "tenant_id": tenant_id,
                "tenant_context": self.active_tenants[tenant_id]
            }
            
            # Execute tool
            result = await self.mcp_abstraction.execute_tool(
                server_name=role_name,
                tool_name=tool_name,
                parameters=parameters_with_tenant
            )
            
            # Update metrics
            if result.get("success", False):
                self.business_metrics["successful_operations"] += 1
                self.business_metrics["role_interactions"] += 1
            else:
                self.business_metrics["failed_operations"] += 1
            
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            self.logger.info(f"✅ Executed {tool_name} on {role_name} for tenant {tenant_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute operation for tenant {tenant_id}: {e}")
            self.business_metrics["failed_operations"] += 1
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            return {
                "success": False,
                "error": str(e),
                "tenant_id": tenant_id,
                "role_name": role_name,
                "tool_name": tool_name
            }
    
    async def get_tenant_health(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get health status for a specific tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Dict containing tenant health status
        """
        try:
            if tenant_id not in self.active_tenants:
                return {
                    "success": False,
                    "status": "tenant_not_found",
                    "message": f"Tenant {tenant_id} not found"
                }
            
            tenant_info = self.active_tenants[tenant_id]
            role_health = {}
            
            # Check health for each assigned role
            for role_name in self.role_assignments.get(tenant_id, []):
                health_result = await self.mcp_abstraction.get_server_health(role_name)
                role_health[role_name] = health_result
            
            # Calculate overall tenant health
            healthy_roles = sum(1 for health in role_health.values() 
                              if health.get("success", False))
            total_roles = len(role_health)
            
            overall_status = "healthy" if healthy_roles == total_roles else "degraded"
            if healthy_roles == 0:
                overall_status = "unhealthy"
            
            return {
                "success": True,
                "status": overall_status,
                "tenant_id": tenant_id,
                "healthy_roles": healthy_roles,
                "total_roles": total_roles,
                "role_health": role_health,
                "tenant_info": tenant_info
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get tenant health for {tenant_id}: {e}")
            return {
                "success": False,
                "status": "error",
                "error": str(e),
                "tenant_id": tenant_id
            }
    
    async def disconnect_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """
        Disconnect a tenant from all assigned roles.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Dict containing disconnection results
        """
        try:
            if tenant_id not in self.active_tenants:
                return {
                    "success": False,
                    "error": f"Tenant {tenant_id} not found",
                    "message": "Tenant not established"
                }
            
            disconnected_roles = []
            failed_disconnections = []
            
            # Disconnect from each assigned role
            for role_name in self.role_assignments.get(tenant_id, []):
                try:
                    success = await self.mcp_abstraction.disconnect_from_server(role_name)
                    if success:
                        disconnected_roles.append(role_name)
                    else:
                        failed_disconnections.append(role_name)
                except Exception as e:
                    self.logger.error(f"❌ Error disconnecting {role_name} for tenant {tenant_id}: {e}")
                    failed_disconnections.append(role_name)
            
            # Remove tenant from state
            del self.active_tenants[tenant_id]
            del self.role_assignments[tenant_id]
            
            # Update metrics
            self.business_metrics["active_tenants"] = len(self.active_tenants)
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            return {
                "success": len(disconnected_roles) > 0,
                "tenant_id": tenant_id,
                "disconnected_roles": disconnected_roles,
                "failed_disconnections": failed_disconnections,
                "message": f"Disconnected {len(disconnected_roles)} roles for tenant {tenant_id}"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to disconnect tenant {tenant_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tenant_id": tenant_id
            }
    
    def _get_role_endpoint(self, role_name: str) -> str:
        """Get endpoint for a specific role."""
        role_endpoints = {
            "librarian": "http://localhost:8001",
            "data_steward": "http://localhost:8002",
            "conductor": "http://localhost:8003",
            "post_office": "http://localhost:8004",
            "security_guard": "http://localhost:8005",
            "nurse": "http://localhost:8006",
            "city_manager": "http://localhost:8007",
            "traffic_cop": "http://localhost:8008"
        }
        
        return role_endpoints.get(role_name, f"http://localhost:8000/{role_name}")
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """Get business metrics for MCP operations."""
        return self.business_metrics.copy()
    
    def get_active_tenants(self) -> List[str]:
        """Get list of active tenant IDs."""
        return list(self.active_tenants.keys())
    
    def get_tenant_roles(self, tenant_id: str) -> List[str]:
        """Get roles assigned to a specific tenant."""
        return self.role_assignments.get(tenant_id, [])
    
    def get_composition_health(self) -> Dict[str, Any]:
        """Get MCP composition service health status."""
        return {
            "service_name": "MCPCompositionService",
            "abstraction_health": self.mcp_abstraction.get_abstraction_health(),
            "business_metrics": self.get_business_metrics(),
            "active_tenants": len(self.active_tenants),
            "total_role_assignments": sum(len(roles) for roles in self.role_assignments.values()),
            "status": "healthy"
        }


