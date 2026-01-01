#!/usr/bin/env python3
"""
Content Analysis Orchestrator Unit Tests

Tests for the Content Analysis Orchestrator that composes content enabling services.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from utilities import UserContext

@pytest.mark.unit
@pytest.mark.business_enablement
class TestContentAnalysisOrchestratorUnit:
    """Unit tests for Content Analysis Orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_di_container):
        """Test orchestrator initializes correctly."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        # Mock business orchestrator
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = ContentAnalysisOrchestrator(business_orchestrator=mock_biz_orch)
        
        assert orchestrator.name == "ContentAnalysisOrchestrator"
        assert orchestrator.liaison_agent is None  # Not initialized yet
        assert orchestrator.processing_agent is None
    
    @pytest.mark.asyncio
    async def test_orchestrator_discovers_enabling_services(self, mock_di_container, mock_curator):
        """Test orchestrator discovers enabling services via Curator."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        # Mock enabling services
        mock_services = {
            "FileParserService": MagicMock(),
            "TextExtractorService": MagicMock(),
            "ContentMetadataService": MagicMock()
        }
        
        async def mock_get_service(name):
            if name in mock_services:
                return mock_services[name]
            raise Exception(f"{name} not found")
        
        mock_curator.get_service = AsyncMock(side_effect=mock_get_service)
        mock_di_container.curator = mock_curator
        
        # Mock business orchestrator
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = ContentAnalysisOrchestrator(business_orchestrator=mock_biz_orch)
        
        # Initialize should discover services
        await orchestrator.initialize()
        
        # Verify service references exist
        assert orchestrator.file_parser_service is not None
        assert orchestrator.text_extractor_service is not None
        assert orchestrator.content_metadata_service is not None
    
    @pytest.mark.asyncio
    async def test_orchestrator_integrates_liaison_agent(self, mock_di_container):
        """Test orchestrator integrates with liaison agent."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        # Mock business orchestrator
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = ContentAnalysisOrchestrator(business_orchestrator=mock_biz_orch)
        await orchestrator.initialize()
        
        # Liaison agent should be initialized
        assert orchestrator.liaison_agent is not None
        assert hasattr(orchestrator.liaison_agent, 'process_user_query')
    
    @pytest.mark.asyncio
    async def test_orchestrator_delegates_to_enabling_services(self, mock_di_container, mock_curator):
        """Test orchestrator properly delegates to enabling services."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        # Mock enabling services
        mock_file_parser = MagicMock()
        mock_file_parser.parse_file = AsyncMock(return_value={
            "success": True,
            "content": "Test content",
            "metadata": {"type": "text"}
        })
        
        mock_curator.get_service = AsyncMock(return_value=mock_file_parser)
        mock_di_container.curator = mock_curator
        
        # Mock business orchestrator
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = ContentAnalysisOrchestrator(business_orchestrator=mock_biz_orch)
        orchestrator.file_parser_service = mock_file_parser
        
        # Request content analysis
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        result = await orchestrator.analyze_content({
            "file_path": "/test/doc.pdf",
            "user_context": user_context
        })
        
        # Verify service was called
        mock_file_parser.parse_file.assert_called_once()
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_orchestrator_composes_multi_step_workflow(self, mock_di_container):
        """Test orchestrator can compose multi-step workflows."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        # Mock services for workflow
        mock_file_parser = MagicMock()
        mock_file_parser.parse_file = AsyncMock(return_value={
            "success": True,
            "content": "Test content"
        })
        
        mock_text_extractor = MagicMock()
        mock_text_extractor.extract_text = AsyncMock(return_value={
            "success": True,
            "text": "Extracted text"
        })
        
        mock_metadata_service = MagicMock()
        mock_metadata_service.extract_metadata = AsyncMock(return_value={
            "success": True,
            "metadata": {"author": "Test"}
        })
        
        # Mock business orchestrator
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = ContentAnalysisOrchestrator(business_orchestrator=mock_biz_orch)
        orchestrator.file_parser_service = mock_file_parser
        orchestrator.text_extractor_service = mock_text_extractor
        orchestrator.content_metadata_service = mock_metadata_service
        
        # Execute workflow
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        result = await orchestrator.execute_full_analysis({
            "file_path": "/test/doc.pdf",
            "user_context": user_context
        })
        
        # All services should be called in sequence
        mock_file_parser.parse_file.assert_called_once()
        mock_text_extractor.extract_text.assert_called_once()
        mock_metadata_service.extract_metadata.assert_called_once()
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_orchestrator_health_check(self, mock_di_container):
        """Test orchestrator health check."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        # Mock business orchestrator
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = ContentAnalysisOrchestrator(business_orchestrator=mock_biz_orch)
        
        health = await orchestrator.health_check()
        
        assert "status" in health
        assert "orchestrator_name" in health or "name" in health
    
    @pytest.mark.asyncio
    async def test_orchestrator_registers_with_curator(self, mock_di_container, mock_curator):
        """Test orchestrator registers itself with Curator."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        mock_curator.register_service = AsyncMock()
        mock_di_container.curator = mock_curator
        
        # Mock business orchestrator
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = ContentAnalysisOrchestrator(business_orchestrator=mock_biz_orch)
        await orchestrator.register_with_curator()
        
        # Should register with Curator
        mock_curator.register_service.assert_called_once()
        call_args = mock_curator.register_service.call_args[0]
        assert call_args[0] == "ContentAnalysisOrchestrator"

