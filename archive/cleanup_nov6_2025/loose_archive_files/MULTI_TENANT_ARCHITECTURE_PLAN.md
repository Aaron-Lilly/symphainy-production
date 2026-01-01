# Multi-Tenant Architecture Plan

## Executive Summary

This plan implements multi-tenancy through our DDD architectural layers, following the **lightweight service + smart city role** pattern. The **Security Service** remains lightweight and delegates heavy lifting to the **Security Guard** (smart city role), just like the telemetry service and the nurse.

## Current State Analysis

### ✅ **Existing Foundation (Build On)**
- **Security Service**: Already widely used across all platform layers
- **UserContext**: Already includes `tenant_id` field
- **Permission System**: Already has role-based access control
- **Audit Logging**: Already tracks user actions
- **Service Integration**: Already integrated with all pillar services

### ❌ **Missing Multi-Tenant Capabilities**
- **Tenant Isolation**: No data filtering by tenant
- **Tenant Management**: No tenant creation/management
- **Access Control**: No tenant-specific permissions
- **Data Segregation**: No tenant-specific data storage

## Architecture Overview

### **Lightweight Security Service + Security Guard Pattern**

```
┌─────────────────────────────────────────────────────────────┐
│                SECURITY SERVICE (Lightweight)              │
│              (Delegates to Security Guard)                 │
├─────────────────────────────────────────────────────────────┤
│ • Simple UserContext Management                            │
│ • Basic Token Validation                                   │
│ • Calls Security Guard for Heavy Lifting                   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                SECURITY GUARD (Smart City Role)            │
│                 (Does the Heavy Lifting)                   │
├─────────────────────────────────────────────────────────────┤
│ • Tenant Management & Creation                             │
│ • Complex User Context with Tenant Isolation               │
│ • Advanced Access Control & Permissions                    │
│ • Comprehensive Audit Logging                              │
│ • Multi-Tenant Token Validation                            │
│ • Tenant-Specific Data Operations                          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                ALL PLATFORM LAYERS                         │
│              (Automatically Multi-Tenant)                  │
├─────────────────────────────────────────────────────────────┤
│ • Experience Layer (Frontend Integration)                  │
│ • Business Enablement Pillars                              │
│ • Smart City Services                                      │
│ • Foundation Services                                       │
│ • All Micro-Modules                                        │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Lightweight Security Service + Security Guard

### 1.1 Lightweight Security Service (Foundation Layer)

**File**: `foundations/utility_foundation/utilities/security/security_service.py`

**Real Implementation** (Lightweight, delegates to Security Guard):
```python
@dataclass
class UserContext:
    """Simple user context - Security Guard provides full details."""
    user_id: str
    email: str
    full_name: str
    session_id: str
    permissions: List[str]
    tenant_id: Optional[str] = None
    request_id: str = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

class SecurityService:
    """Lightweight Security Service that delegates to Security Guard."""
    
    def __init__(self, service_name: str, security_guard_client=None):
        """Initialize lightweight security service."""
        self.service_name = service_name
        self.security_guard_client = security_guard_client
        self.logger = logging.getLogger(f"SecurityService-{service_name}")
        
        # Simple user context cache
        self.user_context_cache = {}
        
        self.logger.info(f"Lightweight security service initialized for {service_name}")
    
    async def get_user_context(self, token: str) -> Optional[UserContext]:
        """Get user context by delegating to Security Guard."""
        try:
            # Check cache first
            if token in self.user_context_cache:
                cached_context = self.user_context_cache[token]
                if self._is_context_valid(cached_context):
                    return cached_context
            
            # Delegate to Security Guard for heavy lifting
            if self.security_guard_client:
                result = await self.security_guard_client.call_tool(
                    "get_user_context_with_tenant",
                    input_data=json.dumps({"token": token})
                )
                
                if result.get("success") and result.get("user_context"):
                    user_data = result["user_context"]
                    
                    user_context = UserContext(
                        user_id=user_data["user_id"],
                        email=user_data["email"],
                        full_name=user_data["full_name"],
                        session_id=user_data["session_id"],
                        permissions=user_data.get("permissions", []),
                        tenant_id=user_data.get("tenant_id"),
                        request_id=str(uuid.uuid4()),
                        timestamp=datetime.utcnow()
                    )
                    
                    # Cache the context
                    self.user_context_cache[token] = user_context
                    
                    return user_context
            else:
                # Fallback for development
                self.logger.warning("Security Guard client not available, using mock user context")
                return self._create_mock_user_context(token)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get user context: {e}")
            return None
    
    async def validate_user_permission(self, user_id: str, resource: str, action: str, 
                                     user_permissions: List[str] = None) -> bool:
        """Validate user permission by delegating to Security Guard."""
        try:
            if self.security_guard_client:
                result = await self.security_guard_client.call_tool(
                    "validate_user_permission",
                    input_data=json.dumps({
                        "user_id": user_id,
                        "resource": resource,
                        "action": action,
                        "user_permissions": user_permissions or []
                    })
                )
                return result.get("authorized", False)
            else:
                # Fallback for development
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to validate user permission: {e}")
            return False
    
    async def audit_user_action(self, user_context: UserContext, action: str, resource: str, 
                               details: Dict[str, Any] = None):
        """Audit user action by delegating to Security Guard."""
        try:
            if self.security_guard_client:
                await self.security_guard_client.call_tool(
                    "audit_user_action",
                    input_data=json.dumps({
                        "user_context": user_context.to_dict(),
                        "action": action,
                        "resource": resource,
                        "service": self.service_name,
                        "details": details or {}
                    })
                )
            else:
                # Simple logging for development
                self.logger.info(f"Audit: {user_context.email} performed {action} on {resource}")
                
        except Exception as e:
            self.logger.error(f"Failed to audit user action: {e}")
    
    def set_security_guard_client(self, security_guard_client):
        """Set Security Guard client for heavy lifting."""
        self.security_guard_client = security_guard_client
        self.logger.info(f"Set Security Guard client for {self.service_name}")
    
    def _is_context_valid(self, context: UserContext) -> bool:
        """Check if cached context is still valid."""
        # Simple validation - could be enhanced
        return context.timestamp and (datetime.utcnow() - context.timestamp).seconds < 3600
    
    def _create_mock_user_context(self, token: str) -> UserContext:
        """Create mock user context for development."""
        return UserContext(
            user_id="mock_user",
            email="mock@example.com",
            full_name="Mock User",
            session_id=f"session_{int(datetime.utcnow().timestamp())}",
            permissions=["user"],
            tenant_id="default_tenant"
        )
```

### 1.2 Security Guard (Smart City Role) - Heavy Lifting

**File**: `backend/smart_city/services/security_guard/security_guard_service.py`

**Real Implementation** (Does the heavy lifting):
```python
class SecurityGuardService:
    """Security Guard Service - Does the heavy lifting for multi-tenancy."""
    
    def __init__(self, supabase_client):
        self.supabase_client = supabase_client
        self.logger = logging.getLogger("SecurityGuardService")
        
        # Tenant management
        self.tenant_cache = {}
        
        # User context cache with full tenant details
        self.user_context_cache = {}
        
        # Audit log storage
        self.audit_logs = []
        
        self.logger.info("Security Guard Service initialized with multi-tenant capabilities")
    
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
```

**Real Implementation**:
```python
class TenantManagementService:
    """Manages tenant creation, configuration, and isolation."""
    
    def __init__(self, supabase_client):
        self.supabase_client = supabase_client
        self.logger = logging.getLogger("TenantManagementService")
    
    async def create_tenant(self, tenant_name: str, tenant_type: str, 
                          admin_user_id: str, admin_email: str) -> Dict[str, Any]:
        """Create a new tenant with admin user."""
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
                raise Exception("Failed to create tenant")
                
        except Exception as e:
            self.logger.error(f"Tenant creation failed: {e}")
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
            self.logger.error(f"Get tenant info failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def add_user_to_tenant(self, user_id: str, tenant_id: str, 
                                permissions: List[str] = None) -> Dict[str, Any]:
        """Add user to tenant with specific permissions."""
        try:
            # Verify tenant exists
            tenant_result = await self.get_tenant_info(tenant_id)
            if not tenant_result["success"]:
                return {"success": False, "error": "Tenant not found"}
            
            # Update user with tenant information
            await self._update_user_tenant(user_id, tenant_id, permissions=permissions)
            
            return {"success": True, "message": "User added to tenant"}
            
        except Exception as e:
            self.logger.error(f"Add user to tenant failed: {e}")
            return {"success": False, "error": str(e)}
    
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
```

### 1.3 Enhanced Security Service with Multi-Tenancy

**File**: `foundations/utility_foundation/utilities/security/security_service.py`

**Real Implementation**:
```python
class SecurityService:
    """Enhanced Security Service with full multi-tenant support."""
    
    def __init__(self, service_name: str, supabase_client=None):
        self.service_name = service_name
        self.supabase_client = supabase_client
        self.tenant_management = TenantManagementService(supabase_client) if supabase_client else None
        self.logger = logging.getLogger(f"SecurityService-{service_name}")
        
        # User context cache with tenant isolation
        self.user_context_cache = {}
        
        # Audit log storage with tenant context
        self.audit_logs = []
        
        self.logger.info(f"Multi-tenant security service initialized for {service_name}")
    
    async def get_user_context(self, token: str) -> Optional[UserContext]:
        """Get user context with full tenant information."""
        try:
            # Check cache first (tenant-isolated)
            cache_key = f"{token}_context"
            if cache_key in self.user_context_cache:
                cached_context = self.user_context_cache[cache_key]
                if self._is_context_valid(cached_context):
                    return cached_context
            
            # Validate token with Supabase
            if self.supabase_client:
                user_response = self.supabase_client.auth.get_user(token)
                
                if user_response.user:
                    # Get user data with tenant information
                    user_data = await self._get_user_with_tenant_info(user_response.user.id)
                    
                    if user_data:
                        user_context = UserContext(
                            user_id=user_data["id"],
                            email=user_data["email"],
                            full_name=user_data.get("full_name", ""),
                            session_id=f"session_{user_data['id']}_{int(datetime.utcnow().timestamp())}",
                            permissions=user_data.get("permissions", []),
                            tenant_id=user_data.get("tenant_id", "default"),
                            tenant_name=user_data.get("tenant_name", "Default Tenant"),
                            tenant_type=user_data.get("tenant_type", "individual"),
                            tenant_permissions=user_data.get("tenant_permissions", []),
                            is_tenant_admin=user_data.get("is_tenant_admin", False),
                            tenant_metadata=user_data.get("tenant_metadata", {}),
                            request_id=str(uuid.uuid4()),
                            timestamp=datetime.utcnow(),
                            last_active=datetime.utcnow()
                        )
                        
                        # Cache the context
                        self.user_context_cache[cache_key] = user_context
                        
                        return user_context
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get user context: {e}")
            return None
    
    async def _get_user_with_tenant_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data with tenant information from Supabase."""
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
    
    async def validate_tenant_access(self, user_context: UserContext, resource_tenant_id: str) -> bool:
        """Validate user can access resource in specific tenant."""
        try:
            # User can access their own tenant
            if user_context.tenant_id == resource_tenant_id:
                return True
            
            # Tenant admins can access their tenant
            if user_context.is_tenant_admin and user_context.tenant_id == resource_tenant_id:
                return True
            
            # System admins can access any tenant
            if "admin" in user_context.permissions:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to validate tenant access: {e}")
            return False
    
    async def audit_user_action(self, user_context: UserContext, action: str, resource: str, 
                               details: Dict[str, Any] = None):
        """Audit user action with full tenant context."""
        try:
            audit_entry = {
                "user_id": user_context.user_id,
                "email": user_context.email,
                "session_id": user_context.session_id,
                "tenant_id": user_context.tenant_id,
                "tenant_name": user_context.tenant_name,
                "action": action,
                "resource": resource,
                "service": self.service_name,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": user_context.request_id,
                "details": details or {},
                "is_tenant_admin": user_context.is_tenant_admin
            }
            
            # Store in local cache
            self.audit_logs.append(audit_entry)
            
            # Store in Supabase if available
            if self.supabase_client:
                self.supabase_client.table("audit_logs").insert(audit_entry).execute()
            
            self.logger.info(f"Audit: {user_context.email} ({user_context.tenant_name}) performed {action} on {resource}")
            
        except Exception as e:
            self.logger.error(f"Failed to audit user action: {e}")
```

## Phase 2: Platform Layer Integration

### 2.1 Content Pillar Multi-Tenant Integration

**File**: `backend/business_enablement/pillars/content_pillar/content_pillar_service.py`

**Real Implementation**:
```python
class ContentPillarService(FoundationServiceBase):
    """Content Pillar Service with multi-tenant support."""
    
    async def list_user_files(self, user_id: str, user_context: UserContext) -> Dict[str, Any]:
        """List files for user with tenant isolation."""
        try:
            # Validate tenant access
            if not await self.security_service.validate_tenant_access(user_context, user_context.tenant_id):
                return {"success": False, "error": "Access denied"}
            
            # Get files filtered by user and tenant
            files = await self._get_files_for_tenant(user_context.tenant_id, user_id)
            
            # Audit the action
            await self.security_service.audit_user_action(
                user_context, "list_files", "content_pillar", 
                {"file_count": len(files)}
            )
            
            return {"success": True, "files": files}
            
        except Exception as e:
            self.logger.error(f"List user files failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def upload_file(self, request: UploadRequest, user_context: UserContext) -> UploadResponse:
        """Upload file with tenant isolation."""
        try:
            # Validate tenant access
            if not await self.security_service.validate_tenant_access(user_context, user_context.tenant_id):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Create file metadata with tenant information
            file_metadata = FileMetadata(
                file_id=request.file_id,
                filename=request.filename,
                file_type=request.file_type,
                file_size=request.file_size,
                upload_timestamp=datetime.utcnow(),
                user_id=user_context.user_id,
                session_id=user_context.session_id,
                tenant_id=user_context.tenant_id,  # Add tenant isolation
                content_hash=request.content_hash,
                mime_type=request.mime_type,
                metadata=request.metadata
            )
            
            # Store file with tenant isolation
            result = await self._store_file_with_tenant(file_metadata, user_context.tenant_id)
            
            # Audit the action
            await self.security_service.audit_user_action(
                user_context, "upload_file", "content_pillar",
                {"file_id": file_metadata.file_id, "file_type": file_metadata.file_type.value}
            )
            
            return UploadResponse(
                success=True,
                file_metadata=file_metadata,
                message="File uploaded successfully"
            )
            
        except Exception as e:
            self.logger.error(f"File upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_files_for_tenant(self, tenant_id: str, user_id: str) -> List[FileMetadata]:
        """Get files for specific tenant and user."""
        try:
            # Query Supabase with tenant and user filters
            result = self.supabase_client.table("files").select("*").eq("tenant_id", tenant_id).eq("user_id", user_id).execute()
            
            files = []
            for file_data in result.data:
                files.append(FileMetadata(
                    file_id=file_data["file_id"],
                    filename=file_data["filename"],
                    file_type=FileType(file_data["file_type"]),
                    file_size=file_data["file_size"],
                    upload_timestamp=datetime.fromisoformat(file_data["upload_timestamp"]),
                    user_id=file_data["user_id"],
                    session_id=file_data["session_id"],
                    tenant_id=file_data["tenant_id"],
                    content_hash=file_data["content_hash"],
                    mime_type=file_data["mime_type"],
                    metadata=file_data.get("metadata", {})
                ))
            
            return files
            
        except Exception as e:
            self.logger.error(f"Get files for tenant failed: {e}")
            return []
```

### 2.2 Experience Layer Multi-Tenant Integration

**File**: `experience/roles/frontend_integration/micro_modules/pillar_api_handlers.py`

**Real Implementation**:
```python
class PillarAPIHandlers:
    """Pillar API Handlers with multi-tenant support."""
    
    async def get_user_context(self, token: str = None) -> UserContext:
        """Get user context with tenant validation."""
        try:
            if not token:
                raise HTTPException(status_code=401, detail="No authentication token")
            
            # Use security service to get user context with tenant info
            user_context = await self.security_service.get_user_context(token)
            
            if not user_context:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Validate tenant access
            if not await self.security_service.validate_tenant_access(user_context, user_context.tenant_id):
                raise HTTPException(status_code=403, detail="Tenant access denied")
            
            return user_context
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"User context retrieval failed: {e}")
            raise HTTPException(status_code=500, detail="Authentication failed")
    
    async def content_upload_handler(self, file_data: bytes, filename: str, 
                                   file_type: str, user_context: UserContext) -> JSONResponse:
        """Handle content upload with tenant isolation."""
        try:
            # Create upload request with tenant context
            upload_request = UploadRequest(
                file_id=generate_file_id(filename),
                filename=filename,
                file_type=FileType(file_type),
                file_size=len(file_data),
                file_data=file_data,
                user_id=user_context.user_id,
                session_id=user_context.session_id,
                tenant_id=user_context.tenant_id,  # Add tenant context
                content_hash=hashlib.sha256(file_data).hexdigest(),
                mime_type=detect_mime_type_from_extension(get_file_extension(filename)),
                metadata={}
            )
            
            # Upload through content pillar service
            result = await self.content_service.upload_file(upload_request, user_context)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": result.success,
                    "file_metadata": result.file_metadata.to_dict() if result.file_metadata else None,
                    "message": result.message
                }
            )
            
        except Exception as e:
            self.logger.error(f"Content upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
```

## Phase 3: Database Schema Updates

### 3.1 Supabase Schema Updates

**Real Implementation**:
```sql
-- Tenants table
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('individual', 'organization', 'enterprise')),
    admin_user_id UUID NOT NULL,
    admin_email VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced users table
ALTER TABLE users ADD COLUMN tenant_id UUID REFERENCES tenants(id);
ALTER TABLE users ADD COLUMN is_tenant_admin BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN tenant_permissions TEXT[] DEFAULT '{}';
ALTER TABLE users ADD COLUMN last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Enhanced files table
ALTER TABLE files ADD COLUMN tenant_id UUID REFERENCES tenants(id);
CREATE INDEX idx_files_tenant_user ON files(tenant_id, user_id);

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    email VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    tenant_id UUID REFERENCES tenants(id),
    tenant_name VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    service VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    request_id UUID NOT NULL,
    details JSONB DEFAULT '{}',
    is_tenant_admin BOOLEAN DEFAULT FALSE
);

-- Row Level Security (RLS) policies
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only see their own files" ON files
    FOR ALL USING (user_id = auth.uid() AND tenant_id = (
        SELECT tenant_id FROM users WHERE id = auth.uid()
    ));

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only see their tenant's audit logs" ON audit_logs
    FOR ALL USING (tenant_id = (
        SELECT tenant_id FROM users WHERE id = auth.uid()
    ));
```

## Phase 4: Frontend Multi-Tenant Integration

### 4.1 Enhanced Experience Layer Client

**File**: `lib/api/experience-layer-client.ts`

**Real Implementation**:
```typescript
export interface UserContext {
  user_id: string;
  email: string;
  full_name: string;
  session_id: string;
  tenant_id: string;
  tenant_name: string;
  tenant_type: string;
  permissions: string[];
  tenant_permissions: string[];
  is_tenant_admin: boolean;
  created_at: string;
  last_active: string;
}

export class ExperienceLayerClient {
  private sessionToken: string | null = null;
  private userContext: UserContext | null = null;

  // Real authentication with tenant context
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    
    const data = await response.json();
    
    if (data.success && data.token) {
      this.sessionToken = data.token;
      this.userContext = data.user;
      this.saveToStorage();
    }
    
    return data;
  }

  // Real content operations with tenant isolation
  content = {
    listFiles: async () => {
      const response = await fetch(`${API_BASE}/api/content/files`, {
        headers: this.getHeaders(),
      });
      return response.json();
    },
    
    uploadFile: async (file: File, fileType: string) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("file_type", fileType);
      
      const response = await fetch(`${API_BASE}/api/content/upload`, {
        method: "POST",
        body: formData,
        headers: this.getHeaders(false),
      });
      return response.json();
    },

    deleteFile: async (fileId: string) => {
      const response = await fetch(`${API_BASE}/api/content/files/${fileId}`, {
        method: "DELETE",
        headers: this.getHeaders(),
      });
      return response.json();
    }
  };

  // Real tenant management
  tenant = {
    getInfo: async () => {
      const response = await fetch(`${API_BASE}/api/tenant/info`, {
        headers: this.getHeaders(),
      });
      return response.json();
    },

    addUser: async (email: string, permissions: string[] = []) => {
      const response = await fetch(`${API_BASE}/api/tenant/add-user`, {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify({ email, permissions }),
      });
      return response.json();
    }
  };
}
```

## Implementation Timeline

### Week 1: Security Service Foundation
- Day 1-2: Enhanced UserContext and TenantManagementService
- Day 3-4: Enhanced SecurityService with multi-tenancy
- Day 5: Database schema updates

### Week 2: Platform Integration
- Day 1-2: Content Pillar multi-tenant integration
- Day 3-4: Experience Layer multi-tenant integration
- Day 5: Other pillar services integration

### Week 3: Frontend & Testing
- Day 1-2: Frontend multi-tenant client
- Day 3-4: Multi-tenant testing
- Day 5: Production readiness validation

## Success Criteria

### ✅ **Security Service Success**
- Tenant management working with Supabase
- User context includes full tenant information
- Access control validates tenant access
- Audit logging includes tenant context

### ✅ **Platform Success**
- All pillar services filter by tenant
- All API calls include tenant validation
- Data isolation working correctly
- No cross-tenant data leakage

### ✅ **Frontend Success**
- User context includes tenant information
- All API calls use tenant-aware client
- Tenant management UI working
- Multi-user testing successful

## Benefits

### ✅ **Lightweight Service Pattern**
- Security Service remains lightweight and focused
- Security Guard does the heavy lifting
- Follows established telemetry service + nurse pattern

### ✅ **Automatic Multi-Tenancy**
- All platform layers automatically get multi-tenancy
- No need to modify individual services
- Consistent tenant isolation everywhere

### ✅ **Smart City Role Integration**
- Security Guard handles complex tenant operations
- MCP server integration for tool calls
- Scalable and maintainable architecture

### ✅ **Production Ready**
- Built for multiple tenants from the start
- No architectural debt
- Real multi-user system with proper isolation

This plan ensures multi-tenancy is implemented through our DDD architectural layers with the **lightweight Security Service** delegating to the **Security Guard smart city role**, providing automatic tenant isolation throughout the entire platform while following our established patterns.
