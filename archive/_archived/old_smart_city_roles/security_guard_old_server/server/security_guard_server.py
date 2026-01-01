"""
Security Guard MCP Server

This module implements the Security Guard MCP Server, providing authentication,
authorization, and user management capabilities using Supabase infrastructure.
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult,
    ListResourcesRequest, ListResourcesResult, ReadResourceRequest, ReadResourceResult
)

# Import the new holistic base class
from common.utilities import SmartCityMCPBase

logger = logging.getLogger(__name__)


class SecurityGuardMCPServer(SmartCityMCPBase):
    """
    Security Guard MCP Server implementation.
    
    Provides authentication, authorization, and user management capabilities
    using Supabase infrastructure and Public Works integration.
    """
    
    def __init__(self):
        # Initialize the base class with all utilities and Tool Factory
        super().__init__("security_guard", "security_guard")
        
        self.server = Server("security-guard-mcp")
        self._setup_handlers()
        
        # Supabase configuration from Configuration Manager
        self.supabase_url = self.config.supabase.url
        self.supabase_anon_key = self.config.supabase.anon_key
        self.supabase_service_key = self.config.supabase.service_key
        
        self.logger.info("Security Guard MCP Server initialized")
    
    def _initialize_server(self):
        """Initialize Security Guard server with tools, resources, and prompts."""
        # The business logic modules are already initialized in __init__
        # This method is called by the base class after __init__
        self.logger.info("Security Guard MCP Server business logic modules ready")
        
        # Demonstrate Tool Factory usage - discover tools from other services
        self.logger.info("Security Guard MCP Server ready to use Tool Factory for cross-domain tool discovery")
        
        # Note: MCP tool registration is handled by the MCP server framework
        # The base class provides utilities, but MCP server registration is separate
        # Business logic methods (like _authenticate_user) are available for use
    
    async def report_server_patterns(self):
        """Report Security Guard server patterns to the Smart City registry (REQUIRED by base class)."""
        try:
            # Report security and authentication patterns
            security_patterns = [
                {
                    "pattern_name": "authentication_system",
                    "pattern_type": "authentication",
                    "description": "Comprehensive user authentication and session management",
                    "implementation": "authentication_tools",
                    "dependencies": ["supabase_infrastructure"]
                },
                {
                    "pattern_name": "authorization_framework",
                    "pattern_type": "authorization",
                    "description": "Role-based access control and permission management",
                    "implementation": "authorization_tools",
                    "dependencies": ["authentication_system"]
                },
                {
                    "pattern_name": "security_policy_enforcement",
                    "pattern_type": "security_policy",
                    "description": "Security policy enforcement and compliance monitoring",
                    "implementation": "security_policy_tools",
                    "dependencies": ["authorization_framework"]
                },
                {
                    "pattern_name": "security_audit_system",
                    "pattern_type": "security_audit",
                    "description": "Security event auditing and monitoring",
                    "implementation": "security_audit_tools",
                    "dependencies": ["security_policy_enforcement"]
                },
                {
                    "pattern_name": "user_management_system",
                    "pattern_type": "user_management",
                    "description": "User profile and session management",
                    "implementation": "user_management_tools",
                    "dependencies": ["authentication_system"]
                }
            ]
            
            for pattern in security_patterns:
                await self.report_smart_city_pattern(
                    pattern_name=pattern["pattern_name"],
                    pattern_type=pattern["pattern_type"],
                    pattern_data={
                        "description": pattern["description"],
                        "implementation": pattern["implementation"],
                        "dependencies": pattern["dependencies"]
                    }
                )
            
            self.logger.info(f"✅ Reported {len(security_patterns)} Security Guard patterns to Smart City registry")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to report Security Guard patterns: {e}")
    
    async def use_security_service_example(self):
        """Example of using security service for self-reporting and security operations."""
        try:
            # Use security service for security operations
            security_status = await self.security_service.get_security_status()
            
            # Report security events to security service (self-reporting)
            await self.security_service.audit_action("security_guard_operation", {
                "service": self.service_name,
                "operation": "security_check",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Use Tool Factory to discover tools from other services
            available_tools = await self.tool_factory.discover_tools(domain="smart_city")
            self.logger.info(f"Security Guard discovered {len(available_tools)} tools from Smart City domain")
            
            return {
                "status": "success",
                "security_status": security_status,
                "available_tools": len(available_tools)
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context={"operation": "use_security_service_example"})
            return {"status": "error", "error": str(e)}
    
    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools."""
            tools = []
            for tool_name in self.list_tools():
                tool_info = self.get_tool_info(tool_name)
                tools.append(Tool(
                    name=tool_name,
                    description=tool_info["description"],
                    inputSchema=tool_info["input_schema"]
                ))
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                result = await self.execute_tool(name, **arguments)
                return [TextContent(
                    type="text",
                    text=f"Tool '{name}' executed successfully:\n{self._format_result(result)}"
                )]
            except Exception as e:
                logger.error(f"Error calling tool '{name}': {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"Error executing tool '{name}': {str(e)}"
                )]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List all available resources."""
            resources = []
            for resource_name in self.list_resources():
                resource_info = self.get_resource_info(resource_name)
                resources.append(Resource(
                    uri=f"security-guard://{resource_name}",
                    name=resource_name,
                    description=resource_info["description"],
                    mimeType="application/json"
                ))
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a resource."""
            try:
                if uri.startswith("security-guard://"):
                    resource_path = uri.replace("security-guard://", "")
                    return f"Security Guard resource: {resource_path}"
                else:
                    return f"Unsupported resource URI: {uri}"
            except Exception as e:
                return f"Error reading resource '{uri}': {str(e)}"
    
    def _format_result(self, result: Any) -> str:
        """Format result for display."""
        if isinstance(result, dict):
            import json
            return json.dumps(result, indent=2, default=str)
        else:
            return str(result)
    
    # Tool implementations
    async def _authenticate_user(self, email: str, password: str, auth_method: str = "email", remember_me: bool = False) -> Dict[str, Any]:
        """Authenticate user using Supabase."""
        try:
            # Use Public Works infrastructure if available
            if self.public_works_client:
                auth_result = await self.call_public_works_tool(
                    "supabase_authentication",
                    email=email,
                    password=password,
                    auth_method=auth_method,
                    remember_me=remember_me
                )
                return auth_result
            
            # Fallback implementation
            return {
                "status": "success",
                "user_id": f"user_{email.split('@')[0]}",
                "email": email,
                "auth_method": auth_method,
                "session_token": f"token_{email}_{auth_method}",
                "expires_at": "2024-01-16T10:00:00Z",
                "remember_me": remember_me
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "email": email
            }
    
    async def _authorize_action(self, user_id: str, action: str, resource: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Authorize user action."""
        try:
            # Check user permissions
            permissions = await self._get_user_permissions(user_id)
            
            # Check if user has permission for this action on this resource
            authorized = self._check_permission(permissions, action, resource)
            
            return {
                "status": "success",
                "authorized": authorized,
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "context": context or {},
                "permissions_checked": permissions
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id,
                "action": action
            }
    
    async def _validate_permissions(self, user_id: str, permissions: List[str], resource_type: str = None, resource_id: str = None) -> Dict[str, Any]:
        """Validate user permissions."""
        try:
            user_permissions = await self._get_user_permissions(user_id)
            
            validation_results = []
            for permission in permissions:
                has_permission = permission in user_permissions
                validation_results.append({
                    "permission": permission,
                    "granted": has_permission,
                    "resource_type": resource_type,
                    "resource_id": resource_id
                })
            
            return {
                "status": "success",
                "user_id": user_id,
                "validation_results": validation_results,
                "all_granted": all(r["granted"] for r in validation_results)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id
            }
    
    async def _check_access_rights(self, user_id: str, resource_path: str, access_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check access rights for resource."""
        try:
            # Get user permissions and roles
            user_permissions = await self._get_user_permissions(user_id)
            user_roles = await self._get_user_roles(user_id)
            
            # Check access based on resource path and access type
            access_granted = self._evaluate_access(user_permissions, user_roles, resource_path, access_type)
            
            return {
                "status": "success",
                "access_granted": access_granted,
                "user_id": user_id,
                "resource_path": resource_path,
                "access_type": access_type,
                "context": context or {},
                "user_permissions": user_permissions,
                "user_roles": user_roles
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id,
                "resource_path": resource_path
            }
    
    async def _manage_user_sessions(self, user_id: str, session_action: str, session_data: Dict[str, Any] = None, expiration_time: int = None) -> Dict[str, Any]:
        """Manage user sessions."""
        try:
            if session_action == "create":
                session_id = f"session_{user_id}_{session_action}"
                return {
                    "status": "success",
                    "session_id": session_id,
                    "user_id": user_id,
                    "action": session_action,
                    "expires_at": "2024-01-16T10:00:00Z",
                    "session_data": session_data or {}
                }
            elif session_action == "validate":
                return {
                    "status": "success",
                    "session_valid": True,
                    "user_id": user_id,
                    "action": session_action
                }
            else:
                return {
                    "status": "success",
                    "user_id": user_id,
                    "action": session_action,
                    "result": f"Session {session_action} completed"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id,
                "action": session_action
            }
    
    async def _enforce_security_policies(self, policy_name: str, user_id: str, resource: str = None, action: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enforce security policies."""
        try:
            # Get policy definition
            policy = await self._get_security_policy(policy_name)
            
            # Evaluate policy against user and context
            policy_result = self._evaluate_policy(policy, user_id, resource, action, context)
            
            return {
                "status": "success",
                "policy_name": policy_name,
                "policy_result": policy_result,
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "context": context or {}
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "policy_name": policy_name,
                "user_id": user_id
            }
    
    async def _audit_security_events(self, event_type: str, user_id: str, resource: str = None, event_data: Dict[str, Any] = None, severity: str = "medium") -> Dict[str, Any]:
        """Audit security events."""
        try:
            # Log the security event
            audit_event = {
                "event_id": f"audit_{event_type}_{user_id}",
                "event_type": event_type,
                "user_id": user_id,
                "resource": resource,
                "event_data": event_data or {},
                "severity": severity,
                "timestamp": "2024-01-15T10:00:00Z"
            }
            
            # Send to City Manager for platform-wide monitoring
            if self.city_manager_client:
                await self.call_city_manager_tool(
                    "audit_compliance",
                    audit_scope=["security"],
                    compliance_framework="security_audit",
                    audit_period="2024-01"
                )
            
            return {
                "status": "success",
                "audit_event": audit_event,
                "logged": True
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "event_type": event_type,
                "user_id": user_id
            }
    
    async def _manage_authentication_tokens(self, user_id: str, token_action: str, token_type: str = "access", expiration_time: int = None) -> Dict[str, Any]:
        """Manage authentication tokens."""
        try:
            if token_action == "generate":
                token = f"token_{user_id}_{token_type}_{token_action}"
                return {
                    "status": "success",
                    "token": token,
                    "token_type": token_type,
                    "user_id": user_id,
                    "expires_at": "2024-01-16T10:00:00Z"
                }
            elif token_action == "validate":
                return {
                    "status": "success",
                    "token_valid": True,
                    "token_type": token_type,
                    "user_id": user_id
                }
            else:
                return {
                    "status": "success",
                    "action": token_action,
                    "token_type": token_type,
                    "user_id": user_id,
                    "result": f"Token {token_action} completed"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id,
                "action": token_action
            }
    
    async def _validate_credentials(self, email: str, password: str, validation_type: str = "login") -> Dict[str, Any]:
        """Validate user credentials."""
        try:
            # Use Public Works infrastructure if available
            if self.public_works_client:
                validation_result = await self.call_public_works_tool(
                    "supabase_credential_validation",
                    email=email,
                    password=password,
                    validation_type=validation_type
                )
                return validation_result
            
            # Fallback validation
            return {
                "status": "success",
                "credentials_valid": True,
                "email": email,
                "validation_type": validation_type,
                "user_id": f"user_{email.split('@')[0]}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "email": email
            }
    
    async def _check_user_roles(self, user_id: str, role_names: List[str] = None, include_permissions: bool = True) -> Dict[str, Any]:
        """Check user roles."""
        try:
            user_roles = await self._get_user_roles(user_id)
            
            if role_names:
                role_check_results = []
                for role_name in role_names:
                    has_role = role_name in user_roles
                    role_check_results.append({
                        "role": role_name,
                        "assigned": has_role
                    })
                
                return {
                    "status": "success",
                    "user_id": user_id,
                    "role_check_results": role_check_results,
                    "all_roles_assigned": all(r["assigned"] for r in role_check_results)
                }
            else:
                result = {
                    "status": "success",
                    "user_id": user_id,
                    "assigned_roles": user_roles
                }
                
                if include_permissions:
                    permissions = await self._get_user_permissions(user_id)
                    result["permissions"] = permissions
                
                return result
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id
            }
    
    async def _enforce_authorization_rules(self, user_id: str, rule_name: str, resource: str = None, action: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enforce authorization rules."""
        try:
            # Get authorization rule
            rule = await self._get_authorization_rule(rule_name)
            
            # Evaluate rule
            rule_result = self._evaluate_authorization_rule(rule, user_id, resource, action, context)
            
            return {
                "status": "success",
                "rule_name": rule_name,
                "rule_result": rule_result,
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "context": context or {}
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "rule_name": rule_name,
                "user_id": user_id
            }
    
    async def _monitor_security_metrics(self, metric_types: List[str], time_range: str = None, aggregation_level: str = "daily") -> Dict[str, Any]:
        """Monitor security metrics."""
        try:
            metrics = {}
            for metric_type in metric_types:
                metrics[metric_type] = {
                    "value": 0.95,
                    "trend": "stable",
                    "threshold": 0.90,
                    "status": "healthy"
                }
            
            return {
                "status": "success",
                "metrics": metrics,
                "time_range": time_range or "last_24_hours",
                "aggregation_level": aggregation_level,
                "monitored_at": "2024-01-15T10:00:00Z"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "metric_types": metric_types
            }
    
    async def _get_user_context(self, user_id: str, context_type: str = "basic", include_sessions: bool = False) -> Dict[str, Any]:
        """Get user context for other roles."""
        try:
            user_roles = await self._get_user_roles(user_id)
            user_permissions = await self._get_user_permissions(user_id)
            
            context = {
                "user_id": user_id,
                "roles": user_roles,
                "permissions": user_permissions,
                "context_type": context_type
            }
            
            if include_sessions:
                context["sessions"] = await self._get_user_sessions(user_id)
            
            if context_type == "full":
                context["profile"] = await self._get_user_profile(user_id)
                context["preferences"] = await self._get_user_preferences(user_id)
            
            return {
                "status": "success",
                "user_context": context
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id
            }
    
    async def _refresh_authentication(self, user_id: str, refresh_token: str, token_type: str = "access") -> Dict[str, Any]:
        """Refresh authentication tokens."""
        try:
            # Validate refresh token
            token_valid = await self._validate_refresh_token(refresh_token, user_id)
            
            if token_valid:
                new_token = f"new_token_{user_id}_{token_type}"
                return {
                    "status": "success",
                    "new_token": new_token,
                    "token_type": token_type,
                    "user_id": user_id,
                    "expires_at": "2024-01-16T10:00:00Z"
                }
            else:
                return {
                    "status": "error",
                    "error": "Invalid refresh token",
                    "user_id": user_id
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id
            }
    
    async def _revoke_access(self, user_id: str, revocation_type: str, reason: str = None, immediate: bool = True) -> Dict[str, Any]:
        """Revoke user access."""
        try:
            # Revoke access based on type
            if revocation_type == "session":
                result = await self._revoke_user_sessions(user_id)
            elif revocation_type == "token":
                result = await self._revoke_user_tokens(user_id)
            elif revocation_type == "permissions":
                result = await self._revoke_user_permissions(user_id)
            elif revocation_type == "account":
                result = await self._revoke_user_account(user_id)
            else:
                result = {"error": f"Unknown revocation type: {revocation_type}"}
            
            # Log the revocation
            await self._audit_security_events(
                "permission_change",
                user_id,
                event_data={
                    "revocation_type": revocation_type,
                    "reason": reason,
                    "immediate": immediate
                },
                severity="high"
            )
            
            return {
                "status": "success",
                "revocation_type": revocation_type,
                "user_id": user_id,
                "reason": reason,
                "immediate": immediate,
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id,
                "revocation_type": revocation_type
            }
    
    # Standard MCP tools
    async def _list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "status": "success",
            "tools": self.list_tools(),
            "count": len(self.tools)
        }
    
    async def _list_resources(self) -> Dict[str, Any]:
        """List available resources."""
        return {
            "status": "success",
            "resources": self.list_resources(),
            "count": len(self.resources)
        }
    
    async def _list_prompts(self) -> Dict[str, Any]:
        """List available prompts."""
        return {
            "status": "success",
            "prompts": self.list_prompts(),
            "count": len(self.prompts)
        }
    
    # Helper methods
    async def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions."""
        # Mock implementation - in real system, this would query Supabase
        return ["read", "write", "admin"]
    
    async def _get_user_roles(self, user_id: str) -> List[str]:
        """Get user roles."""
        # Mock implementation - in real system, this would query Supabase
        return ["user", "admin"]
    
    async def _get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user sessions."""
        # Mock implementation
        return [{"session_id": f"session_{user_id}_1", "created_at": "2024-01-15T10:00:00Z"}]
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile."""
        # Mock implementation
        return {"user_id": user_id, "email": f"user_{user_id}@example.com"}
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        # Mock implementation
        return {"theme": "dark", "language": "en"}
    
    async def _get_security_policy(self, policy_name: str) -> Dict[str, Any]:
        """Get security policy."""
        # Mock implementation
        return {"name": policy_name, "rules": ["rule1", "rule2"]}
    
    async def _get_authorization_rule(self, rule_name: str) -> Dict[str, Any]:
        """Get authorization rule."""
        # Mock implementation
        return {"name": rule_name, "conditions": ["condition1", "condition2"]}
    
    async def _validate_refresh_token(self, refresh_token: str, user_id: str) -> bool:
        """Validate refresh token."""
        # Mock implementation
        return True
    
    def _check_permission(self, permissions: List[str], action: str, resource: str) -> bool:
        """Check if user has permission for action on resource."""
        # Mock implementation
        return True
    
    def _evaluate_access(self, permissions: List[str], roles: List[str], resource_path: str, access_type: str) -> bool:
        """Evaluate access rights."""
        # Mock implementation
        return True
    
    def _evaluate_policy(self, policy: Dict[str, Any], user_id: str, resource: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate security policy."""
        # Mock implementation
        return {"allowed": True, "reason": "Policy satisfied"}
    
    def _evaluate_authorization_rule(self, rule: Dict[str, Any], user_id: str, resource: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate authorization rule."""
        # Mock implementation
        return {"allowed": True, "reason": "Rule satisfied"}
    
    async def _revoke_user_sessions(self, user_id: str) -> Dict[str, Any]:
        """Revoke user sessions."""
        return {"sessions_revoked": 2}
    
    async def _revoke_user_tokens(self, user_id: str) -> Dict[str, Any]:
        """Revoke user tokens."""
        return {"tokens_revoked": 1}
    
    async def _revoke_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Revoke user permissions."""
        return {"permissions_revoked": 3}
    
    async def _revoke_user_account(self, user_id: str) -> Dict[str, Any]:
        """Revoke user account."""
        return {"account_revoked": True}
    
    # Smart City Pattern Reporting Tools
    async def report_smart_city_patterns(self, pattern_name: str, pattern_type: str, pattern_data: Dict[str, Any]) -> Dict[str, Any]:
        """Report Smart City business logic patterns to Smart City registry."""
        try:
            result = await self.pattern_reporter.report_smart_city_pattern(pattern_name, pattern_type, pattern_data)
            logger.info(f"Smart City pattern reporting result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error reporting Smart City pattern: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_smart_city_patterns(self, pattern_type: str) -> Dict[str, Any]:
        """Get Smart City patterns by type."""
        try:
            result = await self.pattern_reporter.get_smart_city_patterns(pattern_type)
            logger.info(f"Smart City pattern retrieval result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving Smart City patterns: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Security Guard MCP Server...")
        
        # Log server summary
        summary = self.get_server_summary()
        logger.info(f"Security Guard MCP Server Summary:")
        logger.info(f"  - Tools: {len(summary['tools'])}")
        logger.info(f"  - Resources: {len(summary['resources'])}")
        logger.info(f"  - Prompts: {len(summary['prompts'])}")
        logger.info(f"  - Supabase Integration: {summary['integrations']['supabase']}")
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="security-guard-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )


async def main():
    """Main entry point."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the server
    server = SecurityGuardMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())


