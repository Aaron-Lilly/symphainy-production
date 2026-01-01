#!/usr/bin/env python3
"""
Transformation Engine Service - Functional Tests

Tests Transformation Engine Service with lessons learned from previous testing:
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
async def transformation_engine_service(smart_city_infrastructure):
    """
    TransformationEngineService instance for each test.
    
    NOTE: Using function scope to match smart_city_infrastructure fixture scope.
    Reuses the proven pattern from previous service tests.
    """
    logger.info("🔧 Fixture: Starting transformation_engine_service fixture...")
    
    from backend.business_enablement.enabling_services.transformation_engine_service.transformation_engine_service import TransformationEngineService
    
    logger.info("🔧 Fixture: Got infrastructure, creating TransformationEngineService...")
    infra = smart_city_infrastructure
    service = TransformationEngineService(
        service_name="TransformationEngineService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: TransformationEngineService instance created")
    
    # Initialize with timeout protection (lesson learned: infrastructure can be slow)
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("Transformation Engine Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("Transformation Engine Service initialization timed out after 60 seconds")
    except Exception as e:
        logger.error(f"❌ Fixture: Service initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Service ready, yielding to test...")
    yield service
    logger.info("✅ Fixture: Test completed, cleaning up...")


# ============================================================================
# HELPER FUNCTIONS - Test Data Creation
# ============================================================================

from tests.integration.layer_8_business_enablement.test_utilities import ContentStewardHelper, TestDataManager

@pytest.fixture(scope="function")
async def storage_helper(smart_city_infrastructure, infrastructure_storage):
    """Content Steward helper for file storage."""
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

class TestTransformationEngineServiceFunctional:
    """Functional tests for Transformation Engine Service core methods."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_service_initialization(self, transformation_engine_service):
        """Test service initialization."""
        logger.info("🧪 Test: Service initialization")
        
        assert transformation_engine_service is not None
        assert transformation_engine_service.is_initialized is True
        
        logger.info("✅ Service initialized correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_transform_data(self, transformation_engine_service, storage_helper):
        """Test transforming data."""
        logger.info("🧪 Test: Transform data")
        
        # Store test data first
        import json
        test_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "balance": 1000.50
        }
        file_id = await storage_helper.store_file(
            file_data=json.dumps(test_data).encode('utf-8'),
            filename="test_data.json",
            content_type="application/json"
        )
        
        transformation_rules = {
            "type": "data_normalization",
            "rules": [
                {"field": "name", "transform": "uppercase"},
                {"field": "email", "transform": "lowercase"}
            ]
        }
        
        result = await transformation_engine_service.transform_data(
            data_id=file_id,
            transformation_rules=transformation_rules
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "transformed_data" in result or "data" in result
        
        logger.info(f"✅ Data transformed successfully")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_convert_format(self, transformation_engine_service, storage_helper):
        """Test converting data format."""
        logger.info("🧪 Test: Convert format")
        
        # Store test data first
        import json
        test_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        file_id = await storage_helper.store_file(
            file_data=json.dumps(test_data).encode('utf-8'),
            filename="test_data.json",
            content_type="application/json"
        )
        
        result = await transformation_engine_service.convert_format(
            data_id=file_id,
            target_format="csv"
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "converted_data" in result or "data" in result
        
        logger.info(f"✅ Format converted successfully")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_map_schema(self, transformation_engine_service, storage_helper):
        """Test mapping data to a different schema."""
        logger.info("🧪 Test: Map schema")
        
        # Store test data first
        import json
        test_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        file_id = await storage_helper.store_file(
            file_data=json.dumps(test_data).encode('utf-8'),
            filename="test_data.json",
            content_type="application/json"
        )
        
        target_schema = {
            "fields": [
                {"name": "full_name", "source": "name"},
                {"name": "years_old", "source": "age"},
                {"name": "email_address", "source": "email"}
            ]
        }
        
        result = await transformation_engine_service.map_schema(
            data_id=file_id,
            target_schema=target_schema
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "mapped_data" in result or "data" in result
        
        logger.info(f"✅ Schema mapped successfully")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_enrich_data(self, transformation_engine_service, storage_helper):
        """Test enriching data with additional information."""
        logger.info("🧪 Test: Enrich data")
        
        # Store test data first
        import json
        test_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        file_id = await storage_helper.store_file(
            file_data=json.dumps(test_data).encode('utf-8'),
            filename="test_data.json",
            content_type="application/json"
        )
        
        # Store enrichment source data
        enrichment_source_data = {
            "status": "active",
            "created_at": "2024-01-01"
        }
        enrichment_source_id = await storage_helper.store_file(
            file_data=json.dumps(enrichment_source_data).encode('utf-8'),
            filename="enrichment_source.json",
            content_type="application/json"
        )
        
        # enrich_data expects a list of enrichment source IDs
        enrichment_sources = [enrichment_source_id]
        
        result = await transformation_engine_service.enrich_data(
            data_id=file_id,
            enrichment_sources=enrichment_sources
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "enriched_data" in result or "enriched_data_id" in result
        
        logger.info(f"✅ Data enriched successfully")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_transform_batch(self, transformation_engine_service, storage_helper):
        """Test batch transformation."""
        logger.info("🧪 Test: Transform batch")
        
        # Store test data batch first
        import json
        data_batch_ids = []
        for i in range(3):
            test_data = {
                "name": f"User {i}",
                "age": 20 + i,
                "email": f"user{i}@example.com"
            }
            file_id = await storage_helper.store_file(
                file_data=json.dumps(test_data).encode('utf-8'),
                filename=f"test_data_{i}.json",
                content_type="application/json"
            )
            data_batch_ids.append(file_id)
        
        transformation_rules = {
            "type": "data_normalization",
            "rules": [
                {"field": "name", "transform": "uppercase"}
            ]
        }
        
        # Create transformation requests
        transformations = [
            {
                "data_id": data_id,
                "transformation_rules": transformation_rules
            }
            for data_id in data_batch_ids
        ]
        
        result = await transformation_engine_service.transform_batch(
            transformations=transformations
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "transformed_batch" in result or "batch" in result or "results" in result
        
        logger.info(f"✅ Batch transformed successfully")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_architecture_verification(self, transformation_engine_service):
        """Test that service follows proper architecture patterns."""
        logger.info("🧪 Test: Architecture verification")
        
        # Verify service extends RealmServiceBase
        from bases.realm_service_base import RealmServiceBase
        assert isinstance(transformation_engine_service, RealmServiceBase)
        
        # Verify Platform Gateway access
        assert transformation_engine_service.platform_gateway is not None
        
        # Verify Smart City services are available
        assert transformation_engine_service.librarian is not None
        assert transformation_engine_service.data_steward is not None
        
        logger.info("✅ Architecture patterns verified")

