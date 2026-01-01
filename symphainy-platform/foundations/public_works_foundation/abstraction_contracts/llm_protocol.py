#!/usr/bin/env python3
"""
LLM Protocol - Infrastructure Abstraction Contract

Protocol definition for LLM infrastructure abstractions.
Defines the interface for swappable LLM providers.
"""

from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field


class LLMModel(Enum):
    """LLM model types."""
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    OLLAMA_LLAMA2 = "llama2"
    OLLAMA_LLAMA3 = "llama3"
    OLLAMA_MISTRAL = "mistral"
    OLLAMA_CODELLAMA = "codellama"


@dataclass
class LLMRequest:
    """LLM request definition."""
    messages: List[Dict[str, str]]
    model: Optional[LLMModel] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM response definition."""
    response_id: Optional[str]
    model: LLMModel
    content: str
    usage: Dict[str, Any]
    finish_reason: Optional[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class LLMProtocol(Protocol):
    """Protocol for LLM infrastructure abstractions."""
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate LLM response."""
        ...
    
    async def generate_embeddings(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Generate embeddings for text."""
        ...
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available LLM models."""
        ...
    
    async def validate_model(self, model: str) -> bool:
        """Validate if model is available."""
        ...
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get model information."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        ...