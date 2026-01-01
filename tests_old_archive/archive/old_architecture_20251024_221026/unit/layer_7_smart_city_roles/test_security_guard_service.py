"""
Test Security Guard Service - Smart City Role for Multi-Tenant Operations

Tests the Security Guard service which handles the heavy lifting for multi-tenancy,
including tenant management, user context handling, and audit logging.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime
from typing import Dict, Any

from backend.smart_city.services.security_guard.security_guard_service import SecurityGuardService
from foundations.utility_foundation.utilities.security.security_service import UserContext
from tests.unit.layer_7_smart_city_roles.test_base import SmartCityRolesTestBase


class TestSecurityGuardService(SmartCityRolesTestBase):
    """Test Security Guard Service implementation."""
    
    @pytest.mark.asyncio
    async def test_security_guard_service_initialization(self, mock_supabase_client, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Security Guard service initialization."""
        service = SecurityGuardService(
            supabase_client=mock_supabase_client,
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test basic initialization
        self.assert_service_initialization(service, [
            'supabase_client', 'public_works_foundation',
            'smart_city_abstractions', 'tenant_cache', 'user_context_cache', 'audit_logs'
        ])
        
        # Test multi-tenant capabilities
        self.assert_multi_tenant_capabilities(service)
        
        # Test abstraction access
        self.assert_abstraction_access(service, "multi_tenant_management")
        
        assert service.supabase_client == mock_supabase_client
        assert service.public_works_foundation == mock_public_works_foundation
    
    @pytest.mark.asyncio
    async def test_security_guard_service_initialization_async(self, mock_supabase_client, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Security Guard service async initialization."""
        service = SecurityGuardService(
            supabase_client=mock_supabase_client,
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test async initialization
        await service.initialize()
        
        # Verify smart city abstractions are loaded
        assert service.smart_city_abstractions is not None
        assert isinstance(service.smart_city_abstractions, dict)
    
    @pytest.mark.asyncio
    async def test_security_guard_abstraction_methods(self, mock_supabase_client, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Security Guard abstraction access methods."""
        service = SecurityGuardService(
            supabase_client=mock_supabase_client,
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test get_smart_city_abstractions
        abstractions = service.get_smart_city_abstractions()
        assert abstractions is not None
        assert isinstance(abstractions, dict)
        
        # Test get_abstraction_for_role
        abstraction = service.get_abstraction_for_role("security_guard")
        assert abstraction is not None
        
        # Test has_abstraction
        has_abstraction = service.has_abstraction("multi_tenant_management")
        assert has_abstraction is True
        
        # Test get_abstraction
        abstraction = service.get_abstraction("multi_tenant_management")
        assert abstraction is not None
    
    @pytest.mark.asyncio
    async def test_security_guard_tenant_operations(self, mock_supabase_client, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation, sample_tenant_data):
        """Test Security Guard tenant management operations."""
        service = SecurityGuardService(
            supabase_client=mock_supabase_client,
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test create_tenant
        create_result = await service.create_tenant(
            tenant_name="Test Organization",
            tenant_type="organization", 
            admin_user_id="user_admin_001",
            admin_email="admin@testorg.com"
        )
        assert create_result is not None
        assert isinstance(create_result, dict)
        assert "success" in create_result
        
        # Test get_tenant_info
        tenant_result = await service.get_tenant_info("tenant_001")
        assert tenant_result is not None
        assert isinstance(tenant_result, dict)
        
        # Test add_user_to_tenant
        add_user_result = await service.add_user_to_tenant("tenant_001", "user_002", ["read", "write"])
        assert add_user_result is not None
        assert isinstance(add_user_result, dict)
        assert "success" in add_user_result
    
    @pytest.mark.asyncio
    async def test_security_guard_user_context_operations(self, mock_supabase_client, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation, sample_user_context):
        """Test Security Guard user context operations."""
        service = SecurityGuardService(
            supabase_client=mock_supabase_client,
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test get_user_context_with_tenant
        context_result = await service.get_user_context_with_tenant("test_token")
        assert context_result is not None
        assert isinstance(context_result, dict)
        assert "success" in context_result
        
        # Test validate_user_permission
        permission_result = await service.validate_user_permission(
            "user_001", 
            "analytics", 
            "read",
            ["read", "write"]
        )
        assert permission_result is not None
        assert isinstance(permission_result, dict)
        assert "authorized" in permission_result
    
    @pytest.mark.asyncio
    async def test_security_guard_audit_operations(self, mock_supabase_client, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Security Guard audit logging operations."""
        service = SecurityGuardService(
            supabase_client=mock_supabase_client,
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test audit_user_action
        audit_result = await service.audit_user_action(
            user_context={"user_id": "user_001", "email": "user@test.com", "session_id": "session_001", "tenant_id": "tenant_001"},
            action="data_access",
            resource="analytics",
            service="analytics_service",
            details={"action": "read", "resource_id": "data_123"}
        )
        assert audit_result is not None
        assert isinstance(audit_result, dict)
        assert "success" in audit_result
    
    @pytest.mark.asyncio
    async def test_security_guard_health_check(self, mock_supabase_client, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Security Guard health check."""
        service = SecurityGuardService(
            supabase_client=mock_supabase_client,
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test health check (inherited from SOAServiceBase)
        health_result = await service.get_service_health()
        self.assert_health_check(health_result)
        
        # Verify service name
        assert health_result["service"] == "SecurityGuardService"
    
    @pytest.mark.asyncio
    async def test_security_guard_multi_tenant_coordination(self, mock_supabase_client, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Security Guard multi-tenant coordination capabilities."""
        service = SecurityGuardService(
            supabase_client=mock_supabase_client,
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test tenant information retrieval
        tenant_info = await service.get_tenant_info("tenant_001")
        assert tenant_info is not None
        assert isinstance(tenant_info, dict)
        
        # Test tenant user addition
        add_user_result = await service.add_user_to_tenant(
            "tenant_001", 
            "user_002", 
            ["read", "write"]
        )
        assert add_user_result is not None
        assert isinstance(add_user_result, dict)
        assert "success" in add_user_result
        
        # Test user permission validation
        permission_result = await service.validate_user_permission(
            "user_002", 
            "analytics", 
            "read",
            ["read", "write"]
        )
        assert permission_result is not None
        assert isinstance(permission_result, dict)
        assert "authorized" in permission_result
    
    @pytest.mark.asyncio
    async def test_security_guard_error_handling(self, mock_supabase_client, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Security Guard error handling."""
        service = SecurityGuardService(
            supabase_client=mock_supabase_client,
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test error handling for invalid tenant
        invalid_tenant_result = await service.get_tenant_info("invalid_tenant")
        assert invalid_tenant_result is not None
        assert isinstance(invalid_tenant_result, dict)
        
        # Test error handling for invalid user
        invalid_user_result = await service.get_user_context_with_tenant("invalid_token")
        assert invalid_user_result is not None
        assert isinstance(invalid_user_result, dict)
        assert "error" in invalid_user_result or "status" in invalid_user_result
