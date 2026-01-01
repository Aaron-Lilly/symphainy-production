#!/usr/bin/env python3
"""
Layer 2: Security Context Utility Tests

Tests that validate security context utility works correctly.

WHAT: Validate security context utility
HOW: Test SecurityContextUtility
"""

import pytest

import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from utilities.security_context_utility import SecurityContextUtility, SecurityContext, TenantContext, TraceContext

class TestSecurityContextUtility:
    """Test security context utility."""
    
    @pytest.fixture
    def security_context_utility(self):
        """Create security context utility instance."""
        return SecurityContextUtility()
    
    def test_security_context_utility_initialization(self, security_context_utility):
        """Test that security context utility initializes correctly."""
        assert security_context_utility is not None
        assert security_context_utility.logger is not None
    
    @pytest.mark.asyncio
    async def test_build_user_context(self, security_context_utility):
        """Test building user context from token."""
        # Mock token parsing
        async def mock_parse_token(token):
            return {
                "user_id": "user123",
                "tenant_id": "tenant456",
                "roles": ["admin"],
                "permissions": ["read", "write"]
            }
        
        security_context_utility._parse_token = mock_parse_token
        
        context = await security_context_utility.build_user_context("test_token")
        
        assert context.user_id == "user123"
        assert context.tenant_id == "tenant456"
        assert "admin" in context.roles
        assert "read" in context.permissions
    
    def test_create_security_context(self, security_context_utility):
        """Test creating security context directly."""
        context = SecurityContext(
            user_id="user123",
            tenant_id="tenant456",
            roles=["admin"],
            permissions=["read", "write"]
        )
        
        assert context.user_id == "user123"
        assert context.tenant_id == "tenant456"
        assert "admin" in context.roles
        assert "read" in context.permissions
    
    def test_create_trace_context(self, security_context_utility):
        """Test creating trace context."""
        context = TraceContext(
            request_id="req123",
            trace_id="trace456"
        )
        
        assert context.request_id == "req123"
        assert context.trace_id == "trace456"
        assert context.service_name == "security_context_utility"
    
    def test_security_context_immutability(self, security_context_utility):
        """Test that security context is immutable."""
        context = SecurityContext(
            user_id="user123",
            tenant_id="tenant456",
            roles=["admin"]
        )
        
        # Should not be able to modify frozen dataclass
        with pytest.raises(Exception):  # FrozenInstanceError
            context.user_id = "new_user"
