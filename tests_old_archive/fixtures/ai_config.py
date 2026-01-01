#!/usr/bin/env python3
"""
AI Configuration for Business Enablement Tests

Manages AI API configuration for integration tests (Phase 4 and Phase 5).
Supports OpenAI and other AI providers with response caching.

Usage:
    from tests.fixtures.ai_config import get_ai_config, is_ai_enabled
    
    if is_ai_enabled():
        config = get_ai_config()
        # Use config to make API calls
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================

# Default AI provider (can be overridden via environment)
DEFAULT_AI_PROVIDER = "openai"
DEFAULT_AI_MODEL = "gpt-4o-mini"  # Cheapest OpenAI model for testing
DEFAULT_MAX_TOKENS = 500  # Limit token usage
DEFAULT_TEMPERATURE = 0.7  # Consistent responses

# AI Response Cache Configuration
AI_CACHE_DIR = Path(__file__).parent.parent / "fixtures" / "ai_cache"
AI_CACHE_ENABLED = True  # Enable caching by default


# ============================================================================
# ENVIRONMENT VARIABLE NAMES
# ============================================================================

ENV_OPENAI_API_KEY = "OPENAI_API_KEY"
ENV_OPENAI_MODEL = "OPENAI_MODEL"
ENV_OPENAI_MAX_TOKENS = "OPENAI_MAX_TOKENS"
ENV_OPENAI_TEMPERATURE = "OPENAI_TEMPERATURE"
ENV_AI_PROVIDER = "AI_PROVIDER"
ENV_AI_ENABLED = "AI_ENABLED"  # Set to "true" to enable real AI calls
ENV_AI_CACHE_ENABLED = "AI_CACHE_ENABLED"


# ============================================================================
# CONFIGURATION FUNCTIONS
# ============================================================================

def is_ai_enabled() -> bool:
    """Check if AI is enabled for tests."""
    return os.getenv(ENV_AI_ENABLED, "false").lower() == "true"


def is_ai_cache_enabled() -> bool:
    """Check if AI response caching is enabled."""
    if not is_ai_enabled():
        return False
    return os.getenv(ENV_AI_CACHE_ENABLED, str(AI_CACHE_ENABLED)).lower() == "true"


def get_ai_provider() -> str:
    """Get AI provider name."""
    return os.getenv(ENV_AI_PROVIDER, DEFAULT_AI_PROVIDER)


def get_ai_config() -> Dict[str, Any]:
    """
    Get AI configuration for tests.
    
    Returns:
        Dict with AI configuration:
        - provider: AI provider name (e.g., "openai")
        - model: Model name (e.g., "gpt-4o-mini")
        - api_key: API key (if available)
        - max_tokens: Maximum tokens per request
        - temperature: Temperature setting
        - cache_enabled: Whether caching is enabled
        - cache_dir: Cache directory path
    """
    provider = get_ai_provider()
    
    config = {
        "provider": provider,
        "cache_enabled": is_ai_cache_enabled(),
        "cache_dir": str(AI_CACHE_DIR),
    }
    
    if provider == "openai":
        config.update({
            "model": os.getenv(ENV_OPENAI_MODEL, DEFAULT_AI_MODEL),
            "api_key": os.getenv(ENV_OPENAI_API_KEY),
            "max_tokens": int(os.getenv(ENV_OPENAI_MAX_TOKENS, DEFAULT_MAX_TOKENS)),
            "temperature": float(os.getenv(ENV_OPENAI_TEMPERATURE, DEFAULT_TEMPERATURE)),
        })
    else:
        # Add support for other providers here
        config.update({
            "model": "default",
            "api_key": None,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "temperature": DEFAULT_TEMPERATURE,
        })
    
    return config


def get_ai_cache_dir() -> Path:
    """Get AI cache directory path."""
    cache_dir = AI_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


# ============================================================================
# VALIDATION
# ============================================================================

def validate_ai_config() -> tuple[bool, Optional[str]]:
    """
    Validate AI configuration.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not is_ai_enabled():
        return True, None  # AI not enabled, config is valid
    
    config = get_ai_config()
    
    if config["provider"] == "openai":
        if not config.get("api_key"):
            return False, f"{ENV_OPENAI_API_KEY} environment variable is required"
    
    return True, None


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_ai_cache():
    """Initialize AI cache directory."""
    if is_ai_cache_enabled():
        cache_dir = get_ai_cache_dir()
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    return None

