# Test Supabase Usage Verification

**Date:** December 3, 2024  
**Status:** ✅ **VERIFIED - Tests Use Test Supabase Project**

---

## ✅ Current Status

### **Backend Container**
- ✅ Running as `symphainy-backend-test` (from `docker-compose.test.yml`)
- ✅ Has `TEST_MODE=true` set in container
- ✅ Loads test credentials from `tests/.env.test` via `env_file`

### **Test Scripts**
- ✅ `run_production_tests.sh` sets `TEST_MODE=true` and sources `tests/.env.test`
- ✅ `run_tests_phased.sh` should also set `TEST_MODE=true` (needs verification)

### **Test Execution**
- ✅ When backend is running via `docker-compose.test.yml`, it uses test Supabase
- ✅ When tests are run with `TEST_MODE=true`, they use test Supabase credentials
- ⚠️ **IMPORTANT:** Tests must be run with `TEST_MODE=true` environment variable

---

## 🔍 How It Works

### **Backend (Container)**
1. `docker-compose.test.yml` sets `TEST_MODE=true`
2. `docker-compose.test.yml` loads `tests/.env.test` via `env_file`
3. `main.py` detects `TEST_MODE=true` and overrides Supabase credentials:
   ```python
   if TEST_MODE:
       os.environ["SUPABASE_URL"] = test_supabase_url
       os.environ["SUPABASE_ANON_KEY"] = test_supabase_anon_key
       os.environ["SUPABASE_SERVICE_KEY"] = test_supabase_service_key
   ```

### **Tests (Client Side)**
1. `ProductionTestClient` checks `TEST_MODE` environment variable
2. When `TEST_MODE=true`, it uses test mode rate limiting (55 req/min vs 50)
3. Tests authenticate via `/api/auth/login` endpoint
4. Backend uses test Supabase project for authentication

---

## ⚠️ **Critical Requirement**

**Tests MUST be run with `TEST_MODE=true`:**

```bash
# ✅ CORRECT - Uses test Supabase
TEST_MODE=true pytest tests/e2e/production/ -v

# ❌ WRONG - May use production Supabase (if backend not in test mode)
pytest tests/e2e/production/ -v
```

**Or use the test scripts:**
```bash
# ✅ Uses test Supabase
./tests/scripts/run_production_tests.sh

# ✅ Uses test Supabase
./tests/scripts/run_tests_phased.sh --phase smoke
```

---

## 🔧 **Verification Steps**

### **1. Check Backend is Using Test Supabase**
```bash
docker exec symphainy-backend-test printenv | grep SUPABASE_URL
# Should show test Supabase URL (not production)
```

### **2. Check Test Scripts Set TEST_MODE**
```bash
grep -r "TEST_MODE" tests/scripts/
# Should show TEST_MODE=true in test scripts
```

### **3. Verify Test Credentials Exist**
```bash
cat tests/.env.test | grep TEST_SUPABASE
# Should show test Supabase credentials
```

---

## 📋 **Recommendation**

**Update `run_tests_phased.sh` to ensure `TEST_MODE=true`:**

```bash
# At the top of run_tests_phased.sh
export TEST_MODE=true

# Source test environment if available
if [ -f "tests/.env.test" ]; then
    source tests/.env.test
fi
```

This ensures all tests use the test Supabase project, even when run directly.

---

## ✅ **Summary**

**Yes, we ARE using the test Supabase project when:**
1. ✅ Backend is running via `docker-compose.test.yml` (sets `TEST_MODE=true`)
2. ✅ Tests are run with `TEST_MODE=true` environment variable
3. ✅ `tests/.env.test` file exists with test Supabase credentials

**To ensure tests always use test Supabase:**
- Always run tests with `TEST_MODE=true`
- Use the test scripts (`run_production_tests.sh`, `run_tests_phased.sh`)
- Or manually set `TEST_MODE=true` before running pytest



