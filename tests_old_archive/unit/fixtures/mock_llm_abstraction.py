#!/usr/bin/env python3
"""
Mock LLM Abstraction for Unit Tests

Simulates LLM API calls without real costs.
"""

import json
from typing import Dict, Any, Optional, List
from foundations.public_works_foundation.abstraction_contracts.llm_protocol import (
    LLMRequest, LLMResponse, LLMModel
)

class MockLLMAbstraction:
    """Mock LLM abstraction that simulates API calls without real costs."""
    
    def __init__(self, responses: Optional[Dict[str, str]] = None):
        """
        Initialize mock LLM abstraction.
        
        Args:
            responses: Optional dict of prompt -> response mappings
        """
        self.responses = responses or {}
        self.call_count = 0
        self.call_history = []
        self.should_fail = False
        self.fail_error = None
        self.should_timeout = False
    
    async def generate_response(self, request: LLMRequest, **kwargs) -> LLMResponse:
        """Generate mock LLM response."""
        self.call_count += 1
        self.call_history.append({
            "request": request,
            "kwargs": kwargs
        })
        
        # Simulate timeout if configured
        if self.should_timeout:
            import asyncio
            await asyncio.sleep(0.1)  # Small delay to simulate timeout
            raise TimeoutError("Mock LLM timeout")
        
        # Simulate failure if configured
        if self.should_fail:
            if self.fail_error:
                raise self.fail_error
            raise RuntimeError("Mock LLM failure")
        
        # Get response from mapping or use default
        prompt = request.messages[-1]["content"] if request.messages else ""
        response_content = self.responses.get(prompt, self._get_default_response(prompt))
        
        return LLMResponse(
            response_id=f"mock_{self.call_count}",
            model=request.model or LLMModel.GPT_4O_MINI,
            content=response_content,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop"
        )
    
    def _get_default_response(self, prompt: str) -> str:
        """Get default mock response."""
        return json.dumps({
            "reasoning": "Mock reasoning for test",
            "tool_calls": [],
            "response": "Mock response"
        })
    
    def set_response(self, prompt: str, response: str):
        """Set response for specific prompt."""
        self.responses[prompt] = response
    
    def set_failure(self, error: Exception = None):
        """Configure mock to fail on next call."""
        self.should_fail = True
        self.fail_error = error
    
    def set_timeout(self):
        """Configure mock to timeout on next call."""
        self.should_timeout = True
    
    def reset(self):
        """Reset call count and history."""
        self.call_count = 0
        self.call_history = []
        self.should_fail = False
        self.fail_error = None
        self.should_timeout = False







