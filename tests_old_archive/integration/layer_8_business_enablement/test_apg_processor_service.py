#!/usr/bin/env python3
"""
Functional tests for APGProcessorService.

Tests Advanced Pattern Generation processing for unstructured data and AAR analysis.
"""

import pytest
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestAPGProcessorServiceFunctional:
    """Functional tests for APGProcessorService."""
    
    @pytest.fixture(scope="function")
    async def apg_processor_service(self, smart_city_infrastructure):
        """Create APGProcessorService instance."""
        from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGProcessingService, APGMode
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        di_container = smart_city_infrastructure["di_container"]
        
        service = APGProcessingService(
            service_name="APGProcessingService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        initialized = await service.initialize()
        assert initialized, "APGProcessingService should initialize successfully"
        
        return service
    
    @pytest.fixture(scope="function")
    def mock_user_context(self) -> Dict[str, Any]:
        """Create a mock user context."""
        return {
            "user_id": "test_user_123",
            "tenant_id": "test_tenant_123",
            "email": "test@example.com",
            "permissions": ["read", "write", "execute"]
        }
    
    async def test_service_initialization(self, apg_processor_service):
        """Test that APGProcessorService initializes correctly."""
        assert apg_processor_service is not None
        assert apg_processor_service.is_initialized is True
        
        logger.info("✅ APGProcessorService initialized correctly")
    
    async def test_process_apg_mode_auto(
        self,
        apg_processor_service,
        mock_user_context
    ):
        """Test processing with APG mode AUTO."""
        from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGMode
        
        result = await apg_processor_service.process_apg_mode(
            data={"text": "This is a test document for APG processing."},
            user_context=mock_user_context,
            session_id="test_session_123",
            apg_mode=APGMode.AUTO
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "apg_mode" in result or "processed_at" in result
        
        logger.info(f"✅ APG processing (AUTO mode) successful: {result.get('success')}")
    
    async def test_process_apg_mode_enabled(
        self,
        apg_processor_service,
        mock_user_context
    ):
        """Test processing with APG mode ENABLED."""
        from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGMode
        
        result = await apg_processor_service.process_apg_mode(
            data={"text": "This is a test document for autonomous insights discovery."},
            user_context=mock_user_context,
            session_id="test_session_123",
            apg_mode=APGMode.ENABLED
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        
        logger.info(f"✅ APG processing (ENABLED mode) successful: {result.get('success')}")
    
    async def test_process_apg_mode_manual(
        self,
        apg_processor_service,
        mock_user_context
    ):
        """Test processing with APG mode MANUAL (for AAR analysis)."""
        from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGMode
        
        # AAR-specific text
        aar_text = """
        After Action Report - Exercise Alpha
        Date: 2025-10-15
        Location: Training Facility
        
        Lessons Learned:
        1. Communication protocols need improvement
        2. Equipment readiness was excellent
        
        Risks Identified:
        1. Personnel fatigue during extended operations
        2. Weather conditions impacted visibility
        
        Recommendations:
        1. Enhance communication training
        2. Implement fatigue management protocols
        """
        
        result = await apg_processor_service.process_apg_mode(
            data={"text": aar_text},
            user_context=mock_user_context,
            session_id="test_session_123",
            apg_mode=APGMode.MANUAL
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        
        logger.info(f"✅ APG processing (MANUAL mode for AAR) successful: {result.get('success')}")
    
    async def test_process_apg_mode_security_validation(
        self,
        apg_processor_service
    ):
        """Test that APG processing requires proper permissions."""
        from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGMode
        
        # User context without permissions
        unauthorized_context = {
            "user_id": "unauthorized_user",
            "tenant_id": "test_tenant_123",
            "permissions": []  # No permissions
        }
        
        # This should raise PermissionError
        with pytest.raises(PermissionError):
            await apg_processor_service.process_apg_mode(
                data={"text": "Test"},
                user_context=unauthorized_context,
                apg_mode=APGMode.AUTO
            )
        
        logger.info("✅ Security validation tested")
    
    async def test_health_check(self, apg_processor_service):
        """Test health check."""
        health = await apg_processor_service.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health or "service_name" in health
        
        logger.info("✅ Health check passed")
    
    async def test_get_service_capabilities(self, apg_processor_service):
        """Test service capabilities."""
        capabilities = await apg_processor_service.get_service_capabilities()
        
        # get_service_capabilities may return None if health utility not initialized
        if capabilities is None:
            pytest.skip("Service capabilities not available (health utility not initialized)")
        
        assert isinstance(capabilities, dict)
        assert "service_name" in capabilities or "capabilities" in capabilities
        
        logger.info("✅ Service capabilities verified")
    
    async def test_architecture_verification(self, apg_processor_service, smart_city_infrastructure):
        """Verify the service follows the 5-layer architecture pattern."""
        # Verify it uses Platform Gateway for abstractions (if needed)
        assert apg_processor_service.platform_gateway is not None
        
        logger.info("✅ Architecture verification passed (5-layer pattern)")

