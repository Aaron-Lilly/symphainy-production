# SSH Session Crash Root Cause Analysis

## Problem Summary
SSH sessions are crashing multiple times per day during test execution. This is a new issue (last 6 months were fine).

## Root Cause Identified

### Critical Issue: Synchronous Blocking Calls in ArangoDB Adapter Initialization

**Location**: `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/arangodb_adapter.py`

**Problem Lines**:
- Line 57: `sys_db = self._client.db('_system', username=username, password=password)`
- Line 71: `self._db: StandardDatabase = self._client.db(database, username, password)`

**Why This Causes SSH Crashes**:
1. These are **synchronous blocking calls** that happen during `__init__`
2. If ArangoDB is unavailable or slow, these calls can hang **indefinitely**
3. The ArangoDB adapter is created during `_create_all_adapters()` in `initialize_foundation()`
4. This blocks the entire async event loop
5. The SSH session times out and crashes

**Evidence**:
- The adapter has comments acknowledging this: "Connection attempts here are synchronous and may block if ArangoDB is unavailable"
- The `test_connection()` method is async with timeouts, but `__init__` is not
- Other adapters (Consul) use async `connect()` methods with timeouts

## Why This Started Happening Recently

Possible reasons:
1. **Infrastructure changes**: ArangoDB container may be slower to start or more frequently unavailable
2. **Test timing**: Tests may be running before infrastructure is fully ready
3. **Resource constraints**: VM may be under more load, causing slower responses
4. **Configuration changes**: Recent changes to secrets/config loading may have affected startup timing

## Solution Strategy

### Option 1: Lazy Initialization (Recommended)
- Defer connection until first use
- Make `__init__` lightweight (just store config)
- Add async `connect()` method with timeout
- Update all callers to call `connect()` before use

### Option 2: Async Initialization
- Move connection logic to async `initialize()` method
- Keep `__init__` lightweight
- Update foundation service to await adapter initialization

### Option 3: Timeout Wrapper
- Wrap blocking calls in `asyncio.wait_for()` with timeout
- Use `run_in_executor()` to make blocking calls async
- Fail fast if ArangoDB unavailable

## Recommended Fix: Lazy Initialization

This is the cleanest approach:
1. **Lightweight `__init__`**: Only store configuration, don't connect
2. **Async `connect()` method**: Connect with timeout (like Consul adapter)
3. **Connection check in operations**: Verify connection before use
4. **Update foundation service**: Call `await adapter.connect()` after creation

## Additional Issues Found

1. **No timeout on adapter creation**: `_create_all_adapters()` doesn't have timeouts
2. **Health checks happen too late**: Early health checks in conftest help, but adapter creation still blocks
3. **Other adapters may have similar issues**: Should audit all adapters for blocking `__init__` calls

## Implementation Plan

1. ✅ Fix ArangoDB adapter to use lazy initialization
2. ✅ Update foundation service to call `connect()` after creation
3. ✅ Add timeout to adapter creation in `_create_all_adapters()`
4. ✅ Audit other adapters for similar issues
5. ✅ Test with unavailable ArangoDB to verify fix




