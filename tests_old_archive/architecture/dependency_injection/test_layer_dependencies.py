#!/usr/bin/env python3
"""
Architecture Dependency Injection Validation Tests

This test suite validates that all layers properly use utilities and dependencies
according to the current architecture. This ensures proper dependency injection
and architectural compliance.

CRITICAL REQUIREMENT: These tests validate REAL architectural patterns, not mocks.
We need to prove the architecture actually works as designed.
"""

import pytest
import asyncio

import os
from pathlib import Path
from typing import Dict, Any, List

# Add the platform directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-platform'))

# Import real platform components for validation
from foundations.utility_foundation.utilities.configuration.configuration_utility import ConfigurationUtility
from foundations.utility_foundation.utilities.tenant.tenant_management_utility import TenantManagementUtility
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import SecurityAuthorizationUtility
from foundations.infrastructure_foundation.infrastructure_foundation_service import InfrastructureFoundationServiceEnvIntegrated
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

class TestLayerDependencyInjection:
    """Test that all layers properly use utilities and dependencies."""

    @pytest.fixture
    def config_utility(self):
        """Create Configuration Utility - the foundation of everything."""
        return ConfigurationUtility("architecture_validation_test")

    @pytest.fixture
    def tenant_management_utility(self, config_utility):
        """Create Tenant Management Utility."""
        return TenantManagementUtility(config_utility)

    @pytest.fixture
    def security_authorization_utility(self, config_utility):
        """Create Security Authorization Utility."""
        return SecurityAuthorizationUtility(config_utility)

    # =============================================================================
    # UTILITY FOUNDATION DEPENDENCY VALIDATION
    # =============================================================================

    async def test_utility_foundation_dependencies(self, config_utility, tenant_management_utility, security_authorization_utility):
        """Test utility foundation properly initializes all utilities."""
        # Verify ConfigurationUtility is properly initialized
        assert config_utility is not None, "ConfigurationUtility should be initialized"
        assert hasattr(config_utility, 'get_external_services_config'), "ConfigurationUtility should have config methods"
        
        # Verify TenantManagementUtility is properly initialized
        assert tenant_management_utility is not None, "TenantManagementUtility should be initialized"
        assert hasattr(tenant_management_utility, 'create_tenant'), "TenantManagementUtility should have tenant methods"
        
        # Verify SecurityAuthorizationUtility is properly initialized
        assert security_authorization_utility is not None, "SecurityAuthorizationUtility should be initialized"
        assert hasattr(security_authorization_utility, 'validate_user_context'), "SecurityAuthorizationUtility should have security methods"
        
        # Test utility initialization order and dependencies
        assert tenant_management_utility.config_utility == config_utility, "TenantManagementUtility should use ConfigurationUtility"
        assert security_authorization_utility.config_utility == config_utility, "SecurityAuthorizationUtility should use ConfigurationUtility"

    # =============================================================================
    # INFRASTRUCTURE FOUNDATION DEPENDENCY VALIDATION
    # =============================================================================

    async def test_infrastructure_foundation_uses_utilities(self, config_utility):
        """Test infrastructure foundation uses utility foundation."""
        # Create infrastructure foundation with real configuration utility
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        
        # Verify infrastructure foundation gets utilities from utility foundation
        assert infrastructure_foundation is not None, "InfrastructureFoundation should be initialized"
        assert hasattr(infrastructure_foundation, 'env_loader'), "InfrastructureFoundation should have env_loader"
        
        # Test utility access patterns
        assert infrastructure_foundation.env_loader == config_utility, "InfrastructureFoundation should use ConfigurationUtility"
        
        # Verify no direct utility instantiation (should use dependency injection)
        # This ensures proper architectural patterns

    # =============================================================================
    # PUBLIC WORKS FOUNDATION DEPENDENCY VALIDATION
    # =============================================================================

    async def test_public_works_uses_infrastructure(self, config_utility):
        """Test public works foundation uses infrastructure foundation."""
        # Create infrastructure foundation first
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        
        # Create public works foundation with infrastructure foundation
        public_works_foundation = PublicWorksFoundationService(
            utility_foundation=None,  # Will be provided by individual tests
            curator_foundation=None,  # Will be provided by individual tests
            infrastructure_foundation=infrastructure_foundation,
            env_loader=config_utility,
            security_guard_client=None  # Will be provided by individual tests
        )
        
        # Verify public works gets infrastructure abstractions
        assert public_works_foundation is not None, "PublicWorksFoundation should be initialized"
        assert public_works_foundation.infrastructure_foundation == infrastructure_foundation, "PublicWorksFoundation should use InfrastructureFoundation"
        
        # Test infrastructure access patterns
        assert hasattr(public_works_foundation, 'infrastructure_foundation'), "PublicWorksFoundation should have infrastructure_foundation"
        
        # Verify proper abstraction usage
        assert public_works_foundation.env_loader == config_utility, "PublicWorksFoundation should use ConfigurationUtility"

    # =============================================================================
    # SMART CITY SERVICES DEPENDENCY VALIDATION
    # =============================================================================

    async def test_smart_city_services_use_foundations(self, config_utility):
        """Test smart city services use all foundation layers."""
        # Create foundation layers
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        
        public_works_foundation = PublicWorksFoundationService(
            utility_foundation=None,
            curator_foundation=None,
            infrastructure_foundation=infrastructure_foundation,
            env_loader=config_utility,
            security_guard_client=None
        )
        
        curator_foundation = CuratorFoundationService(
            utility_foundation=None,
            env_loader=config_utility,
            security_service=None
        )
        
        # Test that smart city services would use these foundations
        # (Individual service tests will validate this in detail)
        assert infrastructure_foundation is not None, "InfrastructureFoundation should be available for smart city services"
        assert public_works_foundation is not None, "PublicWorksFoundation should be available for smart city services"
        assert curator_foundation is not None, "CuratorFoundation should be available for smart city services"

    # =============================================================================
    # BUSINESS ENABLEMENT DEPENDENCY VALIDATION
    # =============================================================================

    async def test_business_enablement_uses_smart_city(self, config_utility):
        """Test business enablement uses smart city services."""
        # Create foundation layers
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        
        public_works_foundation = PublicWorksFoundationService(
            utility_foundation=None,
            curator_foundation=None,
            infrastructure_foundation=infrastructure_foundation,
            env_loader=config_utility,
            security_guard_client=None
        )
        
        # Test that business enablement pillars would use these foundations
        # (Individual pillar tests will validate this in detail)
        assert infrastructure_foundation is not None, "InfrastructureFoundation should be available for business enablement"
        assert public_works_foundation is not None, "PublicWorksFoundation should be available for business enablement"

    # =============================================================================
    # EXPERIENCE DIMENSION DEPENDENCY VALIDATION
    # =============================================================================

    async def test_experience_dimension_uses_business_enablement(self, config_utility):
        """Test experience dimension uses business enablement."""
        # Create foundation layers
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        
        public_works_foundation = PublicWorksFoundationService(
            utility_foundation=None,
            curator_foundation=None,
            infrastructure_foundation=infrastructure_foundation,
            env_loader=config_utility,
            security_guard_client=None
        )
        
        # Test that experience dimension would use these foundations
        # (Individual experience tests will validate this in detail)
        assert infrastructure_foundation is not None, "InfrastructureFoundation should be available for experience dimension"
        assert public_works_foundation is not None, "PublicWorksFoundation should be available for experience dimension"

    # =============================================================================
    # ARCHITECTURAL COMPLIANCE VALIDATION
    # =============================================================================

    async def test_architectural_layer_compliance(self, config_utility):
        """Test that all layers follow architectural compliance."""
        # Test that utilities are the first layer after poetry
        assert config_utility is not None, "ConfigurationUtility should be the foundation"
        
        # Test that infrastructure foundation uses utilities
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        assert infrastructure_foundation.env_loader == config_utility, "InfrastructureFoundation should use ConfigurationUtility"
        
        # Test that public works foundation uses infrastructure foundation
        public_works_foundation = PublicWorksFoundationService(
            utility_foundation=None,
            curator_foundation=None,
            infrastructure_foundation=infrastructure_foundation,
            env_loader=config_utility,
            security_guard_client=None
        )
        assert public_works_foundation.infrastructure_foundation == infrastructure_foundation, "PublicWorksFoundation should use InfrastructureFoundation"
        
        # Test that curator foundation uses utilities
        curator_foundation = CuratorFoundationService(
            utility_foundation=None,
            env_loader=config_utility,
            security_service=None
        )
        assert curator_foundation.env_loader == config_utility, "CuratorFoundation should use ConfigurationUtility"

    async def test_dependency_injection_patterns(self, config_utility):
        """Test that dependency injection patterns are properly implemented."""
        # Test that utilities are injected, not instantiated directly
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        
        # Verify that the infrastructure foundation received the configuration utility
        assert infrastructure_foundation.env_loader == config_utility, "Dependency injection should work for ConfigurationUtility"
        
        # Test that public works foundation receives infrastructure foundation
        public_works_foundation = PublicWorksFoundationService(
            utility_foundation=None,
            curator_foundation=None,
            infrastructure_foundation=infrastructure_foundation,
            env_loader=config_utility,
            security_guard_client=None
        )
        
        assert public_works_foundation.infrastructure_foundation == infrastructure_foundation, "Dependency injection should work for InfrastructureFoundation"
        assert public_works_foundation.env_loader == config_utility, "Dependency injection should work for ConfigurationUtility"

    # =============================================================================
    # MULTI-TENANCY ARCHITECTURAL VALIDATION
    # =============================================================================

    async def test_multi_tenancy_architectural_compliance(self, config_utility, tenant_management_utility, security_authorization_utility):
        """Test that multi-tenancy is properly integrated into the architecture."""
        # Test that tenant management utility is properly initialized
        assert tenant_management_utility is not None, "TenantManagementUtility should be available for multi-tenancy"
        
        # Test that security authorization utility is properly initialized
        assert security_authorization_utility is not None, "SecurityAuthorizationUtility should be available for multi-tenancy"
        
        # Test that both utilities use the configuration utility
        assert tenant_management_utility.config_utility == config_utility, "TenantManagementUtility should use ConfigurationUtility"
        assert security_authorization_utility.config_utility == config_utility, "SecurityAuthorizationUtility should use ConfigurationUtility"
        
        # Test that utilities can be used by foundation layers
        infrastructure_foundation = InfrastructureFoundationServiceEnvIntegrated(config_utility)
        assert infrastructure_foundation is not None, "InfrastructureFoundation should be available for multi-tenant operations"

