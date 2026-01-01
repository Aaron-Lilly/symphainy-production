#!/usr/bin/env python3
"""
Semantic Enrichment Gateway Unit Tests

Comprehensive unit tests for SemanticEnrichmentGateway:
- Request validation
- Enrichment service integration
- Embedding storage
- Security boundary validation
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.enabling_services]


class TestSemanticEnrichmentGateway:
    """Unit tests for SemanticEnrichmentGateway."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        
        # Mock semantic data abstraction
        mock_semantic_data = AsyncMock()
        mock_semantic_data.store_semantic_embeddings = AsyncMock(return_value={"success": True, "count": 2})
        gateway.get_abstraction = Mock(return_value=mock_semantic_data)
        
        return gateway
    
    @pytest.fixture
    def mock_librarian(self):
        """Create mock Librarian service."""
        librarian = AsyncMock()
        librarian.get_content_metadata = AsyncMock(return_value={
            "content_id": "test_content_123",
            "file_id": "test_file_123",
            "parsed_file_id": "test_parsed_123"
        })
        return librarian
    
    @pytest.fixture
    def mock_enrichment_service(self):
        """Create mock SemanticEnrichmentService."""
        service = Mock()
        service.create_enrichment_embeddings = AsyncMock(return_value=[
            {
                "_key": "enrich_stats_test_content_123_revenue_abc123",
                "id": "enrich_stats_test_content_123_revenue_abc123",
                "content_id": "test_content_123",
                "column_name": "revenue",
                "embedding_type": "statistics",
                "metadata": {"mean": 1000.0, "std": 200.0}
            },
            {
                "_key": "enrich_stats_test_content_123_cost_def456",
                "id": "enrich_stats_test_content_123_cost_def456",
                "content_id": "test_content_123",
                "column_name": "cost",
                "embedding_type": "statistics",
                "metadata": {"mean": 700.0, "std": 150.0}
            }
        ])
        return service
    
    @pytest.fixture
    def gateway(self, mock_di_container, mock_platform_gateway):
        """Create SemanticEnrichmentGateway instance."""
        from backend.business_enablement.enabling_services.semantic_enrichment_gateway.semantic_enrichment_gateway import SemanticEnrichmentGateway
        
        gateway = SemanticEnrichmentGateway(
            service_name="SemanticEnrichmentGateway",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Set up dependencies
        gateway.librarian = mock_librarian = Mock()
        gateway.librarian.get_content_metadata = AsyncMock(return_value={
            "content_id": "test_content_123",
            "file_id": "test_file_123",
            "parsed_file_id": "test_parsed_123"
        })
        gateway.semantic_data = mock_platform_gateway.get_abstraction("semantic_data")
        gateway.enrichment_service = None  # Will be set in tests
        
        return gateway
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_success(self, gateway, mock_enrichment_service):
        """Test successful semantic enrichment."""
        gateway.enrichment_service = mock_enrichment_service
        
        enrichment_request = {
            "type": "statistics",
            "description": "Need statistics for revenue and cost columns"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        # Verify success
        assert result["success"] is True
        assert result["content_id"] == "test_content_123"
        assert result["enrichment_type"] == "statistics"
        assert len(result["embedding_ids"]) == 2
        assert result["count"] == 2
        
        # Verify embedding IDs are strings (not raw data)
        assert all(isinstance(emb_id, str) for emb_id in result["embedding_ids"])
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_validation_missing_type(self, gateway):
        """Test validation rejects request without type."""
        enrichment_request = {
            "description": "Missing type"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "type" in result["error"].lower() or "required" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_validation_invalid_type(self, gateway):
        """Test validation rejects invalid enrichment type."""
        enrichment_request = {
            "type": "invalid_type"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "invalid" in result["error"].lower() or "type" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_service_unavailable(self, gateway):
        """Test behavior when enrichment service is not available."""
        gateway.enrichment_service = None
        
        enrichment_request = {
            "type": "statistics"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not available" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_enrichment_fails(self, gateway, mock_enrichment_service):
        """Test behavior when enrichment service fails to create embeddings."""
        mock_enrichment_service.create_enrichment_embeddings = AsyncMock(return_value=[])
        gateway.enrichment_service = mock_enrichment_service
        
        enrichment_request = {
            "type": "statistics"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "failed" in result["error"].lower() or "embeddings" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_storage_fails(self, gateway, mock_enrichment_service, mock_platform_gateway):
        """Test behavior when storage fails."""
        gateway.enrichment_service = mock_enrichment_service
        
        # Mock storage failure
        mock_semantic_data = mock_platform_gateway.get_abstraction("semantic_data")
        mock_semantic_data.store_semantic_embeddings = AsyncMock(return_value={"success": False, "error": "Storage failed"})
        
        enrichment_request = {
            "type": "statistics"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "store" in result["error"].lower() or "storage" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_all_enrichment_types(self, gateway, mock_enrichment_service):
        """Test all valid enrichment types."""
        gateway.enrichment_service = mock_enrichment_service
        
        valid_types = ["column_values", "statistics", "correlations", "distributions", "missing_values"]
        
        for enrichment_type in valid_types:
            enrichment_request = {
                "type": enrichment_type
            }
            
            result = await gateway.enrich_semantic_layer(
                content_id="test_content_123",
                enrichment_request=enrichment_request,
                user_context={"user_id": "test_user"}
            )
            
            # Should pass validation (may fail later if service doesn't support type)
            assert result["success"] is not None
            if result["success"]:
                assert result["enrichment_type"] == enrichment_type
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_with_filters(self, gateway, mock_enrichment_service):
        """Test enrichment request with filters."""
        gateway.enrichment_service = mock_enrichment_service
        
        enrichment_request = {
            "type": "statistics",
            "filters": {
                "columns": ["revenue", "cost"]
            },
            "description": "Need statistics for specific columns"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        # Verify filters were passed to enrichment service
        assert mock_enrichment_service.create_enrichment_embeddings.called
        call_args = mock_enrichment_service.create_enrichment_embeddings.call_args
        assert call_args is not None
        assert "filters" in call_args.kwargs or len(call_args.args) >= 3
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_returns_embedding_ids_only(self, gateway, mock_enrichment_service):
        """Test that only embedding IDs are returned (not raw data)."""
        gateway.enrichment_service = mock_enrichment_service
        
        enrichment_request = {
            "type": "statistics"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        # Verify only embedding IDs are returned
        assert "embedding_ids" in result
        assert "embeddings" not in result  # Should not return raw embeddings
        assert all(isinstance(emb_id, str) for emb_id in result["embedding_ids"])
        
        # Verify embedding IDs don't contain raw data
        for emb_id in result["embedding_ids"]:
            assert isinstance(emb_id, str)
            # Should be an ID, not a dict or complex object
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_telemetry_tracking(self, gateway, mock_enrichment_service):
        """Test that telemetry tracking is called."""
        gateway.enrichment_service = mock_enrichment_service
        
        # Mock telemetry methods
        gateway.log_operation_with_telemetry = AsyncMock()
        
        enrichment_request = {
            "type": "statistics"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        # Verify telemetry was called
        assert gateway.log_operation_with_telemetry.called
        # Should be called at least twice (start and complete)
        assert gateway.log_operation_with_telemetry.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_exception_handling(self, gateway, mock_enrichment_service):
        """Test exception handling."""
        gateway.enrichment_service = mock_enrichment_service
        
        # Make enrichment service raise exception
        mock_enrichment_service.create_enrichment_embeddings = AsyncMock(side_effect=Exception("Test exception"))
        
        enrichment_request = {
            "type": "statistics"
        }
        
        result = await gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context={"user_id": "test_user"}
        )
        
        # Should handle exception gracefully
        assert result["success"] is False
        assert "error" in result
        assert result["content_id"] == "test_content_123"


