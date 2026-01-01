# Authentication Refactor - Move Infrastructure Logic to Abstraction

**Date:** December 2024  
**Status:** 📋 **READY TO IMPLEMENT**  
**Pattern:** Role=What, Service=How, Abstraction=Swappability

---

## 🎯 Goal

Move all infrastructure logic from handlers into `AuthAbstraction`, making handlers simple and swapping seamless.

---

## 📋 Implementation Steps

### **Step 1: Add `get_user_context()` to Protocol**

**File:** `foundations/public_works_foundation/abstraction_contracts/authentication_protocol.py`

**Add method:**
```python
class AuthenticationProtocol(Protocol):
    """Generic authentication protocol - no technology dependencies."""
    
    # User/Tenant Authentication (Supabase API) - NEW
    async def get_user_context(self, token: str) -> SecurityContext:
        """
        Get user/tenant context from authentication service (Supabase API).
        
        This is for user/tenant authentication - requires network call to get
        user context (tenant_id, roles, permissions).
        
        Use case: ForwardAuth endpoint (needs user context in headers)
        """
        ...
    
    # Token Validation (JWKS Local) - EXISTING (keep as-is)
    async def validate_token(self, token: str) -> SecurityContext:
        """
        Validate token signature using local verification (JWKS).
        
        This is for token validation - fast, local, no network calls.
        Validates signature, expiration, issuer.
        
        Use case: Handler-level validation (fast token check)
        """
        ...
    
    # Existing methods (keep as-is)
    async def authenticate_user(self, credentials: Dict[str, Any]) -> SecurityContext: ...
    async def refresh_token(self, refresh_token: str) -> SecurityContext: ...
    async def logout_user(self, token: str) -> bool: ...
    async def get_user_info(self, user_id: str) -> Dict[str, Any]: ...
    async def update_user_metadata(self, user_id: str, metadata: Dict[str, Any]) -> bool: ...
```

---

### **Step 2: Implement `get_user_context()` in AuthAbstraction**

**File:** `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py`

**Add method (after `authenticate_user`, before `validate_token`):**
```python
async def get_user_context(self, token: str) -> SecurityContext:
    """
    Get user/tenant context via Supabase API.
    
    ALL infrastructure logic here:
    - Calls Supabase API (get_user)
    - Handles errors
    - Extracts user/tenant/roles
    - Queries database for tenant info (if needed)
    - Returns SecurityContext
    
    Handler just calls: context = await auth.get_user_context(token)
    """
    try:
        self.logger.info("🔐 [AUTH_ABSTRACTION] Getting user context (Supabase API)...")
        
        # Infrastructure logic: Supabase API call
        result = await self.supabase.get_user(token)
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            self.logger.error(f"❌ [AUTH_ABSTRACTION] User context failed: {error_msg}")
            raise AuthenticationError(f"User context failed: {error_msg}")
        
        self.logger.info("🔐 [AUTH_ABSTRACTION] User context retrieved (Supabase API)")
        
        # Infrastructure logic: Extract user info
        user_data = result.get("user", {})
        user_id = user_data.get("id")
        email = user_data.get("email")
        user_metadata = user_data.get("user_metadata", {})
        
        # Infrastructure logic: Extract tenant info
        # Try multiple sources (user_metadata, database query, etc.)
        tenant_id = (
            user_metadata.get("tenant_id") or
            user_data.get("tenant_id") or
            None
        )
        
        # Infrastructure logic: Extract roles/permissions
        roles = user_metadata.get("roles", [])
        permissions = user_metadata.get("permissions", [])
        
        # Infrastructure logic: Query database for tenant info (if needed)
        # This is where we'd add database queries for tenant context
        # For now, use what we got from Supabase
        if not tenant_id and user_id:
            # Could query database here for tenant info
            # tenant_info = await self._get_user_tenant_info_from_db(user_id)
            # tenant_id = tenant_info.get("tenant_id")
            self.logger.warning(f"⚠️ User {user_id} has no tenant_id - using default")
        
        # Return clean SecurityContext - handler doesn't need to know how we got it
        context = SecurityContext(
            user_id=user_id,
            tenant_id=tenant_id,
            roles=roles if isinstance(roles, list) else [roles] if roles else [],
            permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
            origin="supabase_user_context"
        )
        
        self.logger.info(f"✅ User context retrieved: user={user_id}, tenant={tenant_id}")
        return context
        
    except AuthenticationError:
        raise  # Re-raise authentication errors
    except Exception as e:
        self.logger.error(f"❌ [AUTH_ABSTRACTION] User context error: {e}", exc_info=True)
        raise AuthenticationError(f"Failed to get user context: {str(e)}")
```

---

### **Step 3: Simplify ForwardAuth Handler**

**File:** `backend/api/auth_router.py`

**Replace `validate_token_forwardauth()` method:**
```python
@router.get("/validate-token")
async def validate_token_forwardauth(request: Request) -> Response:
    """
    ForwardAuth endpoint - uses user authentication abstraction.
    
    Handler is simple - just calls abstraction.
    All infrastructure logic moved to AuthAbstraction.get_user_context()
    """
    try:
        # Extract token (minimal - just header parsing)
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.debug("ForwardAuth: Missing or invalid Authorization header")
            return Response(status_code=401, content="Unauthorized: Missing or invalid token")
        
        token = auth_header.replace("Bearer ", "")
        
        # Get abstraction (dependency injection)
        from backend.api.auth_router import get_security_guard
        security_guard = await get_security_guard()
        
        if not security_guard or not hasattr(security_guard, 'get_auth_abstraction'):
            logger.error("ForwardAuth: Security Guard not available")
            return Response(status_code=503, content="Service Unavailable: Security Guard not available")
        
        auth_abstraction = security_guard.get_auth_abstraction()
        
        if not auth_abstraction:
            logger.error("ForwardAuth: Auth abstraction not available")
            return Response(status_code=503, content="Service Unavailable: Auth abstraction not available")
        
        # Call abstraction - ALL infrastructure logic is here
        user_context = await auth_abstraction.get_user_context(token)
        
        # Return headers - simple mapping
        return Response(
            status_code=200,
            headers={
                "X-User-Id": user_context.user_id or "",
                "X-Tenant-Id": user_context.tenant_id or "",
                "X-User-Email": user_context.email or "",
                "X-User-Roles": ",".join(user_context.roles) if user_context.roles else "",
                "X-User-Permissions": ",".join(user_context.permissions) if user_context.permissions else "",
                "X-Auth-Origin": user_context.origin or "forwardauth"
            }
        )
        
    except AuthenticationError as e:
        logger.error(f"ForwardAuth: Authentication error: {e}")
        return Response(status_code=401, content=f"Unauthorized: {str(e)}")
    except Exception as e:
        logger.error(f"ForwardAuth: Error: {e}", exc_info=True)
        return Response(status_code=503, content=f"Service Unavailable: {str(e)}")
```

---

### **Step 4: Handler-Level Already Simple (No Changes Needed)**

**File:** `backend/api/universal_pillar_router.py`

**Current implementation is already good:**
```python
# Handler already calls abstraction - no infrastructure logic here
auth_abstraction = security_guard.get_auth_abstraction()
security_context = await auth_abstraction.validate_token(token)  # ✅ Already using abstraction
```

**No changes needed** - handler-level validation already follows the pattern!

---

## ✅ Benefits

### **1. ForwardAuth Handler Simplified**
- **Before:** 80+ lines of infrastructure logic (Supabase API calls, error handling, header extraction)
- **After:** ~30 lines (just calls abstraction, maps to headers)

### **2. Swapping Is Easy**
- **Change Supabase → Auth0:** Just swap adapter in AuthAbstraction
- **Change JWKS → Custom:** Just swap adapter in AuthAbstraction
- **Handlers never change**

### **3. No Handler Updates**
- Infrastructure changes → AuthAbstraction only
- Adapter changes → Adapter only
- Handlers stay simple

### **4. Follows Your Pattern**
- **Role=What:** Authentication (what we need)
- **Service=How:** AuthAbstraction (how we do it)
- **Abstraction=Swappability:** Change adapter, not handlers

---

## 🔄 Swapping Example

### **Swap Supabase for Auth0**

**Step 1: Create Auth0Adapter**
```python
class Auth0Adapter:
    async def get_user(self, token: str) -> Dict[str, Any]:
        # Auth0 API call logic
        ...
```

**Step 2: Update AuthAbstraction**
```python
auth_abstraction = AuthAbstraction(
    supabase_adapter=None,  # Remove Supabase
    auth0_adapter=auth0_adapter  # Add Auth0
)
```

**Step 3: Handlers Don't Change**
```python
# ForwardAuth handler - no changes needed!
user_context = await auth_abstraction.get_user_context(token)  # ✅ Still works

# Handler-level - no changes needed!
security_context = await auth_abstraction.validate_token(token)  # ✅ Still works
```

---

## 📝 Summary

**What We're Doing:**
1. ✅ Add `get_user_context()` to protocol and abstraction
2. ✅ Move ForwardAuth infrastructure logic into `AuthAbstraction.get_user_context()`
3. ✅ Simplify ForwardAuth handler to just call abstraction
4. ✅ Handler-level already follows pattern (no changes needed)

**Result:**
- ✅ ForwardAuth handler: 80+ lines → ~30 lines
- ✅ All infrastructure logic in abstraction
- ✅ Swapping: Change adapter, not handlers
- ✅ Follows Role=What, Service=How, Abstraction=Swappability pattern

