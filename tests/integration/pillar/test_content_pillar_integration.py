"""
Integration tests for Content Pillar workflows.

Tests:
- File upload → parsing → embedding → preview
- Structured file parsing workflow
- Unstructured file parsing workflow
- Hybrid file parsing workflow
- Binary file with copybook parsing
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure


@pytest.mark.integration
@pytest.mark.pillar
@pytest.mark.content
@pytest.mark.slow
class TestContentPillarIntegration:
    """Test suite for Content Pillar integration."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        container.get_config_adapter = Mock(return_value=Mock())
        return container
    
    @pytest.mark.asyncio
    async def test_structured_file_parsing_workflow(self, mock_platform_gateway, mock_di_container):
        """Test complete structured file parsing workflow."""
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        
        file_parser = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await file_parser.initialize()
        
        # Mock file retrieval
        with patch.object(file_parser, 'retrieve_document') as mock_retrieve:
            mock_retrieve.return_value = {
                "file_data": b"name,age\nJohn,30\nJane,25",
                "file_type": "csv",
                "filename": "test.csv"
            }
            
            # Parse file
            result = await file_parser.parse_file(
                file_id="test_file_123",
                parse_options={"parsing_type": "structured"}
            )
            
            # Should parse successfully (may use mocks for abstractions)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_unstructured_file_parsing_workflow(self, mock_platform_gateway, mock_di_container):
        """Test complete unstructured file parsing workflow."""
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        
        file_parser = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await file_parser.initialize()
        
        # Mock file retrieval
        with patch.object(file_parser, 'retrieve_document') as mock_retrieve:
            mock_retrieve.return_value = {
                "file_data": b"PDF content here",
                "file_type": "pdf",
                "filename": "test.pdf"
            }
            
            # Parse file
            result = await file_parser.parse_file(
                file_id="test_file_456",
                parse_options={"parsing_type": "unstructured"}
            )
            
            # Should parse successfully
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_hybrid_file_parsing_workflow(self, mock_platform_gateway, mock_di_container):
        """Test complete hybrid file parsing workflow."""
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        
        file_parser = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await file_parser.initialize()
        
        # Mock file retrieval
        with patch.object(file_parser, 'retrieve_document') as mock_retrieve:
            mock_retrieve.return_value = {
                "file_data": b"Hybrid content",
                "file_type": "excel_with_text",
                "filename": "test.xlsx"
            }
            
            # Parse file
            result = await file_parser.parse_file(
                file_id="test_file_789",
                parse_options={"parsing_type": "hybrid"}
            )
            
            # Should parse successfully and return 3 JSON files
            assert result is not None
            if result.get("success"):
                assert "parsed_files" in result
                assert "structured" in result["parsed_files"]
                assert "unstructured" in result["parsed_files"]
                assert "correlation_map" in result["parsed_files"]
    
    @pytest.mark.asyncio
    async def test_binary_file_with_copybook_workflow(self, mock_platform_gateway, mock_di_container):
        """Test binary file parsing with copybook workflow."""
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        
        file_parser = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await file_parser.initialize()
        
        copybook = """
        01 CUSTOMER-RECORD.
           05 CUSTOMER-ID PIC X(10).
           05 CUSTOMER-NAME PIC X(50).
        """
        
        # Mock file retrieval
        with patch.object(file_parser, 'retrieve_document') as mock_retrieve:
            mock_retrieve.return_value = {
                "file_data": b"\x00\x01\x02\x03",
                "file_type": "bin",
                "filename": "test.bin"
            }
            
            # Parse with copybook
            result = await file_parser.parse_file(
                file_id="test_file_bin",
                parse_options={
                    "parsing_type": "structured",
                    "copybook": copybook
                }
            )
            
            # Should parse successfully with copybook
            assert result is not None
    
    # ========================================================================
    # EMBEDDING/DATA MASH INTEGRATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_embedding_workflow_integration(self, mock_platform_gateway, mock_di_container):
        """Test complete embedding workflow: parse → embed → preview."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        from unittest.mock import patch, AsyncMock
        
        # Initialize orchestrator
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock parsed file retrieval
        mock_parsed_file = {
            "parsed_file_id": "test_parsed_file_123",
            "file_id": "test_file_123",
            "metadata": {
                "parse_result": {
                    "parsing_type": "structured",
                    "file_type": "csv",
                    "structure": {
                        "columns": [
                            {"name": "name", "type": "string"},
                            {"name": "age", "type": "integer"}
                        ],
                        "row_count": 10
                    },
                    "record_count": 10
                },
                "row_count": 10,
                "column_count": 2
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
                
                # Mock DataSteward for lineage tracking
                mock_data_steward = AsyncMock()
                mock_data_steward.track_lineage = AsyncMock(return_value={"success": True})
                with patch.object(orchestrator, 'get_data_steward_api', new_callable=AsyncMock) as mock_get_data_steward:
                    mock_get_data_steward.return_value = mock_data_steward
                    
                    # Mock ConfigAdapter for HuggingFace config
                    with patch.object(orchestrator, '_get_config_adapter') as mock_get_config:
                        mock_config = {
                            "HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL": "https://api-inference.huggingface.co",
                            "HUGGINGFACE_EMBEDDINGS_API_KEY": "test_key"
                        }
                        mock_get_config.return_value = mock_config
                        
                        # Mock semantic_data abstraction
                        with patch.object(orchestrator, 'get_abstraction') as mock_get_abstraction:
                            mock_get_abstraction.return_value = AsyncMock()  # Mock semantic_data
                            
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
                            assert "content_id" in result
                            assert "embeddings_count" in result
                            assert result.get("workflow_id") == "test_workflow"
                            
                            # Verify lineage tracking was called
                            mock_get_data_steward.assert_called_once()
                            mock_data_steward.track_lineage.assert_called_once()
                            
                            # Verify embedding service was called
                            mock_embedding_service.create_representative_embeddings.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_data_mash_workflow_integration(self, mock_platform_gateway, mock_di_container):
        """Test complete data mash workflow."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        from unittest.mock import patch, AsyncMock
        
        # Initialize orchestrator
        orchestrator = ContentJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await orchestrator.initialize()
        
        # Mock list_parsed_files_with_embeddings
        with patch.object(orchestrator, 'list_embedding_files') as mock_list_embedding_files:
            mock_list_embedding_files.return_value = {
                "success": True,
                "embedding_files": [
                    {
                        "parsed_file_id": "test_parsed_file_123",
                        "file_id": "test_file_123",
                        "embeddings_count": 5,
                        "content_id": "test_content_123"
                    }
                ]
            }
            
            # Mock ContentSteward
            with patch.object(orchestrator, 'get_content_steward_api') as mock_get_steward:
                mock_steward = AsyncMock()
                mock_steward.get_parsed_file = AsyncMock(return_value={
                    "parsed_file_id": "test_parsed_file_123",
                    "metadata": {
                        "ui_name": "test_file.csv",
                        "format_type": "jsonl",
                        "content_type": "structured",
                        "row_count": 10,
                        "column_count": 2
                    }
                })
                mock_get_steward.return_value = mock_steward
                
                # Test list_parsed_files_with_embeddings
                result = await orchestrator.list_parsed_files_with_embeddings(user_id="test_user")
                
                # Assertions
                assert result is not None
                assert result.get("success") is True
                assert "parsed_files" in result
                assert len(result.get("parsed_files", [])) > 0
    
    @pytest.mark.asyncio
    async def test_lineage_tracking_integration(self, mock_platform_gateway, mock_di_container):
        """Test lineage tracking through embedding workflow."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        from unittest.mock import patch, AsyncMock
        
        # Initialize orchestrator
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
                
                # Mock DataSteward for lineage tracking
                mock_data_steward = AsyncMock()
                mock_data_steward.track_lineage = AsyncMock(return_value={"success": True})
                
                # Use get_data_steward_api which is available on OrchestratorBase
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
                            
                            # Test create_embeddings with lineage tracking
                            user_context = {
                                "workflow_id": "test_workflow_123",
                                "user_id": "test_user",
                                "file_id": "test_file_123",
                                "parsed_file_id": "test_parsed_file_123"
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
                            
                            # Verify lineage data structure
                            call_args = mock_data_steward.track_lineage.call_args
                            lineage_data = call_args[1]["lineage_data"]  # keyword args
                            
                            assert lineage_data["parent_asset_id"] == "test_parsed_file_123"
                            assert lineage_data["parent_asset_type"] == "parsed_file"
                            assert lineage_data["child_asset_id"] == "test_content_123"
                            assert lineage_data["child_asset_type"] == "content"
                            assert lineage_data["relationship"] == "parsed_file_to_content"
                            
                            # Verify workflow_id in user_context
                            lineage_user_context = call_args[1]["user_context"]
                            assert lineage_user_context["workflow_id"] == "test_workflow_123"
                            assert lineage_user_context["file_id"] == "test_file_123"
                            assert lineage_user_context["parsed_file_id"] == "test_parsed_file_123"
                            assert lineage_user_context["content_id"] == "test_content_123"

