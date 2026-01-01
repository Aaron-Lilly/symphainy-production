#!/usr/bin/env python3
"""
SOA/MCP Module - Security Guard Service

Handles SOA API exposure and MCP tool integration.
"""

from typing import Dict, Any


class SoaMcp:
    """SOA/MCP module for Security Guard Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for realm consumption."""
        self.service.soa_apis = {
            "authenticate_user": {
                "endpoint": "/api/v1/security/authenticate",
                "method": "POST",
                "description": "Authenticate user and create session"
            },
            "authorize_action": {
                "endpoint": "/api/v1/security/authorize",
                "method": "POST",
                "description": "Authorize user action on resource"
            },
            "orchestrate_security_communication": {
                "endpoint": "/api/v1/security/communication",
                "method": "POST",
                "description": "Orchestrate security-validated communication"
            },
            "orchestrate_zero_trust_policy": {
                "endpoint": "/api/v1/security/zero-trust",
                "method": "POST",
                "description": "Orchestrate zero-trust policy enforcement"
            },
            "orchestrate_tenant_isolation": {
                "endpoint": "/api/v1/security/tenant-isolation",
                "method": "POST",
                "description": "Orchestrate tenant isolation enforcement"
            }
        }
    
    async def initialize_mcp_server_integration(self):
        """Initialize MCP server integration for agent access."""
        self.service.mcp_tools = {
            "authenticate_user": {
                "name": "authenticate_user",
                "description": "Authenticate a user and create a session"
            },
            "authorize_action": {
                "name": "authorize_action",
                "description": "Authorize a user action on a specific resource"
            },
            "validate_session": {
                "name": "validate_session",
                "description": "Validate a user session"
            },
            "enforce_zero_trust": {
                "name": "enforce_zero_trust",
                "description": "Enforce zero-trust policy for resource access"
            }
        }
        
        # Enable MCP server
        self.service.mcp_server_enabled = True
    
    async def _mcp_authenticate_user(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for authenticate_user tool."""
        try:
            authentication = self.service.get_module("authentication")
            request = {
                "username": arguments.get("username"),
                "password": arguments.get("password"),
                "authentication_method": arguments.get("authentication_method", "password")
            }
            
            response = await authentication.authenticate_user(request)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Authentication {'successful' if response['success'] else 'failed'}: {response['message']}"
                    }
                ],
                "isError": not response["success"]
            }
            
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Authentication error: {str(e)}"}],
                "isError": True
            }
    
    async def _mcp_authorize_action(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for authorize_action tool."""
        try:
            authentication = self.service.get_module("authentication")
            request = {
                "user_id": arguments.get("user_id"),
                "action": arguments.get("action"),
                "resource_id": arguments.get("resource_id"),
                "resource_type": arguments.get("resource_type"),
                "context": arguments.get("context", {})
            }
            
            response = await authentication.authorize_action(request)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Authorization {'granted' if response['authorized'] else 'denied'}: {response['message']}"
                    }
                ],
                "isError": not response["success"]
            }
            
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Authorization error: {str(e)}"}],
                "isError": True
            }
    
    async def _mcp_validate_session(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for validate_session tool."""
        try:
            session_id = arguments.get("session_id")
            session = self.service.active_sessions.get(session_id)
            
            if session and session.get("status") == "active":
                return {
                    "content": [{"type": "text", "text": f"Session {session_id} is valid and active"}],
                    "isError": False
                }
            else:
                return {
                    "content": [{"type": "text", "text": f"Session {session_id} is invalid or expired"}],
                    "isError": True
                }
                
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Session validation error: {str(e)}"}],
                "isError": True
            }
    
    async def _mcp_enforce_zero_trust(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for enforce_zero_trust tool."""
        try:
            orchestration = self.service.get_module("orchestration")
            request = {
                "resource_id": arguments.get("resource_id"),
                "user_id": arguments.get("user_id"),
                "action": arguments.get("action"),
                "policy_rules": arguments.get("policy_rules", []),
                "tenant_id": arguments.get("tenant_id")
            }
            
            response = await orchestration.orchestrate_zero_trust_policy(request)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Zero-trust policy {'granted' if response['access_granted'] else 'denied'} access to {response['resource_id']}"
                    }
                ],
                "isError": not response.get("access_granted", False)
            }
            
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Zero-trust enforcement error: {str(e)}"}],
                "isError": True
            }
    
    async def register_capabilities(self) -> Dict[str, Any]:
        """Register Security Guard capabilities with Curator using Phase 2 pattern (simplified for Smart City)."""
        try:
            # Build capabilities list with SOA API and MCP Tool contracts
            capabilities = []
            
            # Create authentication capability (combines authenticate_user SOA API + MCP tool)
            capabilities.append({
                "name": "authentication",
                "protocol": "SecurityGuardServiceProtocol",
                "description": "User authentication and session management",
                "contracts": {
                    "soa_api": {
                        "api_name": "authenticate_user",
                        "endpoint": self.service.soa_apis.get("authenticate_user", {}).get("endpoint", "/soa/security/authenticate_user"),
                        "method": self.service.soa_apis.get("authenticate_user", {}).get("method", "POST"),
                        "handler": getattr(self.service, "authenticate_user", None),
                        "metadata": {
                            "description": "Authenticate user and create session"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "security_guard_authenticate_user",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "security_guard_authenticate_user",
                            "description": "Authenticate a user and create a session",
                            "input_schema": {}
                        }
                    }
                }
            })
            
            # Create authorization capability
            capabilities.append({
                "name": "authorization",
                "protocol": "SecurityGuardServiceProtocol",
                "description": "User authorization and access control",
                "contracts": {
                    "soa_api": {
                        "api_name": "authorize_action",
                        "endpoint": self.service.soa_apis.get("authorize_action", {}).get("endpoint", "/soa/security/authorize_action"),
                        "method": self.service.soa_apis.get("authorize_action", {}).get("method", "POST"),
                        "handler": getattr(self.service, "authorize_action", None),
                        "metadata": {
                            "description": "Authorize user action on resource"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "security_guard_authorize_action",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "security_guard_authorize_action",
                            "description": "Authorize a user action on a specific resource",
                            "input_schema": {}
                        }
                    }
                }
            })
            
            # Create zero-trust capability
            capabilities.append({
                "name": "zero_trust_policy",
                "protocol": "SecurityGuardServiceProtocol",
                "description": "Zero-trust policy enforcement",
                "contracts": {
                    "soa_api": {
                        "api_name": "orchestrate_zero_trust_policy",
                        "endpoint": self.service.soa_apis.get("orchestrate_zero_trust_policy", {}).get("endpoint", "/soa/security/zero_trust"),
                        "method": self.service.soa_apis.get("orchestrate_zero_trust_policy", {}).get("method", "POST"),
                        "handler": getattr(self.service, "orchestrate_zero_trust_policy", None),
                        "metadata": {
                            "description": "Orchestrate zero-trust policy enforcement"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "security_guard_enforce_zero_trust",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "security_guard_enforce_zero_trust",
                            "description": "Enforce zero-trust policy for resource access",
                            "input_schema": {}
                        }
                    }
                }
            })
            
            # Register using register_with_curator (simplified Phase 2 pattern)
            soa_api_names = list(self.service.soa_apis.keys())
            mcp_tool_names = [f"security_guard_{tool}" for tool in self.service.mcp_tools.keys()]
            
            success = await self.service.register_with_curator(
                capabilities=capabilities,
                soa_apis=soa_api_names,
                mcp_tools=mcp_tool_names,
                protocols=[{
                    "name": "SecurityGuardServiceProtocol",
                    "definition": {
                        "methods": {
                            "authenticate_user": {"input_schema": {}, "output_schema": {}},
                            "authorize_action": {"input_schema": {}, "output_schema": {}},
                            "orchestrate_zero_trust_policy": {"input_schema": {}, "output_schema": {}}
                        }
                    }
                }]
            )
            
            if success:
                if hasattr(self.service, '_log'):
                    self.service._log("info", f"✅ Security Guard registered with Curator (Phase 2 pattern - Smart City): {len(capabilities)} capabilities")
            else:
                if hasattr(self.service, '_log'):
                    self.service._log("warning", "⚠️ Failed to register Security Guard with Curator")
                    
        except Exception as e:
            if hasattr(self.service, '_log'):
                self.service._log("error", f"❌ Failed to register Security Guard capabilities: {e}")
                import traceback
                self.service._log("error", f"Traceback: {traceback.format_exc()}")
        
        return {}







