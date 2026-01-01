#!/usr/bin/env python3
"""
Layer 2: Tenant Context Utility Tests

Tests that validate tenant context utility works correctly.

WHAT: Validate tenant context utility
HOW: Test TenantContextUtility
"""

import pytest

import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from utilities.tenant_context_utility import TenantContextUtility, TenantContext, IsolationContext, FeatureContext

class TestTenantContextUtility:
    """Test tenant context utility."""
    
    @pytest.fixture
    def tenant_context_utility(self):
        """Create tenant context utility instance."""
        return TenantContextUtility()
    
    def test_tenant_context_utility_initialization(self, tenant_context_utility):
        """Test that tenant context utility initializes correctly."""
        assert tenant_context_utility is not None
        assert tenant_context_utility.logger is not None
    
    @pytest.mark.asyncio
    async def test_build_tenant_context(self, tenant_context_utility):
        """Test building tenant context."""
        # Mock tenant info retrieval
        async def mock_get_tenant_info(tenant_id):
            return {
                "tenant_name": "Test Tenant",
                "tenant_type": "enterprise",
                "max_users": 100,
                "features": ["feature1", "feature2"],
                "limits": {"storage": "100GB"}
            }
        
        tenant_context_utility._get_tenant_info = mock_get_tenant_info
        
        context = await tenant_context_utility.build_tenant_context("tenant123")
        
        assert context.tenant_id == "tenant123"
        assert context.tenant_name == "Test Tenant"
        assert context.tenant_type == "enterprise"
        assert context.max_users == 100
        assert "feature1" in context.features
    
    def test_create_tenant_context(self, tenant_context_utility):
        """Test creating tenant context directly."""
        context = TenantContext(
            tenant_id="tenant123",
            tenant_name="Test Tenant",
            tenant_type="enterprise",
            max_users=100,
            features=["feature1"],
            limits={"storage": "100GB"}
        )
        
        assert context.tenant_id == "tenant123"
        assert context.tenant_name == "Test Tenant"
        assert context.is_active is True
    
    def test_create_isolation_context(self, tenant_context_utility):
        """Test creating isolation context."""
        context = IsolationContext(
            user_tenant="tenant1",
            resource_tenant="tenant2",
            user_tenant_type="enterprise",
            resource_tenant_type="enterprise",
            isolation_required=True
        )
        
        assert context.user_tenant == "tenant1"
        assert context.resource_tenant == "tenant2"
        assert context.isolation_required is True
    
    def test_create_feature_context(self, tenant_context_utility):
        """Test creating feature context."""
        context = FeatureContext(
            tenant_id="tenant123",
            feature="feature1",
            tenant_type="enterprise",
            feature_available=True,
            usage_limits={"requests": 1000}
        )
        
        assert context.tenant_id == "tenant123"
        assert context.feature == "feature1"
        assert context.feature_available is True
