# Test Audit and Safety Analysis

## What Triggered the Infinite Loop Issue

### The Problematic Test

**File**: `test_file_parser_core.py`
**Test**: `test_parse_text_file` (line 163)
**Fixture**: `test_infrastructure` (line 27)

### Root Cause Analysis

The infinite loop was triggered during **test fixture initialization**, specifically:

1. **Line 64**: `pwf_result = await pwf.initialize()`
   - This initializes `PublicWorksFoundationService`
   - During initialization, it attempts to connect to:
     - **Consul** (line 1809 in `public_works_foundation_service.py`)
     - **ArangoDB** (line 1639 in `public_works_foundation_service.py`)

2. **The Hang Point**:
   - Before our fixes, `ConsulServiceDiscoveryAdapter.connect()` had **no timeout**
   - If Consul container was unavailable or in a restart loop, the connection attempt would **hang indefinitely**
   - This blocked the test fixture initialization
   - The test never got to run, but the fixture initialization never completed

3. **Why It Locked the VM Session**:
   - The test command was running in the foreground
   - The hanging connection blocked the Python process
   - If this was the only active session, it could prevent SSH access
   - Docker health check failures might have been causing container restart loops, consuming resources

### What We Fixed

✅ **Consul Connection Timeout** (5 seconds)
✅ **ArangoDB Connection Timeout** (5 seconds)
✅ **Graceful Failure** (raises ConnectionError instead of hanging)

## What to Avoid in Tests

### ❌ DON'T: Initialize Infrastructure Without Timeouts

**Bad Pattern**:
```python
@pytest.fixture
async def test_infrastructure(self):
    # This can hang indefinitely if infrastructure is unavailable
    service = SomeService()
    await service.initialize()  # No timeout!
    yield service
```

**Good Pattern**:
```python
@pytest.fixture
async def test_infrastructure(self):
    service = SomeService()
    try:
        # Use asyncio.wait_for for timeout
        result = await asyncio.wait_for(service.initialize(), timeout=10.0)
        if not result:
            pytest.skip("Infrastructure unavailable")
    except asyncio.TimeoutError:
        pytest.skip("Infrastructure initialization timed out")
    except ConnectionError as e:
        pytest.skip(f"Infrastructure connection failed: {e}")
    yield service
```

### ❌ DON'T: Call Docker Commands Without Timeouts

**Bad Pattern**:
```python
# This can hang if Docker daemon is unresponsive
result = subprocess.run(["docker", "logs", "container"], capture_output=True)
```

**Good Pattern**:
```python
# Use timeout
result = subprocess.run(
    ["docker", "logs", "container"],
    capture_output=True,
    timeout=5  # 5 second timeout
)
```

### ❌ DON'T: Use Blocking Operations in Async Tests

**Bad Pattern**:
```python
async def test_something(self):
    # This blocks the event loop
    result = requests.get("http://localhost:8500/v1/status/leader")
```

**Good Pattern**:
```python
async def test_something(self):
    # Use async HTTP client with timeout
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        async with session.get("http://localhost:8500/v1/status/leader") as resp:
            result = await resp.json()
```

### ❌ DON'T: Skip Error Handling in Fixtures

**Bad Pattern**:
```python
@pytest.fixture
async def service(self):
    service = Service()
    await service.initialize()  # If this fails, fixture fails, test fails
    yield service
```

**Good Pattern**:
```python
@pytest.fixture
async def service(self):
    service = Service()
    try:
        result = await service.initialize()
        if not result:
            pytest.skip("Service initialization failed")
    except Exception as e:
        pytest.skip(f"Service unavailable: {e}")
    yield service
```

## Safe Docker Inspection Practices

### ✅ Use the Safe Inspection Script

We've created `safe_docker_inspect.py` which:
- ✅ Uses timeouts on all Docker commands
- ✅ Prevents hanging operations
- ✅ Provides structured output
- ✅ Can inspect all containers or specific ones

**Usage**:
```bash
# Check all containers
python3 safe_docker_inspect.py --all

# Check specific container
python3 safe_docker_inspect.py symphainy-consul

# Check only health status
python3 safe_docker_inspect.py --health

# Skip logs (faster)
python3 safe_docker_inspect.py --all --no-logs
```

### ✅ Safe Docker Commands (Manual)

If you need to run Docker commands manually, always use timeouts:

```bash
# Safe: Use timeout command
timeout 5 docker logs --tail 50 symphainy-consul

# Safe: Use --since to limit log output
docker logs --since 5m symphainy-consul

# Safe: Use --tail to limit lines
docker logs --tail 100 symphainy-consul

# Safe: Check status (fast, unlikely to hang)
docker ps --filter name=symphainy-consul

# Safe: Check health (fast)
docker inspect --format '{{.State.Health.Status}}' symphainy-consul
```

### ❌ Avoid These Commands (Can Hang)

```bash
# BAD: No timeout, can hang if container is stuck
docker logs symphainy-consul

# BAD: Can hang if Docker daemon is unresponsive
docker exec symphainy-consul curl http://localhost:8500/v1/status/leader

# BAD: Can hang if container is in bad state
docker exec -it symphainy-consul /bin/sh
```

## Test Safety Recommendations

### 1. Always Use Timeouts in Async Operations

```python
import asyncio

async def safe_operation():
    try:
        result = await asyncio.wait_for(
            some_async_operation(),
            timeout=10.0
        )
        return result
    except asyncio.TimeoutError:
        raise TimeoutError("Operation timed out after 10 seconds")
```

### 2. Use pytest-timeout Plugin

Add to `pytest.ini` or `setup.cfg`:
```ini
[pytest]
timeout = 300  # 5 minute timeout for all tests
timeout_method = thread  # Use thread-based timeout
```

Or use decorator:
```python
@pytest.mark.timeout(60)  # 60 second timeout for this test
async def test_something(self):
    ...
```

### 3. Skip Tests Gracefully When Infrastructure Unavailable

```python
@pytest.fixture
async def infrastructure(self):
    try:
        # Try to connect with timeout
        result = await asyncio.wait_for(
            connect_to_infrastructure(),
            timeout=5.0
        )
        if not result:
            pytest.skip("Infrastructure unavailable")
        yield result
    except (asyncio.TimeoutError, ConnectionError) as e:
        pytest.skip(f"Infrastructure connection failed: {e}")
```

### 4. Use Health Checks Before Initialization

```python
async def check_infrastructure_health():
    """Check if infrastructure is healthy before using it."""
    try:
        # Quick health check with timeout
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
            async with session.get("http://localhost:8500/v1/status/leader") as resp:
                if resp.status == 200:
                    return True
    except Exception:
        return False
    return False
```

### 5. Monitor Test Execution

```python
import signal
import sys

def timeout_handler(signum, frame):
    print("Test execution timeout - exiting safely")
    sys.exit(124)  # Timeout exit code

# Set timeout for entire test session
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(600)  # 10 minute timeout
```

## Safe Test Execution Commands

### ✅ Safe Test Execution

```bash
# Use pytest-timeout
pytest --timeout=300 tests/integration/layer_8_business_enablement/test_file_parser_core.py

# Use timeout command as backup
timeout 600 pytest tests/integration/layer_8_business_enablement/test_file_parser_core.py

# Run in background with output redirection
nohup pytest test_file_parser_core.py > test_output.log 2>&1 &

# Check if test is still running
ps aux | grep pytest

# Kill if needed (safely)
pkill -f "pytest.*test_file_parser_core"
```

### ❌ Avoid These Patterns

```bash
# BAD: No timeout, can hang forever
pytest tests/integration/layer_8_business_enablement/test_file_parser_core.py

# BAD: Can lock terminal if test hangs
pytest -v test_file_parser_core.py

# BAD: Can consume all resources if test loops
pytest -x test_file_parser_core.py  # Without timeout
```

## Summary

### Key Takeaways

1. ✅ **Always use timeouts** for network operations and Docker commands
2. ✅ **Use the safe inspection script** (`safe_docker_inspect.py`) for Docker checks
3. ✅ **Skip tests gracefully** when infrastructure is unavailable
4. ✅ **Use pytest-timeout** plugin for test-level timeouts
5. ✅ **Monitor test execution** and have a way to kill hanging tests

### What We Fixed

- ✅ Consul connection timeout (5 seconds)
- ✅ ArangoDB connection timeout (5 seconds)
- ✅ Graceful failure instead of hanging
- ✅ Created safe Docker inspection script

### Tools Created

- ✅ `safe_docker_inspect.py` - Safe Docker container inspection with timeouts
- ✅ This document - Safety guidelines and best practices

