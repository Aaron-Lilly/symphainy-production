#!/usr/bin/env python3
"""
Layer 2: Security Authorization Utility Tests

Tests that validate security authorization utility works correctly.

WHAT: Validate security authorization utility
HOW: Test SecurityAuthorizationUtility
"""

import pytest

import os
from unittest.mock import Mock, patch

from utilities.security_authorization.security_authorization_utility import SecurityAuthorizationUtility, UserContext

class TestSecurityAuthorizationUtility:
    """Test security authorization utility."""
    
    @pytest.fixture
    def security_authorization_utility(self):
        """Create security authorization utility instance."""
        return SecurityAuthorizationUtility("test_service")
    
    def test_security_authorization_utility_initialization(self, security_authorization_utility):
        """Test that security authorization utility initializes correctly."""
        assert security_authorization_utility is not None
        assert security_authorization_utility.service_name == "test_service"  # Uses service_name, not realm_name
        assert security_authorization_utility.is_bootstrapped is False
    
    def test_create_user_context(self, security_authorization_utility):
        """Test creating user context."""
        user_context = UserContext(
            user_id="user123",
            email="user@example.com",
            full_name="Test User",
            session_id="session123",
            permissions=["read", "write"],
            tenant_id="tenant456"
        )
        
        assert user_context.user_id == "user123"
        assert user_context.email == "user@example.com"
        assert user_context.tenant_id == "tenant456"
        assert "read" in user_context.permissions
        assert user_context.request_id is not None  # Auto-generated
        assert user_context.timestamp is not None  # Auto-generated
    
    def test_user_context_to_dict(self, security_authorization_utility):
        """Test converting user context to dictionary."""
        user_context = UserContext(
            user_id="user123",
            email="user@example.com",
            full_name="Test User",
            session_id="session123",
            permissions=["read"]
        )
        
        context_dict = user_context.to_dict()
        
        assert context_dict["user_id"] == "user123"
        assert context_dict["email"] == "user@example.com"
        assert context_dict["permissions"] == ["read"]
