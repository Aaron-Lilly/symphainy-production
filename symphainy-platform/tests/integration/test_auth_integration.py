#!/usr/bin/env python3
"""
Integration Tests for Supabase Authentication

Tests the complete authentication flow:
- Backend API endpoints (/api/auth/register, /api/auth/login)
- Integration with Supabase
- Frontend-backend communication

Run with: pytest tests/integration/test_auth_integration.py -v
"""

import pytest
import requests
import os
import time
import uuid
from typing import Dict, Any, Optional

# Test configuration
BACKEND_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")

# Pre-authorized test user credentials (same as Playwright tests)
# These users are pre-created and confirmed in Supabase
# Run: python3 scripts/setup_test_users.py to create them
TEST_EMAIL = os.getenv("TEST_EMAIL", "testuser0@symphainy.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "TestPassword123!")
TEST_EMAIL_DOMAIN = "symphainy.com"  # Valid domain, no bounces


class TestAuthIntegration:
    """Integration tests for Supabase authentication"""
    
    @pytest.fixture(autouse=True)
    def setup_test_account(self):
        """Use pre-authorized test account (no creation/deletion needed)"""
        # Use pre-confirmed test user (testuser0@symphainy.com)
        # This user is already created and confirmed in Supabase
        # Run: python3 scripts/setup_test_users.py to create if missing
        self.test_email = TEST_EMAIL
        self.test_password = TEST_PASSWORD
        self.test_name = "E2E Test User"
        self.user_id: Optional[str] = None
        
        yield
        
        # No cleanup needed - we reuse the same test account
        # This prevents email spam and Supabase bounce issues
    
    def test_backend_health_check(self):
        """Test that backend auth endpoint is available"""
        response = requests.get(f"{BACKEND_URL}/api/auth/health", timeout=5)
        assert response.status_code == 200, f"Backend health check failed: {response.status_code}"
        data = response.json()
        assert "status" in data or "success" in data, "Health check response missing status"
        
        # Check if Security Guard is available (required for Supabase auth)
        security_guard_available = data.get("security_guard_available", False)
        if not security_guard_available:
            pytest.skip(
                "⚠️  Security Guard not available - Supabase authentication requires Security Guard to be initialized. "
                "Check backend logs to see why Security Guard isn't loading."
            )
    
    def test_register_user_via_backend(self):
        """Test user registration through backend API"""
        # Check if Security Guard is available first
        health_response = requests.get(f"{BACKEND_URL}/api/auth/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            if not health_data.get("security_guard_available", False):
                pytest.skip("Security Guard not available - cannot test Supabase authentication")
        
        # Try to register pre-existing user (should fail gracefully)
        # This tests that duplicate registration is properly rejected
        register_data = {
            "name": self.test_name,
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # 503 means Security Guard not available
        if response.status_code == 503:
            pytest.skip(
                "Security Guard not available - backend returned 503. "
                "Security Guard must be initialized for Supabase authentication to work."
            )
        
        # User already exists (expected for pre-authorized test user)
        # Should return 400 or 409 for duplicate registration
        assert response.status_code in [200, 201, 400, 409], \
            f"Registration failed with unexpected status: {response.status_code}, response: {response.text[:200]}"
        
        if response.status_code in [400, 409]:
            print(f"✅ Duplicate registration correctly rejected for: {self.test_email}")
        else:
            print(f"⚠️  User registered (expected to already exist): {self.test_email}")
    
    def test_login_user_via_backend(self):
        """Test user login through backend API (using pre-authorized test user)"""
        # Check if Security Guard is available first
        health_response = requests.get(f"{BACKEND_URL}/api/auth/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            if not health_data.get("security_guard_available", False):
                pytest.skip("Security Guard not available - cannot test Supabase authentication")
        
        # Test login with pre-authorized user (no registration needed)
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # 503 means Security Guard not available
        if response.status_code == 503:
            pytest.skip(
                "Security Guard not available - backend returned 503. "
                "Security Guard must be initialized for Supabase authentication to work."
            )
        
        assert response.status_code == 200, \
            f"Login failed with status: {response.status_code}, response: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Login should succeed"
        assert "user" in data, "Response should include user data"
        assert "token" in data or "access_token" in data, "Response should include token"
        
        # Verify user data
        user_data = data.get("user", {})
        assert user_data.get("email") == self.test_email, "Email should match"
        
        # Store token for subsequent tests
        self.auth_token = data.get("token") or data.get("access_token")
        
        print(f"✅ User logged in: {self.test_email}")
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Check if Security Guard is available first
        health_response = requests.get(f"{BACKEND_URL}/api/auth/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            if not health_data.get("security_guard_available", False):
                pytest.skip("Security Guard not available - cannot test Supabase authentication")
        
        # Use pre-existing test user with wrong password (no email spam)
        login_data = {
            "email": self.test_email,
            "password": "WrongPassword123!"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # 503 means Security Guard not available
        if response.status_code == 503:
            pytest.skip("Security Guard not available - cannot test authentication")
        
        # Should fail with 401 Unauthorized
        assert response.status_code == 401, \
            f"Invalid login should return 401, got: {response.status_code}"
        
        print("✅ Invalid credentials correctly rejected")
    
    def test_register_duplicate_user(self):
        """Test registering a user that already exists (using pre-authorized test user)"""
        # Check if Security Guard is available first
        health_response = requests.get(f"{BACKEND_URL}/api/auth/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            if not health_data.get("security_guard_available", False):
                pytest.skip("Security Guard not available - cannot test Supabase authentication")
        
        # Try to register pre-existing test user (should fail)
        register_data = {
            "name": self.test_name,
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # 503 means Security Guard not available
        if response.status_code == 503:
            pytest.skip("Security Guard not available - cannot test authentication")
        
        # Should fail with 400 Bad Request (user already exists)
        assert response.status_code in [400, 409], \
            f"Duplicate registration should return 400/409, got: {response.status_code}"
        
        print("✅ Duplicate registration correctly rejected")
    
    def test_auth_token_format(self):
        """Test that auth tokens are in correct format (using pre-authorized test user)"""
        # Check if Security Guard is available first
        health_response = requests.get(f"{BACKEND_URL}/api/auth/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            if not health_data.get("security_guard_available", False):
                pytest.skip("Security Guard not available - cannot test Supabase authentication")
        
        # Login with pre-authorized user
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # 503 means Security Guard not available
        if response.status_code == 503:
            pytest.skip("Security Guard not available - cannot test authentication")
        
        assert response.status_code == 200
        data = response.json()
        token = data.get("token") or data.get("access_token")
        
        assert token is not None, "Token should be present"
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 0, "Token should not be empty"
        
        # JWT tokens typically have 3 parts separated by dots
        # (This is a basic check, actual validation would require decoding)
        if "." in token:
            parts = token.split(".")
            assert len(parts) == 3, "JWT token should have 3 parts"
        
        print("✅ Token format is valid")
    
    def test_backend_frontend_integration(self):
        """Test that backend response format matches frontend expectations"""
        # Login with pre-authorized user
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        login_response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert login_response.status_code == 200
        data = login_response.json()
        
        # Verify response matches frontend expectations (from lib/api/auth.ts)
        assert data.get("success") is True, "Response should have success: true"
        assert "user" in data, "Response should include user object"
        assert "token" in data or "access_token" in data, "Response should include token"
        
        user = data.get("user", {})
        # Frontend expects: user.id, user.email, user.name (or user.full_name)
        assert "email" in user, "User object should have email"
        assert user.get("email") == self.test_email, "Email should match"
        
        # Check for either id or user_id
        assert "id" in user or "user_id" in user, "User object should have id or user_id"
        
        print("✅ Backend response format matches frontend expectations")


@pytest.mark.integration
class TestAuthEndToEnd:
    """End-to-end integration tests (requires both frontend and backend)"""
    
    @pytest.fixture(autouse=True)
    def setup_test_account(self):
        """Use pre-authorized test account (no creation needed)"""
        self.test_email = TEST_EMAIL
        self.test_password = TEST_PASSWORD
        self.test_name = "E2E Test User"
        yield
    
    @pytest.mark.skipif(
        not os.getenv("TEST_FRONTEND_URL"),
        reason="Frontend URL not configured"
    )
    def test_frontend_backend_communication(self):
        """Test that frontend can communicate with backend auth endpoints"""
        # Test backend is accessible
        backend_health = requests.get(f"{BACKEND_URL}/api/auth/health", timeout=5)
        assert backend_health.status_code == 200, "Backend should be accessible"
        
        # Test frontend is accessible
        frontend_response = requests.get(f"{FRONTEND_URL}", timeout=5)
        assert frontend_response.status_code == 200, "Frontend should be accessible"
        
        print("✅ Frontend and backend are both accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

