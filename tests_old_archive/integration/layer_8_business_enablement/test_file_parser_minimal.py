#!/usr/bin/env python3
"""
Minimal File Parser Test - Isolate Issues

This is a minimal test to isolate where the timeout is occurring.
Tests infrastructure initialization step by step.
"""

import pytest
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration]


class TestFileParserMinimal:
    """Minimal tests to isolate timeout issues."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(180)
    async def test_infrastructure_available(self, smart_city_infrastructure):
        """Test 1: Just verify infrastructure fixture works."""
        logger.info("✅ Test 1: Infrastructure fixture initialized successfully")
        assert smart_city_infrastructure is not None
        assert "di_container" in smart_city_infrastructure
        assert "public_works_foundation" in smart_city_infrastructure
        logger.info("✅ Test 1: Infrastructure fixture verified")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(180)
    async def test_service_initialization(self, smart_city_infrastructure):
        """Test 2: Just initialize the service (no file operations)."""
        logger.info("🔧 Test 2: Starting service initialization...")
        
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        infra = smart_city_infrastructure
        logger.info("✅ Test 2: Got infrastructure")
        
        logger.info("🔧 Test 2: Creating FileParserService instance...")
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=infra["platform_gateway"],
            di_container=infra["di_container"]
        )
        logger.info("✅ Test 2: FileParserService instance created")
        
        logger.info("🔧 Test 2: Initializing service (this may take time)...")
        try:
            result = await asyncio.wait_for(service.initialize(), timeout=60.0)
            logger.info(f"✅ Test 2: Service initialized, result: {result}")
            assert result is True, "Service should initialize successfully"
        except asyncio.TimeoutError:
            logger.error("❌ Test 2: Service initialization timed out after 60 seconds")
            pytest.fail("Service initialization timed out")
        except Exception as e:
            logger.error(f"❌ Test 2: Service initialization failed: {e}")
            raise
        
        logger.info("✅ Test 2: Service initialization test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(180)
    async def test_storage_helper(self, smart_city_infrastructure, infrastructure_storage):
        """Test 3: Just test storage helper (no file parsing)."""
        logger.info("🔧 Test 3: Testing storage helper...")
        
        from tests.integration.layer_8_business_enablement.test_utilities import (
            ContentStewardHelper,
            TestDataManager
        )
        
        storage = infrastructure_storage["file_storage"]
        logger.info("✅ Test 3: Got storage")
        
        user_context = TestDataManager.get_user_context()
        logger.info("✅ Test 3: Got user context")
        
        helper = ContentStewardHelper(storage, user_context)
        logger.info("✅ Test 3: Created ContentStewardHelper")
        
        # Just verify helper is ready (don't store anything yet)
        assert helper is not None
        assert helper.storage is not None
        logger.info("✅ Test 3: Storage helper test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_create_test_file(self):
        """Test 4: Just create a test file (no storage, no parsing)."""
        logger.info("🔧 Test 4: Creating test Excel file...")
        
        from tests.integration.layer_8_business_enablement.test_file_helpers import (
            create_test_excel_file
        )
        
        try:
            excel_data, filename = create_test_excel_file()
            logger.info(f"✅ Test 4: Created test file: {filename}, size: {len(excel_data)} bytes")
            assert excel_data is not None
            assert len(excel_data) > 0
            assert filename.endswith('.xlsx')
            logger.info("✅ Test 4: Test file creation passed")
        except Exception as e:
            logger.error(f"❌ Test 4: Test file creation failed: {e}")
            raise

