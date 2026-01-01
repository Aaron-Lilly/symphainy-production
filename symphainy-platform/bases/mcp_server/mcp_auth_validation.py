#!/usr/bin/env python3
"""
MCP Auth Validation

Handles authentication and tenant validation for MCP servers.

WHAT (Micro-Module Role): I provide authentication and tenant validation for MCP servers
HOW (Micro-Module Implementation): I validate tokens and tenant access using platform utilities
"""

from typing import Dict, Any
from fastapi import Request

from .mcp_tool_definition import MCPToolDefinition


class MCPAuthValidation:
    """
    Authentication and tenant validation for MCP servers.
    
    Handles token validation and tenant access control using platform utilities.
    """
    
    def __init__(self, utilities):
        """Initialize auth validation."""
        self.utilities = utilities
        self.logger = utilities.logger
    
    async def validate_auth_and_tenant(self, request: Request, payload: Dict[str, Any], 
                                     tool_def: MCPToolDefinition) -> Dict[str, Any]:
        """Validate authentication and tenant using our security utility."""
        try:
            # Get authorization header
            auth_header = request.headers.get("authorization")
            if not auth_header:
                return {"valid": False, "error": "Authorization header required"}
            
            # Validate token (via our security utility)
            token_result = self.utilities.security.validate_token(auth_header)
            if not token_result["valid"]:
                return {"valid": False, "error": "Invalid token"}
            
            # Check tenant if required
            if tool_def.requires_tenant:
                tenant_id = payload.get("tenant_id")
                if not tenant_id:
                    return {"valid": False, "error": "tenant_id required"}
                
                # Validate tenant access (via our tenant utility)
                tenant_result = self.utilities.tenant.validate_tenant_access(token_result["user_id"], tenant_id)
                if not tenant_result["valid"]:
                    return {"valid": False, "error": "Invalid tenant access"}
            
            return {"valid": True, "user_context": token_result}
            
        except Exception as e:
            self.logger.error(f"Auth validation failed: {e}")
            return {"valid": False, "error": "Authentication validation failed"}
    
    def validate_token(self, auth_header: str) -> Dict[str, Any]:
        """Validate authentication token."""
        try:
            return self.utilities.security.validate_token(auth_header)
        except Exception as e:
            self.logger.error(f"Token validation failed: {e}")
            return {"valid": False, "error": "Token validation failed"}
    
    def validate_tenant_access(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Validate tenant access for user."""
        try:
            return self.utilities.tenant.validate_tenant_access(user_id, tenant_id)
        except Exception as e:
            self.logger.error(f"Tenant validation failed: {e}")
            return {"valid": False, "error": "Tenant validation failed"}
    
    def extract_user_context(self, request: Request) -> Dict[str, Any]:
        """Extract user context from request."""
        try:
            auth_header = request.headers.get("authorization")
            if not auth_header:
                return {"valid": False, "error": "No authorization header"}
            
            token_result = self.validate_token(auth_header)
            if not token_result["valid"]:
                return token_result
            
            return {
                "valid": True,
                "user_id": token_result.get("user_id"),
                "tenant_id": token_result.get("tenant_id"),
                "scopes": token_result.get("scopes", [])
            }
            
        except Exception as e:
            self.logger.error(f"User context extraction failed: {e}")
            return {"valid": False, "error": "User context extraction failed"}




























