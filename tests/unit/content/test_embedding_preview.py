"""
Unit tests for embedding preview functionality.

Tests:
- ContentJourneyOrchestrator.preview_embeddings()
- Preview structure validation
- max_columns parameter
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from config.test_config import TestConfig


@pytest.mark.unit
@pytest.mark.content
@pytest.mark.embedding
class TestEmbeddingPreview:
    """Unit tests for embedding preview."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_logger = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.mark.asyncio
    async def test_preview_embeddings_success(self, mock_platform_gateway, mock_di_container):
        """Test successful embedding preview."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock preview result
        mock_preview = {
            "success": True,
            "content_id": "test_content_123",
            "file_id": "test_file_123",
            "columns": [
                {
                    "column_name": "name",
                    "data_type": "string",
                    "semantic_meaning": "Person's full name",
                    "sample_values": ["John", "Jane", "Bob"],
                    "column_position": 0,
                    "row_count": 10
                },
                {
                    "column_name": "age",
                    "data_type": "integer",
                    "semantic_meaning": "Person's age in years",
                    "sample_values": [30, 25, 35],
                    "column_position": 1,
                    "row_count": 10
                }
            ],
            "structure": {
                "column_count": 2,
                "row_count": 10,
                "table_count": 1,
                "semantic_insights_summary": ["Test insight"]
            }
        }
        
        # Mock EmbeddingService
        with patch('backend.content.services.embedding_service.embedding_service.EmbeddingService') as mock_embedding_class:
            mock_embedding_service = AsyncMock()
            mock_embedding_service.initialize = AsyncMock(return_value=True)
            mock_embedding_service.preview_embeddings = AsyncMock(return_value=mock_preview)
            mock_embedding_class.return_value = mock_embedding_service
            
            # Test preview_embeddings
            result = await orchestrator.preview_embeddings(
                content_id="test_content_123",
                user_id="test_user",
                max_columns=20
            )
            
            # Assertions
            assert result is not None
            assert result.get("success") is True
            assert result.get("content_id") == "test_content_123"
            assert "columns" in result
            assert "structure" in result
            assert len(result.get("columns", [])) == 2
    
    @pytest.mark.asyncio
    async def test_preview_embeddings_max_columns(self, mock_platform_gateway, mock_di_container):
        """Test preview with max_columns parameter."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock preview with many columns
        many_columns = [{"column_name": f"col_{i}", "data_type": "string"} for i in range(30)]
        mock_preview = {
            "success": True,
            "content_id": "test_content_123",
            "columns": many_columns,
            "structure": {"column_count": 30, "row_count": 10}
        }
        
        # Mock EmbeddingService
        with patch('backend.content.services.embedding_service.embedding_service.EmbeddingService') as mock_embedding_class:
            mock_embedding_service = AsyncMock()
            mock_embedding_service.initialize = AsyncMock(return_value=True)
            mock_embedding_service.preview_embeddings = AsyncMock(return_value=mock_preview)
            mock_embedding_class.return_value = mock_embedding_service
            
            # Test preview_embeddings with max_columns=10
            result = await orchestrator.preview_embeddings(
                content_id="test_content_123",
                user_id="test_user",
                max_columns=10
            )
            
            # Verify max_columns was passed to service
            call_args = mock_embedding_service.preview_embeddings.call_args
            assert call_args[1]["max_columns"] == 10  # keyword args
    
    @pytest.mark.asyncio
    async def test_preview_embeddings_missing_content(self, mock_platform_gateway, mock_di_container):
        """Test preview with missing content_id."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock EmbeddingService returning error
        with patch('backend.content.services.embedding_service.embedding_service.EmbeddingService') as mock_embedding_class:
            mock_embedding_service = AsyncMock()
            mock_embedding_service.initialize = AsyncMock(return_value=True)
            mock_embedding_service.preview_embeddings = AsyncMock(return_value={
                "success": False,
                "error": "Content not found"
            })
            mock_embedding_class.return_value = mock_embedding_service
            
            # Test preview_embeddings with invalid content_id
            result = await orchestrator.preview_embeddings(
                content_id="nonexistent_content",
                user_id="test_user"
            )
            
            # Assertions
            assert result is not None
            assert result.get("success") is False
            assert "error" in result

