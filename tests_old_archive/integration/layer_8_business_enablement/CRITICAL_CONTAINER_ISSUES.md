# Critical Container Issues - Root Cause Analysis

## 🔍 Investigation Summary

### Issues Found

1. **Tempo**: Health check failing - `curl` not available in container
2. **OPA**: Health check failing - `curl` not available in container  
3. **Celery Worker/Beat**: Container restarting - Exit code 137 (killed) + missing configuration

---

## 🐛 Issue #1: Tempo Health Check Failure

### Root Cause
- **Health Check Command**: `curl -f http://localhost:3200/status`
- **Problem**: `curl` is **NOT available** in the `grafana/tempo:latest` image
- **Error**: `exec: "curl": executable file not found in $PATH`
- **Failing Streak**: 163+ consecutive failures
- **Impact**: Container marked as "unhealthy" but still running

### Available Tools
- ✅ `wget` is available at `/busybox/wget` (Alpine-based image)
- ❌ `curl` is NOT available

### Solution
Change health check from `curl` to `wget`:

```yaml
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "-O", "/dev/null", "http://localhost:3200/status"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 30s
```

**Why**: Tempo image is Alpine-based and includes `wget` via busybox, but not `curl`.

---

## 🐛 Issue #2: OPA Health Check Failure

### Root Cause
- **Health Check Command**: `curl -f http://localhost:8181/health`
- **Problem**: `curl` is **NOT available** in the `openpolicyagent/opa:latest` image
- **Error**: `exec: "curl": executable file not found in $PATH`
- **Failing Streak**: 164+ consecutive failures
- **Impact**: Container marked as "unhealthy" but still running

### Available Tools
- ❌ `curl` is NOT available
- ❌ `wget` is NOT available (checked - not found)
- ⚠️ Need to verify what tools ARE available

### Solution Options

**Option 1: Use OPA's native health check**
OPA might have a built-in health check command. Need to verify.

**Option 2: Install curl/wget in custom image**
Create a custom OPA image that includes curl or wget.

**Option 3: Use a different health check method**
- Check if OPA exposes a different endpoint
- Use a shell script that uses available tools
- Use `depends_on` with `service_started` instead of health check

**Option 4: Use wget if available via busybox**
Some Alpine images have wget at `/busybox/wget` - need to test.

**Recommended**: First verify what tools are available, then choose the best option.

---

## 🐛 Issue #3: Celery Worker/Beat Restart Loops

### Root Cause
- **Status**: Container is **restarting** (not just unhealthy)
- **Exit Code**: 137 (killed - likely OOM or manual kill)
- **Error Messages**:
  - Missing required configuration: `ARANGO_URL`, `REDIS_URL`, `SECRET_KEY`, `JWT_SECRET`
  - `Unable to load celery application. The module main.celery was not found.`
- **Impact**: Containers cannot start properly

### Issues Identified

1. **Missing Environment Variables**:
   - `ARANGO_URL` (should be set in docker-compose)
   - `REDIS_URL` (should be set in docker-compose)
   - `SECRET_KEY` (not in docker-compose)
   - `JWT_SECRET` (not in docker-compose)

2. **Missing Celery Module**:
   - `main.celery` module not found
   - This suggests the Dockerfile might not be copying the application code correctly
   - Or the working directory is incorrect

3. **Container Killed (Exit 137)**:
   - Could be OOM (Out of Memory)
   - Could be manual kill
   - Need to check system resources

### Solution Steps

1. **Verify Environment Variables**:
   - Check if `.env` file has all required variables
   - Ensure docker-compose is reading from `.env`
   - Add missing `SECRET_KEY` and `JWT_SECRET` if needed

2. **Verify Dockerfile**:
   - Ensure `main.celery` module is copied
   - Check working directory
   - Verify Python path

3. **Check System Resources**:
   - Monitor memory usage
   - Check if containers are being killed due to OOM

4. **Review Celery Configuration**:
   - Ensure `main.celery` exists and is properly configured
   - Verify Celery app initialization

---

## 🔧 Recommended Fixes

### Priority 1: Fix Health Checks (Tempo & OPA)

**Tempo** - Change to wget:
```yaml
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "-O", "/dev/null", "http://localhost:3200/status"]
```

**OPA** - Need to investigate available tools first, then fix accordingly.

### Priority 2: Fix Celery Configuration

1. Add missing environment variables to docker-compose
2. Verify Dockerfile copies application code correctly
3. Check system resources for OOM issues

---

## ⚠️ Safety Considerations

- **No Blocking Operations**: All fixes use safe, non-blocking health checks
- **No Infinite Loops**: Health checks have timeouts and retry limits
- **Graceful Failure**: Containers will fail health checks but won't hang the system
- **VM Session Safe**: These fixes won't cause SSH/VM access issues

---

## 📋 Next Steps

1. ✅ Fix Tempo health check (change curl to wget)
2. ⚠️ Investigate OPA health check (verify available tools)
3. ⚠️ Fix Celery configuration (environment variables + module path)
4. ✅ Test all fixes safely
5. ✅ Monitor containers after fixes

