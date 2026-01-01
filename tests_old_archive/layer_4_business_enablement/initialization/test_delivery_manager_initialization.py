#!/usr/bin/env python3
"""
Business Enablement Delivery Manager Initialization Tests

Validates that Delivery Manager can be initialized correctly.
Tests that Delivery Manager:
- Can be instantiated with DI Container
- Has required attributes
- Can orchestrate all pillars
- Follows ManagerServiceBase patterns
"""

import pytest

import os
from unittest.mock import Mock, MagicMock

from foundations.di_container.di_container_service import DIContainerService

@pytest.mark.business_enablement
class TestDeliveryManagerInitialization:
    """Test Delivery Manager can be initialized."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock(spec=DIContainerService)
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=None)
        return gateway
    
    def test_delivery_manager_can_be_instantiated(self, mock_di_container, mock_platform_gateway):
        """Test that Delivery Manager can be instantiated."""
        try:
            from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
            
            service = DeliveryManagerService(
                di_container=mock_di_container,
                platform_gateway=mock_platform_gateway
            )
            assert service is not None, "DeliveryManagerService should be instantiated"
        except ImportError as e:
            pytest.skip(f"Could not import DeliveryManagerService: {e}")
        except Exception as e:
            pytest.fail(f"DeliveryManagerService failed to instantiate: {e}")
    
    def test_delivery_manager_has_di_container(self, mock_di_container, mock_platform_gateway):
        """Test that Delivery Manager has di_container attribute."""
        try:
            from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
            
            service = DeliveryManagerService(
                di_container=mock_di_container,
                platform_gateway=mock_platform_gateway
            )
            assert hasattr(service, 'di_container'), \
                "DeliveryManagerService should have di_container attribute"
            assert service.di_container == mock_di_container, \
                "DeliveryManagerService should have correct di_container"
        except ImportError:
            pytest.skip("Could not import DeliveryManagerService")
        except Exception as e:
            pytest.fail(f"DeliveryManagerService failed: {e}")
    
    def test_delivery_manager_extends_manager_service_base(self, mock_di_container, mock_platform_gateway):
        """Test that Delivery Manager extends ManagerServiceBase."""
        try:
            from bases.manager_service_base import ManagerServiceBase
            from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
            
            service = DeliveryManagerService(
                di_container=mock_di_container,
                platform_gateway=mock_platform_gateway
            )
            assert isinstance(service, ManagerServiceBase), \
                "DeliveryManagerService should extend ManagerServiceBase"
        except ImportError:
            pytest.skip("Could not import DeliveryManagerService")
        except Exception as e:
            pytest.fail(f"DeliveryManagerService failed: {e}")
    
    def test_delivery_manager_has_pillar_orchestrators(self, mock_di_container, mock_platform_gateway):
        """Test that Delivery Manager has MVP pillar orchestrators."""
        try:
            from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
            
            service = DeliveryManagerService(
                di_container=mock_di_container,
                platform_gateway=mock_platform_gateway
            )
            assert hasattr(service, 'mvp_pillar_orchestrators'), \
                "DeliveryManagerService should have mvp_pillar_orchestrators attribute"
            assert isinstance(service.mvp_pillar_orchestrators, dict), \
                "mvp_pillar_orchestrators should be a dictionary"
        except ImportError:
            pytest.skip("Could not import DeliveryManagerService")
        except Exception as e:
            pytest.fail(f"DeliveryManagerService failed: {e}")

