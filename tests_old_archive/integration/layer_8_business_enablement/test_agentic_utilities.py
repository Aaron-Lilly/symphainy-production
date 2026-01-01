#!/usr/bin/env python3
"""
Test Utilities for Agentic Foundation Tests

Provides mock LLM adapters and test helpers for Phase 1 (mocked) testing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class MockLLMAdapter:
    """
    Mock LLM adapter for testing.
    
    Returns predictable, context-aware responses without making real API calls.
    """
    
    def __init__(self, provider: str = "openai"):
        """Initialize mock adapter."""
        self.provider = provider
        self.call_count = 0
        self.call_history = []
    
    async def generate_completion(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock LLM completion.
        
        Returns context-aware responses based on request content.
        """
        self.call_count += 1
        
        # Extract messages from request
        messages = request.get("messages", [])
        last_message = messages[-1].get("content", "") if messages else ""
        model = request.get("model", "gpt-4o-mini")
        
        # Track call
        self.call_history.append({
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "model": model,
            "request": request
        })
        
        # Generate context-aware response
        response_content = self._generate_mock_response(last_message)
        
        return {
            "id": f"mock-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(last_message.split()) if last_message else 10,
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(last_message.split()) + len(response_content.split()) if last_message else 20
            },
            "metadata": {
                "provider": self.provider,
                "mock": True
            }
        }
    
    def _generate_mock_response(self, message: str) -> str:
        """Generate context-aware mock response."""
        message_lower = message.lower()
        
        # Guidance requests
        if "guidance" in message_lower or "help" in message_lower or "how" in message_lower:
            return (
                "Here's your guidance:\n\n"
                "1. First, identify your goal\n"
                "2. Review available capabilities\n"
                "3. Follow the recommended steps\n\n"
                "Would you like more specific guidance on any step?"
            )
        
        # Conversation requests
        if "conversation" in message_lower or "chat" in message_lower or "talk" in message_lower:
            return (
                "I'm here to help! I can assist you with:\n"
                "- Understanding capabilities\n"
                "- Providing guidance\n"
                "- Answering questions\n\n"
                "What would you like to know?"
            )
        
        # Analysis requests
        if "analyze" in message_lower or "analysis" in message_lower:
            return (
                "Analysis Results:\n\n"
                "Based on the provided data, I've identified key patterns:\n"
                "1. Primary trend: [Mocked analysis]\n"
                "2. Secondary factors: [Mocked factors]\n"
                "3. Recommendations: [Mocked recommendations]\n\n"
                "Would you like more detailed analysis?"
            )
        
        # Tool selection requests
        if "tool" in message_lower or "capability" in message_lower:
            return (
                "Available tools:\n"
                "- Tool 1: Description\n"
                "- Tool 2: Description\n"
                "- Tool 3: Description\n\n"
                "Which tool would you like to use?"
            )
        
        # Default response
        return (
            f"Mocked response for: {message[:50]}...\n\n"
            "This is a test response from the mock LLM adapter. "
            "In real usage, this would be an actual LLM response."
        )
    
    def get_call_statistics(self) -> Dict[str, Any]:
        """Get statistics about adapter calls."""
        return {
            "total_calls": self.call_count,
            "provider": self.provider,
            "call_history": self.call_history
        }
    
    def reset(self):
        """Reset call count and history."""
        self.call_count = 0
        self.call_history = []


class MockLLMAbstraction:
    """
    Mock LLM Abstraction for testing.
    
    Wraps MockLLMAdapter to provide LLMAbstraction interface.
    """
    
    def __init__(self, mock_adapter: MockLLMAdapter = None):
        """Initialize mock abstraction."""
        self.mock_adapter = mock_adapter or MockLLMAdapter()
        self.default_model = "gpt-4o-mini"
        self.max_tokens = 4000
        self.temperature = 0.7
    
    async def generate_response(self, request) -> Any:
        """
        Generate mock LLM response.
        
        Args:
            request: LLMRequest object or dict with messages, model, etc.
        
        Returns:
            LLMResponse-like object or dict
        """
        # Convert request to dict if needed
        if hasattr(request, 'messages'):
            request_dict = {
                "messages": request.messages,
                "model": getattr(request, 'model', self.default_model),
                "max_tokens": getattr(request, 'max_tokens', self.max_tokens),
                "temperature": getattr(request, 'temperature', self.temperature)
            }
        else:
            request_dict = request
        
        # Generate response
        response = await self.mock_adapter.generate_completion(request_dict)
        
        # Return as LLMResponse-like object
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMResponse, LLMModel
        
        # Convert model string to LLMModel enum if needed
        model_str = response.get("model", self.default_model)
        try:
            model = LLMModel[model_str.upper().replace("-", "_")]
        except (KeyError, AttributeError):
            model = LLMModel.GPT_4O_MINI
        
        return LLMResponse(
            response_id=response.get("id"),
            model=model,
            content=response["choices"][0]["message"]["content"],
            usage=response.get("usage", {}),
            finish_reason=response["choices"][0].get("finish_reason"),
            metadata=response.get("metadata")
        )


def create_mock_llm_abstraction(provider: str = "openai") -> MockLLMAbstraction:
    """
    Create a mock LLM abstraction for testing.
    
    Args:
        provider: LLM provider name (for tracking)
    
    Returns:
        MockLLMAbstraction instance
    """
    mock_adapter = MockLLMAdapter(provider=provider)
    return MockLLMAbstraction(mock_adapter=mock_adapter)




