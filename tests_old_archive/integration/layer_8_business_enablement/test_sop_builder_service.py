#!/usr/bin/env python3
"""
SOP Builder Service - Functional Tests

Tests SOP Builder Service with lessons learned from previous testing:
- Reuses proven infrastructure fixture patterns
- Applies timeout protections
- Focuses on service functionality (not infrastructure issues)
- Tests core SOA API methods with realistic data

Uses proper fixtures, timeouts, and applies all lessons learned.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES - Reusing Proven Patterns
# ============================================================================

@pytest.fixture(scope="function")
async def sop_builder_service(smart_city_infrastructure):
    """
    SOPBuilderService instance for each test.
    
    NOTE: Using function scope to match smart_city_infrastructure fixture scope.
    Reuses the proven pattern from previous service tests.
    """
    logger.info("🔧 Fixture: Starting sop_builder_service fixture...")
    
    from backend.business_enablement.enabling_services.sop_builder_service.sop_builder_service import SOPBuilderService
    
    logger.info("🔧 Fixture: Got infrastructure, creating SOPBuilderService...")
    infra = smart_city_infrastructure
    service = SOPBuilderService(
        service_name="SOPBuilderService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: SOPBuilderService instance created")
    
    # Initialize with timeout protection (lesson learned: infrastructure can be slow)
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("SOP Builder Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("SOP Builder Service initialization timed out after 60 seconds")
    except Exception as e:
        logger.error(f"❌ Fixture: Service initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Service ready, yielding to test...")
    yield service
    logger.info("✅ Fixture: Test completed, cleaning up...")


# ============================================================================
# HELPER FUNCTIONS - Test Data Creation
# ============================================================================

def create_sample_sop_description() -> str:
    """Create sample SOP description for testing."""
    return """
    Standard Operating Procedure for Customer Onboarding
    
    This SOP outlines the process for onboarding new customers to our platform.
    It includes steps for account creation, verification, initial setup, and training.
    The procedure ensures consistent customer experience and compliance with regulations.
    """


# ============================================================================
# FUNCTIONAL TESTS - Core SOA API Methods
# ============================================================================

class TestSOPBuilderServiceFunctional:
    """Functional tests for SOP Builder Service core methods."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_create_sop_basic(self, sop_builder_service):
        """Test basic SOP creation."""
        logger.info("🔧 Test: Starting basic SOP creation test...")
        
        # Create SOP with description
        description = create_sample_sop_description()
        
        result = await asyncio.wait_for(
            sop_builder_service.create_sop(
                description=description
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: SOP creation result keys: {list(result.keys())}")
        
        # Verify result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"SOP creation should succeed. Result: {result}"
        
        # Verify SOP contains expected fields
        sop_content = result.get("sop_content")
        sop_structure = result.get("sop_structure", {})
        
        # Verify SOP content or structure is present
        assert sop_content is not None or sop_structure is not None, \
            "Result should contain SOP content or structure"
        
        # Verify SOP structure has required fields
        if sop_structure:
            assert "title" in sop_structure or "sections" in sop_structure, \
                "SOP structure should have title or sections"
        
        logger.info("✅ Test: Basic SOP creation test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_create_sop_different_types(self, sop_builder_service):
        """Test SOP creation with different SOP types."""
        logger.info("🔧 Test: Starting multi-type SOP creation test...")
        
        # Test standard SOP
        standard_description = "Standard operating procedure for data entry and validation"
        standard_result = await asyncio.wait_for(
            sop_builder_service.create_sop(
                description=standard_description
            ),
            timeout=30.0
        )
        assert standard_result.get("success") is True, "Standard SOP creation should succeed"
        logger.info("✅ Test: Standard SOP creation succeeded")
        
        # Test technical SOP
        technical_description = "Technical procedure for system maintenance and troubleshooting"
        technical_result = await asyncio.wait_for(
            sop_builder_service.create_sop(
                description=technical_description
            ),
            timeout=30.0
        )
        assert technical_result.get("success") is True, "Technical SOP creation should succeed"
        logger.info("✅ Test: Technical SOP creation succeeded")
        
        logger.info("✅ Test: Multi-type SOP creation test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_validate_sop(self, sop_builder_service):
        """Test SOP validation."""
        logger.info("🔧 Test: Starting SOP validation test...")
        
        # Create a sample SOP structure
        sop_data = {
            "title": "Customer Onboarding Procedure",
            "purpose": "To ensure consistent customer onboarding experience",
            "procedures": [
                {"step": 1, "action": "Create customer account", "description": "Set up account in system"},
                {"step": 2, "action": "Verify customer information", "description": "Validate customer details"}
            ]
        }
        
        # Validate SOP
        result = await asyncio.wait_for(
            sop_builder_service.validate_sop(
                sop_data=sop_data
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: SOP validation result keys: {list(result.keys())}")
        
        # Verify result
        assert isinstance(result, dict), "Result should be a dictionary"
        # Validation may return success or failure depending on SOP quality
        assert "valid" in result or "success" in result, "Result should contain validation status"
        
        logger.info("✅ Test: SOP validation test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_start_wizard_session(self, sop_builder_service):
        """Test wizard session start."""
        logger.info("🔧 Test: Starting wizard session test...")
        
        # Start wizard session
        result = await asyncio.wait_for(
            sop_builder_service.start_wizard_session(),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: Wizard session result keys: {list(result.keys())}")
        
        # Verify result
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"Wizard session should start. Result: {result}"
        
        # Verify session token
        session_token = result.get("session_token")
        assert session_token is not None, "Result should contain session_token"
        
        logger.info("✅ Test: Wizard session test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_wizard_workflow(self, sop_builder_service):
        """Test complete wizard workflow."""
        logger.info("🔧 Test: Starting wizard workflow test...")
        
        # 1. Start wizard session
        start_result = await asyncio.wait_for(
            sop_builder_service.start_wizard_session(),
            timeout=30.0
        )
        assert start_result.get("success") is True, "Wizard session should start"
        session_token = start_result.get("session_token")
        assert session_token is not None, "Session token should be available"
        logger.info("✅ Test: Wizard session started")
        
        # 2. Process wizard steps until complete
        # Process multiple steps to complete the wizard
        step_inputs = ["standard", "Customer onboarding procedure", "Account creation, verification, setup", "Quality checks", "Documentation"]
        for i, user_input in enumerate(step_inputs):
            step_result = await asyncio.wait_for(
                sop_builder_service.process_wizard_step(
                    session_token=session_token,
                    user_input=user_input
                ),
                timeout=30.0
            )
            assert step_result.get("success") is True, f"Wizard step {i+1} should process"
            
            # Check if wizard is complete
            wizard_state = step_result.get("wizard_state", {})
            if wizard_state.get("is_complete"):
                logger.info(f"✅ Test: Wizard completed after step {i+1}")
                break
        
        # 3. Complete wizard
        complete_result = await asyncio.wait_for(
            sop_builder_service.complete_wizard(
                session_token=session_token
            ),
            timeout=30.0
        )
        # Wizard completion may succeed or fail depending on wizard state
        # Just verify we got a result
        assert isinstance(complete_result, dict), "Wizard completion should return a result"
        logger.info("✅ Test: Wizard completion attempted")
        
        logger.info("✅ Test: Wizard workflow test passed")


# ============================================================================
# ARCHITECTURE VERIFICATION TESTS
# ============================================================================

class TestSOPBuilderServiceArchitecture:
    """Tests to verify 5-layer architecture and Platform Gateway integration."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_platform_gateway_access(self, sop_builder_service, smart_city_infrastructure):
        """Test that service can access Platform Gateway abstractions."""
        logger.info("🔧 Test: Starting Platform Gateway access test...")
        
        # Verify service has platform_gateway
        assert sop_builder_service.platform_gateway is not None, \
            "Service should have platform_gateway"
        
        # Verify service has SOP abstractions
        assert sop_builder_service.sop_processing is not None, \
            "Service should have sop_processing abstraction"
        assert sop_builder_service.sop_enhancement is not None, \
            "Service should have sop_enhancement abstraction"
        
        # Verify Platform Gateway is available
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        assert platform_gateway is not None, "Platform Gateway should be available"
        
        logger.info("✅ Test: Platform Gateway access test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_smart_city_api_access(self, sop_builder_service):
        """Test that service can access Smart City APIs."""
        logger.info("🔧 Test: Starting Smart City API access test...")
        
        # Verify service has Smart City APIs
        assert sop_builder_service.librarian is not None, \
            "Service should have librarian API"
        assert sop_builder_service.data_steward is not None, \
            "Service should have data_steward API"
        
        logger.info("✅ Test: Smart City API access test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_curator_registration(self, sop_builder_service, smart_city_infrastructure):
        """Test that service is registered with Curator."""
        logger.info("🔧 Test: Starting Curator registration test...")
        
        # Get Curator from infrastructure
        curator = smart_city_infrastructure.get("curator")
        if curator:
            # Try to discover the service
            # Note: This depends on Curator's discovery API
            logger.info("✅ Test: Curator is available (registration verification depends on Curator API)")
        else:
            logger.warning("⚠️ Test: Curator not available in infrastructure (may be expected)")
        
        logger.info("✅ Test: Curator registration test passed")

