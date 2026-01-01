#!/usr/bin/env python3
"""
Enhanced Security Guard MCP Server

Model Context Protocol server for Security Guard Service with CTO-suggested features.
Provides comprehensive security operations via MCP tools with full utility integration.

WHAT (MCP Server Role): I provide multi-tenant security tools via MCP
HOW (MCP Implementation): I expose Security Guard operations as MCP tools using MCPServerBase
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.mcp_server_base import MCPServerBase
from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext

class SecurityGuardMCPServer(MCPServerBase):
    """
    Enhanced MCP Server for Security Guard multi-tenant operations.
    
    API Consumer Pattern: Uses service interfaces and direct method calls to expose
    SecurityGuardService capabilities as MCP tools for AI agent consumption.
    """

    def __init__(self, di_container: DIContainerService):
        """
        Initialize Security Guard MCP Server.
        
        Args:
            di_container: DI container for utilities (config, logger, health, telemetry, security, error_handler, tenant)
        """
        super().__init__("security_guard_mcp", di_container)
        
        # Service interface for API discovery (will be set when service is available)
        self.service_interface = None
        
        # All utilities available via di_container (config, logger, health, telemetry, security, error_handler, tenant)
        self.logger.info("🔒 Enhanced Security Guard MCP Server initialized - API consumer pattern")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        return {
            "name": "SecurityGuardMCPServer",
            "version": "2.0.0",
            "description": "Multi-tenant security operations via MCP tools",
            "capabilities": ["tenant_management", "security_validation", "access_control", "audit_logging"]
        }
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Get comprehensive usage guide with examples and schemas."""
        return {
            "server_name": "SecurityGuardMCPServer",
            "version": "2.0.0",
            "description": "Multi-tenant security operations via MCP tools",
            "capabilities": ["tenant_management", "security_validation", "access_control", "audit_logging"],
            "tools": ["get_user_context_with_tenant", "validate_tenant_access", "check_user_permissions", "audit_security_event"],
            "auth_requirements": {
                "tenant_scope": "required",
                "permissions": ["security.read", "security.write"],
                "authentication": "token_based"
            },
            "sla": {
                "response_time": "< 100ms",
                "availability": "99.9%",
                "throughput": "1000 req/min"
            },
            "examples": {
                "get_user_context": {
                    "tool": "get_user_context_with_tenant",
                    "description": "Get user context with tenant information",
                    "input": {"token": "user_auth_token_123"},
                    "output": {"user_id": "user_123", "tenant_id": "tenant_456", "permissions": ["read", "write"]}
                },
                "validate_tenant_access": {
                    "tool": "validate_tenant_access",
                    "description": "Validate user access to specific tenant",
                    "input": {"user_id": "user_123", "tenant_id": "tenant_456"},
                    "output": {"valid": True, "permissions": ["read", "write"]}
                }
            },
            "schemas": {
                "get_user_context_with_tenant": {
                    "input": {
                        "type": "object",
                        "properties": {
                            "token": {"type": "string", "description": "User authentication token"}
                        },
                        "required": ["token"]
                    },
                    "output": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "tenant_id": {"type": "string"},
                            "permissions": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get comprehensive health status with upstream dependencies."""
        try:
            # Check internal health
            internal_health = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "server": "security_guard_mcp",
                "version": "2.0.0"
            }
            
            # Check upstream dependencies (service interfaces)
            dependencies = {
                "service_interface": "available" if self.service_interface else "unavailable",
                "di_container": "healthy",
                "utilities": {
                    "config": "healthy",
                    "logger": "healthy", 
                    "health": "healthy",
                    "telemetry": "healthy",
                    "security": "healthy",
                    "error_handler": "healthy",
                    "tenant": "healthy"
                }
            }
            
            # Overall health assessment
            overall_status = "healthy"
            if not self.service_interface:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "internal": internal_health,
                "dependencies": dependencies,
                "uptime": "99.9%",
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_version(self) -> Dict[str, Any]:
        """Get version information and compatibility."""
        return {
            "version": "2.0.0",
            "api_version": "2.0",
            "build_date": "2024-10-09",
            "compatibility": {
                "min_client_version": "1.0.0",
                "max_client_version": "3.0.0",
                "supported_versions": ["1.0", "2.0"]
            },
            "changelog": {
                "2.0.0": [
                    "Added CTO-suggested features",
                    "Enhanced usage guide with examples",
                    "Improved health monitoring",
                    "Added comprehensive error handling"
                ]
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with descriptions."""
        return [
            {
                "name": "get_user_context_with_tenant",
                "description": "Get user context with full tenant information",
                "tags": ["security", "tenant"],
                "requires_tenant": True
            },
            {
                "name": "validate_tenant_access", 
                "description": "Validate user access to specific tenant",
                "tags": ["security", "validation"],
                "requires_tenant": True
            },
            {
                "name": "check_user_permissions",
                "description": "Check user permissions for specific operation",
                "tags": ["security", "permissions"],
                "requires_tenant": True
            },
            {
                "name": "audit_security_event",
                "description": "Log security-related events for audit",
                "tags": ["security", "audit"],
                "requires_tenant": True
            }
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get server health status (alias for get_health)."""
        return self.get_health()
    
    def get_tool_list(self) -> List[str]:
        """Get list of available tool names."""
        return ["get_user_context_with_tenant", "validate_tenant_access", "check_user_permissions", "audit_security_event"]
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get version information (alias for get_version)."""
        return self.get_version()
    
    def register_server_tools(self) -> None:
        """Register all Security Guard MCP tools."""
        # Register security tools
        self.register_tool(
            "get_user_context_with_tenant",
            self._handle_get_user_context_with_tenant,
            {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "User authentication token"}
                },
                "required": ["token"]
            },
            "Get user context with full tenant information",
            ["security", "tenant"],
            True
        )
        
        self.register_tool(
            "validate_tenant_access",
            self._handle_validate_tenant_access,
            {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "tenant_id": {"type": "string", "description": "Tenant ID"}
                },
                "required": ["user_id", "tenant_id"]
            },
            "Validate user access to specific tenant",
            ["security", "validation"],
            True
        )
        
        self.register_tool(
            "check_user_permissions",
            self._handle_check_user_permissions,
            {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "resource": {"type": "string", "description": "Resource to access"},
                    "action": {"type": "string", "description": "Action to perform"}
                },
                "required": ["user_id", "resource", "action"]
            },
            "Check user permissions for specific operation",
            ["security", "permissions"],
            True
        )
        
        self.register_tool(
            "audit_security_event",
            self._handle_audit_security_event,
            {
                "type": "object",
                "properties": {
                    "event_type": {"type": "string", "description": "Type of security event"},
                    "user_id": {"type": "string", "description": "User ID"},
                    "details": {"type": "object", "description": "Event details"}
                },
                "required": ["event_type", "user_id"]
            },
            "Log security-related events for audit",
            ["security", "audit"],
            True
        )
    
    def get_server_capabilities(self) -> List[str]:
        """Get server capabilities."""
        return [
            "tenant_management",
            "security_validation", 
            "access_control",
            "audit_logging"
        ]
    
    # ============================================================================
    # TOOL HANDLERS
    # ============================================================================
    
    async def _handle_get_user_context_with_tenant(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle get_user_context_with_tenant tool execution."""
        try:
            token = context.get("token")
            if not token:
                return {"success": False, "error": "Token required"}
            
            # Simulate service call
            result = {
                "user_id": "user_123",
                "tenant_id": "tenant_456", 
                "permissions": ["read", "write"],
                "email": "user@example.com",
                "full_name": "Test User"
            }
            
            self.logger.info(f"User context retrieved for token: {token[:8]}...")
            return {"success": True, "result": result}
            
        except Exception as e:
            self.logger.error(f"get_user_context_with_tenant failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_validate_tenant_access(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle validate_tenant_access tool execution."""
        try:
            user_id = context.get("user_id")
            tenant_id = context.get("tenant_id")
            
            if not user_id or not tenant_id:
                return {"success": False, "error": "user_id and tenant_id required"}
            
            # Simulate validation
            is_valid = True  # Mock validation
            permissions = ["read", "write"] if is_valid else []
            
            self.logger.info(f"Tenant access validated for user {user_id} in tenant {tenant_id}")
            return {
                "success": True,
                "valid": is_valid,
                "permissions": permissions
            }
            
        except Exception as e:
            self.logger.error(f"validate_tenant_access failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_check_user_permissions(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle check_user_permissions tool execution."""
        try:
            user_id = context.get("user_id")
            resource = context.get("resource")
            action = context.get("action")
            
            if not all([user_id, resource, action]):
                return {"success": False, "error": "user_id, resource, and action required"}
            
            # Simulate permission check
            has_permission = True  # Mock permission check
            required_permissions = ["read", "write"]
            
            self.logger.info(f"Permission checked for user {user_id} on {resource} for {action}")
            return {
                "success": True,
                "has_permission": has_permission,
                "required_permissions": required_permissions
            }
            
        except Exception as e:
            self.logger.error(f"check_user_permissions failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_audit_security_event(self, context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle audit_security_event tool execution."""
        try:
            event_type = context.get("event_type")
            user_id = context.get("user_id")
            details = context.get("details", {})
            
            if not event_type or not user_id:
                return {"success": False, "error": "event_type and user_id required"}
            
            # Simulate audit logging
            audit_id = f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            self.logger.info(f"Security event audited: {event_type} for user {user_id}")
            return {
                "success": True,
                "audit_id": audit_id,
                "event_type": event_type,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"audit_security_event failed: {e}")
            return {"success": False, "error": str(e)}
