#!/usr/bin/env python3
"""
Authentication Router

FastAPI router for authentication endpoints (login, register).
Uses Security Guard service for authentication via Supabase.

WHAT: Provides REST API endpoints for user authentication
HOW: FastAPI router that delegates to Security Guard service
"""

from fastapi import APIRouter, HTTPException, status, Request, Response
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.get("/test")
async def test_auth_router():
    """Test endpoint to verify auth router is accessible."""
    logger.info("✅ [test_auth_router] Test endpoint called - auth router is working!")
    return {"status": "ok", "message": "Auth router is accessible"}


# Request/Response Models
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    success: bool
    user: Optional[Dict[str, Any]] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None  # ✅ NEW: Refresh token for token refresh
    message: str
    error: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Global state for Security Guard access
_security_guard_instance = None
_city_manager = None

def set_city_manager(city_manager: Any):
    """Set City Manager (called during router registration)."""
    global _city_manager
    _city_manager = city_manager
    logger.info("✅ City Manager set in auth router")

async def get_security_guard():
    """
    Get Security Guard service instance via proper service discovery.
    
    Security Guard is a Smart City service, discoverable via:
    1. Curator Foundation (primary - service discovery)
    2. City Manager (fallback - Smart City realm manager)
    
    Platform Gateway should NEVER be used - "platform" realm doesn't have access to "auth" abstraction.
    This is a security boundary that must be respected.
    """
    global _security_guard_instance, _city_manager
    
    # Use cached instance if available
    if _security_guard_instance:
        return _security_guard_instance
    
    # 1. Try Curator Foundation (primary - service discovery)
    logger.info("🔍 [get_security_guard] Step 1: Trying Curator...")
    try:
        from utilities.service_discovery.curator import Curator
        curator = Curator()
        logger.info("🔍 [get_security_guard] Curator instance created, calling get_service('SecurityGuardService')...")
        security_guard = await curator.get_service("SecurityGuardService")
        logger.info(f"🔍 [get_security_guard] Curator.get_service returned: {security_guard is not None}")
        if security_guard:
            _security_guard_instance = security_guard
            logger.info("✅ Security Guard retrieved via Curator Foundation")
            return security_guard
    except Exception as e:
        logger.warning(f"⚠️ Curator lookup failed: {e}", exc_info=True)
    
    # 2. Try City Manager (fallback - Smart City realm manager)
    logger.info(f"🔍 [get_security_guard] Step 2: Checking City Manager (available: {_city_manager is not None})...")
    if _city_manager:
        try:
            logger.info(f"🔍 [get_security_guard] City Manager has smart_city_services: {hasattr(_city_manager, 'smart_city_services')}")
            # Check if Security Guard is already in City Manager's registry
            if hasattr(_city_manager, 'smart_city_services'):
                service_info = _city_manager.smart_city_services.get("security_guard")
                logger.info(f"🔍 [get_security_guard] City Manager registry lookup: service_info={service_info is not None}, has_instance={service_info and service_info.get('instance') is not None if service_info else False}")
                if service_info and service_info.get("instance"):
                    security_guard = service_info["instance"]
                    _security_guard_instance = security_guard
                    logger.info("✅ Security Guard retrieved via City Manager")
                    return security_guard
            
            # Bootstrap Security Guard via City Manager if needed
            logger.info(f"🔍 [get_security_guard] Attempting bootstrap via City Manager...")
            if hasattr(_city_manager, 'realm_orchestration_module'):
                logger.info("🔍 [get_security_guard] City Manager has realm_orchestration_module, calling orchestrate_realm_startup...")
                result = await _city_manager.realm_orchestration_module.orchestrate_realm_startup(
                    services=["security_guard"]
                )
                logger.info(f"🔍 [get_security_guard] Bootstrap result: {result}")
                if result and result.get("success"):
                    service_info = _city_manager.smart_city_services.get("security_guard")
                    if service_info and service_info.get("instance"):
                        security_guard = service_info["instance"]
                        _security_guard_instance = security_guard
                        logger.info("✅ Security Guard bootstrapped via City Manager")
                        return security_guard
        except Exception as e:
            logger.warning(f"⚠️ City Manager lookup failed: {e}", exc_info=True)
    else:
        logger.warning("⚠️ City Manager not available")
    
    logger.error("❌ Security Guard service not available")
    return None


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest):
    """
    Register a new user account.
    
    Uses Security Guard service which delegates to Supabase Auth.
    """
    try:
        logger.info(f"📝 Registration request for: {request.email}")
        
        security_guard = await get_security_guard()
        
        if not security_guard:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Security Guard service not available. Authentication requires Supabase."
            )
        
        if not hasattr(security_guard, 'register_user'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User registration not available. Security Guard missing register_user method."
            )
        
        # Use Security Guard for registration (Supabase)
        logger.info("Using Security Guard for registration (Supabase)")
        result = await security_guard.register_user({
            "name": request.name,
            "email": request.email,
            "password": request.password
        })
        
        if not result.get("success"):
            error_message = result.get("message", "Registration failed")
            logger.warning(f"Registration failed for {request.email}: {error_message}")
            return AuthResponse(
                success=False,
                message=error_message,
                error=error_message
            )
        
        # Extract user data from result
        user_id = result.get("user_id")
        access_token = result.get("access_token")
        tenant_id = result.get("tenant_id", "default_tenant")
        roles = result.get("roles", ["user"])
        permissions = result.get("permissions", ["read", "write"])
        
        logger.info(f"✅ Registration successful for: {request.email} (user_id: {user_id})")
        
        return AuthResponse(
            success=True,
            user={
                "user_id": user_id,
                "email": request.email,
                "full_name": request.name,
                "tenant_id": tenant_id,
                "roles": roles,
                "permissions": permissions
            },
            token=access_token,
            message="Registration successful! Welcome to Symphainy!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(request: LoginRequest):
    """
    Authenticate user and create session.
    
    Uses Security Guard service which delegates to Supabase Auth.
    """
    try:
        logger.info(f"🔐 [login_user] ENTRY: Login request received for: {request.email}")
        logger.info(f"🔍 [login_user] Starting get_security_guard()...")
        
        try:
            security_guard = await get_security_guard()
            logger.info(f"🔍 [login_user] get_security_guard() returned: {security_guard is not None} (type: {type(security_guard).__name__ if security_guard else 'None'})")
        except Exception as e:
            logger.error(f"❌ [login_user] get_security_guard() raised exception: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Security Guard service lookup failed: {str(e)}"
            )
        
        if not security_guard:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Security Guard service not available. Authentication requires Supabase."
            )
        
        if not hasattr(security_guard, 'authenticate_user'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User authentication not available. Security Guard missing authenticate_user method."
            )
        
        # Use Security Guard for authentication (Supabase)
        # ✅ Enhanced: Generate workflow_id at router level for correlation
        import uuid
        workflow_id = str(uuid.uuid4())
        logger.info(f"Using Security Guard for login (Supabase) - workflow_id: {workflow_id}")
        result = await security_guard.authenticate_user({
            "email": request.email,
            "password": request.password,
            "workflow_id": workflow_id  # ✅ Pass workflow_id to Security Guard
        })
        
        if not result.get("success"):
            error_message = result.get("message", "Authentication failed")
            logger.warning(f"Login failed for {request.email}: {error_message}")
            return AuthResponse(
                success=False,
                message=error_message,
                error=error_message
            )
        
        # Extract user data from result
        user_id = result.get("user_id")
        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")  # ✅ NEW: Extract refresh_token
        tenant_id = result.get("tenant_id", "default_tenant")
        roles = result.get("roles", ["user"])
        permissions = result.get("permissions", ["read", "write"])
        email = result.get("email", request.email)
        name = result.get("name", "")
        
        logger.info(f"✅ Login successful for: {request.email} (user_id: {user_id})")
        
        return AuthResponse(
            success=True,
            user={
                "user_id": user_id,
                "email": email,
                "full_name": name,
                "tenant_id": tenant_id,
                "roles": roles,
                "permissions": permissions
            },
            token=access_token,
            refresh_token=refresh_token,  # ✅ NEW: Include refresh_token in response
            message="Login successful!"
        )
        
    except HTTPException:
        logger.warning(f"⚠️ [login_user] HTTPException raised, re-raising")
        raise
    except Exception as e:
        logger.error(f"❌ [login_user] UNHANDLED EXCEPTION: {type(e).__name__}: {e}", exc_info=True)
        import traceback
        logger.error(f"❌ [login_user] Full traceback:\n{traceback.format_exc()}")
        # Add context to error message for better debugging
        error_msg = str(e)
        if "Security Guard" in error_msg or "security_guard" in error_msg.lower():
            error_detail = f"Security Guard error: {error_msg}"
        elif "Supabase" in error_msg or "supabase" in error_msg.lower():
            error_detail = f"Supabase authentication error: {error_msg}"
        else:
            error_detail = f"Login failed: {error_msg}"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    
    Uses Security Guard service which delegates to Supabase Auth.
    Returns new access_token and refresh_token.
    """
    try:
        logger.info(f"🔄 [refresh_token] Token refresh request received")
        
        security_guard = await get_security_guard()
        
        if not security_guard:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Security Guard service not available. Token refresh requires Supabase."
            )
        
        if not hasattr(security_guard, 'get_auth_abstraction'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Token refresh not available. Security Guard missing auth abstraction."
            )
        
        auth_abstraction = security_guard.get_auth_abstraction()
        
        if not auth_abstraction:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth abstraction not available. Token refresh requires Supabase."
            )
        
        # Use AuthAbstraction.refresh_token (delegates to Supabase)
        logger.info("Using AuthAbstraction for token refresh (Supabase)")
        security_context = await auth_abstraction.refresh_token(request.refresh_token)
        
        # Get new tokens from Supabase adapter
        new_access_token = None
        new_refresh_token = None
        try:
            if hasattr(auth_abstraction, 'supabase'):
                # Call refresh_session to get new tokens
                refresh_result = await auth_abstraction.supabase.refresh_session(request.refresh_token)
                if refresh_result.get("success"):
                    new_access_token = refresh_result.get("access_token")
                    new_refresh_token = refresh_result.get("refresh_token")
                    logger.info(f"✅ Retrieved new tokens from Supabase")
        except Exception as e:
            logger.warning(f"Could not get new tokens from Supabase adapter: {e}")
        
        logger.info(f"✅ Token refresh successful for user: {security_context.user_id}")
        
        return AuthResponse(
            success=True,
            user={
                "user_id": security_context.user_id,
                "email": security_context.email or "",
                "tenant_id": security_context.tenant_id or "",
                "roles": security_context.roles or [],
                "permissions": security_context.permissions or []
            },
            token=new_access_token,
            refresh_token=new_refresh_token,  # ✅ NEW: Return new refresh_token
            message="Token refreshed successfully!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh error: {e}", exc_info=True)
        error_msg = str(e)
        if "Token refresh failed" in error_msg or "expired" in error_msg.lower():
            return AuthResponse(
                success=False,
                message="Token refresh failed. Please log in again.",
                error=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token refresh failed: {error_msg}"
            )


@router.get("/validate-token")
async def validate_token_forwardauth(request: Request) -> Response:
    """
    ForwardAuth endpoint for Traefik.
    
    Validates Supabase JWT token and returns user context in headers.
    Traefik will forward these headers to backend services.
    
    Handler is simple - just calls abstraction.
    All infrastructure logic moved to AuthAbstraction.get_user_context()
    
    Returns:
        - 200 OK with user context headers if token is valid
        - 401 Unauthorized if token is invalid or missing
        - 503 Service Unavailable if authentication service unavailable
    """
    try:
        # Extract token (minimal - just header parsing)
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.debug("ForwardAuth: Missing or invalid Authorization header")
            return Response(status_code=401, content="Unauthorized: Missing or invalid token")
        
        token = auth_header.replace("Bearer ", "")
        
        # Get abstraction (dependency injection)
        security_guard = await get_security_guard()
        
        if not security_guard or not hasattr(security_guard, 'get_auth_abstraction'):
            logger.error("ForwardAuth: Security Guard not available")
            return Response(status_code=503, content="Service Unavailable: Security Guard not available")
        
        auth_abstraction = security_guard.get_auth_abstraction()
        
        if not auth_abstraction:
            logger.error("ForwardAuth: Auth abstraction not available")
            return Response(status_code=503, content="Service Unavailable: Auth abstraction not available")
        
        # FIX: Use validate_token (local JWKS) instead of get_user_context (network call)
        # ForwardAuth needs to be fast - local JWKS validation is much faster than network calls
        logger.info("🔐 [ForwardAuth] Starting token validation (JWKS)...")
        user_context = await auth_abstraction.validate_token(token)
        logger.info(f"✅ [ForwardAuth] Token validated: user={user_context.user_id}, tenant={user_context.tenant_id}")
        
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
        
    except Exception as e:
        # Check if it's an authentication error (from abstraction)
        error_msg = str(e)
        if "User context failed" in error_msg or "Failed to get user context" in error_msg:
            logger.error(f"ForwardAuth: Authentication error: {e}")
            return Response(status_code=401, content=f"Unauthorized: {error_msg}")
        else:
            logger.error(f"ForwardAuth: Error: {e}", exc_info=True)
            return Response(status_code=503, content=f"Service Unavailable: {error_msg}")

