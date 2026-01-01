# Quick Start: Bulletproof Testing

## 🚀 Getting Started

### **Step 1: Run Pre-Test Validation**

Before running any tests, validate your environment:

```bash
cd /home/founders/demoversion/symphainy_source
./tests/scripts/pre_test_validation.sh
```

This checks:
- ✅ Critical GCP env vars are not modified
- ✅ Docker containers are running and healthy
- ✅ VM resources are adequate
- ✅ No container restart loops

### **Step 2: Run Tests Safely**

Use the safe test runner (includes timeouts and safety checks):

```bash
./tests/scripts/run_tests_safely.sh tests/integration/layer_0_startup/
```

Or run specific tests:

```bash
./tests/scripts/run_tests_safely.sh tests/integration/layer_8_business_enablement/test_file_parser_core.py
```

### **Step 3: If Something Goes Wrong**

If you lose SSH access or tests hang:

```bash
./tests/scripts/emergency_recovery.sh
```

This will:
- Unset problematic environment variables
- Stop containers in restart loops
- Kill hanging test processes
- Check VM resources

---

## 🛡️ What's Protected

### **SSH Access Protection**
- ✅ Global fixture prevents modification of `GOOGLE_APPLICATION_CREDENTIALS`
- ✅ Tests fail (not skip) if env vars are modified
- ✅ Clear error messages explain what went wrong

### **Infinite Loop Prevention**
- ✅ All Docker operations have timeouts
- ✅ All async operations have timeouts
- ✅ Container restart loops detected before tests
- ✅ Test execution has maximum time limit (10 minutes)

### **Resource Monitoring**
- ✅ VM resources checked before tests
- ✅ Container health monitored
- ✅ Alerts if resources are low

### **Early Issue Detection**
- ✅ Pre-flight checks run before all tests
- ✅ Infrastructure connectivity verified
- ✅ Configuration validated

---

## 📋 Test Execution Order

Tests run in this order (enforced by fixtures):

1. **Pre-flight checks** (automatic)
   - SSH access protection
   - VM resource check
   - Container health check

2. **Layer 0: Infrastructure Pre-flight** (`test_infrastructure_preflight.py`)
   - Docker container verification
   - Infrastructure connectivity
   - Configuration validation

3. **Layer 0: Platform Startup** (`test_platform_startup.py`)
   - Foundation initialization
   - Platform startup

4. **Layers 1-7**: Other tests

---

## 🔍 What Tests Do Now

### **Before (Problematic)**
```python
if not pwf_result:
    pytest.skip("Public Works Foundation requires infrastructure")
```

**Problem**: Tests skip, hiding configuration issues.

### **After (Bulletproof)**
```python
if not pwf_result:
    # Get detailed diagnostics
    consul_status = check_container_status("symphainy-consul")
    arango_status = check_container_status("symphainy-arangodb")
    
    pytest.fail(
        f"Public Works Foundation initialization failed.\n"
        f"Infrastructure status:\n"
        f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
        f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
        f"Check: docker logs symphainy-consul"
    )
```

**Benefit**: Tests fail with actionable diagnostics.

---

## 📚 Documentation

- **Implementation Plan**: `BULLETPROOF_TESTING_IMPLEMENTATION_PLAN.md`
- **Gap Analysis**: `COMPREHENSIVE_LAYER_GAP_ANALYSIS.md`
- **SSH Guardrails**: `layer_8_business_enablement/SSH_ACCESS_GUARDRAILS.md`
- **Implementation Guide**: `IMPLEMENTATION_GUIDE.md`

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Tests fail (not skip) when infrastructure is unavailable
2. ✅ Error messages tell you exactly what's wrong and how to fix it
3. ✅ No SSH access issues (protection fixtures prevent env var modification)
4. ✅ No infinite loops (all operations have timeouts)
5. ✅ Pre-flight checks catch issues before tests run

---

## 🎯 Next Steps

1. **Run pre-test validation** to ensure environment is safe
2. **Run Layer 0 tests** to verify infrastructure is ready
3. **Run your specific tests** using the safe test runner
4. **Review test failures** - they now provide actionable diagnostics

