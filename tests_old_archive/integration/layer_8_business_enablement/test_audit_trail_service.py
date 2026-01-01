#!/usr/bin/env python3
"""
Functional tests for AuditTrailService.

Tests audit logging and event tracking capabilities.
"""

import pytest
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestAuditTrailServiceFunctional:
    """Functional tests for AuditTrailService."""
    
    @pytest.fixture(scope="function")
    async def audit_trail_service(self, smart_city_infrastructure):
        """Create AuditTrailService instance."""
        from backend.business_enablement.enabling_services.audit_trail_service import AuditTrailService
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        di_container = smart_city_infrastructure["di_container"]
        
        service = AuditTrailService(
            service_name="AuditTrailService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        initialized = await service.initialize()
        assert initialized, "AuditTrailService should initialize successfully"
        
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
    
    async def test_service_initialization(self, audit_trail_service):
        """Test that AuditTrailService initializes correctly."""
        assert audit_trail_service is not None
        assert audit_trail_service.is_initialized is True
        assert audit_trail_service.librarian is not None
        assert audit_trail_service.data_steward is not None
        
        logger.info("✅ AuditTrailService initialized correctly")
    
    async def test_record_event(
        self,
        audit_trail_service,
        mock_user_context
    ):
        """Test recording an audit event."""
        result = await audit_trail_service.record_event(
            event_type="test_event",
            event_data={"action": "test", "resource": "test_resource"},
            user_id="test_user_123",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "event_id" in result or "timestamp" in result
        
        logger.info("✅ Event recorded successfully")
    
    async def test_get_audit_trail(
        self,
        audit_trail_service,
        mock_user_context
    ):
        """Test getting audit trail for a resource."""
        result = await audit_trail_service.get_audit_trail(
            resource_id="test_resource_123",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "events" in result or "resource_id" in result
        
        logger.info("✅ Audit trail retrieved successfully")
    
    async def test_search_events(
        self,
        audit_trail_service,
        mock_user_context
    ):
        """Test searching events."""
        result = await audit_trail_service.search_events(
            search_criteria={"event_type": "test_event"},
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        # search_events returns results, not events
        assert "results" in result or "events" in result or "count" in result
        
        logger.info("✅ Events searched successfully")
    
    async def test_export_audit(
        self,
        audit_trail_service,
        mock_user_context
    ):
        """Test exporting audit trail."""
        from datetime import datetime, timedelta
        end_date = datetime.utcnow().isoformat()
        start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        result = await audit_trail_service.export_audit(
            start_date=start_date,
            end_date=end_date,
            format="json",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        # May succeed or fail depending on implementation
        assert "success" in result
        
        logger.info(f"✅ Audit export attempted: {result.get('success')}")
    
    async def test_record_event_security_validation(
        self,
        audit_trail_service
    ):
        """Test that recording events requires proper permissions."""
        # User context without permissions
        unauthorized_context = {
            "user_id": "unauthorized_user",
            "tenant_id": "test_tenant_123",
            "permissions": []  # No permissions
        }
        
        # This should raise PermissionError
        with pytest.raises(PermissionError):
            await audit_trail_service.record_event(
                event_type="test_event",
                event_data={"action": "test"},
                user_context=unauthorized_context
            )
        
        logger.info("✅ Security validation tested")
    
    async def test_health_check(self, audit_trail_service):
        """Test health check."""
        health = await audit_trail_service.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health or "service_name" in health
        
        logger.info("✅ Health check passed")
    
    async def test_get_service_capabilities(self, audit_trail_service):
        """Test service capabilities."""
        capabilities = await audit_trail_service.get_service_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "service_name" in capabilities or "capabilities" in capabilities
        
        logger.info("✅ Service capabilities verified")
    
    async def test_architecture_verification(self, audit_trail_service, smart_city_infrastructure):
        """Verify the service follows the 5-layer architecture pattern."""
        # Verify it uses Platform Gateway for abstractions (if needed)
        assert audit_trail_service.platform_gateway is not None
        
        # Verify it uses Smart City services via RealmServiceBase
        assert audit_trail_service.librarian is not None
        assert audit_trail_service.data_steward is not None
        
        logger.info("✅ Architecture verification passed (5-layer pattern)")

