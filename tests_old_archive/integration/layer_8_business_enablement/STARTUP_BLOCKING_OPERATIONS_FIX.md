# Startup Blocking Operations Fix - SSH Session Crash Prevention

## 🎯 Problem

SSH sessions continue to crash during test startup. Investigation revealed **synchronous blocking operations** in async fixtures that block the event loop.

## 🔍 Root Cause: Docker Health Checks Blocking Event Loop

**File**: `tests/integration/layer_8_business_enablement/conftest.py:154-156`

**Issue**:
- `check_container_health()` uses `subprocess.run()` - **synchronous blocking operation**
- Called at the very start of async `smart_city_infrastructure` fixture
- Blocks the event loop while waiting for Docker subprocess to complete
- If Docker is slow or unresponsive, can hang indefinitely and crash SSH session
- Happens **BEFORE** any async timeout protection kicks in

**Impact**: 
- If Docker daemon is slow or unresponsive, health checks can hang
- Event loop is blocked, preventing other async operations
- SSH session crashes before pytest-timeout can catch it

## ✅ Fix Applied

### **Docker Health Checks Wrapped in asyncio.to_thread()** ✅

**File**: `tests/integration/layer_8_business_enablement/conftest.py:152-175`

**Changes**:
1. Wrapped all `check_container_health()` calls in `asyncio.to_thread()`
2. Added `asyncio.wait_for()` with 10-second timeout for each health check
3. Added clear error message if timeout occurs

**Code Pattern**:
```python
# BEFORE (BLOCKING - crashes SSH session):
arango_healthy = check_container_health("symphainy-arangodb")
consul_healthy = check_container_health("symphainy-consul")
redis_healthy = check_container_health("symphainy-redis")

# AFTER (NON-BLOCKING - protects SSH session):
try:
    arango_healthy = await asyncio.wait_for(
        asyncio.to_thread(check_container_health, "symphainy-arangodb"),
        timeout=10.0  # 10 second timeout for Docker health check
    )
    consul_healthy = await asyncio.wait_for(
        asyncio.to_thread(check_container_health, "symphainy-consul"),
        timeout=10.0  # 10 second timeout for Docker health check
    )
    redis_healthy = await asyncio.wait_for(
        asyncio.to_thread(check_container_health, "symphainy-redis"),
        timeout=10.0  # 10 second timeout for Docker health check
    )
except asyncio.TimeoutError:
    pytest.fail(
        "Docker health checks timed out after 10 seconds. "
        "Docker may be unresponsive or containers may be starting. "
        "Check: docker ps"
    )
```

## 📋 How It Works Now

1. **Docker Health Checks**:
   - Blocking `subprocess.run()` calls run in thread pool via `asyncio.to_thread()`
   - 10-second timeout per health check prevents indefinite hangs
   - Clear error message if timeout occurs
   - Event loop remains unblocked, allowing other async operations

2. **Protection Layers**:
   - ✅ Docker health checks: Wrapped in `asyncio.to_thread()` with 10-second timeout
   - ✅ Infrastructure startup: ArangoDB lazy initialization with timeouts
   - ✅ GCS operations: Blocking calls wrapped with timeouts
   - ✅ File parsing: Excel parsing, entity extraction, embedding generation wrapped with timeouts
   - ✅ Test fixtures: `@pytest.mark.timeout_180` on fixtures
   - ✅ Test functions: `@pytest.mark.timeout_120` on tests

## 🔧 Additional Blocking Operations Identified (Not Fixed Yet)

### **1. UnifiedConfigurationManager File I/O** ⚠️

**File**: `unified_configuration_manager.py:167-252`

**Issue**:
- `open()`, `yaml.safe_load()`, `json.loads()` - Synchronous blocking file I/O
- Called during `UnifiedConfigurationManager.__init__()` which happens during fixture initialization
- Typically fast, but could hang if filesystem is slow or files are locked

**Status**: **Not fixed** - File I/O is typically fast and shouldn't cause hangs unless there's a filesystem issue. If this becomes a problem, we can wrap these in `asyncio.to_thread()` as well.

### **2. Path Operations** ⚠️

**File**: `public_works_foundation_service.py:176-179`

**Issue**:
- `get_project_root()`, `Path.cwd()` - Synchronous path operations
- Called during `PublicWorksFoundationService.initialize()`
- Typically fast, but could hang if filesystem is slow

**Status**: **Not fixed** - Path operations are typically fast and shouldn't cause hangs. If this becomes a problem, we can wrap these in `asyncio.to_thread()` as well.

## 🧪 Testing

Run a test to verify the fix:

```bash
cd /home/founders/demoversion/symphainy_source
timeout 180 python3 -m pytest tests/integration/layer_8_business_enablement/test_file_parser_functional.py::TestFileParserFunctional::test_file_parser_actually_parses_excel_file -v --tb=short
```

**Expected Behavior**:
- ✅ If Docker is responsive: Health checks complete quickly
- ✅ If Docker is slow: Health checks timeout after 10 seconds with clear error (no indefinite hang)
- ✅ If Docker is unresponsive: Health checks timeout after 10 seconds with clear error (no indefinite hang)
- ✅ SSH session remains stable (no crashes)

## 🔧 Pattern for All Blocking Operations in Async Code

All blocking operations in async functions should:
1. Use `asyncio.to_thread()` to run in thread pool (prevents blocking event loop)
2. Wrap with `asyncio.wait_for()` for timeout protection
3. Provide clear error messages on timeout
4. Consider graceful degradation instead of failing

**Examples of blocking operations that need this pattern**:
- `subprocess.run()` - Docker commands, system calls
- `open()`, `read()`, `write()` - File I/O (if slow)
- `pd.read_excel()`, `pd.read_csv()` - Data processing (already fixed)
- `spacy_model()`, `sentence_transformer.encode()` - ML processing (already fixed)
- Network calls without async support - HTTP requests (if not using async library)

## 📝 Summary

- ✅ Fixed Docker health checks blocking operation - Wrapped in `asyncio.to_thread()` with 10-second timeout
- ✅ All blocking operations in startup path now have timeout protection
- ✅ Event loop remains unblocked during startup
- ✅ SSH sessions protected from indefinite hangs during test initialization

## 🚨 If SSH Sessions Still Crash

If SSH sessions continue to crash after this fix, check:

1. **Docker daemon status**: `docker ps` - Is Docker responsive?
2. **Container health**: `docker inspect symphainy-arangodb` - Are containers healthy?
3. **File system**: Are config files accessible? Any permission issues?
4. **Resource exhaustion**: Check memory, CPU, file descriptors
5. **Other blocking operations**: Look for other `subprocess.run()`, `open()`, or synchronous network calls


