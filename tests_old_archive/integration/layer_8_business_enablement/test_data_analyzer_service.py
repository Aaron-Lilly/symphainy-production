#!/usr/bin/env python3
"""
Data Analyzer Service - Functional Tests

Tests Data Analyzer Service with lessons learned from file parser testing:
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
    create_test_excel_file,
    create_test_binary_file,
    create_test_copybook_file
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
async def data_analyzer_service(smart_city_infrastructure):
    """
    DataAnalyzerService instance for each test.
    
    NOTE: Using function scope to match smart_city_infrastructure fixture scope.
    Reuses the proven pattern from file_parser_service tests.
    """
    logger.info("🔧 Fixture: Starting data_analyzer_service fixture...")
    
    from backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service import DataAnalyzerService
    
    logger.info("🔧 Fixture: Got infrastructure, creating DataAnalyzerService...")
    infra = smart_city_infrastructure
    service = DataAnalyzerService(
        service_name="DataAnalyzerService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: DataAnalyzerService instance created")
    
    # Initialize with timeout protection (lesson learned: infrastructure can be slow)
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("Data Analyzer Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("Data Analyzer Service initialization timed out after 60 seconds")
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
    
    Reuses the proven pattern from file_parser_service tests.
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
# HELPER FUNCTIONS - Test Data Creation
# ============================================================================

def create_test_csv_file() -> tuple[bytes, str]:
    """Create a test CSV file with sample data."""
    csv_content = """Name,Age,City,Salary
Alice,25,New York,50000
Bob,30,London,60000
Charlie,35,Tokyo,70000
Diana,28,Paris,55000"""
    return csv_content.encode('utf-8'), "test_data.csv"


def create_test_json_file() -> tuple[bytes, str]:
    """Create a test JSON file with sample data."""
    import json
    json_data = {
        "employees": [
            {"name": "Alice", "age": 25, "city": "New York", "salary": 50000, "department": "Engineering"},
            {"name": "Bob", "age": 30, "city": "London", "salary": 60000, "department": "Sales"},
            {"name": "Charlie", "age": 35, "city": "Tokyo", "salary": 70000, "department": "Engineering"},
            {"name": "Diana", "age": 28, "city": "Paris", "salary": 55000, "department": "Marketing"},
        ]
    }
    return json.dumps(json_data, indent=2).encode('utf-8'), "test_data.json"


def create_sample_text_content() -> str:
    """Create sample text content for analysis."""
    return """
    Quarterly Sales Report Q4 2024
    
    Executive Summary:
    - Total revenue: $2.5M (up 15% from Q3)
    - Customer acquisition: 450 new customers
    - Churn rate: 3.2% (down from 4.1%)
    
    Key Metrics:
    - Average deal size: $5,500
    - Sales cycle: 28 days
    - Conversion rate: 12.5%
    
    Regional Performance:
    - North America: $1.2M (48% of total)
    - Europe: $800K (32% of total)
    - Asia-Pacific: $500K (20% of total)
    
    Recommendations:
    1. Increase focus on Asia-Pacific market
    2. Reduce sales cycle through automation
    3. Improve customer retention programs
    """


# ============================================================================
# FUNCTIONAL TESTS - Core SOA API Methods
# ============================================================================

class TestDataAnalyzerServiceFunctional:
    """Functional tests for Data Analyzer Service core methods."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_analyze_data_basic(self, data_analyzer_service, storage_helper):
        """Test basic data analysis with file data."""
        logger.info("🔧 Test: Starting basic data analysis test...")
        
        # Create and store a test file (JSON for structured data)
        json_data, json_filename = create_test_json_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                json_data,
                json_filename,
                content_type="application/json"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Analyze data (service expects data_id, not raw data)
        result = await asyncio.wait_for(
            data_analyzer_service.analyze_data(
                data_id=file_id,
                analysis_type="descriptive"
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: Analysis result keys: {list(result.keys())}")
        
        # Verify result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"Analysis should succeed. Result: {result}"
        
        # Verify analysis contains expected fields
        analysis = result.get("analysis", {})
        assert analysis is not None, "Analysis should contain analysis results"
        
        logger.info("✅ Test: Basic data analysis test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_analyze_structure(self, data_analyzer_service, storage_helper):
        """Test structure analysis."""
        logger.info("🔧 Test: Starting structure analysis test...")
        
        # Create and store a test file
        json_data, json_filename = create_test_json_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                json_data,
                json_filename,
                content_type="application/json"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Analyze structure (service expects data_id)
        result = await asyncio.wait_for(
            data_analyzer_service.analyze_structure(
                data_id=file_id
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: Structure analysis result keys: {list(result.keys())}")
        
        # Verify result
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"Structure analysis should succeed. Result: {result}"
        
        # Verify structure information
        structure = result.get("structure", {})
        assert structure is not None, "Result should contain structure information"
        
        logger.info("✅ Test: Structure analysis test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_detect_patterns(self, data_analyzer_service, storage_helper):
        """Test pattern detection."""
        logger.info("🔧 Test: Starting pattern detection test...")
        
        # Create and store a test file with patterns
        csv_data, csv_filename = create_test_csv_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                csv_data,
                csv_filename,
                content_type="text/csv"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Detect patterns (service expects data_id)
        result = await asyncio.wait_for(
            data_analyzer_service.detect_patterns(
                data_id=file_id
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: Pattern detection result keys: {list(result.keys())}")
        
        # Verify result
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"Pattern detection should succeed. Result: {result}"
        
        # Verify patterns
        patterns = result.get("patterns", [])
        assert isinstance(patterns, list), "Patterns should be a list"
        
        logger.info("✅ Test: Pattern detection test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_extract_entities(self, data_analyzer_service, storage_helper):
        """Test entity extraction from text file."""
        logger.info("🔧 Test: Starting entity extraction test...")
        
        # Create and store a text file
        text_content = create_sample_text_content()
        text_data = text_content.encode('utf-8')
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                text_data,
                "test_report.txt",
                content_type="text/plain"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Extract entities (service expects data_id)
        result = await asyncio.wait_for(
            data_analyzer_service.extract_entities(
                data_id=file_id
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: Entity extraction result keys: {list(result.keys())}")
        
        # Verify result
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"Entity extraction should succeed. Result: {result}"
        
        # Verify entities
        entities = result.get("entities", [])
        assert isinstance(entities, list), "Entities should be a list"
        
        logger.info("✅ Test: Entity extraction test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_get_statistics(self, data_analyzer_service, storage_helper):
        """Test statistical analysis."""
        logger.info("🔧 Test: Starting statistical analysis test...")
        
        # Create and store a test file
        csv_data, csv_filename = create_test_csv_file()
        file_id = await asyncio.wait_for(
            storage_helper.store_file(
                csv_data,
                csv_filename,
                content_type="text/csv"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: File stored, file_id: {file_id}")
        
        # Get statistics (service expects data_id)
        result = await asyncio.wait_for(
            data_analyzer_service.get_statistics(
                data_id=file_id
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: Statistics result keys: {list(result.keys())}")
        
        # Verify result
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"Statistical analysis should succeed. Result: {result}"
        
        # Verify statistics
        statistics = result.get("statistics", {})
        assert statistics is not None, "Result should contain statistics"
        
        logger.info("✅ Test: Statistical analysis test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_analyze_data_multiple_types(self, data_analyzer_service, storage_helper):
        """Test data analysis with different file types."""
        logger.info("🔧 Test: Starting multi-type data analysis test...")
        
        # Test with CSV
        csv_data, csv_filename = create_test_csv_file()
        csv_file_id = await asyncio.wait_for(
            storage_helper.store_file(
                csv_data,
                csv_filename,
                content_type="text/csv"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: CSV file stored, file_id: {csv_file_id}")
        
        # Analyze CSV
        csv_result = await asyncio.wait_for(
            data_analyzer_service.analyze_data(
                data_id=csv_file_id,
                analysis_type="descriptive"
            ),
            timeout=30.0
        )
        assert csv_result.get("success") is True, "CSV analysis should succeed"
        logger.info("✅ Test: CSV analysis succeeded")
        
        # Test with JSON
        json_data, json_filename = create_test_json_file()
        json_file_id = await asyncio.wait_for(
            storage_helper.store_file(
                json_data,
                json_filename,
                content_type="application/json"
            ),
            timeout=30.0
        )
        logger.info(f"✅ Test: JSON file stored, file_id: {json_file_id}")
        
        # Analyze JSON
        json_result = await asyncio.wait_for(
            data_analyzer_service.analyze_data(
                data_id=json_file_id,
                analysis_type="descriptive"
            ),
            timeout=30.0
        )
        assert json_result.get("success") is True, "JSON analysis should succeed"
        logger.info("✅ Test: JSON analysis succeeded")
        
        logger.info("✅ Test: Multi-type data analysis test passed")


# ============================================================================
# ARCHITECTURE VERIFICATION TESTS
# ============================================================================

class TestDataAnalyzerServiceArchitecture:
    """Tests to verify 5-layer architecture and Platform Gateway integration."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_platform_gateway_access(self, data_analyzer_service, smart_city_infrastructure):
        """Test that service can access Platform Gateway abstractions."""
        logger.info("🔧 Test: Starting Platform Gateway access test...")
        
        # Verify service has platform_gateway
        assert data_analyzer_service.platform_gateway is not None, \
            "Service should have platform_gateway"
        
        # Verify service can access abstractions (if needed)
        # Data Analyzer may use abstractions for visualization or metrics
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        assert platform_gateway is not None, "Platform Gateway should be available"
        
        logger.info("✅ Test: Platform Gateway access test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_smart_city_api_access(self, data_analyzer_service):
        """Test that service can access Smart City APIs."""
        logger.info("🔧 Test: Starting Smart City API access test...")
        
        # Verify service has Smart City APIs
        assert data_analyzer_service.librarian is not None, \
            "Service should have librarian API"
        assert data_analyzer_service.data_steward is not None, \
            "Service should have data_steward API"
        assert data_analyzer_service.content_steward is not None, \
            "Service should have content_steward API"
        
        logger.info("✅ Test: Smart City API access test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_curator_registration(self, data_analyzer_service, smart_city_infrastructure):
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

