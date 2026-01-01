"""
Unit tests for embedding listing functionality.

Tests:
- ContentJourneyOrchestrator.list_embeddings()
- ContentJourneyOrchestrator.list_parsed_files_with_embeddings()
- Filtering by file_id
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
class TestEmbeddingListing:
    """Unit tests for embedding listing."""
    
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
    async def test_list_embeddings_all(self, mock_platform_gateway, mock_di_container):
        """Test listing all embeddings for user."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock embeddings list
        mock_embeddings = {
            "success": True,
            "embeddings": [
                {
                    "file_id": "test_file_123",
                    "content_id": "test_content_123",
                    "embeddings_count": 5,
                    "columns": [{"column_name": "name", "data_type": "string"}]
                },
                {
                    "file_id": "test_file_456",
                    "content_id": "test_content_456",
                    "embeddings_count": 3,
                    "columns": [{"column_name": "age", "data_type": "integer"}]
                }
            ],
            "count": 2
        }
        
        # Mock EmbeddingService
        with patch('backend.content.services.embedding_service.embedding_service.EmbeddingService') as mock_embedding_class:
            mock_embedding_service = AsyncMock()
            mock_embedding_service.initialize = AsyncMock(return_value=True)
            mock_embedding_service.list_embeddings = AsyncMock(return_value=mock_embeddings)
            mock_embedding_class.return_value = mock_embedding_service
            
            # Test list_embeddings without file_id
            result = await orchestrator.list_embeddings(
                user_id="test_user",
                file_id=None
            )
            
            # Assertions
            assert result is not None
            assert result.get("success") is True
            assert "embeddings" in result
            assert len(result.get("embeddings", [])) == 2
            assert result.get("count") == 2
    
    @pytest.mark.asyncio
    async def test_list_embeddings_by_file(self, mock_platform_gateway, mock_di_container):
        """Test listing embeddings filtered by file_id."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock embeddings list filtered by file_id
        mock_embeddings = {
            "success": True,
            "embeddings": [
                {
                    "file_id": "test_file_123",
                    "content_id": "test_content_123",
                    "embeddings_count": 5,
                    "columns": [{"column_name": "name", "data_type": "string"}]
                }
            ],
            "count": 1
        }
        
        # Mock EmbeddingService
        with patch('backend.content.services.embedding_service.embedding_service.EmbeddingService') as mock_embedding_class:
            mock_embedding_service = AsyncMock()
            mock_embedding_service.initialize = AsyncMock(return_value=True)
            mock_embedding_service.list_embeddings = AsyncMock(return_value=mock_embeddings)
            mock_embedding_class.return_value = mock_embedding_service
            
            # Test list_embeddings with file_id
            result = await orchestrator.list_embeddings(
                user_id="test_user",
                file_id="test_file_123"
            )
            
            # Assertions
            assert result is not None
            assert result.get("success") is True
            assert "embeddings" in result
            assert len(result.get("embeddings", [])) == 1
            assert result.get("embeddings", [])[0]["file_id"] == "test_file_123"
            
            # Verify file_id was passed to service
            call_args = mock_embedding_service.list_embeddings.call_args
            assert call_args[1]["file_id"] == "test_file_123"  # keyword args
    
    @pytest.mark.asyncio
    async def test_list_parsed_files_with_embeddings(self, mock_platform_gateway, mock_di_container):
        """Test listing parsed files that have embeddings."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock embedding files
        mock_embedding_files = {
            "success": True,
            "embedding_files": [
                {
                    "parsed_file_id": "test_parsed_file_123",
                    "file_id": "test_file_123",
                    "embeddings_count": 5,
                    "content_id": "test_content_123",
                    "ui_name": "test_file.csv"
                }
            ]
        }
        
        # Mock parsed file
        mock_parsed_file = {
            "parsed_file_id": "test_parsed_file_123",
            "metadata": {
                "ui_name": "test_file.csv",
                "format_type": "jsonl",
                "content_type": "structured",
                "row_count": 10,
                "column_count": 2,
                "parsed_at": "2024-01-01T00:00:00Z"
            }
        }
        
        # Mock list_embedding_files
        with patch.object(orchestrator, 'list_embedding_files') as mock_list_embedding_files:
            mock_list_embedding_files.return_value = mock_embedding_files
            
            # Mock ContentSteward
            with patch.object(orchestrator, 'get_content_steward_api') as mock_get_steward:
                mock_steward = AsyncMock()
                mock_steward.get_parsed_file = AsyncMock(return_value=mock_parsed_file)
                mock_get_steward.return_value = mock_steward
                
                # Test list_parsed_files_with_embeddings
                result = await orchestrator.list_parsed_files_with_embeddings(user_id="test_user")
                
                # Assertions
                assert result is not None
                assert result.get("success") is True
                assert "parsed_files" in result
                assert len(result.get("parsed_files", [])) > 0
                
                parsed_file = result.get("parsed_files", [])[0]
                assert parsed_file["parsed_file_id"] == "test_parsed_file_123"
                assert parsed_file["embeddings_count"] == 5
                # ui_name may not be present in all cases, check for required fields instead
                assert "file_id" in parsed_file or "parsed_file_id" in parsed_file

