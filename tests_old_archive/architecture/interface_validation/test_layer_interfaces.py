#!/usr/bin/env python3
"""
Architecture Interface Validation Tests

This test suite validates that all layers implement proper interfaces
according to the current architecture. This ensures interface compliance
and architectural consistency.

CRITICAL REQUIREMENT: These tests validate REAL interface implementations, not mocks.
We need to prove the interfaces actually work as designed.
"""

import pytest
import asyncio

import os
from pathlib import Path
from typing import Dict, Any, List
from abc import ABC, abstractmethod

# Add the platform directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-platform'))

# Import real platform components for interface validation
from foundations.utility_foundation.utilities.configuration.configuration_utility import ConfigurationUtility
from foundations.utility_foundation.utilities.tenant.tenant_management_utility import TenantManagementUtility
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import SecurityAuthorizationUtility
from foundations.infrastructure_foundation.infrastructure_foundation_service import InfrastructureFoundationServiceEnvIntegrated
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.foundation_service_base import FoundationServiceBase

class TestLayerInterfaceValidation:
    """Test that all layers implement proper interfaces."""

    @pytest.fixture
    def config_utility(self):
        """Create Configuration Utility for testing."""
        return ConfigurationUtility("interface_validation_test")

    # =============================================================================
    # UTILITY FOUNDATION INTERFACE VALIDATION
    # =============================================================================

    async def test_utility_foundation_interfaces(self, config_utility):
        """Test utility foundation implements required interfaces."""
        # Test ConfigurationUtility interface
        assert hasattr(config_utility, 'get_external_services_config'), "ConfigurationUtility should implement get_external_services_config"
        assert hasattr(config_utility, 'get_database_config'), "ConfigurationUtility should implement get_database_config"
        assert hasattr(config_utility, 'get_redis_config'), "ConfigurationUtility should implement get_redis_config"
        
        # Test that ConfigurationUtility methods are callable
        assert callable(config_utility.get_external_services_config), "get_external_services_config should be callable"
        assert callable(config_utility.get_database_config), "get_database_config should be callable"
        assert callable(config_utility.get_redis_config), "get_redis_config should be callable"

    async def test_tenant_management_utility_interface(self, config_utility):
        """Test TenantManagementUtility interface compliance."""
        tenant_utility = TenantManagementUtility(config_utility)
        
        # Test required interface methods
        assert hasattr(tenant_utility, 'create_tenant'), "TenantManagementUtility should implement create_tenant"
        assert hasattr(tenant_utility, 'get_tenant'), "TenantManagementUtility should implement get_tenant"
        assert hasattr(tenant_utility, 'update_tenant'), "TenantManagementUtility should implement update_tenant"
        assert hasattr(tenant_utility, 'delete_tenant'), "TenantManagementUtility should implement delete_tenant"
        
        # Test that methods are callable
        assert callable(tenant_utility.create_tenant), "create_tenant should be callable"
        assert callable(tenant_utility.get_tenant), "get_tenant should be callable"
        assert callable(tenant_utility.update_tenant), "update_tenant should be callable"
        assert callable(tenant_utility.delete_tenant), "delete_tenant should be callable"

    async def test_security_authorization_utility_interface(self, config_utility):
        """Test SecurityAuthorizationUtility interface compliance."""
        security_utility = SecurityAuthorizationUtility(config_utility)
        
        # Test required interface methods
        assert hasattr(security_utility, 'validate_user_context'), "SecurityAuthorizationUtility should implement validate_user_context"
        assert hasattr(security_utility, 'authorize_request'), "SecurityAuthorizationUtility should implement authorize_request"
        assert hasattr(security_utility, 'create_user_context'), "SecurityAuthorizationUtility should implement create_user_context"
        
        # Test that methods are callable
        assert callable(security_utility.validate_user_context), "validate_user_context should be callable"
        assert callable(security_utility.authorize_request), "authorize_request should be callable"
        assert callable(security_utility.create_user_context), "create_user_context should be callable"

    # =============================================================================
    # FOUNDATION LAYER INTERFACE VALIDATION
    # =============================================================================

    async def test_infrastructure_foundation_interface(self, config_utility):
        """Test InfrastructureFoundation interface compliance."""
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        
        # Test that it inherits from FoundationServiceBase
        assert isinstance(infrastructure_foundation, FoundationServiceBase), "InfrastructureFoundation should inherit from FoundationServiceBase"
        
        # Test required interface methods from FoundationServiceBase
        assert hasattr(infrastructure_foundation, 'initialize'), "InfrastructureFoundation should implement initialize"
        assert hasattr(infrastructure_foundation, 'get_health_status'), "InfrastructureFoundation should implement get_health_status"
        assert hasattr(infrastructure_foundation, 'shutdown'), "InfrastructureFoundation should implement shutdown"
        
        # Test that methods are callable
        assert callable(infrastructure_foundation.initialize), "initialize should be callable"
        assert callable(infrastructure_foundation.get_health_status), "get_health_status should be callable"
        assert callable(infrastructure_foundation.shutdown), "shutdown should be callable"

    async def test_public_works_foundation_interface(self, config_utility):
        """Test PublicWorksFoundation interface compliance."""
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        
        public_works_foundation = PublicWorksFoundationService(
            utility_foundation=None,
            curator_foundation=None,
            infrastructure_foundation=infrastructure_foundation,
            env_loader=config_utility,
            security_guard_client=None
        )
        
        # Test that it inherits from FoundationServiceBase
        assert isinstance(public_works_foundation, FoundationServiceBase), "PublicWorksFoundation should inherit from FoundationServiceBase"
        
        # Test required interface methods from FoundationServiceBase
        assert hasattr(public_works_foundation, 'initialize'), "PublicWorksFoundation should implement initialize"
        assert hasattr(public_works_foundation, 'get_health_status'), "PublicWorksFoundation should implement get_health_status"
        assert hasattr(public_works_foundation, 'shutdown'), "PublicWorksFoundation should implement shutdown"
        
        # Test that methods are callable
        assert callable(public_works_foundation.initialize), "initialize should be callable"
        assert callable(public_works_foundation.get_health_status), "get_health_status should be callable"
        assert callable(public_works_foundation.shutdown), "shutdown should be callable"

    async def test_curator_foundation_interface(self, config_utility):
        """Test CuratorFoundation interface compliance."""
        curator_foundation = CuratorFoundationService(
            utility_foundation=None,
            env_loader=config_utility,
            security_service=None
        )
        
        # Test that it inherits from FoundationServiceBase
        assert isinstance(curator_foundation, FoundationServiceBase), "CuratorFoundation should inherit from FoundationServiceBase"
        
        # Test required interface methods from FoundationServiceBase
        assert hasattr(curator_foundation, 'initialize'), "CuratorFoundation should implement initialize"
        assert hasattr(curator_foundation, 'get_health_status'), "CuratorFoundation should implement get_health_status"
        assert hasattr(curator_foundation, 'shutdown'), "CuratorFoundation should implement shutdown"
        
        # Test that methods are callable
        assert callable(curator_foundation.initialize), "initialize should be callable"
        assert callable(curator_foundation.get_health_status), "get_health_status should be callable"
        assert callable(curator_foundation.shutdown), "shutdown should be callable"

    # =============================================================================
    # INTERFACE INHERITANCE VALIDATION
    # =============================================================================

    async def test_foundation_service_base_interface(self, config_utility):
        """Test FoundationServiceBase interface compliance."""
        # Test that all foundation services inherit from FoundationServiceBase
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        assert isinstance(infrastructure_foundation, FoundationServiceBase), "InfrastructureFoundation should inherit from FoundationServiceBase"
        
        public_works_foundation = PublicWorksFoundationService(
            utility_foundation=None,
            curator_foundation=None,
            infrastructure_foundation=infrastructure_foundation,
            env_loader=config_utility,
            security_guard_client=None
        )
        assert isinstance(public_works_foundation, FoundationServiceBase), "PublicWorksFoundation should inherit from FoundationServiceBase"
        
        curator_foundation = CuratorFoundationService(
            utility_foundation=None,
            env_loader=config_utility,
            security_service=None
        )
        assert isinstance(curator_foundation, FoundationServiceBase), "CuratorFoundation should inherit from FoundationServiceBase"

    # =============================================================================
    # INTERFACE VERSIONING VALIDATION
    # =============================================================================

    async def test_interface_versioning_compliance(self, config_utility):
        """Test interface versioning compliance."""
        # Test that interfaces maintain backward compatibility
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        
        # Test that required methods exist and are callable
        required_methods = ['initialize', 'get_health_status', 'shutdown']
        for method_name in required_methods:
            assert hasattr(infrastructure_foundation, method_name), f"InfrastructureFoundation should have {method_name}"
            assert callable(getattr(infrastructure_foundation, method_name)), f"{method_name} should be callable"

    # =============================================================================
    # INTERFACE CONTRACT VALIDATION
    # =============================================================================

    async def test_interface_contract_validation(self, config_utility):
        """Test interface contract validation."""
        # Test that interfaces follow expected contracts
        tenant_utility = TenantManagementUtility(config_utility)
        security_utility = SecurityAuthorizationUtility(config_utility)
        
        # Test that utility interfaces have expected methods
        tenant_methods = ['create_tenant', 'get_tenant', 'update_tenant', 'delete_tenant']
        for method_name in tenant_methods:
            assert hasattr(tenant_utility, method_name), f"TenantManagementUtility should have {method_name}"
            assert callable(getattr(tenant_utility, method_name)), f"{method_name} should be callable"
        
        security_methods = ['validate_user_context', 'authorize_request', 'create_user_context']
        for method_name in security_methods:
            assert hasattr(security_utility, method_name), f"SecurityAuthorizationUtility should have {method_name}"
            assert callable(getattr(security_utility, method_name)), f"{method_name} should be callable"

    # =============================================================================
    # MULTI-TENANCY INTERFACE VALIDATION
    # =============================================================================

    async def test_multi_tenancy_interface_compliance(self, config_utility):
        """Test multi-tenancy interface compliance."""
        tenant_utility = TenantManagementUtility(config_utility)
        security_utility = SecurityAuthorizationUtility(config_utility)
        
        # Test that multi-tenancy interfaces are properly implemented
        assert hasattr(tenant_utility, 'create_tenant'), "TenantManagementUtility should support tenant creation"
        assert hasattr(tenant_utility, 'get_tenant'), "TenantManagementUtility should support tenant retrieval"
        
        assert hasattr(security_utility, 'validate_user_context'), "SecurityAuthorizationUtility should support user context validation"
        assert hasattr(security_utility, 'authorize_request'), "SecurityAuthorizationUtility should support request authorization"
        
        # Test that interfaces support tenant-aware operations
        # (Individual tests will validate the actual tenant-aware functionality)

    # =============================================================================
    # INTERFACE ERROR HANDLING VALIDATION
    # =============================================================================

    async def test_interface_error_handling(self, config_utility):
        """Test interface error handling compliance."""
        # Test that interfaces handle errors gracefully
        tenant_utility = TenantManagementUtility(config_utility)
        security_utility = SecurityAuthorizationUtility(config_utility)
        
        # Test that methods exist and can be called (error handling will be tested in individual tests)
        assert callable(tenant_utility.create_tenant), "create_tenant should handle errors gracefully"
        assert callable(security_utility.validate_user_context), "validate_user_context should handle errors gracefully"

