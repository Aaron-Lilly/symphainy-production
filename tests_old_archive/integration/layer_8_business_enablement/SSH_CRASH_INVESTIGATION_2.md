# SSH Session Crash Investigation - Test Hanging Issue

## 🚨 Problem

Tests are hanging and crashing SSH sessions, particularly when running `test_file_parser_functional.py`.

## 🔍 Root Cause Analysis

### **1. Fixture Timeout Coverage Issue** ⚠️

**Problem**: The `smart_city_infrastructure` fixture has `asyncio.wait_for()` timeouts (30 seconds), but:
- The fixture itself doesn't have a `@pytest.mark.timeout_*` marker
- Pytest-timeout plugin may not catch fixture initialization hangs
- If fixture hangs during initialization, SSH session can crash before timeout triggers

**Location**: `tests/integration/layer_8_business_enablement/conftest.py:129`

```python
@pytest.fixture(scope="function")
async def smart_city_infrastructure():
    # ...
    try:
        pwf_result = await asyncio.wait_for(
            pwf.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        # This may not be caught if SSH session crashes first
```

### **2. ArangoDB Connection Test** ⚠️

**Problem**: ArangoDB connection test in `PublicWorksFoundationService` may hang if:
- ArangoDB is unavailable
- Network issues
- Connection pool exhaustion
- No timeout on the actual connection attempt

**Location**: `symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py:1630`

```python
arango_connected = await self.arango_adapter.test_connection()
# If this hangs, the entire fixture hangs
```

### **3. Multiple Sequential Initializations** ⚠️

**Problem**: The fixture initializes many services sequentially:
1. PublicWorksFoundationService (30s timeout)
2. CuratorFoundationService (30s timeout)
3. SmartCityServiceManager.initialize_all_services (60s timeout)

**Total potential wait**: 120+ seconds, but if any step hangs, SSH crashes before timeout.

### **4. Docker Container Status Checks** ⚠️

**Problem**: Multiple `check_container_status()` calls in error handlers:
- Each call has 5-second timeout
- If containers are unresponsive, these can accumulate
- Called in exception handlers, which may not be reached if SSH crashes

**Location**: `tests/integration/layer_8_business_enablement/conftest.py:165-167`

## 🎯 Solutions

### **Solution 1: Add Pytest Timeout to Fixture** ✅

Add timeout marker to fixture to ensure pytest-timeout plugin catches hangs:

```python
@pytest.fixture(scope="function")
@pytest.mark.timeout_180  # 3 minutes for full initialization
async def smart_city_infrastructure():
    # ...
```

### **Solution 2: Add Timeout to ArangoDB Connection Test** ✅

Ensure ArangoDB connection test has explicit timeout:

```python
# In arangodb_adapter.py
async def test_connection(self, timeout: float = 10.0) -> bool:
    try:
        result = await asyncio.wait_for(
            self._test_connection_internal(),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        return False
```

### **Solution 3: Reduce Fixture Scope or Add Caching** ✅

Consider:
- Using `scope="session"` for infrastructure fixture (initialize once)
- Or adding fixture caching/teardown to prevent re-initialization

### **Solution 4: Add Early Exit Checks** ✅

Add health checks before expensive operations:

```python
# Check containers are healthy before initialization
if not check_container_health("symphainy-arangodb"):
    pytest.skip("ArangoDB not available - skipping test")
```

### **Solution 5: Use Thread-Based Timeout for Fixtures** ✅

Ensure pytest-timeout uses thread method (already configured in pytest.ini):
- `--timeout-method=thread` catches hangs in async code better

## 📋 Immediate Actions

1. ✅ Add `@pytest.mark.timeout_180` to `smart_city_infrastructure` fixture
2. ✅ Verify ArangoDB adapter has timeout on `test_connection()`
3. ✅ Add early health checks before fixture initialization
4. ✅ Consider reducing fixture scope or adding session-level caching

## 🔧 Implementation

See fixes in:
- `tests/integration/layer_8_business_enablement/conftest.py` - Add timeout marker
- `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/arangodb_adapter.py` - Add timeout to test_connection





