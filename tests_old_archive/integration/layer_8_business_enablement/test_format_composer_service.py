#!/usr/bin/env python3
"""
Functional tests for FormatComposerService.

Tests format composition capabilities for AI-friendly formats.
"""

import pytest
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestFormatComposerServiceFunctional:
    """Functional tests for FormatComposerService."""
    
    @pytest.fixture(scope="function")
    async def format_composer_service(self, smart_city_infrastructure):
        """Create FormatComposerService instance."""
        from backend.business_enablement.enabling_services.format_composer_service import FormatComposerService
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        di_container = smart_city_infrastructure["di_container"]
        
        service = FormatComposerService(
            service_name="FormatComposerService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        initialized = await service.initialize()
        assert initialized, "FormatComposerService should initialize successfully"
        
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
    
    @pytest.fixture(scope="function")
    def sample_parsed_data_structured(self) -> Dict[str, Any]:
        """Create sample parsed data for structured content (CSV/Excel)."""
        return {
            "text_content": "Name,Age,City\nAlice,24,New York\nBob,35,San Francisco",
            "structured_data": {
                "tables": [
                    {
                        "rows": [
                            ["Name", "Age", "City"],
                            ["Alice", 24, "New York"],
                            ["Bob", 35, "San Francisco"]
                        ]
                    }
                ]
            },
            "metadata": {
                "file_type": "csv",
                "row_count": 2,
                "column_count": 3
            }
        }
    
    @pytest.fixture(scope="function")
    def sample_parsed_data_unstructured(self) -> Dict[str, Any]:
        """Create sample parsed data for unstructured content (PDF/Word)."""
        return {
            "text_content": "This is a sample document. It contains multiple paragraphs. Each paragraph has some text content.",
            "metadata": {
                "file_type": "pdf",
                "page_count": 1
            }
        }
    
    async def test_service_initialization(self, format_composer_service):
        """Test that FormatComposerService initializes correctly."""
        assert format_composer_service is not None
        assert format_composer_service.is_initialized is True
        assert format_composer_service.parquet_composer is not None
        assert format_composer_service.json_structured_composer is not None
        assert format_composer_service.json_chunks_composer is not None
        assert format_composer_service.content_steward is not None
        
        logger.info("✅ FormatComposerService initialized correctly")
    
    async def test_compose_format_parquet(
        self,
        format_composer_service,
        sample_parsed_data_structured,
        mock_user_context
    ):
        """Test composing structured data to Parquet format."""
        result = await format_composer_service.compose_format(
            parsed_data=sample_parsed_data_structured,
            target_format="parquet",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "composed_data" in result
        # Format is in metadata or target_format in result
        assert result.get("target_format") == "parquet" or result.get("metadata", {}).get("format") == "parquet"
        
        logger.info("✅ Parquet format composition successful")
    
    async def test_compose_format_json_structured(
        self,
        format_composer_service,
        sample_parsed_data_structured,
        mock_user_context
    ):
        """Test composing structured data to JSON Structured format."""
        result = await format_composer_service.compose_format(
            parsed_data=sample_parsed_data_structured,
            target_format="json_structured",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "composed_data" in result
        # Format is in metadata or target_format in result
        assert result.get("target_format") == "json_structured" or result.get("metadata", {}).get("format") == "json_structured"
        
        logger.info("✅ JSON Structured format composition successful")
    
    async def test_compose_format_json_chunks(
        self,
        format_composer_service,
        sample_parsed_data_unstructured,
        mock_user_context
    ):
        """Test composing unstructured data to JSON Chunks format."""
        result = await format_composer_service.compose_format(
            parsed_data=sample_parsed_data_unstructured,
            target_format="json_chunks",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "composed_data" in result or "chunks" in result
        # Format is in metadata or target_format in result
        assert result.get("target_format") == "json_chunks" or result.get("metadata", {}).get("format") == "json_chunks"
        
        logger.info("✅ JSON Chunks format composition successful")
    
    async def test_compose_format_unsupported(
        self,
        format_composer_service,
        sample_parsed_data_structured,
        mock_user_context
    ):
        """Test composing with unsupported format."""
        result = await format_composer_service.compose_format(
            parsed_data=sample_parsed_data_structured,
            target_format="unsupported_format",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "unsupported" in result.get("error", "").lower() or "unsupported" in result.get("message", "").lower()
        
        logger.info("✅ Unsupported format correctly rejected")
    
    async def test_get_recommended_format_csv(
        self,
        format_composer_service,
        mock_user_context
    ):
        """Test getting recommended format for CSV file."""
        result = await format_composer_service.get_recommended_format(
            file_type="csv",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("recommended_format") == "parquet"
        assert "rationale" in result
        
        logger.info("✅ Format recommendation for CSV successful")
    
    async def test_get_recommended_format_pdf(
        self,
        format_composer_service,
        mock_user_context
    ):
        """Test getting recommended format for PDF file."""
        result = await format_composer_service.get_recommended_format(
            file_type="pdf",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("recommended_format") == "json_chunks"
        assert "rationale" in result
        
        logger.info("✅ Format recommendation for PDF successful")
    
    async def test_get_recommended_format_mainframe(
        self,
        format_composer_service,
        mock_user_context
    ):
        """Test getting recommended format for mainframe file."""
        result = await format_composer_service.get_recommended_format(
            file_type="mainframe_copybook",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("recommended_format") == "json_structured"
        assert "rationale" in result
        
        logger.info("✅ Format recommendation for mainframe successful")
    
    async def test_get_supported_formats(
        self,
        format_composer_service,
        mock_user_context
    ):
        """Test getting supported formats."""
        result = await format_composer_service.get_supported_formats(
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "supported_formats" in result
        assert "parquet" in result.get("supported_formats", [])
        assert "json_structured" in result.get("supported_formats", [])
        assert "json_chunks" in result.get("supported_formats", [])
        assert "format_descriptions" in result
        
        logger.info("✅ Supported formats retrieved successfully")
    
    async def test_health_check(self, format_composer_service):
        """Test health check."""
        # health_check is provided by PerformanceMonitoringMixin
        # It may return None if health utility is not initialized
        health = await format_composer_service.health_check()
        if health is None:
            pytest.skip("health_check returned None (health utility may not be initialized)")
        assert isinstance(health, dict)
        # PerformanceMonitoringMixin returns health_data - check for any key
        assert len(health) > 0
        logger.info(f"✅ Health check passed: {list(health.keys())[:3]}")
    
    async def test_get_service_capabilities(self, format_composer_service):
        """Test service capabilities."""
        # get_service_capabilities is provided by PerformanceMonitoringMixin
        capabilities = await format_composer_service.get_service_capabilities()
        if capabilities is None:
            pytest.skip("get_service_capabilities returned None")
        assert isinstance(capabilities, dict)
        # PerformanceMonitoringMixin returns service metadata - check for any key
        assert len(capabilities) > 0
        logger.info(f"✅ Service capabilities verified: {list(capabilities.keys())[:3]}")
    
    async def test_architecture_verification(self, format_composer_service, smart_city_infrastructure):
        """Verify the service follows the 5-layer architecture pattern."""
        # Verify it uses Platform Gateway for abstractions (if needed)
        assert format_composer_service.platform_gateway is not None
        
        # Verify it uses Smart City services via RealmServiceBase
        assert format_composer_service.content_steward is not None
        
        # Verify it uses micro-modules for format composition
        assert format_composer_service.parquet_composer is not None
        assert format_composer_service.json_structured_composer is not None
        assert format_composer_service.json_chunks_composer is not None
        
        logger.info("✅ Architecture verification passed (5-layer pattern)")

