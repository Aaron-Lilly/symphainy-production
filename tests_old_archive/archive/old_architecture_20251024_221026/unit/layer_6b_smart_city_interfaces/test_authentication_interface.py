#!/usr/bin/env python3
"""
Tests for Authentication Interface.

Tests the authentication interface data models and concrete implementations
for Smart City authentication operations.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add the symphainy-platform path
platform_path = project_root / "symphainy-source" / "symphainy-platform"
sys.path.insert(0, str(platform_path))

from backend.smart_city.interfaces.authentication_interface import (
    AuthProvider,
    UserRole,
    UserProfile,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    PermissionCheck,
    IAuthentication
)
from tests.unit.layer_5b_smart_city_interfaces.test_base import SmartCityInterfacesTestBase


class TestAuthProvider:
    """Test AuthProvider enum."""
    
    def test_auth_provider_values(self):
        """Test auth provider enum values."""
        assert AuthProvider.SUPABASE.value == "supabase"
        assert AuthProvider.LOCAL.value == "local"
        assert AuthProvider.OAUTH.value == "oauth"
        assert AuthProvider.LDAP.value == "ldap"


class TestUserRole:
    """Test UserRole enum."""
    
    def test_user_role_values(self):
        """Test user role enum values."""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.USER.value == "user"
        assert UserRole.GUEST.value == "guest"
        assert UserRole.SERVICE.value == "service"


class TestUserProfile:
    """Test UserProfile data model."""
    
    def test_user_profile_creation(self):
        """Test creating a user profile."""
        user_profile = UserProfile(
            user_id="user_001",
            email="user@testorg.com",
            username="testuser",
            full_name="John Doe",
            role=UserRole.USER,
            provider=AuthProvider.SUPABASE,
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            last_login=datetime(2024, 1, 1, 7, 30, 0),
            is_active=True,
            metadata={"department": "analytics", "location": "office"}
        )
        
        assert user_profile.user_id == "user_001"
        assert user_profile.email == "user@testorg.com"
        assert user_profile.username == "testuser"
        assert user_profile.full_name == "John Doe"
        assert user_profile.role == UserRole.USER
        assert user_profile.provider == AuthProvider.SUPABASE
        assert user_profile.created_at == datetime(2024, 1, 1, 0, 0, 0)
        assert user_profile.last_login == datetime(2024, 1, 1, 7, 30, 0)
        assert user_profile.is_active is True
        assert user_profile.metadata["department"] == "analytics"
        assert user_profile.metadata["location"] == "office"
    
    def test_user_profile_defaults(self):
        """Test user profile with default values."""
        user_profile = UserProfile(
            user_id="user_002",
            email="user2@testorg.com",
            username="testuser2",
            full_name="Jane Doe",
            role=UserRole.ADMIN,
            provider=AuthProvider.LOCAL,
            created_at=datetime(2024, 1, 1, 0, 0, 0)
        )
        
        assert user_profile.user_id == "user_002"
        assert user_profile.email == "user2@testorg.com"
        assert user_profile.username == "testuser2"
        assert user_profile.full_name == "Jane Doe"
        assert user_profile.role == UserRole.ADMIN
        assert user_profile.provider == AuthProvider.LOCAL
        assert user_profile.last_login is None
        assert user_profile.is_active is True
        assert user_profile.metadata == {}


class TestLoginRequest:
    """Test LoginRequest data model."""
    
    def test_login_request_creation(self):
        """Test creating a login request."""
        login_request = LoginRequest(
            email="user@testorg.com",
            password="password123",
            provider=AuthProvider.SUPABASE,
            remember_me=True,
            metadata={"device_id": "device_001"}
        )
        
        assert login_request.email == "user@testorg.com"
        assert login_request.password == "password123"
        assert login_request.provider == AuthProvider.SUPABASE
        assert login_request.remember_me is True
        assert login_request.metadata["device_id"] == "device_001"
    
    def test_login_request_defaults(self):
        """Test login request with default values."""
        login_request = LoginRequest(
            email="user@testorg.com",
            password="password123"
        )
        
        assert login_request.email == "user@testorg.com"
        assert login_request.password == "password123"
        assert login_request.provider == AuthProvider.SUPABASE
        assert login_request.remember_me is False
        assert login_request.metadata == {}


class TestLoginResponse:
    """Test LoginResponse data model."""
    
    def test_login_response_success(self):
        """Test creating a successful login response."""
        user_profile = UserProfile(
            user_id="user_001",
            email="user@testorg.com",
            username="testuser",
            full_name="John Doe",
            role=UserRole.USER,
            provider=AuthProvider.SUPABASE,
            created_at=datetime(2024, 1, 1, 0, 0, 0)
        )
        
        login_response = LoginResponse(
            success=True,
            user_id="user_001",
            access_token="access_token_123",
            refresh_token="refresh_token_456",
            expires_at=datetime(2024, 1, 1, 8, 0, 0),
            user_profile=user_profile
        )
        
        assert login_response.success is True
        assert login_response.user_id == "user_001"
        assert login_response.access_token == "access_token_123"
        assert login_response.refresh_token == "refresh_token_456"
        assert login_response.expires_at == datetime(2024, 1, 1, 8, 0, 0)
        assert login_response.user_profile == user_profile
        assert login_response.error_message is None
    
    def test_login_response_failure(self):
        """Test creating a failed login response."""
        login_response = LoginResponse(
            success=False,
            user_id="",
            access_token="",
            refresh_token="",
            expires_at=datetime(2024, 1, 1, 0, 0, 0),
            user_profile=None,
            error_message="Invalid credentials"
        )
        
        assert login_response.success is False
        assert login_response.user_id == ""
        assert login_response.access_token == ""
        assert login_response.refresh_token == ""
        assert login_response.user_profile is None
        assert login_response.error_message == "Invalid credentials"


class TestRegisterRequest:
    """Test RegisterRequest data model."""
    
    def test_register_request_creation(self):
        """Test creating a register request."""
        register_request = RegisterRequest(
            email="newuser@testorg.com",
            password="password123",
            username="newuser",
            full_name="New User",
            provider=AuthProvider.SUPABASE,
            metadata={"invite_code": "INVITE123"}
        )
        
        assert register_request.email == "newuser@testorg.com"
        assert register_request.password == "password123"
        assert register_request.username == "newuser"
        assert register_request.full_name == "New User"
        assert register_request.provider == AuthProvider.SUPABASE
        assert register_request.metadata["invite_code"] == "INVITE123"


class TestRegisterResponse:
    """Test RegisterResponse data model."""
    
    def test_register_response_success(self):
        """Test creating a successful register response."""
        user_profile = UserProfile(
            user_id="user_003",
            email="newuser@testorg.com",
            username="newuser",
            full_name="New User",
            role=UserRole.USER,
            provider=AuthProvider.SUPABASE,
            created_at=datetime(2024, 1, 1, 0, 0, 0)
        )
        
        register_response = RegisterResponse(
            success=True,
            user_id="user_003",
            user_profile=user_profile
        )
        
        assert register_response.success is True
        assert register_response.user_id == "user_003"
        assert register_response.user_profile == user_profile
        assert register_response.error_message is None


class TestPermissionCheck:
    """Test PermissionCheck data model."""
    
    def test_permission_check_creation(self):
        """Test creating a permission check."""
        permission_check = PermissionCheck(
            user_id="user_001",
            resource="analytics_dashboard",
            action="read",
            context={"tenant_id": "tenant_001", "feature": "basic_analytics"}
        )
        
        assert permission_check.user_id == "user_001"
        assert permission_check.resource == "analytics_dashboard"
        assert permission_check.action == "read"
        assert permission_check.context["tenant_id"] == "tenant_001"
        assert permission_check.context["feature"] == "basic_analytics"


class TestAuthenticationInterface(SmartCityInterfacesTestBase):
    """Test IAuthentication implementation."""
    
    @pytest.mark.asyncio
    async def test_authentication_interface_initialization(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test authentication interface initialization."""
        # Create a concrete implementation for testing
        class TestAuthenticationInterface(IAuthentication):
            def __init__(self):
                self.users = {}
                self.tokens = {}
            
            async def login(self, request: LoginRequest, user_context=None) -> LoginResponse:
                # Mock authentication logic
                user_data = self.users.get(request.email)
                if user_data and user_data.get("password") == request.password:
                    user_profile = UserProfile(
                        user_id=user_data["user_id"],
                        email=user_data["email"],
                        username=user_data["username"],
                        full_name=user_data["full_name"],
                        role=user_data["role"],
                        provider=request.provider,
                        created_at=user_data["created_at"],
                        last_login=datetime.utcnow(),
                        is_active=True,
                        metadata=user_data.get("metadata", {})
                    )
                    
                    return LoginResponse(
                        success=True,
                        user_id=user_data["user_id"],
                        access_token=f"access_token_{user_data['user_id']}",
                        refresh_token=f"refresh_token_{user_data['user_id']}",
                        expires_at=datetime.utcnow().replace(hour=8),
                        user_profile=user_profile
                    )
                else:
                    return LoginResponse(
                        success=False,
                        user_id="",
                        access_token="",
                        refresh_token="",
                        expires_at=datetime.utcnow(),
                        user_profile=None,
                        error_message="Invalid credentials"
                    )
            
            async def register(self, request: RegisterRequest, user_context=None) -> RegisterResponse:
                if request.email in self.users:
                    return RegisterResponse(
                        success=False,
                        user_id="",
                        user_profile=None,
                        error_message="User already exists"
                    )
                
                user_id = f"user_{len(self.users) + 1}"
                user_profile = UserProfile(
                    user_id=user_id,
                    email=request.email,
                    username=request.username,
                    full_name=request.full_name,
                    role=UserRole.USER,
                    provider=request.provider,
                    created_at=datetime.utcnow(),
                    is_active=True,
                    metadata=request.metadata or {}
                )
                
                self.users[request.email] = {
                    "user_id": user_id,
                    "email": request.email,
                    "username": request.username,
                    "full_name": request.full_name,
                    "password": request.password,
                    "role": UserRole.USER,
                    "created_at": datetime.utcnow(),
                    "metadata": request.metadata or {}
                }
                
                return RegisterResponse(
                    success=True,
                    user_id=user_id,
                    user_profile=user_profile
                )
            
            async def logout(self, user_id: str, user_context=None) -> Dict[str, Any]:
                return {"status": "logged_out", "user_id": user_id, "message": "User logged out successfully"}
            
            async def refresh_token(self, refresh_token: str, user_context=None) -> Dict[str, Any]:
                for user_data in self.users.values():
                    if f"refresh_token_{user_data['user_id']}" == refresh_token:
                        return {
                            "success": True,
                            "access_token": f"new_access_token_{user_data['user_id']}",
                            "refresh_token": f"new_refresh_token_{user_data['user_id']}",
                            "expires_at": datetime.utcnow().replace(hour=8)
                        }
                
                return {
                    "success": False,
                    "error_message": "Invalid refresh token"
                }
            
            async def validate_token(self, access_token: str, user_context=None) -> Dict[str, Any]:
                if access_token.startswith("access_token_"):
                    user_id = access_token.replace("access_token_", "")
                    return {
                        "valid": True,
                        "user_id": user_id,
                        "expires_at": datetime.utcnow().replace(hour=8)
                    }
                return {"valid": False, "error_message": "Invalid token"}
            
            async def get_user_profile(self, user_id: str, user_context=None) -> Optional[UserProfile]:
                for user_data in self.users.values():
                    if user_data["user_id"] == user_id:
                        return UserProfile(
                            user_id=user_data["user_id"],
                            email=user_data["email"],
                            username=user_data["username"],
                            full_name=user_data["full_name"],
                            role=user_data["role"],
                            provider=AuthProvider.SUPABASE,
                            created_at=user_data["created_at"],
                            is_active=True,
                            metadata=user_data.get("metadata", {})
                        )
                return None
            
            async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any], user_context=None) -> Dict[str, Any]:
                for user_data in self.users.values():
                    if user_data["user_id"] == user_id:
                        user_data.update(profile_data)
                        return {"status": "updated", "user_id": user_id, "message": "Profile updated successfully"}
                return {"status": "not_found", "user_id": user_id, "message": "User not found"}
            
            async def check_permission(self, check: PermissionCheck, user_context=None) -> bool:
                # Mock permission check
                return check.user_id in [user_data["user_id"] for user_data in self.users.values()]
            
            async def grant_permission(self, user_id: str, resource: str, action: str, user_context=None) -> Dict[str, Any]:
                return {"status": "granted", "user_id": user_id, "resource": resource, "action": action}
            
            async def revoke_permission(self, user_id: str, resource: str, action: str, user_context=None) -> Dict[str, Any]:
                return {"status": "revoked", "user_id": user_id, "resource": resource, "action": action}
            
            async def list_user_permissions(self, user_id: str, user_context=None) -> List[Dict[str, str]]:
                return [{"resource": "analytics", "action": "read"}]
            
            async def change_password(self, user_id: str, old_password: str, new_password: str, user_context=None) -> Dict[str, Any]:
                return {"status": "changed", "user_id": user_id, "message": "Password changed successfully"}
            
            async def reset_password(self, email: str, user_context=None) -> Dict[str, Any]:
                return {"status": "reset_initiated", "email": email, "message": "Password reset email sent"}
            
            async def get_auth_analytics(self, user_context=None) -> Dict[str, Any]:
                return {
                    "total_users": len(self.users),
                    "active_users": len(self.users),
                    "login_attempts": 100,
                    "successful_logins": 95
                }
        
        interface = TestAuthenticationInterface()
        
        assert interface is not None
        assert hasattr(interface, 'login')
        assert hasattr(interface, 'register')
        assert hasattr(interface, 'logout')
        assert hasattr(interface, 'refresh_token')
        assert hasattr(interface, 'validate_token')
    
    @pytest.mark.asyncio
    async def test_authentication_interface_operations(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test authentication interface operations."""
        class TestAuthenticationInterface(IAuthentication):
            def __init__(self):
                self.users = {}
                self.tokens = {}
            
            async def login(self, request: LoginRequest, user_context=None) -> LoginResponse:
                user_data = self.users.get(request.email)
                if user_data and user_data.get("password") == request.password:
                    user_profile = UserProfile(
                        user_id=user_data["user_id"],
                        email=user_data["email"],
                        username=user_data["username"],
                        full_name=user_data["full_name"],
                        role=user_data["role"],
                        provider=request.provider,
                        created_at=user_data["created_at"],
                        last_login=datetime.utcnow(),
                        is_active=True,
                        metadata=user_data.get("metadata", {})
                    )
                    
                    return LoginResponse(
                        success=True,
                        user_id=user_data["user_id"],
                        access_token=f"access_token_{user_data['user_id']}",
                        refresh_token=f"refresh_token_{user_data['user_id']}",
                        expires_at=datetime.utcnow().replace(hour=8),
                        user_profile=user_profile
                    )
                else:
                    return LoginResponse(
                        success=False,
                        user_id="",
                        access_token="",
                        refresh_token="",
                        expires_at=datetime.utcnow(),
                        user_profile=None,
                        error_message="Invalid credentials"
                    )
            
            async def register(self, request: RegisterRequest, user_context=None) -> RegisterResponse:
                if request.email in self.users:
                    return RegisterResponse(
                        success=False,
                        user_id="",
                        user_profile=None,
                        error_message="User already exists"
                    )
                
                user_id = f"user_{len(self.users) + 1}"
                user_profile = UserProfile(
                    user_id=user_id,
                    email=request.email,
                    username=request.username,
                    full_name=request.full_name,
                    role=UserRole.USER,
                    provider=request.provider,
                    created_at=datetime.utcnow(),
                    is_active=True,
                    metadata=request.metadata or {}
                )
                
                self.users[request.email] = {
                    "user_id": user_id,
                    "email": request.email,
                    "username": request.username,
                    "full_name": request.full_name,
                    "password": request.password,
                    "role": UserRole.USER,
                    "created_at": datetime.utcnow(),
                    "metadata": request.metadata or {}
                }
                
                return RegisterResponse(
                    success=True,
                    user_id=user_id,
                    user_profile=user_profile
                )
            
            async def logout(self, user_id: str, user_context=None) -> Dict[str, Any]:
                return {"status": "logged_out", "user_id": user_id, "message": "User logged out successfully"}
            
            async def refresh_token(self, refresh_token: str, user_context=None) -> Dict[str, Any]:
                for user_data in self.users.values():
                    if f"refresh_token_{user_data['user_id']}" == refresh_token:
                        return {
                            "success": True,
                            "access_token": f"new_access_token_{user_data['user_id']}",
                            "refresh_token": f"new_refresh_token_{user_data['user_id']}",
                            "expires_at": datetime.utcnow().replace(hour=8)
                        }
                
                return {
                    "success": False,
                    "error_message": "Invalid refresh token"
                }
            
            async def validate_token(self, access_token: str, user_context=None) -> Dict[str, Any]:
                if access_token.startswith("access_token_"):
                    user_id = access_token.replace("access_token_", "")
                    return {
                        "valid": True,
                        "user_id": user_id,
                        "expires_at": datetime.utcnow().replace(hour=8)
                    }
                return {"valid": False, "error_message": "Invalid token"}
            
            async def get_user_profile(self, user_id: str, user_context=None) -> Optional[UserProfile]:
                for user_data in self.users.values():
                    if user_data["user_id"] == user_id:
                        return UserProfile(
                            user_id=user_data["user_id"],
                            email=user_data["email"],
                            username=user_data["username"],
                            full_name=user_data["full_name"],
                            role=user_data["role"],
                            provider=AuthProvider.SUPABASE,
                            created_at=user_data["created_at"],
                            is_active=True,
                            metadata=user_data.get("metadata", {})
                        )
                return None
            
            async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any], user_context=None) -> Dict[str, Any]:
                for user_data in self.users.values():
                    if user_data["user_id"] == user_id:
                        user_data.update(profile_data)
                        return {"status": "updated", "user_id": user_id, "message": "Profile updated successfully"}
                return {"status": "not_found", "user_id": user_id, "message": "User not found"}
            
            async def check_permission(self, check: PermissionCheck, user_context=None) -> bool:
                return check.user_id in [user_data["user_id"] for user_data in self.users.values()]
            
            async def grant_permission(self, user_id: str, resource: str, action: str, user_context=None) -> Dict[str, Any]:
                return {"status": "granted", "user_id": user_id, "resource": resource, "action": action}
            
            async def revoke_permission(self, user_id: str, resource: str, action: str, user_context=None) -> Dict[str, Any]:
                return {"status": "revoked", "user_id": user_id, "resource": resource, "action": action}
            
            async def list_user_permissions(self, user_id: str, user_context=None) -> List[Dict[str, str]]:
                return [{"resource": "analytics", "action": "read"}]
            
            async def change_password(self, user_id: str, old_password: str, new_password: str, user_context=None) -> Dict[str, Any]:
                return {"status": "changed", "user_id": user_id, "message": "Password changed successfully"}
            
            async def reset_password(self, email: str, user_context=None) -> Dict[str, Any]:
                return {"status": "reset_initiated", "email": email, "message": "Password reset email sent"}
            
            async def get_auth_analytics(self, user_context=None) -> Dict[str, Any]:
                return {
                    "total_users": len(self.users),
                    "active_users": len(self.users),
                    "login_attempts": 100,
                    "successful_logins": 95
                }
        
        interface = TestAuthenticationInterface()
        
        # Test register
        register_request = RegisterRequest(
            email="test@example.com",
            password="password123",
            username="testuser",
            full_name="Test User",
            provider=AuthProvider.SUPABASE,
            metadata={"department": "analytics"}
        )
        
        register_result = await interface.register(register_request)
        assert register_result.success is True
        assert register_result.user_id is not None
        assert register_result.user_profile is not None
        assert register_result.user_profile.email == "test@example.com"
        assert register_result.user_profile.username == "testuser"
        
        user_id = register_result.user_id
        
        # Test login
        login_request = LoginRequest(
            email="test@example.com",
            password="password123",
            provider=AuthProvider.SUPABASE,
            remember_me=True
        )
        
        login_result = await interface.login(login_request)
        assert login_result.success is True
        assert login_result.user_id == user_id
        assert login_result.access_token is not None
        assert login_result.refresh_token is not None
        assert login_result.user_profile is not None
        
        # Test failed login
        failed_login_request = LoginRequest(
            email="test@example.com",
            password="wrong_password"
        )
        
        failed_login_result = await interface.login(failed_login_request)
        assert failed_login_result.success is False
        assert failed_login_result.error_message == "Invalid credentials"
        
        # Test get_user_profile
        user_profile = await interface.get_user_profile(user_id)
        assert user_profile is not None
        assert user_profile.user_id == user_id
        assert user_profile.email == "test@example.com"
        assert user_profile.username == "testuser"
        assert user_profile.full_name == "Test User"
        
        # Test update_user_profile
        update_result = await interface.update_user_profile(user_id, {"full_name": "Updated Test User"})
        assert update_result["status"] == "updated"
        
        # Verify update
        updated_profile = await interface.get_user_profile(user_id)
        assert updated_profile.full_name == "Updated Test User"
        
        # Test validate_token
        token_validation = await interface.validate_token(login_result.access_token)
        assert token_validation["valid"] is True
        assert token_validation["user_id"] == user_id
        
        # Test refresh_token
        refresh_result = await interface.refresh_token(login_result.refresh_token)
        assert refresh_result["success"] is True
        assert refresh_result["access_token"] != login_result.access_token  # Should be different
        
        # Test check_permission
        permission_check = PermissionCheck(
            user_id=user_id,
            resource="analytics_dashboard",
            action="read"
        )
        
        has_permission = await interface.check_permission(permission_check)
        assert has_permission is True
        
        # Test logout
        logout_result = await interface.logout(user_id)
        assert logout_result["status"] == "logged_out"
        assert logout_result["user_id"] == user_id