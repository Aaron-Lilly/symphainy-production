#!/usr/bin/env python3
"""
Test Configuration for Cost Management

Controls LLM API usage in tests to manage costs.
"""

import os
from typing import Optional

class TestConfig:
    """Test configuration with cost controls."""
    
    # Cost control flags (set via environment variables)
    USE_REAL_LLM = os.getenv("TEST_USE_REAL_LLM", "false").lower() == "true"
    USE_CHEAPEST_MODEL = os.getenv("TEST_USE_CHEAPEST_MODEL", "true").lower() == "true"
    ENABLE_RETRIES_IN_TESTS = os.getenv("TEST_ENABLE_RETRIES", "false").lower() == "true"
    MAX_TOKENS_IN_TESTS = int(os.getenv("TEST_MAX_TOKENS", "50"))  # Minimal tokens for tests
    
    # Cost tracking
    TRACK_COSTS = os.getenv("TEST_TRACK_COSTS", "true").lower() == "true"
    MAX_TEST_COST = float(os.getenv("TEST_MAX_COST", "1.00"))  # $1 max per test run
    
    # Model selection
    CHEAPEST_MODEL = "gpt-4o-mini"  # ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
    
    # Response caching
    USE_RESPONSE_CACHE = os.getenv("TEST_USE_CACHE", "true").lower() == "true"
    CACHE_DIR = os.getenv("TEST_CACHE_DIR", "tests/.llm_cache")
    
    @classmethod
    def should_use_real_llm(cls) -> bool:
        """Check if tests should use real LLM."""
        return cls.USE_REAL_LLM
    
    @classmethod
    def get_test_model(cls) -> str:
        """Get model to use for testing."""
        if cls.USE_CHEAPEST_MODEL:
            return cls.CHEAPEST_MODEL
        return os.getenv("LLM_MODEL_DEFAULT", "gpt-4o-mini")
    
    @classmethod
    def get_test_retry_config(cls) -> dict:
        """Get retry config for tests."""
        if cls.ENABLE_RETRIES_IN_TESTS:
            return {
                "enabled": True,
                "max_attempts": 2,  # Reduced retries for tests
                "base_delay": 0.1  # Fast retries (100ms)
            }
        return {"enabled": False}  # No retries in tests by default
    
    @classmethod
    def get_test_timeout(cls) -> float:
        """Get timeout for tests (shorter than production)."""
        return float(os.getenv("TEST_TIMEOUT", "30.0"))  # 30s for tests vs 120s production
    
    @classmethod
    def should_track_costs(cls) -> bool:
        """Check if costs should be tracked."""
        return cls.TRACK_COSTS
    
    @classmethod
    def get_max_cost(cls) -> float:
        """Get maximum cost allowed per test run."""
        return cls.MAX_TEST_COST







