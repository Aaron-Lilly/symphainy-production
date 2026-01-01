# Real Infrastructure Testing Guide

**Philosophy:** Use real infrastructure by default to catch production issues early.

---

## 🎯 Why Real Infrastructure?

### The Problem with Mocks
- ❌ Mocks don't catch real integration issues
- ❌ Mocks don't validate actual LLM reasoning
- ❌ Mocks don't test real authentication flows
- ❌ Mocks can hide production surprises

### The Solution: Real Infrastructure
- ✅ Catch actual production issues early
- ✅ Validate real LLM reasoning (agentic-forward approach)
- ✅ Test real Supabase authentication and rate limiting
- ✅ No unpleasant surprises in production

---

## 🔧 Configuration

### Test Supabase Project

**Why:** Separate test project with rate limiting prevention

**Setup:**
1. Create a test Supabase project (separate from production)
2. Configure in `.env.test`:
   ```bash
   TEST_SUPABASE_URL=https://your-test-project.supabase.co
   TEST_SUPABASE_ANON_KEY=your-test-anon-key
   TEST_SUPABASE_SERVICE_KEY=your-test-service-key
   TEST_SUPABASE_JWKS_URL=https://your-test-project.supabase.co/auth/v1/.well-known/jwks.json
   TEST_SUPABASE_JWT_ISSUER=https://your-test-project.supabase.co/auth/v1
   ```

**Benefits:**
- ✅ No rate limiting issues
- ✅ Isolated test data
- ✅ Safe to run extensive tests

---

### Real LLM Calls (Cheaper Models)

**Why:** Validate actual LLM reasoning while minimizing costs

**Configuration:**
```bash
# Use cheaper models for testing
TEST_OPENAI_API_KEY=your-openai-api-key
TEST_OPENAI_MODEL=gpt-3.5-turbo  # Cheaper than gpt-4

# Or use Anthropic
TEST_ANTHROPIC_API_KEY=your-anthropic-api-key
TEST_ANTHROPIC_MODEL=claude-3-haiku-20240307  # Cheaper than claude-3-opus
```

**Cheaper Models:**
- **OpenAI:** `gpt-3.5-turbo` (default) - ~90% cheaper than gpt-4
- **Anthropic:** `claude-3-haiku-20240307` (default) - ~95% cheaper than claude-3-opus

**Benefits:**
- ✅ Validate real LLM reasoning
- ✅ Test agentic-forward approach
- ✅ Catch LLM integration issues
- ✅ Minimize costs with cheaper models

---

### Real Infrastructure Services

**Configuration:**
```bash
# Use Docker Compose test services (default)
TEST_ARANGO_URL=http://localhost:8529
TEST_REDIS_URL=redis://localhost:6379
TEST_CONSUL_HOST=localhost

# Or use real services
TEST_ARANGO_URL=https://your-arangodb-instance.com
TEST_REDIS_URL=redis://your-redis-instance.com:6379
```

**Benefits:**
- ✅ Test real database operations
- ✅ Validate actual service interactions
- ✅ Catch integration issues early

---

## 🚀 Usage

### Default Behavior (Real Infrastructure)

Tests use real infrastructure by default:

```python
# Tests automatically use real Supabase and LLMs
def test_user_authentication(di_container):
    # Uses real Supabase test project
    # Uses real LLM (cheaper models)
    # Uses real infrastructure services
    pass
```

### Override to Use Mocks

If you need to use mocks for specific tests:

```python
import pytest
from unittest.mock import Mock

@pytest.mark.skipif(
    TestConfig.USE_REAL_INFRASTRUCTURE,
    reason="Skipping when real infrastructure is enabled"
)
def test_with_mocks():
    # Use mocks instead
    pass
```

Or set environment variable:
```bash
export TEST_USE_REAL_INFRASTRUCTURE=false
export TEST_USE_REAL_LLM=false
```

---

## 📊 Cost Management

### LLM Costs

**Cheaper Models (Default):**
- `gpt-3.5-turbo`: ~$0.002 per 1K tokens
- `claude-3-haiku`: ~$0.00025 per 1K tokens

**Example Test Run:**
- 100 tests × 1K tokens each = 100K tokens
- Cost: ~$0.20 (gpt-3.5-turbo) or ~$0.025 (claude-3-haiku)

**Cost Optimization:**
- Use cheaper models by default
- Cache LLM responses when possible
- Skip LLM tests if no API key: `TEST_SKIP_LLM_TESTS=true`

---

## ✅ Validation

### Check Infrastructure Availability

```python
from config.test_config import TestConfig

# Check what's configured
validation = TestConfig.validate_real_infrastructure()
print(validation)  # {'supabase': True, 'openai': True, ...}

# Get missing services
missing = TestConfig.get_missing_infrastructure()
if missing:
    print(f"Missing: {missing}")
```

### Skip Tests if Infrastructure Missing

```python
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure

def test_requires_supabase():
    skip_if_missing_real_infrastructure(["supabase"])
    # Test code here
```

---

## 🔒 Security

### Test Credentials

- ✅ Use separate test Supabase project
- ✅ Use test API keys (not production keys)
- ✅ Never commit `.env.test` to git
- ✅ Rotate test credentials regularly

### Environment Variables

Test credentials are loaded from:
1. `.env.test` file (if exists)
2. Environment variables (TEST_*)
3. Fallback to production variables (with warning)

---

## 📝 Best Practices

1. **Always Use Real Infrastructure for Integration/E2E Tests**
   - Catch production issues early
   - Validate real service interactions

2. **Use Cheaper LLM Models for Testing**
   - Validate functionality
   - Minimize costs
   - Still catch LLM integration issues

3. **Use Test Supabase Project**
   - Avoid rate limiting
   - Isolated test data
   - Safe for extensive testing

4. **Skip Tests if Infrastructure Missing**
   - Don't fail tests if infrastructure unavailable
   - Provide clear error messages
   - Allow graceful degradation

---

**Last Updated:** January 2025



