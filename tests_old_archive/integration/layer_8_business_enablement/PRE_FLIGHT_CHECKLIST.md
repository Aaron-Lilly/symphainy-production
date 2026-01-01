# Pre-Flight Checklist - Before Resuming Layer 8 Testing

## ✅ Fixes Applied (Verify These Are In Place)

### 1. Consul Connection Timeout ✅
- **File**: `consul_service_discovery_adapter.py`
- **Fix**: 5-second timeout, raises ConnectionError instead of hanging
- **Status**: ✅ Fixed

### 2. ArangoDB Connection Timeout ✅
- **File**: `arangodb_adapter.py`
- **Fix**: 5-second timeout in `test_connection()`, raises ConnectionError
- **Status**: ✅ Fixed

### 3. Document Intelligence Abstraction ✅
- **File**: `document_intelligence_abstraction.py`
- **Fix**: `_parse_with_adapter()` now returns error dict instead of None
- **Status**: ✅ Fixed

### 4. Docker Health Checks ✅
- **File**: `docker-compose.infrastructure.yml`
- **Fix**: Improved ArangoDB health check with proper wget flags
- **Status**: ✅ Fixed

### 5. Configuration Ports ✅
- **Verification**: All config defaults match Docker container ports
- **Status**: ✅ Verified (ArangoDB: 8529, Consul: 8500)

## 🔍 Pre-Flight Checks

### 1. Environment Variables
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` is not being modified globally
- [ ] Test-specific variables are used (`TEST_GCS_CREDENTIALS`, etc.)

### 2. Docker Containers
- [ ] No containers in restart loops
- [ ] Container health checks are passing
- [ ] Containers are accessible

### 3. System Resources
- [ ] Sufficient memory available
- [ ] CPU load is reasonable
- [ ] Disk space available

### 4. No Hanging Processes
- [ ] No old pytest processes running
- [ ] No hanging Python processes

## 🚀 Safe Test Execution Plan

### Step 1: Run Diagnostics (Safe - Has Timeouts)
```bash
python3 diagnose_background_issues.py
```

### Step 2: Check Docker Containers (Safe - Has Timeouts)
```bash
python3 safe_docker_inspect.py --all --health
```

### Step 3: Verify Fixes Are In Place
- Check that timeout fixes are in the code
- Verify document intelligence fix is applied

### Step 4: Run Test with Safety Measures
```bash
# Use timeout as backup
timeout 300 pytest tests/integration/layer_8_business_enablement/test_file_parser_core.py::TestFileParserCore::test_parse_text_file -v

# Or use pytest-timeout plugin
pytest --timeout=300 tests/integration/layer_8_business_enablement/test_file_parser_core.py::TestFileParserCore::test_parse_text_file -v
```

## ⚠️ Safety Measures in Place

1. ✅ **Connection Timeouts**: Consul and ArangoDB connections have 5-second timeouts
2. ✅ **Graceful Failures**: Infrastructure failures cause clean errors, not hangs
3. ✅ **Test Timeouts**: Can use pytest-timeout or system timeout command
4. ✅ **Safe Inspection**: Diagnostic scripts have timeouts on all operations

## 📋 What to Check Before Running Tests

1. **Docker Container Status**: Are containers running and healthy?
2. **No Restart Loops**: Are containers stable?
3. **System Resources**: Is there enough memory/CPU?
4. **Environment Variables**: Is GOOGLE_APPLICATION_CREDENTIALS safe?

## 🎯 Next Steps After Diagnostics

1. If diagnostics show issues → Fix them first
2. If diagnostics are clean → Proceed with test
3. Monitor test execution → Use timeout as backup
4. If test hangs → Kill it safely and investigate

