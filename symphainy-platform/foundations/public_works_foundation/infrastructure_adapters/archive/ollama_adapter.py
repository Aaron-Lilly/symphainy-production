#!/usr/bin/env python3
"""
Ollama Infrastructure Adapter

Raw Ollama client wrapper for LLM operations.
Thin wrapper around Ollama API with no business logic.
"""

import logging
from typing import Dict, Any, List, Optional
import aiohttp
import json


class OllamaAdapter:
    """Raw Ollama adapter for LLM operations."""
    
    def __init__(self, base_url: str = "http://localhost:11434", **kwargs):
        """
        Initialize Ollama adapter.
        
        Args:
            base_url: Ollama server base URL
        """
        self.base_url = base_url
        self.logger = logging.getLogger("OllamaAdapter")
        
        # HTTP session
        self.session = None
        
        # Initialize HTTP session
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize HTTP session."""
        try:
            self.session = aiohttp.ClientSession()
            self.logger.info("✅ Ollama adapter initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama session: {e}")
            self.session = None
    
    async def generate_completion(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate completion using Ollama.
        
        Args:
            request: Completion request
            
        Returns:
            Dict: Completion response
        """
        if not self.session:
            return {"error": "Ollama session not initialized"}
            
        try:
            # Convert messages to Ollama format
            messages = request.get("messages", [])
            prompt = self._convert_messages_to_prompt(messages)
            
            # Generate completion
            ollama_request = {
                "model": request.get("model", "llama2"),
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": request.get("temperature", 0.7),
                    "num_predict": request.get("max_tokens", 1000)
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=ollama_request
            ) as response:
                if response.status != 200:
                    return {"error": f"Ollama API error: {response.status}"}
                
                result = await response.json()
                
                # Convert to standardized format
                return {
                    "id": f"ollama_{int(datetime.now().timestamp())}",
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": result.get("response", "")
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": result.get("prompt_eval_count", 0),
                        "completion_tokens": result.get("eval_count", 0),
                        "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                    },
                    "model": request.get("model"),
                    "created": int(datetime.now().timestamp())
                }
            
        except Exception as e:
            self.logger.error(f"Failed to generate completion: {e}")
            return {"error": str(e)}
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Ollama prompt format."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)
    
    async def generate_embeddings(self, text: str, model: str = "nomic-embed-text") -> List[float]:
        """
        Generate embeddings using Ollama.
        
        Args:
            text: Input text
            model: Embedding model
            
        Returns:
            List[float]: Embeddings
        """
        if not self.session:
            return []
            
        try:
            # Generate embeddings
            ollama_request = {
                "model": model,
                "prompt": text
            }
            
            async with self.session.post(
                f"{self.base_url}/api/embeddings",
                json=ollama_request
            ) as response:
                if response.status != 200:
                    return []
                
                result = await response.json()
                return result.get("embedding", [])
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            return []
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from Ollama.
        
        Returns:
            List[Dict]: Available models
        """
        if not self.session:
            return []
            
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    return []
                
                result = await response.json()
                models = []
                
                for model in result.get("models", []):
                    models.append({
                        "id": model.get("name", ""),
                        "object": "model",
                        "created": int(model.get("modified_at", 0)),
                        "owned_by": "ollama"
                    })
                
                return models
            
        except Exception as e:
            self.logger.error(f"Failed to get models: {e}")
            return []
    
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
            if not self.session:
                return {
                    "healthy": False,
                    "error": "Ollama session not initialized"
                }
            
            # Test with a simple request
            test_response = await self.generate_completion({
                "model": "llama2",
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
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()


