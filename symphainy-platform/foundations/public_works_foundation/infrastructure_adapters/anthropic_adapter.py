#!/usr/bin/env python3
"""
Anthropic Infrastructure Adapter

Raw Anthropic client wrapper for LLM operations.
Thin wrapper around Anthropic SDK with no business logic.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import json
import logging

try:
    import anthropic
except ImportError:
    anthropic = None


class AnthropicAdapter:
    """Raw Anthropic adapter for LLM operations."""
    
    def __init__(self, api_key: str = None, config_adapter = None, **kwargs):
        """
        Initialize Anthropic adapter.
        
        Args:
            api_key: Anthropic API key (takes precedence)
            config_adapter: Optional ConfigAdapter for reading configuration (preferred over os.getenv)
        """
        self.config_adapter = config_adapter
        
        # Priority: parameter > ConfigAdapter > environment (with warning)
        if api_key:
            self.api_key = api_key
        elif config_adapter:
            self.api_key = config_adapter.get("ANTHROPIC_API_KEY")
        else:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if self.api_key:
                self.logger = logging.getLogger("AnthropicAdapter")
                self.logger.warning("⚠️ [ANTHROPIC_ADAPTER] Using os.getenv() - consider passing config_adapter for centralized configuration")
        
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger("AnthropicAdapter")
        
        # Anthropic client (private - use wrapper methods instead)
        self._client = None
        
        # Initialize Anthropic client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Anthropic client."""
        if anthropic is None:
            self.logger.error("Anthropic SDK not installed")
            return
            
        try:
            # Create Anthropic client (private)
            self._client = anthropic.AsyncAnthropic(
                api_key=self.api_key
            )
            # Keep client as alias for backward compatibility (will be removed)
            self.client = self._client
            
            self.logger.info("✅ Anthropic adapter initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic client: {e}")
            self._client = None
            self.client = None
    
    async def generate_completion(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate completion using Anthropic.
        
        Args:
            request: Completion request
            
        Returns:
            Dict: Completion response
        """
        if not self._client:
            return {"error": "Anthropic client not initialized"}
            
        try:
            # Generate completion
            response = await self._client.messages.create(
                model=request.get("model", "claude-3-sonnet-20240229"),
                max_tokens=request.get("max_tokens", 1000),
                temperature=request.get("temperature", 0.7),
                messages=request.get("messages", [])
            )
            
            # Convert to standardized format
            return {
                "id": response.id,
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response.content[0].text if response.content else ""
                        },
                        "finish_reason": response.stop_reason
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "model": request.get("model"),
                "created": int(response.created_at.timestamp())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate completion: {e}")
            return {"error": str(e)}
    
    async def generate_embeddings(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        Generate embeddings using Anthropic.
        
        Args:
            text: Input text
            model: Embedding model (Anthropic doesn't have embeddings, return empty)
            
        Returns:
            List[float]: Embeddings (empty for Anthropic)
        """
        self.logger.warning("Anthropic does not support embeddings")
        return []
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from Anthropic.
        
        Returns:
            List[Dict]: Available models
        """
        # Anthropic models (hardcoded since they don't have a models API)
        return [
            {
                "id": "claude-3-haiku-20240307",
                "object": "model",
                "created": 1677610602,
                "owned_by": "anthropic"
            },
            {
                "id": "claude-3-sonnet-20240229",
                "object": "model", 
                "created": 1677610602,
                "owned_by": "anthropic"
            },
            {
                "id": "claude-3-opus-20240229",
                "object": "model",
                "created": 1677610602,
                "owned_by": "anthropic"
            }
        ]
    
    async def is_model_available(self, model: str) -> bool:
        """
        Check if model is available.
        
        Args:
            model: Model name
            
        Returns:
            bool: Model availability
        """
        try:
            models = await self.get_models()
            model_ids = [m["id"] for m in models]
            
            available = model in model_ids
            self.logger.info(f"✅ Model {model} availability: {available}")
            return available
            
        except Exception as e:
            self.logger.error(f"Failed to check model availability {model}: {e}")
            return False
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get model information.
        
        Args:
            model: Model name
            
        Returns:
            Dict: Model information
        """
        try:
            models = await self.get_models()
            model_info = next((m for m in models if m["id"] == model), {})
            
            self.logger.info(f"✅ Retrieved model info for {model}")
            return model_info
            
        except Exception as e:
            self.logger.error(f"Failed to get model info for {model}: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            if not self._client:
                return {
                    "healthy": False,
                    "error": "Anthropic client not initialized"
                }
            
            # Test with a simple request
            test_response = await self.generate_completion({
                "model": "claude-3-haiku-20240307",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            })
            
            if "error" in test_response:
                return {
                    "healthy": False,
                    "error": test_response["error"]
                }
            
            return {
                "healthy": True,
                "model": test_response.get("model"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }


