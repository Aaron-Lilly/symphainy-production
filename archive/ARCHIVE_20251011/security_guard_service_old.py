"""
Security Guard Service

Smart City role that handles the heavy lifting for multi-tenancy.
Follows the lightweight service + smart city role pattern.

WHAT (Smart City Role): I handle complex multi-tenant operations
HOW (Service Implementation): I use Supabase and MCP for heavy lifting
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json

from supabase import create_client, Client
from utilities import UserContext
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from bases.soa_service_base import SOAServiceBase
from backend.smart_city.protocols.soa_service_protocol import SOAServiceProtocol, SOAEndpoint, SOAServiceInfo

class SecurityGuardService(SOAServiceBase):
    """Security Guard Service - Does the heavy lifting for multi-tenancy."""

    def __init__(self, supabase_client: Client, utility_foundation, curator_foundation: CuratorFoundationService = None, public_works_foundation: PublicWorksFoundationService = None):
        """Initialize Security Guard Service."""
        super().__init__("SecurityGuardService", utility_foundation, curator_foundation)
        
        self.supabase_client = supabase_client
        self.public_works_foundation = public_works_foundation
        
        # Smart city abstractions from public works
        self.smart_city_abstractions = {}

        # Tenant management
        self.tenant_cache = {}

        # User context cache with full tenant details
        self.user_context_cache = {}

        # Audit log storage
        self.audit_logs = []
        
        # Initialize SOA protocol
        self.soa_protocol = SecurityGuardSOAProtocol("SecurityGuardService", self, curator_foundation), public_works_foundation

        self.logger.info("Security Guard Service initialized with multi-tenant capabilities")
    
    async def initialize(self):
        """Initialize Security Guard Service and load smart city abstractions."""
        try:
            # Call parent initialize first
            await super().initialize()
            
            self.logger.info("🚀 Initializing Security Guard Service...")
            
            # Initialize SOA protocol
            await self.soa_protocol.initialize()
            self.logger.info("✅ SOA Protocol initialized")
            
            # Load smart city abstractions from public works foundation
            if self.public_works_foundation:
                await self.soa_protocol.load_smart_city_abstractions()
                self.smart_city_abstractions = self.soa_protocol.get_all_abstractions()
                self.logger.info(f"✅ Loaded {len(self.smart_city_abstractions)} smart city abstractions from public works")
            else:
                self.logger.warning("⚠️ Public works foundation not available - using limited abstractions")
            
            self.logger.info("✅ Security Guard Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Security Guard Service: {e}")
            raise

    async def get_user_context_with_tenant(self, token: str) -> Dict[str, Any]:
        """Get user context with full tenant information - Heavy lifting."""
        try:
            # Check cache first
            if token in self.user_context_cache:
                cached_context = self.user_context_cache[token]
                if self._is_context_valid(cached_context):
                    return {"success": True, "user_context": cached_context}

            # Validate token with Supabase
            user_response = self.supabase_client.auth.get_user(token)

            if user_response.user:
                # Get user data with full tenant information
                user_data = await self._get_user_with_full_tenant_info(user_response.user.id)

                if user_data:
                    user_context = {
                        "user_id": user_data["id"],
                        "email": user_data["email"],
                        "full_name": user_data.get("full_name", ""),
                        "session_id": f"session_{user_data['id']}_{int(datetime.utcnow().timestamp())}",
                        "permissions": user_data.get("permissions", []),
                        "tenant_id": user_data.get("tenant_id", "default"),
                        "tenant_name": user_data.get("tenant_name", "Default Tenant"),
                        "tenant_type": user_data.get("tenant_type", "individual"),
                        "tenant_permissions": user_data.get("tenant_permissions", []),
                        "is_tenant_admin": user_data.get("is_tenant_admin", False),
                        "tenant_metadata": user_data.get("tenant_metadata", {}),
                        "request_id": str(uuid.uuid4()),
                        "timestamp": datetime.utcnow().isoformat(),
                        "last_active": datetime.utcnow().isoformat()
                    }

                    # Cache the context
                    self.user_context_cache[token] = user_context

                    return {"success": True, "user_context": user_context}

            return {"success": False, "error": "User not found"}

        except Exception as e:
            self.logger.error(f"Failed to get user context with tenant: {e}")
            return {"success": False, "error": str(e)}

    async def create_tenant(self, tenant_name: str, tenant_type: str,
                          admin_user_id: str, admin_email: str) -> Dict[str, Any]:
        """Create a new tenant - Heavy lifting."""
        try:
            # Create tenant record in Supabase
            tenant_data = {
                "name": tenant_name,
                "type": tenant_type,
                "admin_user_id": admin_user_id,
                "admin_email": admin_email,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
                "metadata": {
                    "max_users": self._get_max_users_for_type(tenant_type),
                    "features": self._get_features_for_type(tenant_type)
                }
            }

            result = self.supabase_client.table("tenants").insert(tenant_data).execute()

            if result.data:
                tenant_id = result.data[0]["id"]

                # Update user with tenant information
                await self._update_user_tenant(admin_user_id, tenant_id, is_admin=True)

                return {
                    "success": True,
                    "tenant_id": tenant_id,
                    "tenant": result.data[0]
                }
            else:
                return {"success": False, "error": "Failed to create tenant"}

        except Exception as e:
            self.logger.error(f"Tenant creation failed: {e}")
            return {"success": False, "error": str(e)}

    async def validate_user_permission(self, user_id: str, resource: str, action: str,
                                     user_permissions: List[str]) -> Dict[str, Any]:
        """Validate user permission with tenant context - Heavy lifting."""
        try:
            # Get user context with tenant information
            user_context = await self._get_user_context_by_id(user_id)

            if not user_context:
                return {"authorized": False, "error": "User not found"}

            # Check tenant access
            if not await self._validate_tenant_access(user_context, resource):
                return {"authorized": False, "error": "Tenant access denied"}

            # Check permissions
            has_permission = await self._check_user_permissions(
                user_context, resource, action, user_permissions
            )

            return {"authorized": has_permission}

        except Exception as e:
            self.logger.error(f"Permission validation failed: {e}")
            return {"authorized": False, "error": str(e)}

    async def audit_user_action(self, user_context: Dict[str, Any], action: str,
                               resource: str, service: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Audit user action with full tenant context - Heavy lifting."""
        try:
            audit_entry = {
                "user_id": user_context["user_id"],
                "email": user_context["email"],
                "session_id": user_context["session_id"],
                "tenant_id": user_context.get("tenant_id"),
                "tenant_name": user_context.get("tenant_name"),
                "action": action,
                "resource": resource,
                "service": service,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": user_context.get("request_id"),
                "details": details or {},
                "is_tenant_admin": user_context.get("is_tenant_admin", False)
            }

            # Store in local cache
            self.audit_logs.append(audit_entry)

            # Store in Supabase
            self.supabase_client.table("audit_logs").insert(audit_entry).execute()

            self.logger.info(f"Audit: {user_context['email']} ({user_context.get('tenant_name', 'No Tenant')}) performed {action} on {resource}")

            return {"success": True}

        except Exception as e:
            self.logger.error(f"Audit logging failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information."""
        try:
            result = self.supabase_client.table("tenants").select("*").eq("id", tenant_id).execute()

            if result.data:
                return {"success": True, "tenant": result.data[0]}
            else:
                return {"success": False, "error": "Tenant not found"}

        except Exception as e:
            self.logger.error(f"Tenant info retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    async def add_user_to_tenant(self, tenant_id: str, user_id: str, permissions: List[str] = None) -> Dict[str, Any]:
        """Add user to tenant."""
        try:
            # Update user with tenant information
            await self._update_user_tenant(user_id, tenant_id, is_admin=False, permissions=permissions)

            return {"success": True, "message": "User added to tenant"}

        except Exception as e:
            self.logger.error(f"Add user to tenant failed: {e}")
            return {"success": False, "error": str(e)}

    async def _get_user_with_full_tenant_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data with full tenant information from Supabase."""
        try:
            # Get user data
            user_result = self.supabase_client.table("users").select("*").eq("id", user_id).execute()

            if not user_result.data:
                return None

            user_data = user_result.data[0]

            # Get tenant information if user has tenant
            if user_data.get("tenant_id"):
                tenant_result = self.supabase_client.table("tenants").select("*").eq("id", user_data["tenant_id"]).execute()

                if tenant_result.data:
                    tenant_info = tenant_result.data[0]
                    user_data.update({
                        "tenant_name": tenant_info["name"],
                        "tenant_type": tenant_info["type"],
                        "tenant_metadata": tenant_info.get("metadata", {})
                    })

            return user_data

        except Exception as e:
            self.logger.error(f"Failed to get user with tenant info: {e}")
            return None

    async def _get_user_context_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user context by user ID."""
        try:
            user_data = await self._get_user_with_full_tenant_info(user_id)
            if user_data:
                return {
                    "user_id": user_data["id"],
                    "tenant_id": user_data.get("tenant_id"),
                    "permissions": user_data.get("permissions", []),
                    "tenant_permissions": user_data.get("tenant_permissions", []),
                    "is_tenant_admin": user_data.get("is_tenant_admin", False)
                }
            return None

        except Exception as e:
            self.logger.error(f"Failed to get user context by ID: {e}")
            return None

    async def _validate_tenant_access(self, user_context: Dict[str, Any], resource: str) -> bool:
        """Validate tenant access for resource."""
        # Simple validation - could be enhanced
        return True

    async def _check_user_permissions(self, user_context: Dict[str, Any], resource: str, action: str, user_permissions: List[str]) -> bool:
        """Check if user has permission for action on resource."""
        # Simple permission check - could be enhanced
        if "admin" in user_permissions:
            return True
        
        # Check tenant-specific permissions
        tenant_permissions = user_context.get("tenant_permissions", [])
        if f"{resource}:{action}" in tenant_permissions:
            return True
        
        return False

    async def _update_user_tenant(self, user_id: str, tenant_id: str,
                                 is_admin: bool = False, permissions: List[str] = None):
        """Update user with tenant information."""
        update_data = {
            "tenant_id": tenant_id,
            "is_tenant_admin": is_admin,
            "updated_at": datetime.utcnow().isoformat()
        }

        if permissions:
            update_data["tenant_permissions"] = permissions

        self.supabase_client.table("users").update(update_data).eq("id", user_id).execute()

    def _get_max_users_for_type(self, tenant_type: str) -> int:
        """Get maximum users for tenant type."""
        limits = {
            "individual": 1,
            "organization": 50,
            "enterprise": 1000
        }
        return limits.get(tenant_type, 1)

    def _get_features_for_type(self, tenant_type: str) -> List[str]:
        """Get features available for tenant type."""
        features = {
            "individual": ["basic_analytics", "file_upload"],
            "organization": ["basic_analytics", "file_upload", "team_collaboration", "advanced_insights"],
            "enterprise": ["basic_analytics", "file_upload", "team_collaboration", "advanced_insights", "custom_integrations", "audit_logs"]
        }
        return features.get(tenant_type, ["basic_analytics"])

    def _is_context_valid(self, context: Dict[str, Any]) -> bool:
        """Check if cached context is still valid."""
        timestamp_str = context.get("timestamp")
        if not timestamp_str:
            return False

        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            return (datetime.utcnow() - timestamp).seconds < 3600
        except:
            return False
    
    def get_smart_city_abstractions(self) -> Dict[str, Any]:
        """Get all smart city abstractions from public works foundation."""
        return self.smart_city_abstractions.copy()
    
    def get_abstraction_for_role(self, role: str) -> Dict[str, Any]:
        """Get abstractions specific to a smart city role."""
        if not self.public_works_foundation:
            return {}
        
        try:
            return self.public_works_foundation.get_role_abstractions("smart_city", role)
        except Exception as e:
            self.logger.error(f"Failed to get abstractions for role {role}: {e}")
            return {}
    
    def has_abstraction(self, abstraction_name: str) -> bool:
        """Check if a specific abstraction is available."""
        return abstraction_name in self.smart_city_abstractions
    
    def get_abstraction(self, abstraction_name: str) -> Any:
        """Get a specific abstraction by name."""
        return self.smart_city_abstractions.get(abstraction_name)


class SecurityGuardSOAProtocol(SOAServiceProtocol):
    """SOA Protocol implementation for Security Guard Service."""
    
    def __init__(self, service_name: str, service_instance, curator_foundation=None, public_works_foundation=None):
        """Initialize Security Guard SOA Protocol."""
        super().__init__(service_name, None, curator_foundation, public_works_foundation)
        self.service_instance = service_instance
        self.service_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the SOA service."""
        # Create service info with multi-tenant metadata
        self.service_info = SOAServiceInfo(
            service_name="SecurityGuardService",
            version="1.0.0",
            description="Security Guard Service - Multi-tenant security and tenant management",
            interface_name="ISecurityGuard",
            endpoints=self._create_all_endpoints(),
            tags=["security", "multi-tenant", "tenant-management"],
            contact={"email": "security@smartcity.com"},
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_service_info(self) -> SOAServiceInfo:
        """Get service information for OpenAPI generation."""
        return self.service_info
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI 3.0 specification for this service."""
        if not self.service_info:
            return {"error": "Service not initialized"}
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.service_info.service_name,
                "version": self.service_info.version,
                "description": self.service_info.description,
                "contact": self.service_info.contact
            },
            "servers": [
                {"url": "https://api.smartcity.com/security-guard", "description": "Security Guard Service"}
            ],
            "paths": self._create_openapi_paths(),
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }
    
    def get_docs(self) -> Dict[str, Any]:
        """Get service documentation."""
        return {
            "service": self.service_info.service_name,
            "description": self.service_info.description,
            "version": self.service_info.version,
            "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
            "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
            "tenant_isolation_level": self.service_info.tenant_isolation_level
        }
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this service with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.service_info.interface_name,
                "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
                "tools": [],  # MCP tools handled separately
                "description": self.service_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
                "tenant_isolation_level": self.service_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.service_name, 
                capability, 
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_endpoints(self) -> List[SOAEndpoint]:
        """Create all endpoints for Security Guard Service."""
        endpoints = []
        
        # Standard endpoints
        endpoints.extend(self._create_standard_endpoints())
        endpoints.extend(self._create_health_endpoints())
        endpoints.extend(self._create_tenant_aware_endpoints())
        
        # Security Guard specific endpoints
        endpoints.extend([
            SOAEndpoint(
                path="/user-context",
                method="POST",
                summary="Get User Context with Tenant",
                description="Get user context with full tenant information",
                request_schema={
                    "type": "object",
                    "properties": {
                        "token": {"type": "string", "description": "User authentication token"}
                    },
                    "required": ["token"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "tenant_id": {"type": "string"},
                        "permissions": {"type": "array", "items": {"type": "string"}}
                    }
                }),
                tags=["Security", "Multi-Tenant"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/tenant/create",
                method="POST",
                summary="Create Tenant",
                description="Create a new tenant",
                request_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "tenant_type": {"type": "string"},
                        "admin_user_id": {"type": "string"},
                        "admin_email": {"type": "string"}
                    },
                    "required": ["name", "tenant_type", "admin_user_id", "admin_email"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Tenant", "Management"],
                requires_tenant=False,
                tenant_scope="global"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}",
                method="GET",
                summary="Get Tenant Information",
                description="Get information about a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Tenant", "Information"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return endpoints
    
    def _create_openapi_paths(self) -> Dict[str, Any]:
        """Create OpenAPI paths for all endpoints."""
        paths = {}
        
        for endpoint in self.service_info.endpoints:
            path_item = {
                endpoint.method.lower(): {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "security": [{"BearerAuth": []}] if endpoint.requires_tenant else []
                }
            }
            
            if endpoint.parameters:
                path_item[endpoint.method.lower()]["parameters"] = endpoint.parameters
            
            if endpoint.request_schema:
                path_item[endpoint.method.lower()]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
            
            if endpoint.response_schema:
                path_item[endpoint.method.lower()]["responses"] = {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": self._create_error_response_schema()
                            }
                        }
                    }
                }
            
            paths[endpoint.path] = path_item
        
        return paths
    