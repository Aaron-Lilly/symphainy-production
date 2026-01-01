"""
Unit tests for embedding creation functionality.

Tests:
- ContentJourneyOrchestrator.create_embeddings()
- Error handling (missing parsed file, missing config, etc.)
- Solution context integration
- Lineage tracking
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from config.test_config import TestConfig


@pytest.mark.unit
@pytest.mark.content
@pytest.mark.embedding
class TestEmbeddingCreation:
    """Unit tests for embedding creation."""
    
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
    async def test_create_embeddings_success(self, mock_platform_gateway, mock_di_container):
        """Test successful embedding creation."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock parsed file
        mock_parsed_file = {
            "parsed_file_id": "test_parsed_file_123",
            "file_id": "test_file_123",
            "metadata": {
                "parse_result": {
                    "parsing_type": "structured",
                    "file_type": "csv",
                    "structure": {
                        "columns": [{"name": "name", "type": "string"}],
                        "row_count": 10
                    },
                    "record_count": 10
                },
                "row_count": 10,
                "column_count": 1
            }
        }
        
        # Mock ContentSteward
        with patch.object(orchestrator, 'get_content_steward_api') as mock_get_steward:
            mock_steward = AsyncMock()
            mock_steward.get_parsed_file = AsyncMock(return_value=mock_parsed_file)
            mock_get_steward.return_value = mock_steward
            
            # Mock EmbeddingService
            with patch('backend.content.services.embedding_service.embedding_service.EmbeddingService') as mock_embedding_class:
                mock_embedding_service = AsyncMock()
                mock_embedding_service.initialize = AsyncMock(return_value=True)
                mock_embedding_service.create_representative_embeddings = AsyncMock(return_value={
                    "success": True,
                    "content_id": "test_content_123",
                    "embeddings_count": 5,
                    "stored_count": 5
                })
                mock_embedding_class.return_value = mock_embedding_service
                
                # Mock DataSteward - use get_data_steward_api which is available
                mock_data_steward = AsyncMock()
                mock_data_steward.track_lineage = AsyncMock(return_value={"success": True})
                with patch.object(orchestrator, 'get_data_steward_api', new_callable=AsyncMock) as mock_get_data_steward:
                    mock_get_data_steward.return_value = mock_data_steward
                    
                    # Mock ConfigAdapter
                    with patch.object(orchestrator, '_get_config_adapter') as mock_get_config:
                        mock_get_config.return_value = {
                            "HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL": "https://api-inference.huggingface.co",
                            "HUGGINGFACE_EMBEDDINGS_API_KEY": "test_key"
                        }
                        
                        # Mock semantic_data abstraction
                        with patch.object(orchestrator, 'get_abstraction') as mock_get_abstraction:
                            mock_get_abstraction.return_value = AsyncMock()
                            
                            # Test create_embeddings
                            result = await orchestrator.create_embeddings(
                                parsed_file_id="test_parsed_file_123",
                                user_id="test_user",
                                file_id="test_file_123",
                                user_context={"workflow_id": "test_workflow"}
                            )
                            
                            # Assertions
                            assert result is not None
                            assert result.get("success") is True
                            assert result.get("content_id") == "test_content_123"
                            assert result.get("embeddings_count") == 5
                            assert result.get("workflow_id") == "test_workflow"
    
    @pytest.mark.asyncio
    async def test_create_embeddings_missing_parsed_file(self, mock_platform_gateway, mock_di_container):
        """Test embedding creation with missing parsed file."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock ContentSteward returning None
        with patch.object(orchestrator, 'get_content_steward_api') as mock_get_steward:
            mock_steward = AsyncMock()
            mock_steward.get_parsed_file = AsyncMock(return_value=None)
            mock_get_steward.return_value = mock_steward
            
            # Test create_embeddings with missing parsed file
            result = await orchestrator.create_embeddings(
                parsed_file_id="nonexistent_parsed_file",
                user_id="test_user"
            )
            
            # Assertions
            assert result is not None
            assert result.get("success") is False
            assert "error" in result
            assert "not found" in result.get("error", "").lower()
    
    @pytest.mark.asyncio
    async def test_create_embeddings_missing_huggingface_config(self, mock_platform_gateway, mock_di_container):
        """Test embedding creation without HuggingFace config."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock parsed file
        mock_parsed_file = {
            "parsed_file_id": "test_parsed_file_123",
            "metadata": {"parse_result": {"parsing_type": "structured"}}
        }
        
        # Mock ContentSteward
        with patch.object(orchestrator, 'get_content_steward_api') as mock_get_steward:
            mock_steward = AsyncMock()
            mock_steward.get_parsed_file = AsyncMock(return_value=mock_parsed_file)
            mock_get_steward.return_value = mock_steward
            
            # Mock ConfigAdapter returning None/missing config
            with patch.object(orchestrator, '_get_config_adapter') as mock_get_config:
                mock_get_config.return_value = None  # No config adapter
                
                # Also mock os.getenv to return None
                with patch('os.getenv') as mock_getenv:
                    mock_getenv.return_value = None
                    
                    # Test create_embeddings without HuggingFace config
                    result = await orchestrator.create_embeddings(
                        parsed_file_id="test_parsed_file_123",
                        user_id="test_user"
                    )
                    
                    # Assertions
                    assert result is not None
                    assert result.get("success") is False
                    assert "error" in result
                    assert "huggingface" in result.get("error", "").lower() or "not configured" in result.get("error", "").lower()
    
    @pytest.mark.asyncio
    async def test_create_embeddings_solution_context(self, mock_platform_gateway, mock_di_container):
        """Test embedding creation with solution context."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock parsed file
        mock_parsed_file = {
            "parsed_file_id": "test_parsed_file_123",
            "metadata": {
                "parse_result": {
                    "parsing_type": "structured",
                    "structure": {"columns": [], "row_count": 10},
                    "record_count": 10
                }
            }
        }
        
        # Mock ContentSteward
        with patch.object(orchestrator, 'get_content_steward_api') as mock_get_steward:
            mock_steward = AsyncMock()
            mock_steward.get_parsed_file = AsyncMock(return_value=mock_parsed_file)
            mock_get_steward.return_value = mock_steward
            
            # Mock EmbeddingService
            with patch('backend.content.services.embedding_service.embedding_service.EmbeddingService') as mock_embedding_class:
                mock_embedding_service = AsyncMock()
                mock_embedding_service.initialize = AsyncMock(return_value=True)
                mock_embedding_service.create_representative_embeddings = AsyncMock(return_value={
                    "success": True,
                    "content_id": "test_content_123",
                    "embeddings_count": 5
                })
                mock_embedding_class.return_value = mock_embedding_service
                
                # Mock MVP Journey Orchestrator
                with patch.object(orchestrator, '_get_mvp_journey_orchestrator') as mock_get_mvp:
                    mock_mvp = AsyncMock()
                    mock_mvp.get_solution_context = AsyncMock(return_value={
                        "specialization_context": "test context",
                        "user_goals": ["goal1", "goal2"]
                    })
                    mock_get_mvp.return_value = mock_mvp
                    
                    # Mock DataSteward and config
                    with patch.object(orchestrator, 'get_data_steward_api', new_callable=AsyncMock) as mock_get_data_steward:
                        mock_get_data_steward.return_value = AsyncMock()
                        
                        with patch.object(orchestrator, '_get_config_adapter') as mock_get_config:
                            mock_get_config.return_value = {
                                "HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL": "https://api-inference.huggingface.co",
                                "HUGGINGFACE_EMBEDDINGS_API_KEY": "test_key"
                            }
                            
                            with patch.object(orchestrator, 'get_abstraction') as mock_get_abstraction:
                                mock_get_abstraction.return_value = AsyncMock()
                                
                                # Test create_embeddings with solution context
                                user_context = {
                                    "session_id": "test_session",
                                    "workflow_id": "test_workflow"
                                }
                                
                                result = await orchestrator.create_embeddings(
                                    parsed_file_id="test_parsed_file_123",
                                    user_id="test_user",
                                    user_context=user_context
                                )
                                
                                # Verify solution context was retrieved
                                mock_mvp.get_solution_context.assert_called_once_with("test_session")
                                
                                # Verify embedding service was called with solution context
                                call_args = mock_embedding_service.create_representative_embeddings.call_args
                                passed_user_context = call_args[1]["user_context"]  # keyword args
                                assert "solution_context" in passed_user_context
    
    @pytest.mark.asyncio
    async def test_create_embeddings_lineage_tracking(self, mock_platform_gateway, mock_di_container):
        """Test lineage tracking during embedding creation."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock parsed file
        mock_parsed_file = {
            "parsed_file_id": "test_parsed_file_123",
            "file_id": "test_file_123",
            "metadata": {
                "parse_result": {
                    "parsing_type": "structured",
                    "structure": {"columns": [], "row_count": 10},
                    "record_count": 10
                }
            }
        }
        
        # Mock ContentSteward
        with patch.object(orchestrator, 'get_content_steward_api') as mock_get_steward:
            mock_steward = AsyncMock()
            mock_steward.get_parsed_file = AsyncMock(return_value=mock_parsed_file)
            mock_get_steward.return_value = mock_steward
            
            # Mock EmbeddingService
            with patch('backend.content.services.embedding_service.embedding_service.EmbeddingService') as mock_embedding_class:
                mock_embedding_service = AsyncMock()
                mock_embedding_service.initialize = AsyncMock(return_value=True)
                mock_embedding_service.create_representative_embeddings = AsyncMock(return_value={
                    "success": True,
                    "content_id": "test_content_123",
                    "embeddings_count": 5
                })
                mock_embedding_class.return_value = mock_embedding_service
                
                # Mock DataSteward - use get_data_steward_api which is available
                mock_data_steward = AsyncMock()
                mock_data_steward.track_lineage = AsyncMock(return_value={"success": True})
                with patch.object(orchestrator, 'get_data_steward_api', new_callable=AsyncMock) as mock_get_data_steward:
                    mock_get_data_steward.return_value = mock_data_steward
                    
                    # Mock ConfigAdapter and semantic_data
                    with patch.object(orchestrator, '_get_config_adapter') as mock_get_config:
                        mock_get_config.return_value = {
                            "HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL": "https://api-inference.huggingface.co",
                            "HUGGINGFACE_EMBEDDINGS_API_KEY": "test_key"
                        }
                        
                        with patch.object(orchestrator, 'get_abstraction') as mock_get_abstraction:
                            mock_get_abstraction.return_value = AsyncMock()
                            
                            # Test create_embeddings
                            user_context = {
                                "workflow_id": "test_workflow_123",
                                "user_id": "test_user"
                            }
                            
                            result = await orchestrator.create_embeddings(
                                parsed_file_id="test_parsed_file_123",
                                user_id="test_user",
                                file_id="test_file_123",
                                user_context=user_context
                            )
                            
                            # Verify lineage tracking was called
                            mock_get_data_steward.assert_called_once()
                            mock_data_steward.track_lineage.assert_called_once()
                            
                            # Verify lineage data
                            call_args = mock_data_steward.track_lineage.call_args
                            lineage_data = call_args[1]["lineage_data"]
                            
                            assert lineage_data["parent_asset_id"] == "test_parsed_file_123"
                            assert lineage_data["parent_asset_type"] == "parsed_file"
                            assert lineage_data["child_asset_id"] == "test_content_123"
                            assert lineage_data["child_asset_type"] == "content"
                            assert lineage_data["relationship"] == "parsed_file_to_content"

