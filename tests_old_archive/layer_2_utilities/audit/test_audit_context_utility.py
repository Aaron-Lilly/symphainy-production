#!/usr/bin/env python3
"""
Layer 2: Audit Context Utility Tests

Tests that validate audit context utility works correctly.

WHAT: Validate audit context utility
HOW: Test AuditContextUtility
"""

import pytest

import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from utilities.audit_context_utility import AuditContextUtility, AuditContext, SecurityEvent
from utilities.security_context_utility import SecurityContext, TraceContext

class TestAuditContextUtility:
    """Test audit context utility."""
    
    @pytest.fixture
    def audit_context_utility(self):
        """Create audit context utility instance."""
        return AuditContextUtility()
    
    def test_audit_context_utility_initialization(self, audit_context_utility):
        """Test that audit context utility initializes correctly."""
        assert audit_context_utility is not None
        assert audit_context_utility.logger is not None
    
    @pytest.mark.asyncio
    async def test_build_audit_context(self, audit_context_utility):
        """Test building audit context."""
        user_context = SecurityContext(
            user_id="user123",
            tenant_id="tenant456",
            roles=["admin"],
            permissions=["read", "write"]
        )
        
        trace_context = TraceContext(
            request_id="req123",
            trace_id="trace456"
        )
        
        context = await audit_context_utility.build_audit_context(
            user_context=user_context,
            action="read",
            resource="resource1",
            trace_context=trace_context,
            details={"key": "value"}
        )
        
        assert context.user_id == "user123"
        assert context.tenant_id == "tenant456"
        assert context.action == "read"
        assert context.resource == "resource1"
        assert context.trace_id == "trace456"
        assert context.request_id == "req123"
        assert "admin" in context.user_roles
    
    def test_create_audit_context(self, audit_context_utility):
        """Test creating audit context directly."""
        context = AuditContext(
            user_id="user123",
            tenant_id="tenant456",
            action="read",
            resource="resource1",
            trace_id="trace123",
            request_id="req123",
            user_roles=["admin"],
            user_permissions=["read"],
            details={"key": "value"}
        )
        
        assert context.user_id == "user123"
        assert context.action == "read"
        assert context.trace_id == "trace123"
    
    def test_create_security_event(self, audit_context_utility):
        """Test creating security event."""
        event = SecurityEvent(
            event_type="access_denied",
            severity="high",
            user_id="user123",
            tenant_id="tenant456",
            action="write",
            resource="resource1",
            trace_id="trace123",
            details={"reason": "unauthorized"}
        )
        
        assert event.event_type == "access_denied"
        assert event.severity == "high"
        assert event.user_id == "user123"
