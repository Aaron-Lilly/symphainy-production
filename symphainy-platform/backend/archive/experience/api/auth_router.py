#!/usr/bin/env python3
"""
Authentication API Router

Handles user authentication and registration.
Routes requests to Security Guard (Smart City) via City Manager.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Request/Response models
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
    error: Optional[str] = None


# Platform orchestrator reference (set by main.py)
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    """Set the platform orchestrator reference."""
    global _platform_orchestrator
    _platform_orchestrator = orchestrator
    logger.info("✅ Auth router connected to platform orchestrator")


def get_city_manager():
    """Get City Manager from platform orchestrator."""
    if not _platform_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Platform not initialized"
        )
    return _platform_orchestrator.managers.get("city_manager")


async def get_security_guard():
    """Get Security Guard service via City Manager (with lazy instantiation)."""
    try:
        city_manager = get_city_manager()
        if not city_manager:
            logger.warning("City Manager not available")
            return None
        
        # Strategy 1: Check City Manager's smart_city_services (where it's registered)
        if hasattr(city_manager, 'smart_city_services'):
            security_guard_info = city_manager.smart_city_services.get("security_guard")
            if security_guard_info and security_guard_info.get("instance"):
                security_guard = security_guard_info.get("instance")
                if security_guard and hasattr(security_guard, 'is_initialized') and security_guard.is_initialized:
                    logger.info("✅ Retrieved Security Guard from City Manager")
                    return security_guard
        
        # Strategy 2: Try lazy instantiation via City Manager
        if hasattr(city_manager, 'service_management_module'):
            logger.info("🔄 Attempting lazy instantiation of Security Guard...")
            try:
                result = await city_manager.service_management_module.manage_smart_city_service("security_guard", "start")
                if result.get("success"):
                    security_guard_info = city_manager.smart_city_services.get("security_guard")
                    if security_guard_info and security_guard_info.get("instance"):
                        security_guard = security_guard_info.get("instance")
                        logger.info("✅ Security Guard lazy-initialized successfully")
                        
                        # Also register in DI container for backward compatibility
                        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
                        if di_container:
                            di_container.service_registry["SecurityGuard"] = security_guard
                            logger.info("✅ Security Guard registered in DI container")
                        
                        return security_guard
                else:
                    logger.warning(f"⚠️ Security Guard lazy initialization failed: {result.get('error')}")
            except Exception as lazy_error:
                logger.warning(f"⚠️ Security Guard lazy initialization error: {lazy_error}")
        
        # Strategy 3: Try DI container (backward compatibility)
        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
        if di_container:
            security_guard = di_container.service_registry.get("SecurityGuard")
            if security_guard:
                logger.info("✅ Retrieved Security Guard from DI container")
                return security_guard
        
        logger.warning("Security Guard not available, using mock auth")
        return None
        
    except Exception as e:
        logger.error(f"Error getting Security Guard: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


@router.post("/register", response_model=AuthResponse)
async def register_user(request: RegisterRequest):
    """
    Register a new user account.
    
    REQUIRES: Security Guard with Supabase authentication (no fallbacks).
    All authentication MUST run through Supabase exclusively.
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
        
        # Use Security Guard for real authentication (Supabase)
        logger.info("Using Security Guard for registration (Supabase)")
        result = await security_guard.register_user({
            "name": request.name,
            "email": request.email,
            "password": request.password
        })
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("message", "Registration failed")
            )
        
        return AuthResponse(
            success=True,
            user={
                "id": result.get("user_id"),
                "email": request.email,
                "name": request.name,
                "tenant_id": result.get("tenant_id", "default_tenant"),
                "roles": result.get("roles", ["user"]),
                "permissions": result.get("permissions", ["read", "write"])
            },
            token=result.get("access_token")
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
    
    REQUIRES: Security Guard with Supabase authentication (no fallbacks).
    All authentication MUST run through Supabase exclusively.
    """
    try:
        logger.info(f"🔐 Login request for: {request.email}")
        
        security_guard = await get_security_guard()
        
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
        
        # Use Security Guard for real authentication (Supabase)
        logger.info("Using Security Guard for login (Supabase)")
        result = await security_guard.authenticate_user({
            "email": request.email,
            "password": request.password
        })
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("message", "Authentication failed")
            )
        
        return AuthResponse(
            success=True,
            user={
                "id": result.get("user_id"),
                "email": request.email,
                "tenant_id": result.get("tenant_id", "default_tenant"),
                "roles": result.get("roles", ["user"]),
                "permissions": result.get("permissions", [])
            },
            token=result.get("access_token")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
async def logout_user(token: str = None):
    """
    Logout user and destroy session.
    
    For MVP: Returns success (session cleanup is optional).
    Production: Destroys session via Security Guard/Traffic Cop.
    """
    try:
        logger.info("👋 Logout request")
        
        # For MVP: Just return success
        # Production would destroy session here
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/health")
async def auth_health():
    """Auth service health check."""
    security_guard = await get_security_guard()
    
    return {
        "status": "healthy",
        "service": "authentication",
        "security_guard_available": security_guard is not None,
        "mode": "production" if security_guard else "mock"
    }


