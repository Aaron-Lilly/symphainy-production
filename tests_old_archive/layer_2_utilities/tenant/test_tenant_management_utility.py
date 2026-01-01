#!/usr/bin/env python3
"""
Layer 2: Tenant Management Utility Tests

Tests that validate tenant management utility works correctly.

WHAT: Validate tenant management utility
HOW: Test TenantManagementUtility
"""

import pytest

import os
from unittest.mock import Mock, patch

from utilities.tenant.tenant_management_utility import TenantManagementUtility

class TestTenantManagementUtility:
    """Test tenant management utility."""
    
    @pytest.fixture
    def mock_env_loader(self):
        """Create mock environment loader."""
        mock_loader = Mock()
        mock_loader.is_multi_tenant_enabled = Mock(return_value=True)
        mock_loader.get_multi_tenant_config = Mock(return_value={"default_tenant_config": {}})
        return mock_loader
    
    @pytest.fixture
    def tenant_management_utility(self, mock_env_loader):
        """Create tenant management utility instance."""
        return TenantManagementUtility(mock_env_loader)
    
    def test_tenant_management_utility_initialization(self, tenant_management_utility, mock_env_loader):
        """Test that tenant management utility initializes correctly."""
        assert tenant_management_utility is not None
        assert tenant_management_utility.env_loader == mock_env_loader  # Uses env_loader, not config
        assert tenant_management_utility.multi_tenant_enabled is True
    
    def test_get_tenant_config(self, tenant_management_utility):
        """Test getting tenant configuration."""
        config = tenant_management_utility.get_tenant_config("individual")
        
        assert config is not None
        assert "max_users" in config
        assert "features" in config
        assert config["type"] == "individual"
