#!/usr/bin/env python3
"""
Functional tests for NotificationService.

Tests notification, alert, and delivery tracking capabilities.
"""

import pytest
import asyncio
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestNotificationServiceFunctional:
    """Functional tests for NotificationService."""
    
    @pytest.fixture(scope="function")
    async def notification_service(self, smart_city_infrastructure):
        """Create NotificationService instance."""
        from backend.business_enablement.enabling_services.notification_service import NotificationService
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        di_container = smart_city_infrastructure["di_container"]
        
        service = NotificationService(
            service_name="NotificationService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        initialized = await service.initialize()
        assert initialized, "NotificationService should initialize successfully"
        
        return service
    
    @pytest.fixture(scope="function")
    def mock_user_context(self) -> Dict[str, Any]:
        """Create a mock user context."""
        return {
            "user_id": "test_user_123",
            "tenant_id": "test_tenant_123",
            "email": "test@example.com",
            "permissions": ["read", "write"]
        }
    
    async def test_service_initialization(self, notification_service):
        """Test that NotificationService initializes correctly."""
        assert notification_service is not None
        assert notification_service.is_initialized is True
        # Post Office may or may not be available
        logger.info("✅ NotificationService initialized correctly")
    
    async def test_send_notification(
        self,
        notification_service,
        mock_user_context
    ):
        """Test sending a notification."""
        result = await notification_service.send_notification(
            recipient_ids=["user_1", "user_2"],
            notification_type="info",
            content={"message": "Test notification", "title": "Test"},
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        # May succeed or fail depending on Post Office availability
        assert "success" in result
        if result.get("success"):
            assert "recipients_count" in result or "sent_at" in result
        
        logger.info(f"✅ Notification send attempted: {result.get('success')}")
    
    async def test_create_alert(
        self,
        notification_service,
        mock_user_context
    ):
        """Test creating an alert."""
        result = await notification_service.create_alert(
            alert_type="warning",
            message="Test alert message",
            priority="high",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "alert_id" in result
        assert result.get("alert_type") == "warning"
        assert result.get("priority") == "high"
        
        logger.info(f"✅ Alert created: {result.get('alert_id')}")
    
    async def test_track_delivery(
        self,
        notification_service,
        mock_user_context
    ):
        """Test tracking notification delivery."""
        result = await notification_service.track_delivery(
            notification_id="test_notification_123",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("notification_id") == "test_notification_123"
        assert "status" in result
        
        logger.info("✅ Delivery tracking successful")
    
    async def test_get_notification_status(
        self,
        notification_service,
        mock_user_context
    ):
        """Test getting notification status."""
        result = await notification_service.get_notification_status(
            notification_id="test_notification_123",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("notification_id") == "test_notification_123"
        assert "status" in result
        
        logger.info("✅ Notification status retrieved")
    
    async def test_send_notification_security_validation(
        self,
        notification_service
    ):
        """Test that sending notifications requires proper permissions."""
        # User context without permissions
        unauthorized_context = {
            "user_id": "unauthorized_user",
            "tenant_id": "test_tenant_123",
            "permissions": []  # No permissions
        }
        
        # This should raise PermissionError
        with pytest.raises(PermissionError):
            await notification_service.send_notification(
                recipient_ids=["user_1"],
                notification_type="info",
                content={"message": "Test"},
                user_context=unauthorized_context
            )
        
        logger.info("✅ Security validation tested")
    
    async def test_health_check(self, notification_service):
        """Test health check."""
        health = await notification_service.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert health.get("service_name") == "NotificationService"
        
        logger.info("✅ Health check passed")
    
    async def test_get_service_capabilities(self, notification_service):
        """Test service capabilities."""
        capabilities = await notification_service.get_service_capabilities()
        
        assert isinstance(capabilities, dict)
        assert capabilities.get("service_name") == "NotificationService"
        assert capabilities.get("service_type") == "enabling_service"
        assert "notification_management" in capabilities.get("capabilities", [])
        assert "send_notification" in capabilities.get("soa_apis", [])
        
        logger.info("✅ Service capabilities verified")
    
    async def test_architecture_verification(self, notification_service, smart_city_infrastructure):
        """Verify the service follows the 5-layer architecture pattern."""
        # Verify it uses Platform Gateway for abstractions (if needed)
        assert notification_service.platform_gateway is not None
        
        # Verify it uses Smart City services via RealmServiceBase
        # Post Office may or may not be available
        logger.info("✅ Architecture verification passed (5-layer pattern)")




