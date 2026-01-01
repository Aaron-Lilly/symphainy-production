#!/usr/bin/env python3
"""
LLM Infrastructure Abstraction

Infrastructure abstraction for LLM capabilities with provider switching.
Implements LLMProtocol using configurable adapters.

WHAT (Infrastructure Role): I provide LLM capabilities with provider abstraction
HOW (Infrastructure Implementation): I coordinate multiple LLM providers and handle switching
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
import asyncio

from ..abstraction_contracts.llm_protocol import LLMProtocol, LLMRequest, LLMResponse, LLMModel
from ..infrastructure_adapters.openai_adapter import OpenAIAdapter
from ..infrastructure_adapters.anthropic_adapter import AnthropicAdapter
# Ollama adapter has been moved to archive - not part of current platform scope
# from ..infrastructure_adapters.archive.ollama_adapter import OllamaAdapter
OllamaAdapter = None  # Not in current platform scope

class LLMAbstraction:
    """LLM infrastructure abstraction with provider switching - supports factory pattern for future."""
    
    def __init__(self,
                 # Option 1: Direct adapter injection (for testing and simple cases)
                 openai_adapter: Optional[Any] = None,
                 anthropic_adapter: Optional[Any] = None,
                 ollama_adapter: Optional[Any] = None,  # OllamaAdapter is optional, not in current platform scope
                 # Option 2: Factory injection (for future dynamic creation)
                 adapter_factory: Optional[Any] = None,
                 # Configuration
                 provider: str = "openai",
                 di_container=None,
                 **kwargs):
        """
        Initialize LLM abstraction with dependency injection.
        
        Supports two patterns:
        1. Direct injection (current): Provide adapters directly
        2. Factory injection (future): Provide factory for dynamic creation
        
        At least one option must be provided.
        
        Args:
            openai_adapter: OpenAI adapter (optional if factory provided)
            anthropic_adapter: Anthropic adapter (optional if factory provided)
            ollama_adapter: Ollama adapter (optional)
            adapter_factory: Factory for creating adapters dynamically (optional)
            provider: Primary LLM provider ("openai", "anthropic", "ollama")
            di_container: DI Container for utilities (optional)
            **kwargs: Additional configuration (passed to factory if provided)
        """
        self.provider = provider
        self.di_container = di_container
        self.service_name = "llm_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("LLMAbstraction")
        
        # LLM configuration
        self.default_model = LLMModel.GPT_4O_MINI
        self.max_tokens = 4000
        self.temperature = 0.7
        
        # Production resilience configuration (from config or kwargs)
        self.retry_enabled = kwargs.get("retry_enabled", True)
        max_retries_raw = kwargs.get("max_retries", 3)
        # Ensure max_retries is an integer (config might return string)
        self.max_retries = int(max_retries_raw) if max_retries_raw is not None else 3
        retry_base_delay_raw = kwargs.get("retry_base_delay", 2.0)
        # Ensure retry_base_delay is a float (config might return string)
        self.retry_base_delay = float(retry_base_delay_raw) if retry_base_delay_raw is not None else 2.0
        timeout_raw = kwargs.get("timeout", 120.0)
        # Ensure timeout is a float (config might return string)
        self.timeout = float(timeout_raw) if timeout_raw is not None else 120.0
        self.rate_limiting_abstraction = kwargs.get("rate_limiting_abstraction", None)
        
        # Load configuration from DI container if available
        if di_container and hasattr(di_container, 'get_config'):
            config = di_container.get_config()
            if config:
                self.retry_enabled = config.get("LLM_RETRY_ENABLED", self.retry_enabled)
                max_retries_config = config.get("LLM_RETRY_ATTEMPTS", self.max_retries)
                # Ensure max_retries is an integer (config might return string)
                self.max_retries = int(max_retries_config) if max_retries_config is not None else 3
                retry_delay_config = config.get("LLM_RETRY_DELAY", self.retry_base_delay)
                # Ensure retry_base_delay is a float (config might return string)
                self.retry_base_delay = float(retry_delay_config) if retry_delay_config is not None else 2.0
                timeout_config = config.get("LLM_TIMEOUT", self.timeout)
                # Ensure timeout is a float (config might return string)
                self.timeout = float(timeout_config) if timeout_config is not None else 120.0
        
        # Initialize adapters using factory OR direct injection
        if adapter_factory:
            # FUTURE: Use factory for dynamic creation
            self.adapters = adapter_factory.create_adapters(**kwargs)
            self.logger.info("✅ LLM abstraction initialized with factory")
        elif openai_adapter or anthropic_adapter:
            # CURRENT: Use direct injection
            self.adapters = {
                "openai": openai_adapter,
                "anthropic": anthropic_adapter,
                "ollama": ollama_adapter
            }
            self.logger.info("✅ LLM abstraction initialized with direct injection")
        else:
            raise ValueError(
                "Must provide either adapters (openai_adapter, anthropic_adapter) "
                "or adapter_factory"
            )
        
        # Set primary adapter
        self.primary_adapter = self.adapters.get(provider)
        if not self.primary_adapter:
            raise ValueError(f"Provider {provider} not available")
    
    def _get_adapter(self, model: Optional[LLMModel] = None) -> Any:
        """Get appropriate adapter for model."""
        if not model:
            return self.primary_adapter
        
        # Map models to providers
        model_provider_map = {
            LLMModel.GPT_3_5_TURBO: "openai",
            LLMModel.GPT_4: "openai",
            LLMModel.GPT_4_TURBO: "openai",
            LLMModel.GPT_4O: "openai",
            LLMModel.GPT_4O_MINI: "openai",
            LLMModel.CLAUDE_3_HAIKU: "anthropic",
            LLMModel.CLAUDE_3_SONNET: "anthropic",
            LLMModel.CLAUDE_3_OPUS: "anthropic",
            LLMModel.GEMINI_PRO: "openai",  # Using OpenAI for Gemini for now
            LLMModel.GEMINI_PRO_VISION: "openai",
            LLMModel.OLLAMA_LLAMA2: "ollama",
            LLMModel.OLLAMA_LLAMA3: "ollama",
            LLMModel.OLLAMA_MISTRAL: "ollama",
            LLMModel.OLLAMA_CODELLAMA: "ollama"
        }
        
        provider = model_provider_map.get(model, self.provider)
        return self.adapters.get(provider, self.primary_adapter)
    
    async def generate_response(self, request: LLMRequest, 
                                retry_config: Optional[Dict[str, Any]] = None,
                                timeout: Optional[float] = None) -> LLMResponse:
        """
        Generate LLM response with retry logic, timeout handling, and rate limiting.
        
        Args:
            request: LLM request
            retry_config: Optional retry configuration (overrides instance defaults)
            timeout: Optional timeout in seconds (overrides instance default)
            
        Returns:
            LLMResponse: LLM response
        """
        # Use provided config or instance defaults
        retry_enabled = retry_config.get("enabled", self.retry_enabled) if retry_config else self.retry_enabled
        max_retries = retry_config.get("max_attempts", self.max_retries) if retry_config else self.max_retries
        # Ensure max_retries is an integer (config might return string)
        max_retries = int(max_retries) if max_retries is not None else 3
        retry_base_delay = retry_config.get("base_delay", self.retry_base_delay) if retry_config else self.retry_base_delay
        timeout_value = timeout or self.timeout
        # Ensure timeout_value is a float (config might return string)
        timeout_value = float(timeout_value) if timeout_value is not None else 120.0
        
        # Get appropriate adapter
        adapter = self._get_adapter(request.model)
        
        # Prepare request for adapter
        adapter_request = {
            "model": request.model.value if request.model else self.default_model.value,
            "messages": request.messages,
            "max_tokens": request.max_tokens or self.max_tokens,
            "temperature": request.temperature or self.temperature,
            "stream": request.stream or False
        }
        
        # Rate limiting check (if enabled)
        if self.rate_limiting_abstraction:
            try:
                from ..abstraction_contracts.llm_rate_limiting_protocol import RateLimitRequest
                user_id = request.metadata.get("user_id", "default") if request.metadata else "default"
                model_name = request.model.value if request.model else self.default_model.value
                
                # Estimate tokens (rough estimate: 4 chars per token)
                estimated_tokens = sum(len(msg.get("content", "")) for msg in request.messages) // 4
                
                rate_limit_request = RateLimitRequest(
                    user_id=user_id,
                    model=model_name,
                    estimated_tokens=estimated_tokens
                )
                
                rate_limit_response = await self.rate_limiting_abstraction.check_rate_limit(rate_limit_request)
                
                if not rate_limit_response.allowed:
                    self.logger.warning(
                        f"⚠️ Rate limit exceeded: {rate_limit_response.reason}. "
                        f"Retry after {rate_limit_response.retry_after}s"
                    )
                    raise RuntimeError(
                        f"Rate limit exceeded: {rate_limit_response.reason}. "
                        f"Retry after {rate_limit_response.retry_after}s"
                    )
            except Exception as e:
                # If rate limiting check fails, log but continue (non-critical)
                self.logger.debug(f"Rate limiting check failed (non-critical): {e}")
        
        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(max_retries if retry_enabled else 1):
            try:
                # Generate response with timeout
                async def _call_adapter():
                    response = await adapter.generate_completion(adapter_request)
                    
                    # Check for adapter errors
                    if "error" in response:
                        error_msg = response.get("error", "Unknown error")
                        self.logger.error(f"❌ Adapter returned error: {error_msg}")
                        raise RuntimeError(f"LLM adapter error: {error_msg}")
                    
                    return response
                
                # Apply timeout
                try:
                    response = await asyncio.wait_for(_call_adapter(), timeout=timeout_value)
                except asyncio.TimeoutError:
                    raise TimeoutError(f"LLM request timed out after {timeout_value}s")
                
                # Create LLM response
                kwargs = {
                    "response_id": response.get("id"),
                    "model": request.model or self.default_model,
                    "content": response.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "usage": response.get("usage", {}),
                    "finish_reason": response.get("choices", [{}])[0].get("finish_reason")
                }
                if response.get("metadata"):
                    kwargs["metadata"] = response.get("metadata")
                llm_response = LLMResponse(**kwargs)
                
                self.logger.info(f"✅ LLM response generated for model {llm_response.model.value}")
                return llm_response
                
            except (TimeoutError, ConnectionError) as e:
                # Retryable errors
                last_exception = e
                if retry_enabled and attempt < max_retries - 1:
                    delay = retry_base_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(
                        f"⚠️ LLM request failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Max retries exceeded or retry disabled
                    self.logger.error(f"❌ LLM request failed after {attempt + 1} attempts: {e}")
                    raise
                    
            except (ValueError, RuntimeError) as e:
                # Check if it's a rate limit error (retryable)
                error_str = str(e).lower()
                if "rate limit" in error_str or "429" in error_str:
                    # Rate limit error - retryable
                    last_exception = e
                    if retry_enabled and attempt < max_retries - 1:
                        delay = retry_base_delay * (2 ** attempt)  # Exponential backoff
                        self.logger.warning(
                            f"⚠️ Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        self.logger.error(f"❌ Rate limit exceeded after {attempt + 1} attempts: {e}")
                        raise
                else:
                    # Non-retryable errors (authentication, invalid request, etc.)
                    self.logger.error(f"❌ Non-retryable error: {e}")
                    raise
                    
            except Exception as e:
                # Unknown errors - don't retry by default
                self.logger.error(f"❌ Unexpected error in LLM request: {e}")
                raise
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        raise RuntimeError("LLM request failed for unknown reason")

        """
        Generate embeddings for text.
        
        Args:
            text: Input text
            model: Embedding model
            
        Returns:
            List[float]: Embeddings
        """
        try:
            # Determine provider from model
            if "claude" in model.lower():
                adapter = self.adapters["anthropic"]
            elif "llama" in model.lower() or "mistral" in model.lower():
                adapter = self.adapters["ollama"]
            else:
                adapter = self.adapters["openai"]
            
            # Generate embeddings using adapter
            embeddings = await adapter.generate_embeddings(text, model)
            
            self.logger.info(f"✅ Embeddings generated for text (length: {len(text)})")
            
            return embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate embeddings: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get available LLM models from all providers.
        
        Returns:
            List[Dict]: Available models
        """
        try:
            all_models = []
            
            # Get models from all adapters
            for provider, adapter in self.adapters.items():
                try:
                    models = await adapter.get_models()
                    for model in models:
                        model["provider"] = provider
                    all_models.extend(models)
                except Exception as e:
                    self.logger.error(f"❌ Error: {e}")
                    self.logger.warning(f"Failed to get models from {provider}: {e}")
            
                    raise  # Re-raise for service layer to handle

            
            return all_models
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get available models: {e}")
            raise  # Re-raise for service layer to handle

        """
        Validate if model is available.
        
        Args:
            model: Model name
            
        Returns:
            bool: Model availability
        """
        try:
            is_available = False
            
            # Check all adapters
            for adapter in self.adapters.values():
                try:
                    if await adapter.is_model_available(model):
                        is_available = True
                        break
                except Exception as e:
                    self.logger.error(f"❌ Error: {e}")
                    self.logger.warning(f"Failed to check model {model}: {e}")
            
            # Record platform operation event
                    raise  # Re-raise for service layer to handle

            
        except Exception as e:
            self.logger.error(f"❌ Failed to validate model {model}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get model information.
        
        Args:
            model: Model name
            
        Returns:
            Dict: Model information
        """
        try:
            # Check all adapters
            for provider, adapter in self.adapters.items():
                try:
                    model_info = await adapter.get_model_info(model)
                    if model_info:
                        model_info["provider"] = provider
                        return model_info
                except Exception as e:
                    self.logger.error(f"❌ Error: {e}")
                    self.logger.warning(f"Failed to get model info for {model} from {provider}: {e}")
            
                    raise  # Re-raise for service layer to handle

            
            return model_info
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get model info for {model}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Perform health check on all providers.
        
        Returns:
            Dict: Health check result
        """
        try:
            health_status = {
                "healthy": True,
                "providers": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check all adapters
            for provider, adapter in self.adapters.items():
                try:
                    provider_health = await adapter.health_check()
                    health_status["providers"][provider] = provider_health
                    
                    if not provider_health.get("healthy", False):
                        health_status["healthy"] = False
                        
                except Exception as e:
                    self.logger.error(f"❌ Error: {e}")
                    health_status["providers"][provider] = {
                        "healthy": False,
                        "error": str(e)
                    }
                    health_status["healthy"] = False
            
            return health_status

            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Switch primary provider.
        
        Args:
            provider: Provider name
            
        Returns:
            bool: Success status
        """
        try:
            if provider not in self.adapters:
                self.logger.error(f"Provider {provider} not available")
            
            self.provider = provider
            self.primary_adapter = self.adapters[provider]
            
            self.logger.info(f"✅ Switched to provider: {provider}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to switch provider: {e}")
            raise  # Re-raise for service layer to handle
