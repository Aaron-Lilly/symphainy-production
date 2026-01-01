#!/usr/bin/env python3
"""
Security Guard Service - Infrastructure-Connected Clean Rebuild

Updated clean rebuild that properly uses infrastructure abstractions:
- Authentication via Supabase + JWT
- Session management via Redis
- Tenant management via Redis
- Policy management via Supabase
- Proper infrastructure mapping validation

WHAT (Smart City Role): I provide platform security with proper infrastructure integration
HOW (Service Implementation): I use SmartCityRoleBase with infrastructure abstractions
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# Import ONLY our new base and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.security_guard_service_protocol import SecurityGuardServiceProtocol


class SecurityGuardService(SmartCityRoleBase, SecurityGuardServiceProtocol):
    """
    Security Guard Service - Infrastructure-Connected Clean Rebuild
    
    Clean implementation using ONLY our new base and protocol construct
    with proper infrastructure abstractions for authentication, session management,
    tenant management, and policy enforcement.
    
    WHAT (Smart City Role): I provide platform security with proper infrastructure integration
    HOW (Service Implementation): I use SmartCityRoleBase with infrastructure abstractions
    """
    
    def __init__(self, di_container: Any):
        """Initialize Security Guard Service with infrastructure integration."""
        super().__init__(
            service_name="SecurityGuardService",
            role_name="security_guard",
            di_container=di_container
        )
        
        # Infrastructure Abstractions (will be initialized in initialize())
        self.auth_abstraction = None
        self.authorization_abstraction = None
        self.session_management_abstraction = None
        self.tenant_abstraction = None
        self.policy_abstraction = None
        
        # Service State
        self.is_infrastructure_connected = False
        
        # Week 3 Enhancement: SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        self.mcp_server_enabled = False
        
        # Logger is initialized by SmartCityRoleBase
        if self.logger:
            self.logger.info("✅ Security Guard Service (Infrastructure-Connected Clean Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Security Guard Service with infrastructure connections."""
        try:
            if self.logger:
                self.logger.info("🚀 Initializing Security Guard Service with infrastructure connections...")
            
            # Initialize infrastructure abstractions
            await self._initialize_infrastructure_connections()
            
            # Initialize SOA API exposure
            await self._initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self._initialize_mcp_tool_integration()
            
            # Register capabilities with curator
            capabilities = await self._register_security_guard_capabilities()
            await self.register_capability("SecurityGuardService", capabilities)
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            if self.logger:
                self.logger.info("✅ Security Guard Service (Infrastructure-Connected) initialized successfully")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to initialize Security Guard Service: {str(e)}")
            self.service_health = "unhealthy"
            return False
    
    async def _initialize_infrastructure_connections(self):
        """Initialize connections to infrastructure abstractions."""
        try:
            if self.logger:
                self.logger.info("🔌 Connecting to security infrastructure abstractions...")
            
            # Get Public Works Foundation
            public_works_foundation = self.get_public_works_foundation()
            if not public_works_foundation:
                raise Exception("Public Works Foundation not available")
            
            # Get Authentication Abstraction (Supabase + JWT)
            self.auth_abstraction = await public_works_foundation.get_abstraction("auth")
            if not self.auth_abstraction:
                raise Exception("Authentication Abstraction not available")
            
            # Get Authorization Abstraction (Supabase)
            self.authorization_abstraction = await public_works_foundation.get_abstraction("authorization")
            if not self.authorization_abstraction:
                raise Exception("Authorization Abstraction not available")
            
            # Get Session Management Abstraction (Redis)
            self.session_management_abstraction = await public_works_foundation.get_abstraction("session_management")
            if not self.session_management_abstraction:
                raise Exception("Session Management Abstraction not available")
            
            # Get Tenant Abstraction (Redis)
            self.tenant_abstraction = await public_works_foundation.get_abstraction("tenant")
            if not self.tenant_abstraction:
                raise Exception("Tenant Abstraction not available")
            
            # Get Policy Abstraction (Supabase)
            self.policy_abstraction = await public_works_foundation.get_abstraction("policy")
            if not self.policy_abstraction:
                raise Exception("Policy Abstraction not available")
            
            self.is_infrastructure_connected = True
            
            if self.logger:
                self.logger.info("✅ Security infrastructure connections established:")
                self.logger.info("  - Authentication (Supabase + JWT): ✅")
                self.logger.info("  - Authorization (Supabase): ✅")
                self.logger.info("  - Session Management (Redis): ✅")
                self.logger.info("  - Tenant Management (Redis): ✅")
                self.logger.info("  - Policy Management (Supabase): ✅")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to connect to security infrastructure: {str(e)}")
            raise e
    
    async def _initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Smart City capabilities."""
        self.soa_apis = {
            "authenticate_user": {
                "endpoint": "/api/security/authenticate",
                "method": "POST",
                "description": "Authenticate user with credentials",
                "parameters": ["credentials"]
            },
            "authorize_action": {
                "endpoint": "/api/security/authorize",
                "method": "POST",
                "description": "Authorize user action",
                "parameters": ["user_id", "action", "resource"]
            },
            "validate_session": {
                "endpoint": "/api/security/validate-session",
                "method": "POST",
                "description": "Validate user session",
                "parameters": ["session_id"]
            },
            "get_tenant_context": {
                "endpoint": "/api/security/tenant/{tenant_id}",
                "method": "GET",
                "description": "Get tenant security context",
                "parameters": ["tenant_id"]
            },
            "enforce_policy": {
                "endpoint": "/api/security/enforce-policy",
                "method": "POST",
                "description": "Enforce security policy",
                "parameters": ["policy_id", "context"]
            }
        }
    
    async def _initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for security operations."""
        self.mcp_tools = {
            "user_authenticator": {
                "name": "user_authenticator",
                "description": "Authenticate users and manage sessions",
                "parameters": ["credentials", "session_options"]
            },
            "access_controller": {
                "name": "access_controller",
                "description": "Control access to resources and actions",
                "parameters": ["user_id", "action", "resource", "context"]
            },
            "session_manager": {
                "name": "session_manager",
                "description": "Manage user sessions and security contexts",
                "parameters": ["session_id", "session_data", "action"]
            },
            "tenant_security": {
                "name": "tenant_security",
                "description": "Manage tenant security contexts and isolation",
                "parameters": ["tenant_id", "security_config", "action"]
            }
        }
    
    async def _register_security_guard_capabilities(self) -> Dict[str, Any]:
        """Register Security Guard Service capabilities."""
        return {
            "service_name": "SecurityGuardService",
            "service_type": "security_enforcement",
            "realm": "smart_city",
            "capabilities": [
                "user_authentication",
                "access_authorization",
                "session_management",
                "tenant_isolation",
                "policy_enforcement",
                "zero_trust_security",
                "infrastructure_integration"
            ],
            "infrastructure_connections": {
                "authentication": "Supabase + JWT",
                "authorization": "Supabase",
                "session_management": "Redis",
                "tenant_management": "Redis",
                "policy_management": "Supabase"
            },
            "soa_apis": self.soa_apis,
            "mcp_tools": self.mcp_tools,
            "status": "active",
            "infrastructure_connected": self.is_infrastructure_connected,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # AUTHENTICATION METHODS WITH INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def authenticate_user(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user using Supabase + JWT infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Authentication Abstraction (Supabase + JWT)
            security_context = await self.auth_abstraction.authenticate_user(credentials)
            
            if security_context and security_context.is_authenticated:
                if self.logger:
                    self.logger.info(f"✅ User authenticated: {security_context.user_id}")
                
                return {
                    "user_id": security_context.user_id,
                    "tenant_id": security_context.tenant_id,
                    "session_id": security_context.session_id,
                    "permissions": security_context.permissions,
                    "authenticated": True,
                    "expires_at": security_context.expires_at,
                    "status": "success"
                }
            else:
                return {
                    "user_id": None,
                    "authenticated": False,
                    "error": "Invalid credentials",
                    "status": "error"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error authenticating user: {str(e)}")
            return {
                "user_id": None,
                "authenticated": False,
                "error": str(e),
                "status": "error"
            }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh authentication token using JWT infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Authentication Abstraction (JWT)
            new_context = await self.auth_abstraction.refresh_token(refresh_token)
            
            if new_context and new_context.is_authenticated:
                if self.logger:
                    self.logger.info(f"✅ Token refreshed for user: {new_context.user_id}")
                
                return {
                    "user_id": new_context.user_id,
                    "tenant_id": new_context.tenant_id,
                    "session_id": new_context.session_id,
                    "permissions": new_context.permissions,
                    "authenticated": True,
                    "expires_at": new_context.expires_at,
                    "status": "success"
                }
            else:
                return {
                    "user_id": None,
                    "authenticated": False,
                    "error": "Invalid refresh token",
                    "status": "error"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error refreshing token: {str(e)}")
            return {
                "user_id": None,
                "authenticated": False,
                "error": str(e),
                "status": "error"
            }
    
    # ============================================================================
    # AUTHORIZATION METHODS WITH INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def authorize_action(self, user_id: str, action: str, resource: str, context: Dict[str, Any] = None) -> bool:
        """Authorize user action using Supabase infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Authorization Abstraction (Supabase)
            is_authorized = await self.authorization_abstraction.authorize_action(
                user_id=user_id,
                action=action,
                resource=resource,
                context=context or {}
            )
            
            if self.logger:
                self.logger.info(f"✅ Authorization check: {user_id} -> {action} on {resource}: {'✅' if is_authorized else '❌'}")
            
            return is_authorized
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error authorizing action: {str(e)}")
            return False
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions using Supabase infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Authorization Abstraction (Supabase)
            permissions = await self.authorization_abstraction.get_user_permissions(user_id)
            
            if self.logger:
                self.logger.info(f"✅ Retrieved {len(permissions)} permissions for user: {user_id}")
            
            return permissions
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting user permissions: {str(e)}")
            return []
    
    # ============================================================================
    # SESSION MANAGEMENT METHODS WITH INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate session using Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Session Management Abstraction (Redis)
            session_context = await self.session_management_abstraction.validate_session(session_id)
            
            if session_context and session_context.is_valid:
                if self.logger:
                    self.logger.info(f"✅ Session validated: {session_id}")
                
                return {
                    "session_id": session_id,
                    "user_id": session_context.user_id,
                    "tenant_id": session_context.tenant_id,
                    "is_valid": True,
                    "expires_at": session_context.expires_at,
                    "status": "success"
                }
            else:
                return {
                    "session_id": session_id,
                    "is_valid": False,
                    "error": "Invalid or expired session",
                    "status": "error"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error validating session: {str(e)}")
            return {
                "session_id": session_id,
                "is_valid": False,
                "error": str(e),
                "status": "error"
            }
    
    async def create_session(self, user_id: str, tenant_id: str, session_data: Dict[str, Any] = None) -> str:
        """Create session using Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Session Management Abstraction (Redis)
            session_id = await self.session_management_abstraction.create_session(
                user_id=user_id,
                tenant_id=tenant_id,
                session_data=session_data or {}
            )
            
            if session_id:
                if self.logger:
                    self.logger.info(f"✅ Session created: {session_id} for user: {user_id}")
                return session_id
            else:
                raise Exception("Failed to create session")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error creating session: {str(e)}")
            raise e
    
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate session using Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Session Management Abstraction (Redis)
            success = await self.session_management_abstraction.terminate_session(session_id)
            
            if success:
                if self.logger:
                    self.logger.info(f"✅ Session terminated: {session_id}")
                return True
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ Session not found or already terminated: {session_id}")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error terminating session: {str(e)}")
            return False
    
    # ============================================================================
    # TENANT MANAGEMENT METHODS WITH INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def get_tenant_context(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant context using Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Tenant Abstraction (Redis)
            tenant_context = await self.tenant_abstraction.get_tenant_context(tenant_id)
            
            if tenant_context:
                if self.logger:
                    self.logger.info(f"✅ Tenant context retrieved: {tenant_id}")
                
                return {
                    "tenant_id": tenant_id,
                    "tenant_name": tenant_context.tenant_name,
                    "security_config": tenant_context.security_config,
                    "isolation_level": tenant_context.isolation_level,
                    "status": "success"
                }
            else:
                return {
                    "tenant_id": tenant_id,
                    "error": "Tenant not found",
                    "status": "error"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting tenant context: {str(e)}")
            return {
                "tenant_id": tenant_id,
                "error": str(e),
                "status": "error"
            }
    
    async def validate_tenant_access(self, user_id: str, tenant_id: str) -> bool:
        """Validate tenant access using Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Tenant Abstraction (Redis)
            has_access = await self.tenant_abstraction.validate_tenant_access(user_id, tenant_id)
            
            if self.logger:
                self.logger.info(f"✅ Tenant access validation: {user_id} -> {tenant_id}: {'✅' if has_access else '❌'}")
            
            return has_access
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error validating tenant access: {str(e)}")
            return False
    
    # ============================================================================
    # POLICY ENFORCEMENT METHODS WITH INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def enforce_policy(self, policy_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce security policy using Supabase infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Policy Abstraction (Supabase)
            enforcement_result = await self.policy_abstraction.enforce_policy(policy_id, context)
            
            if enforcement_result.get("enforced", False):
                if self.logger:
                    self.logger.info(f"✅ Policy enforced: {policy_id}")
                
                return {
                    "policy_id": policy_id,
                    "enforced": True,
                    "result": enforcement_result.get("result"),
                    "status": "success"
                }
            else:
                return {
                    "policy_id": policy_id,
                    "enforced": False,
                    "error": enforcement_result.get("error", "Policy enforcement failed"),
                    "status": "error"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error enforcing policy: {str(e)}")
            return {
                "policy_id": policy_id,
                "enforced": False,
                "error": str(e),
                "status": "error"
            }
    
    # ============================================================================
    # INFRASTRUCTURE VALIDATION METHODS
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that security infrastructure mapping is working correctly."""
        try:
            validation_results = {
                "authentication_supabase_jwt": False,
                "authorization_supabase": False,
                "session_management_redis": False,
                "tenant_management_redis": False,
                "policy_management_supabase": False,
                "overall_status": False
            }
            
            # Test Authentication (Supabase + JWT)
            try:
                if self.auth_abstraction:
                    # Test basic auth operation
                    test_result = await self.auth_abstraction.health_check()
                    validation_results["authentication_supabase_jwt"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Authentication (Supabase + JWT) test failed: {str(e)}")
            
            # Test Authorization (Supabase)
            try:
                if self.authorization_abstraction:
                    # Test basic authorization operation
                    test_result = await self.authorization_abstraction.health_check()
                    validation_results["authorization_supabase"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Authorization (Supabase) test failed: {str(e)}")
            
            # Test Session Management (Redis)
            try:
                if self.session_management_abstraction:
                    # Test basic session operation
                    test_result = await self.session_management_abstraction.health_check()
                    validation_results["session_management_redis"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Session Management (Redis) test failed: {str(e)}")
            
            # Test Tenant Management (Redis)
            try:
                if self.tenant_abstraction:
                    # Test basic tenant operation
                    test_result = await self.tenant_abstraction.health_check()
                    validation_results["tenant_management_redis"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Tenant Management (Redis) test failed: {str(e)}")
            
            # Test Policy Management (Supabase)
            try:
                if self.policy_abstraction:
                    # Test basic policy operation
                    test_result = await self.policy_abstraction.health_check()
                    validation_results["policy_management_supabase"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Policy Management (Supabase) test failed: {str(e)}")
            
            # Overall status
            validation_results["overall_status"] = all([
                validation_results["authentication_supabase_jwt"],
                validation_results["authorization_supabase"],
                validation_results["session_management_redis"],
                validation_results["tenant_management_redis"],
                validation_results["policy_management_supabase"]
            ])
            
            if self.logger:
                self.logger.info("🔍 Security infrastructure mapping validation completed:")
                self.logger.info(f"  - Authentication (Supabase + JWT): {'✅' if validation_results['authentication_supabase_jwt'] else '❌'}")
                self.logger.info(f"  - Authorization (Supabase): {'✅' if validation_results['authorization_supabase'] else '❌'}")
                self.logger.info(f"  - Session Management (Redis): {'✅' if validation_results['session_management_redis'] else '❌'}")
                self.logger.info(f"  - Tenant Management (Redis): {'✅' if validation_results['tenant_management_redis'] else '❌'}")
                self.logger.info(f"  - Policy Management (Supabase): {'✅' if validation_results['policy_management_supabase'] else '❌'}")
                self.logger.info(f"  - Overall Status: {'✅' if validation_results['overall_status'] else '❌'}")
            
            return validation_results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error validating security infrastructure mapping: {str(e)}")
            return {
                "authentication_supabase_jwt": False,
                "authorization_supabase": False,
                "session_management_redis": False,
                "tenant_management_redis": False,
                "policy_management_supabase": False,
                "overall_status": False,
                "error": str(e)
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities with infrastructure status."""
        try:
            return {
                "service_name": "SecurityGuardService",
                "service_type": "security_enforcement",
                "realm": "smart_city",
                "capabilities": [
                    "user_authentication",
                    "access_authorization",
                    "session_management",
                    "tenant_isolation",
                    "policy_enforcement",
                    "zero_trust_security",
                    "infrastructure_integration"
                ],
                "infrastructure_connections": {
                    "authentication": "Supabase + JWT",
                    "authorization": "Supabase",
                    "session_management": "Redis",
                    "tenant_management": "Redis",
                    "policy_management": "Supabase"
                },
                "infrastructure_status": {
                    "connected": self.is_infrastructure_connected,
                    "authentication_available": self.auth_abstraction is not None,
                    "authorization_available": self.authorization_abstraction is not None,
                    "session_management_available": self.session_management_abstraction is not None,
                    "tenant_management_available": self.tenant_abstraction is not None,
                    "policy_management_available": self.policy_abstraction is not None
                },
                "soa_apis": self.soa_apis,
                "mcp_tools": self.mcp_tools,
                "status": "active",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting service capabilities: {str(e)}")
            return {
                "service_name": "SecurityGuardService",
                "error": str(e),
                "status": "error"
            }
