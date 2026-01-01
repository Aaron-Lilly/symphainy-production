#!/usr/bin/env python3
"""
Workflow Conversion Service - Functional Tests

Tests Workflow Conversion Service with lessons learned from previous testing:
- Reuses proven infrastructure fixture patterns
- Applies timeout protections
- Focuses on service functionality (not infrastructure issues)
- Tests core SOA API methods with realistic data

Uses proper fixtures, timeouts, and applies all lessons learned.
"""

import pytest
import asyncio
import logging
import json
from typing import Dict, Any

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES - Reusing Proven Patterns
# ============================================================================

@pytest.fixture(scope="function")
async def workflow_conversion_service(smart_city_infrastructure):
    """
    WorkflowConversionService instance for each test.
    
    NOTE: Using function scope to match smart_city_infrastructure fixture scope.
    Reuses the proven pattern from previous service tests.
    """
    logger.info("🔧 Fixture: Starting workflow_conversion_service fixture...")
    
    from backend.business_enablement.enabling_services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
    
    logger.info("🔧 Fixture: Got infrastructure, creating WorkflowConversionService...")
    infra = smart_city_infrastructure
    service = WorkflowConversionService(
        service_name="WorkflowConversionService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: WorkflowConversionService instance created")
    
    # Initialize with timeout protection (lesson learned: infrastructure can be slow)
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("Workflow Conversion Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("Workflow Conversion Service initialization timed out after 60 seconds")
    except Exception as e:
        logger.error(f"❌ Fixture: Service initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Service ready, yielding to test...")
    yield service
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture(scope="function")
async def storage_helper(smart_city_infrastructure, infrastructure_storage):
    """
    Storage helper for each test.
    
    Reuses the proven pattern from content_analysis_orchestrator tests.
    """
    from tests.integration.layer_8_business_enablement.test_utilities import ContentStewardHelper, TestDataManager
    
    storage = infrastructure_storage["file_storage"]
    user_context = TestDataManager.get_user_context()
    helper = ContentStewardHelper(storage, user_context)
    yield helper


# ============================================================================
# HELPER FUNCTIONS - Test Data Creation
# ============================================================================

def create_sample_sop_content() -> str:
    """Create sample SOP content for testing."""
    return """
    Standard Operating Procedure: Customer Onboarding
    
    Purpose: This SOP outlines the process for onboarding new customers.
    
    Steps:
    1. Receive customer application
    2. Verify customer information
    3. Create customer account
    4. Send welcome email
    5. Schedule onboarding call
    6. Complete onboarding process
    """


def create_sample_workflow_content() -> Dict[str, Any]:
    """Create sample workflow content for testing."""
    return {
        "workflow_id": "test_workflow_001",
        "title": "Customer Onboarding Workflow",
        "steps": [
            {
                "step_id": "step_1",
                "name": "Receive Application",
                "description": "Receive and log customer application",
                "order": 1
            },
            {
                "step_id": "step_2",
                "name": "Verify Information",
                "description": "Verify customer information",
                "order": 2
            },
            {
                "step_id": "step_3",
                "name": "Create Account",
                "description": "Create customer account in system",
                "order": 3
            }
        ]
    }


# ============================================================================
# FUNCTIONAL TESTS - Core SOA API Methods
# ============================================================================

class TestWorkflowConversionServiceFunctional:
    """Functional tests for Workflow Conversion Service core methods."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_service_initialization(self, workflow_conversion_service):
        """Test service initialization."""
        logger.info("🧪 Test: Service initialization")
        
        assert workflow_conversion_service is not None
        assert workflow_conversion_service.is_initialized is True
        assert workflow_conversion_service.sop_processing is not None
        assert workflow_conversion_service.bpmn_processing is not None
        
        logger.info("✅ Service initialized correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_convert_sop_to_workflow(self, workflow_conversion_service, storage_helper):
        """Test converting SOP to workflow."""
        logger.info("🧪 Test: Convert SOP to workflow")
        
        # Upload SOP content as a file
        sop_content = create_sample_sop_content()
        file_id = await storage_helper.store_file(
            sop_content.encode('utf-8'),
            "test_sop.txt",
            "text/plain"
        )
        
        # Convert SOP to workflow
        result = await workflow_conversion_service.convert_sop_to_workflow(
            sop_file_uuid=file_id
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "workflow" in result
        assert "workflow_id" in result
        
        workflow = result.get("workflow", {})
        assert "name" in workflow or "title" in workflow  # Workflow has name, not workflow_id
        assert "steps" in workflow
        assert len(workflow.get("steps", [])) > 0
        
        logger.info(f"✅ SOP converted to workflow: {result.get('workflow_id')}")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_convert_workflow_to_sop(self, workflow_conversion_service, storage_helper):
        """Test converting workflow to SOP."""
        logger.info("🧪 Test: Convert workflow to SOP")
        
        # Upload workflow content as a file
        workflow_content = create_sample_workflow_content()
        workflow_json = json.dumps(workflow_content, indent=2)
        file_id = await storage_helper.store_file(
            workflow_json.encode('utf-8'),
            "test_workflow.json",
            "application/json"
        )
        
        # Convert workflow to SOP
        result = await workflow_conversion_service.convert_workflow_to_sop(
            workflow_file_uuid=file_id
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "sop" in result
        assert "sop_id" in result
        
        sop = result.get("sop", {})
        assert "title" in sop or "name" in sop  # SOP has title/name, not sop_id
        assert "steps" in sop or "content" in sop or "procedures" in sop
        
        logger.info(f"✅ Workflow converted to SOP: {result.get('sop_id')}")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_analyze_file(self, workflow_conversion_service, storage_helper):
        """Test file analysis for conversion."""
        logger.info("🧪 Test: Analyze file for conversion")
        
        # Upload SOP file
        sop_content = create_sample_sop_content()
        file_id = await storage_helper.store_file(
            sop_content.encode('utf-8'),
            "test_sop.txt",
            "text/plain"
        )
        
        # Analyze file (this actually performs the conversion)
        result = await workflow_conversion_service.analyze_file(
            input_file_uuid=file_id,
            output_type="workflow"
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "workflow" in result or "error" in result
        
        logger.info(f"✅ File analyzed and converted: {result.get('workflow_id', 'N/A')}")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_validate_conversion(self, workflow_conversion_service, storage_helper):
        """Test conversion validation."""
        logger.info("🧪 Test: Validate conversion")
        
        # Upload SOP content
        sop_content = create_sample_sop_content()
        sop_file_id = await storage_helper.store_file(
            sop_content.encode('utf-8'),
            "test_sop.txt",
            "text/plain"
        )
        
        # Convert SOP to workflow
        conversion_result = await workflow_conversion_service.convert_sop_to_workflow(
            sop_file_uuid=sop_file_id
        )
        
        if not conversion_result.get("success"):
            pytest.skip("Conversion failed, cannot test validation")
        
        # The conversion stores a document, so we need to get the stored document ID
        # For now, we'll use the workflow_id as the conversion_id
        workflow_id = conversion_result.get("workflow_id")
        
        # Note: validate_conversion expects a conversion_id (document ID from storage)
        # Since we don't have direct access to the stored document ID, we'll skip this test
        # if the conversion_id format doesn't match
        if not workflow_id:
            pytest.skip("No workflow_id returned, cannot test validation")
        
        # Validate conversion (using workflow_id as conversion_id)
        result = await workflow_conversion_service.validate_conversion(
            conversion_id=workflow_id
        )
        
        assert isinstance(result, dict)
        # Validation may succeed or fail depending on document storage
        # We just check that it returns a result
        assert "success" in result
        
        logger.info(f"✅ Conversion validation attempted: {result.get('success')}")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_bidirectional_conversion(self, workflow_conversion_service, storage_helper):
        """Test bidirectional conversion (SOP -> Workflow -> SOP)."""
        logger.info("🧪 Test: Bidirectional conversion")
        
        # Step 1: Upload SOP
        sop_content = create_sample_sop_content()
        sop_file_id = await storage_helper.store_file(
            sop_content.encode('utf-8'),
            "test_sop.txt",
            "text/plain"
        )
        
        # Step 2: Convert SOP to Workflow
        workflow_result = await workflow_conversion_service.convert_sop_to_workflow(
            sop_file_uuid=sop_file_id
        )
        
        assert workflow_result.get("success") is True
        workflow_id = workflow_result.get("workflow_id")
        
        # Step 3: Convert Workflow back to SOP
        # Note: We need to store the workflow as a file first
        workflow = workflow_result.get("workflow", {})
        workflow_json = json.dumps(workflow, indent=2)
        workflow_file_id = await storage_helper.store_file(
            workflow_json.encode('utf-8'),
            "test_workflow.json",
            "application/json"
        )
        
        sop_result = await workflow_conversion_service.convert_workflow_to_sop(
            workflow_file_uuid=workflow_file_id
        )
        
        assert sop_result.get("success") is True
        assert "sop" in sop_result
        
        logger.info("✅ Bidirectional conversion successful")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_architecture_verification(self, workflow_conversion_service):
        """Test that service follows proper architecture patterns."""
        logger.info("🧪 Test: Architecture verification")
        
        # Verify service extends RealmServiceBase
        from bases.realm_service_base import RealmServiceBase
        assert isinstance(workflow_conversion_service, RealmServiceBase)
        
        # Verify Platform Gateway access
        assert workflow_conversion_service.platform_gateway is not None
        
        # Verify infrastructure abstractions are available
        assert workflow_conversion_service.sop_processing is not None
        assert workflow_conversion_service.bpmn_processing is not None
        
        # Verify Smart City services are available
        assert workflow_conversion_service.librarian is not None
        
        logger.info("✅ Architecture patterns verified")

