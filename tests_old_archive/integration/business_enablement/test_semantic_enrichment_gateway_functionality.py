#!/usr/bin/env python3
"""
Functional Test: SemanticEnrichmentGateway

This test verifies that SemanticEnrichmentGateway can:
1. Validate enrichment requests
2. Request enrichment from secure boundary service
3. Store enriched embeddings in semantic layer
4. Return embedding IDs (not raw data)
5. Maintain security boundary (gateway doesn't access parsed data directly)

Goal: Validate the security boundary pattern and enrichment flow works correctly.
"""

import pytest
import os
import sys
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'symphainy-platform'))


# ============================================================================
# TEST DATA: Mock Enriched Embeddings
# ============================================================================

def create_test_enriched_embeddings(enrichment_type: str = "statistics") -> List[Dict[str, Any]]:
    """
    Create test enriched embeddings that match the expected structure.
    
    These embeddings represent new semantic data created from parsed data.
    """
    if enrichment_type == "statistics":
        return [
            {
                "_key": "enrich_stats_test_content_123_revenue_abc123",
                "id": "enrich_stats_test_content_123_revenue_abc123",
                "content_id": "test_content_123",
                "column_name": "revenue",
                "embedding_type": "statistics",
                "metadata": {
                    "mean": 1000.0,
                    "median": 950.0,
                    "std": 200.0,
                    "min": 500.0,
                    "max": 1500.0,
                    "count": 100,
                    "null_count": 5,
                    "skewness": 0.2,
                    "kurtosis": 2.1
                },
                "created_at": "2025-01-15T10:00:00",
                "enrichment_type": "statistics"
            },
            {
                "_key": "enrich_stats_test_content_123_cost_def456",
                "id": "enrich_stats_test_content_123_cost_def456",
                "content_id": "test_content_123",
                "column_name": "cost",
                "embedding_type": "statistics",
                "metadata": {
                    "mean": 700.0,
                    "median": 680.0,
                    "std": 150.0,
                    "min": 400.0,
                    "max": 1000.0,
                    "count": 100,
                    "null_count": 2,
                    "skewness": 0.1,
                    "kurtosis": 2.0
                },
                "created_at": "2025-01-15T10:00:00",
                "enrichment_type": "statistics"
            }
        ]
    elif enrichment_type == "column_values":
        return [
            {
                "_key": "enrich_colval_test_content_123_revenue_xyz789",
                "id": "enrich_colval_test_content_123_revenue_xyz789",
                "content_id": "test_content_123",
                "column_name": "revenue",
                "embedding_type": "column_values",
                "metadata": {
                    "data_type": "float64",
                    "total_count": 100,
                    "non_null_count": 95,
                    "null_count": 5,
                    "sample_size": 10
                },
                "sample_values": [950.0, 1200.0, 800.0, 1100.0, 900.0, 1300.0, 750.0, 1000.0, 1050.0, 1150.0],
                "created_at": "2025-01-15T10:00:00",
                "enrichment_type": "column_values"
            }
        ]
    else:
        return []


# ============================================================================
# TEST FIXTURES: Mock Dependencies
# ============================================================================

@pytest.fixture
def mock_di_container():
    """Create mock DI Container."""
    container = Mock()
    container.realm_name = "business_enablement"
    container.get_utility = Mock(return_value=Mock())
    container.get_service = Mock(return_value=None)
    container.get_foundation_service = Mock(return_value=None)
    container.get_logger = Mock(return_value=Mock())
    return container


@pytest.fixture
def mock_platform_gateway():
    """Create mock Platform Gateway."""
    gateway = Mock()
    
    # Mock semantic data abstraction
    mock_semantic_data = AsyncMock()
    mock_semantic_data.store_semantic_embeddings = AsyncMock(return_value={"success": True, "count": 2})
    gateway.get_abstraction = Mock(return_value=mock_semantic_data)
    
    return gateway


@pytest.fixture
def mock_smart_city_apis():
    """Create mock Smart City service APIs."""
    # Mock Librarian
    mock_librarian = AsyncMock()
    mock_librarian.get_content_metadata = AsyncMock(return_value={
        "content_id": "test_content_123",
        "file_id": "test_file_123",
        "parsed_file_id": "test_parsed_file_123"
    })
    
    # Mock Content Steward
    mock_content_steward = AsyncMock()
    mock_content_steward.get_file = AsyncMock(return_value={
        "file_id": "test_parsed_file_123",
        "data": [{"revenue": 1000.0, "cost": 700.0}]
    })
    
    # Mock Nurse
    mock_nurse = AsyncMock()
    mock_nurse.record_platform_operation_event = AsyncMock(return_value=True)
    
    return {
        "librarian": mock_librarian,
        "content_steward": mock_content_steward,
        "nurse": mock_nurse
    }


@pytest.fixture
def mock_user_context():
    """Create mock User Context."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "roles": ["user"],
        "permissions": ["execute", "read"]
    }


@pytest.fixture
async def semantic_enrichment_gateway(mock_di_container, mock_platform_gateway, mock_smart_city_apis):
    """Create SemanticEnrichmentGateway instance with mocks."""
    from backend.business_enablement.enabling_services.semantic_enrichment_gateway import SemanticEnrichmentGateway
    
    service = SemanticEnrichmentGateway(
        service_name="SemanticEnrichmentGateway",
        realm_name="business_enablement",
        platform_gateway=mock_platform_gateway,
        di_container=mock_di_container
    )
    
    # Manually set up dependencies (bypassing full initialization)
    service.librarian = mock_smart_city_apis["librarian"]
    service.semantic_data = mock_platform_gateway.get_abstraction("semantic_data")
    service.content_steward = mock_smart_city_apis["content_steward"]
    service.nurse = mock_smart_city_apis["nurse"]
    
    return service


@pytest.fixture
async def mock_enrichment_service(mock_di_container, mock_platform_gateway, mock_smart_city_apis):
    """Create mock SemanticEnrichmentService."""
    from backend.business_enablement.enabling_services.semantic_enrichment_service import SemanticEnrichmentService
    
    service = SemanticEnrichmentService(
        service_name="SemanticEnrichmentService",
        realm_name="business_enablement",
        platform_gateway=mock_platform_gateway,
        di_container=mock_di_container
    )
    
    # Manually set up dependencies
    service.librarian = mock_smart_city_apis["librarian"]
    service.content_steward = mock_smart_city_apis["content_steward"]
    service.nurse = mock_smart_city_apis["nurse"]
    
    # Mock create_enrichment_embeddings to return test embeddings
    async def mock_create_embeddings(content_id, enrichment_type, filters=None, user_context=None):
        return create_test_enriched_embeddings(enrichment_type)
    
    service.create_enrichment_embeddings = mock_create_embeddings
    
    return service


# ============================================================================
# FUNCTIONAL TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
@pytest.mark.functional
class TestSemanticEnrichmentGatewayFunctionality:
    """Test SemanticEnrichmentGateway functionality."""
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_statistics(
        self,
        semantic_enrichment_gateway,
        mock_enrichment_service,
        mock_user_context
    ):
        """Test semantic enrichment with statistics type."""
        # Set enrichment service on gateway
        semantic_enrichment_gateway.enrichment_service = mock_enrichment_service
        
        # Create enrichment request
        enrichment_request = {
            "type": "statistics",
            "description": "Need statistics for revenue and cost columns"
        }
        
        # Execute enrichment
        result = await semantic_enrichment_gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context=mock_user_context
        )
        
        # Verify result structure
        assert result is not None
        assert result["success"] is True
        assert result["content_id"] == "test_content_123"
        assert result["enrichment_type"] == "statistics"
        assert "embedding_ids" in result
        assert len(result["embedding_ids"]) == 2
        assert result["count"] == 2
        
        # Verify embedding IDs are returned (not raw data)
        assert all(isinstance(emb_id, str) for emb_id in result["embedding_ids"])
        assert "enrich_stats" in result["embedding_ids"][0]
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_column_values(
        self,
        semantic_enrichment_gateway,
        mock_enrichment_service,
        mock_user_context
    ):
        """Test semantic enrichment with column_values type."""
        # Set enrichment service on gateway
        semantic_enrichment_gateway.enrichment_service = mock_enrichment_service
        
        # Create enrichment request with filters
        enrichment_request = {
            "type": "column_values",
            "filters": {
                "columns": ["revenue"]
            },
            "description": "Need sample values for revenue column"
        }
        
        # Execute enrichment
        result = await semantic_enrichment_gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context=mock_user_context
        )
        
        # Verify result structure
        assert result["success"] is True
        assert result["enrichment_type"] == "column_values"
        assert len(result["embedding_ids"]) >= 1
        assert "enrich_colval" in result["embedding_ids"][0]
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_validation_error(
        self,
        semantic_enrichment_gateway,
        mock_user_context
    ):
        """Test that invalid enrichment requests are rejected."""
        # Missing type
        enrichment_request = {
            "description": "Missing type"
        }
        
        result = await semantic_enrichment_gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context=mock_user_context
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "type" in result["error"].lower() or "required" in result["error"].lower()
        
        # Invalid type
        enrichment_request = {
            "type": "invalid_type"
        }
        
        result = await semantic_enrichment_gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context=mock_user_context
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "invalid" in result["error"].lower() or "type" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_service_unavailable(
        self,
        semantic_enrichment_gateway,
        mock_user_context
    ):
        """Test behavior when enrichment service is not available."""
        # Don't set enrichment service
        semantic_enrichment_gateway.enrichment_service = None
        
        enrichment_request = {
            "type": "statistics"
        }
        
        result = await semantic_enrichment_gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context=mock_user_context
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not available" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_enrich_semantic_layer_storage_integration(
        self,
        semantic_enrichment_gateway,
        mock_enrichment_service,
        mock_platform_gateway,
        mock_user_context
    ):
        """Test that enriched embeddings are stored in semantic layer."""
        # Set enrichment service
        semantic_enrichment_gateway.enrichment_service = mock_enrichment_service
        
        # Get semantic data mock to verify storage was called
        mock_semantic_data = mock_platform_gateway.get_abstraction("semantic_data")
        mock_semantic_data.store_semantic_embeddings = AsyncMock(return_value={"success": True, "count": 2})
        
        enrichment_request = {
            "type": "statistics"
        }
        
        result = await semantic_enrichment_gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context=mock_user_context
        )
        
        # Verify storage was called
        assert mock_semantic_data.store_semantic_embeddings.called
        
        # Verify result
        assert result["success"] is True
        assert result["count"] == 2
    
    @pytest.mark.asyncio
    async def test_security_boundary_pattern(
        self,
        semantic_enrichment_gateway,
        mock_enrichment_service,
        mock_user_context
    ):
        """
        Test that security boundary is maintained.
        
        Gateway should NOT access parsed data directly.
        Only enrichment service (secure boundary) accesses parsed data.
        """
        # Set enrichment service
        semantic_enrichment_gateway.enrichment_service = mock_enrichment_service
        
        # Verify gateway doesn't have direct access to parsed data
        # (it should use enrichment service instead)
        assert not hasattr(semantic_enrichment_gateway, 'get_parsed_file') or \
               not callable(getattr(semantic_enrichment_gateway, 'get_parsed_file', None))
        
        enrichment_request = {
            "type": "statistics"
        }
        
        result = await semantic_enrichment_gateway.enrich_semantic_layer(
            content_id="test_content_123",
            enrichment_request=enrichment_request,
            user_context=mock_user_context
        )
        
        # Verify enrichment happened via service (not direct access)
        assert result["success"] is True
        # Gateway should only see embedding IDs, not raw parsed data
        assert "embedding_ids" in result
        assert all(isinstance(emb_id, str) for emb_id in result["embedding_ids"])

