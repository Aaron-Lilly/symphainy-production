# Test Implementation Guide - Fail Instead of Skip

## 🎯 Overview

This guide shows how to update all test layers (0-7) to **fail instead of skip** when infrastructure is unavailable, providing detailed diagnostics.

---

## ✅ What's Been Done

### 1. Comprehensive Gap Analysis
**File**: `tests/integration/COMPREHENSIVE_LAYER_GAP_ANALYSIS.md`

- Analyzed all layers 0-7
- Identified gaps in each layer
- Documented missing tests
- Created implementation plan

### 2. Infrastructure Pre-Flight Tests
**File**: `tests/integration/layer_0_startup/test_infrastructure_preflight.py`

- Docker container health checks
- Infrastructure connectivity tests with timeouts
- Configuration validation
- Celery app module verification

**These tests run FIRST and FAIL (not skip) when infrastructure is unavailable.**

---

## 📋 Pattern for Updating Tests

### **Before (Problematic)**
```python
@pytest.mark.asyncio
async def test_foundation_initializes(self):
    try:
        pwf = PublicWorksFoundationService(di_container=di_container)
        pwf_result = await pwf.initialize()
        
        if not pwf_result:
            pytest.skip("Public Works Foundation requires infrastructure")
        
        assert pwf_result is True
    except ImportError as e:
        pytest.skip(f"Public Works Foundation not available: {e}")
    except Exception as e:
        pytest.skip(f"Initialization requires infrastructure: {e}")
```

**Problem**: Tests skip, hiding configuration issues.

---

### **After (Fixed)**
```python
@pytest.mark.asyncio
async def test_foundation_initializes(self):
    """Test that foundation initializes correctly. FAILS with diagnostics if infrastructure unavailable."""
    try:
        pwf = PublicWorksFoundationService(di_container=di_container)
        pwf_result = await pwf.initialize()
        
        if not pwf_result:
            # Check infrastructure status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                f"Check Docker containers: docker ps --filter name=symphainy-\n"
                f"Check logs: docker logs <container_name>"
            )
        
        assert pwf_result is True, "Public Works Foundation should initialize"
        assert pwf.is_initialized, "Public Works Foundation should be marked as initialized"
        
    except ImportError as e:
        pytest.fail(
            f"Public Works Foundation not available: {e}\n\n"
            f"Check that foundations are installed and in Python path"
        )
    except ConnectionError as e:
        # ConnectionError means infrastructure unavailable (with timeout)
        pytest.fail(
            f"Infrastructure connection failed: {e}\n\n"
            f"This indicates infrastructure is unavailable or misconfigured.\n"
            f"Check Docker containers and configuration."
        )
    except Exception as e:
        # Check if it's an infrastructure-related error
        error_str = str(e).lower()
        if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
            pytest.fail(
                f"Infrastructure error during initialization: {e}\n\n"
                f"Check Docker containers: docker ps --filter name=symphainy-\n"
                f"Check configuration: Verify ports and environment variables match Docker containers"
            )
        else:
            # Re-raise non-infrastructure errors
            raise
```

**Benefits**: Tests fail with detailed diagnostics, making it easy to identify and fix issues.

---

## 🔧 Helper Functions

Add these helper functions to test files or `conftest.py`:

```python
def check_container_status(container_name: str) -> Dict[str, any]:
    """Check Docker container status."""
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", 
             "{{.State.Status}}|{{.State.Health.Status}}|{{.RestartCount}}", 
             container_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return {"exists": False, "status": "not_found", "error": result.stderr}
        
        parts = result.stdout.strip().split("|")
        return {
            "exists": True,
            "status": parts[0] if len(parts) > 0 else "unknown",
            "health": parts[1] if len(parts) > 1 else "unknown",
            "restart_count": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        }
    except Exception as e:
        return {"exists": False, "status": "error", "error": str(e)}
```

---

## 📝 Files to Update

### **Priority 1: Critical (Do First)**

1. **Layer 0**: `tests/integration/layer_0_startup/test_platform_startup.py`
   - ✅ Already has pre-flight tests
   - ⚠️ Update existing tests to fail instead of skip

2. **Layer 2**: `tests/integration/layer_2_public_works/adapters/test_adapters_initialization.py`
   - Update all adapter tests to fail with diagnostics
   - Add connectivity tests with timeouts

### **Priority 2: High (Do Next)**

3. **Layer 1**: `tests/integration/layer_1_utilities/test_di_container_functionality.py`
4. **Layer 3**: `tests/integration/layer_3_curator/test_curator_foundation.py`
5. **Layer 4**: `tests/integration/layer_4_communication/test_communication_foundation.py`
6. **Layer 5**: `tests/integration/layer_5_agentic/test_agentic_foundation.py`
7. **Layer 6**: `tests/integration/layer_6_experience/test_experience_foundation.py`
8. **Layer 7**: `tests/integration/layer_7_smart_city/test_all_smart_city_services.py`

---

## 🎯 Key Principles

1. **Fail, Don't Skip**: When infrastructure is unavailable, tests should **fail** with detailed diagnostics, not skip.

2. **Provide Diagnostics**: Error messages should include:
   - Container status (running, stopped, restarting)
   - Health status (healthy, unhealthy, unknown)
   - Connection errors with timeouts
   - Configuration mismatches
   - Suggested fixes

3. **Use Timeouts**: All connectivity tests should use `asyncio.wait_for` with 5-second timeout.

4. **Check Infrastructure First**: Before testing functionality, verify infrastructure is available.

5. **Distinguish Error Types**:
   - `ConnectionError` with timeout → Infrastructure unavailable
   - `ImportError` → Code/dependency issue
   - Other exceptions → Re-raise or provide specific diagnostics

---

## 📊 Test Execution Order

Tests should run in this order:

1. **Pre-flight checks** (`test_infrastructure_preflight.py`) - Run first, fail fast
2. **Layer 0 tests** - Platform startup
3. **Layer 1 tests** - DI Container
4. **Layer 2 tests** - Public Works Foundation
5. **Layer 3-7 tests** - Other foundations and realms

If pre-flight checks fail, all other tests will fail quickly with clear diagnostics.

---

## 🔍 Example: Complete Test Update

### **File**: `tests/integration/layer_2_public_works/adapters/test_adapters_initialization.py`

**Before**:
```python
async def test_redis_adapter_initializes(self):
    try:
        # ... initialization code ...
        if not pwf_result:
            pytest.skip("Public Works Foundation requires infrastructure")
    except Exception as e:
        pytest.skip(f"Redis adapter initialization requires infrastructure: {e}")
```

**After**:
```python
async def test_redis_adapter_initializes(self):
    """Test that Redis adapter initializes correctly. FAILS with diagnostics if Redis unavailable."""
    try:
        di_container = DIContainerService("test_platform")
        pwf = PublicWorksFoundationService(di_container=di_container)
        pwf_result = await pwf.initialize()
        
        if not pwf_result:
            # Check Redis container status
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization failed (required for Redis adapter).\n"
                f"Redis container status: {redis_status['status']} (health: {redis_status['health']})\n\n"
                f"Check: docker logs symphainy-redis\n"
                f"Start: docker-compose -f docker-compose.infrastructure.yml up -d redis"
            )
        
        redis_adapter = pwf.redis_adapter
        assert redis_adapter is not None, "Redis adapter should be available"
        
        # Test actual connectivity
        try:
            await asyncio.wait_for(
                redis_adapter.get("test_key"),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            pytest.fail(
                f"Redis adapter connection timeout (5 seconds).\n"
                f"Redis container may be running but not responding.\n"
                f"Check: docker logs symphainy-redis"
            )
        except Exception as e:
            # Connection errors are OK for this test (we're just testing initialization)
            pass
        
    except ImportError as e:
        pytest.fail(f"Redis adapter not available: {e}")
    except ConnectionError as e:
        pytest.fail(
            f"Redis connection failed: {e}\n\n"
            f"Check Redis container: docker ps --filter name=symphainy-redis\n"
            f"Check Redis logs: docker logs symphainy-redis"
        )
    except Exception as e:
        error_str = str(e).lower()
        if "infrastructure" in error_str or "connection" in error_str:
            pytest.fail(
                f"Infrastructure error: {e}\n\n"
                f"Check Docker containers and configuration."
            )
        else:
            raise
```

---

## ✅ Success Criteria

After updating all tests:

1. ✅ All tests fail (not skip) when infrastructure is unavailable
2. ✅ All failures include detailed diagnostics (container status, connection errors, configuration issues)
3. ✅ All connectivity tests use timeouts (5 seconds)
4. ✅ Pre-flight checks run first and catch infrastructure issues early
5. ✅ Error messages are actionable (tell user what to check/fix)

---

## 🚀 Next Steps

1. **Update Layer 0 tests** - Change skip to fail in `test_platform_startup.py`
2. **Update Layer 2 adapter tests** - Add connectivity tests and change skip to fail
3. **Update Layers 1, 3-7** - Apply same pattern to all remaining layers
4. **Add connectivity tests** - Add timeout-based connectivity tests to all layers
5. **Test the changes** - Run tests and verify failures provide useful diagnostics

---

## 📚 Reference

- **Gap Analysis**: `tests/integration/COMPREHENSIVE_LAYER_GAP_ANALYSIS.md`
- **Pre-flight Tests**: `tests/integration/layer_0_startup/test_infrastructure_preflight.py`
- **Original Gap Analysis**: `tests/integration/layer_8_business_enablement/EARLY_LAYER_TEST_GAP_ANALYSIS.md`

