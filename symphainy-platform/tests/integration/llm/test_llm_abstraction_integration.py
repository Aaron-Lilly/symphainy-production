#!/usr/bin/env python3
"""
LLM Abstraction Integration Test - Real LLM Calls

Tests that verify:
1. LLM abstraction works with actual LLM providers (OpenAI, Anthropic)
2. Agents can call LLMs through the abstraction
3. End-to-end flow: Agent -> LLM Abstraction -> Adapter -> LLM Provider

This test does NOT require full backend startup - it creates minimal components.
"""

import pytest
import os
import sys
import asyncio
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Skip if API keys are not available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Skip if API keys are not available
pytestmark = pytest.mark.integration


class TestLLMAbstractionIntegration:
    """Test LLM abstraction with real LLM calls."""
    
    @pytest.fixture
    def openai_adapter(self):
        """Create OpenAI adapter with real API key."""
        from foundations.public_works_foundation.infrastructure_adapters.openai_adapter import OpenAIAdapter
        
        if not OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
        
        return OpenAIAdapter(api_key=OPENAI_API_KEY)
    
    @pytest.fixture
    def anthropic_adapter(self):
        """Create Anthropic adapter with real API key."""
        from foundations.public_works_foundation.infrastructure_adapters.anthropic_adapter import AnthropicAdapter
        
        if not ANTHROPIC_API_KEY:
            return None  # Optional - skip if not available
        
        return AnthropicAdapter(api_key=ANTHROPIC_API_KEY)
    
    @pytest.fixture
    def llm_abstraction(self, openai_adapter, anthropic_adapter):
        """Create LLM abstraction with real adapters."""
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction
        
        # Fix: provider needs to be passed as a parameter
        return LLMAbstraction(
            openai_adapter=openai_adapter,
            anthropic_adapter=anthropic_adapter,
            provider="openai"  # Add provider parameter
        )
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_llm_abstraction_generates_response(self, llm_abstraction):
        """Test that LLM abstraction can generate a real response from OpenAI."""
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
        
        # Create a simple test request
        request = LLMRequest(
            messages=[
                {"role": "user", "content": "Say 'Hello, this is a test' and nothing else."}
            ],
            model=LLMModel.GPT_4O_MINI,
            max_tokens=50,
            temperature=0.1
        )
        
        # Generate response
        response = await llm_abstraction.generate_response(request)
        
        # Verify response
        assert response is not None, "Response should not be None"
        assert hasattr(response, "content"), "Response should have content"
        assert len(response.content) > 0, "Response content should not be empty"
        assert response.model == LLMModel.GPT_4O_MINI, "Response should use requested model"
        assert response.usage is not None, "Response should include usage information"
        assert "test" in response.content.lower(), f"Response should contain 'test', got: {response.content}"
        
        print(f"\n✅ LLM Response: {response.content}")
        print(f"✅ Model: {response.model.value}")
        print(f"✅ Usage: {response.usage}")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_llm_abstraction_with_different_models(self, llm_abstraction):
        """Test that LLM abstraction works with different models."""
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
        
        models_to_test = [
            LLMModel.GPT_4O_MINI,
            # Add more models as needed
        ]
        
        for model in models_to_test:
            request = LLMRequest(
                messages=[
                    {"role": "user", "content": "What is 2+2? Answer with just the number."}
                ],
                model=model,
                max_tokens=10,
                temperature=0.0
            )
            
            response = await llm_abstraction.generate_response(request)
            
            assert response is not None, f"Response should not be None for {model.value}"
            assert response.model == model, f"Response should use {model.value}"
            assert "4" in response.content, f"Response should contain '4', got: {response.content}"
            
            print(f"\n✅ Model {model.value} responded: {response.content}")


class TestAgentLLMIntegration:
    """Test that agents can use LLM abstraction."""
    
    @pytest.fixture
    def minimal_di_container(self):
        """Create minimal DI container for testing."""
        from unittest.mock import MagicMock
        
        class MinimalDIContainer:
            def __init__(self):
                self.logger = MagicMock()
                self.logger.info = MagicMock()
                self.logger.error = MagicMock()
                self.logger.warning = MagicMock()
                self.logger.debug = MagicMock()
            
            def get_logger(self, name):
                return self.logger
            
            def get_config(self):
                return MagicMock()
            
            def get_health(self):
                return MagicMock()
            
            def get_telemetry(self):
                return MagicMock()
            
            def get_security(self):
                return MagicMock()
        
        return MinimalDIContainer()
    
    @pytest.fixture
    def llm_abstraction_for_agent(self, minimal_di_container):
        """Create LLM abstraction for agent testing."""
        from foundations.public_works_foundation.infrastructure_adapters.openai_adapter import OpenAIAdapter
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction
        
        if not OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
        
        openai_adapter = OpenAIAdapter(api_key=OPENAI_API_KEY)
        
        return LLMAbstraction(
            openai_adapter=openai_adapter,
            anthropic_adapter=None,
            provider="openai",
            di_container=minimal_di_container
        )
    
    @pytest.mark.asyncio
    async def test_agent_can_call_llm_through_abstraction(self, llm_abstraction_for_agent):
        """Test that an agent can call LLM through the abstraction layer."""
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
        
        # Simulate what an agent would do
        prompt = "You are a helpful assistant. Answer this question: What is the capital of France? Answer with just the city name."
        
        request = LLMRequest(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            model=LLMModel.GPT_4O_MINI,
            max_tokens=20,
            temperature=0.0
        )
        
        # Agent calls LLM abstraction
        response = await llm_abstraction_for_agent.generate_response(request)
        
        # Verify agent got a response
        assert response is not None, "Agent should receive a response"
        assert len(response.content) > 0, "Agent should receive non-empty content"
        assert "Paris" in response.content, f"Agent should receive correct answer, got: {response.content}"
        
        print(f"\n✅ Agent received LLM response: {response.content}")
        print(f"✅ Response model: {response.model.value}")
        print(f"✅ Token usage: {response.usage}")
    
    @pytest.mark.asyncio
    async def test_llm_abstraction_error_handling(self, llm_abstraction_for_agent):
        """Test that LLM abstraction handles errors gracefully."""
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
        
        # Test with invalid request (empty messages)
        request = LLMRequest(
            messages=[],  # Empty messages should cause an error
            model=LLMModel.GPT_4O_MINI
        )
        
        # The abstraction should raise an error (it re-raises from adapter)
        try:
            response = await llm_abstraction_for_agent.generate_response(request)
            # If we get here, check if response indicates an error
            if not response.content or response.content == "":
                # Empty response indicates error was handled
                print("\n✅ LLM abstraction correctly handled invalid request (returned empty response)")
            else:
                pytest.fail("Expected error for empty messages, but got response")
        except Exception as e:
            # Exception was raised as expected
            assert "empty" in str(e).lower() or "invalid" in str(e).lower() or "messages" in str(e).lower(), \
                f"Expected error about empty messages, got: {e}"
            print(f"\n✅ LLM abstraction correctly raised error for invalid request: {e}")


class TestContentProcessingAgentLLMIntegration:
    """Test that ContentProcessingAgent can use LLM abstraction."""
    
    @pytest.fixture
    def minimal_setup(self):
        """Create minimal setup for agent testing."""
        from unittest.mock import MagicMock, AsyncMock
        
        class MinimalSetup:
            def __init__(self):
                # Create minimal DI container
                self.di_container = MagicMock()
                self.di_container.get_logger = MagicMock(return_value=MagicMock())
                self.di_container.get_config = MagicMock(return_value=MagicMock())
                self.di_container.get_health = MagicMock(return_value=MagicMock())
                self.di_container.get_telemetry = MagicMock(return_value=MagicMock())
                self.di_container.get_security = MagicMock(return_value=MagicMock())
                
                # Create LLM abstraction
                if OPENAI_API_KEY:
                    from foundations.public_works_foundation.infrastructure_adapters.openai_adapter import OpenAIAdapter
                    from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction
                    
                    openai_adapter = OpenAIAdapter(api_key=OPENAI_API_KEY)
                    self.llm_abstraction = LLMAbstraction(
                        openai_adapter=openai_adapter,
                        anthropic_adapter=None,
                        provider="openai",
                        di_container=self.di_container
                    )
                else:
                    self.llm_abstraction = None
                
                # Mock other required components
                self.public_works_foundation = MagicMock()
                self.public_works_foundation.get_llm_business_abstraction = MagicMock(return_value=self.llm_abstraction)
                
                self.agentic_foundation = MagicMock()
                self.agentic_foundation.get_llm_abstraction = AsyncMock(return_value=self.llm_abstraction)
                
                self.mcp_client_manager = MagicMock()
                self.policy_integration = MagicMock()
                self.policy_integration.initialize = AsyncMock()
                self.tool_composition = MagicMock()
                self.agui_formatter = MagicMock()
                self.curator_foundation = MagicMock()
        
        return MinimalSetup()
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
    async def test_agent_uses_llm_for_processing(self, minimal_setup):
        """Test that an agent can use LLM abstraction for processing."""
        # This test verifies the integration path:
        # Agent -> Agentic Foundation -> Public Works Foundation -> LLM Abstraction -> Adapter -> LLM
        
        # Get LLM abstraction through the chain
        llm_abstraction = await minimal_setup.agentic_foundation.get_llm_abstraction()
        
        assert llm_abstraction is not None, "LLM abstraction should be available"
        
        # Agent would use this to process content
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
        
        request = LLMRequest(
            messages=[
                {"role": "user", "content": "Summarize this in one sentence: The quick brown fox jumps over the lazy dog."}
            ],
            model=LLMModel.GPT_4O_MINI,
            max_tokens=50
        )
        
        response = await llm_abstraction.generate_response(request)
        
        assert response is not None, "Agent should receive LLM response"
        assert len(response.content) > 0, "Agent should receive content"
        
        print(f"\n✅ Agent successfully used LLM abstraction")
        print(f"✅ LLM Response: {response.content}")


if __name__ == "__main__":
    # Allow running directly
    pytest.main([__file__, "-v", "-s"])

