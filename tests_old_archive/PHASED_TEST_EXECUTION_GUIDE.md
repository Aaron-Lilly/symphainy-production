# Phased Test Execution Guide

**Purpose:** Run tests efficiently in order of complexity, making it easy to identify and fix issues.

---

## 🎯 **Strategy**

### **Why Phased Testing?**
1. **Early Detection:** Find simple issues before complex tests
2. **Easy Troubleshooting:** Failures are isolated to specific categories
3. **Efficient:** Don't waste time on complex tests if basics fail
4. **Clear Progress:** See exactly where things break

### **Test Order (Simple → Complex)**

1. **Smoke Tests** - Verify endpoints exist
2. **Configuration** - Verify config is correct
3. **Infrastructure** - Verify services are running
4. **WebSocket** - Verify WebSocket connectivity
5. **Authentication** - Verify auth works
6. **Session Management** - Verify sessions work
7. **File Upload (Basic)** - Verify file operations
8. **User Journey (Basic)** - Verify basic workflows
9. **Cross-Pillar Workflows** - Verify multi-pillar integration
10. **State Management** - Verify state persistence
11. **Real User Scenarios** - Verify real-world usage
12. **Complex Integration** - Verify complex scenarios
13. **Startup Sequence** - Verify startup order

---

## 🚀 **Usage**

### **Run All Tests (Stops on First Failure)**
```bash
./tests/scripts/run_tests_phased.sh
```

### **Run All Tests (Continue Despite Failures)**
```bash
./tests/scripts/run_tests_phased.sh --all
```

### **Run Specific Phase**
```bash
./tests/scripts/run_tests_phased.sh --phase smoke
./tests/scripts/run_tests_phased.sh --phase upload
```

### **Continue After Failure**
```bash
./tests/scripts/run_tests_phased.sh --continue
```

### **Verbose Output**
```bash
./tests/scripts/run_tests_phased.sh -v
```

---

## 📋 **Available Phases**

| Phase ID | Name | Tests |
|----------|------|-------|
| `smoke` | API Smoke Tests | Basic endpoint existence |
| `config` | Configuration Validation | Config file validation |
| `infra` | Infrastructure Health | Service health checks |
| `websocket` | WebSocket Connectivity | WebSocket connections |
| `auth` | Authentication & Registration | User registration/login |
| `session` | Session Management | Session creation |
| `upload` | File Upload (Basic) | File upload/list |
| `journey` | User Journey (Basic) | Basic user workflows |
| `cross` | Cross-Pillar Workflows | Multi-pillar integration |
| `state` | State Management | State persistence |
| `scenarios` | Real User Scenarios | Real-world usage |
| `integration` | Complex Integration | Complex scenarios |
| `startup` | Startup Sequence | Startup order validation |

---

## 🔍 **Troubleshooting Workflow**

### **Step 1: Run Phased Tests**
```bash
./tests/scripts/run_tests_phased.sh
```

### **Step 2: If a Phase Fails**
1. **Note the phase ID** (e.g., `upload`)
2. **Check the error output** - it will show which test failed
3. **Re-run just that phase** to see details:
   ```bash
   ./tests/scripts/run_tests_phased.sh --phase upload -v
   ```

### **Step 3: Fix the Issue**
- Fix the issue in the code or test
- Re-run the specific phase to verify:
  ```bash
   ./tests/scripts/run_tests_phased.sh --phase upload
   ```

### **Step 4: Continue**
- Once fixed, continue with remaining phases:
  ```bash
   ./tests/scripts/run_tests_phased.sh --continue
   ```

---

## 📊 **Example Output**

```
============================================================
SymphAIny Platform - Phased Test Execution
============================================================

✅ Backend is running

============================================================
Phase: smoke - API Smoke Tests
============================================================
...
✅ Phase smoke PASSED

============================================================
Phase: config - Configuration Validation
============================================================
...
✅ Phase config PASSED

============================================================
Test Execution Summary
============================================================
Total Phases: 13
Passed: 13
Failed: 0

✅ All phases passed!
```

---

## 💡 **Tips**

1. **Start with `--all`** to see all failures at once
2. **Then fix issues** and re-run specific phases
3. **Use `-v`** for detailed error output when debugging
4. **Check logs** if tests fail unexpectedly:
   ```bash
   docker logs symphainy-backend-test --tail 50
   ```

---

## 🎯 **Quick Reference**

```bash
# Run all, stop on first failure
./tests/scripts/run_tests_phased.sh

# Run all, continue despite failures
./tests/scripts/run_tests_phased.sh --all

# Run specific phase
./tests/scripts/run_tests_phased.sh --phase smoke

# Verbose output
./tests/scripts/run_tests_phased.sh -v

# Help
./tests/scripts/run_tests_phased.sh --help
```

---

**Ready to start?** Run the first command and let's see how we do! 🚀



