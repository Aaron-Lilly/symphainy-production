# Scaling Safety Test Setup Guide

**Date:** January 2025  
**Purpose:** Guide for setting up and running scaling safety tests with test Supabase project

---

## Overview

The scaling safety tests validate all three phases of scaling safety implementation:
- **Phase 1:** Traffic Cop WebSocket state in Redis (connection registry)
- **Phase 2:** Session state survives service restart (session persistence)
- **Phase 3:** Multi-tenant isolation prevents cross-tenant access

These tests use a **test Supabase project** (with rate limiting disabled) to properly validate security enablement.

---

## Prerequisites

### Required Infrastructure

1. **Redis** - Running on `localhost:6379` (or configured via `TEST_REDIS_URL`)
2. **Test Supabase Project** - With rate limiting disabled
3. **Python 3.10+** with required packages

### Test Supabase Project Setup

1. **Create Test Project in Supabase**
   - Create a new Supabase project for testing
   - Disable rate limiting (for testing purposes)
   - Enable RLS (Row Level Security) policies
   - Create test user account

2. **Get Credentials**
   - Project URL
   - Anon Key (Publishable Key)
   - Service Key (Secret Key)

---

## Environment Variables

### Required Variables

```bash
# Test Supabase Project Credentials
export TEST_SUPABASE_URL="https://your-test-project.supabase.co"
export TEST_SUPABASE_ANON_KEY="your_test_anon_key"
export TEST_SUPABASE_SERVICE_KEY="your_test_service_key"

# Test User Credentials (for auth)
export TEST_SUPABASE_EMAIL="test@symphainy.com"
export TEST_SUPABASE_PASSWORD="test_password_123"
```

### Optional Variables

```bash
# Redis Configuration (if not using defaults)
export TEST_REDIS_URL="redis://localhost:6379"
export TEST_REDIS_HOST="localhost"
export TEST_REDIS_PORT="6379"

# Test Infrastructure Flag
export TEST_USE_REAL_INFRASTRUCTURE="true"
```

---

## Test User Setup

### Automatic Setup

The tests automatically create a test user if it doesn't exist using:
- `get_test_supabase_token()` function
- Admin API (service key) to create user
- Auto-confirms email (no verification needed)

### Manual Setup (Optional)

If you prefer to create the user manually:

1. **Create User in Supabase Dashboard**
   - Email: `test@symphainy.com` (or your TEST_SUPABASE_EMAIL)
   - Password: `test_password_123` (or your TEST_SUPABASE_PASSWORD)
   - Confirm email immediately

2. **Set User Metadata (Optional)**
   - Add `permissions` to user metadata if needed
   - Add `tenant_id` if testing multi-tenant scenarios

---

## Running Tests

### Run All Scaling Safety Tests

```bash
cd /home/founders/demoversion/symphainy_source
python3 -m pytest tests/integration/scaling_safety/test_scaling_safety_holistic.py -v
```

### Run Specific Phase Tests

```bash
# Phase 1: Connection Registry
pytest tests/integration/scaling_safety/test_scaling_safety_holistic.py::TestScalingSafetyHolistic::test_phase1_connection_registry_redis -v

# Phase 2: Session Persistence
pytest tests/integration/scaling_safety/test_scaling_safety_holistic.py::TestScalingSafetyHolistic::test_phase2_session_persistence -v

# Phase 3: Tenant Isolation
pytest tests/integration/scaling_safety/test_scaling_safety_holistic.py::TestScalingSafetyHolistic::test_phase3_session_isolation -v
```

### Run with Markers

```bash
# Run only scaling safety tests
pytest -m scaling_safety -v

# Run integration tests
pytest -m integration -v
```

---

## Test Architecture

### Security Context Helper

The tests use `build_user_context_for_test()` helper function that:
1. Gets Supabase token via `get_test_supabase_token()`
2. Validates token through auth abstraction
3. Extracts user_id, tenant_id, and permissions
4. Returns properly formatted user_context dict

**Location:** `tests/utils/test_security_context_helper.py`

### Test Flow

1. **Setup:** Get test Supabase token
2. **Validation:** Validate token through auth abstraction
3. **Context Building:** Build user_context with permissions
4. **Security Checks:** Pass user_context to service methods
5. **Verification:** Assert security checks work correctly

---

## Expected Test Results

### Passing Tests (Core Functionality)

- ✅ `test_phase1_connection_registry_redis` - Connection registry uses Redis
- ✅ `test_phase1_connection_persistence` - Connections persist across restarts
- ✅ `test_phase2_session_storage_redis` - Sessions stored in Redis
- ✅ `test_phase3_file_isolation` - File isolation validation exists

### Tests Requiring Supabase Auth

- ⚠️ `test_phase2_session_persistence` - Requires Supabase token validation
- ⚠️ `test_phase3_session_isolation` - Requires Supabase token validation
- ⚠️ `test_holistic_scaling_safety` - Requires Supabase token validation
- ⚠️ `test_holistic_service_restart_simulation` - Requires Supabase token validation

**Note:** These tests will pass once Supabase credentials are configured and tokens are properly validated.

---

## Troubleshooting

### Issue: "Test Supabase token not available"

**Solution:**
1. Check environment variables are set:
   ```bash
   echo $TEST_SUPABASE_URL
   echo $TEST_SUPABASE_ANON_KEY
   ```
2. Verify test user exists in Supabase
3. Check service key has admin permissions

### Issue: "Access denied: insufficient permissions"

**Solution:**
1. Verify token validation is working:
   - Check auth abstraction is initialized
   - Verify token is valid (not expired)
   - Check user has permissions in Supabase

2. Check user metadata in Supabase:
   - Ensure `permissions` field exists
   - Verify permissions include required actions

### Issue: "Tenant isolation violation" when it shouldn't

**Solution:**
1. Verify tenant_id is set correctly in user_context
2. Check session tenant_id matches user tenant_id
3. Verify tenant validation logic is working

### Issue: "Connection lost after restart"

**Solution:**
1. Verify Redis is running and accessible
2. Check connection registry is initialized
3. Verify connection keys are correct format

---

## Security Context Helper Usage

### Basic Usage

```python
from utils.test_security_context_helper import build_user_context_for_test

# Get test token and build context
test_token = get_test_supabase_token()
user_context = await build_user_context_for_test(
    test_token=test_token,
    user_id="test_user_123",
    tenant_id="test_tenant_456",
    di_container=di_container
)

# Use in service calls
session_response = await traffic_cop_service.get_session(
    session_id,
    user_context=user_context
)
```

### Advanced Usage

```python
# Build context with custom permissions
user_context = await build_user_context_for_test(
    test_token=test_token,
    user_id="test_user_123",
    tenant_id="test_tenant_456",
    permissions=["session_management:read", "session_management:write"],
    di_container=di_container
)

# Build context from token only (extracts all info from token)
user_context = await build_user_context_from_token(
    access_token=test_token,
    di_container=di_container
)
```

---

## Test Data Cleanup

### Automatic Cleanup

Tests automatically clean up:
- Redis connections (via `unregister_connection`)
- Test sessions (via TTL expiration)

### Manual Cleanup (if needed)

```bash
# Connect to Redis
redis-cli

# List all test keys
KEYS traffic_cop:*
KEYS session:*

# Delete test keys (be careful!)
DEL traffic_cop:session:test_session_*
DEL session:test_session_*
```

---

## Best Practices

### 1. Use Test Supabase Project

- **Never** use production Supabase credentials in tests
- Use separate test project with rate limiting disabled
- Keep test project isolated from production data

### 2. Test User Management

- Use dedicated test user account
- Don't use real user accounts for testing
- Clean up test users periodically

### 3. Security Validation

- Always validate tokens through auth abstraction
- Don't bypass security checks in tests
- Verify permissions are extracted correctly

### 4. Test Isolation

- Each test should be independent
- Use unique session_ids and user_ids
- Clean up test data after each test

---

## Next Steps

1. **Set Environment Variables**
   - Configure TEST_SUPABASE_* variables
   - Verify Redis is running

2. **Run Tests**
   - Start with individual phase tests
   - Run full suite once individual tests pass

3. **Verify Results**
   - Check all 8 tests pass
   - Verify security checks are working
   - Confirm tenant isolation is enforced

---

**Last Updated:** January 2025

