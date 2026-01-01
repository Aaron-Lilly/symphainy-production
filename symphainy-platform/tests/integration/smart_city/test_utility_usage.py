#!/usr/bin/env python3
"""
Utility Usage Verification Tests

Tests that standard Smart City services properly use platform utilities:
1. Telemetry tracking (log_operation_with_telemetry)
2. Error handling (handle_error_with_audit)
3. Health metrics (record_health_metric)
4. Security validation (get_security, check_permissions)
5. Multi-tenancy (get_tenant, validate_tenant_access)

WHAT: Verify services use utilities correctly
HOW: Mock utility methods and verify they're called with correct parameters
"""

import sys
from pathlib import Path
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
from backend.smart_city.services.post_office.post_office_service import PostOfficeService
from backend.smart_city.services.librarian.librarian_service import LibrarianService


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for module-scoped async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def foundation_stack(event_loop):
    """Initialize foundation stack (Public Works, Curator)."""
    container = DIContainerService("test")
    
    # Initialize Public Works Foundation
    public_works = PublicWorksFoundationService(di_container=container)
    await public_works.initialize()
    container.register_foundation_service("PublicWorksFoundationService", public_works)
    
    # Initialize Curator Foundation
    curator = CuratorFoundationService(
        foundation_services=container,
        public_works_foundation=public_works
    )
    await curator.initialize()
    container.register_foundation_service("CuratorFoundationService", curator)
    
    yield {
        "di_container": container,
        "public_works": public_works,
        "curator": curator
    }
    
    # Cleanup
    if hasattr(curator, 'shutdown'):
        await curator.shutdown()
    if hasattr(public_works, 'shutdown'):
        await public_works.shutdown()


@pytest.fixture
async def data_steward_service(foundation_stack):
    """Create Data Steward service for testing."""
    container = foundation_stack["di_container"]
    service = DataStewardService(di_container=container)
    
    # Mock infrastructure connections to avoid real infrastructure requirements
    service.is_infrastructure_connected = True
    service.knowledge_governance_abstraction = MagicMock()
    service.knowledge_governance_abstraction.create_governance_policy = AsyncMock(return_value="policy_123")
    service.knowledge_governance_abstraction.create_asset_metadata = AsyncMock(return_value=True)
    service.knowledge_governance_abstraction.get_asset_metadata = AsyncMock(return_value={"policy_id": "policy_123"})
    service.knowledge_governance_abstraction.get_governance_policies = AsyncMock(return_value=[{"_key": "policy_123", "data": {}}])
    service.messaging_abstraction = MagicMock()
    service.messaging_abstraction.set_value = AsyncMock(return_value=True)
    service.messaging_abstraction.get_value = AsyncMock(return_value={"policy_id": "policy_123"})
    
    yield service


@pytest.fixture
async def post_office_service(foundation_stack):
    """Create Post Office service for testing."""
    container = foundation_stack["di_container"]
    service = PostOfficeService(di_container=container)
    
    # Mock infrastructure connections
    service.is_infrastructure_connected = True
    service.messaging_abstraction = MagicMock()
    service.messaging_abstraction.send_message = AsyncMock(return_value="msg_123")
    service.messaging_abstraction.get_messages = AsyncMock(return_value=[])
    
    yield service


@pytest.fixture
async def librarian_service(foundation_stack):
    """Create Librarian service for testing."""
    container = foundation_stack["di_container"]
    service = LibrarianService(di_container=container)
    
    # Mock infrastructure connections
    service.is_infrastructure_connected = True
    service.knowledge_governance_abstraction = MagicMock()
    service.knowledge_governance_abstraction.create_asset_metadata = AsyncMock(return_value=True)
    service.knowledge_discovery_abstraction = MagicMock()
    service.knowledge_discovery_abstraction.search_knowledge = AsyncMock(return_value={"hits": [], "totalHits": 0})
    cache_abstraction = MagicMock()
    cache_abstraction.set_value = AsyncMock(return_value=True)
    service.get_cache_abstraction = MagicMock(return_value=cache_abstraction)
    
    yield service


class TestDataStewardUtilityUsage:
    """Test Data Steward service utility usage."""
    
    @pytest.mark.asyncio
    async def test_create_content_policy_uses_telemetry(self, data_steward_service):
        """Test that create_content_policy uses telemetry tracking."""
        # Track telemetry calls
        telemetry_calls = []
        
        async def track_telemetry(operation, success=True, details=None):
            telemetry_calls.append({"operation": operation, "success": success, "details": details})
        
        data_steward_service.log_operation_with_telemetry = AsyncMock(side_effect=track_telemetry)
        data_steward_service.record_health_metric = AsyncMock()
        data_steward_service.handle_error_with_audit = AsyncMock()
        
        # Mock security and tenant to allow access
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        data_steward_service.get_security = MagicMock(return_value=mock_security)
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        data_steward_service.get_tenant = MagicMock(return_value=mock_tenant)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method
        result = await data_steward_service.create_content_policy(
            data_type="test_data",
            rules={"rule1": "value1"},
            user_context=user_context
        )
        
        # Verify telemetry was called
        assert len(telemetry_calls) >= 2, "Telemetry should be called at least twice (start and complete)"
        
        # Check for start call
        start_calls = [c for c in telemetry_calls if "start" in c["operation"]]
        assert len(start_calls) > 0, "Should have telemetry start call"
        
        # Check for complete call
        complete_calls = [c for c in telemetry_calls if "complete" in c["operation"]]
        assert len(complete_calls) > 0, "Should have telemetry complete call"
        
        # Verify health metric was recorded
        data_steward_service.record_health_metric.assert_called()
    
    @pytest.mark.asyncio
    async def test_create_content_policy_uses_security_validation(self, data_steward_service):
        """Test that create_content_policy validates security."""
        data_steward_service.log_operation_with_telemetry = AsyncMock()
        data_steward_service.record_health_metric = AsyncMock()
        
        # Mock security to deny access
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=False)
        data_steward_service.get_security = MagicMock(return_value=mock_security)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method - should raise PermissionError
        with pytest.raises(PermissionError, match="Access denied"):
            await data_steward_service.create_content_policy(
                data_type="test_data",
                rules={"rule1": "value1"},
                user_context=user_context
            )
        
        # Verify security was checked
        mock_security.check_permissions.assert_called_once()
        call_args = mock_security.check_permissions.call_args
        assert call_args[0][0] == user_context, "Should pass user_context to security check"
        assert call_args[0][1] == "data_governance", "Should check data_governance permission"
        assert call_args[0][2] == "write", "Should check write permission"
    
    @pytest.mark.asyncio
    async def test_create_content_policy_uses_tenant_validation(self, data_steward_service):
        """Test that create_content_policy validates tenant access."""
        data_steward_service.log_operation_with_telemetry = AsyncMock()
        data_steward_service.record_health_metric = AsyncMock()
        
        # Mock security to allow, but tenant to deny
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        data_steward_service.get_security = MagicMock(return_value=mock_security)
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=False)
        data_steward_service.get_tenant = MagicMock(return_value=mock_tenant)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method - should raise PermissionError
        with pytest.raises(PermissionError, match="Tenant access denied"):
            await data_steward_service.create_content_policy(
                data_type="test_data",
                rules={"rule1": "value1"},
                user_context=user_context
            )
        
        # Verify tenant was validated
        mock_tenant.validate_tenant_access.assert_called_once_with("test_tenant")
    
    @pytest.mark.asyncio
    async def test_create_content_policy_uses_error_handling(self, data_steward_service):
        """Test that create_content_policy uses error handling with audit."""
        data_steward_service.log_operation_with_telemetry = AsyncMock()
        data_steward_service.record_health_metric = AsyncMock()
        data_steward_service.handle_error_with_audit = AsyncMock()
        
        # Mock security and tenant to allow
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        data_steward_service.get_security = MagicMock(return_value=mock_security)
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        data_steward_service.get_tenant = MagicMock(return_value=mock_tenant)
        
        # Make the abstraction raise an error
        data_steward_service.knowledge_governance_abstraction.create_governance_policy = AsyncMock(
            side_effect=Exception("Test error")
        )
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method - should raise exception
        with pytest.raises(Exception):
            await data_steward_service.create_content_policy(
                data_type="test_data",
                rules={"rule1": "value1"},
                user_context=user_context
            )
        
        # Verify error handling was called
        data_steward_service.handle_error_with_audit.assert_called_once()
        call_args = data_steward_service.handle_error_with_audit.call_args
        assert "create_content_policy" in str(call_args[0][1]), "Should pass operation name to error handler"


class TestPostOfficeUtilityUsage:
    """Test Post Office service utility usage."""
    
    @pytest.mark.asyncio
    async def test_send_message_uses_telemetry(self, post_office_service):
        """Test that send_message uses telemetry tracking."""
        telemetry_calls = []
        
        async def track_telemetry(operation, success=True, details=None):
            telemetry_calls.append({"operation": operation, "success": success, "details": details})
        
        post_office_service.log_operation_with_telemetry = AsyncMock(side_effect=track_telemetry)
        post_office_service.record_health_metric = AsyncMock()
        
        # Mock security and tenant
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        post_office_service.get_security = MagicMock(return_value=mock_security)
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        post_office_service.get_tenant = MagicMock(return_value=mock_tenant)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method
        result = await post_office_service.send_message(
            recipient="test_recipient",
            message_type="test",
            content={"test": "data"},
            user_context=user_context
        )
        
        # Verify telemetry was called
        assert len(telemetry_calls) >= 2, "Telemetry should be called at least twice"
        assert any("start" in c["operation"] for c in telemetry_calls), "Should have start call"
        assert any("complete" in c["operation"] for c in telemetry_calls), "Should have complete call"
        
        # Verify health metric was recorded
        post_office_service.record_health_metric.assert_called()


class TestLibrarianUtilityUsage:
    """Test Librarian service utility usage."""
    
    @pytest.mark.asyncio
    async def test_store_knowledge_uses_telemetry(self, librarian_service):
        """Test that store_knowledge uses telemetry tracking."""
        telemetry_calls = []
        
        async def track_telemetry(operation, success=True, details=None):
            telemetry_calls.append({"operation": operation, "success": success, "details": details})
        
        librarian_service.log_operation_with_telemetry = AsyncMock(side_effect=track_telemetry)
        librarian_service.record_health_metric = AsyncMock()
        
        # Mock security and tenant
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        librarian_service.get_security = MagicMock(return_value=mock_security)
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        librarian_service.get_tenant = MagicMock(return_value=mock_tenant)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method
        result = await librarian_service.store_knowledge(
            knowledge_data={
                "title": "Test Knowledge",
                "content": "Test content",
                "category": "test"
            },
            user_context=user_context
        )
        
        # Verify telemetry was called
        assert len(telemetry_calls) >= 2, "Telemetry should be called at least twice"
        assert any("start" in c["operation"] for c in telemetry_calls), "Should have start call"
        assert any("complete" in c["operation"] for c in telemetry_calls), "Should have complete call"
        
        # Verify health metric was recorded
        librarian_service.record_health_metric.assert_called()
    
    @pytest.mark.asyncio
    async def test_search_knowledge_uses_security_validation(self, librarian_service):
        """Test that search_knowledge validates security."""
        librarian_service.log_operation_with_telemetry = AsyncMock()
        librarian_service.record_health_metric = AsyncMock()
        
        # Mock security to deny access
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=False)
        librarian_service.get_security = MagicMock(return_value=mock_security)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method - should raise PermissionError
        with pytest.raises(PermissionError, match="Access denied"):
            await librarian_service.search_knowledge(
                query="test query",
                filters=None,
                user_context=user_context
            )
        
        # Verify security was checked
        mock_security.check_permissions.assert_called_once()
        call_args = mock_security.check_permissions.call_args
        assert call_args[0][1] == "knowledge_management", "Should check knowledge_management permission"
        assert call_args[0][2] == "read", "Should check read permission"


class TestUtilityUsagePattern:
    """Test that utility usage pattern is consistent across services."""
    
    @pytest.mark.asyncio
    async def test_all_services_use_telemetry_pattern(self, data_steward_service, post_office_service, librarian_service):
        """Test that all services use the same telemetry pattern."""
        services = [
            ("DataSteward", data_steward_service, "create_content_policy", {"data_type": "test", "rules": {}}),
            ("PostOffice", post_office_service, "send_message", {"recipient": "test", "message_type": "test", "content": {}}),
            ("Librarian", librarian_service, "store_knowledge", {"knowledge_data": {"title": "test", "content": "test"}})
        ]
        
        for service_name, service, method_name, method_args in services:
            telemetry_calls = []
            
            async def track_telemetry(operation, success=True, details=None):
                telemetry_calls.append({"operation": operation, "success": success})
            
            service.log_operation_with_telemetry = AsyncMock(side_effect=track_telemetry)
            service.record_health_metric = AsyncMock()
            service.handle_error_with_audit = AsyncMock()
            
            # Mock security and tenant
            mock_security = MagicMock()
            mock_security.check_permissions = AsyncMock(return_value=True)
            service.get_security = MagicMock(return_value=mock_security)
            
            mock_tenant = MagicMock()
            mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
            service.get_tenant = MagicMock(return_value=mock_tenant)
            
            user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
            
            # Call the method
            method = getattr(service, method_name)
            try:
                await method(**method_args, user_context=user_context)
            except Exception:
                pass  # Some methods may fail due to missing infrastructure, but telemetry should still be called
            
            # Verify telemetry pattern (start and complete)
            assert len(telemetry_calls) >= 2, f"{service_name}.{method_name} should call telemetry at least twice"
            assert any("start" in c["operation"] for c in telemetry_calls), f"{service_name}.{method_name} should have start call"
            assert any("complete" in c["operation"] for c in telemetry_calls), f"{service_name}.{method_name} should have complete call"
    
    @pytest.mark.asyncio
    async def test_all_services_use_security_validation(self, data_steward_service, post_office_service, librarian_service):
        """Test that all services validate security."""
        services = [
            ("DataSteward", data_steward_service, "create_content_policy", {"data_type": "test", "rules": {}}),
            ("PostOffice", post_office_service, "send_message", {"recipient": "test", "message_type": "test", "content": {}}),
            ("Librarian", librarian_service, "store_knowledge", {"knowledge_data": {"title": "test", "content": "test"}})
        ]
        
        for service_name, service, method_name, method_args in services:
            service.log_operation_with_telemetry = AsyncMock()
            service.record_health_metric = AsyncMock()
            
            # Mock security to deny
            mock_security = MagicMock()
            mock_security.check_permissions = AsyncMock(return_value=False)
            service.get_security = MagicMock(return_value=mock_security)
            
            user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
            
            # Call the method - should raise PermissionError
            method = getattr(service, method_name)
            with pytest.raises(PermissionError, match="Access denied"):
                await method(**method_args, user_context=user_context)
            
            # Verify security was checked
            assert mock_security.check_permissions.called, f"{service_name}.{method_name} should check permissions"





