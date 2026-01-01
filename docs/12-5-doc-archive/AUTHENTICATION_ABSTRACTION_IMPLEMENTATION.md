# Authentication Abstraction Implementation - Clean Separation

**Date:** December 2024  
**Status:** 📋 **IMPLEMENTATION PLAN**  
**Pattern:** Role=What, Service=How, Abstraction=Swappability

---

## 🎯 Goal

Move all infrastructure logic from handlers into the abstraction, making:
- **Handlers simple:** Just call the abstraction
- **Swapping easy:** Change adapter, not handlers
- **No handler updates:** Infrastructure changes don't touch handlers

---

## 📋 Implementation Plan

### **Step 1: Extend AuthenticationProtocol**

**File:** `foundations/public_works_foundation/abstraction_contracts/authentication_protocol.py`

**Add two distinct methods:**
```python
class AuthenticationProtocol(Protocol):
    """Generic authentication protocol - no technology dependencies."""
    
    # User/Tenant Authentication (Supabase API)
    async def get_user_context(self, token: str) -> SecurityContext:
        """
        Get user/tenant context from authentication service (Supabase API).
        
        This is for user/tenant authentication - requires network call to get
        user context (tenant_id, roles, permissions).
        
        Use case: ForwardAuth endpoint (needs user context in headers)
        """
        ...
    
    # Token Validation (JWKS Local)
    async def validate_token(self, token: str) -> SecurityContext:
        """
        Validate token signature using local verification (JWKS).
        
        This is for token validation - fast, local, no network calls.
        Validates signature, expiration, issuer.
        
        Use case: Handler-level validation (fast token check)
        """
        ...
    
    # Existing methods...
    async def authenticate_user(self, credentials: Dict[str, Any]) -> SecurityContext: ...
    async def refresh_token(self, refresh_token: str) -> SecurityContext: ...
    ...
```

---

### **Step 2: Update AuthAbstraction - Move Infrastructure Logic**

**File:** `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py`

**Key Changes:**
1. **`get_user_context()`** - Handles all Supabase API logic
2. **`validate_token()`** - Handles all JWKS logic
3. **Both return SecurityContext** - Handlers don't need to know the difference

```python
class AuthAbstraction(AuthenticationProtocol):
    """
    Generic authentication abstraction - all infrastructure logic here.
    
    Handlers just call methods - no infrastructure knowledge needed.
    """
    
    async def get_user_context(self, token: str) -> SecurityContext:
        """
        Get user/tenant context via Supabase API.
        
        ALL infrastructure logic here:
        - Calls Supabase API
        - Handles errors
        - Extracts user/tenant/roles
        - Queries database for tenant info
        - Returns SecurityContext
        
        Handler just calls: context = await auth.get_user_context(token)
        """
        try:
            # Infrastructure logic: Supabase API call
            result = await self.supabase.get_user(token)
            
            if not result.get("success"):
                raise AuthenticationError(f"User context failed: {result.get('error')}")
            
            user_data = result.get("user", {})
            
            # Infrastructure logic: Extract user info
            user_id = user_data.get("id")
            email = user_data.get("email")
            
            # Infrastructure logic: Get tenant info from database
            tenant_info = await self._get_user_tenant_info(user_id)
            tenant_id = tenant_info.get("tenant_id")
            roles = tenant_info.get("roles", [])
            permissions = tenant_info.get("permissions", [])
            
            # Return clean SecurityContext - handler doesn't need to know how we got it
            return SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                roles=roles,
                permissions=permissions,
                origin="supabase_user_context"
            )
        except Exception as e:
            self.logger.error(f"❌ User context error: {e}")
            raise AuthenticationError(f"Failed to get user context: {str(e)}")
    
    async def validate_token(self, token: str) -> SecurityContext:
        """
        Validate token signature using local JWKS verification.
        
        ALL infrastructure logic here:
        - JWKS fetching/caching
        - Token signature verification
        - Expiration/issuer validation
        - Claims extraction
        - Returns SecurityContext
        
        Handler just calls: context = await auth.validate_token(token)
        """
        try:
            # Infrastructure logic: Local JWKS verification
            result = await self.supabase.validate_token_local(token)
            
            if not result.get("success"):
                raise AuthenticationError(f"Token validation failed: {result.get('error')}")
            
            # Infrastructure logic: Extract claims from token
            user_data = result.get("user", {})
            user_id = user_data.get("id")
            email = user_data.get("email")
            
            # Infrastructure logic: Get tenant info (still need database query)
            tenant_info = await self._get_user_tenant_info(user_id)
            tenant_id = tenant_info.get("tenant_id")
            roles = tenant_info.get("roles", [])
            permissions = tenant_info.get("permissions", [])
            
            # Return clean SecurityContext - handler doesn't need to know how we got it
            return SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                roles=roles,
                permissions=permissions,
                origin="jwks_token_validation"
            )
        except Exception as e:
            self.logger.error(f"❌ Token validation error: {e}")
            raise AuthenticationError(f"Token validation failed: {str(e)}")
    
    async def _get_user_tenant_info(self, user_id: str) -> Dict[str, Any]:
        """Infrastructure helper - get tenant info from database."""
        # All database query logic here
        # Handler doesn't need to know about this
        ...
```

---

### **Step 3: Simplify ForwardAuth Handler**

**File:** `backend/api/auth_router.py`

**Before (infrastructure logic in handler):**
```python
@router.get("/validate-token")
async def validate_token_forwardauth(request: Request) -> Response:
    # Infrastructure logic: Extract token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return Response(401, "Unauthorized")
    token = auth_header.replace("Bearer ", "")
    
    # Infrastructure logic: Get Supabase config
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    if not supabase_url or not supabase_key:
        return Response(503, "Configuration error")
    
    # Infrastructure logic: Call Supabase API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{supabase_url}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            return Response(401, "Unauthorized")
        user_data = response.json()
    
    # Infrastructure logic: Extract user/tenant info
    user_id = user_data.get("id")
    tenant_id = user_data.get("user_metadata", {}).get("tenant_id")
    # ... more extraction logic ...
    
    # Return headers
    return Response(200, headers={
        "X-User-Id": user_id,
        "X-Tenant-Id": tenant_id,
        ...
    })
```

**After (all logic in abstraction):**
```python
@router.get("/validate-token")
async def validate_token_forwardauth(request: Request) -> Response:
    """
    ForwardAuth endpoint - uses user authentication abstraction.
    
    Handler is simple - just calls abstraction.
    All infrastructure logic moved to AuthAbstraction.get_user_context()
    """
    # Extract token (minimal - just header parsing)
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return Response(401, "Unauthorized: Missing token")
    token = auth_header.replace("Bearer ", "")
    
    try:
        # Get abstraction (dependency injection)
        auth_abstraction = get_auth_abstraction()
        
        # Call abstraction - ALL infrastructure logic is here
        user_context = await auth_abstraction.get_user_context(token)
        
        # Return headers - simple mapping
        return Response(
            status_code=200,
            headers={
                "X-User-Id": user_context.user_id or "",
                "X-Tenant-Id": user_context.tenant_id or "",
                "X-User-Email": user_context.email or "",
                "X-User-Roles": ",".join(user_context.roles),
                "X-User-Permissions": ",".join(user_context.permissions),
                "X-Auth-Origin": user_context.origin or "forwardauth"
            }
        )
    except AuthenticationError as e:
        logger.error(f"ForwardAuth error: {e}")
        return Response(401, f"Unauthorized: {str(e)}")
    except Exception as e:
        logger.error(f"ForwardAuth error: {e}")
        return Response(503, f"Service Unavailable: {str(e)}")
```

---

### **Step 4: Simplify Handler-Level Validation**

**File:** `backend/api/universal_pillar_router.py`

**Before (infrastructure logic in handler):**
```python
async def universal_pillar_handler(request: Request, ...):
    # Infrastructure logic: Extract token
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    
    # Infrastructure logic: Get Security Guard
    security_guard = await get_security_guard()
    auth_abstraction = security_guard.get_auth_abstraction()
    
    # Infrastructure logic: Validate token (JWKS)
    security_context = await auth_abstraction.validate_token(token)
    
    # Infrastructure logic: Extract user/tenant
    user_id = security_context.user_id
    tenant_id = security_context.tenant_id
    # ... more extraction logic ...
```

**After (all logic in abstraction):**
```python
async def universal_pillar_handler(request: Request, ...):
    """
    Handler-level validation - uses token validation abstraction.
    
    Handler is simple - just calls abstraction.
    All infrastructure logic moved to AuthAbstraction.validate_token()
    """
    # Extract token (minimal - just header parsing)
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Unauthorized: Missing token")
    token = auth_header.replace("Bearer ", "")
    
    try:
        # Get abstraction (dependency injection)
        security_guard = await get_security_guard()
        auth_abstraction = security_guard.get_auth_abstraction()
        
        # Call abstraction - ALL infrastructure logic is here
        security_context = await auth_abstraction.validate_token(token)
        
        # Use context - simple mapping
        user_id = security_context.user_id
        tenant_id = security_context.tenant_id
        
        # Continue with request...
    except AuthenticationError as e:
        raise HTTPException(401, f"Unauthorized: {str(e)}")
    except Exception as e:
        raise HTTPException(503, f"Service Unavailable: {str(e)}")
```

---

## ✅ Benefits

### **1. Handlers Are Simple**
- ✅ No infrastructure knowledge needed
- ✅ Just call abstraction methods
- ✅ Clean, readable code

### **2. Swapping Is Easy**
- ✅ Change adapter → abstraction handles it
- ✅ Change Supabase → AuthAbstraction handles it
- ✅ Change JWKS → AuthAbstraction handles it
- ✅ **No handler updates needed**

### **3. No Handler Updates**
- ✅ Infrastructure changes stay in abstraction
- ✅ Adapter changes stay in adapter
- ✅ Handlers never need to change

### **4. Follows Your Pattern**
- ✅ **Role=What:** Authentication (what we need)
- ✅ **Service=How:** AuthAbstraction (how we do it)
- ✅ **Abstraction=Swappability:** Change adapter, not handlers

---

## 🔄 Swapping Example

### **Swap Supabase for Auth0**

**Before (would need handler updates):**
```python
# Would need to update ForwardAuth handler
# Would need to update universal_pillar_router handler
# Would need to update every handler that uses auth
```

**After (just change adapter):**
```python
# Create Auth0Adapter
auth0_adapter = Auth0Adapter(
    domain=config.get("AUTH0_DOMAIN"),
    client_id=config.get("AUTH0_CLIENT_ID")
)

# Update AuthAbstraction to use Auth0Adapter
auth_abstraction = AuthAbstraction(
    supabase_adapter=None,  # Remove Supabase
    auth0_adapter=auth0_adapter  # Add Auth0
)

# Handlers don't change at all!
# ForwardAuth still calls: await auth_abstraction.get_user_context(token)
# Handler still calls: await auth_abstraction.validate_token(token)
```

---

## 📝 Summary

**What We're Doing:**
1. Extend `AuthenticationProtocol` with `get_user_context()` and `validate_token()`
2. Move ALL infrastructure logic into `AuthAbstraction`
3. Simplify handlers to just call abstraction methods
4. Enable easy swapping by changing adapters only

**Result:**
- ✅ Handlers are simple (no infrastructure knowledge)
- ✅ Swapping is easy (change adapter, not handlers)
- ✅ No handler updates needed (infrastructure changes stay in abstraction)
- ✅ Follows your Role=What, Service=How, Abstraction=Swappability pattern


