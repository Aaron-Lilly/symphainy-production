#!/usr/bin/env python3
"""
Authentication API Router

Exposes authentication endpoints that the frontend can call.
Routes requests to Security Guard (Smart City) via Experience Manager.
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

# Store reference to platform orchestrator (will be set by main.py)
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    """Set the platform orchestrator reference."""
    global _platform_orchestrator
    _platform_orchestrator = orchestrator

async def _get_security_guard():
    """Get Security Guard service."""
    if not _platform_orchestrator:
        raise HTTPException(status_code=500, detail="Platform not initialized")
    
    # Get via DI Container
    security_guard = _platform_orchestrator.infrastructure_services["di_container"].service_registry.get("SecurityGuard")
    if not security_guard:
        logger.warning("Security Guard not available, using mock auth")
        return None
    return security_guard


@router.post("/register", response_model=AuthResponse)
async def register_user(request: RegisterRequest):
    """
    Register a new user account.
    
    For MVP: Creates a session and returns a mock token.
    Production: Would create actual user in database via Security Guard.
    """
    try:
        logger.info(f"Registration request for: {request.email}")
        
        security_guard = await _get_security_guard()
        
        if security_guard:
            # Use Security Guard for real authentication
            result = await security_guard.register_user({
                "name": request.name,
                "email": request.email,
                "password": request.password
            })
            
            if result.get("success"):
                return AuthResponse(
                    success=True,
                    user={
                        "id": result.get("user_id"),
                        "email": request.email,
                        "name": request.name
                    },
                    token=result.get("access_token")
                )
        
        # MVP Fallback: Mock authentication for testing
        logger.warning("Using mock authentication for MVP")
        return AuthResponse(
            success=True,
            user={
                "id": f"user_{request.email.split('@')[0]}",
                "email": request.email,
                "name": request.name,
                "tenant_id": "default_tenant",
                "roles": ["user"],
                "permissions": ["read", "write"]
            },
            token=f"mock_token_{request.email}"
        )
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(request: LoginRequest):
    """
    Authenticate user and create session.
    
    For MVP: Returns a mock session.
    Production: Would validate credentials via Security Guard.
    """
    try:
        logger.info(f"Login request for: {request.email}")
        
        security_guard = await _get_security_guard()
        
        if security_guard:
            # Use Security Guard for real authentication
            result = await security_guard.authenticate_user({
                "username": request.email,
                "password": request.password,
                "authentication_method": "password"
            })
            
            if result.get("success"):
                return AuthResponse(
                    success=True,
                    user={
                        "id": result.get("user_id"),
                        "email": request.email
                    },
                    token=result.get("access_token")
                )
        
        # MVP Fallback: Mock authentication
        logger.warning("Using mock authentication for MVP")
        return AuthResponse(
            success=True,
            user={
                "id": f"user_{request.email.split('@')[0]}",
                "email": request.email,
                "tenant_id": "default_tenant",
                "roles": ["user"]
            },
            token=f"mock_token_{request.email}"
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/logout")
async def logout_user():
    """Logout user and destroy session."""
    try:
        # For MVP: Just return success
        # Production: Would destroy session via Security Guard/Traffic Cop
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


