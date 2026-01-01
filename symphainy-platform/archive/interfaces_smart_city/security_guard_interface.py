#!/usr/bin/env python3
"""
Security Guard Interface

Defines the contracts for Security Guard service operations.
This interface matches the existing SecurityGuardService APIs.

WHAT (Interface Role): I define the contracts for authentication and authorization
HOW (Interface Implementation): I provide clear, typed interfaces for consumers
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AuthStatus(str, Enum):
    """Authentication status levels."""
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    INVALID = "invalid"
    LOCKED = "locked"


class AuthLevel(str, Enum):
    """Authorization level levels."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class SessionStatus(str, Enum):
    """Session status levels."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


# Request Models
class AuthenticateUserRequest(BaseModel):
    """Request to authenticate a user."""
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant authentication")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional authentication metadata")


class AuthorizeActionRequest(BaseModel):
    """Request to authorize a user action."""
    user_id: str = Field(..., description="User ID requesting authorization")
    action: str = Field(..., description="Action to authorize")
    resource: str = Field(..., description="Resource being accessed")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Authorization context")


class CreateSessionRequest(BaseModel):
    """Request to create a new user session."""
    user_id: str = Field(..., description="User ID for the session")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant sessions")
    session_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Session metadata")
    expires_in_seconds: Optional[int] = Field(3600, description="Session expiration time in seconds")


class ValidateSessionRequest(BaseModel):
    """Request to validate an existing session."""
    session_id: str = Field(..., description="Session ID to validate")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant validation")


class RevokeSessionRequest(BaseModel):
    """Request to revoke a user session."""
    session_id: str = Field(..., description="Session ID to revoke")
    reason: Optional[str] = Field("user_request", description="Reason for revocation")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant revocation")


# Response Models
class AuthenticateUserResponse(BaseModel):
    """Response for user authentication."""
    success: bool = Field(..., description="Authentication success status")
    user_id: Optional[str] = Field(None, description="Authenticated user ID")
    auth_token: Optional[str] = Field(None, description="Authentication token")
    auth_level: Optional[AuthLevel] = Field(None, description="User authorization level")
    expires_at: Optional[str] = Field(None, description="Token expiration timestamp")
    message: str = Field(..., description="Response message")


class AuthorizeActionResponse(BaseModel):
    """Response for action authorization."""
    success: bool = Field(..., description="Authorization success status")
    authorized: bool = Field(..., description="Whether action is authorized")
    user_id: Optional[str] = Field(None, description="User ID")
    action: Optional[str] = Field(None, description="Action that was authorized")
    resource: Optional[str] = Field(None, description="Resource that was accessed")
    auth_level: Optional[AuthLevel] = Field(None, description="Required authorization level")
    message: str = Field(..., description="Response message")


class CreateSessionResponse(BaseModel):
    """Response for session creation."""
    success: bool = Field(..., description="Session creation success status")
    session_id: Optional[str] = Field(None, description="Created session ID")
    user_id: Optional[str] = Field(None, description="User ID for the session")
    expires_at: Optional[str] = Field(None, description="Session expiration timestamp")
    session_metadata: Optional[Dict[str, Any]] = Field(None, description="Session metadata")
    message: str = Field(..., description="Response message")


class ValidateSessionResponse(BaseModel):
    """Response for session validation."""
    success: bool = Field(..., description="Session validation success status")
    valid: bool = Field(..., description="Whether session is valid")
    session_id: Optional[str] = Field(None, description="Session ID")
    user_id: Optional[str] = Field(None, description="User ID for the session")
    session_status: Optional[SessionStatus] = Field(None, description="Current session status")
    expires_at: Optional[str] = Field(None, description="Session expiration timestamp")
    message: str = Field(..., description="Response message")


class RevokeSessionResponse(BaseModel):
    """Response for session revocation."""
    success: bool = Field(..., description="Session revocation success status")
    session_id: Optional[str] = Field(None, description="Revoked session ID")
    user_id: Optional[str] = Field(None, description="User ID for the session")
    revoked_at: Optional[str] = Field(None, description="Revocation timestamp")
    reason: Optional[str] = Field(None, description="Revocation reason")
    message: str = Field(..., description="Response message")


# Interface Definition
class ISecurityGuard:
    """
    Security Guard Interface

    Defines the contracts for Security Guard service operations.
    This interface matches the existing SecurityGuardService APIs.
    """

    # Authentication
    async def authenticate_user(self, request: AuthenticateUserRequest) -> AuthenticateUserResponse:
        """Authenticate a user with credentials."""
        pass

    # Authorization
    async def authorize_action(self, request: AuthorizeActionRequest) -> AuthorizeActionResponse:
        """Authorize a user action."""
        pass

    # Session Management
    async def create_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        """Create a new user session."""
        pass

    async def validate_session(self, request: ValidateSessionRequest) -> ValidateSessionResponse:
        """Validate an existing session."""
        pass

    async def revoke_session(self, request: RevokeSessionRequest) -> RevokeSessionResponse:
        """Revoke a user session."""
        pass























