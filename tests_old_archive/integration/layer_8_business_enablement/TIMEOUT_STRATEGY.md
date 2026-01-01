# Test Timeout Strategy - Preventing Resource Exhaustion

## 🎯 Purpose

This document outlines the timeout strategy for all tests to prevent:
- **Resource Exhaustion**: Tests hanging indefinitely consume CPU, memory, and file descriptors
- **SSH Access Issues**: Resource exhaustion can make VM unresponsive, breaking SSH access
- **Test Suite Blocking**: One hanging test blocks the entire test suite

---

## ⚙️ Configuration

### **pytest-timeout Plugin**

**Installation**: `pytest-timeout==2.2.0` (in `tests/requirements.txt`)

**Configuration** (in `pytest.ini`):
```ini
--timeout=60              # Default timeout: 60 seconds
--timeout-method=thread   # Use thread-based timeout (works with async)
```

**Why Thread Method**:
- Works with async/await code
- Doesn't interfere with event loops
- More reliable than signal-based timeouts

---

## 📋 Timeout Tiers

### **Default Timeout: 60 seconds**

All tests default to **60 seconds** unless explicitly marked otherwise.

**Rationale**:
- Most tests should complete in < 60 seconds
- Prevents indefinite hangs
- Allows enough time for infrastructure initialization
- Fast enough to detect issues quickly

---

### **Timeout Markers**

Use markers to specify custom timeouts for specific tests:

```python
@pytest.mark.timeout_10   # 10 seconds - Very fast unit tests
@pytest.mark.timeout_30   # 30 seconds - Fast integration tests
@pytest.mark.timeout_60   # 60 seconds - Default (most tests)
@pytest.mark.timeout_120  # 120 seconds - Slower integration tests
@pytest.mark.timeout_300  # 300 seconds - E2E tests, complex scenarios
@pytest.mark.timeout_600  # 600 seconds - Very long-running tests (rare)
```

**Example**:
```python
@pytest.mark.asyncio
@pytest.mark.timeout_30
async def test_fast_integration(smart_city_infrastructure):
    """Fast integration test with 30 second timeout."""
    # Test code here
```

---

## 🎯 Timeout Guidelines by Test Type

### **Unit Tests** (`@pytest.mark.unit`)
- **Default**: 10 seconds
- **Marker**: `@pytest.mark.timeout_10`
- **Rationale**: Unit tests should be fast and isolated

### **Integration Tests** (`@pytest.mark.integration`)
- **Default**: 60 seconds
- **Marker**: `@pytest.mark.timeout_60` (or omit for default)
- **Rationale**: May need to initialize infrastructure, connect to services

### **E2E Tests** (`@pytest.mark.e2e`)
- **Default**: 300 seconds (5 minutes)
- **Marker**: `@pytest.mark.timeout_300`
- **Rationale**: Full platform initialization, multiple services, complex workflows

### **Functional Tests** (`@pytest.mark.functional`)
- **Default**: 120 seconds
- **Marker**: `@pytest.mark.timeout_120`
- **Rationale**: Real file processing, AI API calls, complex operations

### **AI Tests** (`@pytest.mark.ai`)
- **Default**: 300 seconds
- **Marker**: `@pytest.mark.timeout_300`
- **Rationale**: AI API calls can be slow, may need retries

---

## 🔧 Per-Test Timeout Override

### **Method 1: Marker (Recommended)**

```python
@pytest.mark.asyncio
@pytest.mark.timeout_30
async def test_specific_timeout(smart_city_infrastructure):
    """Test with custom 30 second timeout."""
    # Test code
```

### **Method 2: Decorator**

```python
import pytest

@pytest.mark.asyncio
@pytest.mark.timeout(30)  # Direct timeout value
async def test_direct_timeout(smart_city_infrastructure):
    """Test with direct timeout value."""
    # Test code
```

### **Method 3: Command Line**

```bash
# Override default timeout for specific test
pytest tests/integration/layer_8_business_enablement/test_file_parser_functional.py::TestFileParserFunctional::test_file_parser_actually_parses_excel_file --timeout=120
```

---

## 🛡️ Timeout Best Practices

### **✅ DO**

1. **Use appropriate timeouts**:
   - Unit tests: 10 seconds
   - Integration tests: 60 seconds
   - E2E tests: 300 seconds

2. **Mark slow tests explicitly**:
   ```python
   @pytest.mark.slow
   @pytest.mark.timeout_300
   async def test_complex_scenario():
       # Test code
   ```

3. **Use async timeouts for async operations**:
   ```python
   result = await asyncio.wait_for(
       service.initialize(),
       timeout=30.0
   )
   ```

4. **Handle timeout errors gracefully**:
   ```python
   try:
       result = await asyncio.wait_for(operation(), timeout=30.0)
   except asyncio.TimeoutError:
       pytest.fail("Operation timed out after 30 seconds")
   ```

### **❌ DON'T**

1. **Don't disable timeouts**:
   ```python
   # ❌ BAD - No timeout protection
   @pytest.mark.timeout(0)  # Disables timeout
   async def test_no_timeout():
       # This can hang indefinitely
   ```

2. **Don't set extremely long timeouts**:
   ```python
   # ❌ BAD - Too long, defeats purpose
   @pytest.mark.timeout(3600)  # 1 hour - too long
   ```

3. **Don't rely only on pytest-timeout**:
   ```python
   # ✅ GOOD - Multiple layers of protection
   @pytest.mark.timeout_60  # pytest-timeout
   async def test_with_protection():
       result = await asyncio.wait_for(  # asyncio timeout
           operation(),
           timeout=30.0
       )
   ```

---

## 🔍 Timeout Debugging

### **When a Test Times Out**

1. **Check the timeout value**:
   ```bash
   pytest -v --timeout=60 test_file.py::test_name
   ```

2. **Check for hanging operations**:
   - Network calls without timeouts
   - File operations on slow disks
   - Infinite loops
   - Deadlocks

3. **Check infrastructure status**:
   ```python
   from tests.utils.safe_docker import check_container_status
   consul_status = check_container_status("symphainy-consul")
   # Check if containers are healthy
   ```

4. **Add intermediate timeouts**:
   ```python
   # Break down long operations into smaller chunks with timeouts
   result1 = await asyncio.wait_for(step1(), timeout=10.0)
   result2 = await asyncio.wait_for(step2(), timeout=10.0)
   ```

---

## 📊 Timeout Statistics

### **Expected Test Durations**

| Test Type | Expected Duration | Timeout | Margin |
|-----------|------------------|---------|--------|
| Unit | < 1 second | 10 seconds | 10x |
| Integration | 5-30 seconds | 60 seconds | 2-12x |
| Functional | 10-60 seconds | 120 seconds | 2-12x |
| E2E | 30-180 seconds | 300 seconds | 1.7-10x |

**Margin**: Timeout should be 2-10x expected duration to account for:
- Infrastructure startup delays
- Network latency
- Resource contention
- System load

---

## 🚨 Timeout Failures

### **What Happens When a Test Times Out**

1. **pytest-timeout kills the test**:
   - Sends signal to test thread
   - Test is marked as failed
   - Test output shows timeout error

2. **Test output**:
   ```
   FAILED test_file.py::test_name - TimeoutError: Test timed out after 60.0 seconds
   ```

3. **Resource cleanup**:
   - pytest-timeout attempts to clean up
   - But some resources may remain (file descriptors, connections)
   - This is why we also use `asyncio.wait_for()` for async operations

---

## 🔄 Migration Guide

### **For Existing Tests**

1. **Add timeout markers**:
   ```python
   # Before
   @pytest.mark.asyncio
   async def test_example():
       # Test code
   
   # After
   @pytest.mark.asyncio
   @pytest.mark.timeout_60  # Add appropriate timeout
   async def test_example():
       # Test code
   ```

2. **Review long-running tests**:
   - Identify tests that take > 60 seconds
   - Add appropriate timeout markers
   - Consider optimizing slow tests

3. **Add async timeouts**:
   ```python
   # Before
   result = await service.initialize()
   
   # After
   result = await asyncio.wait_for(
       service.initialize(),
       timeout=30.0
   )
   ```

---

## 📚 Related Documents

- `SSH_BREAK_ROOT_CAUSE_ANALYSIS.md` - Why timeouts are critical
- `SSH_ACCESS_GUARDRAILS.md` - SSH access protection
- `TEST_AUDIT_AND_SAFETY.md` - Test safety guidelines

---

## ✅ Verification

After implementing timeouts:

1. ✅ All tests have timeout protection (default or explicit)
2. ✅ Timeout values are appropriate for test type
3. ✅ Tests fail fast when they hang
4. ✅ Resource exhaustion is prevented
5. ✅ SSH access remains stable

---

## 🎯 Summary

**Key Principles**:
1. **Default timeout**: 60 seconds for all tests
2. **Explicit timeouts**: Use markers for custom timeouts
3. **Multiple layers**: pytest-timeout + asyncio.wait_for()
4. **Appropriate values**: 2-10x expected duration
5. **Fast failure**: Detect hangs quickly to prevent resource exhaustion

**Result**: Tests fail fast when they hang, preventing resource exhaustion and SSH access issues.

