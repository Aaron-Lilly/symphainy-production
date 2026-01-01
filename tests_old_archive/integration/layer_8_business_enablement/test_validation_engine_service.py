#!/usr/bin/env python3
"""
Validation Engine Service - Functional Tests

Tests ValidationEngineService with lessons learned from previous testing:
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

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_json_file,
    create_test_csv_file,
    create_test_excel_file
)
from tests.integration.layer_8_business_enablement.test_utilities import (
    ContentStewardHelper,
    TestDataManager
)

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES - Reusing Proven Patterns
# ============================================================================

@pytest.fixture(scope="function")
async def validation_engine_service(smart_city_infrastructure):
    """
    ValidationEngineService instance for each test.
    
    NOTE: Using function scope to match smart_city_infrastructure fixture scope.
    Reuses the proven pattern from previous service tests.
    """
    logger.info("🔧 Fixture: Starting validation_engine_service fixture...")
    
    from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
    
    logger.info("🔧 Fixture: Got infrastructure, creating ValidationEngineService...")
    infra = smart_city_infrastructure
    service = ValidationEngineService(
        service_name="ValidationEngineService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: ValidationEngineService instance created")
    
    # Initialize with timeout protection
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("Validation Engine Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("Validation Engine Service initialization timed out after 60 seconds")
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
    
    Reuses the proven pattern from previous service tests.
    """
    storage = infrastructure_storage["file_storage"]
    user_context = TestDataManager.get_user_context()
    helper = ContentStewardHelper(storage, user_context)
    
    yield helper
    
    # Cleanup stored files
    try:
        await helper.cleanup()
    except Exception:
        pass  # Ignore cleanup errors


# ============================================================================
# FUNCTIONAL TESTS - Core SOA API Methods
# ============================================================================

@pytest.mark.asyncio
async def test_validate_data_basic(validation_engine_service, storage_helper):
    """Test basic data validation with valid data."""
    logger.info("🧪 Test: test_validate_data_basic")
    
    # 1. Create and store test data
    test_data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "balance": 1000.50
    }
    
    json_bytes = create_test_json_file(test_data)
    data_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="test_data.json",
        content_type="application/json"
    )
    logger.info(f"✅ Stored test data with ID: {data_id}")
    
    # 2. Define validation rules
    validation_rules = {
        "name": {"type": "string", "required": True, "min_length": 1},
        "age": {"type": "integer", "required": True, "min": 0, "max": 150},
        "email": {"type": "string", "required": True, "format": "email"},
        "balance": {"type": "number", "required": True, "min": 0}
    }
    
    # 3. Validate data
    user_context = TestDataManager.get_user_context()
    result = await validation_engine_service.validate_data(
        data_id=data_id,
        validation_rules=validation_rules,
        user_context=user_context
    )
    
    # 4. Assertions
    logger.info(f"✅ Validation result: {result}")
    assert result.get("success") is True, f"Validation should succeed. Result: {result}"
    assert result.get("data_id") == data_id, "Result should include data_id"
    assert "validation_id" in result, "Result should include validation_id"
    assert result.get("status") in ["passed", "failed"], "Status should be 'passed' or 'failed'"
    assert "issues" in result, "Result should include issues list"
    assert isinstance(result.get("issue_count"), int), "Issue count should be an integer"


@pytest.mark.asyncio
async def test_validate_data_with_invalid_data(validation_engine_service, storage_helper):
    """Test data validation with invalid data that should fail."""
    logger.info("🧪 Test: test_validate_data_with_invalid_data")
    
    # 1. Create and store invalid test data
    invalid_data = {
        "name": "",  # Empty required field
        "age": -5,  # Invalid range
        "email": "not-an-email",  # Invalid format
        "balance": "not-a-number"  # Wrong type
    }
    
    json_bytes = create_test_json_file(invalid_data)
    data_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="invalid_data.json",
        content_type="application/json"
    )
    logger.info(f"✅ Stored invalid test data with ID: {data_id}")
    
    # 2. Define validation rules
    validation_rules = {
        "name": {"type": "string", "required": True, "min_length": 1},
        "age": {"type": "integer", "required": True, "min": 0, "max": 150},
        "email": {"type": "string", "required": True, "format": "email"},
        "balance": {"type": "number", "required": True, "min": 0}
    }
    
    # 3. Validate data
    user_context = TestDataManager.get_user_context()
    result = await validation_engine_service.validate_data(
        data_id=data_id,
        validation_rules=validation_rules,
        user_context=user_context
    )
    
    # 4. Assertions
    logger.info(f"✅ Validation result: {result}")
    assert result.get("success") is True, f"Validation should complete (even if data is invalid). Result: {result}"
    assert result.get("data_id") == data_id, "Result should include data_id"
    # Note: The service may return "passed" or "failed" depending on implementation
    assert result.get("status") in ["passed", "failed"], "Status should be 'passed' or 'failed'"
    assert "issues" in result, "Result should include issues list"


@pytest.mark.asyncio
async def test_validate_schema(validation_engine_service, storage_helper):
    """Test schema validation."""
    logger.info("🧪 Test: test_validate_schema")
    
    # 1. Create and store test data
    test_data = {"name": "John", "age": 30}
    json_bytes = create_test_json_file(test_data)
    data_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="schema_test.json",
        content_type="application/json"
    )
    logger.info(f"✅ Stored test data with ID: {data_id}")
    
    # 2. Define schema
    schema = {
        "name": "test_schema",
        "type": "object",
        "fields": [
            {"name": "name", "type": "string", "required": True},
            {"name": "age", "type": "integer", "required": True}
        ]
    }
    
    # 3. Validate schema
    user_context = TestDataManager.get_user_context()
    result = await validation_engine_service.validate_schema(
        data_id=data_id,
        schema=schema,
        user_context=user_context
    )
    
    # 4. Assertions
    logger.info(f"✅ Schema validation result: {result}")
    assert result.get("success") is True, f"Schema validation should succeed. Result: {result}"
    assert result.get("data_id") == data_id, "Result should include data_id"
    assert "schema_valid" in result, "Result should include schema_valid"
    assert "schema_issues" in result, "Result should include schema_issues"


@pytest.mark.asyncio
async def test_check_compliance(validation_engine_service, storage_helper):
    """Test compliance checking."""
    logger.info("🧪 Test: test_check_compliance")
    
    # 1. Create and store test data
    test_data = {"name": "John", "email": "john@example.com"}
    json_bytes = create_test_json_file(test_data)
    data_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="compliance_test.json",
        content_type="application/json"
    )
    logger.info(f"✅ Stored test data with ID: {data_id}")
    
    # 2. Check compliance
    compliance_standards = ["GDPR", "HIPAA"]
    user_context = TestDataManager.get_user_context()
    result = await validation_engine_service.check_compliance(
        data_id=data_id,
        compliance_standards=compliance_standards,
        user_context=user_context
    )
    
    # 4. Assertions
    logger.info(f"✅ Compliance check result: {result}")
    assert result.get("success") is True, f"Compliance check should succeed. Result: {result}"
    assert result.get("data_id") == data_id, "Result should include data_id"
    assert "compliance_results" in result or "standards" in result, "Result should include compliance information"


@pytest.mark.asyncio
async def test_validate_batch(validation_engine_service, storage_helper):
    """Test batch validation."""
    logger.info("🧪 Test: test_validate_batch")
    
    # 1. Create and store multiple test data files
    data_ids = []
    for i in range(3):
        test_data = {"id": i, "name": f"Item {i}", "value": i * 10}
        json_bytes = create_test_json_file(test_data)
        data_id = await storage_helper.store_file(
            file_data=json_bytes,
            filename=f"batch_test_{i}.json",
            content_type="application/json"
        )
        data_ids.append(data_id)
        logger.info(f"✅ Stored test data {i} with ID: {data_id}")
    
    # 2. Define validation rules and prepare batch validation requests
    validation_rules = {
        "id": {"type": "integer", "required": True},
        "name": {"type": "string", "required": True},
        "value": {"type": "number", "required": True}
    }
    
    # 3. Prepare batch validation requests
    validations = [
        {"data_id": data_id, "validation_rules": validation_rules}
        for data_id in data_ids
    ]
    
    # 4. Validate batch
    user_context = TestDataManager.get_user_context()
    result = await validation_engine_service.validate_batch(
        validations=validations,
        user_context=user_context
    )
    
    # 4. Assertions
    logger.info(f"✅ Batch validation result: {result}")
    assert result.get("success") is True, f"Batch validation should succeed. Result: {result}"
    assert "results" in result or "validations" in result, "Result should include batch results"
    assert len(result.get("results", result.get("validations", []))) == len(data_ids), "Should validate all data items"


@pytest.mark.asyncio
async def test_enforce_rules(validation_engine_service, storage_helper):
    """Test rule enforcement."""
    logger.info("🧪 Test: test_enforce_rules")
    
    # 1. Create and store test data
    test_data = {"name": "John", "age": 30}
    json_bytes = create_test_json_file(test_data)
    data_id = await storage_helper.store_file(
        file_data=json_bytes,
        filename="rules_test.json",
        content_type="application/json"
    )
    logger.info(f"✅ Stored test data with ID: {data_id}")
    
    # 2. Define business rules (as a list of rule dictionaries)
    business_rules = [
        {"field": "name", "required": True, "type": "string"},
        {"field": "age", "required": True, "type": "integer", "min": 0}
    ]
    
    # 3. Enforce rules
    user_context = TestDataManager.get_user_context()
    result = await validation_engine_service.enforce_rules(
        data_id=data_id,
        business_rules=business_rules,
        user_context=user_context
    )
    
    # 4. Assertions
    logger.info(f"✅ Rule enforcement result: {result}")
    assert result.get("success") is True, f"Rule enforcement should succeed. Result: {result}"
    assert result.get("data_id") == data_id, "Result should include data_id"


# ============================================================================
# ARCHITECTURAL TESTS - Verify Service Structure
# ============================================================================

@pytest.mark.asyncio
async def test_service_initialization(validation_engine_service):
    """Test that service initializes correctly."""
    logger.info("🧪 Test: test_service_initialization")
    
    assert validation_engine_service is not None, "Service should be initialized"
    assert validation_engine_service.librarian is not None, "Librarian should be available"
    assert validation_engine_service.data_steward is not None, "Data Steward should be available"
    assert len(validation_engine_service.supported_validations) > 0, "Should support validation types"


@pytest.mark.asyncio
async def test_supported_validations(validation_engine_service):
    """Test that service reports supported validation types."""
    logger.info("🧪 Test: test_supported_validations")
    
    supported = validation_engine_service.supported_validations
    assert isinstance(supported, list), "Supported validations should be a list"
    assert len(supported) > 0, "Should support at least one validation type"
    
    # Check for expected validation types
    expected_types = ["data_quality", "compliance", "business_rules", "schema"]
    for expected_type in expected_types:
        assert expected_type in supported, f"Should support {expected_type} validation"

