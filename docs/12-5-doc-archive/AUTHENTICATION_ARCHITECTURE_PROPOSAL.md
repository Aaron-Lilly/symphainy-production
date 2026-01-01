# Authentication Architecture Proposal - Clear Separation of Concerns

**Date:** December 2024  
**Status:** 📋 **PROPOSAL**  
**Priority:** HIGH - Architectural Clarity

---

## 🎯 The Problem

We're confusing two different authentication concerns:

1. **User/Tenant Authentication** (Supabase API)
   - "Is this a valid user?"
   - "What tenant are they in?"
   - "What are their roles/permissions?"
   - **Requires:** Supabase API call to get user/tenant context

2. **Token Validation** (JWKS Local)
   - "Is this token valid?"
   - "Has it been tampered with?"
   - "Is it expired?"
   - **Requires:** Local JWKS verification (no network calls)

**Current Confusion:**
- ForwardAuth endpoint: Making Supabase API calls (user auth) ✅
- Handler-level: Using JWKS (token validation) ✅
- But we're trying to make them use the same abstraction ❌

---

## ✅ Proposed Solution: Two Distinct Abstractions

### **1. User Authentication Abstraction**

**Purpose:** Validate user identity and get user/tenant context

**Methods:**
- `authenticate_user(credentials)` - Login with email/password
- `get_user_context(token)` - Get user/tenant info from Supabase API
- `refresh_user_session(refresh_token)` - Refresh user session

**Implementation:**
- Uses Supabase API calls
- Returns user/tenant/roles/permissions
- Requires network calls (but can be cached)

**Use Cases:**
- ForwardAuth endpoint (needs user/tenant context)
- Login endpoint
- User profile endpoints

---

### **2. Token Validation Abstraction**

**Purpose:** Validate JWT token signature and extract claims

**Methods:**
- `validate_token(token)` - Verify token signature using JWKS
- `extract_token_claims(token)` - Extract user_id, email, etc. from token

**Implementation:**
- Uses local JWKS verification
- No network calls (fast)
- Validates signature, expiration, issuer

**Use Cases:**
- Handler-level token validation
- API request authentication
- Fast token checks

---

## 🔧 Updated Architecture

### **ForwardAuth Endpoint (User/Tenant Auth)**

```python
@router.get("/validate-token")
async def validate_token_forwardauth(request: Request) -> Response:
    """
    ForwardAuth endpoint - validates user/tenant context via Supabase API.
    
    This is for user/tenant authentication, not just token validation.
    We need user context (tenant_id, roles) which requires Supabase API call.
    """
    token = extract_token(request)
    
    # Use User Authentication Abstraction (Supabase API)
    user_auth = get_user_authentication_abstraction()
    user_context = await user_auth.get_user_context(token)
    
    # Return user context in headers for Traefik
    return Response(
        status_code=200,
        headers={
            "X-User-Id": user_context.user_id,
            "X-Tenant-Id": user_context.tenant_id,
            "X-User-Email": user_context.email,
            "X-User-Roles": ",".join(user_context.roles)
        }
    )
```

---

### **Handler-Level Validation (Token Validation)**

```python
async def universal_pillar_handler(request: Request, ...):
    """
    Handler-level token validation - validates token signature via JWKS.
    
    This is for token validation only (fast, no network calls).
    We already have user context from ForwardAuth headers (if available).
    """
    token = extract_token(request)
    
    # Use Token Validation Abstraction (JWKS Local)
    token_validator = get_token_validation_abstraction()
    token_valid = await token_validator.validate_token(token)
    
    if not token_valid:
        raise HTTPException(401, "Invalid token")
    
    # Extract user context from ForwardAuth headers (if available)
    # OR from token claims (if ForwardAuth not used)
    user_id = request.headers.get("X-User-Id") or token_valid.user_id
    tenant_id = request.headers.get("X-Tenant-Id") or token_valid.tenant_id
    
    # Continue with request...
```

---

## 📋 Implementation Plan

### **Step 1: Create Two Separate Abstractions**

**File:** `foundations/public_works_foundation/abstraction_contracts/authentication_protocol.py`

```python
class UserAuthenticationProtocol(Protocol):
    """User/tenant authentication - requires Supabase API calls."""
    
    async def authenticate_user(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Login with email/password - returns user/tenant context."""
        ...
    
    async def get_user_context(self, token: str) -> SecurityContext:
        """Get user/tenant context from Supabase API."""
        ...
    
    async def refresh_user_session(self, refresh_token: str) -> SecurityContext:
        """Refresh user session."""
        ...


class TokenValidationProtocol(Protocol):
    """Token validation - uses local JWKS verification."""
    
    async def validate_token(self, token: str) -> TokenValidationResult:
        """Validate token signature using JWKS (local, fast)."""
        ...
    
    async def extract_token_claims(self, token: str) -> Dict[str, Any]:
        """Extract claims from token (user_id, email, etc.)."""
        ...
```

---

### **Step 2: Update AuthAbstraction to Implement Both**

**File:** `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py`

```python
class AuthAbstraction(UserAuthenticationProtocol, TokenValidationProtocol):
    """
    Unified authentication abstraction that supports both:
    - User authentication (Supabase API)
    - Token validation (JWKS local)
    """
    
    # User Authentication Methods (Supabase API)
    async def get_user_context(self, token: str) -> SecurityContext:
        """Get user/tenant context via Supabase API."""
        result = await self.supabase.get_user(token)  # Network call
        # Extract user/tenant/roles from result
        return SecurityContext(...)
    
    # Token Validation Methods (JWKS Local)
    async def validate_token(self, token: str) -> TokenValidationResult:
        """Validate token signature using JWKS (local, fast)."""
        result = await self.supabase.validate_token_local(token)  # Local JWKS
        return TokenValidationResult(...)
```

---

### **Step 3: Update ForwardAuth to Use User Authentication**

**File:** `backend/api/auth_router.py`

```python
@router.get("/validate-token")
async def validate_token_forwardauth(request: Request) -> Response:
    """ForwardAuth - uses user authentication (Supabase API)."""
    token = extract_token(request)
    
    # Use user authentication (gets user/tenant context)
    user_auth = get_auth_abstraction()  # Returns AuthAbstraction
    user_context = await user_auth.get_user_context(token)  # Supabase API call
    
    return Response(
        status_code=200,
        headers={
            "X-User-Id": user_context.user_id,
            "X-Tenant-Id": user_context.tenant_id,
            ...
        }
    )
```

---

### **Step 4: Update Handler-Level to Use Token Validation**

**File:** `backend/api/universal_pillar_router.py`

```python
async def universal_pillar_handler(request: Request, ...):
    """Handler-level - uses token validation (JWKS local)."""
    token = extract_token(request)
    
    # Use token validation (fast, local)
    token_validator = get_auth_abstraction()  # Returns AuthAbstraction
    token_valid = await token_validator.validate_token(token)  # JWKS local
    
    if not token_valid:
        raise HTTPException(401, "Invalid token")
    
    # Get user context from ForwardAuth headers (if available)
    # OR from token claims (if ForwardAuth not used)
    user_id = request.headers.get("X-User-Id") or token_valid.user_id
    ...
```

---

## 🎯 Benefits

### **1. Clear Separation of Concerns**
- ✅ User authentication = Supabase API (user/tenant context)
- ✅ Token validation = JWKS local (fast, no network)

### **2. No More Confusion**
- ✅ ForwardAuth uses user authentication (correct)
- ✅ Handler-level uses token validation (correct)
- ✅ Each has its own abstraction method

### **3. Better Performance**
- ✅ ForwardAuth: Gets user context once (can be cached)
- ✅ Handler-level: Fast token validation (no network calls)

### **4. Flexible Architecture**
- ✅ Can use ForwardAuth (user context in headers)
- ✅ Can use handler-level only (token validation)
- ✅ Can use both (defense in depth)

---

## 📝 Summary

**Current Problem:**
- Trying to make user authentication and token validation use the same pattern
- ForwardAuth needs user/tenant context (Supabase API)
- Handler-level needs token validation (JWKS local)
- Confusion about which to use when

**Proposed Solution:**
- **User Authentication Abstraction**: `get_user_context()` - Supabase API
- **Token Validation Abstraction**: `validate_token()` - JWKS local
- Clear separation: Use the right abstraction for the right purpose

**Next Steps:**
1. Create two protocol interfaces (UserAuthentication, TokenValidation)
2. Update AuthAbstraction to implement both
3. Update ForwardAuth to use `get_user_context()`
4. Update handler-level to use `validate_token()`
5. Document the distinction clearly

