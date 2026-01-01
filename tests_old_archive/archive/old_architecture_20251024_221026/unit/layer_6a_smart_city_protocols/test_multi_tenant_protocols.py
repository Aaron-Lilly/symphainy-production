#!/usr/bin/env python3
"""
Tests for Multi-Tenant Protocols.

Tests the multi-tenant protocol definitions and data models
for Smart City multi-tenant operations.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add the symphainy-platform path
platform_path = project_root / "symphainy-source" / "symphainy-platform"
sys.path.insert(0, str(platform_path))

from backend.smart_city.protocols.multi_tenant_protocol import (
    TenantContext,
    UserTenantContext,
    IMultiTenantProtocol
)
from .test_base import SmartCityProtocolsTestBase


class TestTenantContext:
    """Test TenantContext data model."""
    
    def test_tenant_context_creation(self):
        """Test creating a tenant context."""
        tenant_context = TenantContext(
            tenant_id="tenant_001",
            tenant_name="Test Tenant",
            tenant_type="organization",
            features=["basic_analytics", "team_collaboration"],
            max_users=50,
            metadata={"industry": "technology", "region": "us-west"},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        assert tenant_context.tenant_id == "tenant_001"
        assert tenant_context.tenant_name == "Test Tenant"
        assert tenant_context.tenant_type == "organization"
        assert len(tenant_context.features) == 2
        assert "basic_analytics" in tenant_context.features
        assert "team_collaboration" in tenant_context.features
        assert tenant_context.max_users == 50
        assert tenant_context.metadata["industry"] == "technology"
        assert tenant_context.metadata["region"] == "us-west"
        assert tenant_context.created_at == "2024-01-01T00:00:00Z"
        assert tenant_context.updated_at == "2024-01-01T00:00:00Z"
    
    def test_tenant_context_serialization(self):
        """Test tenant context serialization."""
        from dataclasses import asdict
        
        tenant_context = TenantContext(
            tenant_id="serializable_tenant",
            tenant_name="Serializable Tenant",
            tenant_type="enterprise",
            features=["advanced_analytics"],
            max_users=1000,
            metadata={"serializable": True},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        tenant_dict = asdict(tenant_context)
        
        assert isinstance(tenant_dict, dict)
        assert tenant_dict["tenant_id"] == "serializable_tenant"
        assert tenant_dict["tenant_name"] == "Serializable Tenant"
        assert tenant_dict["tenant_type"] == "enterprise"
        assert tenant_dict["features"] == ["advanced_analytics"]
        assert tenant_dict["max_users"] == 1000
        assert tenant_dict["metadata"]["serializable"] is True


class TestUserTenantContext:
    """Test UserTenantContext data model."""
    
    def test_user_tenant_context_creation(self):
        """Test creating a user tenant context."""
        user_tenant_context = UserTenantContext(
            user_id="user_001",
            tenant_id="tenant_001",
            is_tenant_admin=True,
            tenant_permissions=["manage_users", "view_analytics"],
            user_permissions=["read_data", "write_data"],
            joined_at="2024-01-01T00:00:00Z"
        )
        
        assert user_tenant_context.user_id == "user_001"
        assert user_tenant_context.tenant_id == "tenant_001"
        assert user_tenant_context.is_tenant_admin is True
        assert len(user_tenant_context.tenant_permissions) == 2
        assert "manage_users" in user_tenant_context.tenant_permissions
        assert "view_analytics" in user_tenant_context.tenant_permissions
        assert len(user_tenant_context.user_permissions) == 2
        assert "read_data" in user_tenant_context.user_permissions
        assert "write_data" in user_tenant_context.user_permissions
        assert user_tenant_context.joined_at == "2024-01-01T00:00:00Z"
    
    def test_user_tenant_context_serialization(self):
        """Test user tenant context serialization."""
        from dataclasses import asdict
        
        user_tenant_context = UserTenantContext(
            user_id="serializable_user",
            tenant_id="serializable_tenant",
            is_tenant_admin=False,
            tenant_permissions=["read_only"],
            user_permissions=["basic_access"],
            joined_at="2024-01-01T00:00:00Z"
        )
        
        user_dict = asdict(user_tenant_context)
        
        assert isinstance(user_dict, dict)
        assert user_dict["user_id"] == "serializable_user"
        assert user_dict["tenant_id"] == "serializable_tenant"
        assert user_dict["is_tenant_admin"] is False
        assert user_dict["tenant_permissions"] == ["read_only"]
        assert user_dict["user_permissions"] == ["basic_access"]


class TestIMultiTenantProtocol:
    """Test IMultiTenantProtocol abstract class."""
    
    def test_multi_tenant_protocol_interface(self):
        """Test multi-tenant protocol interface methods."""
        # Check that IMultiTenantProtocol has the required abstract methods
        assert hasattr(IMultiTenantProtocol, 'get_tenant_context')
        assert hasattr(IMultiTenantProtocol, 'validate_tenant_access')
        assert hasattr(IMultiTenantProtocol, 'get_user_tenant_context')
        assert hasattr(IMultiTenantProtocol, 'create_tenant')
        assert hasattr(IMultiTenantProtocol, 'audit_tenant_action')
        
        # Check that these are abstract methods
        assert getattr(IMultiTenantProtocol.get_tenant_context, '__isabstractmethod__', False)
        assert getattr(IMultiTenantProtocol.validate_tenant_access, '__isabstractmethod__', False)
        assert getattr(IMultiTenantProtocol.get_user_tenant_context, '__isabstractmethod__', False)
        assert getattr(IMultiTenantProtocol.create_tenant, '__isabstractmethod__', False)
        assert getattr(IMultiTenantProtocol.audit_tenant_action, '__isabstractmethod__', False)


class TestMultiTenantProtocolImplementation(SmartCityProtocolsTestBase):
    """Test concrete implementation of multi-tenant protocol."""
    
    @pytest.mark.asyncio
    async def test_multi_tenant_protocol_implementation(self, mock_utility_foundation, mock_public_works_foundation):
        """Test concrete multi-tenant protocol implementation."""
        # Create a concrete implementation for testing
        class TestMultiTenantProtocol(IMultiTenantProtocol):
            def __init__(self):
                self.tenants = {
                    "tenant_001": TenantContext(
                        tenant_id="tenant_001",
                        tenant_name="Test Tenant",
                        tenant_type="organization",
                        features=["basic_analytics"],
                        max_users=50,
                        metadata={"test": True},
                        created_at="2024-01-01T00:00:00Z",
                        updated_at="2024-01-01T00:00:00Z"
                    )
                }
                self.user_tenants = {
                    "user_001": UserTenantContext(
                        user_id="user_001",
                        tenant_id="tenant_001",
                        is_tenant_admin=True,
                        tenant_permissions=["manage_users"],
                        user_permissions=["read_data"],
                        joined_at="2024-01-01T00:00:00Z"
                    )
                }
            
            async def get_tenant_context(self, tenant_id: str) -> Optional[TenantContext]:
                return self.tenants.get(tenant_id)
            
            async def validate_tenant_access(self, user_id: str, tenant_id: str) -> bool:
                user_context = self.user_tenants.get(user_id)
                return user_context is not None and user_context.tenant_id == tenant_id
            
            async def get_user_tenant_context(self, user_id: str) -> Optional[UserTenantContext]:
                return self.user_tenants.get(user_id)
            
            async def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
                return {"status": "created", "tenant_id": "new_tenant"}
            
            async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
                return {"status": "updated", "tenant_id": tenant_id}
            
            async def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
                return {"status": "deleted", "tenant_id": tenant_id}
            
            async def list_tenants(self, user_id: str) -> List[TenantContext]:
                return list(self.tenants.values())
            
            async def add_user_to_tenant(self, tenant_id: str, user_id: str, permissions: List[str] = None) -> Dict[str, Any]:
                return {"status": "added", "tenant_id": tenant_id, "user_id": user_id}
            
            async def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
                return {"status": "removed", "tenant_id": tenant_id, "user_id": user_id}
            
            async def get_tenant_users(self, tenant_id: str) -> List[UserTenantContext]:
                return [ctx for ctx in self.user_tenants.values() if ctx.tenant_id == tenant_id]
            
            async def validate_tenant_feature_access(self, tenant_id: str, feature: str) -> bool:
                tenant = self.tenants.get(tenant_id)
                return tenant is not None and feature in tenant.features
            
            async def get_tenant_usage_stats(self, tenant_id: str) -> Dict[str, Any]:
                return {"tenant_id": tenant_id, "usage": "stats"}
            
            async def audit_tenant_action(self, tenant_id: str, user_id: str, action: str, resource: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
                return {
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "action": action,
                    "resource": resource,
                    "details": details,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "audited": True
                }
        
        protocol = TestMultiTenantProtocol()
        
        # Test get_tenant_context
        tenant_context = await protocol.get_tenant_context("tenant_001")
        assert tenant_context is not None
        assert tenant_context.tenant_id == "tenant_001"
        assert tenant_context.tenant_name == "Test Tenant"
        assert tenant_context.tenant_type == "organization"
        
        # Test get_tenant_context with invalid tenant
        invalid_tenant = await protocol.get_tenant_context("invalid_tenant")
        assert invalid_tenant is None
        
        # Test validate_tenant_access
        is_valid = await protocol.validate_tenant_access("user_001", "tenant_001")
        assert is_valid is True
        
        is_invalid = await protocol.validate_tenant_access("user_001", "invalid_tenant")
        assert is_invalid is False
        
        # Test get_user_tenant_context
        user_context = await protocol.get_user_tenant_context("user_001")
        assert user_context is not None
        assert user_context.user_id == "user_001"
        assert user_context.tenant_id == "tenant_001"
        assert user_context.is_tenant_admin is True
        
        # Test create_tenant
        create_result = await protocol.create_tenant({"name": "New Tenant", "type": "organization"})
        assert create_result["status"] == "created"
        assert create_result["tenant_id"] == "new_tenant"
        
        # Test validate_tenant_feature_access
        has_feature = await protocol.validate_tenant_feature_access("tenant_001", "basic_analytics")
        assert has_feature is True
        
        lacks_feature = await protocol.validate_tenant_feature_access("tenant_001", "advanced_analytics")
        assert lacks_feature is False
        
        # Test audit_tenant_action
        audit_result = await protocol.audit_tenant_action(
            "tenant_001",
            "user_001", 
            "data_access", 
            "analytics",
            {"action": "read"}
        )
        assert audit_result["tenant_id"] == "tenant_001"
        assert audit_result["user_id"] == "user_001"
        assert audit_result["action"] == "data_access"
        assert audit_result["resource"] == "analytics"
        assert audit_result["audited"] is True
