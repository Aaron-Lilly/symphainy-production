# Testing Cost Controls - Quick Start Guide

**Date:** 2025-12-05  
**Purpose:** Quick reference for using cost controls in tests

---

## 🚀 Quick Start

### **Default Mode (Controlled Costs)**
```bash
# Tests use real API with cost controls enabled
python3 scripts/insurance_use_case/test_universal_mapper_declarative_comprehensive.py
```
**Cost:** ~$0.01-0.05 per run (with caching)

---

### **Zero Cost Mode (Mocks Only)**
```bash
# Tests use mocks - zero API costs
TEST_USE_REAL_LLM=false python3 scripts/insurance_use_case/test_universal_mapper_declarative_comprehensive.py
```
**Cost:** $0

---

### **Full Real API Mode (Limited Runs)**
```bash
# Full real API calls (use sparingly)
TEST_USE_REAL_LLM=true \
TEST_ENABLE_RETRIES=true \
TEST_MAX_TOKENS=2000 \
TEST_MAX_COST=5.00 \
python3 scripts/insurance_use_case/test_universal_mapper_declarative_comprehensive.py
```
**Cost:** ~$0.10-0.50 per run

---

## 💰 Cost Controls

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_USE_REAL_LLM` | `false` | Use real LLM API (true) or mocks (false) |
| `TEST_USE_CHEAPEST_MODEL` | `true` | Always use gpt-4o-mini for tests |
| `TEST_ENABLE_RETRIES` | `false` | Enable retry logic in tests |
| `TEST_MAX_TOKENS` | `50` | Maximum tokens per request |
| `TEST_TRACK_COSTS` | `true` | Track and report costs |
| `TEST_MAX_COST` | `1.00` | Maximum cost per test run ($) |
| `TEST_USE_CACHE` | `true` | Cache responses to avoid repeated calls |
| `TEST_TIMEOUT` | `30.0` | Timeout for test requests (seconds) |

---

## 📊 Cost Estimates

### **Per Test Run:**
- **Unit Tests (Mocked):** $0
- **Integration Tests (Controlled):** $0.01-0.05
- **E2E Tests (Full):** $0.10-0.50

### **Monthly (Daily CI Runs):**
- **Unit Tests:** $0
- **Integration Tests:** ~$1.50/month
- **E2E Tests:** ~$15/month
- **Total:** ~$16.50/month

---

## 🎯 Best Practices

1. **Default to Mocks** - Use `TEST_USE_REAL_LLM=false` for development
2. **Use Cache** - Enable `TEST_USE_CACHE=true` to avoid repeated calls
3. **Minimal Tokens** - Use `TEST_MAX_TOKENS=50` for most tests
4. **Disable Retries** - Use `TEST_ENABLE_RETRIES=false` in tests
5. **Track Costs** - Always enable `TEST_TRACK_COSTS=true`
6. **Set Limits** - Use `TEST_MAX_COST=1.00` to prevent overruns

---

## 🔧 Response Cache

Responses are cached in `tests/.llm_cache/responses.json`:
- **First run:** Makes real API calls, caches responses
- **Subsequent runs:** Uses cached responses (zero cost)
- **Cache cleared:** Delete `tests/.llm_cache/` directory

---

## ⚠️ Cost Limit Protection

If cost limit is exceeded:
```
RuntimeError: Test cost limit exceeded: $1.05 > $1.00. Stop tests to prevent further costs.
```

**Action:** Increase `TEST_MAX_COST` or investigate why costs are high.

---

## 📝 Example Usage

```bash
# Development (zero cost)
TEST_USE_REAL_LLM=false pytest tests/unit/

# Integration testing (controlled cost)
TEST_USE_REAL_LLM=true TEST_MAX_COST=1.00 pytest tests/integration/

# Full validation (limited runs)
TEST_USE_REAL_LLM=true TEST_MAX_COST=5.00 pytest tests/e2e/
```

---

## 🎯 Recommended Workflow

1. **Development:** Use mocks (`TEST_USE_REAL_LLM=false`)
2. **Pre-commit:** Run unit tests with mocks
3. **CI/CD:** Run integration tests with cost controls
4. **Pre-deployment:** Run full E2E tests (limited runs)

---

## 💡 Tips

- **Cache is your friend:** First run costs money, subsequent runs are free
- **Use cheapest model:** Always use `gpt-4o-mini` for tests
- **Minimize tokens:** Use `TEST_MAX_TOKENS=50` for most tests
- **Disable retries:** Retries multiply costs
- **Track everything:** Always enable cost tracking







