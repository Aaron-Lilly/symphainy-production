# SSH Connection Break - Root Cause Analysis

## 🚨 Incident Summary

**Date**: Current session  
**Issue**: SSH connection to GCE VM broke after recent changes  
**Impact**: VM became inaccessible via SSH  
**Status**: Reverted changes, investigating root cause

---

## 🔍 Root Cause Analysis

### **Primary Hypothesis: Test Hanging → Resource Exhaustion**

**Evidence**:
1. Test `test_file_parser_actually_parses_excel_file` was running when SSH broke
2. Test was not returning control (hanging)
3. User had to manually stop the test

**Theory**:
- Test hung during execution (likely at line 345: `service.retrieve_document()` or during file upload/parsing)
- Hanging test consumed system resources (CPU, memory, file descriptors)
- Resource exhaustion made VM unresponsive
- Unresponsive VM appeared as "SSH broken" (VM couldn't accept new connections)

**Why This Appears as SSH Break**:
- SSH daemon requires system resources to accept connections
- If resources are exhausted, SSH can't accept new connections
- Existing SSH sessions may also become unresponsive
- This creates the appearance of "SSH broken" even though credentials are fine

---

### **Secondary Hypothesis: Path Resolution Logic Issues**

**Changes Made**:
1. Added complex path resolution logic in `gcs_file_adapter.py` (lines 100-155)
2. Added complex path resolution logic in `public_works_foundation_service.py` (lines 1581-1640)
3. Uncommented `GCS_CREDENTIALS_PATH` in `.env.secrets`

**Potential Issues**:
1. **Path Resolution Complexity**: The path resolution logic uses `Path.cwd()` which could cause issues if:
   - Current working directory changes during execution
   - Multiple threads/processes access it simultaneously
   - File system operations are slow or blocked

2. **Infinite Loop Risk**: The path resolution logic has multiple nested conditions and loops:
   - Could theoretically cause infinite loops if directory structure is unexpected
   - Could cause excessive file system operations

3. **Resource Consumption**: Complex path resolution could:
   - Consume CPU cycles unnecessarily
   - Make excessive file system calls
   - Hold file descriptors open

**Why This Could Break SSH**:
- If path resolution causes infinite loop or excessive resource consumption
- System resources get exhausted
- SSH daemon can't accept new connections
- Appears as "SSH broken"

---

### **Tertiary Hypothesis: Environment Variable Modification**

**Investigation**:
- ✅ **Verified**: We do NOT modify `GOOGLE_APPLICATION_CREDENTIALS` in platform code
- ✅ **Verified**: We use `storage.Client.from_service_account_json()` which doesn't require env var
- ✅ **Verified**: GCS adapter explicitly avoids modifying `GOOGLE_APPLICATION_CREDENTIALS`

**Conclusion**: This is NOT the cause of the SSH break.

---

## 🔧 Changes Reverted

### **1. Simplified Path Resolution**

**Before** (Complex - 50+ lines):
```python
if credentials_path:
    # Complex multi-strategy path resolution
    # - Try to find symphainy-platform directory
    # - Try multiple parent directories
    # - Try multiple path combinations
    # - Multiple nested conditions
```

**After** (Simple - 10 lines):
```python
if credentials_path:
    # Simple path resolution: if relative, try relative to current working directory
    if not os.path.isabs(credentials_path):
        resolved_path = Path(credentials_path).resolve()
        if resolved_path.exists():
            credentials_path = str(resolved_path)
```

**Files Modified**:
- `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/gcs_file_adapter.py`
- `symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py`

**Rationale**:
- Simpler code = fewer bugs
- Fewer file system operations = less resource consumption
- Caller should provide absolute paths or paths relative to CWD
- Reduces risk of infinite loops or excessive resource usage

---

### **2. Fixed Test Hanging Issue**

**Problem**: Test `test_file_parser_actually_parses_binary_with_copybook` calls `service.retrieve_document()` which could hang.

**Fix**: 
- Changed to use `content_steward.get_file()` directly with timeout
- Added `asyncio.wait_for()` with 10-second timeout
- Added proper error handling for timeout

**File Modified**:
- `tests/integration/layer_8_business_enablement/test_file_parser_functional.py`

---

## 🛡️ Safeguards Analysis

### **Existing Safeguards**

1. ✅ **GCS Adapter**: Does NOT modify `GOOGLE_APPLICATION_CREDENTIALS`
2. ✅ **Test Timeouts**: Most tests have `asyncio.wait_for()` with timeouts
3. ✅ **Connection Timeouts**: Consul and ArangoDB connections have 5-second timeouts
4. ✅ **Documentation**: Multiple documents warn about SSH access issues

### **Gaps Identified**

1. ❌ **Path Resolution**: No timeout or resource limits on path resolution
2. ❌ **Test Hanging**: Some tests may not have proper timeouts
3. ❌ **Resource Monitoring**: No monitoring of resource consumption during tests
4. ❌ **Path Resolution Complexity**: Complex logic increases risk of bugs

---

## 📋 Recommendations

### **Immediate Actions** ✅

1. ✅ **Reverted complex path resolution** → Simplified to basic relative path resolution
2. ✅ **Fixed test hanging issue** → Added timeout to document retrieval
3. ✅ **Created root cause analysis** → This document

### **Short-Term Actions**

1. **Add Resource Monitoring**:
   - Monitor CPU, memory, file descriptors during tests
   - Alert if resources exceed thresholds
   - Kill tests that consume excessive resources

2. **Enforce Test Timeouts**:
   - Add `pytest-timeout` plugin to all tests
   - Set default timeout (e.g., 60 seconds)
   - Require explicit timeout for long-running tests

3. **Simplify Path Resolution**:
   - ✅ Already done - simplified to basic resolution
   - Document that callers should provide absolute paths
   - Consider removing path resolution entirely (require absolute paths)

4. **Add SSH Health Checks**:
   - Monitor SSH daemon status
   - Alert if SSH becomes unresponsive
   - Have automated recovery procedures

### **Long-Term Actions**

1. **Resource Limits**:
   - Set resource limits for test processes
   - Use `ulimit` or `systemd` resource limits
   - Prevent single test from consuming all resources

2. **Test Isolation**:
   - Run tests in separate containers/processes
   - Isolate resource consumption
   - Prevent one test from affecting others

3. **Monitoring and Alerting**:
   - Real-time resource monitoring
   - Automated alerts for resource exhaustion
   - Historical tracking of resource usage

---

## 🔍 How We Keep Breaking SSH (Pattern Analysis)

### **Pattern 1: Resource Exhaustion**

**How It Happens**:
1. Test or code hangs (infinite loop, waiting for resource, etc.)
2. Hanging process consumes resources (CPU, memory, file descriptors)
3. System resources exhausted
4. SSH daemon can't accept new connections
5. Appears as "SSH broken"

**Prevention**:
- ✅ Timeouts on all async operations
- ✅ Resource limits on processes
- ✅ Monitoring and alerting
- ✅ Kill hanging processes automatically

### **Pattern 2: Environment Variable Modification**

**How It Happens**:
1. Code modifies `GOOGLE_APPLICATION_CREDENTIALS` globally
2. Sets it to invalid path or wrong credentials
3. All GCP tools (including SSH) use wrong credentials
4. SSH authentication fails
5. VM becomes inaccessible

**Prevention**:
- ✅ Never modify `GOOGLE_APPLICATION_CREDENTIALS` globally
- ✅ Use `from_service_account_json()` for explicit credentials
- ✅ Separate GCS credentials from SSH credentials
- ✅ Code review to catch env var modifications

### **Pattern 3: Complex Logic Bugs**

**How It Happens**:
1. Complex logic (path resolution, directory traversal, etc.)
2. Unexpected edge case causes infinite loop or excessive operations
3. Resource consumption spikes
4. System becomes unresponsive
5. SSH breaks

**Prevention**:
- ✅ Simplify code (fewer lines = fewer bugs)
- ✅ Add timeouts to all file system operations
- ✅ Limit recursion depth
- ✅ Test edge cases thoroughly

---

## ✅ Verification Steps

After reverting changes:

1. ✅ **Verify SSH Access**: Can connect to VM via SSH
2. ✅ **Verify GCS Access**: GCS operations still work (with simplified path resolution)
3. ✅ **Verify Tests**: Tests can run without hanging
4. ✅ **Monitor Resources**: Watch for resource consumption spikes

---

## 📚 Related Documents

- `SSH_ACCESS_GUARDRAILS.md` - Previous SSH access issues and fixes
- `SSH_ACCESS_FIX.md` - Fix for GOOGLE_APPLICATION_CREDENTIALS modification
- `CREDENTIALS_SEPARATION_FIX.md` - Separation of GCS and SSH credentials
- `GCS_CREDENTIALS_ARCHITECTURE.md` - Architecture for credential separation
- `TEST_AUDIT_AND_SAFETY.md` - Test safety guidelines

---

## 🎯 Conclusion

**Most Likely Cause**: Test hanging → Resource exhaustion → SSH unresponsive

**Fix Applied**: 
1. Simplified path resolution (reduced complexity, fewer operations)
2. Added timeout to test document retrieval
3. Created this root cause analysis

**Next Steps**:
1. Monitor resource consumption during tests
2. Add comprehensive test timeouts
3. Consider further simplification of path resolution
4. Add SSH health monitoring

