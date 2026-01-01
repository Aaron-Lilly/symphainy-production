#!/usr/bin/env python3
"""
Lightweight Functional Test: DataAnalyzerService EDA Analysis with Semantic Embeddings

This test verifies that DataAnalyzerService can:
1. Query semantic embeddings via semantic_data abstraction
2. Extract schema information from embeddings
3. Run EDA analysis (statistics, correlations, distributions, missing values)
4. Return deterministic results

Goal: Validate the approach works with semantic data abstractions before building more pieces.
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
# TEST DATA: Mock Semantic Embeddings
# ============================================================================

def create_test_schema_embeddings() -> List[Dict[str, Any]]:
    """
    Create test schema embeddings that match the expected structure.
    
    These embeddings represent schema/metadata for a structured dataset with:
    - Numerical columns (revenue, cost, profit)
    - Categorical columns (region, product_type)
    """
    return [
        {
            "content_id": "test_content_123",
            "column_name": "revenue",
            "data_type": "float",
            "embedding_type": "schema",
            "metadata": {
                "mean": 1000.0,
                "median": 950.0,
                "std": 200.0,
                "min": 500.0,
                "max": 1500.0,
                "count": 100,
                "null_count": 5,
                "skewness": 0.2,
                "kurtosis": 2.1,
                "q1": 800.0,
                "q2": 950.0,
                "q3": 1200.0
            },
            "sample_values": [950.0, 1200.0, 800.0, 1100.0, 900.0, 1300.0, 750.0, 1000.0, 1050.0, 1150.0]
        },
        {
            "content_id": "test_content_123",
            "column_name": "cost",
            "data_type": "float",
            "embedding_type": "schema",
            "metadata": {
                "mean": 700.0,
                "median": 680.0,
                "std": 150.0,
                "min": 400.0,
                "max": 1000.0,
                "count": 100,
                "null_count": 2,
                "skewness": 0.1,
                "kurtosis": 2.0,
                "q1": 600.0,
                "q2": 680.0,
                "q3": 800.0,
                "correlations": {
                    "revenue": 0.85
                }
            },
            "sample_values": [680.0, 800.0, 600.0, 750.0, 650.0, 850.0, 550.0, 700.0, 720.0, 780.0]
        },
        {
            "content_id": "test_content_123",
            "column_name": "profit",
            "data_type": "float",
            "embedding_type": "schema",
            "metadata": {
                "mean": 300.0,
                "median": 270.0,
                "std": 100.0,
                "min": 100.0,
                "max": 500.0,
                "count": 100,
                "null_count": 0,
                "skewness": 0.3,
                "kurtosis": 2.2,
                "q1": 200.0,
                "q2": 270.0,
                "q3": 400.0,
                "correlations": {
                    "revenue": 0.90,
                    "cost": 0.75
                }
            },
            "sample_values": [270.0, 400.0, 200.0, 350.0, 250.0, 450.0, 150.0, 300.0, 320.0, 380.0]
        },
        {
            "content_id": "test_content_123",
            "column_name": "region",
            "data_type": "string",
            "embedding_type": "schema",
            "metadata": {
                "unique_count": 5,
                "most_common": ["North", "South", "East", "West", "Central"],
                "value_counts": {
                    "North": 25,
                    "South": 20,
                    "East": 20,
                    "West": 20,
                    "Central": 15
                },
                "count": 100,
                "null_count": 0
            },
            "sample_values": ["North", "South", "East", "West", "Central", "North", "South", "East", "West", "Central"]
        },
        {
            "content_id": "test_content_123",
            "column_name": "product_type",
            "data_type": "string",
            "embedding_type": "schema",
            "metadata": {
                "unique_count": 3,
                "most_common": ["TypeA", "TypeB", "TypeC"],
                "value_counts": {
                    "TypeA": 40,
                    "TypeB": 35,
                    "TypeC": 25
                },
                "count": 100,
                "null_count": 0
            },
            "sample_values": ["TypeA", "TypeB", "TypeC", "TypeA", "TypeB", "TypeC", "TypeA", "TypeB", "TypeC", "TypeA"]
        }
    ]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_di_container():
    """Create mock DI Container."""
    container = Mock()
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    container.get_logger = Mock(return_value=logger)
    container.get_config = Mock(return_value=Mock())
    container.get_health = Mock(return_value=Mock())
    container.get_telemetry = Mock(return_value=Mock())
    container.get_error_handler = Mock(return_value=Mock())
    container.get_security = Mock(return_value=Mock())
    container.get_tenant = Mock(return_value=Mock())
    return container


@pytest.fixture
def mock_platform_gateway():
    """Create mock Platform Gateway."""
    gateway = Mock()
    
    # Mock semantic_data abstraction
    semantic_data = Mock()
    semantic_data.get_semantic_embeddings = AsyncMock(return_value=create_test_schema_embeddings())
    
    gateway.get_abstraction = Mock(return_value=semantic_data)
    return gateway


@pytest.fixture
def mock_smart_city_apis():
    """Create mock Smart City SOA APIs."""
    librarian = Mock()
    librarian.get_document = AsyncMock(return_value={"document_id": "test_doc_123"})
    
    return {
        "librarian": librarian
    }


@pytest.fixture
def mock_user_context():
    """Create mock user context."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "roles": ["user"],
        "permissions": ["execute", "read"]
    }


@pytest.fixture
async def data_analyzer_service(mock_di_container, mock_platform_gateway, mock_smart_city_apis):
    """Create DataAnalyzerService instance with mocks."""
    from backend.business_enablement.enabling_services.data_analyzer_service import DataAnalyzerService
    
    service = DataAnalyzerService(
        service_name="DataAnalyzerService",
        realm_name="business_enablement",
        platform_gateway=mock_platform_gateway,
        di_container=mock_di_container
    )
    
    # Manually set up dependencies (bypassing full initialization)
    service.semantic_data = mock_platform_gateway.get_abstraction("semantic_data")
    service.librarian = mock_smart_city_apis["librarian"]
    
    return service


# ============================================================================
# FUNCTIONAL TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
@pytest.mark.functional
class TestDataAnalyzerEDAFunctionality:
    """Test DataAnalyzerService EDA analysis with semantic embeddings."""
    
    @pytest.mark.asyncio
    async def test_run_eda_analysis_statistics(self, data_analyzer_service, mock_user_context):
        """Test EDA analysis with statistics."""
        result = await data_analyzer_service.run_eda_analysis(
            content_id="test_content_123",
            analysis_types=["statistics"],
            user_context=mock_user_context
        )
        
        # Verify result structure
        assert result is not None
        assert result["success"] is True
        assert result["content_id"] == "test_content_123"
        assert "eda_results" in result
        assert "statistics" in result["eda_results"]
        
        # Verify statistics for numerical columns
        stats = result["eda_results"]["statistics"]
        assert "revenue" in stats
        assert stats["revenue"]["type"] == "numerical"
        assert stats["revenue"]["mean"] == 1000.0
        assert stats["revenue"]["median"] == 950.0
        assert stats["revenue"]["std"] == 200.0
        
        # Verify statistics for categorical columns
        assert "region" in stats
        assert stats["region"]["type"] == "categorical"
        assert stats["region"]["unique_count"] == 5
    
    @pytest.mark.asyncio
    async def test_run_eda_analysis_correlations(self, data_analyzer_service, mock_user_context):
        """Test EDA analysis with correlations."""
        result = await data_analyzer_service.run_eda_analysis(
            content_id="test_content_123",
            analysis_types=["correlations"],
            user_context=mock_user_context
        )
        
        # Verify result structure
        assert result["success"] is True
        assert "correlations" in result["eda_results"]
        
        # Verify correlation matrix
        correlations = result["eda_results"]["correlations"]
        assert "numerical_columns" in correlations
        assert "revenue" in correlations["numerical_columns"]
        assert "cost" in correlations["numerical_columns"]
        assert "profit" in correlations["numerical_columns"]
        
        # Verify correlation matrix structure
        assert "correlation_matrix" in correlations
        assert "revenue" in correlations["correlation_matrix"]
        assert correlations["correlation_matrix"]["revenue"]["revenue"] == 1.0
        # Correlation is calculated from sample values (deterministic), so we just verify it exists
        assert "cost" in correlations["correlation_matrix"]["revenue"]
        assert isinstance(correlations["correlation_matrix"]["revenue"]["cost"], float)
        # Correlation should be high (close to 1.0) since sample values are correlated
        assert abs(correlations["correlation_matrix"]["revenue"]["cost"]) > 0.5
    
    @pytest.mark.asyncio
    async def test_run_eda_analysis_distributions(self, data_analyzer_service, mock_user_context):
        """Test EDA analysis with distributions."""
        result = await data_analyzer_service.run_eda_analysis(
            content_id="test_content_123",
            analysis_types=["distributions"],
            user_context=mock_user_context
        )
        
        # Verify result structure
        assert result["success"] is True
        assert "distributions" in result["eda_results"]
        
        # Verify distribution for numerical column
        distributions = result["eda_results"]["distributions"]
        assert "revenue" in distributions
        assert distributions["revenue"]["type"] == "numerical"
        assert "quartiles" in distributions["revenue"]
        assert distributions["revenue"]["quartiles"]["q1"] == 800.0
        assert distributions["revenue"]["quartiles"]["q2"] == 950.0
        assert distributions["revenue"]["quartiles"]["q3"] == 1200.0
        
        # Verify distribution for categorical column
        assert "region" in distributions
        assert distributions["region"]["type"] == "categorical"
        assert "value_counts" in distributions["region"]
    
    @pytest.mark.asyncio
    async def test_run_eda_analysis_missing_values(self, data_analyzer_service, mock_user_context):
        """Test EDA analysis with missing values."""
        result = await data_analyzer_service.run_eda_analysis(
            content_id="test_content_123",
            analysis_types=["missing_values"],
            user_context=mock_user_context
        )
        
        # Verify result structure
        assert result["success"] is True
        assert "missing_values" in result["eda_results"]
        
        # Verify missing value analysis
        missing = result["eda_results"]["missing_values"]
        assert "revenue" in missing
        assert missing["revenue"]["total_count"] == 100
        assert missing["revenue"]["null_count"] == 5
        assert missing["revenue"]["missing_percentage"] == 5.0
        assert missing["revenue"]["has_missing"] is True
        
        assert "profit" in missing
        assert missing["profit"]["null_count"] == 0
        assert missing["profit"]["has_missing"] is False
    
    @pytest.mark.asyncio
    async def test_run_eda_analysis_all_types(self, data_analyzer_service, mock_user_context):
        """Test EDA analysis with all analysis types."""
        result = await data_analyzer_service.run_eda_analysis(
            content_id="test_content_123",
            analysis_types=["statistics", "correlations", "distributions", "missing_values"],
            user_context=mock_user_context
        )
        
        # Verify result structure
        assert result["success"] is True
        assert len(result["eda_results"]) == 4
        assert "statistics" in result["eda_results"]
        assert "correlations" in result["eda_results"]
        assert "distributions" in result["eda_results"]
        assert "missing_values" in result["eda_results"]
        
        # Verify schema_info is included
        assert "schema_info" in result
        assert "columns" in result["schema_info"]
        assert len(result["schema_info"]["columns"]) == 5
    
    @pytest.mark.asyncio
    async def test_run_eda_analysis_deterministic(self, data_analyzer_service, mock_user_context):
        """Test that EDA analysis is deterministic (same input = same output)."""
        # Run analysis twice
        result1 = await data_analyzer_service.run_eda_analysis(
            content_id="test_content_123",
            analysis_types=["statistics"],
            user_context=mock_user_context
        )
        
        result2 = await data_analyzer_service.run_eda_analysis(
            content_id="test_content_123",
            analysis_types=["statistics"],
            user_context=mock_user_context
        )
        
        # Results should be identical
        assert result1["success"] == result2["success"]
        assert result1["eda_results"]["statistics"] == result2["eda_results"]["statistics"]
    
    @pytest.mark.asyncio
    async def test_run_eda_analysis_no_embeddings(self, data_analyzer_service, mock_user_context):
        """Test EDA analysis when no embeddings are found."""
        # Mock semantic_data to return empty list
        data_analyzer_service.semantic_data.get_semantic_embeddings = AsyncMock(return_value=[])
        
        result = await data_analyzer_service.run_eda_analysis(
            content_id="test_content_123",
            analysis_types=["statistics"],
            user_context=mock_user_context
        )
        
        # Should return error
        assert result["success"] is False
        assert "No schema embeddings found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_semantic_data_abstraction_integration(self, data_analyzer_service, mock_user_context):
        """Test that semantic_data abstraction is called correctly."""
        # Reset mock to track calls
        data_analyzer_service.semantic_data.get_semantic_embeddings = AsyncMock(return_value=create_test_schema_embeddings())
        
        await data_analyzer_service.run_eda_analysis(
            content_id="test_content_123",
            analysis_types=["statistics"],
            user_context=mock_user_context
        )
        
        # Verify semantic_data.get_semantic_embeddings was called correctly
        data_analyzer_service.semantic_data.get_semantic_embeddings.assert_called_once()
        call_args = data_analyzer_service.semantic_data.get_semantic_embeddings.call_args
        
        assert call_args.kwargs["content_id"] == "test_content_123"
        assert call_args.kwargs["filters"]["embedding_type"] == "schema"
        assert call_args.kwargs["user_context"]["tenant_id"] == "test_tenant_123"

