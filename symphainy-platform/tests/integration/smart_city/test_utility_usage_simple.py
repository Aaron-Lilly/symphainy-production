#!/usr/bin/env python3
"""
Simple Utility Usage Verification Tests

Tests that standard Smart City services properly use platform utilities.
This is a simplified test that directly tests service methods without full infrastructure.

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

# Import services directly
from backend.smart_city.services.data_steward.modules.policy_management import PolicyManagement
from backend.smart_city.services.post_office.modules.messaging import Messaging
from backend.smart_city.services.librarian.modules.knowledge_management import KnowledgeManagement


@pytest.fixture
def mock_service():
    """Create a mock service with utility methods."""
    service = MagicMock()
    
    # Mock utility methods
    service.log_operation_with_telemetry = AsyncMock()
    service.record_health_metric = AsyncMock()
    service.handle_error_with_audit = AsyncMock()
    service.get_security = MagicMock()
    service.get_tenant = MagicMock()
    service.logger = MagicMock()
    service.is_infrastructure_connected = True
    service.di_container = MagicMock()
    service.di_container.get_logger = MagicMock(return_value=MagicMock())
    
    # Mock infrastructure abstractions
    service.knowledge_governance_abstraction = MagicMock()
    service.knowledge_governance_abstraction.create_governance_policy = AsyncMock(return_value="policy_123")
    service.knowledge_governance_abstraction.create_asset_metadata = AsyncMock(return_value=True)
    service.knowledge_governance_abstraction.get_asset_metadata = AsyncMock(return_value={"policy_id": "policy_123"})
    service.knowledge_governance_abstraction.get_governance_policies = AsyncMock(return_value=[{"_key": "policy_123", "data": {}}])
    service.messaging_abstraction = MagicMock()
    service.messaging_abstraction.set_value = AsyncMock(return_value=True)
    service.messaging_abstraction.get_value = AsyncMock(return_value={"policy_id": "policy_123"})
    
    return service


class TestDataStewardUtilityUsage:
    """Test Data Steward service utility usage."""
    
    @pytest.mark.asyncio
    async def test_create_content_policy_uses_telemetry(self, mock_service):
        """Test that create_content_policy uses telemetry tracking."""
        # Mock security and tenant to allow access
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        mock_service.get_security.return_value = mock_security
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        mock_service.get_tenant.return_value = mock_tenant
        
        # Create module instance
        policy_module = PolicyManagement(mock_service)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method
        result = await policy_module.create_content_policy(
            data_type="test_data",
            rules={"rule1": "value1"},
            user_context=user_context
        )
        
        # Verify telemetry was called (start and complete)
        assert mock_service.log_operation_with_telemetry.call_count >= 2, "Telemetry should be called at least twice (start and complete)"
        
        # Check for start call
        start_calls = [c for c in mock_service.log_operation_with_telemetry.call_args_list 
                      if "start" in str(c)]
        assert len(start_calls) > 0, "Should have telemetry start call"
        
        # Check for complete call
        complete_calls = [c for c in mock_service.log_operation_with_telemetry.call_args_list 
                         if "complete" in str(c)]
        assert len(complete_calls) > 0, "Should have telemetry complete call"
        
        # Verify health metric was recorded
        assert mock_service.record_health_metric.called, "Health metric should be recorded"
    
    @pytest.mark.asyncio
    async def test_create_content_policy_uses_security_validation(self, mock_service):
        """Test that create_content_policy validates security."""
        # Mock security to deny access
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=False)
        mock_service.get_security.return_value = mock_security
        
        # Create module instance
        policy_module = PolicyManagement(mock_service)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method - should raise PermissionError
        with pytest.raises(PermissionError, match="Access denied"):
            await policy_module.create_content_policy(
                data_type="test_data",
                rules={"rule1": "value1"},
                user_context=user_context
            )
        
        # Verify security was checked
        assert mock_security.check_permissions.called, "Security should be checked"
        call_args = mock_security.check_permissions.call_args
        assert call_args[0][0] == user_context, "Should pass user_context to security check"
        assert call_args[0][1] == "data_governance", "Should check data_governance permission"
        assert call_args[0][2] == "write", "Should check write permission"
    
    @pytest.mark.asyncio
    async def test_create_content_policy_uses_tenant_validation(self, mock_service):
        """Test that create_content_policy validates tenant access."""
        # Mock security to allow, but tenant to deny
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        mock_service.get_security.return_value = mock_security
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=False)
        mock_service.get_tenant.return_value = mock_tenant
        
        # Create module instance
        policy_module = PolicyManagement(mock_service)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method - should raise PermissionError
        with pytest.raises(PermissionError, match="Tenant access denied"):
            await policy_module.create_content_policy(
                data_type="test_data",
                rules={"rule1": "value1"},
                user_context=user_context
            )
        
        # Verify tenant was validated
        assert mock_tenant.validate_tenant_access.called, "Tenant should be validated"
        mock_tenant.validate_tenant_access.assert_called_once_with("test_tenant")
    
    @pytest.mark.asyncio
    async def test_create_content_policy_uses_error_handling(self, mock_service):
        """Test that create_content_policy uses error handling with audit."""
        # Mock security and tenant to allow
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        mock_service.get_security.return_value = mock_security
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        mock_service.get_tenant.return_value = mock_tenant
        
        # Make the abstraction raise an error
        mock_service.knowledge_governance_abstraction.create_governance_policy = AsyncMock(
            side_effect=Exception("Test error")
        )
        
        # Create module instance
        policy_module = PolicyManagement(mock_service)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method - should raise exception
        with pytest.raises(Exception):
            await policy_module.create_content_policy(
                data_type="test_data",
                rules={"rule1": "value1"},
                user_context=user_context
            )
        
        # Verify error handling was called
        assert mock_service.handle_error_with_audit.called, "Error handling should be called"
        call_args = mock_service.handle_error_with_audit.call_args
        assert "create_content_policy" in str(call_args[0][1]), "Should pass operation name to error handler"


class TestPostOfficeUtilityUsage:
    """Test Post Office service utility usage."""
    
    @pytest.mark.asyncio
    async def test_send_message_uses_telemetry(self, mock_service):
        """Test that send_message uses telemetry tracking."""
        # Mock security and tenant
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        mock_service.get_security.return_value = mock_security
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        mock_service.get_tenant.return_value = mock_tenant
        
        # Mock messaging abstraction - return a message context object
        message_context = MagicMock()
        message_context.message_id = "msg_123"
        message_context.timestamp = "2024-01-01T00:00:00Z"
        mock_service.messaging_abstraction.send_message = AsyncMock(return_value=message_context)
        
        # Create module instance
        messaging_module = Messaging(mock_service)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method (send_message expects a request dict)
        result = await messaging_module.send_message(
            request={
                "recipient": "test_recipient",
                "message_type": "test",
                "message_content": {"test": "data"},
                "sender": "test_sender"
            },
            user_context=user_context
        )
        
        # Verify telemetry was called
        assert mock_service.log_operation_with_telemetry.call_count >= 2, "Telemetry should be called at least twice"
        assert any("start" in str(c) for c in mock_service.log_operation_with_telemetry.call_args_list), "Should have start call"
        assert any("complete" in str(c) for c in mock_service.log_operation_with_telemetry.call_args_list), "Should have complete call"
        
        # Verify health metric was recorded
        assert mock_service.record_health_metric.called, "Health metric should be recorded"


class TestLibrarianUtilityUsage:
    """Test Librarian service utility usage."""
    
    @pytest.mark.asyncio
    async def test_store_knowledge_uses_telemetry(self, mock_service):
        """Test that store_knowledge uses telemetry tracking."""
        # Mock security and tenant
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        mock_service.get_security.return_value = mock_security
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        mock_service.get_tenant.return_value = mock_tenant
        
        # Mock cache abstraction
        cache_abstraction = MagicMock()
        cache_abstraction.set_value = AsyncMock(return_value=True)
        mock_service.get_cache_abstraction = MagicMock(return_value=cache_abstraction)
        
        # Create module instance
        knowledge_module = KnowledgeManagement(mock_service)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method
        result = await knowledge_module.store_knowledge(
            knowledge_data={
                "title": "Test Knowledge",
                "content": "Test content",
                "category": "test"
            },
            user_context=user_context
        )
        
        # Verify telemetry was called
        assert mock_service.log_operation_with_telemetry.call_count >= 2, "Telemetry should be called at least twice"
        assert any("start" in str(c) for c in mock_service.log_operation_with_telemetry.call_args_list), "Should have start call"
        assert any("complete" in str(c) for c in mock_service.log_operation_with_telemetry.call_args_list), "Should have complete call"
        
        # Verify health metric was recorded
        assert mock_service.record_health_metric.called, "Health metric should be recorded"
    
    @pytest.mark.asyncio
    async def test_search_knowledge_uses_security_validation(self, mock_service):
        """Test that search_knowledge validates security."""
        # Ensure infrastructure is connected (so we get to security check)
        mock_service.is_infrastructure_connected = True
        
        # Mock security to deny access - ensure get_security() returns the mock
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=False)
        # Reset the mock to ensure it returns our security mock
        mock_service.get_security = MagicMock(return_value=mock_security)
        
        # Mock knowledge discovery abstraction (won't be called if security denies)
        mock_service.knowledge_discovery_abstraction = MagicMock()
        mock_service.knowledge_discovery_abstraction.search_knowledge = AsyncMock(return_value={"hits": [], "totalHits": 0})
        
        from backend.smart_city.services.librarian.modules.search import Search
        search_module = Search(mock_service)
        
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        # Call the method - search_knowledge catches PermissionError and returns error dict
        result = await search_module.search_knowledge(
            query="test query",
            filters=None,
            user_context=user_context
        )
        
        # Verify security was checked
        assert mock_service.get_security.called, "get_security() should be called"
        assert mock_security.check_permissions.called, "Security should be checked"
        call_args = mock_security.check_permissions.call_args
        assert call_args[0][1] == "knowledge_management", "Should check knowledge_management permission"
        assert call_args[0][2] == "read", "Should check read permission"
        
        # Verify result indicates access denied
        assert result.get("status") == "error", "Result should have error status"
        assert "Access denied" in result.get("error", ""), "Result should contain access denied error"


class TestUtilityUsagePattern:
    """Test that utility usage pattern is consistent across services."""
    
    @pytest.mark.asyncio
    async def test_all_services_use_telemetry_pattern(self, mock_service):
        """Test that all services use the same telemetry pattern."""
        # Mock security and tenant
        mock_security = MagicMock()
        mock_security.check_permissions = AsyncMock(return_value=True)
        mock_service.get_security.return_value = mock_security
        
        mock_tenant = MagicMock()
        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
        mock_service.get_tenant.return_value = mock_tenant
        
        # Test Data Steward
        policy_module = PolicyManagement(mock_service)
        user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
        
        mock_service.log_operation_with_telemetry.reset_mock()
        try:
            await policy_module.create_content_policy(
                data_type="test",
                rules={},
                user_context=user_context
            )
        except Exception:
            pass
        
        # Verify telemetry pattern
        assert mock_service.log_operation_with_telemetry.call_count >= 2, "DataSteward should call telemetry at least twice"
        assert any("start" in str(c) for c in mock_service.log_operation_with_telemetry.call_args_list), "DataSteward should have start call"
        assert any("complete" in str(c) for c in mock_service.log_operation_with_telemetry.call_args_list), "DataSteward should have complete call"

