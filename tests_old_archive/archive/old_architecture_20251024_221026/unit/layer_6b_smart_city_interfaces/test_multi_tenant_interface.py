#!/usr/bin/env python3
"""
Tests for Multi-Tenant Interface.

Tests the multi-tenant interface data models and concrete implementations
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

from backend.smart_city.interfaces.multi_tenant_interface import (
    TenantInfo,
    TenantUser,
    TenantUsageStats,
    IMultiTenantInterface
)
from tests.unit.layer_5b_smart_city_interfaces.test_base import SmartCityInterfacesTestBase


class TestTenantInfo:
    """Test TenantInfo data model."""
    
    def test_tenant_info_creation(self):
        """Test creating a tenant info."""
        tenant_info = TenantInfo(
            id="tenant_001",
            name="Test Organization",
            type="organization",
            status="active",
            admin_user_id="user_001",
            admin_email="admin@testorg.com",
            max_users=50,
            features=["basic_analytics", "team_collaboration"],
            metadata={"industry": "technology", "region": "us-west"},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        assert tenant_info.id == "tenant_001"
        assert tenant_info.name == "Test Organization"
        assert tenant_info.type == "organization"
        assert tenant_info.status == "active"
        assert tenant_info.admin_user_id == "user_001"
        assert tenant_info.admin_email == "admin@testorg.com"
        assert tenant_info.max_users == 50
        assert len(tenant_info.features) == 2
        assert "basic_analytics" in tenant_info.features
        assert "team_collaboration" in tenant_info.features
        assert tenant_info.metadata["industry"] == "technology"
        assert tenant_info.metadata["region"] == "us-west"
        assert tenant_info.created_at == "2024-01-01T00:00:00Z"
        assert tenant_info.updated_at == "2024-01-01T00:00:00Z"
    
    def test_tenant_info_serialization(self):
        """Test tenant info serialization."""
        from dataclasses import asdict
        
        tenant_info = TenantInfo(
            id="serializable_tenant",
            name="Serializable Organization",
            type="enterprise",
            status="active",
            admin_user_id="admin_001",
            admin_email="admin@serializable.com",
            max_users=1000,
            features=["advanced_analytics"],
            metadata={"serializable": True},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        tenant_dict = asdict(tenant_info)
        
        assert isinstance(tenant_dict, dict)
        assert tenant_dict["id"] == "serializable_tenant"
        assert tenant_dict["name"] == "Serializable Organization"
        assert tenant_dict["type"] == "enterprise"
        assert tenant_dict["status"] == "active"
        assert tenant_dict["admin_user_id"] == "admin_001"
        assert tenant_dict["admin_email"] == "admin@serializable.com"
        assert tenant_dict["max_users"] == 1000
        assert tenant_dict["features"] == ["advanced_analytics"]
        assert tenant_dict["metadata"]["serializable"] is True


class TestTenantUser:
    """Test TenantUser data model."""
    
    def test_tenant_user_creation(self):
        """Test creating a tenant user."""
        tenant_user = TenantUser(
            user_id="user_001",
            email="user@testorg.com",
            full_name="John Doe",
            is_tenant_admin=True,
            tenant_permissions=["manage_users", "view_analytics"],
            joined_at="2024-01-01T00:00:00Z"
        )
        
        assert tenant_user.user_id == "user_001"
        assert tenant_user.email == "user@testorg.com"
        assert tenant_user.full_name == "John Doe"
        assert tenant_user.is_tenant_admin is True
        assert len(tenant_user.tenant_permissions) == 2
        assert "manage_users" in tenant_user.tenant_permissions
        assert "view_analytics" in tenant_user.tenant_permissions
        assert tenant_user.joined_at == "2024-01-01T00:00:00Z"
    
    def test_tenant_user_serialization(self):
        """Test tenant user serialization."""
        from dataclasses import asdict
        
        tenant_user = TenantUser(
            user_id="serializable_user",
            email="user@serializable.com",
            full_name="Serializable User",
            is_tenant_admin=False,
            tenant_permissions=["read_only"],
            joined_at="2024-01-01T00:00:00Z"
        )
        
        user_dict = asdict(tenant_user)
        
        assert isinstance(user_dict, dict)
        assert user_dict["user_id"] == "serializable_user"
        assert user_dict["email"] == "user@serializable.com"
        assert user_dict["full_name"] == "Serializable User"
        assert user_dict["is_tenant_admin"] is False
        assert user_dict["tenant_permissions"] == ["read_only"]


class TestTenantUsageStats:
    """Test TenantUsageStats data model."""
    
    def test_tenant_usage_stats_creation(self):
        """Test creating tenant usage stats."""
        usage_stats = TenantUsageStats(
            tenant_id="tenant_001",
            current_users=25,
            max_users=50,
            usage_percentage=50.0,
            files_processed=1000,
            api_calls=5000,
            storage_used_gb=10.5,
            last_active="2024-01-01T12:00:00Z"
        )
        
        assert usage_stats.tenant_id == "tenant_001"
        assert usage_stats.current_users == 25
        assert usage_stats.max_users == 50
        assert usage_stats.usage_percentage == 50.0
        assert usage_stats.files_processed == 1000
        assert usage_stats.api_calls == 5000
        assert usage_stats.storage_used_gb == 10.5
        assert usage_stats.last_active == "2024-01-01T12:00:00Z"
    
    def test_tenant_usage_stats_serialization(self):
        """Test tenant usage stats serialization."""
        from dataclasses import asdict
        
        usage_stats = TenantUsageStats(
            tenant_id="serializable_tenant",
            current_users=100,
            max_users=1000,
            usage_percentage=10.0,
            files_processed=5000,
            api_calls=25000,
            storage_used_gb=50.0,
            last_active="2024-01-01T12:00:00Z"
        )
        
        stats_dict = asdict(usage_stats)
        
        assert isinstance(stats_dict, dict)
        assert stats_dict["tenant_id"] == "serializable_tenant"
        assert stats_dict["current_users"] == 100
        assert stats_dict["max_users"] == 1000
        assert stats_dict["usage_percentage"] == 10.0
        assert stats_dict["files_processed"] == 5000
        assert stats_dict["api_calls"] == 25000
        assert stats_dict["storage_used_gb"] == 50.0


class TestMultiTenantInterface(SmartCityInterfacesTestBase):
    """Test IMultiTenantInterface implementation."""
    
    @pytest.mark.asyncio
    async def test_multi_tenant_interface_initialization(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test multi-tenant interface initialization."""
        # Create a concrete implementation for testing
        class TestMultiTenantInterface(IMultiTenantInterface):
            def __init__(self):
                self.tenants = {}
                self.tenant_users = {}
                self.usage_stats = {}
            
            async def create_tenant(self, name: str, tenant_type: str, admin_user_id: str, admin_email: str) -> Dict[str, Any]:
                tenant_id = f"tenant_{len(self.tenants) + 1}"
                self.tenants[tenant_id] = {
                    "id": tenant_id,
                    "name": name,
                    "type": tenant_type,
                    "status": "active",
                    "admin_user_id": admin_user_id,
                    "admin_email": admin_email,
                    "max_users": 50,
                    "features": ["basic_analytics"],
                    "metadata": {},
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
                return {"status": "created", "tenant_id": tenant_id}
            
            async def get_tenant(self, tenant_id: str) -> Optional[TenantInfo]:
                tenant_data = self.tenants.get(tenant_id)
                if tenant_data:
                    return TenantInfo(**tenant_data)
                return None
            
            async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
                if tenant_id in self.tenants:
                    self.tenants[tenant_id].update(updates)
                    return {"status": "updated", "tenant_id": tenant_id}
                return {"status": "not_found", "tenant_id": tenant_id}
            
            async def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
                if tenant_id in self.tenants:
                    del self.tenants[tenant_id]
                    return {"status": "deleted", "tenant_id": tenant_id}
                return {"status": "not_found", "tenant_id": tenant_id}
            
            async def list_tenants(self, user_id: str) -> List[TenantInfo]:
                return [TenantInfo(**tenant_data) for tenant_data in self.tenants.values()]
            
            async def add_user_to_tenant(self, tenant_id: str, user_id: str, permissions: List[str] = None) -> Dict[str, Any]:
                if permissions is None:
                    permissions = ["read_data"]
                self.tenant_users[user_id] = {
                    "user_id": user_id,
                    "email": f"user{user_id}@example.com",
                    "full_name": f"User {user_id}",
                    "is_tenant_admin": False,
                    "tenant_permissions": permissions,
                    "joined_at": "2024-01-01T00:00:00Z"
                }
                return {"status": "added", "tenant_id": tenant_id, "user_id": user_id}
            
            async def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
                if user_id in self.tenant_users:
                    del self.tenant_users[user_id]
                    return {"status": "removed", "tenant_id": tenant_id, "user_id": user_id}
                return {"status": "not_found", "user_id": user_id}
            
            async def list_tenant_users(self, tenant_id: str) -> List[TenantUser]:
                return [TenantUser(**user_data) for user_data in self.tenant_users.values()]
            
            async def update_tenant_features(self, tenant_id: str, features: List[str]) -> Dict[str, Any]:
                if tenant_id in self.tenants:
                    self.tenants[tenant_id]["features"] = features
                    return {"status": "updated", "tenant_id": tenant_id}
                return {"status": "not_found", "tenant_id": tenant_id}
            
            async def get_tenant_usage_stats(self, tenant_id: str) -> Optional[TenantUsageStats]:
                stats_data = self.usage_stats.get(tenant_id)
                if stats_data:
                    return TenantUsageStats(**stats_data)
                return None
            
            async def validate_tenant_access(self, user_id: str, tenant_id: str) -> bool:
                return user_id in self.tenant_users and tenant_id in self.tenants
            
            async def validate_tenant_feature_access(self, tenant_id: str, feature: str) -> bool:
                tenant = self.tenants.get(tenant_id)
                return tenant is not None and feature in tenant.get("features", [])
            
            async def get_tenant_health_status(self, tenant_id: str) -> Dict[str, Any]:
                return {"tenant_id": tenant_id, "status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
            
            async def audit_tenant_action(self, tenant_id: str, user_id: str, action: str, resource: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
                return {
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "action": action,
                    "resource": resource,
                    "details": details or {},
                    "timestamp": "2024-01-01T00:00:00Z",
                    "audited": True
                }
        
        interface = TestMultiTenantInterface()
        
        assert interface is not None
        assert hasattr(interface, 'create_tenant')
        assert hasattr(interface, 'get_tenant')
        assert hasattr(interface, 'update_tenant')
        assert hasattr(interface, 'delete_tenant')
    
    @pytest.mark.asyncio
    async def test_multi_tenant_interface_operations(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test multi-tenant interface operations."""
        class TestMultiTenantInterface(IMultiTenantInterface):
            def __init__(self):
                self.tenants = {}
                self.tenant_users = {}
                self.usage_stats = {}
            
            async def create_tenant(self, name: str, tenant_type: str, admin_user_id: str, admin_email: str) -> Dict[str, Any]:
                tenant_id = f"tenant_{len(self.tenants) + 1}"
                self.tenants[tenant_id] = {
                    "id": tenant_id,
                    "name": name,
                    "type": tenant_type,
                    "status": "active",
                    "admin_user_id": admin_user_id,
                    "admin_email": admin_email,
                    "max_users": 50,
                    "features": ["basic_analytics"],
                    "metadata": {},
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
                return {"status": "created", "tenant_id": tenant_id}
            
            async def get_tenant(self, tenant_id: str) -> Optional[TenantInfo]:
                tenant_data = self.tenants.get(tenant_id)
                if tenant_data:
                    return TenantInfo(**tenant_data)
                return None
            
            async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
                if tenant_id in self.tenants:
                    self.tenants[tenant_id].update(updates)
                    return {"status": "updated", "tenant_id": tenant_id}
                return {"status": "not_found", "tenant_id": tenant_id}
            
            async def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
                if tenant_id in self.tenants:
                    del self.tenants[tenant_id]
                    return {"status": "deleted", "tenant_id": tenant_id}
                return {"status": "not_found", "tenant_id": tenant_id}
            
            async def list_tenants(self, user_id: str) -> List[TenantInfo]:
                return [TenantInfo(**tenant_data) for tenant_data in self.tenants.values()]
            
            async def add_user_to_tenant(self, tenant_id: str, user_id: str, permissions: List[str] = None) -> Dict[str, Any]:
                if permissions is None:
                    permissions = ["read_data"]
                self.tenant_users[user_id] = {
                    "user_id": user_id,
                    "email": f"user{user_id}@example.com",
                    "full_name": f"User {user_id}",
                    "is_tenant_admin": False,
                    "tenant_permissions": permissions,
                    "joined_at": "2024-01-01T00:00:00Z"
                }
                return {"status": "added", "tenant_id": tenant_id, "user_id": user_id}
            
            async def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
                if user_id in self.tenant_users:
                    del self.tenant_users[user_id]
                    return {"status": "removed", "tenant_id": tenant_id, "user_id": user_id}
                return {"status": "not_found", "user_id": user_id}
            
            async def list_tenant_users(self, tenant_id: str) -> List[TenantUser]:
                return [TenantUser(**user_data) for user_data in self.tenant_users.values()]
            
            async def update_tenant_features(self, tenant_id: str, features: List[str]) -> Dict[str, Any]:
                if tenant_id in self.tenants:
                    self.tenants[tenant_id]["features"] = features
                    return {"status": "updated", "tenant_id": tenant_id}
                return {"status": "not_found", "tenant_id": tenant_id}
            
            async def get_tenant_usage_stats(self, tenant_id: str) -> Optional[TenantUsageStats]:
                stats_data = self.usage_stats.get(tenant_id)
                if stats_data:
                    return TenantUsageStats(**stats_data)
                return None
            
            async def validate_tenant_access(self, user_id: str, tenant_id: str) -> bool:
                return user_id in self.tenant_users and tenant_id in self.tenants
            
            async def validate_tenant_feature_access(self, tenant_id: str, feature: str) -> bool:
                tenant = self.tenants.get(tenant_id)
                return tenant is not None and feature in tenant.get("features", [])
            
            async def get_tenant_health_status(self, tenant_id: str) -> Dict[str, Any]:
                return {"tenant_id": tenant_id, "status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
            
            async def audit_tenant_action(self, tenant_id: str, user_id: str, action: str, resource: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
                return {
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "action": action,
                    "resource": resource,
                    "details": details or {},
                    "timestamp": "2024-01-01T00:00:00Z",
                    "audited": True
                }
        
        interface = TestMultiTenantInterface()
        
        # Test create_tenant
        create_result = await interface.create_tenant("Test Organization", "organization", "admin_001", "admin@testorg.com")
        assert create_result["status"] == "created"
        assert "tenant_id" in create_result
        
        tenant_id = create_result["tenant_id"]
        
        # Test get_tenant
        tenant_info = await interface.get_tenant(tenant_id)
        assert tenant_info is not None
        assert tenant_info.name == "Test Organization"
        assert tenant_info.type == "organization"
        assert tenant_info.admin_user_id == "admin_001"
        assert tenant_info.admin_email == "admin@testorg.com"
        
        # Test update_tenant
        update_result = await interface.update_tenant(tenant_id, {"max_users": 100})
        assert update_result["status"] == "updated"
        
        # Verify update
        updated_tenant = await interface.get_tenant(tenant_id)
        assert updated_tenant.max_users == 100
        
        # Test add_user_to_tenant
        add_user_result = await interface.add_user_to_tenant(tenant_id, "user_001", ["read_data", "write_data"])
        assert add_user_result["status"] == "added"
        assert add_user_result["user_id"] == "user_001"
        
        # Test list_tenant_users
        tenant_users = await interface.list_tenant_users(tenant_id)
        assert len(tenant_users) == 1
        assert tenant_users[0].user_id == "user_001"
        assert tenant_users[0].tenant_permissions == ["read_data", "write_data"]
        
        # Test update_tenant_features
        update_features_result = await interface.update_tenant_features(tenant_id, ["advanced_analytics", "team_collaboration"])
        assert update_features_result["status"] == "updated"
        
        # Verify features update
        updated_tenant = await interface.get_tenant(tenant_id)
        assert "advanced_analytics" in updated_tenant.features
        assert "team_collaboration" in updated_tenant.features
        
        # Test validate_tenant_access
        has_access = await interface.validate_tenant_access("user_001", tenant_id)
        assert has_access is True
        
        # Test validate_tenant_feature_access
        has_feature = await interface.validate_tenant_feature_access(tenant_id, "advanced_analytics")
        assert has_feature is True
        
        lacks_feature = await interface.validate_tenant_feature_access(tenant_id, "premium_feature")
        assert lacks_feature is False
        
        # Test get_tenant_health_status
        health_status = await interface.get_tenant_health_status(tenant_id)
        assert health_status["tenant_id"] == tenant_id
        assert health_status["status"] == "healthy"
        
        # Test audit_tenant_action
        audit_result = await interface.audit_tenant_action(
            tenant_id,
            "user_001", 
            "data_access", 
            "analytics",
            {"action": "read"}
        )
        assert audit_result["tenant_id"] == tenant_id
        assert audit_result["user_id"] == "user_001"
        assert audit_result["action"] == "data_access"
        assert audit_result["resource"] == "analytics"
        assert audit_result["audited"] is True
        
        # Test remove_user_from_tenant
        remove_user_result = await interface.remove_user_from_tenant(tenant_id, "user_001")
        assert remove_user_result["status"] == "removed"
        
        # Test delete_tenant
        delete_result = await interface.delete_tenant(tenant_id)
        assert delete_result["status"] == "deleted"
        
        # Verify deletion
        deleted_tenant = await interface.get_tenant(tenant_id)
        assert deleted_tenant is None