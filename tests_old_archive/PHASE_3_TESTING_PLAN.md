# Phase 3 Testing Plan - What We Can Test Now

**Date**: November 15, 2025  
**Status**: Phase 3 Complete - Ready for Testing  
**Phase 4 Status**: Waiting for Phase 1 & 2 fixes

---

## Overview

Phase 3 (Configuration & Startup Issues) is complete. We can test these fixes immediately while waiting for Phase 1 and Phase 2 to complete.

---

## What We Can Test Now

### ✅ 1. Layer 10: EC2 Deployment Configuration Tests

**Files to Test**:
- `symphainy-frontend/next.config.js`
- `symphainy-frontend/.env.production` (or `.env.local`)
- `symphainy-frontend/shared/services/**/*.ts` (API service files)
- `symphainy-platform/config/production.env`
- `symphainy-platform/main.py`
- `symphainy-platform/startup.sh` (if exists)

**Tests We Can Run**:
```bash
# Run Layer 10 deployment tests
pytest tests/integration/deployment/test_frontend_config.py -v
pytest tests/integration/deployment/test_backend_config.py -v
```

**What We're Validating**:
- ✅ Frontend defaults to EC2 IP (not localhost:3000)
- ✅ Frontend API URL points to EC2 IP (not localhost:8000)
- ✅ Backend binds to 0.0.0.0:8000 (not localhost:8000)
- ✅ Backend internal services use localhost (correct for EC2)
- ✅ Environment variables support Option C migration

---

### ✅ 2. Startup Sequence Validation

**What We Can Test**:
- ✅ Backend startup script health checks
- ✅ API router registration (should fail fast or log clearly)
- ✅ Infrastructure dependency checks
- ✅ Service initialization order

**Test Approach**:
Create integration tests that:
1. Start backend with test configuration
2. Verify startup sequence completes
3. Verify health checks work
4. Verify error handling is proper

---

### ✅ 3. Configuration File Validation

**What We Can Test**:
- ✅ Configuration files exist and are properly formatted
- ✅ Environment variables are set correctly
- ✅ No hardcoded localhost in production configs
- ✅ Option C migration path is documented

**Test Approach**:
Create static analysis tests that:
1. Parse configuration files
2. Validate structure
3. Check for hardcoded values
4. Verify environment variable usage

---

### ✅ 4. Test Infrastructure Validation

**What We Can Test**:
- ✅ Docker Compose test infrastructure works
- ✅ Real infrastructure adapters connect
- ✅ Test fixtures work correctly
- ✅ Test data setup/teardown works

**Test Approach**:
```bash
# Start test infrastructure
docker-compose -f tests/docker-compose.test.yml up -d

# Verify containers are healthy
docker-compose -f tests/docker-compose.test.yml ps

# Run infrastructure tests
pytest tests/integration/infrastructure_adapters/ -v
```

---

## Test Files We Can Create/Enhance Now

### 1. Enhanced Deployment Configuration Tests

**File**: `tests/integration/deployment/test_startup_sequence.py`

**Tests**:
- Backend startup completes successfully
- Health checks work
- API router registration succeeds
- Infrastructure dependencies are available

### 2. Configuration Validation Tests

**File**: `tests/integration/deployment/test_configuration_validation.py`

**Tests**:
- Configuration files are valid
- Environment variables are set
- No hardcoded localhost in production
- Option C migration path exists

### 3. Infrastructure Health Check Tests

**File**: `tests/integration/infrastructure/test_infrastructure_health.py`

**Tests**:
- Redis is accessible
- ArangoDB is accessible
- Meilisearch is accessible
- Consul is accessible

---

## Recommended Testing Order

### Step 1: Validate Test Infrastructure (15 minutes)
```bash
# Start test infrastructure
docker-compose -f tests/docker-compose.test.yml up -d

# Verify containers
docker-compose -f tests/docker-compose.test.yml ps

# Test basic connectivity
pytest tests/integration/infrastructure_adapters/ -v -k "test_connection"
```

### Step 2: Run Layer 10 Tests (30 minutes)
```bash
# Test frontend configuration
pytest tests/integration/deployment/test_frontend_config.py -v

# Test backend configuration
pytest tests/integration/deployment/test_backend_config.py -v
```

### Step 3: Create Additional Phase 3 Tests (1-2 hours)
- Create startup sequence tests
- Create configuration validation tests
- Create infrastructure health check tests

### Step 4: Prepare for Phase 1 & 2 Testing (1 hour)
- Review test fixtures
- Prepare test data
- Document test execution order
- Create test utilities/helpers

---

## What We Should Wait For

### ❌ Cannot Test Yet (Waiting for Phase 1 & 2):
- Layer 8: No Placeholder Tests (requires Phase 1 fixes)
- Layer 7: Access Pattern Tests (requires Phase 2 fixes)
- Layer 9: Graceful Failure Tests (requires Phase 2 fixes)
- Layer 4: Orchestrator Output Tests (requires Phase 2 fixes)

---

## Action Items

1. **Immediate** (Today):
   - ✅ Run Layer 10 deployment tests
   - ✅ Validate test infrastructure
   - ✅ Create startup sequence tests

2. **This Week** (While waiting):
   - ✅ Create configuration validation tests
   - ✅ Create infrastructure health check tests
   - ✅ Enhance test fixtures
   - ✅ Prepare test data for Phase 1 & 2

3. **When Phase 1 & 2 Complete**:
   - Run Layer 8 tests (no placeholders)
   - Run Layer 7 tests (access patterns)
   - Run Layer 9 tests (graceful failures)
   - Run Layer 4 tests (orchestrator outputs)

---

## Success Criteria for Phase 3 Testing

- ✅ All Layer 10 tests pass
- ✅ Configuration files are correct
- ✅ Startup sequence works
- ✅ Infrastructure health checks work
- ✅ Test infrastructure is ready for Phase 1 & 2 testing

---

**Next Steps**: Run Layer 10 tests and create additional Phase 3 validation tests.
