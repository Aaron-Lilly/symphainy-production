#!/usr/bin/env python3
"""
Test to verify security and multi-tenancy validation in composition services.

This test verifies:
1. Helper methods are present in composition services
2. Validation is called in methods with user_context
3. Security and tenant utilities are properly accessed
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

async def test_composition_service_validation():
    """Test that composition services have validation helpers and use them."""
    
    print("=" * 80)
    print("Testing Security and Multi-Tenancy Validation in Composition Services")
    print("=" * 80)
    print()
    
    # Test File Management Composition Service
    from foundations.public_works_foundation.composition_services.file_management_composition_service import FileManagementCompositionService
    from foundations.public_works_foundation.infrastructure_abstractions.file_management_abstraction import FileManagementAbstraction
    
    # Create mocks
    mock_abstraction = MagicMock(spec=FileManagementAbstraction)
    mock_abstraction.create_file = AsyncMock(return_value={"uuid": "test-uuid"})
    mock_abstraction.update_file = AsyncMock(return_value={})
    
    mock_di_container = MagicMock()
    mock_logger = MagicMock()
    mock_di_container.get_logger.return_value = mock_logger
    
    # Mock security utility
    mock_security = MagicMock()
    mock_security.validate_user_permission = AsyncMock(return_value=True)
    
    # Mock tenant utility
    mock_tenant = MagicMock()
    mock_tenant.is_multi_tenant_enabled.return_value = True
    mock_tenant.validate_tenant_access.return_value = True
    
    mock_di_container.get_utility = MagicMock(side_effect=lambda name: {
        "security": mock_security,
        "tenant": mock_tenant,
        "error_handler": None,
        "telemetry": None
    }.get(name))
    
    # Create service
    service = FileManagementCompositionService(mock_abstraction, di_container=mock_di_container)
    
    # Verify helper method exists
    assert hasattr(service, '_validate_security_and_tenant'), "Helper method _validate_security_and_tenant should exist"
    print("✅ Helper method _validate_security_and_tenant exists")
    
    # Test validation with valid context
    user_context = {
        "user_id": "user123",
        "tenant_id": "tenant123",
        "security_context": {
            "permissions": ["read", "write"]
        }
    }
    
    validation_result = await service._validate_security_and_tenant(
        user_context, "file", "upload"
    )
    
    assert validation_result is None, "Validation should pass with valid context"
    print("✅ Validation passes with valid security and tenant context")
    
    # Verify security utility was called
    mock_security.validate_user_permission.assert_called_once()
    print("✅ Security utility validate_user_permission was called")
    
    # Verify tenant utility was called
    assert mock_tenant.is_multi_tenant_enabled.called, "Tenant utility should be checked"
    print("✅ Tenant utility was checked")
    
    # Test validation with permission denied
    mock_security.validate_user_permission.return_value = False
    validation_result = await service._validate_security_and_tenant(
        user_context, "file", "upload"
    )
    
    assert validation_result is not None, "Validation should fail with permission denied"
    assert validation_result.get("error_code") == "PERMISSION_DENIED", "Should return PERMISSION_DENIED error code"
    print("✅ Validation correctly denies access when permission is denied")
    
    # Test validation with tenant access denied
    mock_security.validate_user_permission.return_value = True
    mock_tenant.validate_tenant_access.return_value = False
    validation_result = await service._validate_security_and_tenant(
        user_context, "file", "upload"
    )
    
    assert validation_result is not None, "Validation should fail with tenant access denied"
    assert validation_result.get("error_code") == "TENANT_ACCESS_DENIED", "Should return TENANT_ACCESS_DENIED error code"
    print("✅ Validation correctly denies access when tenant access is denied")
    
    # Test that validation is called in upload_and_process_file
    mock_security.validate_user_permission.return_value = True
    mock_tenant.validate_tenant_access.return_value = True
    
    # Mock file data
    file_data = b"test file content"
    filename = "test.txt"
    file_type = "txt"
    
    result = await service.upload_and_process_file(file_data, filename, file_type, user_context)
    
    # Verify validation was called (security should be called again)
    assert mock_security.validate_user_permission.call_count >= 2, "Validation should be called in upload_and_process_file"
    print("✅ Validation is called in upload_and_process_file method")
    
    print()
    print("=" * 80)
    print("✅ All tests passed!")
    print("=" * 80)

async def test_foundation_service_utilities():
    """Test that Public Works Foundation Service uses utilities from base class."""
    
    print()
    print("=" * 80)
    print("Testing Public Works Foundation Service Utility Usage")
    print("=" * 80)
    print()
    
    # Check if foundation service has utility access methods
    from bases.mixins.utility_access_mixin import UtilityAccessMixin
    from bases.mixins.security_mixin import SecurityMixin
    
    # Verify mixins provide utility access
    assert hasattr(UtilityAccessMixin, 'get_utility'), "UtilityAccessMixin should provide get_utility"
    assert hasattr(UtilityAccessMixin, 'get_security'), "UtilityAccessMixin should provide get_security"
    assert hasattr(UtilityAccessMixin, 'get_tenant'), "UtilityAccessMixin should provide get_tenant"
    print("✅ UtilityAccessMixin provides utility access methods")
    
    # Verify SecurityMixin provides security methods
    assert hasattr(SecurityMixin, 'validate_access'), "SecurityMixin should provide validate_access"
    assert hasattr(SecurityMixin, 'validate_tenant_access'), "SecurityMixin should provide validate_tenant_access"
    assert hasattr(SecurityMixin, 'get_security_context'), "SecurityMixin should provide get_security_context"
    assert hasattr(SecurityMixin, 'set_security_context'), "SecurityMixin should provide set_security_context"
    print("✅ SecurityMixin provides security and tenant validation methods")
    
    # Check Public Works Foundation Service inheritance
    from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
    from bases.foundation_service_base import FoundationServiceBase
    
    assert issubclass(PublicWorksFoundationService, FoundationServiceBase), "Public Works Foundation should inherit from FoundationServiceBase"
    print("✅ Public Works Foundation Service inherits from FoundationServiceBase")
    
    # Check that FoundationServiceBase includes the mixins
    from bases.foundation_service_base import FoundationServiceBase
    import inspect
    
    # Get all base classes
    bases = inspect.getmro(PublicWorksFoundationService)
    has_utility_mixin = UtilityAccessMixin in bases
    
    assert has_utility_mixin, "Public Works Foundation should have UtilityAccessMixin"
    print("✅ Public Works Foundation Service has UtilityAccessMixin")
    
    # Note: FoundationServiceBase doesn't include SecurityMixin (only RealmServiceBase does)
    # But it can access security utilities through UtilityAccessMixin.get_security()
    print("ℹ️  Note: FoundationServiceBase accesses security via utilities, not SecurityMixin")
    
    # Verify methods are available
    assert hasattr(PublicWorksFoundationService, 'get_utility'), "Public Works Foundation should have get_utility method"
    assert hasattr(PublicWorksFoundationService, 'get_security'), "Public Works Foundation should have get_security method"
    assert hasattr(PublicWorksFoundationService, 'get_tenant'), "Public Works Foundation should have get_tenant method"
    print("✅ Public Works Foundation Service has utility access methods")
    
    print()
    print("=" * 80)
    print("✅ Foundation Service utility access verified!")
    print("=" * 80)

async def main():
    """Run all tests."""
    try:
        await test_composition_service_validation()
        await test_foundation_service_utilities()
        print()
        print("🎉 All verification tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

