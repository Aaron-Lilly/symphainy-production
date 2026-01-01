# Quick Fixes Summary

**Date:** 2025-12-04  
**Status:** Ready to apply fixes

---

## ✅ **Fixes Applied**

### 1. **Infrastructure Test - Container Name** ✅
- **Fixed:** Updated to check for `symphainy-backend-test` first, then fallback to `symphainy-backend-prod`
- **File:** `tests/infrastructure/test_infrastructure_health.py`

### 2. **Session Test - Test Name** ✅
- **Fixed:** Updated script to use `test_user_registration_journey` (session creation is part of registration)
- **File:** `tests/scripts/run_tests_phased.sh`

---

## ⚠️ **Remaining Issues to Fix**

### 1. **File Upload Test - Field Name**
- **Issue:** Test sends `file` but endpoint expects `file_data`
- **File:** `tests/e2e/production/test_real_file_upload_flow.py`
- **Fix:** Change `files={"file": ...}` to `files={"file_data": ...}`

### 2. **WebSocket Tests - Library Issue**
- **Issue:** `AttributeError: module 'websockets' has no attribute 'exceptions'`
- **File:** `tests/e2e/production/test_websocket_smoke.py`
- **Fix:** Update websockets library or fix imports

### 3. **Startup Sequence - Async Cleanup**
- **Issue:** Asyncio task cleanup warnings
- **File:** `tests/e2e/production/test_production_startup_sequence.py`
- **Fix:** Improve async task cleanup (low priority)

---

## 🎯 **Next Steps**

1. **Re-run tests** to see improvement:
   ```bash
   ./tests/scripts/run_tests_phased.sh --all
   ```

2. **Fix file upload test** (high priority)

3. **Fix websocket tests** (medium priority)

4. **Re-run full suite** after fixes

---

**Current Status:** 2 fixes applied, 3 remaining issues identified



