#!/usr/bin/env python3
"""
LLMAbstraction Tests

Tests for LLMAbstraction in isolation.
Verifies abstraction works correctly with dependency injection.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestLLMAbstraction:
    """Test LLMAbstraction functionality."""
    
    @pytest.fixture
    def mock_openai_adapter(self):
        """Mock OpenAI adapter."""
        adapter = AsyncMock()
        adapter.generate_completion = AsyncMock(return_value={
            "id": "test-id",
            "choices": [{"message": {"content": "test response"}, "finish_reason": "stop"}],
            "usage": {"total_tokens": 10},
            "metadata": {}
        })
        adapter.get_models = AsyncMock(return_value=[{"id": "gpt-4o-mini"}])
        adapter.is_model_available = AsyncMock(return_value=True)
        adapter.get_model_info = AsyncMock(return_value={"id": "gpt-4o-mini"})
        adapter.health_check = AsyncMock(return_value={"healthy": True})
        adapter.generate_embeddings = AsyncMock(return_value=[0.1, 0.2, 0.3])
        return adapter
    
    @pytest.fixture
    def mock_anthropic_adapter(self):
        """Mock Anthropic adapter."""
        adapter = AsyncMock()
        adapter.generate_completion = AsyncMock(return_value={
            "id": "test-id",
            "choices": [{"message": {"content": "test response"}, "finish_reason": "stop"}],
            "usage": {"total_tokens": 10},
            "metadata": {}
        })
        adapter.get_models = AsyncMock(return_value=[{"id": "claude-3-haiku"}])
        adapter.is_model_available = AsyncMock(return_value=True)
        adapter.get_model_info = AsyncMock(return_value={"id": "claude-3-haiku"})
        adapter.health_check = AsyncMock(return_value={"healthy": True})
        adapter.generate_embeddings = AsyncMock(return_value=[0.1, 0.2, 0.3])
        return adapter
    
    @pytest.fixture
    def abstraction(self, mock_openai_adapter, mock_anthropic_adapter):
        """Create LLMAbstraction instance with dependency injection."""
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction
        
        return LLMAbstraction(
            openai_adapter=mock_openai_adapter,
            anthropic_adapter=mock_anthropic_adapter,
            provider="openai"
        )
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_openai_adapter, mock_anthropic_adapter):
        """Test abstraction initializes correctly with dependency injection."""
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction
        
        abstraction = LLMAbstraction(
            openai_adapter=mock_openai_adapter,
            anthropic_adapter=mock_anthropic_adapter,
            provider="openai"
        )
        assert abstraction.provider == "openai"
        assert abstraction.primary_adapter == mock_openai_adapter
        assert abstraction.adapters["openai"] == mock_openai_adapter
        assert abstraction.adapters["anthropic"] == mock_anthropic_adapter
    
    @pytest.mark.asyncio
    async def test_generate_response(self, abstraction, mock_openai_adapter):
        """Test abstraction can generate LLM response."""
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
        
        request = LLMRequest(
            messages=[{"role": "user", "content": "test prompt"}],
            model=LLMModel.GPT_4O_MINI,
            max_tokens=100
        )
        
        response = await abstraction.generate_response(request)
        assert response is not None
        assert hasattr(response, "content")
        assert response.content == "test response"
        mock_openai_adapter.generate_completion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_requires_adapters(self):
        """Test abstraction requires adapters via dependency injection."""
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction
        
        with pytest.raises(ValueError, match="Must provide either adapters"):
            LLMAbstraction(provider="openai")
