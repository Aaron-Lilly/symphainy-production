# Testing Cost Management Strategy

**Date:** 2025-12-05  
**Purpose:** Control LLM API costs during testing while maintaining test coverage

---

## Problem Statement

With real OpenAI API calls enabled in tests, and new retry/timeout/rate limiting features, we risk:
- **High costs** from repeated API calls during test runs
- **Rate limit violations** from too many concurrent tests
- **Slow test execution** from real network calls
- **Unpredictable costs** from retry logic

---

## Solution: Layered Testing Strategy

### **Layer 1: Unit Tests (Mocked - Zero Cost)**
- Mock LLM abstraction completely
- Test retry logic, timeout handling, JSON parsing in isolation
- Fast execution, no API costs
- **Cost: $0**

### **Layer 2: Integration Tests (Controlled Real Calls)**
- Use real LLM API but with strict controls:
  - Cheapest model (gpt-4o-mini)
  - Minimal tokens (50-100 max)
  - Single call per test (no retries in test mode)
  - Cached responses for repeated tests
- **Cost: ~$0.01-0.05 per test run**

### **Layer 3: End-to-End Tests (Real Calls - Limited)**
- Real API calls for critical workflows only
- Run on-demand or in CI (not on every commit)
- Use cheapest model
- **Cost: ~$0.10-0.50 per full test suite**

---

## Implementation Plan

### 1. Test Environment Configuration

**Create:** `tests/test_config.py`

```python
"""Test configuration for cost management."""

import os
from typing import Optional

class TestConfig:
    """Test configuration with cost controls."""
    
    # Cost control flags
    USE_REAL_LLM = os.getenv("TEST_USE_REAL_LLM", "false").lower() == "true"
    USE_CHEAPEST_MODEL = os.getenv("TEST_USE_CHEAPEST_MODEL", "true").lower() == "true"
    ENABLE_RETRIES_IN_TESTS = os.getenv("TEST_ENABLE_RETRIES", "false").lower() == "true"
    MAX_TOKENS_IN_TESTS = int(os.getenv("TEST_MAX_TOKENS", "50"))  # Minimal tokens
    
    # Cost tracking
    TRACK_COSTS = os.getenv("TEST_TRACK_COSTS", "true").lower() == "true"
    MAX_TEST_COST = float(os.getenv("TEST_MAX_COST", "1.00"))  # $1 max per test run
    
    # Model selection
    CHEAPEST_MODEL = "gpt-4o-mini"  # ~$0.15 per 1M input tokens
    
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
            return {"enabled": True, "max_attempts": 2, "base_delay": 0.1}  # Fast retries
        return {"enabled": False}  # No retries in tests
```

---

### 2. Mock LLM Abstraction for Unit Tests

**Create:** `tests/unit/fixtures/mock_llm_abstraction.py`

```python
"""Mock LLM abstraction for unit tests."""

from typing import Dict, Any, Optional
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
    
    async def generate_response(self, request: LLMRequest, **kwargs) -> LLMResponse:
        """Generate mock LLM response."""
        self.call_count += 1
        self.call_history.append({
            "request": request,
            "kwargs": kwargs
        })
        
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
    
    def reset(self):
        """Reset call count and history."""
        self.call_count = 0
        self.call_history = []
```

---

### 3. Cost Tracking Decorator

**Create:** `tests/utils/cost_tracker.py`

```python
"""Cost tracking for tests."""

import functools
from typing import Dict, Any
from datetime import datetime

class TestCostTracker:
    """Track LLM API costs during tests."""
    
    def __init__(self):
        self.costs: Dict[str, float] = {}
        self.total_cost = 0.0
        self.max_cost = 1.00  # $1 default limit
    
    def record_cost(self, test_name: str, tokens: int, model: str):
        """Record cost for a test."""
        # Model pricing (per 1M tokens)
        pricing = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50}
        }
        
        model_pricing = pricing.get(model, pricing["gpt-4o-mini"])
        # Rough estimate: assume 50/50 input/output
        cost = (tokens / 1_000_000) * ((model_pricing["input"] + model_pricing["output"]) / 2)
        
        self.costs[test_name] = self.costs.get(test_name, 0.0) + cost
        self.total_cost += cost
        
        if self.total_cost > self.max_cost:
            raise RuntimeError(
                f"Test cost limit exceeded: ${self.total_cost:.2f} > ${self.max_cost:.2f}"
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        return {
            "total_cost": self.total_cost,
            "test_costs": self.costs,
            "max_cost": self.max_cost,
            "timestamp": datetime.now().isoformat()
        }

# Global cost tracker
_cost_tracker = TestCostTracker()

def track_llm_cost(test_name: str):
    """Decorator to track LLM costs in tests."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # If using real LLM, track costs
            from tests.test_config import TestConfig
            if TestConfig.should_use_real_llm() and TestConfig.TRACK_COSTS:
                # Intercept LLM calls and track costs
                # (Implementation depends on test framework)
                pass
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

---

### 4. Test Fixtures with Response Caching

**Create:** `tests/fixtures/llm_response_cache.py`

```python
"""LLM response cache for tests."""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

class LLMResponseCache:
    """Cache LLM responses to avoid repeated API calls."""
    
    def __init__(self, cache_dir: str = "tests/.llm_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache: Dict[str, str] = {}
        self._load_cache()
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model."""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response."""
        key = self._get_cache_key(prompt, model)
        return self.cache.get(key)
    
    def set(self, prompt: str, model: str, response: str):
        """Cache response."""
        key = self._get_cache_key(prompt, model)
        self.cache[key] = response
        self._save_cache()
    
    def _load_cache(self):
        """Load cache from disk."""
        cache_file = self.cache_dir / "responses.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                self.cache = json.load(f)
    
    def _save_cache(self):
        """Save cache to disk."""
        cache_file = self.cache_dir / "responses.json"
        with open(cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
```

---

### 5. Updated Test Script with Cost Controls

**Update:** `scripts/insurance_use_case/test_universal_mapper_declarative_comprehensive.py`

```python
"""Comprehensive test with cost controls."""

import os
import sys
from tests.test_config import TestConfig
from tests.fixtures.llm_response_cache import LLMResponseCache

# Set test mode before any imports
os.environ["TEST_USE_REAL_LLM"] = os.getenv("TEST_USE_REAL_LLM", "true")  # Enable for integration tests
os.environ["TEST_USE_CHEAPEST_MODEL"] = "true"
os.environ["TEST_ENABLE_RETRIES"] = "false"  # Disable retries in tests
os.environ["TEST_MAX_TOKENS"] = "50"  # Minimal tokens
os.environ["TEST_TRACK_COSTS"] = "true"
os.environ["TEST_MAX_COST"] = "1.00"  # $1 max

# Initialize response cache
response_cache = LLMResponseCache()

async def test_llm_abstraction(agent):
    """Test LLM abstraction with cost controls."""
    test_name = "LLM Abstraction Validation"
    
    # Check if we should use real LLM
    if not TestConfig.should_use_real_llm():
        # Use mock instead
        from tests.unit.fixtures.mock_llm_abstraction import MockLLMAbstraction
        mock_llm = MockLLMAbstraction()
        agent.llm_abstraction = mock_llm
        # ... test with mock
    
    try:
        # Use cheapest model
        model = TestConfig.get_test_model()
        
        # Check cache first
        test_prompt = "What is 2+2? Respond with just the number."
        cached_response = response_cache.get(test_prompt, model)
        
        if cached_response:
            # Use cached response (zero cost)
            logger.info("   💾 Using cached LLM response (zero cost)")
            # ... use cached response
        else:
            # Make real API call (track cost)
            logger.info(f"   🧪 Making real LLM API call (model: {model}, max_tokens: {TestConfig.MAX_TOKENS_IN_TESTS})")
            llm_request = LLMRequest(
                messages=[{"role": "user", "content": test_prompt}],
                model=LLMModel[model.upper().replace("-", "_")],
                max_tokens=TestConfig.MAX_TOKENS_IN_TESTS,  # Minimal tokens
                temperature=0.0
            )
            
            llm_response = await agent.llm_abstraction.generate_response(
                llm_request,
                retry_config=TestConfig.get_test_retry_config()  # No retries in tests
            )
            
            # Cache response for future tests
            response_cache.set(test_prompt, model, llm_response.content)
            
            # Track cost
            if TestConfig.TRACK_COSTS:
                tokens = llm_response.usage.get("total_tokens", 0)
                _cost_tracker.record_cost(test_name, tokens, model)
        
        # ... rest of test
```

---

## Test Execution Modes

### **Mode 1: Unit Tests (Default - Zero Cost)**
```bash
# All tests use mocks
TEST_USE_REAL_LLM=false pytest tests/unit/
```
**Cost: $0**

---

### **Mode 2: Integration Tests (Controlled Cost)**
```bash
# Use real API but with strict controls
TEST_USE_REAL_LLM=true \
TEST_USE_CHEAPEST_MODEL=true \
TEST_ENABLE_RETRIES=false \
TEST_MAX_TOKENS=50 \
TEST_MAX_COST=1.00 \
pytest tests/integration/
```
**Cost: ~$0.01-0.05 per run**

---

### **Mode 3: Full E2E Tests (Limited Runs)**
```bash
# Full real API calls (run on-demand or in CI)
TEST_USE_REAL_LLM=true \
TEST_USE_CHEAPEST_MODEL=true \
TEST_ENABLE_RETRIES=true \
TEST_MAX_TOKENS=2000 \
TEST_MAX_COST=5.00 \
pytest tests/e2e/
```
**Cost: ~$0.10-0.50 per run**

---

## Cost Estimation

### **Per Test Run (Integration Tests):**
- **Model:** gpt-4o-mini (~$0.15 per 1M input tokens)
- **Tokens per test:** 50-100 tokens
- **Tests per run:** ~10-15 tests
- **Estimated cost:** $0.01-0.05 per run

### **Per Test Run (E2E Tests):**
- **Model:** gpt-4o-mini
- **Tokens per test:** 500-2000 tokens
- **Tests per run:** ~5-10 tests
- **Estimated cost:** $0.10-0.50 per run

### **Monthly Estimate (Daily CI Runs):**
- **Unit tests:** $0 (mocked)
- **Integration tests:** $0.05/day × 30 = $1.50/month
- **E2E tests:** $0.50/day × 30 = $15/month
- **Total:** ~$16.50/month

---

## Recommendations

### **1. Default to Mocks**
- Unit tests should always use mocks (zero cost)
- Only use real API for integration/E2E tests

### **2. Use Cheapest Model**
- Always use `gpt-4o-mini` for tests (~$0.15/1M tokens)
- Never use `gpt-4` in tests (~$30/1M tokens)

### **3. Minimize Tokens**
- Use minimal `max_tokens` (50-100 for integration, 2000 for E2E)
- Keep prompts short and focused

### **4. Disable Retries in Tests**
- Retries multiply API calls
- Use `TEST_ENABLE_RETRIES=false` for most tests

### **5. Cache Responses**
- Cache LLM responses to avoid repeated calls
- Reuse cached responses across test runs

### **6. Cost Tracking**
- Track costs per test
- Fail tests if cost limit exceeded
- Report costs in test summary

### **7. Selective Real API Testing**
- Only test retry/timeout with real API when needed
- Use mocks for JSON parsing, tool extraction, etc.

---

## Implementation Checklist

- [ ] Create `tests/test_config.py` with cost controls
- [ ] Create `tests/unit/fixtures/mock_llm_abstraction.py`
- [ ] Create `tests/utils/cost_tracker.py`
- [ ] Create `tests/fixtures/llm_response_cache.py`
- [ ] Update test script to use cost controls
- [ ] Add `.llm_cache/` to `.gitignore`
- [ ] Add cost tracking to CI/CD pipeline
- [ ] Document test execution modes in README

---

## Example Test Structure

```python
# tests/unit/test_retry_logic.py (Mocked - Zero Cost)
def test_retry_logic_with_mock():
    mock_llm = MockLLMAbstraction()
    # Test retry logic without real API calls
    # Cost: $0

# tests/integration/test_llm_integration.py (Controlled Cost)
@track_llm_cost("test_llm_integration")
async def test_llm_integration():
    # Use real API with minimal tokens
    # Cost: ~$0.01

# tests/e2e/test_full_workflow.py (Limited Runs)
@track_llm_cost("test_full_workflow")
async def test_full_workflow():
    # Full real API calls
    # Cost: ~$0.10
```

---

## Conclusion

This strategy provides:
- ✅ **Zero cost** for unit tests (mocked)
- ✅ **Controlled costs** for integration tests (~$0.01-0.05)
- ✅ **Limited costs** for E2E tests (~$0.10-0.50)
- ✅ **Cost tracking** and limits
- ✅ **Response caching** to avoid repeated calls
- ✅ **Flexible configuration** via environment variables

**Estimated monthly cost:** ~$16.50 for daily CI runs







